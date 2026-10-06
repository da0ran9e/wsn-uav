"""Lawnmower sweep: do later passes make up what a far node missed?

URBAN BRANCH ONLY -- see examples/a2g-sweep-test.cc.

    python3 tools/a2g_sweep_report.py DIR OUTDIR [K]

DIR holds, per lane spacing L, the outputs of a2g-sweep-test --out=sL-rN:
    sL-r*-nodes.csv    every mission, every node
    sL-r1-path.csv     sL-r1-lanes.csv    sL-r1-row.csv   (mission 1)

Two different things can make up a lost packet, and they are kept apart:
    WITHIN a pass   the file is shorter than the reception window, so the same
                    chunk comes round again before the aircraft has gone
    ACROSS passes   another lane (or a turn) delivers what the best one missed
"best" is the single segment that delivered the most distinct chunks;
"union" is the whole mission. union - best is exactly the across-pass part.

Curves use interior rows only (500 <= y <= fieldY - 500): near the lane ends
the turns add passes that a long field would not have. The maps show everything.
"""
import csv, glob, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Rectangle
import numpy as np

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
C_BEST, C_OTHER, C_LOST = "#2a78d6", "#eda100", "#e34948"   # validated: CVD-safe trio
TURN = "#a8a7a2"
K_RAMP = {500: "#86b6ef", 1000: "#3987e5", 2000: "#0d366b"}  # ordinal, validated
SEQ = LinearSegmentedColormap.from_list("blue", ["#f0efec", "#9ec5f4", "#2a78d6", "#0d366b"])
KS = (50, 100, 200, 500, 1000, 2000)


def load(src, L):
    files = sorted(glob.glob(os.path.join(src, f"s{L}-r*-nodes.csv")))
    rows = [r for f in files for r in csv.DictReader(open(f))]
    path = list(csv.DictReader(open(os.path.join(src, f"s{L}-r1-path.csv"))))
    lanes = [float(r["x"]) for r in csv.DictReader(open(os.path.join(src, f"s{L}-r1-lanes.csv")))]
    row = list(csv.DictReader(open(os.path.join(src, f"s{L}-r1-row.csv"))))
    runs = sorted({int(r["run"]) for r in rows})
    return dict(rows=rows, path=path, lanes=lanes, row=row, runs=runs)


def seg_of_seq(path, n):
    """Segment of every packet, rebuilt exactly: the path file lists every boundary."""
    seq = np.array([int(r["seq"]) for r in path])
    seg = np.array([int(r["seg"]) for r in path])
    out = np.empty(n, dtype=np.int32)
    for i in range(len(seq)):
        end = seq[i + 1] if i + 1 < len(seq) else n
        out[seq[i]:end] = seg[i]
    return out


def bits_of(row):
    return np.array([int(c) for h in row["bitsHex"] for c in f"{int(h, 16):04b}"]
                    [: int(row["packets"])], dtype=np.int8)


def style(ax, grid=True):
    ax.set_facecolor(SURF)
    if grid:
        ax.grid(color=GRID, lw=.7)
        ax.set_axisbelow(True)
    ax.tick_params(colors=INK2, labelsize=8)
    for s in ax.spines.values():
        s.set_visible(False)


def interior(rows):
    ymax = max(float(r["y"]) for r in rows)
    return [r for r in rows if 500 <= float(r["y"]) <= ymax - 500]


