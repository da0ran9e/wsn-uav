"""Table of run.sh: T* of CHORD, LM-Tour and DTSP-N + River per channel, and the paired differences (mean +- 95 %
half-width over the draws; in brackets the share of draws where the first scheme is faster).

    python3 compare.py > table.md
"""
import csv, os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ENVS = ("open", "r500", "r200", "r100")


def load(path):
    out = {}
    for r in csv.DictReader(open(path)):
        out.setdefault(r["work"].split("/")[-3], {})[int(r["draw"])] = (float(r["Tstar"]), float(r["team1"]))
    return out


def ci(x):
    x = np.asarray(x)
    return f"{x.mean():.0f} ± {1.96 * x.std(ddof=1) / np.sqrt(len(x)):.0f}"


def diff(a, b):
    d = np.array([a[i][0] - b[i][0] for i in sorted(a)])
    return f"{ci(d)} ({np.mean(d < 0) * 100:.0f} %)"


print("| kênh | T\\* CHORD | T\\* LM-Tour | T\\* DTSP-N + River | LM-Tour − CHORD | LM-Tour − DTSP-N + River | "
      "DTSP-N + River − CHORD | LM-Tour − CHORD (River dự đoán) | đội 1 CHORD / LM / DR (s) |")
print("|---|---|---|---|---|---|---|---|---|")
for e in ENVS:
    f = f"{HERE}/{e}/score-ns3.csv"
    if not os.path.exists(f):
        continue
    s = load(f)
    p = load(f"{HERE}/{e}/score-pred.csv") if os.path.exists(f"{HERE}/{e}/score-pred.csv") else {}
    C, M, D = s["CP"], s["LMD"], s["DR"]
    pr = diff(p["LMD"], p["CP"]) if p else "–"
    print(f"| {e} | {ci([v[0] for v in C.values()])} | {ci([v[0] for v in M.values()])} | "
          f"{ci([v[0] for v in D.values()])} | {diff(M, C)} | {diff(M, D)} | {diff(D, C)} | {pr} | "
          f"{C[0][1]:.0f} / {M[0][1]:.0f} / {D[0][1]:.0f} |")
