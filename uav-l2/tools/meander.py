"""Phase 0 for curved, terrain-following flight (CLAUDE.md §8 item 103): MEANDER, LANE bent to the terrain.

    python3 tools/meander.py --clusters 6 --seed 3 --bend 220 --figs docs/figures          # one map, step figures
    python3 tools/meander.py --campaign --out docs/data/meander/maps                       # curved maps, 3 partitions

LANE (restructure.py) cuts the land into straight parallel lanes, so a bent or lake-riddled domain breaks
into many short pieces and each cluster is flown on one straight line. MEANDER keeps the idea (lanes of
River width, clusters cut along them, a boustrophedon tour known before the clusters are made) but measures
"along" and "across" in the terrain's own curvilinear coordinates:
  1  spine: the geodesic diameter of the land (Dijkstra over land cells, lakes and rivers are holes): from
     any cell to the farthest A, from A to the farthest B, the shortest land path A -> B
  2  along   s(h) = (d_A(h) - d_B(h)) / 2, geodesic, so it bends with the domain and around lakes
     across  n(h) = signed geodesic distance to the spine (multi-source Dijkstra from the spine cells; the
             side is set where a front leaves the spine, left or right of the spine's local tangent)
  3  lanes: n cut into strips L*W wide, offset (0, 1/3, 2/3 of a lane) with the fewest clusters + fragments
  4  pieces, fragments (< cap/4) merged, chunks of equal size along s: steps 2-3 of LANE with s for "along"
  5  flight line of a cluster: the mean cell centre per W/2 of s (the lane's centre curve), resampled every
     10 m and smoothed (Laplacian, ends fixed) until its curvature is at most 1/rho (rho = minimum turn
     radius of the fixed wing); a straight lead-in / lead-out of rho at each end
  6  order: boustrophedon over the lanes by mean n, clusters along each lane by mean s, alternating
Compared on the same maps with partition.py (k-medoids, best straight line through the CH) and LANE 4.5.
Figures have no text (CLAUDE.md §8 item 63).
"""
import argparse, csv, heapq, math, os, random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
import numpy as np

from map_gen import NB, W, add_args, cell_at, centre, corners, generate, strip_text
from partition import pieces
from restructure import CAP, OMEGA, borders, ch_proxy, frame, run_map, touching, water

RHO = 50.0 * 50.0 / 9.80665           # minimum turn radius, m (coop-params.h)
INK, INK2, SURF, LAND = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
DARK, LIGHT = "#1c5cab", "#c9dcf3"


def domain(K, seed, bend, width=1.0, wiggle=30.0, lakes=None, river=0.0):
    p = argparse.ArgumentParser()
    add_args(p)
    g = p.parse_args([])
    g.seed, g.cells, g.lakes, g.lakeCells = seed, 80 * K, K // 2 if lakes is None else lakes, 8
    g.spine, g.bend, g.wiggle, g.width, g.river = 1.1 * K / width, bend, wiggle, width, river
    return generate(g, random.Random(seed))


def dijkstra(land, seeds):
    """seeds: {cell: label}. Returns distance (m) and the label carried from the seed (or set by relabel)."""
    d, lab, pq = {h: 0.0 for h in seeds}, dict(seeds), [(0.0, h) for h in seeds]
    heapq.heapify(pq)
    while pq:
        dh, h = heapq.heappop(pq)
        if dh > d[h]:
            continue
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n in land and dh + W < d.get(n, math.inf):
                d[n], lab[n] = dh + W, lab[h]
                heapq.heappush(pq, (d[n], n))
    return d, lab


def coords(land):
    """Steps 1-2: spine cells and the curvilinear coordinates s, n of every land cell (main land piece)."""
    main = set(max(pieces(list(land)), key=len))
    h0 = next(iter(main))
    dA, _ = dijkstra(main, {h0: 0})
    A = max(dA, key=dA.get)
    dA, _ = dijkstra(main, {A: 0})
    B = max(dA, key=dA.get)
    dB, _ = dijkstra(main, {B: 0})
    spine, h = [B], B                                   # walk down d_A from B
    while h != A:
        h = min(((h[0] + dq, h[1] + dr) for dq, dr in NB if (h[0] + dq, h[1] + dr) in main),
                key=lambda n: dA[n])
        spine.append(h)
    spine = spine[::-1]
    s = {h: (dA[h] - dB[h]) / 2 for h in main}
    on = set(spine)
    seeds = {}
    for i, h in enumerate(spine):                       # side labels on the spine's neighbours
        a, b = np.array(centre(spine[max(i - 2, 0)])), np.array(centre(spine[min(i + 2, len(spine) - 1)]))
        t = b - a
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n in main and n not in on and n not in seeds:
                v = np.array(centre(n)) - np.array(centre(h))
                seeds[n] = 1 if t[0] * v[1] - t[1] * v[0] > 0 else -1
    d, lab = dijkstra(main, seeds)
    n = {h: 0.0 if h in on else lab[h] * (d[h] + W / 2) for h in main}
    return main, spine, s, n


