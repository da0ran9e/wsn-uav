"""A wide map holding several clusters, each made the way uav-coop makes one (models/common/region.cc,
deploy.h), for the layer-2 flight-path problem.

    python3 tools/map_gen.py --seed 1 --clusters 5 --out docs/data/map-s1 --figs docs/figures

Per cluster, on the R = 100 m hex lattice:
  1  seed: a cell drawn uniformly in the map disc (radius --mapRadius cells), at least --seedGap cells
     from the other seeds;
  2  Eden growth to --cells cells: each step adds a cell drawn uniformly from the frontier; a cell
     closer than --gap cells to another cluster, or outside the map, is never taken;
  3  concavity filling to convexity --convexity (cells in the convex hull not in the cluster, the most
     enclosed first, ties at random), skipping cells closer than --gap to another cluster;
  4  nodes: round(area / spacing^2), uniform over the cluster; obs, cpu ~ U[0,1), comm ~ U(0,1];
     CH = strongest (obs*cpu*comm) node at least --chMargin from the cluster's outer edge,
     CL = strongest node of each cell (the CH leads its own cell).
Clusters grow one after another; if one cannot reach --cells, all seeds are drawn again.
Writes OUT-cells.csv, OUT-nodes.csv, OUT-clusters.csv and FIGS/map-steps.png.
"""
import argparse, csv, math, os, random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.lines import Line2D

R = 100.0
W = R * math.sqrt(3)
NB = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
INK, INK2, SURF, GREY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
CAT = ["#1c5cab", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#0d366b", "#52514e"]


def centre(h):   # pointy-top axial
    q, r = h
    return (W * (q + r / 2), 1.5 * R * r)


def corners(h, k=1.0):
    cx, cy = centre(h)
    return [(cx + k * R * math.cos(math.radians(30 + 60 * i)), cy + k * R * math.sin(math.radians(30 + 60 * i)))
            for i in range(6)]


def hexdist(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) // 2


def cell_at(x, y):
    q, r = (math.sqrt(3) / 3 * x - y / 3) / R, (2 / 3 * y) / R
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return (rq, rr)


def hull_cells(cells):
    pts = sorted(centre(h) for h in cells)
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    hull = []
    for seq in (pts, pts[::-1]):
        start = len(hull)
        for p in seq:
            while len(hull) >= start + 2 and cross(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)
        hull.pop()
    eps = 1e-6 * W * W
    qs, rs = [h[0] for h in cells], [h[1] for h in cells]
    return [(q, r) for q in range(min(qs), max(qs) + 1) for r in range(min(rs), max(rs) + 1)
            if all(cross(hull[i], hull[(i + 1) % len(hull)], centre((q, r))) >= -eps for i in range(len(hull)))]


def holes(cells):
    S = set(cells)
    qs, rs = [h[0] for h in cells], [h[1] for h in cells]
    box = lambda h: min(qs) - 1 <= h[0] <= max(qs) + 1 and min(rs) - 1 <= h[1] <= max(rs) + 1
    start = (min(qs) - 1, min(rs) - 1)
    out, todo = {start}, [start]
    while todo:
        h = todo.pop()
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if box(n) and n not in S and n not in out:
                out.add(n)
                todo.append(n)
    return [(q, r) for q in range(min(qs), max(qs) + 1) for r in range(min(rs), max(rs) + 1)
            if (q, r) not in S and (q, r) not in out]


def outer_edges(cells):
    inside = set(cells) | set(holes(cells))
    edges = []
    for h in cells:
        v = corners(h)
        cx, cy = centre(h)
        for k in range(6):
            a, b = v[k], v[(k + 1) % 6]
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if cell_at(2 * m[0] - cx, 2 * m[1] - cy) not in inside:
                edges.append((a, b))
    return edges


def edge_dist(p, edges):
    best = float("inf")
    for a, b in edges:
        ex, ey = b[0] - a[0], b[1] - a[1]
        t = max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ey) / (ex * ex + ey * ey)))
        best = min(best, math.hypot(p[0] - a[0] - t * ex, p[1] - a[1] - t * ey))
    return best


