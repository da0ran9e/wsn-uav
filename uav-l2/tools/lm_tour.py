"""LM-Tour on the pre-existing clusters (paper Section V; CLAUDE.md §8 items 170-175), step C: model level.

    python3 tools/lm_tour.py plan WORK --out LMWORK [--R 450] [--theta 1] [--rounds 2]
    python3 tools/lm_tour.py score WORK[,WORK...] --mode pred|ns3 [--draws 100] --out OUT

WORK is a CHORD mission folder (mission.py --chordTour 0.6,0.8 --kinPass --windowKB 400 --windowAt crit, River
run): its clusters, CHs, critical cells and chords. LM-Tour keeps all of them and changes only each cluster's pass.
  start   the cluster's CHORD chord through its CH. On pre-existing clusters the paper's Steps 1-2 (weighted R-net,
          base tour through the kept nodes' discs) reduce to this: the CH is the first kept node and the chord the
          pass through its disc
  value   a pass is scored by J_k = sum over the cluster's critical cells c of ready_c + theta N_after dur_k, where
          ready_c = min(own_c, dur_k + T_River(c)) seconds from the start of the pass; T_River is the step-A formula
          (river_surrogate.py) on the River plan of this pass; own_c the time at which the expected union reception
          of the fountain-coded clue set by the cell's nodes along the pass reaches FC's target, plus FC's in-cell
          gather; dur_k the pass as pass_speed.fit flies it (slowed down, or looped, so that one copy of the clue
          set is sent over the cluster's cells); N_after the critical cells of the clusters flown after it (each
          second of the pass delays every one of them)
  insert  candidates: critical cells farther than R/2 from the pass. Each re-routes the chord into its disc
          B(c, R/2) (meander_lane.bend_lane: Gaussian bumps, the CH pinned, no cap); the candidate that lowers J_k
          most is inserted, until none lowers it. With uniform priors this is the paper's greedy rule
          w(v) / dL(v) >= theta, w the critical-cell seconds saved and dL the critical-cell seconds of delay
  order   team 1's tour over the new passes as for CHORD (mission_policy.tour kin); round 2 redoes the insertions
          with N_after from that order
Writes LMWORK: every file of WORK linked, except the passes (c{k}-path-const.csv, -path-s35.csv, -speed.json) and
what depends on them (pass, plan and River results, tour, fountain realisations); then lm.json.
score: the mission of l1_rank's P+prog-kin-puq-stage-zero-redir-kt-fcd (CHORD) on each folder, 100 layer-1 draws
as l1_rank, with River's doneS either from ns-3 (mode ns3, the folder's River results, exactly as l1_rank) or
predicted (mode pred: the step-A formula; River's window copy holds every clue). Writes OUT.csv, one row a draw.
"""
import argparse, csv, hashlib, json, math, os, re, sys, tempfile

import numpy as np

import fc_baseline
import kin_time
import l1_model as L
import l1_rank as R
from meander_lane import bend_lane, write_path
from mission import ENV_LOSS
from mission_policy import GAP, tour
from mission_report import load_map
from pass_speed import fit
from river_surrogate import WINDOW, Model, features, mission_plan

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hear_model, load_around, packets  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SURROGATE = os.path.join(HERE, "../docs/data/results/river-surrogate.csv")
METHOD = "P+prog-kin-puq-stage-zero-redir-kt-fcd"
SKIP = re.compile(r"^(pass\d+-|plan\d+\.|r\d+-|tour\.json$|chordfc-|fc-|dn-|lm\.json$|"
                  r"c\d+-path-(const|s35)\.csv$|c\d+-speed\.json$)")