def table(D, Ls):
    print("Interior rows. 'done' = share of (node, mission) pairs holding the whole file.")
    for L in Ls:
        rows = interior(D[L]["rows"])
        print(f"\n=== lanes {L} m apart, {len(D[L]['runs'])} missions, {len(D[L]['lanes'])} lanes")
        print(f"{'dist to lane':>12} {'n':>6} {'pkts rx':>8} {'lanes heard':>11} | "
              + " | ".join(f"K={K:<4} đủ file best -> union (mảnh thiếu TB)" for K in (500, 1000, 2000)))
        for d in sorted({float(r["dLane"]) for r in rows}):
            g = [r for r in rows if float(r["dLane"]) == d]
            s = f"{d:10.0f} m {len(g):6d} {np.mean([int(r['received']) for r in g]):8.0f} " \
                f"{np.mean([int(r['lanes']) for r in g]):11.2f} | "
            parts = []
            for K in (500, 1000, 2000):
                b = np.mean([int(r[f"best{K}"]) == K for r in g])
                u = np.mean([int(r[f"union{K}"]) == K for r in g])
                mb = np.mean([K - int(r[f"best{K}"]) for r in g])
                mu = np.mean([K - int(r[f"union{K}"]) for r in g])
                parts.append(f"{b:6.1%} -> {u:6.1%} (thiếu {mb:5.1f} -> {mu:4.1f})")
            print(s + " | ".join(parts))


# ---------------------------------------------------------------- figure 1: paths
def fig_paths(D, Ls, out):
    fig, ax = plt.subplots(1, len(Ls), figsize=(5.2 * len(Ls), 5.3), dpi=170, facecolor=SURF)
    for a, L in zip(np.atleast_1d(ax), Ls):
        d = D[L]
        xs = sorted({float(r["x"]) for r in d["rows"] if r["run"] == str(d["runs"][0])})
        ys = sorted({float(r["y"]) for r in d["rows"] if r["run"] == str(d["runs"][0])})
        X, Y = np.meshgrid(xs, ys)
        a.scatter(X.ravel(), Y.ravel(), s=1.2, color="#c3c2b7", zorder=1, lw=0)
        a.add_patch(Rectangle((0, 0), xs[-1], ys[-1], fill=False, ec=INK2, lw=1, ls="--", zorder=2))
        px = np.array([float(r["x"]) for r in d["path"]])
        py = np.array([float(r["y"]) for r in d["path"]])
        sg = np.array([int(r["seg"]) for r in d["path"]])
        for g in np.unique(sg):
            m = sg == g
            lane = g % 2 == 0
            a.plot(px[m], py[m], color=C_BEST if lane else TURN, lw=2.2 if lane else 1.6,
                   ls="-" if lane else (0, (4, 2)), zorder=3, solid_capstyle="round")
            if lane:
                i = g // 2
                mid = np.where(m)[0][len(np.where(m)[0]) // 2]
                dy = py[np.where(m)[0][-1]] - py[np.where(m)[0][0]]
                a.annotate("", (px[mid], py[mid] + np.sign(dy) * 120), (px[mid], py[mid]),
                           arrowprops=dict(arrowstyle="-|>", color=C_BEST, lw=1.6), zorder=4)
                a.text(px[mid] + 60, py[mid], f"luống {i + 1}", rotation=90, va="center",
                       fontsize=8, color=INK)
        a.plot(px[0], py[0], "o", ms=9, color=INK, mec=SURF, mew=2, zorder=5)
        a.plot(px[-1], py[-1], "s", ms=9, color=INK, mec=SURF, mew=2, zorder=5)
        a.annotate("bắt đầu", (px[0], py[0]), xytext=(8, -12), textcoords="offset points",
                   fontsize=8, color=INK)
        a.annotate("kết thúc", (px[-1], py[-1]), xytext=(8, 6), textcoords="offset points",
                   fontsize=8, color=INK)
        n = int(d["path"][-1]["seq"]) + 1
        a.set_title(f"Luống cách {L} m — {len(d['lanes'])} luống\n"
                    f"{n} gói = {n * .01:.0f} s bay, phát cả khi rẽ",
                    fontsize=10.5, color=INK, loc="left")
        a.set_aspect("equal")
        a.set_xlim(-150, xs[-1] + 450)
        a.set_ylim(-450, ys[-1] + 450)
        a.set_xlabel("x (m)", fontsize=8.5, color=INK2)
        a.set_ylabel("y (m)", fontsize=8.5, color=INK2)
        style(a)
    fig.suptitle("Đường bay quét luống: UAV 100 m, 50 m/s, quay đầu bán kính 255 m "
                 "(cánh bằng, nghiêng 45°) ngoài vùng", x=.01, ha="left", fontsize=12.5,
                 color=INK, y=.99)
    fig.text(.01, .935, "Chấm xám: node mặt đất, cách 100 m (1271 node, vùng 4 × 3 km, viền "
             "nét đứt). Xanh: luống, mũi tên chỉ chiều bay. Xám nét đứt: đoạn quay đầu. "
             "NHÁNH ĐÔ THỊ.", fontsize=8.5, color=INK2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .925))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure 2: maps