def build(a, rng):
    disc = [(q, r) for q in range(-a.mapRadius, a.mapRadius + 1) for r in range(-a.mapRadius, a.mapRadius + 1)
            if hexdist((q, r), (0, 0)) <= a.mapRadius]
    inmap = set(disc)
    for attempt in range(1, 1001):
        seeds = []
        for _ in range(200 * a.clusters):
            h = rng.choice(disc)
            if all(hexdist(h, s) >= a.seedGap for s in seeds):
                seeds.append(h)
            if len(seeds) == a.clusters:
                break
        if len(seeds) < a.clusters:
            continue
        owner = {}            # cell -> cluster
        clusters = []
        ok = True
        for i, s in enumerate(seeds):
            near_other = lambda h: any(owner.get((h[0] + dq, h[1] + dr), i) != i
                                       for dq in range(-a.gap + 1, a.gap) for dr in range(-a.gap + 1, a.gap)
                                       if hexdist((0, 0), (dq, dr)) < a.gap)
            if near_other(s):
                ok = False
                break
            cells, frontier, onf = [], [], set()

            def add(h):
                cells.append(h)
                owner[h] = i
                for dq, dr in NB:
                    n = (h[0] + dq, h[1] + dr)
                    if n not in owner and n not in onf:
                        onf.add(n)
                        frontier.append(n)
            add(s)
            while len(cells) < a.cells:
                frontier[:] = [h for h in frontier if h in inmap and h not in owner and not near_other(h)]
                if not frontier:
                    break
                k = rng.randrange(len(frontier))
                h = frontier[k]
                frontier[k] = frontier[-1]
                frontier.pop()
                onf.discard(h)
                add(h)
            if len(cells) < a.cells:
                ok = False
                break
            grown = len(cells)
            hull = hull_cells(cells)
            raw = len(cells) / len(hull)
            target = math.ceil(a.convexity * len(hull) - 1e-9)
            todo = [h for h in hull if h not in owner]
            blocked = 0
            while len(cells) < target and todo:
                todo = [h for h in todo if h in inmap and not near_other(h)]
                if not todo:
                    break
                S = set(cells)
                score = [sum((h[0] + dq, h[1] + dr) in S for dq, dr in NB) for h in todo]
                best = max(score)
                tied = [j for j, v in enumerate(score) if v == best]
                h = todo.pop(rng.choice(tied))
                cells.append(h)
                owner[h] = i
            blocked = len([h for h in hull if h not in owner])
            clusters.append(dict(seed=s, cells=cells, grown=grown, raw=raw, conv=len(cells) / len(hull),
                                 blocked=blocked))
        if ok:
            return disc, clusters, attempt
    raise SystemExit("could not place the clusters: enlarge --mapRadius or lower --cells / --gap")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--clusters", type=int, default=5)
    ap.add_argument("--cells", type=int, default=60, help="cells grown per cluster (as uav-coop)")
    ap.add_argument("--convexity", type=float, default=1.0, help="target convexity of each cluster")
    ap.add_argument("--gap", type=int, default=3, help="cells of different clusters are >= gap cells apart")
    ap.add_argument("--seedGap", type=int, default=12, help="seeds >= this many cells apart")
    ap.add_argument("--mapRadius", type=int, default=22, help="map: hex disc of this radius, in cells")
    ap.add_argument("--spacing", type=float, default=35.0, help="one node per spacing^2")
    ap.add_argument("--chMargin", type=float, default=300.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    disc, clusters, attempts = build(a, rng)

    # nodes, capabilities, roles
    area = 3 * math.sqrt(3) / 2 * R * R
    nodes = []
    for i, c in enumerate(clusters):
        n = round(len(c["cells"]) * area / a.spacing ** 2)
        first = len(nodes)
        for _ in range(n):
            h = rng.choice(c["cells"])
            cx, cy = centre(h)
            while True:
                x, y = cx + rng.uniform(-W / 2, W / 2), cy + rng.uniform(-R, R)
                if cell_at(x, y) == h:
                    break
            obs, cpu, comm = rng.random(), rng.random(), 1 - rng.random()
            nodes.append(dict(id=len(nodes), x=x, y=y, q=h[0], r=h[1], cluster=i, obs=obs, cpu=cpu, comm=comm,
                              score=obs * cpu * comm, isCH=0, isCL=0))
        edges = outer_edges(c["cells"])
        mine = nodes[first:]
        far = [v for v in mine if edge_dist((v["x"], v["y"]), edges) >= a.chMargin]
        ch = max(far or mine, key=lambda v: (v["score"], -v["id"]))
        ch["isCH"] = 1
        c["ch"], c["nodes"], c["chFallback"] = ch["id"], len(mine), not far
        best = {}
        for v in mine:
            h = (v["q"], v["r"])
            if h not in best or (v["score"], -v["id"]) > (best[h]["score"], -best[h]["id"]):
                best[h] = v
        best[(ch["q"], ch["r"])] = ch
        for v in best.values():
            v["isCL"] = 1
        c["edges"] = edges

    # outputs
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + "-cells.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["q", "r", "cx", "cy", "cluster", "filled"])
        for i, c in enumerate(clusters):
            for j, h in enumerate(c["cells"]):
                w.writerow([h[0], h[1], f"{centre(h)[0]:.3f}", f"{centre(h)[1]:.3f}", i, int(j >= c["grown"])])
    with open(a.out + "-nodes.csv", "w", newline="") as f:
        keys = ["id", "x", "y", "q", "r", "cluster", "obs", "cpu", "comm", "score", "isCH", "isCL"]
        w = csv.DictWriter(f, keys)
        w.writeheader()
        for v in nodes:
            w.writerow({k: (f"{v[k]:.6g}" if isinstance(v[k], float) else v[k]) for k in keys})
    with open(a.out + "-clusters.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cluster", "seed_q", "seed_r", "grown", "cells", "areaKm2", "rawConvexity", "convexity",
                    "hullCellsBlocked", "nodes", "ch", "chX", "chY"])
        for i, c in enumerate(clusters):
            chn = nodes[c["ch"]]
            w.writerow([i, *c["seed"], c["grown"], len(c["cells"]), f"{len(c['cells']) * area / 1e6:.3f}",
                        f"{c['raw']:.3f}", f"{c['conv']:.3f}", c["blocked"], c["nodes"], c["ch"],
                        f"{chn['x']:.1f}", f"{chn['y']:.1f}"])

    # figure: the four steps
    fig, axs = plt.subplots(2, 2, figsize=(13, 13), dpi=140, facecolor=SURF)
    allc = [centre(h) for h in disc]
    lim = (min(p[0] for p in allc) - W, max(p[0] for p in allc) + W, min(p[1] for p in allc) - W,
           max(p[1] for p in allc) + 2.5 * W)

    def base(ax, title):
        ax.add_collection(PolyCollection([corners(h) for h in disc], facecolors=GREY, edgecolors=SURF,
                                         linewidths=.4, zorder=0))
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, loc="left", fontsize=10, color=INK)

    def label(ax, i, c):
        xs = [centre(h)[0] for h in c["cells"]]; ys = [centre(h)[1] for h in c["cells"]]
        ax.text(sum(xs) / len(xs), max(ys) + 1.3 * R, f"C{i + 1}", ha="center", va="bottom", fontsize=11,
                color=INK, fontweight="bold", zorder=9)

    span_km = (lim[1] - lim[0]) / 1000
    base(axs[0, 0], f"Bước 1 — bản đồ: lưới lục giác R = 100 m,\nđĩa bán kính {a.mapRadius} cell "
                    f"(rộng ≈ {span_km:.1f} km); {a.clusters} hạt giống cách nhau ≥ {a.seedGap} cell")
    for i, c in enumerate(clusters):
        axs[0, 0].scatter(*centre(c["seed"]), s=380, color=CAT[i % len(CAT)], edgecolors=SURF, lw=1.5, zorder=2)
        axs[0, 0].text(*centre(c["seed"]), f"C{i + 1}", ha="center", va="center", fontsize=8.5, color="#ffffff",
                       fontweight="bold", zorder=3)
    base(axs[0, 1], f"Bước 2 — mỗi cluster mọc ngẫu nhiên (Eden) {a.cells} cell;\n"
                    f"cell của hai cluster khác nhau cách nhau ≥ {a.gap} cell")
    for i, c in enumerate(clusters):
        axs[0, 1].add_collection(PolyCollection([corners(h) for h in c["cells"][:c["grown"]]],
                                                facecolors=CAT[i % len(CAT)], edgecolors=SURF, linewidths=.4,
                                                zorder=2))
        label(axs[0, 1], i, c)
    base(axs[1, 0], f"Bước 3 — lấp chỗ lõm tới độ lồi {a.convexity:g}\n(nhạt = cell lấp thêm)")
    for i, c in enumerate(clusters):
        col = CAT[i % len(CAT)]
        axs[1, 0].add_collection(PolyCollection([corners(h) for h in c["cells"][:c["grown"]]], facecolors=col,
                                                edgecolors=SURF, linewidths=.4, zorder=2))
        axs[1, 0].add_collection(PolyCollection([corners(h) for h in c["cells"][c["grown"]:]], facecolors=col,
                                                alpha=.4, edgecolors=SURF, linewidths=.4, zorder=2))
        label(axs[1, 0], i, c)
    axs[1, 0].text(lim[1] - .2 * W, lim[3] - .2 * W,
                   "\n".join(f"C{i + 1}: {c['grown']}→{len(c['cells'])} cell, lồi {c['raw']:.2f}→{c['conv']:.2f}"
                             for i, c in enumerate(clusters)), ha="right", va="top", fontsize=8, color=INK2,
                   zorder=9, bbox=dict(facecolor=SURF, edgecolor="none", alpha=.9))
    base(axs[1, 1], f"Bước 4 — {len(nodes)} node (1 node / {a.spacing:g}² m²);\nCH ★ cách biên ≥ "
                    f"{a.chMargin:g} m; CL ○ mạnh nhất mỗi cell")
    for i, c in enumerate(clusters):
        col = CAT[i % len(CAT)]
        axs[1, 1].add_collection(PolyCollection([corners(h) for h in c["cells"]], facecolors=col, alpha=.18,
                                                edgecolors=SURF, linewidths=.4, zorder=1))
        axs[1, 1].add_collection(LineCollection(c["edges"], colors=col, linewidths=1.1, zorder=3))
        mine = [v for v in nodes if v["cluster"] == i]
        axs[1, 1].scatter([v["x"] for v in mine], [v["y"] for v in mine], s=.6, color=col, zorder=2,
                          rasterized=True)
        cls = [v for v in mine if v["isCL"] and not v["isCH"]]
        axs[1, 1].scatter([v["x"] for v in cls], [v["y"] for v in cls], s=6, color="#ffffff", edgecolors=INK2,
                          lw=.5, zorder=4)
        chn = nodes[c["ch"]]
        axs[1, 1].scatter([chn["x"]], [chn["y"]], s=220, marker="*", color="#ffffff", edgecolors=INK, lw=1.1,
                          zorder=6)
        label(axs[1, 1], i, c)
    axs[1, 1].plot([lim[1] - 1.3 * W - 1000, lim[1] - 1.3 * W], [lim[2] + .8 * W] * 2, color=INK, lw=2)
    axs[1, 1].text(lim[1] - 1.3 * W - 500, lim[2] + 1.1 * W, "1 km", ha="center", fontsize=8, color=INK)
    out = os.path.join(a.figs, "map-steps.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"{a.clusters} clusters in {attempts} draw(s) of the seeds; {len(nodes)} nodes")
    for i, c in enumerate(clusters):
        print(f"  C{i + 1}: seed {c['seed']}, {c['grown']} -> {len(c['cells'])} cells "
              f"({len(c['cells']) * area / 1e6:.2f} km2), convexity {c['raw']:.2f} -> {c['conv']:.2f}"
              f"{', ' + str(c['blocked']) + ' hull cells blocked by the gap' if c['blocked'] else ''}, "
              f"{c['nodes']} nodes, CH #{c['ch']}{' (no node far enough in: strongest overall)' if c['chFallback'] else ''}")
    print(f"  {out}")


if __name__ == "__main__":
    main()
