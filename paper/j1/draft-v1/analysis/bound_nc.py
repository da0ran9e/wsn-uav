"""Theorem 2 of the J1 draft: lower bound on the completion time of ANY non-cooperative delivery scheme
(every critical cell uses only what its own nodes hear from the UAV), evaluated on the campaign-4 maps.

    python3 bound_nc.py C4_CP_DIR CAMPAIGN4_CSV SCORE_DIR OUT_PREFIX

For a radius D and a set S of critical cells whose centres are pairwise more than 2D apart,
    T >= min{ [ Tp (1-delta) Q sum_{k in S} 1/pbar_k + (MST(S + BS) - 2 D |S|)^+ / vmax ] / (1 + sum_{k in S} p_k(D)/pbar_k),
              Tp (1-delta) Q / max_{k in S} p_k(D) }      (the second term: before it, no cell of S can be served from outside its disc)
with pbar_k = sup_x P_k(x) and p_k(D) = sup_{|x - c_k| >= D} P_k(x) (cell-level reception, any code, any trajectory).
The script maximises the bound over D and over greedy choices of S. Measured: FC + DTSP-N team-1 time (its last
completion), CHORD / LM-Tour flight time and mean critical-cell ready time (ns-3, campaign 4).
Writes OUT_PREFIX.md, OUT_PREFIX.csv and OUT_PREFIX.pdf (labelled, for the paper).
"""
import csv, glob, sys
import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.spatial.distance import cdist
from common import ENVS, R50, MAPS, TP, Q, VMAX, p_cell, critical_cells, base_station

CP, CSV, SCORE, OUT = sys.argv[1:5]
DELTA = 0.1
rng = np.random.default_rng(1)
th = np.linspace(0, 2 * np.pi, 72, endpoint=False)
ring = np.c_[np.cos(th), np.sin(th)]
gx = np.arange(-150, 151, 10.0)
grid = np.array([(a, b) for a in gx for b in gx])


def bound(cells, bs, L):
    cen = np.array([c[2].mean(axis=0) for c in cells])
    spread = max(np.linalg.norm(c[2] - c[2].mean(axis=0), axis=1).max() for c in cells)
    pbar = np.array([p_cell(c[2].mean(axis=0) + grid, c[2], L).max() for c in cells])
    dist = cdist(cen, cen)
    best = (0.0, 0, 0)
    for D in np.arange(max(150.0, np.ceil(spread / 50) * 50), 3001, 50):
        pD = np.array([p_cell(c[2].mean(axis=0) + D * ring, c[2], L).max() for c in cells])
        for trial in range(40):
            order = np.argsort(-1 / pbar) if trial == 0 else rng.permutation(len(cells))
            S = []
            for i in order:
                if all(dist[i, j] > 2 * D for j in S): S.append(i)
            S = np.array(S)
            pts = np.vstack([bs, cen[S]])
            mst = minimum_spanning_tree(cdist(pts, pts)).sum()
            num = TP * (1 - DELTA) * Q * np.sum(1 / pbar[S]) + max(mst - 2 * D * len(S), 0.0) / VMAX
            T = num / (1 + np.sum(pD[S] / pbar[S]))
            T = min(T, TP * (1 - DELTA) * Q / max(pD[S].max(), 1e-12))   # below this time every cell of S must be visited
            if T > best[0]: best = (T, D, len(S))
    return best, pbar


meas = {}
for r in csv.DictReader(open(CSV)):
    if r["team1"] and r["kind"] == "ns3":
        meas.setdefault((r["scheme"], r["map"], r["env"]), []).append(float(r["team1"]))
ready = {}
for f in glob.glob(f"{SCORE}/R*/*/score-ns3.csv"):
    for r in csv.DictReader(open(f)):
        tag = "CP" if "/CP/" in r["work"] else "LMD" if "/LMD/" in r["work"] else None
        if tag and r["riverReady"]:
            ready.setdefault((tag, r["map"], r["env"]), {})[r["seed"]] = float(r["riverReady"])
mean = lambda v: sum(v) / len(v) if v else float("nan")

rows = []
for m in MAPS:
    for e, L in ENVS.items():
        w = f"{CP}/{e}/R1/{m}"
        cells = critical_cells(w)
        (T, D, nS), pbar = bound(cells, base_station(w), L)
        rows.append(dict(map=m, env=e, R50=R50[e], ncrit=len(cells), pbar_min=round(float(pbar.min()), 3), LB=round(T), D=int(D), S=nS,
                         FC=round(mean(meas.get(("DN", m, e), []))), CHORD_fly=round(mean(meas.get(("CP", m, e), []))),
                         LM_fly=round(mean(meas.get(("LMD", m, e), []))),
                         CHORD_ready=round(mean(list(ready.get(("CP", m, e), {}).values()))),
                         LM_ready=round(mean(list(ready.get(("LMD", m, e), {}).values())))))
        print(rows[-1], flush=True)
with open(OUT + ".csv", "w") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
out = ["| Map | Env | R50 (m) | critical cells | min pbar | LB non-coop (s) | D (m) | \\|S\\| | FC+DTSP-N measured (s) | CHORD flight / mean ready (s) | LM-Tour flight / mean ready (s) |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    out.append(f"| {r['map']} | {r['env']} | {r['R50']} | {r['ncrit']} | {r['pbar_min']} | {r['LB']} | {r['D']} | {r['S']} | {r['FC']} | "
               f"{r['CHORD_fly']} / {r['CHORD_ready']} | {r['LM_fly']} / {r['LM_ready']} |")
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax, m in zip(axs, MAPS):
    rr = [r for r in rows if r["map"] == m]
    x = [r["R50"] for r in rr]
    ax.plot(x, [r["FC"] for r in rr], "s-", c="#b5403a", ms=4, label="FC + DTSP-N (measured)")
    ax.plot(x, [r["LB"] for r in rr], "k--", lw=1.2, label="Theorem 2 lower bound")
    ax.plot(x, [r["CHORD_fly"] for r in rr], "o-", c="#2a6f97", ms=4, label="CHORD + River, flight end")
    ax.plot(x, [r["LM_fly"] for r in rr], "^-", c="#2a9d8f", ms=4, label="LM-Tour + River, flight end")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{MAPS[m]} clusters, {rr[0]['ncrit']} critical cells", fontsize=8)
    ax.set_xlabel("A2G range $R_{50}$ (m)", fontsize=8); ax.tick_params(labelsize=7); ax.grid(alpha=0.3, which="both", lw=0.4)
axs[0].set_ylabel("time from take-off (s)", fontsize=8)
axs[2].legend(fontsize=6, loc="upper right", frameon=False)
fig.tight_layout(); fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
