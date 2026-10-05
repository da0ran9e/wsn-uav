"""PNG: one pass as a strip of packets, lost ones in red -- straight from ns-3.

URBAN BRANCH ONLY -- see examples/a2g-run-test.cc.

    python3 tools/a2g_strip_figure.py BITS.csv SUMMARY.csv NODE OUT.png [EXTRACT.csv]

BITS.csv is a2g-run-test --dump output, SUMMARY.csv its --out. The pass shown is
not hand-picked: it is the one whose longest run for NODE is closest to the
median over all passes. The three zoom windows are chosen by rule too:
    1  the first 100 packets on the approach where 40-60 % got through
    2  centred on the start of the longest run
    3  centred on its end
EXTRACT.csv, if given, receives that pass's rows so the figure can be redrawn
without the full dump.
"""
import csv, statistics as st, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
RX, LOST = "#86b6ef", "#e34948"
PERIOD_S, SPEED, HALF = 0.010, 50.0, 2000.0
ZOOM = 100


def bits_of(row):
    return np.array([int(c) for h in row["bitsHex"] for c in f"{int(h, 16):04b}"]
                    [: int(row["packets"])], dtype=np.int8)


def pos_m(seq):
    return -HALF + SPEED * PERIOD_S * seq


def main():
    bits_csv, summ_csv, node, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    extract = sys.argv[5] if len(sys.argv) > 5 else None

    summ = [r for r in csv.DictReader(open(summ_csv)) if r["node"] == node]
    med = st.median(int(r["longest"]) for r in summ)
    pick = min(summ, key=lambda r: (abs(int(r["longest"]) - med), int(r["pass"])))
    p = pick["pass"]
    rows = [r for r in csv.DictReader(open(bits_csv)) if r["pass"] == p]
    if extract:
        with open(extract, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
    b = bits_of(next(r for r in rows if r["node"] == node))
    n = b.size

    # Longest run, recomputed from the bitmap and checked against the summary.
    best, cur, end = 0, 0, -1
    for i, v in enumerate(b):
        cur = cur + 1 if v else 0
        if cur > best:
            best, end = cur, i
    start = end - best + 1
    assert best == int(pick["longest"]) and start == int(pick["runStart"])
    assert int(b.sum()) == int(pick["received"])

    edge = next(s for s in range(0, n - ZOOM)
                if 0.40 <= b[s:s + ZOOM].mean() <= 0.60)
    zooms = [("①", edge, "rìa vùng phủ — UAV đang tiến lại, mất gói dày đặc"),
             ("②", start - ZOOM // 2, f"chuỗi dài nhất BẮT ĐẦU ở gói {start}"),
             ("③", end - ZOOM // 2 + 1, f"chuỗi dài nhất KẾT THÚC ở gói {end}")]

    fig = plt.figure(figsize=(14, 9.4), dpi=200, facecolor=SURF)
    gs = fig.add_gridspec(4, 1, height_ratios=[1.25, 1, 1, 1], hspace=.95,
                          left=.04, right=.985, top=.86, bottom=.06)

    # ---- the whole pass --------------------------------------------------
    a = fig.add_subplot(gs[0])
    a.set_facecolor(SURF)
    img = np.where(b[None, :] == 1, 1.0, 0.0)
    a.imshow(img, aspect="auto", interpolation="none", extent=(0, n, 0, 1),
             cmap=matplotlib.colors.ListedColormap([LOST, RX]), vmin=0, vmax=1)
    a.set_xlim(0, n)
    a.set_ylim(0, 2.3)
    a.set_yticks([])
    for s in a.spines.values():
        s.set_visible(False)
    a.set_xticks(range(0, n + 1, 1000))
    a.tick_params(colors=INK2, labelsize=8)
    a.set_xlabel("số thứ tự gói (1 gói = 10 ms = 0.5 m đường bay)", fontsize=8.5,
                 color=INK2, labelpad=2)
    top = a.secondary_xaxis("top", functions=(pos_m, lambda y: (y + HALF) / (SPEED * PERIOD_S)))
    top.set_xticks(range(-2000, 2001, 500))
    top.tick_params(colors=INK2, labelsize=8)
    top.set_xlabel("vị trí UAV dọc đường bay (m) — 0 = ngay trên node 4", fontsize=8.5,
                   color=INK2, labelpad=4)
    for s in top.spines.values():
        s.set_visible(False)
    # longest run bracket
    a.plot([start, start, end, end], [1.42, 1.56, 1.56, 1.42], color=INK, lw=1.4)
    a.text((start + end) / 2, 1.63, f"chuỗi liên tục dài nhất: {best} gói = "
           f"{best * PERIOD_S:.1f} s = {best * SPEED * PERIOD_S:.0f} m",
           ha="center", va="bottom", fontsize=9, color=INK, fontweight="bold")
    a.axvline((0 + HALF) / (SPEED * PERIOD_S), ymin=0, ymax=1 / 2.3, color=INK, lw=1, ls=":")
    for lab, s0, _ in zooms:
        a.add_patch(Rectangle((s0, -0.06), ZOOM, 1.12, fill=False, ec=INK, lw=1.2,
                              clip_on=False))
        a.text(s0 + ZOOM / 2, 1.08, lab, ha="center", va="bottom", fontsize=10, color=INK)

    # ---- the zooms: one box per packet --------------------------------------
    for k, (lab, s0, title) in enumerate(zooms):
        z = fig.add_subplot(gs[k + 1])
        z.set_facecolor(SURF)
        for i in range(ZOOM):
            s = s0 + i
            z.add_patch(Rectangle((s + .06, 0), .88, 1, fc=RX if b[s] else LOST, ec="none"))
            if not b[s] and k > 0:
                z.text(s + .5, 1.12, str(s), ha="center", va="bottom", fontsize=6.5,
                       color=INK, rotation=90)
        if k > 0:
            mark = start if k == 1 else end
            z.plot([mark + (0 if k == 1 else 1)] * 2, [-0.25, 1.0], color=INK, lw=1.6)
            arrow = "→" if k == 1 else "←"
            z.text(mark + (1.5 if k == 1 else -0.5), -0.32,
                   f"{arrow} {best} gói liên tục",
                   ha="left" if k == 1 else "right", va="top", fontsize=8.5, color=INK,
                   fontweight="bold")
        rate = b[s0:s0 + ZOOM].mean()
        z.set_title(f"{lab}  gói {s0}–{s0 + ZOOM - 1}  ·  UAV ở {pos_m(s0):+.0f} … "
                    f"{pos_m(s0 + ZOOM - 1):+.0f} m  ·  {title}  ·  nhận {rate:.0%}",
                    loc="left", fontsize=9.5, color=INK, pad=14 if k > 0 else 6)
        z.set_xlim(s0, s0 + ZOOM)
        z.set_ylim(-0.6, 1.9)
        z.set_yticks([])
        z.set_xticks(range(s0 - s0 % 10 + (10 if s0 % 10 else 0), s0 + ZOOM + 1, 10))
        z.tick_params(colors=INK2, labelsize=8, length=3)
        for sp in z.spines.values():
            sp.set_visible(False)

    fig.suptitle(f"Node {node}: {n} gói của một lượt bay, mỗi ô một gói — đỏ = lỗi/mất",
                 x=.04, ha="left", y=.975, fontsize=13, color=INK)
    fig.text(.04, .935,
             f"Dữ liệu trực tiếp từ ns-3, lượt {p}/{len(summ)} — chọn theo quy tắc: lượt có "
             f"chuỗi dài nhất gần trung vị nhất ({best} vs trung vị {med:.1f}). "
             "α = 3.0, Rician K = 2, TX +10 dBm, UAV 100 m, 50 m/s. NHÁNH ĐÔ THỊ.",
             ha="left", fontsize=8.5, color=INK2)
    fig.legend(handles=[Rectangle((0, 0), 1, 1, fc=RX), Rectangle((0, 0), 1, 1, fc=LOST)],
               labels=["nhận nguyên vẹn", "lỗi / mất"], loc="upper right",
               bbox_to_anchor=(.985, .985), ncol=2, frameon=False, fontsize=9,
               labelcolor=INK2)
    fig.savefig(out, facecolor=SURF)
    print(f"pass {p}: longest {best} ({start}-{end}), median {med}, edge window {edge}")
    print(f"  {out}")


if __name__ == "__main__":
    main()
