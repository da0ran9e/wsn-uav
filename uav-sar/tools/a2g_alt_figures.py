"""PNGs: the longest-run experiment repeated over flight altitude.

URBAN BRANCH ONLY -- see examples/a2g-run-test.cc.

    python3 tools/a2g_alt_figures.py DIR OUT_SUMMARY.png OUT_STRIPS.png [EXTRACT.csv]

DIR holds, for every altitude H:
    h{H}.csv  bits-h{H}.csv   --alt=H               (free space up to H: the spec)
    f{H}.csv                  --alt=H --dref=100    (free space up to 100 m: comparison)

The strips figure shows node 4 at each altitude, one pass per altitude, chosen by
the same rule as a2g_strip_figure.py: the pass whose longest run is closest to
the median. EXTRACT.csv, if given, receives those passes' rows.
"""
import csv, os, re, statistics as st, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from a2g_strip_figure import bits_of, pos_m, INK, INK2, SURF, RX, LOST, PERIOD_S, SPEED

GRID = "#e6e5e1"
LATERAL = ((0, (4,)), (300, (3, 5)), (600, (2, 6)), (900, (1, 7)))
SHADE = {0: "#0d366b", 300: "#1c5cab", 600: "#3987e5", 900: "#86b6ef"}   # near = dark
LEGAL_M = 120


def altitudes(src):
    return sorted(int(m.group(1)) for f in os.listdir(src)
                  if (m := re.fullmatch(r"h(\d+)\.csv", f)))


def agg(path):
    rows = list(csv.DictReader(open(path)))
    out = {}
    for lat, nodes in LATERAL:
        r = [x for x in rows if int(x["node"]) in nodes]
        out[lat] = (np.mean([int(x["longest"]) for x in r]),
                    np.mean([int(x["received"]) for x in r]))
    return out


def style(ax):
    ax.set_facecolor(SURF)
    ax.grid(color=GRID, lw=.7, which="both")
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8.5)
    for s in ax.spines.values():
        s.set_visible(False)


