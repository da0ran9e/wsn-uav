"""Partitions side by side for the propose iterations (CLAUDE.md §8 item 135): clusters, critical cells, flight
paths and team 1's transits of one tour kind. No text (item 63).

    python3 tools/iter_fig.py OUT.png KIND WORK[:KIND] [WORK[:KIND] ...]      (a work's own tour kind after a colon)
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from map_gen import corners, strip_text
from mission_policy import tour
from mission_report import load_map

PAL = ["#c9dcf3", "#f6d6b8", "#cfe8cf", "#e8d3ee", "#f3e6a9", "#d6e4e8", "#f2c9cf", "#dcd6c8",
       "#bfe0dd", "#e6cfb3", "#d9e8b5", "#cfcfe8"]
INK, SURF = "#0b0b0b", "#fcfcfb"


def panel(ax, w, kind):
    M = load_map(w, schemes=("rf",), with_bits=False)
    for h in M["water"]:
        ax.add_collection(PolyCollection([corners(h)], facecolors="#9cc3e6", edgecolors=SURF, linewidths=.3))
    for k, C in M["cl"].items():
        ax.add_collection(PolyCollection([corners(h) for h in C["geo"]["cells"]], facecolors=PAL[(k - 1) % len(PAL)],
                                         edgecolors=SURF, linewidths=.3))
        ax.plot(*C["geo"]["path"].T, color=INK, lw=1.3)
        for h in C["P"]["crit"]:
            ax.scatter(*C["geo"]["c"][h], s=22, color="#ffffff", edgecolors=INK, lw=.8, zorder=4)
        ch = next(x for x in C["geo"]["nodes"] if x["isCH"] == "1")
        ax.scatter(float(ch["x"]), float(ch["y"]), s=90, marker="*", color="#ffffff", edgecolors=INK, lw=.8, zorder=5)
    legs, _ = tour(M, kind)
    pts = [M["bs"]] + [p for l in legs for p in (l[1], l[2])] + [M["bs"]]
    for a, b in zip(pts[0::2], pts[1::2]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#c0392b", lw=1.1, ls=(0, (3, 2)))
    ax.scatter(*M["bs"], s=50, marker="s", color=INK)
    xy = np.array([C["geo"]["c"][h] for C in M["cl"].values() for h in C["geo"]["cells"]] + [M["bs"]])
    ax.set_xlim(xy[:, 0].min() - 300, xy[:, 0].max() + 300)
    ax.set_ylim(xy[:, 1].min() - 300, xy[:, 1].max() + 300)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    out, kind, works = sys.argv[1], sys.argv[2], sys.argv[3:]
    fig, axs = plt.subplots(1, len(works), figsize=(7 * len(works), 7), dpi=130, facecolor=SURF)
    for ax, w in zip(np.atleast_1d(axs), works):
        w, _, k = w.partition(":")
        panel(ax, w, k or kind)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
