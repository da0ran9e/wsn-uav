"""Paired layer-2 differences per map against k-medoids (CLAUDE.md §8 item 136). No text (item 63).

    python3 tools/l2_compare_fig.py OUT.png DRAWS.csv L2M.csv SET [SET ...]

Three panels: T* of P*, the mean time a critical cell holds its clue set (l2_metrics readyMean), team 1's tour.
In each, four groups (k2, k4, k6, k8, left to right); per variant (colour, in the order given) one dot per map (its
paired difference to k-medoids) and a bar for the group mean; the zero line is grey.
"""
import csv, statistics as st, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from map_gen import strip_text

COL = ["#1c5cab", "#2e8b57", "#c0392b", "#8e44ad", "#d68910"]
SURF, GREY = "#fcfcfb", "#b9b8b4"


def main():
    out, draws, l2m, sets = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    T = defaultdict(list)
    for r in csv.DictReader(open(draws)):
        T[(r["set"], r["map"], r["method"])].append(float(r["Tstar"]))
    P = lambda t: f"P+prog-{t}-puq-stage-zero-redir"

    def tstar(s, m):
        ts = [st.mean(T[(s, m, P(t))]) for t in ("kin", "skin") if (s, m, P(t)) in T]
        return min(ts) if s == "kmedoids" else st.mean(T[(s, m, P("skin" if (s, m, P("skin")) in T else "kin"))])
    L2 = {(r["set"], r["map"]): r for r in csv.DictReader(open(l2m))}
    maps = sorted({k[1] for k in T if k[0] == "kmedoids"})
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5), dpi=150, facecolor=SURF)
    for ax, f in zip(axs, ("T", "readyMean", "team1")):
        for g, size in enumerate(("k2", "k4", "k6", "k8")):
            for i, s in enumerate(sets):
                ms = [m for m in maps if m.startswith(size + "-")]
                if f == "T":
                    d = [tstar(s, m) - tstar("kmedoids", m) for m in ms if (s, m, P("skin")) in T or (s, m, P("kin")) in T]
                else:
                    d = [float(L2[(s, m)][f]) - float(L2[("kmedoids", m)][f]) for m in ms if (s, m) in L2]
                if not d:
                    continue
                x = g * (len(sets) + 1) + i
                ax.bar(x, st.mean(d), width=0.7, color=COL[i], alpha=0.35)
                ax.scatter([x] * len(d), d, s=14, color=COL[i], zorder=3)
        ax.axhline(0, color=GREY, lw=1)
        ax.set_xticks([])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
