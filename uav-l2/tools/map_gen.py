"""The layer-2 domain: one region made exactly like a uav-coop cluster (models/common/region.cc,
deploy.h), only larger -- about the size of 4-5 clusters.

    python3 tools/map_gen.py --seed 1 --cells 300 --convexity 0.8 --out docs/data/map-s1 --figs docs/figures

On the R = 100 m hex lattice:
  1  Eden growth from the origin's cell to --cells cells: each step adds a cell drawn uniformly from the
     frontier (unselected cells touching the region). Ragged, may enclose holes. A uav-coop cluster grows
     60 cells, so 300 is five clusters' worth.
  2  concavity filling to convexity --convexity: the cells in the convex hull of the region's centres
     that are not in it are filled one at a time, the most enclosed first, ties at random; convexity =
     cells / hull cells. At or below the grown region's own convexity nothing is filled.
  3  nodes: round(area / spacing^2), uniform over the region; obs, cpu ~ U[0,1), comm ~ U(0,1]. No CH, no CL.
Writes OUT-cells.csv (q, r, centre, order in which the cell joined, filled?), OUT-nodes.csv and
FIGS/map-steps.png (growth, filling to several convexities, nodes).
"""
import argparse, csv, math, os, random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

R = 100.0
W = R * math.sqrt(3)
NB = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
INK, INK2, SURF, GREY = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
GROWN, FILLED = "#1c5cab", "#86b6ef"


def centre(h):   # pointy-top axial
    return (W * (h[0] + h[1] / 2), 1.5 * R * h[1])


def corners(h):
    cx, cy = centre(h)
    return [(cx + R * math.cos(math.radians(30 + 60 * i)), cy + R * math.sin(math.radians(30 + 60 * i)))
            for i in range(6)]


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


