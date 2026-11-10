"""ND1 day 5 (trial): check Proposition B (takeover deviation threshold) on the existing wind runs, no new simulation.

    python3 uav-l2/tools/theory/prop_b.py WIND OUT_PREFIX

WIND holds s<sigma>/R<seed>/k8-s1 of logs/2026-11-01_0600-takeover (channel r100). For every SPINE cell a and its
segment Seg(a):
  e_a        largest cross-track distance of the real transmit points of Seg(a) to the planned path (c<k>-path-s35)
  activated  some packet of Seg(a) heard by no node of a or of a gateway-adjacent cell (same rule as --takeover)
  P_model    1 - prod_s (1 - prod_{u in a+N(a)} (1 - p(d_us)))  with the day-2 channel model (S = -101.04 dBm, r100)
  h_a        cell hops (BFS over gateway links) from a to the farthest cell holding a missing packet
Writes OUT_PREFIX.md and OUT_PREFIX-activation-vs-e.png (no text).
"""
import csv, collections, math, sys, os
import numpy as np
from scipy.stats import ncx2

W, OUT = sys.argv[1], sys.argv[2]
PTX, FSPL1, DREF, ALPHA, K, H, S, L = 10.0, 40.05, 100.0, 3.0, 2.0, 100.0, -101.04, 25.74
ADJ = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]

def p(d):
    sl = np.hypot(d, H)
    pl = np.where(sl <= DREF, FSPL1 + 20 * np.log10(sl), FSPL1 + 20 * np.log10(DREF) + 10 * ALPHA * np.log10(sl / DREF))
    return ncx2.sf(2 * (K + 1) * 10 ** ((S - (PTX - pl - L)) / 10), 2, 2 * K)

rows, Rs = [], []
for sig, R in [(50, 1), (50, 2), (50, 3), (100, 1), (100, 2), (100, 3), (200, 1)]:
    w = f"{W}/s{sig}/R{R}/k8-s1"
    for k in range(1, 9):
        nodes = list(csv.DictReader(open(f"{w}/c{k}-nodes-s35.csv")))
        xy = np.array([[float(n["x"]), float(n["y"])] for n in nodes])
        cell = [(int(n["q"]), int(n["r"])) for n in nodes]
        mem = collections.defaultdict(list)
        for i, c in enumerate(cell): mem[c].append(i)
        if k == 1 and sig == 50 and R == 1:     # hex radius from cell centres: centre = A (q, r) + b, |A col| = sqrt3 R
            cs = sorted(mem); A = np.c_[np.array(cs), np.ones(len(cs))]
            cen = np.array([xy[mem[c]].mean(0) for c in cs]); M = np.linalg.lstsq(A, cen, rcond=None)[0]
            Rs.append(np.linalg.norm(M[0]) / math.sqrt(3))
        gw = set()
        for r in csv.DictReader(open(f"{w}/c{k}-gateways-s35.csv")):
            A_, B_ = (int(r["qA"]), int(r["rA"])), (int(r["qB"]), int(r["rB"])); gw |= {(A_, B_), (B_, A_)}
        lines = open(f"{w}/plan{k}.txt").read().split("\n"); N = int(lines[0].split()[1])
        seg = {(int(q[1]), int(q[2])): (int(q[3]), int(q[4])) for q in (l.split() for l in lines) if q and q[0] == "AXE"}
        trk = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/pass{k}-track.csv"))])
        plan = np.array([[float(r["x"]), float(r["y"])] for r in csv.DictReader(open(f"{w}/c{k}-path-s35.csv"))])
        raw = np.fromfile(f"{w}/pass{k}-bits-r1.bin", dtype=np.uint8).reshape(len(nodes), -1)
        got = np.unpackbits(raw, axis=1, bitorder="little")[:, :N].astype(bool)
        for a, (f, l) in seg.items():
            s = np.arange(f, l + 1)
            e = np.min(np.hypot(trk[s, None, 0] - plan[None, :, 0], trk[s, None, 1] - plan[None, :, 1]), axis=1).max()
            nb = [a] + [(a[0] + d[0], a[1] + d[1]) for d in ADJ if (a, (a[0] + d[0], a[1] + d[1])) in gw]
            ids = [i for c in nb for i in mem[c]]
            heard = got[ids][:, s].any(0)
            d = np.hypot(xy[ids, None, 0] - trk[None, s, 0], xy[ids, None, 1] - trk[None, s, 1])
            miss = np.prod(1 - p(d), axis=0)
            pm = 1 - np.exp(np.sum(np.log1p(-np.minimum(miss, 1 - 1e-12))))
            dmin = d.min(0).max()                                   # worst packet: distance to the nearest node of a+N(a)
            h = 0
            if not heard.all():                                     # BFS over gateway links, nearest holder per missing packet
                par, order = {a: 0}, [a]
                for c in order:
                    for dd in ADJ:
                        c2 = (c[0] + dd[0], c[1] + dd[1])
                        if c2 in par or c2 not in mem or (c, c2) not in gw: continue
                        par[c2] = par[c] + 1; order.append(c2)
                for t in s[~heard]:
                    b = next((c for c in order if c not in nb and got[mem[c], t].any()), None)
                    if b is not None: h = max(h, par[b])
            rows.append(dict(sig=sig, R=R, k=k, a=a, e=e, dmin=dmin, act=int(not heard.all()), nmiss=int((~heard).sum()), pm=pm, h=h))

