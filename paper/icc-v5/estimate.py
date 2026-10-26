"""Evaluation numbers for draft v5 (CLAUDE.md §8 item 184): measured rows from uav-l2/docs/data/results/baselines.csv,
and the LM-Tour + River-FC row ESTIMATED, not run (item 184: no experiments until the quota is back).

    python3 paper/icc-v5/estimate.py      # writes paper/icc-v5/{numbers.csv, table-tstar.tex, table-complete.tex}

Estimate. Across the four A2G regimes the mean T* of CHORD + River-FC moves almost one to one with the mean time its
critical cells are ready (k8: ready +216 s, T* +225 s from r = 1 km to r = 150 m; k16: +316 s, +352 s). LM-Tour with
the disc radius xi = min(omega, rho, sqrt(r^2 - h^2)) (eq. (5)) takes the path to within direct hearing of each
landmark. Assumed: it cuts River's completion time by G of what it is on CHORD's chord, only for the critical cells
River serves (those that cannot decode on their own: share S below, measured), with team 1's tour unchanged:
    T*_LM = T*_CHORD - G * S * mean River time,     last_LM = last_CHORD - G * max River time
G = 0.5 is optimistic: the model-level runs of item 179 (free mode, xi = R/2) gave no gain (paper/LMTOUR-vi.md).
"""
import csv, os

H = os.path.dirname(os.path.abspath(__file__))
G = 0.5
ENVS = (("open", 1000), ("r500", 500), ("r200", 200), ("r100", 150))
MAPS = ("k8-s1", "k12-s1", "k16-s1")
NAME = {"CHORD": "CHORD + River-FC", "FC": "FC + gather", "DN": "FC + DTSP-N", "B4": "Single pass, no cooperation",
        "B1": "No broadcast (rotary TSP)", "B7": "Oracle"}
# measured on ns-3 (logs/2026-10-26_0900-baselines/river-vs-direct.md): River mean / max completion (s)
RIVER = {("open", "k8-s1"): (8, 35), ("open", "k12-s1"): (8, 50), ("open", "k16-s1"): (10, 69),
         ("r500", "k8-s1"): (54, 159), ("r500", "k12-s1"): (45, 90), ("r500", "k16-s1"): (62, 244),
         ("r200", "k8-s1"): (108, 311), ("r200", "k12-s1"): (78, 136), ("r200", "k16-s1"): (99, 259),
         ("r100", "k8-s1"): (126, 300), ("r100", "k12-s1"): (96, 183), ("r100", "k16-s1"): (115, 225)}
# critical cells that decode all 12 clues on their own along CHORD's flight (chordfc-cells.csv)
SELF = {"open": (45, 66, 92), "r500": (29, 42, 61), "r200": (0, 0, 1), "r100": (0, 0, 0)}
CRIT = (45, 66, 92)
# time from take-off until the last critical cell is complete (s), k16-s1 (chord-fc.csv ready_max)
LAST = {"CHORD": (1052, 1204, 1398, 1395), "FC": (1132, 2784, 6591, 7257), "DN": (1041, 2529, 5523, 6761)}

T = {(r["channel"], r["map"], r["design"]): float(r["Tstar"])
     for r in csv.DictReader(open(f"{H}/../../uav-l2/docs/data/results/baselines.csv"))}
rows = []
for e, rr in ENVS:
    for i, m in enumerate(MAPS):
        for d in NAME:
            rows.append(dict(r=rr, map=m, design=NAME[d], Tstar=round(T[(e, m, d)]), kind="measured"))
        S = 1 - SELF[e][i] / CRIT[i]
        rows.append(dict(r=rr, map=m, design="LM-Tour + River-FC",
                         Tstar=round(T[(e, m, "CHORD")] - G * S * RIVER[(e, m)][0]), kind="estimate"))
with open(f"{H}/numbers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

get = {(x["r"], x["map"], x["design"]): x["Tstar"] for x in rows}
order = ["LM-Tour + River-FC"] + list(NAME.values())
L = [r"\begin{table*}[t]\centering\color{blue}\caption{Mean mission time $T^\star$ (s), 100 paired draws, $K$ = 8 / 12 / 16 clusters."
     r" \textcolor{red}{[EST]: estimated, not run.}}\label{tab:tstar}", r"\setlength{\tabcolsep}{3pt}\footnotesize",
     r"\begin{tabular}{lcccc}\toprule", r"Scheme & $r=1000$ m & 500 & 200 & 150 \\\midrule"]
for d in order:
    cells = [" / ".join(str(get[(rr, m, d)]) for m in MAPS) for _, rr in ENVS]
    tag = r"\textcolor{red}{" if d.startswith("LM") else "{"
    L.append(f"{tag}{d}}} & " + " & ".join(cells) + r" \\")
L += [r"\bottomrule\end{tabular}\end{table*}"]
open(f"{H}/table-tstar.tex", "w").write("\n".join(L) + "\n")

lm_last = [LAST["CHORD"][j] - round(G * RIVER[(e, "k16-s1")][1]) for j, (e, _) in enumerate(ENVS)]
pct = lambda e: round(100 * SELF[e][2] / 92)
C = [r"\begin{table*}[t]\centering\color{blue}\caption{Critical cells complete after the pass (\%) and time from take-off to the"
     r" last completion (s) versus A2G range, $K = 16$ (92 critical cells). \textcolor{red}{[EST]: estimated.}}"
     r"\label{tab:complete}", r"\footnotesize\begin{tabular}{lcccc}\toprule",
     r"Scheme & $r=150$ & 200 & 500 & 1000\,m \\\midrule",
     "No cooperation & " + " & ".join(f"{pct(e)}\\,\\% / --" for e, _ in ENVS[::-1]) + r" \\",
     "FC + gather & " + " & ".join(f"100\\,\\% / {x}" for x in LAST["FC"][::-1]) + r" \\",
     "FC + DTSP-N & " + " & ".join(f"100\\,\\% / {x}" for x in LAST["DN"][::-1]) + r" \\",
     "River-FC (CHORD) & " + " & ".join(f"100\\,\\% / {x}" for x in LAST["CHORD"][::-1]) + r" \\",
     r"\textcolor{red}{River-FC + LM-Tour} & " + " & ".join(f"\\textcolor{{red}}{{100\\,\\% / {x}}}" for x in lm_last[::-1])
     + r" \\", r"\bottomrule\end{tabular}\end{table*}"]
open(f"{H}/table-complete.tex", "w").write("\n".join(C) + "\n")
for d in order:
    print(f"{d:30s}", "  ".join(" / ".join(str(get[(rr, m, d)]) for m in MAPS) for _, rr in ENVS))
print("LM last (k16, r=1000..150):", lm_last)
