"""ND1 day 2: does the analytic A2G reception model p(d) match the ns-3 pass, and are receptions independent (A1)?

    python3 uav-l2/tools/theory/channel_check.py WORK OUT_PREFIX

WORK holds c1-nodes-s35.csv and, for each environment loss L, env<L>-track.csv / env<L>-bits-r1.bin
(the calibration passes of uav-l2/tools/a2g_env.py). Writes OUT_PREFIX.md (numbers) and OUT_PREFIX-p-of-d.png (no text).

Model (uav-coop coop-params.h): received mean power P(d) = Ptx - PL(slant) - L with PL free space up to 100 m
then exponent 3.0, Rician K = 2 redrawn per packet; a packet is received when the faded power exceeds an effective
threshold S. S is the only fitted number and is shared by the four environments.
"""
import csv, math, sys
import numpy as np
from scipy.stats import ncx2
from scipy.optimize import minimize_scalar

W, OUT = sys.argv[1], sys.argv[2]
LOSSES = {"open": 0.00, "r500": 9.03, "r200": 19.77, "r100": 25.74}
PTX, FSPL1, DREF, ALPHA, K, H, BIN = 10.0, 40.05, 100.0, 3.0, 2.0, 100.0, 10.0
nodes = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{W}/c1-nodes-s35.csv"))])


def load(L):
    uav = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{W}/env{L:.2f}-track.csv"))])
    raw = np.fromfile(f"{W}/env{L:.2f}-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), -1)
    got = np.unpackbits(raw, axis=1, bitorder="little")[:, :len(uav)]          # bit s = (byte >> s%8) & 1
    r = np.hypot(nodes[:, None, 0] - uav[None, :, 0], nodes[:, None, 1] - uav[None, :, 1])
    return r, got


def p_model(d, L, S):
    sl = np.hypot(d, H)
    pl = np.where(sl <= DREF, FSPL1 + 20 * np.log10(sl), FSPL1 + 20 * np.log10(DREF) + 10 * ALPHA * np.log10(sl / DREF))
    x = 10 ** ((S - (PTX - pl - L)) / 10)                                         # threshold over mean power
    return ncx2.sf(2 * (K + 1) * x, 2, 2 * K)


data, curves = {}, {}
for e, L in LOSSES.items():
    r, got = load(L)
    k = (r / BIN).astype(int).ravel()
    n, g = np.bincount(k), np.bincount(k, weights=got.ravel())
    keep = n >= 200
    d = (np.arange(len(n)) * BIN + BIN / 2)[keep]
    data[e] = (d, (g / np.maximum(n, 1))[keep], n[keep])
    curves[e] = (r, got)

def loss(S):
    return sum(np.sum(w * (p - p_model(d, LOSSES[e], S)) ** 2) for e, (d, p, w) in data.items())
S = minimize_scalar(loss, bounds=(-110, -85), method="bounded").x

def r50(d, p):
    i = int(np.argmax(p < 0.5)); return float(np.interp(0.5, [p[i], p[i - 1]], [d[i], d[i - 1]])) if i else float("nan")

lines = [f"# Kiểm mô hình kênh A2G (ND1 ngày 2)", "", f"Ngưỡng hiệu dụng khớp chung cho 4 môi trường: S = {S:.2f} dBm (danh nghĩa −100 dBm).", "",
         "| Môi trường | L (dB) | R50 đo (m) | R50 mô hình (m) | RMSE p(d) | Sai lệch lớn nhất |", "|---|---|---|---|---|---|"]
for e, (d, p, w) in data.items():
    pm = p_model(d, LOSSES[e], S); dd = np.linspace(0, 1500, 3001)
    lines.append(f"| {e} | {LOSSES[e]:.2f} | {r50(d, p):.0f} | {r50(dd, p_model(dd, LOSSES[e], S)):.0f} | "
                 f"{math.sqrt(np.average((p - pm) ** 2, weights=w)):.3f} | {np.max(np.abs(p - pm)):.3f} |")

# A1: independence. Lag-1 in time (same node, packets s and s+1) and in space (nodes < 20 m apart, same packet),
# on (node, packet) pairs whose model probability is in [0.3, 0.7].
lines += ["", "**Giả định A1 (nhận gói độc lập)**, trên các cặp có xác suất mô hình trong [0,3; 0,7]:", "",
          "| Môi trường | p trung bình | P(nhận s+1 \\| nhận s) | P(nhận s+1 \\| mất s) | P(nhận ở node kề \\| nhận) | P(nhận ở node kề \\| mất) |",
          "|---|---|---|---|---|---|"]
dn = np.hypot(nodes[:, None, 0] - nodes[None, :, 0], nodes[:, None, 1] - nodes[None, :, 1])
pairs = [(i, j) for i in range(len(nodes)) for j in range(i + 1, len(nodes)) if dn[i, j] < 20]
for e, L in LOSSES.items():
    r, got = curves[e]; pm = p_model(r, L, S); mid = (pm > 0.3) & (pm < 0.7)
    a, b, m2 = got[:, :-1], got[:, 1:], mid[:, :-1] & mid[:, 1:]
    t11 = b[m2 & (a == 1)].mean(); t01 = b[m2 & (a == 0)].mean()
    I = np.array([p[0] for p in pairs]); J = np.array([p[1] for p in pairs])
    msk = mid[I] & mid[J]; gi, gj = got[I], got[J]
    s11 = gj[msk & (gi == 1)].mean() if pairs else float("nan"); s01 = gj[msk & (gi == 0)].mean() if pairs else float("nan")
    lines.append(f"| {e} | {got[mid].mean():.3f} | {t11:.3f} | {t01:.3f} | {s11:.3f} | {s01:.3f} |")
lines += ["", f"Số cặp node cách nhau dưới 20 m: {len(pairs)}."]
open(f"{OUT}.md", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(7, 4.2)); cols = ["#1f4e9c", "#2e86c1", "#e07b1a", "#c0392b"]
for c, (e, (d, p, w)) in zip(cols, data.items()):
    dd = np.linspace(0, 1500, 600)
    ax.plot(d, p, "o", ms=2.5, color=c, alpha=0.6); ax.plot(dd, p_model(dd, LOSSES[e], S), "-", color=c, lw=2)
ax.set_xlim(0, 1500); ax.set_ylim(0, 1.02); ax.set_xticklabels([]); ax.set_yticklabels([])
plt.savefig(f"{OUT}-p-of-d.png", dpi=160, bbox_inches="tight", facecolor="white")
