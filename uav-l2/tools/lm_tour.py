"""LM-Tour on the pre-existing clusters (paper Section V; CLAUDE.md §8 items 170-175), step C: model level.

    python3 tools/lm_tour.py plan WORK --out LMWORK [--R 450] [--xi auto] [--theta 1] [--rounds 2]
    python3 tools/lm_tour.py score WORK[,WORK...] --mode pred|ns3 [--draws 100] --out OUT

WORK is a CHORD mission folder (mission.py --chordTour 0.6,0.8 --kinPass --windowKB 400 --windowAt crit, River
run): its clusters, CHs, critical cells and chords. LM-Tour keeps all of them and changes only each cluster's pass.
  start   the cluster's CHORD chord through its CH. On pre-existing clusters the paper's Steps 1-2 (weighted R-net,
          base tour through the kept nodes' discs) reduce to this: the CH is the first kept node and the chord the
          pass through its disc
  value   a pass is scored by J_k = sum over the cluster's n_k critical cells c of ready_c + n_k t_in
          + theta N_after (t_in + dur_k + t_out), where
          ready_c = min(own_c, dur_k + T_River(c)) seconds from the start of the pass; T_River is the step-A formula
          (river_surrogate.py) on the River plan of this pass; own_c the time at which the expected union reception
          of the fountain-coded clue set by the cell's nodes along the pass reaches FC's target, plus FC's in-cell
          gather; dur_k the pass as pass_speed.fit flies it (slowed down, or looped, so that one copy of the clue
          set is sent over the cluster's cells); t_in, t_out the Dubins transits from the previous cluster's pass
          and to the next one's (mission_policy.kin_links; the BS with a free heading at the ends), whose poses
          the bend changes; N_after the critical cells of the clusters flown after it (each second of the pass or
          of its transits delays every one of them)
  insert  candidates: critical cells farther than R/2 from the pass. Each re-routes the chord into its disc
          B(c, xi) (draft v5 line 8; --xi, default R/2 as before; auto: xi = min(omega, rho, R50 of the channel),
          the lateral reach sqrt(r^2 - h^2) at which a node hears the UAV directly) (meander_lane.bend_lane: Gaussian bumps, the CH pinned, no cap); the candidate that lowers J_k
          most is inserted, until none lowers it. With uniform priors this is the paper's greedy rule
          w(v) / dL(v) >= theta, w the critical-cell seconds saved and dL the critical-cell seconds of delay
  order   team 1's tour over the new passes as for CHORD (mission_policy.tour kin); round 2 redoes the insertions
          with N_after from that order
  dtspn   (--dtspn, item 187; WORK then plain CHORD, mission.py without --chordTour) Algorithm 3 line 6: the start
          is not CHORD's chord but a Dubins TSP-N through the discs B(CH_k, xi): per cluster a straight line through
          the CH (a bearing every 30 degrees) over the cluster's cells, no minimum length (a short one is slowed
          down or looped by pass_speed.fit), legs, directions and order chosen together (chord_tour.choose). Then
          the insertions above into each leg, the CH pinned, candidates the critical cells farther than xi of
          weight >= --wmin, until J_k stops falling; the pass must cross the cluster once. --weight cl: each
          critical cell weighs its strongest node's score over the map's mean, in J_k and in the order
Writes LMWORK: every file of WORK linked, except the passes (c{k}-path-const.csv, -path-s35.csv, -speed.json) and
what depends on them (pass, plan and River results, tour, fountain realisations); then lm.json.
score: the mission of l1_rank's P+prog-kin-puq-stage-zero-redir-kt-fcd (CHORD) on each folder, 100 layer-1 draws
as l1_rank, with River's doneS either from ns-3 (mode ns3, the folder's River results, exactly as l1_rank) or
predicted (mode pred: the step-A formula; River's window copy holds every clue). Writes OUT.csv, one row a draw.
"""
import argparse, csv, hashlib, json, math, os, re, sys, tempfile

import numpy as np

