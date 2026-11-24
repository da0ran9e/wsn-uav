"""K9 step B8 (hybrid option, chatlog item 375): AI cells needed per NPU share and rho, against D3 and crops only, and what
K models per AI node add to the matching time (paper/j1/PLAN-K9-DATA-vi.md section 9).

    python3 b8_summary.py K9_DATA OUT_PREFIX

K9_DATA: logs/2026-11-18_1036-k9/data, with cc_select.py outputs in b8/<tag>/ (hybrid), cc-r100-R1-k8-s1.csv (D3) and
b6-fa-*.csv (B5/B6: time to confirm versus AI cells). Phase 2 for a hybrid set is read off the B5 curve at rho = 20
(r100, k = 1) by linear interpolation in the number of AI cells: the hybrid changes how many AI cells are needed and
the matching time, not the phase-2 model itself.
"""
import csv, glob, os, sys

import numpy as np

DATA, OUT = sys.argv[1:3]
DEV = {"Pi 5 + Hailo-8L": 1 / 257.6, "Pi 5 CPU": 1 / 12.6}   # s per embedded image (l1_mission.py)


def needed(f):
    """{(umax, rho): (AI cells, T1 model, coverage)} from a cc_select csv (one row per cluster)."""
    out = {}
    for r in csv.DictReader(open(f)):
        key = (float(r["umax"]), float(r["rho"]))
        m, T, cov = out.get(key, (0, 0.0, 1.0))
        out[key] = (m + int(r["m"]), max(T, float(r["T_k"]) + float(r["leave"])), min(cov, float(r["coverage"])))
    return out


runs = [("D3 (all vectors, 528 B)", f"{DATA}/cc-r100-R1-k8-s1.csv")]
for tag, name in [("npu0.8", "hybrid, NPU 0.8"), ("npu0.5", "hybrid, NPU 0.5"), ("npu0.2", "hybrid, NPU 0.2"),
                  ("npu0", "crops only (5 kB)"), ("npu0.5-crop15k", "NPU 0.5, crop 15 kB"),
                  ("npu0.5-vec4k", "NPU 0.5, vector 4.1 kB")]:
    g = glob.glob(f"{DATA}/b8/{tag}/cc-*.csv")
    if g:
        runs.append((name, g[0]))
curve = {}
for n in ("cell-0-1", "sys-2-4"):
    pts = sorted({(int(r["ai_cells"]), float(r["T_mean"])) for r in csv.DictReader(open(f"{DATA}/b6-fa-{n}.csv"))
                  if r["channel"] == "r100" and r["rho"] == "20" and r["k"] == "1"})
    curve[n] = (np.array([p[0] for p in pts]), np.array([p[1] for p in pts]))

L = ["# K9 B8: hybrid option on k8 r100 (model level)\n",
     "AI cells needed and T1 (River surrogate, s) per budget and rho; 'no' when even an AI node in every cell (617) cannot "
     "carry the flow (coverage in brackets). fcam 0.3, hop limit 5. The surrogate is reliable up to about 70 AI cells (B4).\n"]
for u in (0.1, 0.2):
    L.append(f"\n## Budget {u:g}\n\n| option | rho 20 | rho 50 | rho 100 | rho 200 |\n|---|---|---|---|---|")
    for name, f in runs:
        N = needed(f)
        cells = []
        for rho in (20, 50, 100, 200):
            m, T, cov = N[(u, float(rho))]
            cells.append(f"{m}: {T:.0f}" if cov >= 1 else f"no ({cov:.2f})")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
L.append("\n## Phase 2 at rho = 20, budget 0.1 (read off the B5 curve, r100, k = 1)\n\n| option | AI cells | T, alarm 0.1 per "
         "AI cell (s) | T, 2.4 alarms system-wide (s) |\n|---|---|---|---|")
for name, f in runs:
    m, T, cov = needed(f)[(0.1, 20.0)]
    x = curve["cell-0-1"][0]
    if cov < 1 or m > x.max():
        L.append(f"| {name} | {m} | outside the B5 range | outside the B5 range |")
        continue
    L.append(f"| {name} | {m} | " + " | ".join(f"{np.interp(m, *curve[n]):.0f}" for n in ("cell-0-1", "sys-2-4")) + " |")
L.append("\n## Matching with K models per AI node\n\nThe query stays images: an AI node embeds the L query images once per model "
         "it holds. Extra time over one model (s); the V1 visit is 78 s.\n\n| device | K | first pass, L = 3 | V1, L = 20 |"
         "\n|---|---|---|---|")
for d, e in DEV.items():
    for K in (1, 3, 5):
        L.append(f"| {d} | {K} | {(K - 1) * 3 * e:.2f} | {(K - 1) * 20 * e:.2f} |")
open(OUT + ".md", "w").write("\n".join(L) + "\n")
print(open(OUT + ".md").read())