def fig_maps(D, Ls, K, out):
    fig, ax = plt.subplots(2, len(Ls), figsize=(5.0 * len(Ls), 8.4), dpi=170, facecolor=SURF,
                           squeeze=False)
    for c, L in enumerate(Ls):
        d = D[L]
        xs = sorted({float(r["x"]) for r in d["rows"]})
        ys = sorted({float(r["y"]) for r in d["rows"]})
        xi = {x: i for i, x in enumerate(xs)}
        yi = {y: i for i, y in enumerate(ys)}
        for r_, key, title in ((0, "best", "chỉ lượt tốt nhất"), (1, "union", "cả chuyến bay")):
            M = np.zeros((len(ys), len(xs)))
            N = np.zeros_like(M)
            for r in d["rows"]:
                i, j = yi[float(r["y"])], xi[float(r["x"])]
                M[i, j] += int(r[f"{key}{K}"]) == K
                N[i, j] += 1
            a = ax[r_, c]
            im = a.imshow(M / N, origin="lower", cmap=SEQ, vmin=0, vmax=1, aspect="equal",
                          extent=(xs[0] - 50, xs[-1] + 50, ys[0] - 50, ys[-1] + 50),
                          interpolation="nearest")
            for lx in d["lanes"]:
                a.axvline(lx, color=SURF, lw=1.2, ls=(0, (3, 2)))
            full = (M / N).mean()
            a.set_title(f"L = {L} m · {title}\nđủ file ở {full:.0%} (node × chuyến)",
                        fontsize=10, color=INK, loc="left")
            a.set_xticks([0, 1000, 2000, 3000, 4000])
            a.set_yticks([0, 1000, 2000, 3000])
            style(a, grid=False)
    cb = fig.colorbar(im, ax=ax, shrink=.6, pad=.02)
    cb.set_label(f"xác suất có đủ file K = {K} gói", fontsize=9, color=INK2)
    cb.ax.tick_params(labelsize=8, colors=INK2)
    cb.outline.set_visible(False)
    fig.suptitle(f"Bản đồ: node nào có đủ file {K} gói — một lượt vs cả chuyến bay",
                 x=.01, ha="left", fontsize=12.5, color=INK, y=.995)
    fig.text(.01, .955, "Vạch trắng đứt: vị trí luống. Hàng trên: chỉ tính lượt (luống hoặc "
             "đoạn rẽ) cho nhiều mảnh nhất; hàng dưới: gộp mọi lượt. Khác biệt giữa hai hàng "
             "= phần các lượt khác bù được.", fontsize=8.5, color=INK2, ha="left")
    fig.subplots_adjust(left=.04, right=.86, top=.88, bottom=.04, hspace=.32, wspace=.12)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure 3: curves
