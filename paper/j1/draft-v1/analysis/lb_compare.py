"""River variants against River as planned, paired on the DLG missions (k8, r100; same pass, mission index, binary).

    python3 lb_compare.py DLG_RESULTS_DIR LB_RESULTS_DIR TOUR_JSON OUT_PREFIX

DLG_RESULTS_DIR/R<seed>/r<k>-rf-*.csv: River as planned (experiment DLG). LB_RESULTS_DIR/R<seed>/r<k>-<tag>-*.csv: the
variants run by run_lb.sh. Every variant is compared with River on the missions (seed, cluster) it was run on:
doneS (seconds from the UAV leaving the cluster to the critical cell's CL holding its window), per critical cell and for
the last critical cell of each cluster; frames; MAC give-ups; radio-on time; and, for seeds with all eight clusters, the
time from take-off at which the last critical cell of the mission completes.
Writes OUT_PREFIX.md, OUT_PREFIX.csv (one row per critical cell and variant) and OUT_PREFIX.pdf.
"""
import csv, glob, json, os, sys
import numpy as np

DLG, LB, TOUR, OUT = sys.argv[1:5]
TAU = 4.8e-3
leave = {l["cluster"]: l["leave"] for l in json.load(open(TOUR))["legs"]}
NAMES = {"rf": "River", "rfX": "River + shared trees", "lb": "River-LB (balanced paths)",
         "lbs": "River-LB + shared trees", "lbm": "River-LB, members chosen", "lbms": "River-LB, members chosen + shared trees"}


def load(d, tag):
    """{(seed, cluster): dict(cells={(q, r): (lackCell, doneS, missing)}, hops, fail, on)}"""
    res = {}
    for f in glob.glob(f"{d}/R*/r*-{tag}-crit.csv"):
        seed = int(f.split("/R")[-1].split("/")[0]); k = int(os.path.basename(f).split("-")[0][1:])
        rr = list(csv.DictReader(open(f)))
        runs = list(csv.DictReader(open(f.replace("-crit", "-runs"))))
        if not rr or not runs: continue
        on = sum(float(e["txS"]) + float(e["rxS"]) + float(e["listenS"]) for e in csv.DictReader(open(f.replace("-crit", "-energy"))))
        res[(seed, k)] = dict(cells={(int(r["q"]), int(r["r"])): (int(r["lackCell"]), float(r["doneS"]), int(r["missing"])) for r in rr},
                              hops=int(runs[0]["hops"]), fail=int(runs[0]["macFail"]), on=on)
    return res


base = load(DLG, "rf")
out = ["| Variant | missions | critical cells complete | doneS mean (s): River → variant | per cell, geometric mean of the ratio | cells faster | "
       "last cell of the cluster (s): River → variant | median doneS / single-radio bound | frames | MAC give-ups | radio-on time |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
rows, per, lastm = [], {}, {}
for tag in ("rfX", "lb", "lbs", "lbm", "lbms"):
    v = load(LB, tag)
    ms = sorted(set(v) & set(base))
    if not ms: continue
    b0, v0, bl, vl, ratio_b = [], [], [], [], []
    ok = tot = 0
    for m in ms:
        cb, cv = base[m]["cells"], v[m]["cells"]
        assert set(cb) == set(cv) and all(cb[c][0] == cv[c][0] for c in cb), f"mission {m}: not the same pass"
        tot += len(cv); ok += sum(x[2] == 0 for x in cv.values())
        both = [c for c in cb if cb[c][2] == 0 and cv[c][2] == 0]
        for c in both:
            b0.append(cb[c][1]); v0.append(cv[c][1])
            if cb[c][0] > 500: ratio_b.append(cv[c][1] / (TAU * cb[c][0]))
            rows.append((m[0], m[1], c[0], c[1], tag, cb[c][0], cb[c][1], cv[c][1]))
        bl.append(max(x[1] for x in cb.values())); vl.append(max(x[1] for x in cv.values()))
    b0, v0, bl, vl = map(np.array, (b0, v0, bl, vl)); per[tag] = (b0, v0, bl, vl, ms)
    f = lambda key: sum(v[m][key] for m in ms) / sum(base[m][key] for m in ms)
    out.append(f"| {NAMES[tag]} | {len(ms)} | {ok}/{tot} | {b0.mean():.1f} → {v0.mean():.1f} ({(v0.mean() / b0.mean() - 1) * 100:+.0f} %) | "
               f"{np.exp(np.mean(np.log(np.maximum(v0, .1) / np.maximum(b0, .1)))):.2f} | {np.mean(v0 < b0) * 100:.0f} % | "
               f"{bl.mean():.1f} → {vl.mean():.1f} ({(vl.mean() / bl.mean() - 1) * 100:+.0f} %) | {np.median(ratio_b):.2f} | "
               f"{(f('hops') - 1) * 100:+.0f} % | {(f('fail') - 1) * 100:+.0f} % | {(f('on') - 1) * 100:+.0f} % |")
    for s in sorted({m[0] for m in ms}):
        if all((s, k) in v for k in leave):
            lastm.setdefault(tag, {})[s] = (max(leave[k] + max(x[1] for x in base[(s, k)]["cells"].values()) for k in leave),
                                            max(leave[k] + max(x[1] for x in v[(s, k)]["cells"].values()) for k in leave))
out += ["", "Last completion of the mission from take-off (s), River → variant, per seed with all clusters run:"]
for tag, d in lastm.items():
    out.append(f"- {NAMES[tag]}: " + ", ".join(f"seed {s}: {a:.0f} → {b:.0f}" for s, (a, b) in sorted(d.items()))
               + f"; mean {np.mean([a for a, b in d.values()]):.0f} → {np.mean([b for a, b in d.values()]):.0f}")
out += ["", "Last critical cell per cluster (s), seed: cluster River → variant:"]
for tag, (b0, v0, bl, vl, ms) in per.items():
    out.append(f"- {NAMES[tag]}: " + "; ".join(f"{m[0]}:{m[1]} {a:.0f} → {b:.0f}" for m, a, b in zip(ms, bl, vl)))
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
with open(OUT + ".csv", "w") as f:
    f.write("seed,cluster,q,r,variant,lackCell,doneS_river,doneS_variant\n")
    for r in rows: f.write(",".join(map(str, r)) + "\n")

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
tags = [t for t in ("lb", "lbs", "lbm", "lbms", "rfX") if t in per][:3]
fig, axs = plt.subplots(1, len(tags), figsize=(2.4 * len(tags), 2.5), sharey=True, squeeze=False)
for ax, tag in zip(axs[0], tags):
    b0, v0 = per[tag][:2]; hi = max(b0.max(), v0.max()) * 1.05
    ax.scatter(b0, v0, s=7, c="#2a6f97", alpha=0.7, lw=0); ax.plot([0, hi], [0, hi], "k--", lw=0.8)
    ax.set_xlim(0, hi); ax.set_ylim(0, hi); ax.set_title(NAMES[tag], fontsize=7); ax.tick_params(labelsize=7); ax.grid(alpha=0.3, lw=0.4)
    ax.set_xlabel("River as planned (s)", fontsize=8)
axs[0][0].set_ylabel("variant: completion after\nthe UAV leaves (s)", fontsize=8)
fig.tight_layout(); fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
