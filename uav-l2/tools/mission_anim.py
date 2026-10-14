"""Export one whole mission, every step of every mechanism, for the animated player (CLAUDE.md §8 item 71).

    python3 tools/mission_anim.py --work W/k4 --clusters 4 --seed 2 --trace W/k4/tr --out docs/anim/mission.json

WORK is a mission.py folder whose clusters were also run with uav-coop2-river --trace=TRACE/tK (River prepared,
same frozen binary: results identical to the campaign). The policy shown is l3first / early / score with the
LoRa uplink at the CH (mission_policy.py); the draw is the first that needs more than one team-2 visit.
Coordinates in metres (rounded), times in seconds from team 1's take-off.
"""
import argparse, csv, json, math, os, random, sys
from collections import defaultdict, deque

import numpy as np

from map_gen import NB, add_args, centre, generate
from partition import partition
from mission import bearings
from mission_report import load_map
import mission_policy as MP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist  # noqa: E402

BIN_RIVER, SAMPLES_PASS, BIN_HELD = 0.25, 24, 0.5


def main():
    ap = argparse.ArgumentParser()
    for k in ("work", "trace", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--clusters", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    a = ap.parse_args()
    w = a.work
    # ---- 1-3 the domain, as mission.py grew it
    p = argparse.ArgumentParser()
    add_args(p)
    g_args = p.parse_args([])
    g_args.seed, g_args.cells, g_args.lakes, g_args.lakeCells = a.seed, 80 * a.clusters, a.clusters, 10
    g = generate(g_args, random.Random(a.seed))
    final = g["final"]
    land = set(g["domain"])
    owner, med, _, _ = partition(land, 80, random.Random(a.seed))
    saved = {(int(r["q"]), int(r["r"])): int(r["cluster"]) for r in csv.DictReader(open(f"{w}/clusters.csv"))}
    assert {h: c + 1 for h, c in owner.items()} == saved, "partition does not reproduce clusters.csv"
    idx = {h: i for i, h in enumerate(final)}
    # reveal order inside each cluster: hop distance from its medoid
    dist = {}
    for i, m in enumerate(med):
        mine = {h for h in land if owner[h] == i}
        d, todo = {m: 0}, deque([m])
        while todo:
            x = todo.popleft()
            for dq, dr in NB:
                n = (x[0] + dq, x[1] + dr)
                if n in mine and n not in d:
                    d[n] = d[x] + 1
                    todo.append(n)
        dist.update(d)
    cells = []
    for i, h in enumerate(final):
        cx, cy = centre(h)
        cells.append([round(cx), round(cy), 0 if i < g["grown"] else 1, 1 if h in g["lake_set"] else 0,
                      owner[h] + 1 if h in owner else 0, dist.get(h, 0)])
    # ---- the mission, its clusters and plans
    M = load_map(w, schemes=("rf",))
    legs, back = MP.tour(M, "l3first")
    nodes, clusters = [], {}
    cellof_node = {}
    for k, C in sorted(M["cl"].items()):
        P = C["P"]
        for n in C["geo"]["nodes"]:
            role = 2 if n["isCH"] == "1" else 1 if n["isCL"] == "1" else 0
            cellof_node[(k, int(n["id"]))] = idx[(int(n["q"]), int(n["r"]))]
            nodes.append([round(float(n["x"])), round(float(n["y"])), k, role])
        ch = next(n for n in C["geo"]["nodes"] if n["isCH"] == "1")
        bj = json.load(open(f"{w}/c{k}-bearing.json"))
        scan = sorted(bearings(w, k))
        circ = {}
        for kk in P["crit"]:
            circ[idx[kk]] = [idx[m] for m, G, src in P["circle"][kk]]
        clusters[k] = dict(ch=[round(float(ch["x"])), round(float(ch["y"]))], bearing=bj["bearing"],
                           scan=[[b, i] for b, i in scan], path=[[round(x), round(y)] for x, y in C["geo"]["path"]],
                           axe=[idx[h] for h in P["axe"]], river=[idx[h] for h in sorted(P["river"])],
                           bank=sorted({idx[b] for (x, s_), b in P["bank"].items() if b != x}),
                           crit=[idx[h] for h in P["crit"]], chCell=idx[P["ch"]], circle=circ, D=C["D"])
    leg = {l[0]: l for l in legs}
    # ---- 4 pass: share of D each cell holds (any node) along the pass
    for k, C in sorted(M["cl"].items()):
        P, nodesk = C["P"], C["geo"]["nodes"]
        N = len(C["geo"]["uav"])
        bits = np.unpackbits(np.fromfile(f"{w}/pass{k}-bits-r1.bin", dtype=np.uint8).reshape(len(nodesk), -1),
                             axis=1, bitorder="little")[:, :N].astype(bool)
        inD = np.zeros(N, bool)
        for x in P["axe"]:
            inD[P["seg"][x][0]:P["seg"][x][-1] + 1] = bits[:, P["seg"][x][0]:P["seg"][x][-1] + 1].any(axis=0)
        mem = defaultdict(list)
        for i, n in enumerate(nodesk):
            mem[idx[(int(n["q"]), int(n["r"]))]].append(i)
        _, st, en, t0, t1 = leg[k]
        rev = math.dist(st, C["geo"]["path"][0]) > math.dist(en, C["geo"]["path"][0])
        cuts = np.linspace(0, N, SAMPLES_PASS + 1).astype(int)[1:]
        share = {}
        for c, ms in mem.items():
            got = bits[ms].any(axis=0) & inD
            if rev:   # flown the other way: the packets reach this cell in the opposite order
                got = got[::-1]
            cum = np.cumsum(got)
            share[c] = [round(float(cum[x - 1]) / int(inD.sum()), 3) for x in cuts]
        clusters[k].update(enter=round(t0, 2), leave=round(t1, 2), passShare=share)
    # ---- 5 River: cell-to-cell flows per bin, CL holdings per bin, completion of critical cells
    for k, C in sorted(M["cl"].items()):
        t0 = clusters[k]["leave"]
        flows = defaultdict(int)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-hops.csv")):
            ca, cb = cellof_node[(k, int(r["from"]))], cellof_node[(k, int(r["to"]))]
            flows[(int(float(r["t"]) / BIN_RIVER), ca, cb, r["phase"])] += 1
        phases = ["gather", "bankfill", "circlefill", "pull", "control"]
        clusters[k]["flows"] = sorted([b, ca, cb, phases.index(ph), n] for (b, ca, cb, ph), n in flows.items())
        Dn = clusters[k]["D"]
        held = defaultdict(list)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-held.csv")):
            held[idx[(int(r["q"]), int(r["r"]))]].append(float(r["t"]))
        done = {idx[h]: float(r["doneS"]) for h, r in C["res"]["rf"].items()}
        T = max(done.values())
        nb = int(T / BIN_HELD) + 2
        clusters[k]["held"] = {c: [round(float(np.sum(np.array(ts) <= b * BIN_HELD)) / Dn, 3) for b in range(nb)]
                               for c, ts in held.items()}
        clusters[k]["done"] = {c: round(v, 2) for c, v in done.items()}
    # ---- 6-7 matching, LoRa at the CH, suspects, team 2
    D = None
    for sd in range(1, 400):
        D = MP.draws(M, 1, sd)[0]
        r_, tr = MP.run(M, legs, D, ("l3first", "early", "score"))
        if r_["visits"] >= 2:
            break
    lora = {}
    for k, C in M["cl"].items():
        ch = C["P"]["ch"]
        ph = D["phase"][k]
        atch = {idx[h]: clusters[k]["leave"] + float(C["res"]["rf"][h]["doneS"]) + MP.MATCH + MP.HOP * hexdist(h, ch)
                for h in C["P"]["crit"]}
        sends = sorted({ph + max(0, math.ceil((t - ph) / MP.GAP)) * MP.GAP for t in atch.values()})
        lora[k] = dict(phase=round(ph, 2), atCH={c: round(v, 2) for c, v in atch.items()},
                       sends=[round(s, 2) for s in sends])
        clusters[k]["lora"] = lora[k]
    sus = [[idx[x[1]], x == D["true"], round(D["score"][x], 3)] for x in [D["true"]] + D["false"]]
    team2 = [[e[0], round(e[1], 2), [round(e[2][0]), round(e[2][1])]] for e in tr]
    out = dict(cells=cells, nodes=nodes, clusters=clusters, bs=[round(v) for v in M["bs"]],
               legs=[[l[0], [round(v) for v in l[1]], [round(v) for v in l[2]], round(l[3], 2), round(l[4], 2)]
                     for l in legs], back=round(back, 2), sus=sus, team2=team2, end=round(r_["end"], 2),
               dep=round(r_["dep"], 2), params=dict(match=MP.MATCH, air=MP.AIR, gap=MP.GAP, hover=MP.HOVER, v1=MP.V1,
                                                    v2=MP.V2, binRiver=BIN_RIVER, binHeld=BIN_HELD,
                                                    samplesPass=SAMPLES_PASS, R=100))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB; {len(cells)} cells, {len(nodes)} nodes, "
          f"{sum(len(c['flows']) for c in clusters.values())} flow bins; draw needs {r_['visits']} visits, "
          f"team 2 leaves {r_['dep']:.0f} s, ends {r_['end']:.0f} s")


if __name__ == "__main__":
    main()
