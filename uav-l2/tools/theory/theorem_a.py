"""ND1 days 3-4: does Theorem A's closed form reproduce how FC + DTSP-N slows down as the channel worsens?

    python3 uav-l2/tools/theory/theorem_a.py C4_CP_DIR CAMPAIGN4_SCORE_DIR CAMPAIGN4_CSV OUT_PREFIX

Prediction, per map and environment, with no fitted number except the channel threshold of day 2:
  groups     critical cells grouped as dn_baseline.groups (radius 300 m), served from an orbit about the group
             centroid, radius the farthest member clipped to [R_LOOP, RHO]
  p_k        mean reception probability of critical cell k's CL over its group's orbit, model p(d) of day 2
  dwell      sum over groups of tau * Q (1 + eps) / min_k p_k   (Theorem A's term, packets heard en route ignored)
  T_FC       measured FC team-1 time in the open channel + dwell(env) - dwell(open)
  T_River    measured CHORD + River team-1 time + mean River readiness (ns-3)
Measured: FC + DTSP-N (scheme DN) and CHORD + River (scheme CP) of campaign 4, means over seeds.
--cell: p_k is the cell's reception (a coded packet counts once any node of the cell hears it), as FC's in-cell gather.
Writes OUT_PREFIX.md and OUT_PREFIX-ratio.png (no text).
"""
import csv, glob, math, os, sys
import numpy as np
from scipy.stats import ncx2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from dn_baseline import groups
from fc_baseline import R_LOOP, RHO

CP, SCORE, CSV, OUT = sys.argv[1:5]
CELL = "--cell" in sys.argv   # cell-level reception (CL gathers from its members) instead of the CL alone
ENVS = {"open": 0.00, "r500": 9.03, "r200": 19.77, "r100": 25.74}
R50 = {"open": 1016, "r500": 498, "r200": 199, "r100": 99}
MAPS = ["k8-s1", "k12-s1", "k16-s1"]
S, PTX, FSPL1, DREF, ALPHA, K, H = -101.04, 10.0, 40.05, 100.0, 3.0, 2.0, 100.0
TAU, Q, EPS, RG = 0.01, 4041, 0.05, 300.0


def p_model(d, L):
    sl = np.hypot(d, H)
    pl = np.where(sl <= DREF, FSPL1 + 20 * np.log10(sl), FSPL1 + 20 * np.log10(DREF) + 10 * ALPHA * np.log10(sl / DREF))
    return ncx2.sf(2 * (K + 1) * 10 ** ((S - (PTX - pl - L)) / 10), 2, 2 * K)


def crit_cls(w):
    """CL position of every critical cell, and the positions of all the cell's nodes (the CL gathers from them)."""
    pts, mem = [], []
    for f in sorted(glob.glob(f"{w}/plan*.txt"), key=lambda s: int(s.split("plan")[-1][:-4])):
        k = f.split("plan")[-1][:-4]
        crit = {(int(a), int(b)) for _, a, b in (l.split()[:3] for l in open(f) if l.startswith("CRIT "))}
        rows = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
        for r in rows:
            cell = (int(r["q"]), int(r["r"]))
            if r["isCL"] == "1" and cell in crit:
                pts.append((float(r["x"]), float(r["y"])))
                mem.append(np.array([(float(x["x"]), float(x["y"])) for x in rows if (int(x["q"]), int(x["r"])) == cell]))
    return np.array(pts), mem


def dwell(pts, L, mem=None):
    th = np.linspace(0, 2 * math.pi, 64, endpoint=False)
    tot = 0.0
    for g in groups(pts, RG):
        c = pts[g].mean(axis=0)
        rho = np.linalg.norm(pts[g] - c, axis=1)
        r = min(max(rho.max(), R_LOOP), RHO)
        orb = c + r * np.c_[np.cos(th), np.sin(th)]
        if mem is None:      # the CL alone
            pk = [p_model(np.linalg.norm(orb - pts[i], axis=1), L).mean() for i in g]
        else:                # the cell: a coded packet counts once any node of the cell hears it
            pk = [(1 - np.prod([1 - p_model(np.linalg.norm(orb - x, axis=1), L) for x in mem[i]], axis=0)).mean() for i in g]
        tot += TAU * Q * (1 + EPS) / max(min(pk), 1e-6)
    return tot


