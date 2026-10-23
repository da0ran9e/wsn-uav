"""The factor sweep (factor_sweep.py --table) summarised (CLAUDE.md §8 item 149). Figures have no text (item 63).

    python3 tools/factor_fig.py TABLE.md OUT.md FIG.png

Per factor and level, over the seeds: team 1's tour at 45 degree bank with the delivery fixes, CHORD-T and
MEANDER, the paired difference CHORD - MEANDER (positive: MEANDER faster) and how many seeds MEANDER wins, the same
at 30 degrees, and the critical cells' mean distance to their path. Bank: the base pairs at 30, 45, 60 degrees.
FIG: two rows of small multiples, one panel per factor (size, aspect, bend, bs, span, q, bank; levels left to right
as in factor_sweep.FACTORS). Top: the paired tour difference at 45 degrees (bank: at each bank), bars the mean,
dots the seeds, the zero line grey, one scale for the row. Bottom: the same for the mean critical-cell distance.
"""
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from factor_sweep import BASE, FACTORS
from map_gen import strip_text

SURF, BAR, DOT, ZERO = "#fcfcfb", "#1c5cab", "#0b0b0b", "#b9b8b4"
COLS = ["cụm", "cell", "50", "45", "30", "60", "core", "lead", "transit", "bs", "crit", "dist", "p90", "far"]


def load(path):
    R = defaultdict(dict)   # (factor, level, seed) -> method -> {col: value}
    for line in open(path).read().splitlines()[2:]:
        c = [x.strip() for x in line.strip("|").split("|")]
        v = {k: float(x.split()[0]) for k, x in zip(COLS, c[4:])}
        R[(c[0], int(c[1]), int(c[2]))][c[3]] = v
    return R


def label(f, i):
    lv = FACTORS[f][i]
    return ", ".join(f"{k} {v:g}" if isinstance(v, (int, float)) else f"{k} {v}" for k, v in lv.items())


def main():
    R = load(sys.argv[1])
    rows = ["| yếu tố | mức | seed | tour 45° CHORD-T / MEANDER (s) | chênh TB (min–max) | MEANDER thắng | "
            "chênh 30° | khoảng cách critical TB CHORD-T / MEANDER (m) | cụm |", "|---" * 9 + "|"]
    panels = {}
    for f in list(FACTORS) + ["bank"]:
        levels = range(len(FACTORS[f])) if f != "bank" else range(3)
        dT, dD = [], []
        for i in levels:
            key = (f, i) if f != "bank" else ("size", [lv["K"] for lv in FACTORS["size"]].index(BASE["K"]))
            ps = [(s, m) for (ff, ii, s), m in sorted(R.items()) if (ff, ii) == key and len(m) == 2]
            col = "45" if f != "bank" else ("30", "45", "60")[i]
            t = [m["CHORD"][col] - m["MEANDER"][col] for _, m in ps]
            d = [m["CHORD"]["dist"] - m["MEANDER"]["dist"] for _, m in ps]
            dT.append(t); dD.append(d)
            if not ps:
                continue
            ch, ml = (np.mean([m[x][col] for _, m in ps]) for x in ("CHORD", "MEANDER"))
            t30 = [m["CHORD"]["30"] - m["MEANDER"]["30"] for _, m in ps]
            lv = label(f, i) if f != "bank" else f"bank {(30, 45, 60)[i]}"
            rows.append(f"| {f} | {lv} | {len(ps)} | {ch:.0f} / {ml:.0f} | {np.mean(t):+.0f} ({min(t):+.0f}…{max(t):+.0f}) | "
                        f"{sum(x > 0 for x in t)}/{len(t)} | {np.mean(t30):+.0f} | "
                        f"{np.mean([m['CHORD']['dist'] for _, m in ps]):.0f} / {np.mean([m['MEANDER']['dist'] for _, m in ps]):.0f} | "
                        f"{np.mean([m['MEANDER']['cụm'] for _, m in ps]):.1f} |")
        panels[f] = (dT, dD)
    open(sys.argv[2], "w").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    fig, axs = plt.subplots(2, len(panels), figsize=(2.2 * len(panels), 5.2), dpi=150, facecolor=SURF,
                            sharey="row", gridspec_kw=dict(wspace=0.08, hspace=0.12))
    for j, (f, (dT, dD)) in enumerate(panels.items()):
        for r, vals in enumerate((dT, dD)):
            ax = axs[r, j]
            ax.set_facecolor(SURF)
            for i, v in enumerate(vals):
                if v:
                    ax.bar(i, np.mean(v), width=0.62, color=BAR, alpha=0.85, zorder=2)
                    ax.scatter([i] * len(v), v, s=12, color=DOT, zorder=3, edgecolors=SURF, linewidths=0.6)
            ax.axhline(0, color=ZERO, lw=1, zorder=1)
            ax.set_xticks([])
            for sp in ("top", "right", "bottom"):
                ax.spines[sp].set_visible(False)
            if j:
                ax.spines["left"].set_visible(False)
                ax.tick_params(left=False)
    strip_text(fig)
    fig.savefig(sys.argv[3], facecolor=SURF, bbox_inches="tight", pad_inches=0.05)


if __name__ == "__main__":
    main()
