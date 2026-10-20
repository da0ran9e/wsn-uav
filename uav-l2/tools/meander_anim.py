"""Export one MEANDER mission, every step, for the animated player (CLAUDE.md §8 items 104-105).

    python3 tools/meander_anim.py --work MM/k4 --clusters 4 --seed 2 --trace MM/k4/tr --out docs/anim/meander.json

WORK is a meander_mission.py folder whose clusters were also run with uav-coop2-river --trace=TRACE/tK (River
prepared, same binary and plan: results identical). As tools/mission_anim.py, with MEANDER's own phase 0 and
curved flight lines:
  cells     x, y, grown/filled, lake, cluster, reveal rank (by s inside the cluster)
  meander   per cell s, n (m), lane, piece before merging, fragment; the spine of each land piece (cell ids)
  clusters  CH, the lane centre curve (path0) and the line bent through the CH (path), both every ~10 m; CH
            offset and sigma factor; River plan; pass shares; River flows and CL holdings (ns-3 trace); LoRa
The policy shown is l3first / early / score; the draw is the first that needs more than one team-2 visit.
Coordinates in metres (rounded), times in seconds from team 1's take-off.
"""
import argparse, csv, json, math, os, sys
from collections import defaultdict

import numpy as np

from map_gen import centre
from meander import flight_curve, partition_meander
from mission_report import load_map
from restructure import domain
import mission_policy as MP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hexdist, plan  # noqa: E402

BIN_RIVER, SAMPLES_PASS, BIN_HELD, STEP = 0.25, 24, 0.5, 10.0


def thin(P, step=STEP):
    """Every ~step m of a polyline, both ends kept."""
    out, acc = [P[0]], 0.0
    for a, b in zip(P, P[1:]):
        acc += math.dist(a, b)
        if acc >= step:
            out.append(b); acc = 0.0
    if tuple(out[-1]) != tuple(P[-1]):
        out.append(P[-1])
    return [[round(float(x)), round(float(y))] for x, y in out]


