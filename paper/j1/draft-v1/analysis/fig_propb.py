"""Labelled figure of the takeover activation check (Proposition 5) from the per-cell CSV of logs/2026-11-10_1400-nd1-day5.

    python3 fig_propb.py PROP_B_CELLS_CSV OUT_PREFIX
"""
import csv, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
r = list(csv.DictReader(open(sys.argv[1])))
E = np.array([float(x["e"]) for x in r]); A = np.array([int(x["act"]) for x in r]); P = np.array([float(x["pm"]) for x in r])
bins = [0, 25, 50, 75, 100, 150, 200, 300, 800]
cen = [(a + b) / 2 for a, b in zip(bins, bins[1:])]
fig, ax = plt.subplots(figsize=(3.5, 2.5))
ax.plot(cen, [A[(E >= a) & (E < b)].mean() for a, b in zip(bins, bins[1:])], "o-", c="#b5403a", ms=4, label="ns-3 passes (840 SPINE cells)")
ax.plot(cen, [P[(E >= a) & (E < b)].mean() for a, b in zip(bins, bins[1:])], "s--", c="#2a6f97", ms=4, label="Proposition 5")
ax.set_xlabel("cross-track deviation over the segment (m)", fontsize=8); ax.set_ylabel("fraction of SPINE cells activated", fontsize=8)
ax.tick_params(labelsize=7); ax.legend(fontsize=6.5, frameon=False); ax.grid(alpha=0.3, lw=0.4); ax.set_xlim(0, 560)
fig.tight_layout(); fig.savefig(sys.argv[2] + ".pdf"); fig.savefig(sys.argv[2] + ".png", dpi=200)
