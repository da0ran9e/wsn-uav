"""Cooperation gain per map under two layer-2 sets (CLAUDE.md §8 item 138). No text (item 63).

    python3 tools/coop_gain_fig.py OUT.png DRAWS.csv SET_A SET_B

Per map (grouped k2, k4, k6, k8, left to right), two bars: the paired T* gain of cooperation, B4 minus P* (both
-puq-stage-zero-redir, the tour kind of the set's better P*: kin or skin), SET_A grey, SET_B blue; whiskers +-1
paired standard error over the draws; the zero line is grey. Above zero, River makes the mission faster.
"""
import csv, math, statistics as st, sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from map_gen import strip_text

SURF, GREY, INK, PALE = "#fcfcfb", "#b9b8b4", "#1c5cab", "#8f8e8a"


def main():
    out, draws, sets = sys.argv[1], sys.argv[2], sys.argv[3:5]
    T = defaultdict(dict)
    for r in csv.DictReader(open(draws)):
        T[(r["set"], r["map"], r["method"])][int(r["draw"])] = float(r["Tstar"])
    m_ = lambda b, t: f"{b}-{t}-puq-stage-zero-redir"
    maps = sorted({k[1] for k in T if k[0] == sets[0]}, key=lambda m: (int(m.split("-")[0][1:]), m))
    fig, ax = plt.subplots(figsize=(13, 4.5), dpi=150, facecolor=SURF)
    x = 0
    for g, size in enumerate(("k2", "k4", "k6", "k8")):
        for m in (m for m in maps if m.startswith(size + "-")):
            for i, s in enumerate(sets):
                t = min(("kin", "skin"), key=lambda t: st.mean(T[(s, m, m_("P+prog", t))].values())
                        if (s, m, m_("P+prog", t)) in T else math.inf)
                P, B = T[(s, m, m_("P+prog", t))], T[(s, m, m_("B4", t))]
                d = [B[j] - P[j] for j in P]
                se = st.stdev(d) / math.sqrt(len(d))
                ax.bar(x + 0.4 * i, st.mean(d), width=0.38, color=PALE if i == 0 else INK, alpha=0.85)
                ax.plot([x + 0.4 * i] * 2, [st.mean(d) - se, st.mean(d) + se], color="#0b0b0b", lw=0.8)
            x += 1
        x += 0.8
    ax.axhline(0, color=GREY, lw=1)
    ax.set_xticks([])
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)


if __name__ == "__main__":
    main()