def outline(cells):
    """The region's border segments (hole borders included)."""
    S = set(cells)
    segs = []
    for h in cells:
        v = corners(h)
        cx, cy = centre(h)
        for k in range(6):
            a, b = v[k], v[(k + 1) % 6]
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if cell_at(2 * m[0] - cx, 2 * m[1] - cy) not in S:
                segs.append((a, b))
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cells", type=int, default=300, help="cells grown (a uav-coop cluster: 60)")
    ap.add_argument("--convexity", type=float, default=0.8, help="target convexity of the saved region")
    ap.add_argument("--show", default="0.8,1", help="convexities drawn in the filling panels")
    ap.add_argument("--spacing", type=float, default=35.0, help="one node per spacing^2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)

    # 1 Eden growth
    cells, frontier, onf, S = [], [], set(), set()

    def add(h):
        cells.append(h)
        S.add(h)
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n not in S and n not in onf:
                onf.add(n)
                frontier.append(n)
    add((0, 0))
    while len(cells) < a.cells:
        k = rng.randrange(len(frontier))
        h = frontier[k]
        frontier[k] = frontier[-1]
        frontier.pop()
        onf.discard(h)
        add(h)
    grown = len(cells)

    # 2 concavity filling, recording the order so any convexity can be read off
    hull = hull_cells(cells)
    raw = grown / len(hull)
    todo = [h for h in hull if h not in S]
    while todo:
        score = [sum((h[0] + dq, h[1] + dr) in S for dq, dr in NB) for h in todo]
        best = max(score)
        h = todo.pop(rng.choice([j for j, v in enumerate(score) if v == best]))
        cells.append(h)
        S.add(h)
    upto = lambda kappa: max(grown, math.ceil(kappa * len(hull) - 1e-9))
    final = cells[:upto(a.convexity)]

    # 3 nodes, uniform over the saved region
    area = 3 * math.sqrt(3) / 2 * R * R
    nodes = []
    for _ in range(round(len(final) * area / a.spacing ** 2)):
        h = rng.choice(final)
        cx, cy = centre(h)
        while True:
            x, y = cx + rng.uniform(-W / 2, W / 2), cy + rng.uniform(-R, R)
            if cell_at(x, y) == h:
                break
        obs, cpu, comm = rng.random(), rng.random(), 1 - rng.random()
        nodes.append((len(nodes), x, y, h[0], h[1], obs, cpu, comm))

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + "-cells.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["q", "r", "cx", "cy", "order", "filled"])
        for j, h in enumerate(final):
            w.writerow([h[0], h[1], f"{centre(h)[0]:.3f}", f"{centre(h)[1]:.3f}", j, int(j >= grown)])
    with open(a.out + "-nodes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "x", "y", "q", "r", "obs", "cpu", "comm"])
        for v in nodes:
            w.writerow([v[0], f"{v[1]:.3f}", f"{v[2]:.3f}", v[3], v[4], *(f"{x:.6g}" for x in v[5:])])

    # figure
    xs = [centre(h)[0] for h in cells]; ys = [centre(h)[1] for h in cells]
    lim = (min(xs) - W, max(xs) + W, min(ys) - W, max(ys) + W)
    show = [float(x) for x in a.show.split(",")]
    panels = [(f"Mọc Eden: {n} cell", cells[:n], 0) for n in (a.cells // 3, 2 * a.cells // 3)]
    vn = lambda x, f=".2f": format(x, f).replace(".", ",")
    panels.append((f"Mọc Eden: đủ {grown} cell\nđộ lồi {vn(raw)}, {len(holes(cells[:grown]))} lỗ bên trong",
                   cells[:grown], 0))
    for kappa in show:
        n = upto(kappa)
        panels.append((f"Lấp chỗ lõm tới độ lồi {vn(kappa, 'g')}\n{grown} → {n} cell (nhạt = lấp thêm)", cells[:n],
                       grown))
    fig, axs = plt.subplots(2, 3, figsize=(16, 11.5), dpi=140, facecolor=SURF)
    axs = axs.ravel()

    def frame(ax, title):
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, loc="left", fontsize=10, color=INK)

    for ax, (title, cs, g) in zip(axs, panels):
        ax.add_collection(PolyCollection([corners(h) for h in hull], facecolors=GREY, edgecolors=SURF,
                                         linewidths=.3, zorder=0))
        ax.add_collection(PolyCollection([corners(h) for h in cs[:g or len(cs)]], facecolors=GROWN,
                                         edgecolors=SURF, linewidths=.3, zorder=1))
        if g:
            ax.add_collection(PolyCollection([corners(h) for h in cs[g:]], facecolors=FILLED, edgecolors=SURF,
                                             linewidths=.3, zorder=1))
        frame(ax, title)
    ax = axs[len(panels)]
    ax.add_collection(PolyCollection([corners(h) for h in final], facecolors="#c9dcf3", edgecolors=SURF,
                                     linewidths=.3, zorder=0))
    ax.add_collection(LineCollection(outline(final), colors=INK2, linewidths=.9, zorder=2))
    ax.scatter([v[1] for v in nodes], [v[2] for v in nodes], s=.4, color=GROWN, zorder=1, rasterized=True)
    frame(ax, f"Miền lưu (độ lồi {vn(len(final) / len(hull))}): {len(final)} cell, "
              f"{vn(len(final) * area / 1e6, '.1f')} km²\n{len(nodes)} node (1 node / {a.spacing:g}² m²), chưa chọn CH")
    ax.plot([lim[1] - W - 1000, lim[1] - W], [lim[2] + .6 * W] * 2, color=INK, lw=2)
    ax.text(lim[1] - W - 500, lim[2] + .9 * W, "1 km", ha="center", fontsize=8, color=INK)
    for k in range(len(panels) + 1, len(axs)):
        axs[k].axis("off")
    fig.suptitle(f"Miền cho tầng 2: sinh như một cluster của uav-coop nhưng mọc {a.cells} cell (một cluster: 60); "
                 "ô xám = bao lồi", x=.01, ha="left", fontsize=11, color=INK)
    out = os.path.join(a.figs, "map-steps.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    span = (max(xs) - min(xs) + W) / 1000, (max(ys) - min(ys) + 2 * R) / 1000
    print(f"grown {grown} cells, convexity {raw:.2f}, {len(holes(cells[:grown]))} holes; hull {len(hull)} cells; "
          f"saved convexity {len(final) / len(hull):.2f}: {len(final)} cells, {len(final) * area / 1e6:.2f} km2, "
          f"{len(nodes)} nodes; extent {span[0]:.1f} x {span[1]:.1f} km")
    print(f"  {out}")


if __name__ == "__main__":
    main()
