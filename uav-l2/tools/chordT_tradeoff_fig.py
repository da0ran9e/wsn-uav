"""CHORD-T's trade-off over its constraint (CLAUDE.md §8 item 136). No text (item 63).

    python3 tools/chordT_tradeoff_fig.py OUT.png DRAWS.csv L2M.csv CELLSGLOB SET [SET ...]

SETs in the order to draw, k-medoids first (the reference, at zero). Three panels, one column per set:
  1  paired T* difference to k-medoids: dots one per map, bar the mean (P*, each set's better of kin / skin for
     k-medoids, kin for CHORD-T)
  2  share of critical cells holding all 12 clues after River (l1_rank cells, riverAll)
  3  paired difference of River MAC frames per map (l2_metrics), thousands
"""
import csv, glob, statistics as st, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from map_gen import strip_text

SURF, GREY, INK = "#fcfcfb", "#b9b8b4", "#1c5cab"


def main():
    out, draws, l2m, cells, sets = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
    T = defaultdict(list)
    for r in csv.DictReader(open(draws)):
        T[(r["set"], r["map"], r["method"])].append(float(r["Tstar"]))
    P = lambda t: f"P+prog-{t}-puq-stage-zero-redir"
    tstar = lambda s, m: min(st.mean(T[(s, m, P(t))]) for t in ("kin", "skin") if (s, m, P(t)) in T)
    L2 = {(r["set"], r["map"]): r for r in csv.DictReader(open(l2m))}
    C = defaultdict(list)
    for f in glob.glob(cells):
        for r in csv.DictReader(open(f)):
            C[r["set"]].append(int(r["riverAll"]))
    maps = sorted({k[1] for k in T if k[0] == sets[0]})
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5), dpi=150, facecolor=SURF)
    for i, s in enumerate(sets):
        d = [tstar(s, m) - tstar(sets[0], m) for m in maps]
        axs[0].bar(i, st.mean(d), width=0.6, color=INK, alpha=0.35)
        axs[0].scatter([i] * len(d), d, s=12, color=INK, zorder=3)
        axs[1].bar(i, st.mean(C[s]), width=0.6, color=INK, alpha=0.6)
        f = [(int(L2[(s, m)]["frames"]) - int(L2[(sets[0], m)]["frames"])) / 1000 for m in maps]
        axs[2].bar(i, st.mean(f), width=0.6, color=INK, alpha=0.35)
        axs[2].scatter([i] * len(f), f, s=12, color=INK, zorder=3)
    for ax in axs:
        ax.axhline(0, color=GREY, lw=1)
        ax.set_xticks([])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    axs[1].set_ylim(0, 1.05)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