import dubins
import fc_baseline
from chord_tour import choose
import kin_time
import l1_model as L
import l1_rank as R
from map_gen import cell_at
from meander_lane import bend_lane, write_path
from mission import ENV_LOSS, runseed
from mission_policy import GAP, R_TURN, tour
from mission_report import load_map
from pass_speed import fit
from river_surrogate import WINDOW, Model, features, mission_plan

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hear_model, load_around, packets  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = 50.0
SURROGATE = os.path.join(HERE, "../docs/data/results/river-surrogate.csv")
METHOD = "P+prog-kin-puq-stage-zero-redir-kt-fcd"
OMEGA = 303.0   # m: River half-width, 1.75 cells
R50 = {"open": 1015.0, "r500": 498.0, "r200": 199.0, "r100": 99.0}   # m: lateral reach, calibrate.md
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

    def chord(self, b, gap=300.0):
        """--dtspn (item 187): the straight line through the CH at bearing b (degrees), 10 m vertices, cut to the run
        over the cluster's cells that holds the CH (gaps such as lakes shorter than gap bridged)."""
        u = np.array([math.cos(math.radians(b)), math.sin(math.radians(b))])
        d = np.arange(-8000.0, 8000.0 + 1, 10.0)
        X = self.ch + d[:, None] * u
        inside = np.array([cell_at(*p) in self.geo["S"] for p in X])
        i0 = i1 = len(d) // 2
        while i0 > 0 and inside[max(i0 - int(gap / 10), 0):i0].any():
            i0 -= 1
        while i1 < len(d) - 1 and inside[i1 + 1:i1 + 1 + int(gap / 10)].any():
            i1 += 1
        return X[i0:i1 + 1]

    def rows(self, pulls, xi, line=None, pin=False):
        """CHORD's pass (no pulls) or the chord bent into the discs B(c, xi) of the pulls, the CH pinned; with
        line (--free, item 179) that straight line bent into them instead, nothing pinned; with line and pin
        (--dtspn) that line bent, the CH pinned."""
        if not pulls and line is None:
            return self.rows0
        base, pins = (self.core0, [self.ch]) if line is None else (line, [self.ch] if pin else [])
        Q, idx, _ = bend_lane(base, pins, [np.array(self.geo["c"][h]) for h in pulls], reach=xi, cap=math.inf)
        with tempfile.NamedTemporaryFile("w+", suffix=".csv") as f:
            write_path(f.name, Q, idx[0] if idx else len(Q) // 2)
            return list(csv.DictReader(open(f.name)))

    def once(self, rows, gap=300.0):
        """The pass crosses the cluster once: one run over its cells, gaps (lakes) shorter than gap allowed."""
        X = np.array([[float(r["x"]), float(r["y"])] for r in rows])[::5]
        inside = np.array([cell_at(*p) in self.geo["S"] for p in X])
        idx = np.nonzero(inside)[0]
        if not len(idx):
            return False
        s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(X, axis=0), axis=1))]
        return all(s[b] - s[a] <= gap for a, b in zip(idx[:-1], idx[1:]) if b > a + 1)

    def lines(self, kept, step=30):
        """Straight lines over the cluster through the kept cells' centroid, every step degrees, 10 m vertices."""
        C = np.array([self.geo["c"][h] for h in self.geo["cells"]])
        o = np.mean([self.geo["c"][h] for h in kept], axis=0)
        out = []
        for b in range(0, 180, step):
            u = np.array([math.cos(math.radians(b)), math.sin(math.radians(b))])
            t = (C - o) @ u
            d = np.arange(t.min() - 60, t.max() + 60, 10.0)
            out.append(o + d[:, None] * u)
        return out

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

    def improve(self, R, theta, n_after, nb, free=False, xi=None, dtspn=None, w=None, wmin=0.0):
        """Greedy insertions from CHORD's chord; nb = (previous end pose, next start pose, direction, BS) of the
        tour. free (item 179): the paper's Steps 1-2 instead, the CH not required: a weighted R-net of the critical
        cells (by predicted River time on CHORD's pass, kept at least R apart), the straight lines through the
        kept cells' centroid every 30 degrees bent into their discs, the best line that crosses the cluster once
        (self.once) as the start. dtspn (item 187): the start is that line through the CH (the DTSP-N leg), the CH
        pinned; candidates are the critical cells farther than xi from the pass with weight w >= wmin, each scored
        by its weight; a bend must cross the cluster once. w: {cell: weight}, 1 for every cell when None; n_after
        is then the weight of the critical cells flown after. Returns (pulls, evaluation, base evaluation); base is
        the pass bending starts from."""
        prev, nxt, d, bs = nb
        xi = R / 2 if xi is None else xi
        wt = (lambda h: 1.0) if w is None else (lambda h: w[h])

        def J(e):
            p = np.array([[float(r["x"]), float(r["y"])] for r in e["rows"]])
            p = p[::-1] if d else p
            start = (*p[0], math.atan2(*(p[1] - p[0])[::-1]))
            end = (*p[-1], math.atan2(*(p[-1] - p[-2])[::-1]))
            tin = (dubins.free_start(bs, start, R_TURN) if prev is None else dubins.length(prev, start, R_TURN)) / V1
            tout = (dubins.free_end(end, bs, R_TURN) if nxt is None else dubins.length(end, nxt, R_TURN)) / V1
            e["tin"], e["tout"] = tin, tout
            return sum(wt(h) * t for h, t in e["ready"].items()) + sum(map(wt, e["ready"])) * tin + \
                theta * n_after * (tin + e["dur"] + tout)
        if dtspn is not None:
            base = cur = self.evaluate(self.rows([], xi, dtspn, pin=True))
            J(base)
            pulls = []
            while True:
                Q = np.array([[float(r["x"]), float(r["y"])] for r in cur["rows"]])
                cand = [h for h in base["P"]["crit"] if h not in pulls and wt(h) >= wmin and
                        np.linalg.norm(Q - self.geo["c"][h], axis=1).min() > xi]
                trials = [(J(e), h, e) for h in cand for r in [self.rows(pulls + [h], xi, dtspn, pin=True)]
                          if self.once(r) for e in [self.evaluate(r)]]
                if not trials:
                    break
                j, h, e = min(trials, key=lambda x: x[0])
                if j >= J(cur) - 1e-6:   # the benefit has saturated
                    break
                pulls, cur = pulls + [h], e
            return pulls, cur, base
        base = cur = self.evaluate(self.rows0)
        J(base)
        pulls, line = [], None
        if free:
            order = sorted(base["P"]["crit"], key=lambda h: -base["T"][h])
            kept = []
            for h in order:
                if all(math.dist(self.geo["c"][h], self.geo["c"][g]) >= R for g in kept):
                    kept.append(h)
            best = None
            for ln in self.lines(kept):
                r = self.rows(kept, xi, ln)
                if not self.once(r):
                    continue
                e = self.evaluate(r)
                if best is None or J(e) < best[0]:
                    best = (J(e), ln, e)
            if best is not None:
                _, line, cur = best
                pulls = list(kept)
        while True:
            Q = np.array([[float(r["x"]), float(r["y"])] for r in cur["rows"]])
            cand = [h for h in base["P"]["crit"] if h not in pulls and
                    np.linalg.norm(Q - self.geo["c"][h], axis=1).min() > R / 2]
            trials = [(J(e), h, e) for h in cand for r in [self.rows(pulls + [h], xi, line)]
                      if line is None or self.once(r) for e in [self.evaluate(r)]]
            if not trials:
                break
            j, h, e = min(trials, key=lambda x: x[0])
            if j >= J(cur) - 1e-6:
                break
            pulls, cur = pulls + [h], e
        return pulls, cur, base