def main():
    ap = argparse.ArgumentParser()
    for k in ("work", "trace", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--clusters", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--lane", type=float, default=4.5)
    ap.add_argument("--banks", default="local", help="the Banks the River ran with (meander_mission.py --banks)")
    a = ap.parse_args()
    w = a.work
    # ---- phase 0: the domain, then MEANDER as meander_mission.py ran it
    g = domain(a.clusters, a.seed)
    final, land = g["final"], set(g["domain"])
    owner, lane, s, n, spines, st = partition_meander(land, a.lane)
    saved = {(int(r["q"]), int(r["r"])): int(r["cluster"]) for r in csv.DictReader(open(f"{w}/clusters.csv"))}
    assert {h: c + 1 for h, c in owner.items()} == saved, "partition_meander does not reproduce clusters.csv"
    idx = {h: i for i, h in enumerate(final)}
    rank = {}
    for k in set(owner.values()):
        for i, h in enumerate(sorted((h for h in owner if owner[h] == k), key=lambda h: s[h])):
            rank[h] = i
    cells = []
    for i, h in enumerate(final):
        cx, cy = centre(h)
        cells.append([round(cx), round(cy), 0 if i < g["grown"] else 1, 1 if h in g["lake_set"] else 0,
                      owner[h] + 1 if h in owner else 0, rank.get(h, 0)])
    lanes_ = sorted(set(lane.values()))
    mc = {idx[h]: [round(s[h]), round(n[h]), lanes_.index(lane[h]), st["cut"][h], int(h in st["frag"])] for h in owner}
    meander = dict(cell=mc, spines=[[idx[h] for h in sp] for sp in spines if len(sp) > 1], lanes=len(lanes_))
    # ---- the mission, its clusters and plans
    M = load_map(w, schemes=("rf",))
    legs, back = MP.tour(M, "l3first")
    nodes, clusters, cellof_node = [], {}, {}
    for k, C in sorted(M["cl"].items()):
        P = C["P"] = plan(C["geo"], banks=a.banks, reentry=True)   # load_map plans with parallel Banks
        for nd in C["geo"]["nodes"]:
            role = 2 if nd["isCH"] == "1" else 1 if nd["isCL"] == "1" else 0
            cellof_node[(k, int(nd["id"]))] = idx[(int(nd["q"]), int(nd["r"]))]
            nodes.append([round(float(nd["x"])), round(float(nd["y"])), k, role])
        ch = next(nd for nd in C["geo"]["nodes"] if nd["isCH"] == "1")
        P0, _ = flight_curve([h for h in owner if owner[h] == k - 1], s)
        cv = json.load(open(f"{w}/c{k}-curve.json"))
        clusters[k] = dict(ch=[round(float(ch["x"])), round(float(ch["y"]))], path=thin(C["geo"]["path"]),
                           path0=thin(P0[25:-25]), chOffset=cv["chOffset"], sigmaX=cv["sigmaX"],
                           axe=[idx[h] for h in P["axe"]], river=[idx[h] for h in sorted(P["river"])],
                           bank=sorted({idx[b] for (x, s_), b in P["bank"].items() if b != x}),
                           crit=[idx[h] for h in P["crit"]], chCell=idx[P["ch"]],
                           circle={idx[kk]: [idx[m] for m, G, src in P["circle"][kk]] for kk in P["crit"]}, D=C["D"])
    leg = {l[0]: l for l in legs}
    # ---- pass: share of D each cell holds (any node) along the pass
    for k, C in sorted(M["cl"].items()):
        P, nodesk, bits, inD = C["P"], C["geo"]["nodes"], C["bits"], C["inD"]
        N = len(C["geo"]["uav"])
        mem = defaultdict(list)
        for i, nd in enumerate(nodesk):
            mem[idx[(int(nd["q"]), int(nd["r"]))]].append(i)
        _, st_, en, t0, t1 = leg[k]
        rev = math.dist(st_, C["geo"]["path"][0]) > math.dist(en, C["geo"]["path"][0])
        cuts = np.linspace(0, N, SAMPLES_PASS + 1).astype(int)[1:]
        share = {}
        for c, ms in mem.items():
            got = bits[ms].any(axis=0) & inD
            if rev:   # flown the other way: the packets reach this cell in the opposite order
                got = got[::-1]
            cum = np.cumsum(got)
            share[c] = [round(float(cum[x - 1]) / int(inD.sum()), 3) for x in cuts]
        clusters[k].update(enter=round(t0, 2), leave=round(t1, 2), rev=int(rev), passShare=share)
    # ---- River: cell-to-cell flows per bin, CL holdings per bin, completion of critical cells
    phases = ["gather", "bankfill", "circlefill", "pull", "control"]
    for k, C in sorted(M["cl"].items()):
        flows = defaultdict(int)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-hops.csv")):
            ca, cb = cellof_node[(k, int(r["from"]))], cellof_node[(k, int(r["to"]))]
            flows[(int(float(r["t"]) / BIN_RIVER), ca, cb, r["phase"])] += 1
        clusters[k]["flows"] = sorted([b, ca, cb, phases.index(ph), m] for (b, ca, cb, ph), m in flows.items())
        held = defaultdict(list)
        for r in csv.DictReader(open(f"{a.trace}/t{k}-held.csv")):
            held[idx[(int(r["q"]), int(r["r"]))]].append(float(r["t"]))
        done = {idx[h]: float(r["doneS"]) for h, r in C["res"]["rf"].items()}
        nb = int(max(done.values()) / BIN_HELD) + 2
        clusters[k]["held"] = {c: [round(float(np.sum(np.array(ts) <= b * BIN_HELD)) / clusters[k]["D"], 3)
                                   for b in range(nb)] for c, ts in held.items()}
        clusters[k]["done"] = {c: round(v, 2) for c, v in done.items()}
    # ---- matching, LoRa at the CH, suspects, team 2
    for sd in range(1, 400):
        D = MP.draws(M, 1, sd)[0]
        r_, tr = MP.run(M, legs, D, ("l3first", "early", "score"))
        if r_["visits"] >= 2:
            break
    for k, C in M["cl"].items():
        ch, ph = C["P"]["ch"], D["phase"][k]
        atch = {idx[h]: clusters[k]["leave"] + float(C["res"]["rf"][h]["doneS"]) + MP.MATCH + MP.HOP * hexdist(h, ch)
                for h in C["P"]["crit"]}
        sends = sorted({ph + max(0, math.ceil((t - ph) / MP.GAP)) * MP.GAP for t in atch.values()})
        clusters[k]["lora"] = dict(phase=round(ph, 2), atCH={c: round(v, 2) for c, v in atch.items()},
                                   sends=[round(x, 2) for x in sends])
    out = dict(cells=cells, nodes=nodes, clusters=clusters, meander=meander, bs=[round(v) for v in M["bs"]],
               legs=[[l[0], [round(v) for v in l[1]], [round(v) for v in l[2]], round(l[3], 2), round(l[4], 2)]
                     for l in legs], back=round(back, 2),
               sus=[[idx[x[1]], x == D["true"], round(D["score"][x], 3)] for x in [D["true"]] + D["false"]],
               team2=[[e[0], round(e[1], 2), [round(e[2][0]), round(e[2][1])]] for e in tr], end=round(r_["end"], 2),
               dep=round(r_["dep"], 2), params=dict(match=MP.MATCH, air=MP.AIR, gap=MP.GAP, hover=MP.HOVER, v1=MP.V1,
                                                    v2=MP.V2, binRiver=BIN_RIVER, binHeld=BIN_HELD,
                                                    samplesPass=SAMPLES_PASS, R=100, laneW=a.lane))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print(f"{a.out}: {os.path.getsize(a.out) / 1e6:.2f} MB; {len(cells)} cells, {len(nodes)} nodes, "
          f"{len(clusters)} clusters, {sum(len(c['flows']) for c in clusters.values())} flow bins; draw {sd} needs "
          f"{r_['visits']} visits, team 2 leaves {r_['dep']:.0f} s, ends {r_['end']:.0f} s")


if __name__ == "__main__":
    main()
