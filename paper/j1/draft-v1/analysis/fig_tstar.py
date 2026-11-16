"""Mission time T* of campaign 4 (ns-3, kind = ns3 only): per-seed means, mean and 95 % CI over seeds (Student t).

    python3 fig_tstar.py CAMPAIGN4_CSV OUT_PREFIX      -> OUT_PREFIX.md, .tex (table rows), .pdf (labelled)
"""
import csv, sys, collections
import numpy as np
from scipy.stats import t as tdist

CSV, OUT = sys.argv[1:3]
ENV = [("open", 1016), ("r500", 498), ("r200", 199), ("r100", 99)]
MAPS = [("k8-s1", 8), ("k12-s1", 12), ("k16-s1", 15)]
SCH = [("B1", "No broadcast (rotary TSP)", "#888888", "d"), ("DN", "FC + DTSP-N", "#b5403a", "s"), ("DR", "DTSP-N + River", "#e9a03b", "v"),
       ("CP", "CHORD + River", "#2a6f97", "o"), ("LMD", "LM-Tour + River", "#2a9d8f", "^")]
v = collections.defaultdict(list)
for r in csv.DictReader(open(CSV)):
    if r["kind"] == "ns3": v[(r["scheme"], r["env"], r["map"])].append(float(r["Tstar"]))


def ci(x):
    x = np.array(x); n = len(x)
    return x.mean(), (tdist.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")), n


md = ["| Scheme | " + " | ".join(f"R50 = {r} m" for _, r in ENV) + " |", "|---|---|---|---|---|"]
tex = []
for s, name, _, _ in SCH:
    cells = []
    for e, _ in ENV:
        cells.append(" / ".join(f"{ci(v[(s, e, m)])[0]:.0f}" for m, _ in MAPS))
    md.append(f"| {name} | " + " | ".join(cells) + " |"); tex.append(f"{name} & " + " & ".join(cells) + r" \\")
md += ["", "95 % CI half-widths (s) and seeds, k8 / k12 / k15:", ""]
for s, name, _, _ in SCH:
    md.append(f"- {name}: " + "; ".join(f"{e}: " + " / ".join(f"±{ci(v[(s, e, m)])[1]:.0f} (n={ci(v[(s, e, m)])[2]})" for m, _ in MAPS) for e, _ in ENV))
# paired LM-Tour vs others, per seed
md += ["", "LM-Tour relative to each scheme (%, k8 / k12 / k15):", ""]
for s, name, _, _ in SCH[:-1]:
    md.append(f"- vs {name}: " + "; ".join(f"{e}: " + " / ".join(f"{100 * (ci(v[('LMD', e, m)])[0] / ci(v[(s, e, m)])[0] - 1):+.0f}" for m, _ in MAPS) for e, _ in ENV))
open(OUT + ".md", "w").write("\n".join(md) + "\n"); open(OUT + ".tex", "w").write("\n".join(tex) + "\n"); print("\n".join(md))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.6), sharey=True)
for ax, (m, K) in zip(axs, MAPS):
    for s, name, c, mk in SCH:
        mu = [ci(v[(s, e, m)])[0] for e, _ in ENV]; hw = [ci(v[(s, e, m)])[1] for e, _ in ENV]
        ax.errorbar([r for _, r in ENV], mu, yerr=hw, fmt=mk + "-", c=c, ms=4, lw=1, capsize=2, label=name)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{K} clusters", fontsize=8)
    ax.set_xlabel("A2G range $R_{50}$ (m)", fontsize=8); ax.tick_params(labelsize=7); ax.grid(alpha=0.3, which="both", lw=0.4)
axs[0].set_ylabel("mean mission time $T^\\star$ (s)", fontsize=8)
axs[2].legend(fontsize=5.5, frameon=False, loc="center right")
fig.tight_layout(); fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