def order_after(w):
    """Per cluster, of team 1's tour (mission_policy.tour kin): N_after, the critical cells of the clusters flown
    after it, and its neighbours nb = (previous end pose, next start pose, direction, BS); and the order."""
    M = load_map(w, schemes=(), with_bits=False)
    legs, _ = tour(M, "kin")
    n = {k: len(M["cl"][k]["P"]["crit"]) for k in M["cl"]}
    order = [l[0] for l in legs]
    pose = {}
    for l in legs:   # as mission_policy.kin_links
        p = M["cl"][l[0]]["geo"]["path"]
        d = 0 if math.dist(l[1], p[0]) < 1e-6 else 1
        p = p[::-1] if d else p
        pose[l[0]] = (d, (*p[0], math.atan2(*(p[1] - p[0])[::-1])), (*p[-1], math.atan2(*(p[-1] - p[-2])[::-1])))
    nb = {k: (pose[order[i - 1]][2] if i else None, pose[order[i + 1]][1] if i + 1 < len(order) else None,
              pose[k][0], M["bs"]) for i, k in enumerate(order)}
    return {k: sum(n[j] for j in order[i + 1:]) for i, k in enumerate(order)}, nb, order


def weight_after(order, wk):
    """{k: the weight of the critical cells of the clusters flown after k}."""
    return {k: sum(wk[j] for j in order[i + 1:]) for i, k in enumerate(order)}


