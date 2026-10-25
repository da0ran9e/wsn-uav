"""Figures of LM-Tour steps A and C, without text (CLAUDE.md §8 items 63, 131).

    python3 lm_fig.py surrogate FIGS                       # predicted vs ns-3 River completion, map-disjoint
    python3 lm_fig.py passes FIGS CHORDWORK LMWORK NAME     # CHORD's passes and LM-Tour's on one map
"""
import csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

T = "/home/user/wsn-uav/uav-l2/tools"
sys.path.insert(0, T)
from map_gen import corners  # noqa: E402
from mission_report import CAT, INK, SURF, WATER, load_map  # noqa: E402
from river_surrogate import Model  # noqa: E402

ENVC = {"open": "#1baf7a", "r500": "#1c5cab", "r200": "#eda100", "r100": "#e34948"}


def surrogate(figs):
    rows = [{k: (v if k in ("map", "env") else float(v)) for k, v in r.items()}
            for r in csv.DictReader(open(f"{T}/../docs/data/results/river-surrogate.csv"))]
    y = np.array([r["doneS"] for r in rows])
    p = np.zeros(len(rows))
    for g in sorted({r["map"] for r in rows}):   # leave-one-map-out, as river_surrogate.py scores it
        te = [i for i, r in enumerate(rows) if r["map"] == g]
        p[te] = Model("formula", [r for r in rows if r["map"] != g]).predict([rows[i] for i in te])
    fig, ax = plt.subplots(figsize=(5, 5), facecolor=SURF)
    ax.set_facecolor(SURF)
    top = 320
    for v in range(0, top + 1, 50):
        ax.axhline(v, color="#e6e5e1", lw=0.6, zorder=0)
        ax.axvline(v, color="#e6e5e1", lw=0.6, zorder=0)
    ax.plot([0, top], [0, top], color=INK, lw=1.0, zorder=1)
    for e, c in ENVC.items():
        m = np.array([r["env"] == e for r in rows])
        ax.scatter(y[m], p[m], s=9, color=c, alpha=0.7, lw=0, zorder=2)
    ax.set_xlim(0, top), ax.set_ylim(0, top)
    ax.set_xticks([]), ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#c9c8c3")
    fig.savefig(f"{figs}/lm-surrogate-pred-vs-ns3.png", dpi=160, bbox_inches="tight", facecolor=SURF)


def passes(figs, wc, wl, name):
    Mc, Ml = load_map(wc, schemes=(), with_bits=False), load_map(wl, schemes=(), with_bits=False)
    fig, ax = plt.subplots(figsize=(8, 8), facecolor=SURF)
    ax.set_facecolor(SURF)
    polys, cols = [], []
    for r in csv.DictReader(open(f"{wc}/domain-cells.csv")):
        h = (int(r["q"]), int(r["r"]))
        polys.append(corners(h))
        k = Mc["owner"].get(h, 0)
        cols.append(WATER if r["type"] != "land" else CAT[(k - 1) % len(CAT)] + "33" if k else "#e6e5e1")
    ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="none"))
    for k in sorted(Mc["cl"]):
        pc, pl = Mc["cl"][k]["geo"]["path"], Ml["cl"][k]["geo"]["path"]
        ax.plot(pc[:, 0], pc[:, 1], color=INK, lw=1.2, zorder=3)
        if np.abs(pl.shape[0] - pc.shape[0]) > 0 or np.abs(pl - pc).max() > 1:
            ax.plot(pl[:, 0], pl[:, 1], color="#e34948", lw=1.6, zorder=4)
        g = Mc["cl"][k]["geo"]
        for h in Mc["cl"][k]["P"]["crit"]:
            ax.scatter(*g["c"][h], s=40, facecolor="white", edgecolor=INK, lw=0.8, zorder=5)
        ch = next(n for n in g["nodes"] if n["isCH"] == "1")
        ax.scatter(float(ch["x"]), float(ch["y"]), s=90, marker="*", color="white", edgecolor=INK, lw=0.8, zorder=6)
    ax.scatter(*Mc["bs"], s=60, marker="s", color=INK, zorder=6)
    ax.set_aspect("equal"), ax.autoscale_view(), ax.axis("off")
    fig.savefig(f"{figs}/{name}", dpi=160, bbox_inches="tight", facecolor=SURF)


if __name__ == "__main__":
    if sys.argv[1] == "surrogate":
        surrogate(sys.argv[2])
    else:
        passes(*sys.argv[2:6])
