"""Fixed vs adaptive Circles on one cluster (CLAUDE.md §8 items 66-67), without text (item 63).

    python3 tools/circle_adaptive_figure.py --data docs/data/cap80-c3long --k 3 \
        --crit "docs/data/cap80-c3long/a3-{s}-crit.csv" --runs rf,ad200,ad12 --figs docs/figures --name c3

One panel per run: cluster cells (grey), River (light blue), Axe (blue), flight path, each critical cell
(white mark; star = CH) and its Circle members filled in the critical cell's colour. A fixed run (prep full
or on demand) uses Algorithm 4's ring-1 members; an adaptive run the members of the size it chose (the
`circle` column of its -crit.csv). Writes FIGS/NAME-circles.png and prints the members.
"""
import argparse, csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

from map_gen import corners, strip_text
from cluster_river_figure import load_geo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import plan  # noqa: E402

INK, SURF, GREY, RIVER, AXE = "#0b0b0b", "#fcfcfb", "#e6e5e1", "#c9dcf3", "#1c5cab"
CAT = ["#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#0d366b", "#52514e"]


def main():
    ap = argparse.ArgumentParser()
    for k in ("data", "crit", "runs", "figs", "name"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--k", type=int, required=True)
    a = ap.parse_args()
    geo = load_geo(a.data, a.k)
    P = plan(geo)
    c, sel = geo["c"], geo["cells"]
    ccol = {k: CAT[i % len(CAT)] for i, k in enumerate(P["crit"])}
    runs = a.runs.split(",")
    fig, axs = plt.subplots(1, len(runs), figsize=(6 * len(runs), 7), dpi=150, facecolor=SURF)
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    for ax, s in zip(axs, runs):
        rows = {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(a.crit.format(s=s)))}
        col = {h: RIVER for h in P["river"]}
        col.update({h: AXE for h in P["axe"]})
        mem = {}
        for k in P["crit"]:
            r = rows[k]
            if r["scheme"] == "river-adaptive":
                n = int(r["circle"])
                mem[k] = [m for m, (g0, g1) in P["adapt"][k]["sets"].get(n, []) if g1 >= g0]
            else:
                mem[k] = [m for m, G, src in P["circle"][k]]
            print(f"{s} {k}: lack {r['lackCell']}, {len(mem[k])} members, done {r['doneS']} s: "
                  + " ".join(str(m) for m in mem[k]))
        ax.add_collection(PolyCollection([corners(h) for h in sel], facecolors=[col.get(h, GREY) for h in sel],
                                         edgecolors=SURF, linewidths=.5, zorder=0))
        for k in P["crit"]:
            ax.add_collection(PolyCollection([corners(m) for m in mem[k]], facecolors=ccol[k], alpha=.75,
                                             edgecolors=INK, linewidths=.6, zorder=2))
            star = k == P["ch"]
            ax.scatter(*c[k], s=260 if star else 130, marker="*" if star else "o", color="#ffffff",
                       edgecolors=ccol[k], lw=2, zorder=5)
        ax.plot(*geo["path"].T, color=INK, lw=1.1, zorder=4)
        W = geo["w"]
        ax.set_xlim(min(xs) - 1.5 * W, max(xs) + 1.5 * W); ax.set_ylim(min(ys) - 1.5 * W, max(ys) + 1.5 * W)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
    strip_text(fig)
    out = os.path.join(a.figs, f"{a.name}-circles.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    print(f"  {out}")


if __name__ == "__main__":
    main()
