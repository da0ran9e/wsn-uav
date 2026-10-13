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
  3  gaps (optional), carved after the filling so it never closes them:
     --lakes k --lakeCells m: k lakes, each an Eden blob of m cells grown from a random interior cell
     through interior cells only (cells whose six neighbours are all land), so a lake never opens to the edge;
     --river w: a river w cells wide, the cells within w*width/2 of a random smooth curve through the
     region's centre (it may cut the region in pieces).
  4  nodes: round(area / spacing^2), uniform over the land; obs, cpu ~ U[0,1), comm ~ U(0,1]. No CH, no CL.
Long or curved domains (optional, --spine L): the growth is still Eden, but a frontier cell is drawn with
weight exp(-d^2 / 2 sigma^2) instead of uniformly, d = its distance to a random smooth curve (the spine)
through the origin: length L km, total turn --bend degrees, plus a sinusoidal wiggle of --wiggle degrees;
sigma = --width / 2 km. The edge stays ragged; the domain follows the spine.
Writes OUT-cells.csv (q, r, centre, order in which the cell joined, filled?, type land/lake/river),
OUT-nodes.csv and FIGS/map-steps.png (growth, filling to several convexities, nodes).
"""
import argparse, csv, math, os, random

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

R = 100.0
W = R * math.sqrt(3)
AREA = 3 * math.sqrt(3) / 2 * R * R
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


def strip_text(fig):
    """Figures shown to the user carry no text (CLAUDE.md §8 item 63): titles, labels, legends and
    annotations and tick labels go; the numbers live in the docs. Scale bars stay (1 km)."""
    if fig._suptitle is not None:
        fig._suptitle.remove()
        fig._suptitle = None
    for ax in fig.axes:
        ax.set_title("")
        ax.set_title("", loc="left")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelbottom=False, labelleft=False, labeltop=False, labelright=False)
        for t in list(ax.texts):
            t.remove()
        if ax.get_legend() is not None:
            ax.get_legend().remove()


def smooth_curve(rng, length_m, bend_deg, wiggle_deg, mid=(0.0, 0.0), n=400):
    """A random smooth curve of the given length centred on mid: heading turns by bend_deg in total
    (constant curvature) plus a sinusoid of amplitude wiggle_deg over one period, random direction/phase."""
    s = np.linspace(-0.5, 0.5, n)
    th0, ph = rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)
    sign = rng.choice((-1, 1))
    th = th0 + sign * math.radians(bend_deg) * s + math.radians(wiggle_deg) * np.sin(2 * math.pi * s + ph)
    ds = length_m / (n - 1)
    xy = np.cumsum(np.c_[np.cos(th), np.sin(th)] * ds, axis=0)
    return xy - xy[n // 2] + np.array(mid)


def curve_dist(p, poly):
    a, b = poly[:-1], poly[1:]
    ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / (ab * ab).sum(1), 0, 1)
    return float(np.min(np.hypot(*(a + t[:, None] * ab - p).T)))


def generate(a, rng):
    """Grow, fill, carve and deploy as described above; returns everything the figures need."""
    spine = smooth_curve(rng, a.spine * 1000, a.bend, a.wiggle) if a.spine > 0 else None
    weight = {}

    def w(h):
        if spine is None:
            return 1.0
        if h not in weight:
            d = curve_dist(np.array(centre(h)), spine)
            weight[h] = max(1e-6, math.exp(-0.5 * (d / (a.width * 500)) ** 2))
        return weight[h]

    # 1 Eden growth (weighted by the spine when there is one)
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
        if spine is None:
            k = rng.randrange(len(frontier))
        else:
            ws = [w(h) for h in frontier]
            x, k = rng.random() * sum(ws), 0
            while x > ws[k]:
                x -= ws[k]
                k += 1
        h = frontier[k]
        frontier[k] = frontier[-1]
        frontier.pop()
        onf.discard(h)
        add(h)
    grown = len(cells)

    # 2 concavity filling, recording the order so any convexity can be read off
    hull = hull_cells(cells)
    todo = [h for h in hull if h not in S]
    while todo:
        score = [sum((h[0] + dq, h[1] + dr) in S for dq, dr in NB) for h in todo]
        best = max(score)
        h = todo.pop(rng.choice([j for j, v in enumerate(score) if v == best]))
        cells.append(h)
        S.add(h)
    upto = lambda kappa: max(grown, math.ceil(kappa * len(hull) - 1e-9))
    final = cells[:upto(a.convexity)]

    # 3 gaps: lakes inside, a river across
    land = set(final)
    lakes, river = [], set()
    for _ in range(a.lakes):
        lake = []   # interior: land whose six neighbours are land or this lake (so the lake never reaches the edge)
        interior = lambda h: h in land and all((h[0] + dq, h[1] + dr) in land or (h[0] + dq, h[1] + dr) in lake
                                               for dq, dr in NB)
        cand = [h for h in final if interior(h)]
        if not cand:
            break
        lake.append(rng.choice(cand))
        land.discard(lake[0])
        fr = [(lake[0][0] + dq, lake[0][1] + dr) for dq, dr in NB]
        while len(lake) < a.lakeCells:
            fr = [h for h in fr if interior(h)]
            if not fr:
                break
            h = fr.pop(rng.randrange(len(fr)))
            lake.append(h)
            land.discard(h)
            fr += [(h[0] + dq, h[1] + dr) for dq, dr in NB]
        lakes.append(lake)
    if a.river > 0:
        P = np.array([centre(h) for h in final])
        span = float(np.hypot(*(P.max(0) - P.min(0))))
        river_curve = smooth_curve(rng, 2 * span, a.riverBend, a.riverWiggle, mid=tuple(P.mean(0)))
        river = {h for h in land if curve_dist(np.array(centre(h)), river_curve) <= a.river * W / 2}
        land -= river
    else:
        river_curve = None
    domain = [h for h in final if h in land]

    # 4 nodes, uniform over the land
    nodes = []
    for _ in range(round(len(domain) * AREA / a.spacing ** 2)):
        h = rng.choice(domain)
        cx, cy = centre(h)
        while True:
            x, y = cx + rng.uniform(-W / 2, W / 2), cy + rng.uniform(-R, R)
            if cell_at(x, y) == h:
                break
        obs, cpu, comm = rng.random(), rng.random(), 1 - rng.random()
        nodes.append((len(nodes), x, y, h[0], h[1], obs, cpu, comm))
    return dict(cells=cells, grown=grown, hull=hull, upto=upto, final=final, domain=domain, lakes=lakes,
                river=river, river_curve=river_curve, spine=spine, nodes=nodes,
                lake_set={h for l in lakes for h in l})


def add_args(ap):
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cells", type=int, default=300, help="cells grown (a uav-coop cluster: 60)")
    ap.add_argument("--convexity", type=float, default=0.8, help="target convexity before carving")
    ap.add_argument("--spine", type=float, default=0, help="spine length, km (0: plain Eden growth)")
    ap.add_argument("--bend", type=float, default=0, help="spine: total turn, degrees")
    ap.add_argument("--wiggle", type=float, default=0, help="spine: sinusoidal wiggle amplitude, degrees")
    ap.add_argument("--width", type=float, default=1.0, help="spine: domain width scale (2 sigma), km")
    ap.add_argument("--lakes", type=int, default=0)
    ap.add_argument("--lakeCells", type=int, default=8)
    ap.add_argument("--river", type=float, default=0, help="river width, cells (0: none)")
    ap.add_argument("--riverBend", type=float, default=60, help="river: total turn, degrees")
    ap.add_argument("--riverWiggle", type=float, default=40, help="river: wiggle amplitude, degrees")
    ap.add_argument("--spacing", type=float, default=35.0, help="one node per spacing^2")


def main():
    ap = argparse.ArgumentParser()
    add_args(ap)
    ap.add_argument("--show", default="0.8,1", help="convexities drawn in the filling panels")
    ap.add_argument("--out", required=True)
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    rng = random.Random(a.seed)

    g = generate(a, rng)
    cells, grown, hull, upto, final, nodes = g["cells"], g["grown"], g["hull"], g["upto"], g["final"], g["nodes"]
    raw = grown / len(hull)
    area = AREA
    gaps = {h: "lake" for h in g["lake_set"]} | {h: "river" for h in g["river"]}

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out + "-cells.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["q", "r", "cx", "cy", "order", "filled", "type"])
        for j, h in enumerate(final):
            w.writerow([h[0], h[1], f"{centre(h)[0]:.3f}", f"{centre(h)[1]:.3f}", j, int(j >= grown),
                        gaps.get(h, "land")])
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
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    span = (max(xs) - min(xs) + W) / 1000, (max(ys) - min(ys) + 2 * R) / 1000
    print(f"grown {grown} cells, convexity {raw:.2f}, {len(holes(cells[:grown]))} holes; hull {len(hull)} cells; "
          f"saved convexity {len(final) / len(hull):.2f}: {len(final)} cells, {len(final) * area / 1e6:.2f} km2, "
          f"{len(nodes)} nodes; extent {span[0]:.1f} x {span[1]:.1f} km")
    print(f"  {out}")


if __name__ == "__main__":
    main()