def dtspn(cls, bs, wk, xi, step=30):
    """--dtspn (item 187), Algorithm 3 line 6 on the pre-existing clusters: a Dubins TSP with neighbourhoods
    through the discs B(CH_k, xi). Each cluster's leg is a straight line through its CH (Cluster.chord, a bearing
    every step degrees) flown as pass_speed.fit flies it, so a short crossing pays for its delivery (slowed down or
    looped until one clue-set copy is sent over the cluster); the legs, their directions and the order are chosen
    together, least sum_k W_k leave_k (W_k the weight of the cluster's critical cells), Dubins transits
    (chord_tour.choose). Returns {k: line}, {k: bearing}, the order and nb as order_after."""
    cands, lines = {}, {}
    for k, c in cls.items():
        cands[k], lines[k] = [], []
        for b in range(0, 180, step):
            ln = c.chord(b)
            rows = c.rows([], xi, ln, pin=True)
            new, _, _ = fit(rows, c.geo["S"], c.ch, WINDOW)
            p = np.array([[float(r["x"]), float(r["y"])] for r in rows])
            h0, h1 = math.atan2(*(p[1] - p[0])[::-1]), math.atan2(*(p[-1] - p[-2])[::-1])
            cands[k].append(dict(L=float(new[-1]["t"]) * V1, poses=[((*p[0], h0), (*p[-1], h1)),
                                                                     ((*p[-1], h1 + math.pi), (*p[0], h0 + math.pi))]))
            lines[k].append((b, ln))
    picks, order = choose(bs, cands, wk)
    pose = {k: cands[k][c]["poses"][d] for k, c, d in order}
    ks = [k for k, _, _ in order]
    nb = {k: (pose[ks[i - 1]][1] if i else None, pose[ks[i + 1]][0] if i + 1 < len(ks) else None, d, bs)
          for i, (k, _, d) in enumerate(order)}
    return {k: lines[k][c][1] for k, c in picks.items()}, {k: lines[k][c][0] for k, c in picks.items()}, ks, nb


def every_crit(c, ln, xi):
    """--dtspnRiver: the line ln bent into the discs B(v, xi) of the cluster's critical cells, nothing pinned; the
    cells farther from the line taken first, each kept only if the pass still crosses the cluster once. Rows or
    None."""
    far = sorted(c.geo["crit"], key=lambda h: -np.linalg.norm(ln - c.geo["c"][h], axis=1).min())
    pulls, rows = [], c.rows([], xi, ln)
    if not c.once(rows):
        return None
    for h in far:
        r = c.rows(pulls + [h], xi, ln)
        if c.once(r):
            pulls, rows = pulls + [h], r
    return rows