def fig_curves(D, Ls, out):
    fig, ax = plt.subplots(1, len(Ls), figsize=(5.0 * len(Ls), 4.6), dpi=170,
                           facecolor=SURF, sharey=True)
    for a, L in zip(np.atleast_1d(ax), Ls):
        rows = interior(D[L]["rows"])
        ds = sorted({float(r["dLane"]) for r in rows})
        for K in (500, 1000, 2000):
            b = [np.mean([int(r[f"best{K}"]) == K for r in rows if float(r["dLane"]) == d]) for d in ds]
            u = [np.mean([int(r[f"union{K}"]) == K for r in rows if float(r["dLane"]) == d]) for d in ds]
            a.fill_between(ds, b, u, color=K_RAMP[K], alpha=.18, lw=0)
            a.plot(ds, u, "-o", ms=5, lw=2, color=K_RAMP[K], mec=SURF, mew=1.2)
            a.plot(ds, b, "--", lw=1.4, color=K_RAMP[K])
            a.annotate(f"K = {K}", (ds[-1], u[-1]), xytext=(6, 0), textcoords="offset points",
                       va="center", fontsize=8, color=INK2)
        a.set_title(f"Luống cách {L} m", fontsize=10.5, color=INK, loc="left")
        a.set_xlabel("khoảng cách tới luống gần nhất (m)", fontsize=8.5, color=INK2)
        a.set_xlim(-20, max(ds) * 1.25)
        a.set_ylim(-.03, 1.03)
        a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
        style(a)
    np.atleast_1d(ax)[0].set_ylabel("tỉ lệ có đủ file", fontsize=9, color=INK2)
    h = [plt.Line2D([], [], color=INK2, lw=2, marker="o", ms=5),
         plt.Line2D([], [], color=INK2, lw=1.4, ls="--"),
         Rectangle((0, 0), 1, 1, fc=INK2, alpha=.18)]
    fig.legend(h, ["gộp mọi lượt", "chỉ lượt tốt nhất", "phần các lượt khác bù"],
               loc="upper right", ncol=3, frameon=False, fontsize=8.5, bbox_to_anchor=(.99, 1.0),
               labelcolor=INK2)
    fig.suptitle("Đủ file theo khoảng cách tới luống — vùng tô = phần bù từ lượt khác",
                 x=.01, ha="left", fontsize=12, color=INK, y=1.0)
    fig.text(.01, .92, "Chỉ các hàng node bên trong (500 ≤ y ≤ 2500 m) để loại hiệu ứng "
             "đoạn rẽ ở đầu luống. K = số gói của file, phát xoay vòng.", fontsize=8.5,
             color=INK2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, .9))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ---------------------------------------------------------------- figure 4: one node
