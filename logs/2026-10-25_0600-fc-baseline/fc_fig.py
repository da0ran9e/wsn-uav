"""One map, CHORD (P*, team 1's Dubins tour) beside FC's flight in each channel (CLAUDE.md §8 item 166). No text.

    python3 fc_fig.py OUT.png CHORD_WORK FC_WORK [FC_WORK ...]       (FC_WORK holds fc-path.csv from l1_rank -m FC)
"""
import csv, sys

sys.path.insert(0, "/home/user/wsn-uav/uav-l2/tools")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from iter_fig import INK, PAL, SURF, panel
from map_gen import corners, strip_text
from mission_report import load_map

out, chord, works = sys.argv[1], sys.argv[2], sys.argv[3:]
fig, axs = plt.subplots(1, 1 + len(works), figsize=(6 * (1 + len(works)), 6), dpi=130, facecolor=SURF)
xy = [panel(axs[0], chord, "kin")]
for ax, w in zip(axs[1:], works):
    M = load_map(w, schemes=("rf",), with_bits=False)
    for h in M["water"]:
        ax.add_collection(PolyCollection([corners(h)], facecolors="#9cc3e6", edgecolors=SURF, linewidths=.3))
    for k, C in M["cl"].items():
        ax.add_collection(PolyCollection([corners(h) for h in C["geo"]["cells"]], facecolors=PAL[(k - 1) % len(PAL)],
                                         edgecolors=SURF, linewidths=.3))
        for h in C["P"]["crit"]:
            ax.scatter(*C["geo"]["c"][h], s=22, color="#ffffff", edgecolors=INK, lw=.8, zorder=4)
    P = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/fc-path.csv"))])
    ax.plot(*P.T, color="#c0392b", lw=.9, zorder=3)
    ax.scatter(*M["bs"], s=50, marker="s", color=INK)
    ax.set_aspect("equal")
    ax.axis("off")
    xy.append(P)
xy = np.vstack(xy)
for ax in axs:
    ax.set_xlim(xy[:, 0].min() - 150, xy[:, 0].max() + 150)
    ax.set_ylim(xy[:, 1].min() - 150, xy[:, 1].max() + 150)
strip_text(fig)
fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
