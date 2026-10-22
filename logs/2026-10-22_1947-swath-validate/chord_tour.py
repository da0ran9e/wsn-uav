"""Geometry only (CLAUDE.md §8 item 136): k-medoids clusters, each flown straight across its CH, but the bearings
chosen jointly with team 1's tour (CHORD-T) instead of each cluster's longest in-cluster line on its own.

    python3 chord_tour.py WORK [WORK ...]        (mission.py work folders: clusters, deploy, plans)

Candidates per cluster: bearings (2 degree steps) whose in-cluster flight is at least FRAC of the longest and at least
one clue set long, at least 10 degrees apart, the best NB. Leg = entry - RHO .. exit + RHO along the bearing (the
deploy's lead-in / lead-out), either way round. Held-Karp over (cluster, bearing, direction), Dubins transits (radius
RHO, free heading at the BS), least sum_k n_k leave_k (n_k: the cluster's critical cells), as mission_policy latency.
"""
import math, sys
sys.path.insert(0, "/home/user/wsn-uav/uav-l2/tools")
import csv, json
import dubins
from map_gen import cell_at
from mission import bearings
from mission_report import load_map

RHO, V1, NB = 50.0 ** 2 / 9.80665, 50.0, 6
FRAC, CLUE_M = float(sys.argv.pop(1)), float(sys.argv.pop(1)) * 4041 * 0.5


def legs(W, k):
    cells = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{W}/c{k}-cells.csv"))}
    ch = next(r for r in csv.DictReader(open(f"{W}/c{k}-nodes-s35.csv")) if r["isCH"] == "1")
    cx, cy = float(ch["x"]), float(ch["y"])
    sc = bearings(W, k)
    top = sc[0][1]
    pick = []
    for b, ins in sc:
        if ins < FRAC * top or (ins < CLUE_M and b != sc[0][0]):
            continue
        if all(min(abs(b - p), 180 - abs(b - p)) >= 10 for p, _ in pick):
            pick.append((b, ins))
        if len(pick) == NB:
            break
    out = []
    for b, ins in pick:
        th = math.radians(b)
        far = [max([s for s in range(0, 8000, 5) if cell_at(cx + sg * s * math.cos(th), cy + sg * s * math.sin(th)) in cells]
                   or [0]) for sg in (1, -1)]
        a = (cx - (far[1] + RHO) * math.cos(th), cy - (far[1] + RHO) * math.sin(th))
        z = (cx + (far[0] + RHO) * math.cos(th), cy + (far[0] + RHO) * math.sin(th))
        L = math.dist(a, z)
        out.append(dict(b=b, ins=ins, L=L, poses=[((*a, th), (*z, th)), ((*z, th + math.pi), (*a, th + math.pi))]))
    return out


def best_tour(bs, C, n):
    """C[k]: list of candidate legs; returns (latency sum, back time, order [(k, cand, dir)])."""
    ks = sorted(C)
    st = {}
    for i, k in enumerate(ks):
        for c, g in enumerate(C[k]):
            for d in (0, 1):
                t = (dubins.free_start(bs, g["poses"][d][0], RHO) + g["L"]) / V1
                st[(1 << i, i, c, d)] = (n[k] * t, t, None)
    for mask in range(1, 1 << len(ks)):
        for (m, i, c, d), (lat, t, _) in [(x, v) for x, v in st.items() if x[0] == mask]:
            end = C[ks[i]][c]["poses"][d][1]
            for j, k2 in enumerate(ks):
                if mask >> j & 1:
                    continue
                for c2, g in enumerate(C[k2]):
                    for e in (0, 1):
                        t2 = t + (dubins.length(end, g["poses"][e][0], RHO) + g["L"]) / V1
                        key = (mask | 1 << j, j, c2, e)
                        val = lat + n[k2] * t2
                        if key not in st or val < st[key][0]:
                            st[key] = (val, t2, (m, i, c, d))
    full = (1 << len(ks)) - 1
    fin = [(v[0], v[1] + dubins.free_end(C[ks[x[1]]][x[2]]["poses"][x[3]][1], bs, RHO) / V1, x)
           for x, v in st.items() if x[0] == full]
    lat, back, x = min(fin)
    order = []
    while x:
        order.append((ks[x[1]], x[2], x[3]))
        x = st[x][2]
    return lat, back, order[::-1]


for W in sys.argv[1:]:
    M = load_map(W, schemes=(), with_bits=False)
    n = {k: len(C["P"]["crit"]) for k, C in M["cl"].items()}
    C = {k: legs(W, k) for k in M["cl"]}
    longest = {k: [c[0]] for k, c in C.items()}
    l0, b0, _ = best_tour(M["bs"], longest, n)
    l1, b1, o1 = best_tour(M["bs"], C, n)
    N = sum(n.values())
    print(f"{W.rsplit('/', 1)[-1]}: mean critical leave {l0 / N:.0f} -> {l1 / N:.0f} s, back {b0:.0f} -> {b1:.0f} s; "
          f"candidates {[len(c) for c in C.values()]}, changed {sum(c != 0 for _, c, _ in o1)}/{len(o1)}", flush=True)
