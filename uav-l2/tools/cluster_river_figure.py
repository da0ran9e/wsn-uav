"""The River plan of every cluster of a partitioned domain, on one map, without text (CLAUDE.md §8 item 63).

    python3 tools/cluster_river_figure.py --domain docs/data/domain-lakes --data docs/data/cap80 \
        --figs docs/figures

DATA holds, per cluster k: ck-lattice.csv, ck-nodes-s35.csv, ck-path-s35.csv (uav-coop-deploy --regionIn
--nodesIn) and its River plan (uav-coop2 river_plan.plan, recomputed here). Draws FIGS/cap80-river.png:
cells of each cluster (grey), River (light blue), Banks (green), Axe (blue), lakes (hatched), cluster
borders, flight paths, CH (star) and the other critical cells (rings).
"""
import argparse, csv, glob, os, re, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

from map_gen import NB, W, cell_at, centre, corners, strip_text

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import plan  # noqa: E402

INK, SURF = "#0b0b0b", "#fcfcfb"
LAND, RIVER, BANK, AXE, WATER = "#e6e5e1", "#c9dcf3", "#9fd8bf", "#1c5cab", "#3987e5"


def load_geo(data, k):
    """river_plan.load's dictionary, from one cluster's deploy outputs."""
    import math
    import numpy as np
    lat = list(csv.DictReader(open(os.path.join(data, f"c{k}-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    nodes = list(csv.DictReader(open(os.path.join(data, f"c{k}-nodes-s35.csv"))))
    path = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(os.path.join(data, f"c{k}-path-s35.csv")))])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    d = np.arange(0, seg[-1], 0.5)
    uav = np.c_[np.interp(d, seg, path[:, 0]), np.interp(d, seg, path[:, 1])]
    return dict(c=c, w=W, R=W / math.sqrt(3), cells=sel, S=set(sel), nodes=nodes, path=path, uav=uav)


def main():
    ap = argparse.ArgumentParser()
    for k in ("domain", "data", "figs"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.domain + "-cells.csv")))
    water = [(int(r["q"]), int(r["r"])) for r in rows if r["type"] != "land"]
    ks = sorted(int(re.match(r"c(\d+)-lattice", os.path.basename(f))[1]) for f in glob.glob(os.path.join(a.data, "c*-lattice.csv")))
    fig, ax = plt.subplots(figsize=(9, 10), dpi=150, facecolor=SURF)
    owner, allc = {}, []
    for k in ks:
        geo = load_geo(a.data, k)
        P = plan(geo)
        banks = {b for (x, s_), b in P["bank"].items() if b != x}
        col = {h: LAND for h in geo["cells"]}
        col.update({h: RIVER for h in P["river"]})
        col.update({b: BANK for b in banks})
        col.update({h: AXE for h in P["axe"]})
        ax.add_collection(PolyCollection([corners(h) for h in geo["cells"]], facecolors=[col[h] for h in geo["cells"]],
                                         edgecolors=SURF, linewidths=.4, zorder=0))
        ax.plot(*geo["path"].T, color=INK, lw=1.2, zorder=4)
        for h in P["crit"]:
            star = h == P["ch"]
            ax.scatter(*geo["c"][h], s=230 if star else 120, marker="*" if star else "o", color="#ffffff",
                       edgecolors=INK, lw=1.2, zorder=6)
        for h in geo["cells"]:
            owner[h] = k
        allc += geo["cells"]
    ax.add_collection(PolyCollection([corners(h) for h in water], facecolors="#dbe9f8", edgecolors=WATER,
                                     hatch="////", linewidths=0, zorder=0))
    segs = []
    for h in allc:
        v = corners(h)
        cx, cy = centre(h)
        for j in range(6):
            p, q = v[j], v[(j + 1) % 6]
            n = cell_at(p[0] + q[0] - cx, p[1] + q[1] - cy)
            if owner.get(n) != owner[h]:
                segs.append((p, q))
    ax.add_collection(LineCollection(segs, colors=INK, linewidths=1.5, zorder=3))
    xs = [centre(h)[0] for h in allc + water]; ys = [centre(h)[1] for h in allc + water]
    ax.set_xlim(min(xs) - 2 * W, max(xs) + 2 * W); ax.set_ylim(min(ys) - 2 * W, max(ys) + 2 * W)
    ax.plot([max(xs) - 1000, max(xs)], [min(ys) - 1.2 * W] * 2, color=INK, lw=2)   # 1 km
    ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    out = os.path.join(a.figs, "cap80-river.png")
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")


if __name__ == "__main__":
    main()
