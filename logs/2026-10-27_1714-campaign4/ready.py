"""Mean River-ready time (riverReady of lm_tour.py score: per critical cell, team 1 leaving its cluster plus ns-3
River's doneS, seconds from take-off; mean over the critical cells) per scheme, channel and map, over the seeds
every River scheme has done (as table.py). paper/TECHREPORT-vi.md section 3.3.

    python3 ready.py logs/2026-10-27_1714-campaign4 > ready.md
"""
import csv, glob, os, re, sys

import numpy as np

H = sys.argv[1]
X = {}
for d in sorted(glob.glob(f"{H}/score/R*/*-k*")):
    m = re.search(r"/R(\d+)/(\w+)-k(\d+)$", d)
    R, env, K = int(m[1]), m[2], int(m[3])
    files = ([(None, "score-ns3.csv")] if os.path.exists(f"{d}/done") else []) + \
            [(s, f"score-{s.lower()}.csv") for s in ("CP", "LMD", "DR") if os.path.exists(f"{d}/done-{s.lower()}")]
    for want, f in files:
        for r in csv.DictReader(open(f"{d}/{f}")):
            s = next(s for s in ("LMD", "CP", "DR") if f"/{s}/" in r["work"])
            if want is None and s == "DR":   # the pass before item 193, as table.py
                continue
            X.setdefault((s, env, K, R), []).append(float(r["riverReady"]))
print("| kênh | K | LM-Tour | CHORD | DTSP-N + River | seed |")
print("|---|---|---|---|---|---|")
for env in ("open", "r500", "r200", "r100"):
    for K in (8, 12, 16):
        Rs = [R for R in range(1, 11) if all((s, env, K, R) in X for s in ("LMD", "CP", "DR"))]
        if not Rs:
            continue
        v = [np.mean([np.mean(X[(s, env, K, R)]) for R in Rs]) for s in ("LMD", "CP", "DR")]
        print(f"| {env} | {K} | " + " | ".join(f"{x:.0f}" for x in v) + f" | {len(Rs)} |")
