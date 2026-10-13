"""A gallery of layer-2 domains made by map_gen.generate: long, curved, with lakes, with a river.

    python3 tools/domain_gallery.py --data docs/data --figs docs/figures

Every domain grows 300 cells (five uav-coop clusters' worth). Writes DATA/domain-NAME-{cells,nodes}.csv
and FIGS/domain-gallery.png.
"""
import argparse, csv, math, os, random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
import numpy as np

from map_gen import AREA, W, add_args, centre, corners, generate, hull_cells, outline, holes

INK, INK2, SURF = "#0b0b0b", "#52514e", "#fcfcfb"
LAND, WATER, DOT = "#c9dcf3", "#3987e5", "#1c5cab"

# name, title, options (map_gen flags), seed
DOMAINS = [
    ("long", "Dài, thẳng", dict(spine=7, width=0.7, convexity=0), 1),
    ("arc", "Cong (chữ C)", dict(spine=8, bend=200, width=0.7, convexity=0), 2),
    ("snake", "Uốn lượn (chữ S)", dict(spine=8, wiggle=75, width=0.7, convexity=0), 3),
    ("lakes", "Khối có hồ", dict(convexity=0.8, lakes=4, lakeCells=10), 4),
    ("river", "Khối có sông cắt ngang", dict(convexity=0.8, river=1), 5),
    ("mix", "Dải cong có hồ và sông", dict(spine=8, bend=120, width=1.0, convexity=0, lakes=2, lakeCells=8,
                                           river=1, riverBend=30, riverWiggle=20), 16),
]


def components(cells):
    S, seen, n = set(cells), set(), 0
    for h in cells:
        if h in seen:
            continue
        n += 1
        todo = [h]
        seen.add(h)
        while todo:
            x = todo.pop()
            for dq, dr in ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)):
                m = (x[0] + dq, x[1] + dr)
                if m in S and m not in seen:
                    seen.add(m)
                    todo.append(m)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    a0 = ap.parse_args()
    fig, axs = plt.subplots(2, 3, figsize=(17, 12), dpi=140, facecolor=SURF)
    for ax, (name, title, opts, seed) in zip(axs.ravel(), DOMAINS):
        p = argparse.ArgumentParser()
        add_args(p)
        a = p.parse_args([])
        a.seed = seed
        for k, v in opts.items():
            setattr(a, k, v)
        g = generate(a, random.Random(seed))
        dom = g["domain"]
        gaps = {h: "lake" for h in g["lake_set"]} | {h: "river" for h in g["river"]}
        with open(os.path.join(a0.data, f"domain-{name}-cells.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["q", "r", "cx", "cy", "type"])
            for h in g["final"]:
                w.writerow([h[0], h[1], f"{centre(h)[0]:.3f}", f"{centre(h)[1]:.3f}", gaps.get(h, "land")])
        with open(os.path.join(a0.data, f"domain-{name}-nodes.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "x", "y", "q", "r", "obs", "cpu", "comm"])
            for v in g["nodes"]:
                w.writerow([v[0], f"{v[1]:.3f}", f"{v[2]:.3f}", v[3], v[4], *(f"{x:.6g}" for x in v[5:])])
        # shape numbers
        P = np.array([centre(h) for h in dom])
        ev = np.linalg.eigvalsh(np.cov((P - P.mean(0)).T))
        elong = math.sqrt(ev[1] / ev[0])
        conv = len(dom) / len(hull_cells(dom))
        ext = (P.max(0) - P.min(0) + [W, 2 * 100]) / 1000
        gap_cells = len(gaps) + len(holes(dom)) - len(g["lake_set"])   # carved + left-over holes
        # draw
        ax.add_collection(PolyCollection([corners(h) for h in dom], facecolors=LAND, edgecolors=SURF,
                                         linewidths=.3, zorder=0))
        if gaps:
            ax.add_collection(PolyCollection([corners(h) for h in gaps], facecolors=WATER, alpha=.55,
                                             edgecolors=SURF, linewidths=.3, zorder=0))
        ax.add_collection(LineCollection(outline(dom), colors=INK2, linewidths=.8, zorder=2))
        ax.scatter([v[1] for v in g["nodes"]], [v[2] for v in g["nodes"]], s=.25, color=DOT, zorder=1,
                   rasterized=True)
        if g["spine"] is not None:
            ax.plot(*g["spine"].T, color=INK, lw=.9, ls=(0, (4, 3)), alpha=.6, zorder=3)
        xs = [centre(h)[0] for h in g["final"]]; ys = [centre(h)[1] for h in g["final"]]
        cx, cy, half = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + W
        ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        vn = lambda x, f=".2f": format(x, f).replace(".", ",")
        ax.set_title(f"{title}\n{len(dom)} cell đất, {vn(len(dom) * AREA / 1e6, '.1f')} km², "
                     f"{vn(ext[0], '.1f')} × {vn(ext[1], '.1f')} km; dài {vn(elong, '.1f')} : 1, lồi {vn(conv)}\n"
                     f"{len(g['lakes'])} hồ, {'1 sông, ' if g['river'] else ''}{gap_cells} cell trống; "
                     f"{components(dom)} mảnh đất; {len(g['nodes'])} node",
                     loc="left", fontsize=9, color=INK)
        ax.plot([cx + half - W - 1000, cx + half - W], [cy - half + .5 * W] * 2, color=INK, lw=2)
        ax.text(cx + half - W - 500, cy - half + .8 * W, "1 km", ha="center", fontsize=7.5, color=INK)
        print(f"{name}: {len(dom)} land cells, extent {ext[0]:.1f} x {ext[1]:.1f} km, elongation {elong:.2f}, "
              f"convexity {conv:.2f}, lakes {len(g['lakes'])} ({[len(l) for l in g['lakes']]}), river cells "
              f"{len(g['river'])}, pieces {components(dom)}, nodes {len(g['nodes'])}")
    fig.suptitle("Miền tầng 2 sinh ngẫu nhiên: mỗi miền mọc Eden 300 cell (≈ 5 cluster); nét đứt = xương sống, "
                 "xanh đậm = hồ/sông", x=.01, ha="left", fontsize=11, color=INK)
    out = os.path.join(a0.figs, "domain-gallery.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")


if __name__ == "__main__":
    main()
