"""Fig. 6 of draft v5, redrawn (CLAUDE.md §8 item 184): mean T* versus the number of clusters, one panel per A2G range,
from numbers.csv (estimate.py). The LM-Tour line is an estimate (hollow markers, dashed). Paper version, with labels.

    python3 paper/icc-v5/fig_mission.py      # paper/icc-v5/figs/fig6-tstar-vs-k-4ranges.{pdf,png}
"""
import csv, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(f"{H}/numbers.csv")))
K = {"k8-s1": 8, "k12-s1": 12, "k16-s1": 15}
STYLE = [("LM-Tour + River-FC", "#e34948", "o"), ("CHORD + River-FC", "#1c5cab", "s"), ("FC + gather", "#eda100", "v"),
         ("FC + DTSP-N", "#1baf7a", "D"), ("Single pass, no cooperation", "#7a5195", "^"),
         ("No broadcast (rotary TSP)", "#8c8c8c", ">"), ("Oracle", "#222222", ".")]
fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.4), sharey=True)
for ax, r in zip(axs, ("1000", "500", "200", "150")):
    for d, c, mk in STYLE:
        pts = sorted((K[x["map"]], float(x["Tstar"])) for x in rows if x["r"] == r and x["design"] == d)
        est = d.startswith("LM")
        ax.plot(*zip(*pts), color=c, marker=mk, ms=4, lw=1.1, ls="--" if est or d == "Oracle" else "-",
                mfc="white" if est else c, label=d + (" [EST]" if est else ""))
    ax.set_yscale("log")
    ax.set_title(f"$r$ = {r} m", fontsize=8)
    ax.set_xticks([8, 12, 15])
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3, lw=0.5)
axs[0].set_ylabel("Mean $T^\\star$ (s)", fontsize=8)
fig.supxlabel("Number of clusters $K$", fontsize=8, y=0.02)
fig.legend(*axs[0].get_legend_handles_labels(), loc="upper center", ncol=4, fontsize=6, frameon=False,
           bbox_to_anchor=(0.5, 1.12))
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(f"{H}/figs/fig6-tstar-vs-k-4ranges.{ext}", dpi=200, bbox_inches="tight")
