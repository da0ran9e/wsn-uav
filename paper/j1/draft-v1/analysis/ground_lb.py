"""Ground transport versus the single-radio lower bound, on the paired runs of experiment DLG
(k8-s1, r100, fixed CHORD passes, 5 ns-3 seeds x 8 clusters, 225 critical-cell completions per scheme).

    python3 ground_lb.py DLG_RESULTS_DIR TOUR_JSON OUT_PREFIX

Lower bound (Proposition 4): the CL of critical cell k has one radio, so it cannot finish before tau_min * lackCell_k,
tau_min = 4.256 ms frame + 0.192 ms turnaround + 0.352 ms ACK = 4.8 ms. lackCell = packets of its window that no node
of the cell heard. doneS = seconds from the UAV leaving the cluster to the CL holding its window (ns-3).
Also: least-squares fit doneS ~ a*lackCell + b*(lack of the other critical cells of the cluster), and the time from
take-off at which the last critical cell of the mission completes (leave time of the tour + doneS).
Writes OUT_PREFIX.md and OUT_PREFIX.pdf (labelled, for the paper).
"""
import csv, glob, json, sys
import numpy as np

RES, TOUR, OUT = sys.argv[1:4]
TAU = 4.8e-3
leave = {l["cluster"]: l["leave"] for l in json.load(open(TOUR))["legs"]}
out = ["| Scheme | completions | median doneS / bound | 90th pct | cells at the bound within 1.5x | last completion from take-off (s), per seed |",
       "|---|---|---|---|---|---|"]
data = {}
for tag, name in (("rf", "River"), ("d2", "Direct pull (planned)"), ("t", "Deluge (River cells)"), ("tp", "Deluge (path cells)")):
    rows, last = [], {}
    for f in sorted(glob.glob(f"{RES}/R*/r*-{tag}-crit.csv")):
        seed = f.split("/R")[-1].split("/")[0]; k = int(f.split("/r")[-1].split("-")[0])
        rr = list(csv.DictReader(open(f)))
        tot = sum(int(r["lackCell"]) for r in rr)
        for r in rr:
            if int(r["missing"]) == 0:
                rows.append((int(r["lackCell"]), tot - int(r["lackCell"]), float(r["doneS"]), len(rr)))
        if rr: last[seed] = max(last.get(seed, 0), leave.get(k, 0) + max(float(r["doneS"]) for r in rr))
    if not rows: continue
    a = np.array(rows, float); data[name] = a
    m = a[:, 0] > 500                                        # cells with a real lack
    ratio = a[m, 2] / (TAU * a[m, 0])
    out.append(f"| {name} | {len(a)} | {np.median(ratio):.2f} | {np.percentile(ratio, 90):.2f} | {np.mean(ratio < 1.5) * 100:.0f} % | "
               + ", ".join(f"{last[s]:.0f}" for s in sorted(last)) + f" (mean {np.mean(list(last.values())):.0f}) |")
a = data["River"]
X = np.c_[a[:, 0], a[:, 1], np.ones(len(a))]
coef, *_ = np.linalg.lstsq(X, a[:, 2], rcond=None)
pred = X @ coef
out += ["", f"River fit: doneS = {coef[0]*1e3:.2f} ms x lackCell + {coef[1]*1e3:.2f} ms x (lack of the other critical cells of the cluster) + {coef[2]:.1f} s; "
        f"R2 = {1 - np.sum((a[:, 2] - pred) ** 2) / np.sum((a[:, 2] - a[:, 2].mean()) ** 2):.2f}, n = {len(a)}.",
        f"Mean lackCell {a[:, 0].mean():.0f} packets; mean doneS {a[:, 2].mean():.1f} s; mean bound {TAU * a[:, 0].mean():.1f} s; "
        f"critical cells per cluster {a[:, 3].mean():.1f} (weighted by cell).",
        f"Tour leave times (s): {', '.join(f'{k}: {v:.0f}' for k, v in sorted(leave.items(), key=lambda kv: kv[1]))}."]
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(3.5, 2.6))
for name, c, mk in (("Deluge (path cells)", "#b5403a", "x"), ("Direct pull (planned)", "#e9a03b", "+"), ("River", "#2a6f97", "o")):
    if name in data:
        d = data[name]; ax.scatter(d[:, 0], d[:, 2], s=9, c=c, marker=mk, lw=0.7, alpha=0.8, label=name)
xs = np.array([0, 4300]); ax.plot(xs, TAU * xs, "k--", lw=1.1, label="single-radio bound")
ax.set_xlabel("packets the cell lacks after the pass", fontsize=8); ax.set_ylabel("completion after the UAV leaves (s)", fontsize=8)
ax.tick_params(labelsize=7); ax.legend(fontsize=6.5, frameon=False); ax.grid(alpha=0.3, lw=0.4); ax.set_xlim(0, 4300); ax.set_ylim(0, None)
fig.tight_layout(); fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