meas = {}
for r in csv.DictReader(open(CSV)):
    if r["team1"] and r["scheme"] in ("DN", "CP"):
        meas.setdefault((r["scheme"], r["map"], r["env"]), []).append(float(r["team1"]))
ready = {}
for f in glob.glob(f"{SCORE}/R*/*/score-ns3.csv"):
    for r in csv.DictReader(open(f)):
        if "/CP/" in r["work"] and r["riverReady"]:
            ready.setdefault((r["map"], r["env"]), {})[(r["seed"])] = float(r["riverReady"])
mean = lambda v: sum(v) / len(v)

rows = []
for m in MAPS:
    cm = {e: crit_cls(f"{CP}/{e}/R1/{m}") for e in ENVS}
    pts = {e: cm[e][0] for e in ENVS}
    dw = {e: dwell(cm[e][0], L, cm[e][1] if CELL else None) for e, L in ENVS.items()}
    base = mean(meas[("DN", m, "open")]) - dw["open"]
    for e in ENVS:
        fc_m, cp_m = mean(meas[("DN", m, e)]), mean(meas[("CP", m, e)])
        rr = mean(list(ready.get((m, e), {}).values())) if ready.get((m, e)) else float("nan")
        fc_p = base + dw[e]
        rows.append(dict(map=m, env=e, R50=R50[e], ncrit=len(pts[e]), dwell=dw[e], fc_meas=fc_m, fc_pred=fc_p,
                         river=cp_m + rr, ratio_meas=fc_m / (cp_m + rr), ratio_pred=fc_p / (cp_m + rr)))

L = ["# Kiểm định lý A (ND1 ngày 3–4)", "",
     "T_FC đo: thời gian đội 1 của FC + DTSP-N (C4, trung bình các seed). T_FC dự đoán: T_FC đo ở open, cộng phần thời gian",
     "lượn thay đổi theo công thức của định lý A (chỉ dùng mô hình kênh ngày 2, không khớp thêm tham số). T_River: thời gian",
     "đội 1 của CHORD + River cộng thời điểm sẵn sàng trung bình (ns-3).", "",
     "| Bản đồ | Kênh | R50 (m) | Số critical cell | Lượn dự đoán (s) | T_FC đo (s) | T_FC dự đoán (s) | Sai lệch | T_River (s) | Tỉ số đo | Tỉ số dự đoán |",
     "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    L.append(f"| {r['map']} | {r['env']} | {r['R50']} | {r['ncrit']} | {r['dwell']:.0f} | {r['fc_meas']:.0f} | {r['fc_pred']:.0f} | "
             f"{(r['fc_pred'] - r['fc_meas']) / r['fc_meas'] * 100:+.0f} % | {r['river']:.0f} | {r['ratio_meas']:.2f} | {r['ratio_pred']:.2f} |")
open(f"{OUT}.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.5, 4.2)); cols = {"k8-s1": "#1f4e9c", "k12-s1": "#e07b1a", "k16-s1": "#2e8b57"}
for m in MAPS:
    rs = [r for r in rows if r["map"] == m]; x = [r["R50"] for r in rs]
    ax.plot(x, [r["ratio_pred"] for r in rs], "-", color=cols[m], lw=2)
    ax.plot(x, [r["ratio_meas"] for r in rs], "o", color=cols[m], ms=7)
ax.axhline(1, color="grey", lw=1, ls=":"); ax.set_xscale("log"); ax.set_xticklabels([]); ax.set_yticklabels([])
ax.minorticks_off(); plt.savefig(f"{OUT}-ratio.png", dpi=160, bbox_inches="tight", facecolor="white")
