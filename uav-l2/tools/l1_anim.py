"""Export one mission with the layer-1 model, every step, for the animated player docs/anim/l1-replay.html
(CLAUDE.md §8 item 114).

    python3 tools/l1_anim.py --work KW/k4-s2 --trace TR/k4-s2 --method P+prog-latency-puq-stage-zero --out docs/anim/l1.json

WORK is a mission work folder (any partition) with pass bitmaps and River results; TRACE holds t<k>-hops.csv and
t<k>-held.csv of the same River runs made with river-bin --trace (results identical). The method is one of
l1_rank.py's P / B4 / P+prog variants. The draw shown is the first whose c* is not team 2's first visit and in
which team 2 stages at least once (else the first draw).
Exported (metres rounded, seconds from team 1's take-off):
  cells     x, y, lake, cluster;  nodes  x, y, cluster, role (0 node, 1 CL, 2 CH)
  clue      per clue: aspect (0 face, 1 body, 2 part), packets, importance, recognizability; the broadcast order
  clusters  CH, flight path, Axe / River / Bank / critical cells, enter, leave, River flows per 0.25 s, each
            critical cell's clues: held from its own reception (mask) and when River completed each one (s after
            leaving, -1 never), River done, gather done, LoRa phase and sends
  crit      per critical cell: verified score U, reports [time at the BS, kind (0 own reception, 1 River),
            posterior mean, sd], c*
  team2     moves [kind, t0, t1, from, to, cell]; P(c*) at each decision {cell: p}; Tstar, Tall
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict

import numpy as np

import l1_model as L
import l1_rank as R
from mission_policy import GAP, tour
from mission_report import load_map

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

BIN_RIVER, SAMPLES_PASS = 0.25, 24


def main():
    ap = argparse.ArgumentParser()
    for k in ("work", "trace", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--method", default="P+prog-latency-puq-stage-zero")
    ap.add_argument("--draw", type=int, default=-1, help="the draw to show (default: chosen as above)")
    a = ap.parse_args()
    w = a.work
    M = load_map(w, schemes=("rf",))
    M["name"] = R.mapname(w)
    C = L.clues()
    seqs = {"interleaved": L.order(C, "interleaved"), "grouped": L.order(C, "grouped")}
    order = "grouped" if "grouped" in a.method else "interleaved"
    tk = next((o for o in a.method.split("-") if o in ("short", "latency", "seam")), "l3first")
    legs, back = tour(M, tk)
    tours = {tk: (legs, back), "l3first": tour(M, "l3first")}
    hold = R.holdings(M, C, seqs)
    # ---- the draw: reproduce l1_rank's phases (same seed sequence), pick one worth watching
    import hashlib
    seedm = int.from_bytes(hashlib.sha256(M["name"].encode()).digest()[:4], "little")
    prng = np.random.default_rng(seedm)
    phases = [{k: float(prng.uniform(0, GAP)) for k in sorted(M["cl"])} for _ in range(100)]
    crits = [(k, h) for k in sorted(M["cl"]) for h in M["cl"][k]["P"]["crit"]]
    pos = {x: tuple(M["cl"][x[0]]["geo"]["c"][x[1]]) for x in crits}
    prior = L.calib(C, np.ones(len(C), bool))[3]
    tm = R.match_time(R.DEVICE, len(C), L.M)

    def simulate(d):
        U, mv = R.world(M["name"], d, crits, C)
        star = max(crits, key=lambda x: U[x])
        leave = {l[0]: l[4] for l in legs}
        reps, info = {}, {}
        for kind, col, idx in (("direct", "gatherDoneS", 1), ("river", "doneS", 0)):
            ready = {x: leave[x[0]] + float(M["cl"][x[0]]["res"]["rf"][x[1]][col]) + tm for x in crits}
            arr = R.lora(M, ready, phases[d])
            for x in crits:
                m = hold[x][order][idx]
                S = float(L.report(mv[x], C, m)[0])
                al, be, sd, _ = L.calib(C, m, truth=C)
                post = (al + be * S, max(sd, 1e-4)) if m.any() else (al, sd)
                info.setdefault(x, []).append((arr[x], 0 if kind == "direct" else 1, post, ready[x]))
        base = a.method.split("-")[0]
        for x in crits:
            ev = [e for e in info[x] if base == "P+prog" or (e[1] == 1) == (base == "P")]
            reps[x] = [(e[0], e[2]) for e in sorted(ev, key=lambda e: (e[0], e[1]))]
        trace = []
        dep, rule, stg, beta = R.policy(a.method.split("-")[1:])
        out = R.team2(M["bs"], pos, reps, U, prior, star, dep, rule, stg, trace, beta, "redir" in a.method.split("-"))
        return U, star, info, trace, out

    if a.draw >= 0:
        d = a.draw
    else:
        d = next((d for d in range(100) if (lambda s: s[4][2] >= 2 and any(e[0] == "stage" for e in s[3]))(simulate(d))), 0)
    U, star, info, trace, (Ts, Ta, rank, dep, sin) = simulate(d)
    # ---- export
    idx = {}
    cells = []
    for r in csv.DictReader(open(f"{w}/domain-cells.csv")):
        h = (int(r["q"]), int(r["r"]))
        idx[h] = len(cells)
        cells.append([round(float(r["cx"])), round(float(r["cy"])), 0 if r["type"] == "land" else 1,
                      M["owner"].get(h, 0)])
    nodes, clusters, cellof_node = [], {}, {}
    st, en, Q = L.layout(C, seqs[order])
    for k, cl in sorted(M["cl"].items()):
        P = cl["P"]
        for n in cl["geo"]["nodes"]:
            role = 2 if n["isCH"] == "1" else 1 if n["isCL"] == "1" else 0
            cellof_node[(k, int(n["id"]))] = idx[(int(n["q"]), int(n["r"]))]
            nodes.append([round(float(n["x"])), round(float(n["y"])), k, role])
        ch = next(n for n in cl["geo"]["nodes"] if n["isCH"] == "1")
        lg = next(l for l in legs if l[0] == k)
        # the clue copy on the Axe window (as l1_rank.holdings) and the packets each cell heard along the pass
        allp = np.array(sorted(s for x in P["axe"] for s in P["seg"][x]))
        c0 = int(np.argmin(np.linalg.norm(cl["geo"]["uav"] - [float(ch["x"]), float(ch["y"])], axis=1)))
        n_ = len(allp)
        i0 = min(max(int(np.searchsorted(allp, c0)) - R.WINDOW // 2, 0), n_ - R.WINDOW) if n_ > R.WINDOW else 0
        win = allp[i0:i0 + Q]
        rev = math.dist(lg[1], cl["geo"]["path"][0]) > math.dist(lg[2], cl["geo"]["path"][0])
        cuts = np.linspace(0, len(cl["geo"]["uav"]), SAMPLES_PASS + 1).astype(int)[1:]
        share = {}
        for h, ms in cl["mem"].items():
            got = cl["bits"][ms].any(axis=0)
            gw = np.zeros(len(got), bool)
            gw[win] = got[win]
            if rev:
                gw = gw[::-1]
            cum = np.cumsum(gw)
            share[idx[h]] = [round(float(cum[x - 1]) / max(1, len(win)), 3) for x in cuts]
        # River: flows per bin, and when each clue of the window copy was complete at each critical cell
        flows = defaultdict(int)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-hops.csv")):
            ca, cb = cellof_node[(k, int(r["from"]))], cellof_node[(k, int(r["to"]))]
            flows[(int(float(r["t"]) / BIN_RIVER), ca, cb, r["phase"])] += 1
        phases_ = ["gather", "bankfill", "circlefill", "pull", "control"]
        arr = defaultdict(dict)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-held.csv")):
            arr[(int(r["q"]), int(r["r"]))][int(r["s"])] = float(r["t"])
        crit = {}
        for h in P["crit"]:
            x = (k, h)
            dm = hold[x][order][1]
            done = []
            for j in range(len(C)):
                if i0 + en[j] > n_:
                    done.append(-1)
                    continue
                ts = [arr[h].get(int(s), None) for s in allp[i0 + st[j]:i0 + en[j]]]
                done.append(-1 if any(v is None for v in ts) else round(max(ts), 2))
            crit[idx[h]] = dict(direct=[int(v) for v in dm], riverAt=done,
                                doneS=float(cl["res"]["rf"][h]["doneS"]), gatherS=float(cl["res"]["rf"][h]["gatherDoneS"]))
        sends = sorted({e[0] - R.AIR for x in crits if x[0] == k for e in info[x]})
        clusters[k] = dict(ch=[round(float(ch["x"])), round(float(ch["y"]))],
                           path=[[round(px), round(py)] for px, py in cl["geo"]["path"]],
                           axe=[idx[h] for h in P["axe"]], river=[idx[h] for h in sorted(P["river"])],
                           bank=sorted({idx[b] for (x, s_), b in P["bank"].items() if b != x}),
                           chCell=idx[P["ch"]], enter=round(lg[3], 2), leave=round(lg[4], 2), passShare=share,
                           flows=sorted([b, ca, cb, phases_.index(ph), nn] for (b, ca, cb, ph), nn in flows.items()),
                           crit=crit, lora=dict(phase=round(phases[d][k], 2), sends=[round(s, 2) for s in sends]))
    critx = {}
    for x in crits:
        critx[idx[x[1]]] = dict(U=round(U[x], 4), star=int(x == star),
                                reports=[[round(e[0], 2), e[1], round(e[2][0], 4), round(e[2][1], 4), round(e[3], 2)]
                                         for e in info[x]])
    t2 = []
    psnap = []
    for e in trace:
        if e[0] == "p":
            psnap.append([round(e[1], 2), {str(idx[c[1]]) if c != "unreported" else "u": round(v, 4)
                                           for c, v in e[2].items()}])
        elif e[0] in ("fly", "stage", "back"):
            t2.append([e[0], round(e[1], 2), round(e[2], 2), [round(e[3][0]), round(e[3][1])],
                       [round(e[4][0]), round(e[4][1])], idx[e[5][1]] if e[0] == "fly" else -1])
        else:
            t2.append(["verify", round(e[1], 2), round(e[2], 2), None, None, idx[e[3][1]]])
    out = dict(cells=cells, nodes=nodes, clusters=clusters, crit=critx, bs=[round(v) for v in M["bs"]],
               legs=[[l[0], [round(v) for v in l[1]], [round(v) for v in l[2]], round(l[3], 2), round(l[4], 2)]
                     for l in legs], back=round(back, 2),
               clue=[[c["t"], int(en[j] - st[j]), round(c["w"], 3), round(c["r"], 3)] for j, c in enumerate(C)],
               order=[int(j) for j in seqs[order]], team2=t2, psnap=psnap, star=idx[star[1]], Tstar=round(Ts, 2),
               Tall=round(Ta, 2), dep=round(dep, 2), rank=rank, draw=d, method=a.method,
               params=dict(gap=GAP, air=R.AIR, verify=round(R.VERIFY, 2), v1=50.0, v2=R.V2, binRiver=BIN_RIVER,
                           samplesPass=SAMPLES_PASS, R=100, match=round(tm, 3)))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB; draw {d}: c* cell {idx[star[1]]}, team 2 leaves {dep:.0f} s, "
          f"verifies c* at {Ts:.0f} s (visit {rank}), all at {Ta:.0f} s; {len(psnap)} decisions, "
          f"{sum(1 for e in t2 if e[0] == 'stage')} staging moves")


if __name__ == "__main__":
    main()
