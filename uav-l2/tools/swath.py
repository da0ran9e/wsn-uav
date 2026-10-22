"""SWATH-K, phase 0 for layer 2 (CLAUDE.md §8 items 115-118, 135): one boustrophedon over the whole land, cut
into K clusters along it, so team 1 flies a single continuous line and turns only at the ends of the lanes.

  1  lanes: the land cut into straight strips L cells wide (L = 6: an 80-cell cluster is then about 2 km long, as
     much Axe as one copy of the clue set), across bearing th with offset off
  2  route: each lane flown along its centre line (clipped into its cells) from its first cell to its last,
     alternately both ways; one lane's end joined to the next lane's start by the shortest Dubins path of the fixed
     wing's minimum radius RHO (dubins.path_csc); lakes and gaps are flown over (soft obstacles)
  3  th and off: the shortest route, BS -> route -> BS included (Dubins at both ends). (Asking instead that every
     cluster's stretch carry a copy of the clue set over its own cells was tried on k4-s2, k6-s9, k8-s10: no route
     does on the lake maps, and the fewest short clusters cost up to 6 km more; River's Axe takes the packets sent
     next to the cluster instead, river_plan near / mission.py --axeNear)
  4  chain: the land cells in route order (lane by lane, along the flight); cut into K consecutive runs of about
     N / K cells, repaired into connected clusters (cut)
Each cluster is then flown along its own stretch of the route (swath_mission.py).

    python3 tools/swath.py --clusters 8 --seed 10     # route and cut of one map, printed
"""
import argparse, math

import numpy as np

from map_gen import R as R_CELL, W, centre
from partition import pieces, rebalance
from restructure import CAP, domain, touching
import dubins

RHO = 50.0 * 50.0 / 9.80665   # minimum turn radius at 50 m/s, 45 degree bank (meander.RHO)
STEP = 2.0                    # route vertices, m
CLUE = math.ceil(400 * 1000 / 99)   # one copy of the clue set, 99 B packets (mission.py --windowKB 400)


def route(land, th, L, off):
    """The serpentine over land for bearing th (rad) and offset off: dict with poly (vertices <= STEP apart), s
    (arc length at each vertex), pos {cell: route coordinate of its projection}, lanes [(lane id, cells)]."""
    u, nv = np.array([math.cos(th), math.sin(th)]), np.array([-math.sin(th), math.cos(th)])
    cells = sorted(land)
    P = np.array([centre(h) for h in cells])
    a, c = P @ u, P @ nv
    lane = np.floor((c - c.min()) / (L * W) + off).astype(int)
    ids = sorted(set(lane))
    lo, hi, cc = {}, {}, {}
    for i in ids:
        m = lane == i
        lo[i], hi[i] = a[m].min() - W / 2, a[m].max() + W / 2
        cc[i] = float(np.clip(c.min() + (i - off + 0.5) * L * W, c[m].min(), c[m].max()))
    for i, j in zip(ids, ids[1:]):               # lanes too close for a turn of radius RHO: move the later out
        if cc[j] - cc[i] < 2 * RHO:
            cc[j] = cc[i] + 2 * RHO
    dirs = {i: 1 if n % 2 == 0 else -1 for n, i in enumerate(ids)}
    pts, pos, order = [], {}, []
    s0 = 0.0
    for n, i in enumerate(ids):
        d = dirs[i]
        a0, a1 = (lo[i], hi[i]) if d > 0 else (hi[i], lo[i])
        k = max(2, math.ceil(abs(a1 - a0) / STEP) + 1)
        seg = np.outer(np.linspace(a0, a1, k), u) + cc[i] * nv
        if pts:
            seg = seg[1:]
        mine = [h for h, li in zip(cells, lane) if li == i]
        for h in mine:
            pos[h] = s0 + (float(np.dot(centre(h), u)) - a0) * d
        order.append((i, sorted(mine, key=lambda h: (pos[h], h))))
        pts.append(seg)
        s0 += abs(a1 - a0)
        if n + 1 < len(ids):                     # the shortest turn from this lane's end into the next lane
            j = ids[n + 1]
            b0 = lo[j] if dirs[j] > 0 else hi[j]
            E, S = a1 * u + cc[i] * nv, b0 * u + cc[j] * nv
            h = math.atan2(*(d * u)[::-1])
            turn, L_ = dubins.path_csc((*E, h), (*S, h + math.pi), RHO, STEP)
            pts.append(np.array(turn[1:]))
            s0 += L_
    poly = np.vstack(pts)
    poly = poly[np.r_[True, np.linalg.norm(np.diff(poly, axis=0), axis=1) > 1e-9]]   # a zero-sweep arc repeats
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    return dict(poly=poly, s=s, pos=pos, lanes=order, th=th, L=L, off=off)


def heading(poly, i, back=False):
    v = poly[i] - poly[i - 5] if back else poly[i + 5] - poly[i]
    return math.atan2(v[1], v[0])