class Cluster:
    """What the BS knows of cluster k before take-off, and the score of a pass over it."""

    def __init__(self, w, M, k, model, hear, loss, around):
        self.k, self.model, self.hear, self.loss, self.around = k, model, hear, loss, around
        self.geo = M["cl"][k]["geo"]
        self.rows0 = list(csv.DictReader(open(f"{w}/c{k}-path-const.csv")))   # CHORD's pass, no times
        xy = [(float(r["x"]), float(r["y"])) for r in self.rows0 if r["part"] in ("1", "2")]
        core = np.array([p for i, p in enumerate(xy) if i == 0 or p != xy[i - 1]])
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(core, axis=0), axis=1))]
        d = np.r_[np.arange(0, s[-1], 10.0), s[-1]]
        self.core0 = np.c_[np.interp(d, s, core[:, 0]), np.interp(d, s, core[:, 1])]   # 10 m vertices
        chn = next(x for x in self.geo["nodes"] if x["isCH"] == "1")
        self.ch = np.array([float(chn["x"]), float(chn["y"])])
        pos = {}
        for n in self.geo["nodes"]:
            pos.setdefault((int(n["q"]), int(n["r"])), []).append((float(n["x"]), float(n["y"]), n["isCL"] == "1"))
        self.pos = pos
        C = L.clues()
        K = np.array([math.ceil(c["kB"] * 1000 / 99) for c in C])
        need = np.ceil((1 + fc_baseline.EPS) * K)
        self.need, self.target = float(need.sum()), float((need + 3 * np.sqrt(need)).sum())

    def rows(self, pulls, R):
        """CHORD's pass (no pulls) or the chord bent into the discs B(c, R/2) of the pulls."""
        if not pulls:
            return self.rows0
        Q, idx, _ = bend_lane(self.core0, [self.ch], [np.array(self.geo["c"][h]) for h in pulls], reach=R / 2,
                              cap=math.inf)
        with tempfile.NamedTemporaryFile("w+", suffix=".csv") as f:
            write_path(f.name, Q, idx[0])
            return list(csv.DictReader(open(f.name)))

    def evaluate(self, rows):
        """The pass flown (pass_speed.fit), its River plan and every critical cell's ready time from its start."""
        new, cap, loops = fit(rows, self.geo["S"], self.ch, WINDOW)
        uav = packets(new)
        geo = dict(self.geo, uav=uav)
        P = mission_plan(geo, self.around, self.loss)
        F = features(geo, P, self.loss, self.hear)
        T = dict(zip(P["crit"], self.model.predict([F[h] for h in P["crit"]])))
        dur = float(new[-1]["t"])
        ready, own = {}, {}
        for h in P["crit"]:
            nd = np.array([(x, y) for x, y, _ in self.pos[h]])
            p = self.hear(np.linalg.norm(uav[:, None, :] - nd[None, :, :], axis=2))
            cum = np.cumsum(1 - np.prod(1 - p, axis=1))
            i = int(np.searchsorted(cum, self.target))
            if i < len(cum):   # decoded on its own: then the CL gathers what it lacks from its members
                cl = [j for j, (_, _, z) in enumerate(self.pos[h]) if z][0]
                moved = max(0.0, self.need - float(p[:i + 1, cl].sum()))
                own[h] = i * fc_baseline.SLOT + fc_baseline.GATHER_A + fc_baseline.GATHER_B * moved
            ready[h] = min(own.get(h, math.inf), dur + max(0.0, float(T[h])))
        return dict(rows=rows, timed=new, cap=cap, loops=loops, dur=dur, T=T, own=own, ready=ready, P=P,
                    L=float(np.linalg.norm(np.diff(uav, axis=0), axis=1).sum()))

    def improve(self, R, theta, n_after):
        """Greedy insertions from CHORD's chord; returns (pulls, evaluation, base evaluation)."""
        J = lambda e: sum(e["ready"].values()) + theta * n_after * e["dur"]
        base = cur = self.evaluate(self.rows0)
        pulls = []
        while True:
            Q = np.array([[float(r["x"]), float(r["y"])] for r in cur["rows"]])
            cand = [h for h in base["P"]["crit"] if h not in pulls and
                    np.linalg.norm(Q - self.geo["c"][h], axis=1).min() > R / 2]
            trials = [(J(e), h, e) for h in cand for e in [self.evaluate(self.rows(pulls + [h], R))]]
            if not trials:
                break
            j, h, e = min(trials, key=lambda x: x[0])
            if j >= J(cur) - 1e-6:
                break
            pulls, cur = pulls + [h], e
        return pulls, cur, base


def order_after(w):
    """N_after per cluster: critical cells of the clusters team 1 flies after it (mission_policy.tour kin)."""
    M = load_map(w, schemes=(), with_bits=False)
    legs, _ = tour(M, "kin")
    n = {k: len(M["cl"][k]["P"]["crit"]) for k in M["cl"]}
    order = [l[0] for l in legs]
    return {k: sum(n[j] for j in order[i + 1:]) for i, k in enumerate(order)}, order


def build(w, out, passes):
    """LMWORK: WORK's files linked, the new passes written and flown (pass_speed.run)."""
    import pass_speed
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if SKIP.match(f) or os.path.islink(f"{out}/{f}"):
            os.remove(f"{out}/{f}")
    for f in os.listdir(w):
        if not SKIP.match(f):
            os.symlink(os.path.abspath(f"{w}/{f}"), f"{out}/{f}")
    for k, rows in passes.items():
        with open(f"{out}/c{k}-path-const.csv", "w") as fh:
            wr = csv.DictWriter(fh, fieldnames=["part", "seg", "x", "y", "thDeg"], extrasaction="ignore",
                                lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows)
    pass_speed.run(out, len(passes))


def context(w):
    env = open(f"{w}/env.txt").read().strip() if os.path.exists(f"{w}/env.txt") else "open"
    opts = json.load(open(f"{w}/plan-opts.json"))
    return env, opts["lossDb"], load_around(f"{w}/domain-cl.csv")