def fig_node(D, L, out, Ks=(1000, 2000)):
    d = D[L]
    rows = d["row"]
    n = int(rows[0]["packets"])
    seg = seg_of_seq(d["path"], n)
    segs = np.unique(seg)
    # Chosen by rule: the row's node on a lane and the one farthest from any lane,
    # each the closest such to the middle of the row.
    far = max(rows, key=lambda r: (float(r["dLane"]), -abs(float(r["x"]) - 2000)))
    near = min(rows, key=lambda r: (float(r["dLane"]), abs(float(r["x"]) - 2000)))
    picks = [("trên luống", near), ("xa luống nhất", far)]

    fig = plt.figure(figsize=(14, 10.4), dpi=200, facecolor=SURF)
    gs = fig.add_gridspec(4, 2, height_ratios=[.42, 1.45, .42, 1.45], hspace=.62,
                          wspace=.30, left=.05, right=.985, top=.88, bottom=.03)
    for k, (label, r) in enumerate(picks):
        b = bits_of(r)
        a = fig.add_subplot(gs[2 * k, :])
        heard = [g for g in segs if b[seg == g].any()]
        a.imshow(np.where(b == 0, 0, 1)[None, :], aspect="auto", interpolation="none",
                 extent=(0, n, 0, 1), cmap=ListedColormap(["#f0d6d6", INK2]), vmin=0, vmax=1)
        for g in segs:
            idx = np.where(seg == g)[0]
            a.axvline(idx[0], color=INK2, lw=.6)
            a.text((idx[0] + idx[-1]) / 2, 1.08, f"luống {g // 2 + 1}" if g % 2 == 0 else "rẽ",
                   ha="center", va="bottom", fontsize=7.5 if g % 2 == 0 else 6.5,
                   color=INK if g % 2 == 0 else INK2)
        a.set_xlim(0, n)
        a.set_ylim(0, 1.6)
        a.set_yticks([])
        a.set_xlabel("số thứ tự gói trong cả chuyến bay (1 gói = 10 ms) — xám = nhận, hồng = mất",
                     fontsize=8, color=INK2, labelpad=1)
        style(a, grid=False)
        a.set_title(f"Node ({float(r['x']):.0f}, {float(r['y']):.0f}) m — {label}, cách luống "
                    f"gần nhất {float(r['dLane']):.0f} m · nhận {int(b.sum())} gói từ "
                    f"{len(heard)} lượt", loc="left", fontsize=10.5, color=INK, pad=16)
        for col, K in enumerate(Ks):
            cov = {g: len(set(np.where((b == 1) & (seg == g))[0] % K)) for g in segs}
            best = max(cov, key=cov.get)
            got_best = set(np.where((b == 1) & (seg == best))[0] % K)
            got_any = set(np.where(b == 1)[0] % K)
            z = fig.add_subplot(gs[2 * k + 1, col])
            cols = 50
            nb = no = nl = 0
            for ch in range(K):
                i, j = divmod(ch, cols)
                if ch in got_best:
                    c, nb = C_BEST, nb + 1
                elif ch in got_any:
                    c, no = C_OTHER, no + 1
                else:
                    c, nl = C_LOST, nl + 1
                z.add_patch(Rectangle((j + .08, -i - .92), .84, .84, fc=c, ec="none"))
            z.set_xlim(0, cols)
            z.set_ylim(-int(np.ceil(K / cols)), 0)
            z.set_aspect("equal")
            z.set_anchor("W")
            z.axis("off")
            bname = f"luống {best // 2 + 1}" if best % 2 == 0 else "một đoạn rẽ"
            verdict = "ĐỦ FILE" if nl == 0 else f"THIẾU {nl} mảnh"
            z.set_title(f"file {K} gói — {verdict}\n"
                        f"xanh {nb}: lượt tốt nhất ({bname}) · vàng {no}: lượt khác bù · "
                        f"đỏ {nl}: không bao giờ nhận", loc="left", fontsize=8.5,
                        color=INK, pad=4)
    fig.suptitle(f"Luống cách {L} m: một node trên luống, một node xa luống nhất — "
                 "file phát xoay vòng, mỗi ô một mảnh", x=.05, ha="left", fontsize=12.5,
                 color=INK, y=.99)
    fig.text(.05, .95, "Xanh = mảnh lượt tốt nhất đã mang; vàng = mảnh lượt tốt nhất bỏ sót "
             "nhưng một lượt khác bù lại; đỏ = cả chuyến bay không mang tới. Dữ liệu trực tiếp "
             "từ ns-3, chuyến bay 1, hàng node y = 1500 m. NHÁNH ĐÔ THỊ.",
             fontsize=8.5, color=INK2, ha="left")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    Ls = sorted(int(os.path.basename(f).split("-")[0][1:])
                for f in glob.glob(os.path.join(src, "s*-r1-path.csv")))
    D = {L: load(src, L) for L in Ls}
    table(D, Ls)
    os.makedirs(outdir, exist_ok=True)
    fig_paths(D, Ls, os.path.join(outdir, "a2g-sweep-path.png"))
    fig_maps(D, Ls, K, os.path.join(outdir, f"a2g-sweep-map-K{K}.png"))
    fig_curves(D, Ls, os.path.join(outdir, "a2g-sweep-curves.png"))
    for L in Ls:
        fig_node(D, L, os.path.join(outdir, f"a2g-sweep-node-L{L}.png"))


if __name__ == "__main__":
    main()