def routes(land, bs, L=6.0):
    """Every bearing (5 degree steps) and offset, shortest BS -> route -> BS first: [(metres, deg, off, route)]."""
    out = []
    for deg in range(0, 180, 5):
        for off in (0.0, 1 / 3, 2 / 3):
            r = route(land, math.radians(deg), L, off)
            P = r["poly"]
            tot = r["s"][-1] + min(
                dubins.free_start(bs, (*P[0], heading(P, 0)), RHO) + dubins.free_end((*P[-1], heading(P, len(P) - 1, True)), bs, RHO),
                dubins.free_start(bs, (*P[-1], heading(P, len(P) - 1, True) + math.pi), RHO)
                + dubins.free_end((*P[0], heading(P, 0) + math.pi), bs, RHO))
            out.append((tot, deg, off, r))
    return sorted(out, key=lambda x: x[0])


def cells_at(P):
    """map_gen.cell_at for an array of points."""
    q, r = (math.sqrt(3) / 3 * P[:, 0] - P[:, 1] / 3) / R_CELL, (2 / 3 * P[:, 1]) / R_CELL
    s = -q - r
    rq, rr, rs = np.round(q), np.round(r), np.round(s)
    dq, dr, ds = np.abs(rq - q), np.abs(rr - r), np.abs(rs - s)
    fq, fr = (dq > dr) & (dq > ds), ~((dq > dr) & (dq > ds)) & (dr > ds)
    rq = np.where(fq, -rr - rs, rq)
    rr = np.where(fr, -rq - rs, rr)
    return np.c_[rq, rr].astype(int)


def axe_packets(r, owner, cuts):
    """Per cluster: packets (one per 0.5 m) sent over its own cells along its stretch, each cell's longest visit."""
    out = []
    for k in range(len(cuts) - 1):
        d = np.arange(cuts[k], cuts[k + 1], 0.5)
        P = np.c_[np.interp(d, r["s"], r["poly"][:, 0]), np.interp(d, r["s"], r["poly"][:, 1])]
        H = cells_at(P)
        mine = np.array([owner.get((int(a), int(b))) == k for a, b in H])
        best, run, prev = {}, 0, None
        for (a, b), m in zip(map(tuple, H), mine):
            run = run + 1 if (a, b) == prev else 1
            prev = (a, b)
            if m:
                best[(a, b)] = max(best.get((a, b), 0), run)
        out.append(sum(best.values()))
    return out


def cut(chain, K):
    """Step 4: K consecutive runs of the chain of N / K cells; a run broken by a lake or a bay of the land keeps its
    largest piece, the others join the touching cluster they share most edges with; then partition.rebalance to the
    k-medoids cap (CAP). Returns {cell: cluster index}."""
    N = len(chain)
    owner = {h: min(K - 1, i * K // N) for i, h in enumerate(chain)}
    while True:
        moved = False
        for k in range(K):
            ps = pieces([h for h in owner if owner[h] == k])
            for p in ps[1:]:
                nb = touching(owner, p)
                if nb:
                    j = max(nb, key=lambda j: (nb[j], -j))
                    for h in p:
                        owner[h] = j
                    moved = True
        if not moved:
            break
    rebalance(owner, [sum(1 for c in owner.values() if c == k) for k in range(K)], CAP, set(chain))
    return owner


def swath(land, bs, K=None, L=6.0):
    """Steps 1-4. Returns {cell: cluster}, the route, and the route coordinates of the cuts: cluster k flies its
    stretch [cuts[k], cuts[k + 1]] of the route (the cuts of the chain before the repair)."""
    K = K or math.ceil(len(land) / CAP)
    tot, deg, off, r = routes(land, bs, L)[0]
    chain = [h for _, cs in r["lanes"] for h in cs]
    owner = cut(chain, K)
    pos, N = r["pos"], len(chain)
    b = [i * K // N for i in range(N)]
    cuts = [0.0] + [(pos[chain[i - 1]] + pos[chain[i]]) / 2 for i in range(1, N) if b[i] != b[i - 1]] + [float(r["s"][-1])]
    ax = axe_packets(r, owner, cuts)
    return owner, r, cuts, dict(total=tot, deg=deg, off=off, axe=ax, short=sum(a < CLUE for a in ax))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--lane", type=float, default=6.0)
    a = ap.parse_args()
    land = set(domain(a.clusters, a.seed)["domain"])
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    owner, r, cuts, info = swath(land, bs, L=a.lane)
    sz = np.bincount(list(owner.values()))
    whole = all(len(pieces([h for h in owner if owner[h] == k])) == 1 for k in range(len(sz)))
    print(f"{len(land)} cells, bearing {info['deg']} deg, offset {info['off']:.2f}, {len(r['lanes'])} lanes, route "
          f"{r['s'][-1] / 1000:.1f} km, with BS {info['total'] / 1000:.1f} km; {len(sz)} clusters {sz.tolist()}, "
          f"cv {sz.std() / sz.mean():.3f}, connected {whole}; Axe packets {info['axe']} ({info['short']} short)")


if __name__ == "__main__":
    main()
