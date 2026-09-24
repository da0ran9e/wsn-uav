"""PNG: the two times against cell radius, and what their ratio does.

    python3 tools/make_scaling_figure.py OUT.png CSV [CSV ...]
"""
import csv, os, statistics as st, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, DIM, GRID = "#12151a", "#5b6472", "#dfe3e9"
C_FLY, C_FLOOD, C_REF = "#2f6fd0", "#1f9d6b", "#c2410c"


def main():
    out, csvs = sys.argv[1], sys.argv[2:]
    by = {}
    for fp in csvs:
        for r in csv.DictReader(open(fp)):
            by.setdefault(float(r["Rc"]), []).append(r)
    rc = sorted(by)
    agg = lambda k, f=st.mean: [f([float(r[k]) for r in by[x]]) for x in rc]
    fly, flood = agg("flyS"), agg("floodMeanS")
    flyLo, flyHi = agg("flyS", min), agg("flyS", max)
    flLo, flHi = agg("floodMeanS", min), agg("floodMeanS", max)
    turn, weave = agg("turnS"), agg("weaveS")
    rows, cells = agg("rows"), agg("cells")
    depth, slots, fwd = agg("depthMean"), agg("slotsMean"), agg("fwdMean")

    fig, ax = plt.subplots(1, 3, figsize=(15.2, 4.5), dpi=170)

    # --- 1. the two times, on one log axis so the gap is the message --------
    a = ax[0]
    a.fill_between(rc, flyLo, flyHi, color=C_FLY, alpha=.18, lw=0)
    a.plot(rc, fly, "-o", ms=3.4, color=C_FLY, lw=1.9, label="bay qua mọi CL")
    a.fill_between(rc, flLo, flHi, color=C_FLOOD, alpha=.18, lw=0)
    a.plot(rc, flood, "-o", ms=3.4, color=C_FLOOD, lw=1.9, label="lan 1 gói trong ô")
    a.set_yscale("log")
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_ylabel("giây (log)", fontsize=9.5, color=INK)
    a.set_title("Hai thời gian — thang log\n(vùng mờ = trải 6 hạt giống)",
                fontsize=10.5, color=INK, pad=7)
    a.legend(fontsize=8, frameon=False, loc="center left")
    a.grid(alpha=.25, lw=.6, which="both")

    # --- 2. the ratio: how far the flood is from ever mattering -------------
    a = ax[1]
    ratio = [f / g for f, g in zip(fly, flood)]
    a.plot(rc, ratio, "-o", ms=3.4, color=INK, lw=1.9)
    a.axhline(1.0, color=C_REF, ls="--", lw=1.3)
    a.annotate("lan = bay (chưa bao giờ đạt tới)", (rc[len(rc) // 2], 1.0),
               textcoords="offset points", xytext=(0, 8), ha="center",
               fontsize=8, color=C_REF)
    a.set_yscale("log")
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_ylabel("bay / lan", fontsize=9.5, color=INK)
    a.set_title(f"Tỉ lệ: {ratio[0]:.0f}× → {ratio[-1]:.0f}×\n"
                "lan gói tin KHÔNG BAO GIỜ là nút thắt",
                fontsize=10.5, color=INK, pad=7)
    a.grid(alpha=.25, lw=.6, which="both")

    # --- 3. where each time comes from --------------------------------------
    a = ax[2]
    a.plot(rc, rows, "-o", ms=3.4, color=C_FLY, lw=1.8, label="số hàng (→ bay)")
    a.plot(rc, depth, "-o", ms=3.4, color=C_FLOOD, lw=1.8, label="độ sâu cây (→ lan)")
    a.plot(rc, slots, "-s", ms=3.0, color=C_FLOOD, lw=1.4, ls="--",
           label="khe sau tái dùng không gian")
    a.plot(rc, fwd, "-", color=DIM, lw=1.2, ls=":", label="số nút phải phát")
    a.set_yscale("log")
    a.set_xlabel("$R_c$ (m)", fontsize=9.5, color=INK)
    a.set_title("Nguồn của mỗi thời gian\nsố hàng GIẢM, cây SÂU thêm",
                fontsize=10.5, color=INK, pad=7)
    a.legend(fontsize=7.5, frameon=False)
    a.grid(alpha=.25, lw=.6, which="both")

    for b in ax:
        b.tick_params(labelsize=8.5)
        for s in b.spines.values():
            s.set_color(GRID)
    fig.suptitle("Bán kính ô: thời gian bay qua mọi cụm trưởng vs thời gian lan gói "
                 "trong một ô", fontsize=12.5, color=INK, y=1.01)
    fig.text(0.5, -0.03,
             "Vùng 780×484 m, 1600 nút @20 m, tầm mặt đất 40 m, ρ=63.7 m. "
             "Khe MAC 200 ms là số ĐO ĐƯỢC của dự án; airtime 100 B chỉ 3.2 ms, "
             "nên kích thước gói không quyết định gì — khe MAC quyết định tất cả.",
             ha="center", va="top", fontsize=8.3, color=DIM, wrap=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    print(f"  {out}")


if __name__ == "__main__":
    main()
