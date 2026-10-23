"""Partitions side by side for the propose iterations (CLAUDE.md §8 item 135): clusters, critical cells, flight
paths and team 1's transits of one tour kind. No text (item 63).

    python3 tools/iter_fig.py OUT.png KIND WORK[:KIND] [WORK[:KIND] ...]      (a work's own tour kind after a colon)

Transits are straight dashes, except for the kinds kin and skin: there each is drawn as the shortest Dubins path
team 1 flies (radius R_TURN; from and to the BS with the best free heading), straight where skin flies on
seamlessly.
"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from map_gen import corners, strip_text
from dubins import path
from mission_policy import R_TURN, seams, tour
from mission_report import load_map

PAL = ["#c9dcf3", "#f6d6b8", "#cfe8cf", "#e8d3ee", "#f3e6a9", "#d6e4e8", "#f2c9cf", "#dcd6c8",
       "#bfe0dd", "#e6cfb3", "#d9e8b5", "#cfcfe8"]
INK, SURF = "#0b0b0b", "#fcfcfb"


def poses(M, leg):
    """Start and end pose (x, y, heading) of a tour leg on its cluster's path, in the direction flown."""
    p = M["cl"][leg[0]]["geo"]["path"]
    h0, h1 = math.atan2(*(p[1] - p[0])[::-1]), math.atan2(*(p[-1] - p[-2])[::-1])
    if math.dist(leg[1], p[0]) < 1e-6:
        return (*p[0], h0), (*p[-1], h1)
    return (*p[-1], h1 + math.pi), (*p[0], h0 + math.pi)


def flown(M, legs, kind):
    """Team 1's transits as polylines: BS, between consecutive legs, back to the BS."""
    if kind not in ("kin", "skin"):
        pts = [M["bs"]] + [p for l in legs for p in (l[1], l[2])] + [M["bs"]]
        return [np.array([a, b]) for a, b in zip(pts[0::2], pts[1::2])]
    seam = seams(M) if kind == "skin" else {}
    dirs = [0 if math.dist(l[1], M["cl"][l[0]]["geo"]["path"][0]) < 1e-6 else 1 for l in legs]
    bs, free = M["bs"], [2 * math.pi * i / 72 for i in range(72)]
    out = [np.array(min((path((*bs, h), poses(M, legs[0])[0], R_TURN) for h in free), key=lambda q: q[1])[0])]
    for i in range(1, len(legs)):
        a, b = poses(M, legs[i - 1])[1], poses(M, legs[i])[0]
        out.append(np.array([a[:2], b[:2]]) if (legs[i - 1][0], dirs[i - 1], legs[i][0], dirs[i]) in seam
                   else np.array(path(a, b, R_TURN)[0]))
    end = poses(M, legs[-1])[1]
    out.append(np.array(min((path(end, (*bs, h), R_TURN) for h in free), key=lambda q: q[1])[0]))
    return out


def panel(ax, w, kind):
    M = load_map(w, schemes=("rf",) if os.path.exists(f"{w}/r1-rf-crit.csv") else (), with_bits=False)   # () for --geometry
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
    trs = flown(M, legs, kind)
    for q in trs:
        ax.plot(*q.T, color="#c0392b", lw=1.1, ls=(0, (3, 2)))
    ax.scatter(*M["bs"], s=50, marker="s", color=INK)
    xy = np.vstack([np.array([C["geo"]["c"][h] for C in M["cl"].values() for h in C["geo"]["cells"]] + [M["bs"]])]
                   + trs)
    ax.set_aspect("equal")
    ax.axis("off")
    return xy


def main():
    out, kind, works = sys.argv[1], sys.argv[2], sys.argv[3:]
    fig, axs = plt.subplots(1, len(works), figsize=(7 * len(works), 7), dpi=130, facecolor=SURF)
    xy = []
    for ax, w in zip(np.atleast_1d(axs), works):
        w, _, k = w.partition(":")
        xy.append(panel(ax, w, k or kind))
    xy = np.vstack(xy)   # one scale for all panels
    for ax in np.atleast_1d(axs):
        ax.set_xlim(xy[:, 0].min() - 150, xy[:, 0].max() + 150)
        ax.set_ylim(xy[:, 1].min() - 150, xy[:, 1].max() + 150)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