def plan_lm(w, out, R, theta, rounds):
    env, loss, around = context(w)
    hear, model = hear_model(loss), Model.load(SURROGATE, "formula")
    M = load_map(w, schemes=(), with_bits=False)
    cls = {k: Cluster(w, M, k, model, hear, loss, around) for k in sorted(M["cl"])}
    n_after, order = order_after(w)
    log = []
    for rnd in range(rounds):
        res = {k: c.improve(R, theta, n_after[k]) for k, c in cls.items()}
        build(w, out, {k: r[1]["rows"] for k, r in res.items()})
        log.append(dict(round=rnd + 1, order=order, n_after=n_after, clusters={
            k: dict(pulls=[list(h) for h in r[0]], dur=[round(r[2]["dur"], 1), round(r[1]["dur"], 1)],
                    ready=[round(float(np.mean(list(r[2]["ready"].values()))), 1),
                           round(float(np.mean(list(r[1]["ready"].values()))), 1)],
                    river=[round(float(np.mean(list(r[2]["T"].values()))), 1),
                           round(float(np.mean(list(r[1]["T"].values()))), 1)],
                    own=[len(r[2]["own"]), len(r[1]["own"])], crit=len(r[1]["ready"])) for k, r in res.items()}))
        for k, r in sorted(res.items()):
            print(f"round {rnd + 1} C{k}: {len(r[0])} insertions, pass {r[2]['dur']:.0f} -> {r[1]['dur']:.0f} s, "
                  f"mean ready {np.mean(list(r[2]['ready'].values())):.0f} -> {np.mean(list(r[1]['ready'].values())):.0f} s "
                  f"(River {np.mean(list(r[2]['T'].values())):.0f} -> {np.mean(list(r[1]['T'].values())):.0f} s, "
                  f"own decode {len(r[2]['own'])} -> {len(r[1]['own'])} of {len(r[1]['ready'])}), N_after {n_after[k]}",
                  flush=True)
        n_after, order = order_after(out)
    json.dump(dict(work=os.path.abspath(w), R=R, theta=theta, rounds=log), open(f"{out}/lm.json", "w"), indent=1)


def score(w, mode, draws):
    """T* of every draw on folder w (see the module docstring), and team 1's tour."""
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    M = load_map(w, schemes=("rf",)) if mode == "ns3" else load_map(w, schemes=(), with_bits=False)
    M["name"], M["windowAt"] = R.mapname(w), "crit"
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    if mode == "pred":
        env, loss, around = context(w)
        hear, model = hear_model(loss), Model.load(SURROGATE, "formula")
        for k in M["cl"]:
            geo = M["cl"][k]["geo"]
            P = mission_plan(geo, around, loss)
            assert P["crit"] == M["cl"][k]["P"]["crit"]
            F = features(geo, P, ENV_LOSS[env], hear)
            T = model.predict([F[h] for h in P["crit"]])
            M["cl"][k]["P"] = P
            M["cl"][k]["res"] = {"rf": {h: dict(doneS=max(0.0, float(t)), gatherDoneS=0.0) for h, t in zip(P["crit"], T)}}
    tours = {"kin": tour(M, "kin")}
    _, o = kin_time.run(w, "kin")
    tours["kin/kt"] = ([(*l[:4], o[45]["leave"][l[0]]) for l in tours["kin"][0]], o[45]["profile"] + o[45]["fix"])
    tc, pts, _ = o[45]["track"]
    with tempfile.TemporaryDirectory() as td:
        M["fcd"] = fc_baseline.realise(fc_baseline.Ground(M, C, crits, w), M, C, crits, pts, tc, "chordfc", td, {})
    if mode == "ns3":
        hold = R.holdings(M, C, seqs)
    else:
        full, none = np.ones(len(C), bool), np.zeros(len(C), bool)
        hold = {x: {s: (full, none) for s in seqs} for x in crits}
    prng = np.random.default_rng(int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little"))
    Ts = []
    for d in range(draws):
        phase = {k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])}
        out, _, _ = R.missions(M, tours, hold, d, phase, C, Cq, [METHOD])
        Ts.append(out[METHOD][0])
    leave = tours["kin/kt"][0]
    ready = [l[4] + float(M["cl"][x[0]]["res"]["rf"][x[1]]["doneS"]) for x in crits for l in leave if l[0] == x[0]]
    return Ts, tours["kin/kt"][1], float(np.mean(ready))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("work")
    p.add_argument("--out", required=True)
    p.add_argument("--R", type=float, default=450.0)
    p.add_argument("--theta", type=float, default=1.0)
    p.add_argument("--rounds", type=int, default=2)
    s = sub.add_parser("score")
    s.add_argument("works")
    s.add_argument("--mode", choices=("pred", "ns3"), required=True)
    s.add_argument("--draws", type=int, default=100)
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "plan":
        plan_lm(a.work, a.out, a.R, a.theta, a.rounds)
        return
    rows = []
    for w in a.works.split(","):
        Ts, t1, rd = score(w, a.mode, a.draws)
        env = open(f"{w}/env.txt").read().strip() if os.path.exists(f"{w}/env.txt") else "open"
        rows += [dict(work=w, map=R.mapname(w), env=env, mode=a.mode, draw=d, Tstar=round(t, 1), team1=round(t1, 1),
                      riverReady=round(rd, 1)) for d, t in enumerate(Ts)]
        print(f"{w} [{a.mode}]: T* {np.mean(Ts):.0f} s (sd {np.std(Ts):.0f}), team 1 {t1:.0f} s, "
              f"mean River ready {rd:.0f} s", flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(f"{a.out}.csv", "w") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


if __name__ == "__main__":
    main()