def partition_meander(land, L, cap=CAP):
    """Steps 1-4, each land piece (cut off by a river or a lake) with its own spine. Returns owner, lane,
    s, n, spines and the stages."""
    s, n, lane, ps, spines = {}, {}, {}, [], []
    for i, part in enumerate(sorted(pieces(list(land)), key=len, reverse=True)):
        _, spine, sp, np_ = coords(set(part))
        s.update(sp); n.update(np_); spines.append(spine)
        best = None
        for off in (0, 1 / 3, 2 / 3):                   # step 3
            ln = {h: 1000 * i + int(math.floor(np_[h] / (L * W) + off)) for h in part}
            pp = [p for l in sorted(set(ln.values())) for p in pieces([h for h in part if ln[h] == l])]
            cost = sum(math.ceil(len(p) / cap) for p in pp) + sum(len(p) < cap / 4 for p in pp)
            if best is None or cost < best[0]:
                best = (cost, ln, pp)
        lane.update(best[1])
        ps += best[2]
    main, spine = set(land), spines[0]
    piece = {h: i for i, p in enumerate(ps) for h in p}
    cut, frag = dict(piece), set()
    size = lambda own, i: sum(1 for c in own.values() if c == i)
    while True:                                         # step 4a: fragments join a touching piece
        small = [i for i in set(piece.values()) if size(piece, i) < cap / 4
                 and touching(piece, [h for h in piece if piece[h] == i])]
        if not small:
            break
        i = min(small, key=lambda i: (size(piece, i), i))
        mine = [h for h in piece if piece[h] == i]
        nb = touching(piece, mine)
        j = max(nb, key=lambda j: (nb[j], -j))
        frag |= set(mine)
        for h in mine:
            piece[h] = j
    owner, k = {}, 0
    for i in sorted(set(piece.values())):               # step 4b: equal chunks along s
        p = sorted((h for h in piece if piece[h] == i), key=lambda h: s[h])
        m = math.ceil(len(p) / cap)
        ids = list(range(k, k + m))
        for j in range(m):
            for h in p[j * len(p) // m:(j + 1) * len(p) // m]:
                owner[h] = k + j
        k += m
        for c in ids:
            for part in pieces([h for h in owner if owner[h] == c])[1:]:
                nb = {j: v for j, v in touching(owner, part).items() if j in ids}
                if nb:
                    j = max(nb, key=lambda j: (size(owner, j) + len(part) <= cap, nb[j]))
                    for h in part:
                        owner[h] = j
    ids = {c: i for i, c in enumerate(sorted(set(owner.values())))}
    owner = {h: ids[c] for h, c in owner.items()}
    return owner, lane, s, n, spines, dict(cut=cut, frag=frag, main=main)


def curvature(P, stride=3):
    t = P[stride:] - P[:-stride]
    th = np.unwrap(np.arctan2(t[:, 1], t[:, 0]))
    ds = np.linalg.norm(t, axis=1)
    return np.abs(np.diff(th)) / np.maximum(ds[1:], 1e-9)


def resample(P, step=10.0):
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    d = np.r_[np.arange(0, seg[-1], step), seg[-1]]
    return np.c_[np.interp(d, seg, P[:, 0]), np.interp(d, seg, P[:, 1])]


def flight_curve(cells, s):
    """Step 5: the cluster's centre curve along s, smoothed to radius >= RHO, with lead-in / lead-out."""
    S0, S1 = min(s[h] for h in cells), max(s[h] for h in cells)
    pts = []
    for a in np.arange(S0, S1 + 1e-9, W / 2):
        b = [centre(h) for h in cells if a <= s[h] < a + W / 2]
        if b:
            pts.append(np.mean(b, axis=0))
    if len(pts) < 2:
        c = np.array(centre(cells[0]))
        pts = [c - (W, 0), c + (W, 0)]
    P = np.array(pts)
    if len(P) >= 5:   # moving average over 7 bins (~600 m): the lane's centre, not its cell-scale jitter
        Q = np.vstack([P[:1]] * 3 + [P] + [P[-1:]] * 3)
        P = np.vstack([P[:1], np.mean([Q[i:i + len(P)] for i in range(7)], axis=0)[1:-1], P[-1:]])
    P = resample(P)
    ok = True
    for it in range(4000):
        if len(P) < 8 or curvature(P).max() <= 1 / RHO:
            break
        P[1:-1] += 0.25 * (P[:-2] + P[2:] - 2 * P[1:-1])
        if it % 50 == 49:
            P = resample(P)
    else:
        ok = False
    P = resample(P)
    t0, t1 = P[min(3, len(P) - 1)] - P[0], P[-1] - P[max(len(P) - 4, 0)]
    t0, t1 = t0 / max(np.linalg.norm(t0), 1e-9), t1 / max(np.linalg.norm(t1), 1e-9)
    lead = np.linspace(RHO, 0, 26)[:-1]
    P = np.r_[P[0] - lead[:, None] * t0, P, P[-1] + lead[::-1][:, None] * t1]
    return P, ok


def curve_eval(owner, lane, s, n, nodes, bs):
    """Per-cluster coverage and flight, and the boustrophedon tour (step 6)."""
    ks = sorted(set(owner.values()))
    rows, path = [], {}
    for k in ks:
        cl = [h for h in owner if owner[h] == k]
        P, ok = flight_curve(cl, s)
        S = set(cl)
        mid, ln = (P[1:] + P[:-1]) / 2, np.linalg.norm(np.diff(P, axis=0), axis=1)
        inside = float(sum(l for p, l in zip(mid, ln) if cell_at(*p) in S))
        C = np.array([centre(h) for h in cl])
        dist = np.min(np.linalg.norm(C[:, None, :] - P[None, :, :], axis=2), axis=1)
        path[k] = P
        rows.append(dict(k=k, cells=len(cl), nodes=sum(1 for v in nodes if owner.get((v[3], v[4])) == k),
                         inside=inside, D=2 * inside, cover=float(np.mean(dist <= OMEGA)), farthest=float(dist.max() / W),
                         pieces=len(pieces(cl)), feasible=int(ok), ms=float(np.mean([s[h] for h in cl])),
                         mn=float(np.mean([n[h] for h in cl])), ch=ch_proxy(cl),
                         lane=max(set(lane[h] for h in cl), key=[lane[h] for h in cl].count)))
    lanes = {}
    for r in rows:                                      # the lane most of the cluster's cells sit in
        lanes.setdefault(r["lane"], []).append(r)
    best = None
    for first in (1, -1):
        for d0 in (1, -1):
            order, dirn, pos, tot, turn, pts = [], d0, bs, 0.0, 0.0, [np.array(bs)]
            for l in sorted(lanes, key=lambda l: first * l):
                for r in sorted(lanes[l], key=lambda r: dirn * r["ms"]):
                    P = path[r["k"]] if dirn > 0 else path[r["k"]][::-1]
                    order.append((r["k"], 0 if dirn > 0 else 1))
                    pts.append(P)
                dirn = -dirn
            pts.append(np.array([bs]))
            full = np.vstack([np.atleast_2d(p) for p in pts])
            seglen = np.linalg.norm(np.diff(full, axis=0), axis=1)
            total = float(seglen.sum())
            transit = total - sum(float(np.linalg.norm(np.diff(path[k], axis=0), axis=1).sum()) for k in ks)
            coarse = resample(full, 50.0)   # turning measured on 50 m steps: the flown shape, not sampling jitter
            hd = np.arctan2(*np.diff(coarse, axis=0)[np.linalg.norm(np.diff(coarse, axis=0), axis=1) > 1].T[::-1])
            turn = float(np.degrees(np.abs(np.angle(np.exp(1j * np.diff(hd)))).sum()))
            if best is None or total < best["total"]:
                best = dict(order=order, total=total, transit=transit, turn=turn, full=full)
    return rows, dict(path=path, inside=sum(r["inside"] for r in rows), **best)


def run(K, seed, bend, L=4.5, g=None, width=1.0):
    g = g or domain(K, seed, bend, width)
    R = run_map(K, seed, L, "short", g=g)               # k-medoids and LANE on the same land
    owner, lane, s, n, spines, st = partition_meander(R["land"], L)
    rows, ev = curve_eval(owner, lane, s, n, R["nodes"], R["bs"])
    return dict(R=R, owner=owner, lane=lane, s=s, n=n, spines=spines, st=st, rows=rows, ev=ev)


def summarise(M):
    R = M["R"]
    out = {}
    for name, (rows, ev, own) in {"kmedoids": (*R["base"], R["km"]), "lane": (*R["lane_"], R["lo"]),
                                  "meander": (M["rows"], M["ev"], M["owner"])}.items():
        cells = sum(r["cells"] for r in rows)
        out[name] = dict(clusters=len(rows), minCells=min(r["cells"] for r in rows),
                         cover=sum(r["cover"] * r["cells"] for r in rows) / cells,
                         farthest=float(np.mean([r["farthest"] for r in rows])), inside=ev["inside"] / 1000,
                         transit=ev["transit"] / 1000, turn=ev["turn"], covered=cells / len(R["land"]),
                         feasible=float(np.mean([r.get("feasible", 1) for r in rows])))
    return out


# ---------------------------------------------------------------- figures (no text, CLAUDE.md §8 item 63)
def polys(ax, hs, col, **kw):
    ax.add_collection(PolyCollection([corners(h) for h in hs], facecolors=col, edgecolors=SURF, linewidths=.3, **kw))


def step_figure(M, path):
    R, g, land = M["R"], M["R"]["g"], M["R"]["land"]
    main = sorted(M["st"]["main"])
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    asp = (max(xs) - min(xs) + 2 * W) / (max(ys) - min(ys) + 1250 + 2 * W)
    fig, axs = plt.subplots(2, 4, figsize=(4 * 5 * asp + 1, 10.5), dpi=130, facecolor=SURF)
    axs = axs.ravel()
    sps = [np.array([centre(h) for h in sp]) for sp in M["spines"] if len(sp) > 1]
    # 1 terrain
    polys(axs[0], sorted(land), LAND); water(axs[0], g)
    axs[0].scatter(*R["bs"], marker="s", s=60, color=INK)
    # 2 along-coordinate s and the spine
    sv = np.array([M["s"][h] for h in main])
    polys(axs[1], main, plt.cm.viridis((sv - sv.min()) / max(np.ptp(sv), 1))); water(axs[1], g)
    for sp in sps:
        axs[1].plot(*sp.T, color=SURF, lw=3); axs[1].plot(*sp.T, color=INK, lw=1.5)
        axs[1].scatter(*sp[[0, -1]].T, s=80, color=INK, zorder=5)
    # 3 across-coordinate n
    nv = np.array([M["n"][h] for h in main])
    polys(axs[2], main, plt.cm.RdBu((nv / (2 * np.abs(nv).max())) + 0.5)); water(axs[2], g)
    for sp in sps:
        axs[2].plot(*sp.T, color=INK, lw=1.5)
    # 4 lanes
    polys(axs[3], main, [DARK if M["lane"][h] % 2 else LIGHT for h in main]); water(axs[3], g)
    # 5 pieces before merging; fragments hatched
    cut = M["st"]["cut"]
    cmap = plt.cm.tab20
    polys(axs[4], main, [cmap(cut[h] % 20) for h in main]); water(axs[4], g)
    frag = sorted(M["st"]["frag"])
    if frag:
        axs[4].add_collection(PolyCollection([corners(h) for h in frag], facecolors="none", edgecolors=INK, hatch="xxx",
                                             linewidths=0))
    # 6 clusters, darker = visited earlier
    rank = {k: i for i, (k, _) in enumerate(M["ev"]["order"])}
    nk = len(rank)
    polys(axs[5], sorted(M["owner"]), [plt.cm.Blues(0.9 - 0.65 * rank[M["owner"][h]] / max(nk - 1, 1)) for h in sorted(M["owner"])])
    borders(axs[5], M["owner"]); water(axs[5], g)
    # 7 curved flight lines and the tour
    polys(axs[6], sorted(M["owner"]), LAND); borders(axs[6], M["owner"], lw=.8); water(axs[6], g)
    full = M["ev"]["full"]
    axs[6].plot(*full.T, color=INK2, lw=1, ls=(0, (3, 2)))
    for k, P in M["ev"]["path"].items():
        axs[6].plot(*P.T, color=INK, lw=2.2)
    axs[6].scatter(*R["bs"], marker="s", s=60, color=INK)
    # 8 River coverage: cells within omega of their cluster's curve
    inr = []
    for k, P in M["ev"]["path"].items():
        for h in (h for h in M["owner"] if M["owner"][h] == k):
            if np.min(np.linalg.norm(P - np.array(centre(h)), axis=1)) <= OMEGA:
                inr.append(h)
    S = set(inr)
    polys(axs[7], sorted(M["owner"]), [DARK if h in S else LIGHT for h in sorted(M["owner"])])
    borders(axs[7], M["owner"], lw=.8); water(axs[7], g)
    for P in M["ev"]["path"].values():
        axs[7].plot(*P.T, color=INK, lw=1.4)
    for ax in axs:
        frame(ax, land)
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


def compare_figure(M, path):
    """k-medoids | LANE | MEANDER: River cells dark, flight lines black (same map)."""
    R, g, land = M["R"], M["R"]["g"], M["R"]["land"]
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    asp = (max(xs) - min(xs) + 2 * W) / (max(ys) - min(ys) + 1250 + 2 * W)
    fig, axs = plt.subplots(1, 3, figsize=(3 * 6.5 * asp + 1, 6.5), dpi=130, facecolor=SURF)
    from restructure import line
    for ax, (own, rows, ev, curved) in zip(axs, [(R["km"], *R["base"], False), (R["lo"], *R["lane_"], False),
                                                (M["owner"], M["rows"], M["ev"], True)]):
        inr = set()
        lines = {}
        for r in rows:
            cl = [h for h in own if own[h] == r["k"]]
            if curved:
                P = ev["path"][r["k"]]
            else:
                a, b = ev["seg"][r["k"]]
                P = np.c_[np.linspace(a[0], b[0], 200), np.linspace(a[1], b[1], 200)]
            lines[r["k"]] = P
            inr |= {h for h in cl if np.min(np.linalg.norm(P - np.array(centre(h)), axis=1)) <= OMEGA}
        polys(ax, sorted(own), [DARK if h in inr else LIGHT for h in sorted(own)])
        borders(ax, own, lw=.9); water(ax, g)
        for P in lines.values():
            ax.plot(*P.T, color=INK, lw=1.8)
        ax.scatter(*R["bs"], marker="s", s=50, color=INK)
        frame(ax, land)
    strip_text(fig)
    fig.savefig(path, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, default=6)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--bend", type=float, default=220)
    ap.add_argument("--lane", type=float, default=4.5)
    ap.add_argument("--figs")
    ap.add_argument("--width", type=float, default=1.0, help="domain width scale, km (spine length 1.1 K / width)")
    ap.add_argument("--campaign", action="store_true", help="width 1 / 0.6 x K 4 / 6 x bend 90 / 180 / 270 x 5 seeds")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not a.campaign:
        M = run(a.clusters, a.seed, a.bend, a.lane, width=a.width)
        tag = f"k{a.clusters}-s{a.seed}-b{int(a.bend)}-w{a.width:g}"
        if a.figs:
            step_figure(M, os.path.join(a.figs, f"meander-{tag}-steps.png"))
            compare_figure(M, os.path.join(a.figs, f"meander-{tag}-compare.png"))
        for name, v in summarise(M).items():
            print(name, {k: round(x, 3) for k, x in v.items()})
        return
    rows = []
    for width in (1.0, 0.6):
        for K in (4, 6):
            for bend in (90, 180, 270):
                for seed in range(1, 6):
                    try:
                        M = run(K, seed, bend, a.lane, width=width)
                    except KeyError as e:   # partition.py (k-medoids) fails on land in several pieces
                        print(f"w{width} K{K} b{bend} s{seed}: skipped ({e})", flush=True)
                        continue
                    for name, v in summarise(M).items():
                        rows.append(dict(width=width, K=K, bend=bend, seed=seed, method=name,
                                         **{k: round(x, 4) for k, x in v.items()}))
                    print(f"w{width} K{K} b{bend} s{seed} done", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out + ".csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    keys = ["clusters", "minCells", "cover", "farthest", "inside", "transit", "turn", "feasible"]
    for width in (1.0, 0.6):
        for bend in (90, 180, 270):
            print(f"width {width} bend {bend}")
            for m in ("kmedoids", "lane", "meander"):
                rs = [r for r in rows if r["width"] == width and r["bend"] == bend and r["method"] == m]
                print(f"  {m:9s} n={len(rs):2d} " + "  ".join(f"{k} {np.mean([r[k] for r in rs]):.3f}" for k in keys))
    print("paired, meander - lane, cover: mean, maps better")
    for width in (1.0, 0.6):
        for bend in (90, 180, 270):
            key = lambda r: (r["K"], r["seed"])
            ln = {key(r): r for r in rows if r["width"] == width and r["bend"] == bend and r["method"] == "lane"}
            me = {key(r): r for r in rows if r["width"] == width and r["bend"] == bend and r["method"] == "meander"}
            d = np.array([me[k]["cover"] - ln[k]["cover"] for k in me if k in ln])
            print(f"  width {width} bend {bend}: {d.mean():+.3f}, {np.sum(d > 0)}/{len(d)}")


if __name__ == "__main__":
    main()
