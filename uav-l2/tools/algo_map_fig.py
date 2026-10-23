"""The algorithms side by side on one map (CLAUDE.md §8 item 141). No text (item 63).

    python3 tools/algo_map_fig.py OUT.png phase1 WORK    # P* | B5 | B8-500 | B3-500 | B6
    python3 tools/algo_map_fig.py OUT.png layer3 WORK    # River | direct pull | Trickle

WORK is a CHORD-T work folder (VB/chordT1/<map>, with r<k>-{rf,d,t} runs for layer3). One scale for all panels.
phase1: land grey, lakes blue, critical cells white circles, BS black square. P* as iter_fig draws it. B5 the
  serpentine of l1_rank.b5_sweep's lane width (black), B8 its circles of radius R_TURN around each group's hover
  point (black), B3 the hover points (black triangles), B6 one stop per critical cell; transits red dashed.
layer3: lakes left as holes, the CHORD-T clusters' lines (black) and CHs (white stars); each critical cell filled by the time it holds
  its window after the UAV left its cluster (doneS), one blue ramp light (early) to dark (late), shared by the
  three panels.
"""
import math, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

import l1_model as L
import l1_rank
import swath
from iter_fig import INK, SURF, panel
from map_gen import corners, strip_text
from mission_baselines import groups, tsp_order
from mission_policy import R_TURN
from mission_report import load_map

LAND, WATER, RED = "#e4e3df", "#9cc3e6", "#c0392b"
RAMP = LinearSegmentedColormap.from_list("blue", ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf",
                                                  "#184f95", "#0d366b"])


def ground(ax, M, water=WATER):
    for h in M["water"]:
        ax.add_collection(PolyCollection([corners(h)], facecolors=water, edgecolors=SURF, linewidths=.3))
    for C in M["cl"].values():
        ax.add_collection(PolyCollection([corners(h) for h in C["geo"]["cells"]], facecolors=LAND, edgecolors=SURF,
                                         linewidths=.3))
    ax.scatter(*M["bs"], s=50, marker="s", color=INK, zorder=6)
    ax.set_aspect("equal")
    ax.axis("off")


def crits(M):
    return {(k, h): tuple(C["geo"]["c"][h]) for k, C in M["cl"].items() for h in C["P"]["crit"]}


def marks(ax, pos):
    ax.scatter(*np.array(list(pos.values())).T, s=22, color="#ffffff", edgecolors=INK, lw=.8, zorder=5)


def dash(ax, pts):
    ax.plot(*np.array(pts).T, color=RED, lw=1.1, ls=(0, (3, 2)), zorder=3)


def tour_stops(ax, bs, stops):
    o = tsp_order(bs, stops)
    dash(ax, [bs] + [stops[i] for i in o] + [bs])
    return o


def phase1(axs, w):
    xy = [panel(axs[0], w, "kin")]
    M = load_map(w, schemes=("rf",), with_bits=False)
    M["name"] = l1_rank.mapname(w)
    pos = crits(M)
    for ax in axs[1:]:
        ground(ax, M)
        marks(ax, pos)
    # B5: the serpentine at the lane width l1_rank chose
    C = L.clues()
    _, lane, _ = l1_rank.b5_sweep(M, C, L.order(C, "interleaved"), list(pos), M["cl"])
    land = {h for cl in M["cl"].values() for h in cl["geo"]["cells"]}
    P = swath.routes(land, M["bs"], lane)[0][3]["poly"]
    axs[1].plot(*P.T, color=INK, lw=.8, zorder=4)
    dash(axs[1], [M["bs"], P[0]])
    dash(axs[1], [P[-1], M["bs"]])
    xy.append(P)
    # B8-500 and B3-500: the same groups
    G = groups(pos, 500)
    hp = [g[0] for g in G]
    tour_stops(axs[2], M["bs"], hp)
    for c in hp:
        a = np.linspace(0, 2 * math.pi, 120)
        axs[2].plot(c[0] + R_TURN * np.cos(a), c[1] + R_TURN * np.sin(a), color=INK, lw=1.1, zorder=4)
    tour_stops(axs[3], M["bs"], hp)
    axs[3].scatter(*np.array(hp).T, s=60, marker="^", color=INK, zorder=6)
    # B6: one stop per critical cell
    tour_stops(axs[4], M["bs"], list(pos.values()))
    xy.append(np.array([M["bs"]] + [c for C in M["cl"].values() for c in C["geo"]["c"].values()]))
    return xy


def layer3(axs, w):
    M = load_map(w, schemes=("rf", "d", "t"), with_bits=False)
    done = {t: {(k, h): float(C["res"][t][h]["doneS"]) for k, C in M["cl"].items() for h in C["P"]["crit"]}
            for t in ("rf", "d", "t")}
    vmax = max(v for d in done.values() for v in d.values())
    for ax, t in zip(axs, ("rf", "d", "t")):
        ground(ax, M, water=SURF)
        for (k, h), v in done[t].items():
            ax.add_collection(PolyCollection([corners(h)], facecolors=[RAMP(max(v, 0) / vmax)], edgecolors=INK,
                                             linewidths=.6, zorder=4))
        for C in M["cl"].values():
            ax.plot(*C["geo"]["path"].T, color=INK, lw=1.2, zorder=5)
            ch = next(x for x in C["geo"]["nodes"] if x["isCH"] == "1")
            ax.scatter(float(ch["x"]), float(ch["y"]), s=90, marker="*", color="#ffffff", edgecolors=INK, lw=.8,
                       zorder=6)
    return [np.array([M["bs"]] + [c for C in M["cl"].values() for c in C["geo"]["c"].values()])]


def main():
    out, mode, w = sys.argv[1], sys.argv[2], sys.argv[3]
    n = 5 if mode == "phase1" else 3
    fig, axs = plt.subplots(1, n, figsize=(7 * n, 7), dpi=130, facecolor=SURF)
    xy = np.vstack((phase1 if mode == "phase1" else layer3)(axs, w))
    for ax in axs:
        ax.set_xlim(xy[:, 0].min() - 300, xy[:, 0].max() + 300)
        ax.set_ylim(xy[:, 1].min() - 300, xy[:, 1].max() + 300)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
