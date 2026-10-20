"""Layer-1 sensitivity (CLAUDE.md §8 item 114): one l1_rank.py run per changed parameter; figures without text.

    python3 tools/l1_sens.py --runs base dim64 dim256 rho0 rho05 m105 m693 --data docs/data/l1rank/sens \
        --figs docs/figures --out docs/data/l1rank/sens-table.csv

Per run and method, over every map (sizes pooled): the mean of the map means of Tstar with a 95 % t interval over
maps, the mean rank of c* in team 2's visits, and the paired change of the proposed policy against no cooperation.
FIGS/l1-sens.png: one group per run in the order given, one marker per method (propose dark blue, River report only
light blue, no cooperation amber); the second panel the mean rank of c* (same colours).
"""
import argparse, csv, math
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from map_gen import strip_text
from mission_report import GREY, SURF

METH = [("P+prog-latency-puq-stage-zero", "#1c5cab"), ("P-latency-puq-stage-zero", "#86b6ef"),
        ("B4-latency-puq-stage-zero", "#eda100")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for run in a.runs:
        D = defaultdict(dict)
        for r in csv.DictReader(open(f"{a.data}-{run}-draws.csv")):
            D[r["method"]][(r["map"], int(r["draw"]))] = r
        maps = sorted({k[0] for k in D[METH[0][0]]})
        for m in sorted(D):
            per = np.array([np.mean([float(D[m][k]["Tstar"]) for k in D[m] if k[0] == mp]) for mp in maps])
            d = np.array([np.mean([float(D[m][k]["Tstar"]) - float(D[METH[2][0]][k]["Tstar"]) for k in D[m]
                                   if k[0] == mp]) for mp in maps])
            rows.append(dict(run=run, method=m, maps=len(maps), Tstar=round(float(per.mean()), 1),
                             ci=round(float(1.96 * per.std(ddof=1) / math.sqrt(len(maps))), 1),
                             rank=round(float(np.mean([float(r["rank"]) for r in D[m].values()])), 2),
                             first=round(float(np.mean([r["rank"] == "1" for r in D[m].values()])), 3),
                             dB4=round(float(d.mean()), 1), betterThanB4=int(sum(d < -1e-9))))
    with open(a.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(" ".join(f"{k} {v}" for k, v in r.items()))
    fig, axs = plt.subplots(1, 2, figsize=(14, 4.5), dpi=150, facecolor=SURF, gridspec_kw=dict(width_ratios=[1.4, 1]))
    for ax, key in zip(axs, ("Tstar", "rank")):
        for i, (m, c) in enumerate(METH):
            for j, run in enumerate(a.runs):
                r = next(r for r in rows if r["run"] == run and r["method"] == m)
                x = j + (i - 1) * 0.22
                if key == "Tstar":
                    ax.errorbar(x, r[key], yerr=r["ci"], fmt="o", color=c, ms=6, capsize=2, lw=1.2)
                else:
                    ax.bar(x, r[key], width=.2, color=c)
        ax.set_xticks(range(len(a.runs)))
        ax.set_ylim(0, None)
        ax.grid(axis="y", color=GREY, lw=.6)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURF)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(f"{a.figs}/l1-sens.png", facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)


if __name__ == "__main__":
    main()