Rc = Rs[0]
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
with open(OUT + ".csv", "w") as fo:
    wr = csv.DictWriter(fo, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
E = np.array([r["e"] for r in rows]); ACT = np.array([r["act"] for r in rows]); PM = np.array([r["pm"] for r in rows])
DM = np.array([r["dmin"] for r in rows]); HH = np.array([r["h"] for r in rows])
bins = [0, 25, 50, 75, 100, 150, 200, 300, 800]
out = [f"# Mệnh đề B, thử nghiệm (ND1 ngày 5)", "", f"SPINE cell: {len(rows)}; bán kính cell ước lượng R = {Rc:.1f} m; kênh r100 (R50 ≈ 99 m).", "",
       "| e (m) | số SPINE cell | tỉ lệ kích hoạt đo | tỉ lệ kích hoạt mô hình | hop xa nhất đo |", "|---|---|---|---|---|"]
for lo, hi in zip(bins, bins[1:]):
    m = (E >= lo) & (E < hi)
    if m.any(): out.append(f"| {lo}–{hi} | {m.sum()} | {ACT[m].mean():.2f} | {PM[m].mean():.2f} | {HH[m].max()} |")
for sig in (50, 100, 200):
    m = np.array([r["sig"] == sig for r in rows])
    out.append(f"\nσ = {sig}: kích hoạt đo {ACT[m].sum()} (có cell khác giữ gói {int((HH[m] > 0).sum())}, gói không ai nghe {int((ACT[m] & (HH[m] == 0)).sum())}), "
               f"tổng xác suất mô hình {PM[m].sum():.1f}, e lớn nhất {E[m].max():.0f} m, hop xa nhất {HH[m].max()}")
order = np.argsort(PM); n = len(PM)
out += ["", "Hiệu chỉnh xác suất mô hình (chia 5 nhóm theo P_model):", "", "| P_model trung bình | tỉ lệ đo | n |", "|---|---|---|"]
for g in np.array_split(order, 5): out.append(f"| {PM[g].mean():.3f} | {ACT[g].mean():.3f} | {len(g)} |")
# threshold structure: e_0 = largest e with no activation below it; w from the model: worst-packet distance where P_model < 0.1
e0 = E[ACT == 1].min() if ACT.any() else float("nan")
w = DM[PM < 0.1].max()
out += ["", f"e nhỏ nhất có kích hoạt: {e0:.0f} m. Khoảng cách xa nhất (gói tệ nhất tới node gần nhất của a+N(a)) mà P_model < 0,1: {w:.0f} m.",
        f"Kích hoạt khi khoảng cách gói tệ nhất ≤ {w:.0f} m: {int(ACT[DM <= w].sum())}/{int((DM <= w).sum())}."]
hb = [math.ceil(r["e"] / (math.sqrt(3) * Rc)) + 1 for r in rows]
hold = [i for i, r in enumerate(rows) if r["h"] > 0]
viol = [i for i in hold if rows[i]["h"] > hb[i]]
out += [f"Chặn số hop h(e) = ⌈e/(√3R)⌉ + 1 (w = 0): vi phạm {len(viol)}/{len(hold)} SPINE cell có người giữ; chặt (bằng nhau) "
        f"{sum(rows[i]['h'] == hb[i] for i in hold)}/{len(hold)}; cặp (h đo, chặn): {sorted(collections.Counter((rows[i]['h'], hb[i]) for i in hold).items())}"]
open(OUT + ".md", "w").write("\n".join(out) + "\n"); print("\n".join(out))

import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.scatter(E, PM, s=10, c="#9aa5b1", label=None)
cen = [(lo + hi) / 2 for lo, hi in zip(bins, bins[1:])]
ma = [ACT[(E >= lo) & (E < hi)].mean() if ((E >= lo) & (E < hi)).any() else np.nan for lo, hi in zip(bins, bins[1:])]
mp = [PM[(E >= lo) & (E < hi)].mean() if ((E >= lo) & (E < hi)).any() else np.nan for lo, hi in zip(bins, bins[1:])]
ax.plot(cen, ma, "o-", c="#d1495b"); ax.plot(cen, mp, "s--", c="#2e86ab")
ax.set_ylim(-0.03, 1.03); ax.set_xlim(0, max(E) * 1.05)
ax.tick_params(labelbottom=True, labelleft=True); ax.set_xlabel(""); ax.set_ylabel("")
fig.tight_layout(); fig.savefig(OUT + "-activation-vs-e.png", dpi=150)