def summary(src, H, out):
    data = {m: {h: agg(os.path.join(src, f"{m}{h}.csv")) for h in H} for m in ("h", "f")}
    fig, ax = plt.subplots(2, 2, figsize=(13, 8.6), dpi=170, facecolor=SURF,
                           sharex=True, sharey="row")
    heads = {"h": "Neo tại độ cao bay: tự do tới d = H  (theo đặc tả)",
             "f": "Neo cố định: tự do tới d = 100 m  (đối chiếu)"}
    for c, m in enumerate(("h", "f")):
        for r, (idx, ylab) in enumerate(((0, "chuỗi liên tục dài nhất (gói, log)"),
                                         (1, "số gói nhận được / lượt"))):
            a = ax[r, c]
            for lat, _ in LATERAL:
                y = [data[m][h][lat][idx] for h in H]
                a.plot(H, y, "-o", lw=2, ms=7, color=SHADE[lat], mec=SURF, mew=1.8)
                if True:
                    a.annotate(f"lệch {lat} m", (H[-1], y[-1]), xytext=(8, 0),
                               textcoords="offset points", va="center", fontsize=8.5,
                               color=INK2)
            a.axvline(LEGAL_M, color=INK2, lw=1, ls=":")
            if r == 0:
                a.set_yscale("log")
                a.set_title(heads[m], fontsize=10.5, color=INK, loc="left")
            if c == 0:
                a.set_ylabel(ylab, fontsize=9, color=INK2)
            if r == 1:
                a.set_xlabel("độ cao bay H (m)", fontsize=9, color=INK2)
            style(a)
        ax[1, c].annotate(f"{LEGAL_M} m: trần độ cao phổ biến của UAV", (LEGAL_M, 0),
                          xycoords=("data", "axes fraction"), xytext=(4, 4),
                          textcoords="offset points", va="bottom", fontsize=7.5, color=INK2)
    # the node-4 peak under the spec's anchoring
    y4 = [data["h"][h][0][0] for h in H]
    k = int(np.argmax(y4))
    ax[0, 0].annotate(f"node 4 đạt đỉnh {y4[k]:.0f} gói ở {H[k]} m", (H[k], y4[k]),
                      xytext=(0, -12), textcoords="offset points", ha="center", va="top",
                      fontsize=8.5, color=INK, fontweight="bold")
    ax[1, 1].set_xlim(H[0] - 10, H[-1] * 1.22)
    fig.suptitle("Đổi độ cao bay: kết luận phụ thuộc vào chỗ neo suy hao, không phải vào "
                 "mô phỏng", x=.01, ha="left", fontsize=12.5, color=INK, y=.995)
    fig.text(.01, .955, "Mỗi điểm 200 lượt bay, α = 3.0, Rician K = 2, TX +10 dBm, 50 m/s. "
             "Lệch ngang = khoảng cách từ node tới đường bay; node 4 ở 0 m. NHÁNH ĐÔ THỊ.",
             fontsize=8.5, color=INK2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .945))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def strips(src, H, out, extract):
    fig, ax = plt.subplots(len(H), 1, figsize=(14, 1.15 * len(H) + 1.6), dpi=200,
                           facecolor=SURF, sharex=True)
    picked = []
    for a, h in zip(ax, H):
        summ = [r for r in csv.DictReader(open(os.path.join(src, f"h{h}.csv")))
                if r["node"] == "4"]
        med = st.median(int(r["longest"]) for r in summ)
        pick = min(summ, key=lambda r: (abs(int(r["longest"]) - med), int(r["pass"])))
        rows = [r for r in csv.DictReader(open(os.path.join(src, f"bits-h{h}.csv")))
                if r["pass"] == pick["pass"]]
        for r in rows:
            picked.append({"altM": h, **r})
        b = bits_of(next(r for r in rows if r["node"] == "4"))
        n = b.size
        best, cur, end = 0, 0, -1
        for i, v in enumerate(b):
            cur = cur + 1 if v else 0
            if cur > best:
                best, end = cur, i
        start = end - best + 1
        assert best == int(pick["longest"]) and start == int(pick["runStart"])
        assert int(b.sum()) == int(pick["received"])

        x0, x1 = pos_m(0) - SPEED * PERIOD_S / 2, pos_m(n - 1) + SPEED * PERIOD_S / 2
        a.imshow(np.where(b[None, :] == 1, 1.0, 0.0), aspect="auto", interpolation="none",
                 extent=(x0, x1, 0, 1), vmin=0, vmax=1,
                 cmap=matplotlib.colors.ListedColormap([LOST, RX]))
        ps, pe = pos_m(start), pos_m(end)
        a.plot([ps, ps, pe, pe], [1.1, 1.3, 1.3, 1.1], color=INK, lw=1.3)
        a.text(pe + 25, 1.2, f"{best} gói = {best * PERIOD_S:.1f} s", va="center",
               fontsize=8.5, color=INK, fontweight="bold")
        a.text(x0 - 40, .5, f"H = {h} m", ha="right", va="center", fontsize=10, color=INK)
        a.text(x1 + 40, .5, f"nhận {int(b.sum())}\nlượt {pick['pass']}", ha="left",
               va="center", fontsize=7.5, color=INK2)
        a.axvline(0, ymin=0, ymax=1 / 1.5, color=INK, lw=.9, ls=":")
        a.set_ylim(0, 1.5)
        a.set_yticks([])
        a.set_facecolor(SURF)
        for s in a.spines.values():
            s.set_visible(False)
        a.tick_params(colors=INK2, labelsize=8)
    ax[-1].set_xlim(-2000, 2000)
    ax[-1].set_xlabel("vị trí UAV dọc đường bay (m) — 0 = ngay trên node 4 (vạch chấm)",
                      fontsize=9, color=INK2)
    fig.suptitle("Node 4 ở mỗi độ cao: một lượt bay, mỗi điểm ảnh một gói — đỏ = lỗi/mất",
                 x=.06, ha="left", fontsize=12.5, color=INK, y=.995)
    fig.text(.06, .955, "Dữ liệu trực tiếp từ ns-3. Mỗi độ cao: lượt có chuỗi dài nhất gần "
             "trung vị nhất trong 200 lượt. Neo tự do tới d = H (theo đặc tả). α = 3.0, "
             "Rician K = 2. NHÁNH ĐÔ THỊ.", fontsize=8.5, color=INK2, ha="left")
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=RX), plt.Rectangle((0, 0), 1, 1, fc=LOST)],
               labels=["nhận nguyên vẹn", "lỗi / mất"], loc="upper right",
               bbox_to_anchor=(.985, .998), ncol=2, frameon=False, fontsize=9,
               labelcolor=INK2)
    fig.subplots_adjust(left=.075, right=.925, top=.89, bottom=.075, hspace=.55)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")
    if extract:
        with open(extract, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=picked[0].keys())
            w.writeheader()
            w.writerows(picked)


def main():
    src, out_sum, out_strip = sys.argv[1], sys.argv[2], sys.argv[3]
    extract = sys.argv[4] if len(sys.argv) > 4 else None
    H = altitudes(src)
    summary(src, H, out_sum)
    strips(src, H, out_strip, extract)


if __name__ == "__main__":
    main()