def plan_dr(w, out, xi):
    """Baseline DTSP-N + River (item 187): DN's tour idea, but each cluster crossed once and River fills in. Per
    cluster a straight line through its critical cells' centroid (a bearing every 30 degrees) bent into the discs
    B(v, xi) of all of them (every_crit: zigzag, no loop back over its own path, the CH not required), flown as
    pass_speed.fit flies it; lines, directions and order chosen together, least sum_k n_k leave_k
    (chord_tour.choose)."""
    env, loss, around = context(w)
    if xi == "auto":
        xi = min(OMEGA, R_TURN, R50[env])
    hear, model = hear_model(loss), Model.load(SURROGATE, "formula")
    M = load_map(w, schemes=(), with_bits=False)
    cls = {k: Cluster(w, M, k, model, hear, loss, around) for k in sorted(M["cl"])}
    cands, rows = {}, {}
    for k, c in cls.items():
        c.geo = dict(c.geo, crit=M["cl"][k]["P"]["crit"])
        cands[k], rows[k] = [], []
        opts = [(b, every_crit(c, ln, xi)) for b, ln in zip(range(0, 180, 30), c.lines(c.geo["crit"]))]
        opts = [o for o in opts if o[1] is not None] or [(None, c.rows0)]   # none crosses once: CHORD's pass
        for b, r in opts:
            new, _, _ = fit(r, c.geo["S"], c.ch, WINDOW)
            p = np.array([[float(x["x"]), float(x["y"])] for x in r])
            h0, h1 = math.atan2(*(p[1] - p[0])[::-1]), math.atan2(*(p[-1] - p[-2])[::-1])
            cands[k].append(dict(L=float(new[-1]["t"]) * V1, poses=[((*p[0], h0), (*p[-1], h1)),
                                                                     ((*p[-1], h1 + math.pi), (*p[0], h0 + math.pi))]))
            rows[k].append((b, r))
    picks, order = choose(tuple(M["bs"]), cands, {k: len(M["cl"][k]["P"]["crit"]) for k in cls})
    build(w, out, {k: rows[k][c][1] for k, c in picks.items()})
    bearing = {k: rows[k][c][0] for k, c in picks.items()}
    print("dtsp-n + river: " + ", ".join(f"C{k} {bearing[k]} deg" for k, _, _ in order), flush=True)
    json.dump(dict(work=os.path.abspath(w), xi=xi, dtspnRiver=True, bearing=bearing, order=[k for k, _, _ in order]),
              open(f"{out}/lm.json", "w"), indent=1)


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


def plan_lm(w, out, R, theta, rounds, free=False, xi=None, dtspn_=False, weight="uniform", wmin=0.0):
    env, loss, around = context(w)
    if xi == "auto":   # draft v5 eq. (5): within omega, rho and the direct-hearing reach
        xi = min(OMEGA, R_TURN, R50[env])
    hear, model = hear_model(loss), Model.load(SURROGATE, "formula")
    M = load_map(w, schemes=(), with_bits=False)
    cls = {k: Cluster(w, M, k, model, hear, loss, around) for k in sorted(M["cl"])}
    crit = {k: M["cl"][k]["P"]["crit"] for k in cls}
    wc = None
    if weight == "cl":   # item 187: a critical cell weighs its strongest node's score over the map's mean
        mu = float(np.mean([around[h] for k in crit for h in crit[k]]))
        wc = {h: around[h] / mu for k in crit for h in crit[k]}
    wk = {k: sum(wc[h] for h in crit[k]) if wc else float(len(crit[k])) for k in cls}
    lines, bearing = {}, {}
    if dtspn_:
        lines, bearing, order, nb = dtspn(cls, tuple(M["bs"]), wk, xi)
        n_after = weight_after(order, wk)
        print("dtsp-n: " + ", ".join(f"C{k} {bearing[k]} deg" for k in order), flush=True)
    else:
        n_after, nb, order = order_after(w)
    log = []
    for rnd in range(rounds):
        res = {k: c.improve(R, theta, n_after[k], nb[k], free, xi, lines.get(k), wc, wmin) for k, c in cls.items()}
        build(w, out, {k: r[1]["rows"] for k, r in res.items()})
        log.append(dict(round=rnd + 1, order=order, n_after=n_after, clusters={
            k: dict(pulls=[list(h) for h in r[0]], dur=[round(r[2]["dur"], 1), round(r[1]["dur"], 1)],
                    ready=[round(float(np.mean(list(r[2]["ready"].values()))), 1),
                           round(float(np.mean(list(r[1]["ready"].values()))), 1)],
                    river=[round(float(np.mean(list(r[2]["T"].values()))), 1),
                           round(float(np.mean(list(r[1]["T"].values()))), 1)],
                    transits=[round(r[2]["tin"] + r[2]["tout"], 1), round(r[1]["tin"] + r[1]["tout"], 1)],
                    own=[len(r[2]["own"]), len(r[1]["own"])], crit=len(r[1]["ready"])) for k, r in res.items()}))
        for k, r in sorted(res.items()):
            print(f"round {rnd + 1} C{k}: {len(r[0])} insertions, pass {r[2]['dur']:.0f} -> {r[1]['dur']:.0f} s, "
                  f"transits {r[2]['tin'] + r[2]['tout']:.0f} -> {r[1]['tin'] + r[1]['tout']:.0f} s, "
                  f"mean ready {np.mean(list(r[2]['ready'].values())):.0f} -> {np.mean(list(r[1]['ready'].values())):.0f} s "
                  f"(River {np.mean(list(r[2]['T'].values())):.0f} -> {np.mean(list(r[1]['T'].values())):.0f} s, "
                  f"own decode {len(r[2]['own'])} -> {len(r[1]['own'])} of {len(r[1]['ready'])}), N_after {n_after[k]}",
                  flush=True)
        n_after, nb, order = order_after(out)
        if wc:
            n_after = weight_after(order, wk)
    json.dump(dict(work=os.path.abspath(w), R=R, xi=xi, theta=theta, free=free, dtspn=dtspn_, weight=weight, wmin=wmin,
                   bearing=bearing, rounds=log), open(f"{out}/lm.json", "w"), indent=1)


