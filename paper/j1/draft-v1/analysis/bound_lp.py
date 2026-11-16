"""Theorem 3 of the J1 draft: fractional-covering lower bound on any non-cooperative delivery scheme.

    python3 bound_lp.py C4_CP_DIR IN_CSV(bound_nc) OUT_PREFIX [--nofly]

Every critical cell k must collect, in expectation, at least b = (1 - delta) Q packets from emissions at positions
x_1..x_n: sum_s P_k(x_s) >= b. For any weights lambda >= 0 with sum_k lambda_k P_k(x) <= 1 at every position x,
n >= b sum_k lambda_k. Lambda* = max sum lambda (a linear programme) is the fractional number of critical cells that
cannot be served at the same time; T >= Tp (1 - delta) Q Lambda*.
The LP is solved on a 50 m grid; lambda is then rescaled by the maximum of sum_k lambda_k P_k(x) on a 20 m grid, so
the reported bound holds on that finer grid.
--nofly: also the bound when the UAV may not fly within 400 m / 700 m of the centre of the largest cluster (k8-s1).
Writes OUT_PREFIX.md / .csv and OUT_PREFIX.pdf (labelled, for the paper).
"""
import csv, sys
import numpy as np
from scipy.optimize import linprog
from common import ENVS, R50, MAPS, TP, Q, p_cell, critical_cells

CP, INCSV, OUT = sys.argv[1:4]
DELTA = 0.1


def covering(cells, L, allowed=None):
    cen = np.array([c[2].mean(axis=0) for c in cells])
    lo, hi = cen.min(axis=0) - 400, cen.max(axis=0) + 400

    def P(step):
        gx, gy = np.arange(lo[0], hi[0] + 1, step), np.arange(lo[1], hi[1] + 1, step)
        g = np.array([(a, b) for a in gx for b in gy])
        if allowed is not None: g = g[allowed(g)]
        return np.column_stack([p_cell(g, c[2], L) for c in cells])       # (positions, cells)
    A = P(50.0)
    keep = A.max(axis=1) > 1e-4
    if (A.max(axis=0) < 1e-4).any():                      # a cell no allowed position can reach: no finite bound
        return float("inf"), 0.0
    res = linprog(-np.ones(len(cells)), A_ub=A[keep], b_ub=np.ones(int(keep.sum())), bounds=(0, None), method="highs")
    lam = res.x
    fine = P(20.0) @ lam
    return float(lam.sum() / max(fine.max(), 1.0)), float(fine.max())


prev = {(r["map"], r["env"]): r for r in csv.DictReader(open(INCSV))}
rows = []
for m in MAPS:
    for e, L in ENVS.items():
        cells = critical_cells(f"{CP}/{e}/R1/{m}")
        lam, mx = covering(cells, L)
        p = prev[(m, e)]
        rows.append(dict(map=m, env=e, R50=R50[e], clusters=MAPS[m], ncrit=len(cells), Lambda=round(lam, 2), fine_max=round(mx, 3),
                         LB_cover=round(TP * (1 - DELTA) * Q * lam), LB_pack=int(p["LB"]), FC=int(p["FC"]),
                         CHORD_fly=int(p["CHORD_fly"]), LM_fly=int(p["LM_fly"]), CHORD_ready=int(p["CHORD_ready"]), LM_ready=int(p["LM_ready"])))
        print(rows[-1], flush=True)
with open(OUT + ".csv", "w") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
out = ["| Map | Env | clusters | critical cells | Lambda* | LB covering (s) | LB packing (s) | FC+DTSP-N measured (s) | CHORD flight (s) | LM-Tour flight (s) |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    out.append(f"| {r['map']} | {r['env']} | {r['clusters']} | {r['ncrit']} | {r['Lambda']} | {r['LB_cover']} | {r['LB_pack']} | {r['FC']} | {r['CHORD_fly']} | {r['LM_fly']} |")

if "--nofly" in sys.argv:
    m = "k8-s1"
    out += ["", "No-fly zone (k8-s1): the UAV may not fly within rho of the centroid of the critical cells of the cluster with most critical cells.", "",
            "| Env | rho (m) | critical cells inside | Lambda* | LB covering (s) |", "|---|---|---|---|---|"]
    for e, L in ENVS.items():
        cells = critical_cells(f"{CP}/{e}/R1/{m}")
        byk = {}
        for c in cells: byk.setdefault(c[0], []).append(c[2].mean(axis=0))
        k = max(byk, key=lambda k: len(byk[k])); z = np.mean(byk[k], axis=0)
        for rho in (0, 400, 700):
            lam, _ = covering(cells, L, (lambda g, z=z, rho=rho: np.linalg.norm(g - z, axis=1) >= rho) if rho else None)
            inside = sum(np.linalg.norm(c[2].mean(axis=0) - z) < rho for c in cells)
            out.append(f"| {e} | {rho} | {inside} | {lam:.2f} | {TP * (1 - DELTA) * Q * lam:.0f} |"); print(out[-1], flush=True)
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out[:14]))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
for ax, m in zip(axs, MAPS):
    rr = [r for r in rows if r["map"] == m]
    x = [r["R50"] for r in rr]
    ax.plot(x, [r["FC"] for r in rr], "s-", c="#b5403a", ms=4, label="FC + DTSP-N (measured)")
    ax.plot(x, [max(r["LB_cover"], r["LB_pack"]) for r in rr], "k--", lw=1.2, label="lower bound, any non-coop. scheme")
    ax.plot(x, [r["CHORD_fly"] for r in rr], "o-", c="#2a6f97", ms=4, label="CHORD + River (flight end)")
    ax.plot(x, [r["LM_fly"] for r in rr], "^-", c="#2a9d8f", ms=4, label="LM-Tour + River (flight end)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(f"{MAPS[m]} clusters, {rr[0]['ncrit']} critical cells", fontsize=8)
    ax.set_xlabel("A2G range $R_{50}$ (m)", fontsize=8); ax.tick_params(labelsize=7); ax.grid(alpha=0.3, which="both", lw=0.4)
axs[0].set_ylabel("time from take-off (s)", fontsize=8)
axs[0].legend(fontsize=5.5, loc="lower left", frameon=False)
fig.tight_layout(); fig.savefig(OUT + ".pdf"); fig.savefig(OUT + ".png", dpi=200)