def score(w, mode, draws):
    """T* of every draw on folder w (see the module docstring), and team 1's tour."""
    C = L.clues()
    Cq = [dict(c, w=1.0) for c in C]
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    M = load_map(w, schemes=("rf",)) if mode == "ns3" else load_map(w, schemes=(), with_bits=False)
    M["name"], M["windowAt"], M["rs"] = R.mapname(w), "crit", runseed(w)
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
    prng = np.random.default_rng(int.from_bytes(hashlib.sha256(M["name"].encode() + R.rs_tag(M)).digest()[:4], "little"))
    Ts = []
    for d in range(draws * (M["rs"] - 1), draws * M["rs"]):   # simulation seed R: its own block of draws (item 188)
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
    p.add_argument("--xi", default=None, help="disc radius (m) or auto; default R/2")
    p.add_argument("--theta", type=float, default=1.0)
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--free", action="store_true", help="the CH not required: R-net + lines (item 179)")
    p.add_argument("--dtspn", action="store_true", help="start from a DTSP-N tour through the CH discs (item 187)")
    p.add_argument("--weight", choices=("uniform", "cl"), default="uniform",
                   help="critical-cell weight: 1, or its strongest node's score over the map's mean (item 187)")
    p.add_argument("--wmin", type=float, default=0.0, help="--dtspn: only cells of at least this weight are pulled")
    p.add_argument("--dtspnRiver", action="store_true", help="baseline DTSP-N + River instead of LM-Tour (item 187)")
    s = sub.add_parser("score")
    s.add_argument("works")
    s.add_argument("--mode", choices=("pred", "ns3"), required=True)
    s.add_argument("--draws", type=int, default=100)
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "plan" and a.dtspnRiver:
        plan_dr(a.work, a.out, a.xi if a.xi in (None, "auto") else float(a.xi))
        return
    if a.cmd == "plan":
        plan_lm(a.work, a.out, a.R, a.theta, a.rounds, a.free, a.xi if a.xi in (None, "auto") else float(a.xi),
                a.dtspn, a.weight, a.wmin)
        return
    rows = []
    for w in a.works.split(","):
        Ts, t1, rd = score(w, a.mode, a.draws)
        env = open(f"{w}/env.txt").read().strip() if os.path.exists(f"{w}/env.txt") else "open"
        d0 = a.draws * (runseed(w) - 1)
        rows += [dict(work=w, map=R.mapname(w), env=env, seed=runseed(w), mode=a.mode, draw=d0 + d, Tstar=round(t, 1),
                      team1=round(t1, 1), riverReady=round(rd, 1)) for d, t in enumerate(Ts)]
        print(f"{w} [{a.mode}]: T* {np.mean(Ts):.0f} s (sd {np.std(Ts):.0f}), team 1 {t1:.0f} s, "
              f"mean River ready {rd:.0f} s", flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(f"{a.out}.csv", "w") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        wr.writeheader()
        wr.writerows(rows)


if __name__ == "__main__":
    main()
