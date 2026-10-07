"""Figures for step 1: lattice -> random contiguous region -> random nodes.

    python3 tools/deploy_figures.py DIR OUTDIR [PREFIX] [SEEDS_GLOB]

DIR holds the output of uav-coop-deploy --out=PREFIX (default "deploy"):
PREFIX-lattice.csv, PREFIX-growth.csv, PREFIX-nodes-sS.csv. SEEDS_GLOB (optional,
e.g. "seed*-lattice.csv") adds a figure of the regions other seeds grow.
"""
import csv, glob, math, os, re, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
REGION, FRONTIER, HOLE = "#cde2fb", "#eda100", "#c3c2b7"
ORDER = LinearSegmentedColormap.from_list("order", ["#cde2fb", "#3987e5", "#0d366b"])
SP_RAMP = {20: "#0d366b", 35: "#2a78d6", 50: "#5598e7"}

W = None   # cell width, read from the lattice


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def axial_centre(q, r, w):
    R = w / math.sqrt(3)
    return w * (q + r / 2), 1.5 * R * r


# edge k joins corner k and k+1; the neighbour across it, in axial steps
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def boundary(cells, w):
    """Edges of the union of `cells` (set of (q, r)): those with no selected neighbour."""
    R = w / math.sqrt(3)
    segs = []
    for q, r in cells:
        cx, cy = axial_centre(q, r, w)
        v = corners(cx, cy, R)
        for k, (dq, dr) in enumerate(EDGE_NB):
            if (q + dq, r + dr) not in cells:
                segs.append([v[k], v[(k + 1) % 6]])
    return segs


def frontier(cells):
    f = set()
    for q, r in cells:
        for dq, dr in EDGE_NB:
            n = (q + dq, r + dr)
            if n not in cells:
                f.add(n)
    return f


def load(src, prefix):
    lat = list(csv.DictReader(open(os.path.join(src, f"{prefix}-lattice.csv"))))
    gro = list(csv.DictReader(open(os.path.join(src, f"{prefix}-growth.csv"))))
    nodes = {}
    for f in glob.glob(os.path.join(src, f"{prefix}-nodes-s*.csv")):
        s = int(re.search(r"-s(\d+)\.csv$", f).group(1))
        nodes[s] = list(csv.DictReader(open(f)))
    # width from two neighbouring centres
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    a, b = c[(0, 0)], c[(1, 0)]
    w = math.hypot(b[0] - a[0], b[1] - a[1])
    return lat, gro, nodes, w


def style(ax):
    ax.set_facecolor(SURF)
    ax.set_aspect("equal")
    ax.tick_params(colors=INK2, labelsize=7.5)
    for s in ax.spines.values():
        s.set_visible(False)


def hexes(ax, cells, w, fc, ec, lw=.6, z=1, alpha=1.0):
    R = w / math.sqrt(3)
    polys = [corners(*axial_centre(q, r, w), R) for q, r in cells]
    ax.add_collection(PolyCollection(polys, facecolors=fc, edgecolors=ec, linewidths=lw,
                                     zorder=z, alpha=alpha))


def frame(ax, cells, w, pad=1.6):
    xs = [axial_centre(q, r, w)[0] for q, r in cells]
    ys = [axial_centre(q, r, w)[1] for q, r in cells]
    ax.set_xlim(min(xs) - pad * w, max(xs) + pad * w)
    ax.set_ylim(min(ys) - pad * w, max(ys) + pad * w)


# ------------------------------------------------------------------ figure: the steps
def fig_steps(lat, gro, nodes, w, out, s_show=35):
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    allc = {(int(x["q"]), int(x["r"])) for x in lat}
    order = [(int(x["q"]), int(x["r"])) for x in gro]
    R = w / math.sqrt(3)
    fig, ax = plt.subplots(1, 4, figsize=(19, 5.6), dpi=170, facecolor=SURF,
                           gridspec_kw=dict(width_ratios=[1, 1, 1, .9]))

    # 1. the lattice, with one cell's dimensions
    a = ax[0]
    hexes(a, allc, w, SURF, "#a8a7a2", lw=.5)
    hexes(a, {(0, 0)}, w, REGION, INK, lw=1.2, z=2)
    for q, r in [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]:
        cx, cy = axial_centre(q, r, w)
        a.text(cx, cy - .18 * w, f"({q},{r})", ha="center", va="center", fontsize=6, color=INK2, zorder=3)
    a.plot(0, 0, "*", ms=11, color=INK, zorder=4)
    a.annotate("", (w / 2, -.25 * w), (-w / 2, -.25 * w),
               arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1), zorder=4)
    a.text(0, -.21 * w, f"rộng {w:.0f} m", ha="center", va="bottom", fontsize=7.5, color=INK, zorder=4)
    a.plot([0, 0], [.08 * w, R], color=INK, lw=.9, ls=":", zorder=4)
    a.text(.04 * w, .42 * R, f"R = {R:.1f} m", fontsize=7, color=INK, zorder=4)
    a.set_xlim(-2.6 * w, 2.6 * w)
    a.set_ylim(-2.4 * w, 2.4 * w)
    a.set_title(f"① Lưới lục giác đều từ gốc (★)\nrộng {w:.0f} m mặt–mặt · R = {R:.1f} m · "
                f"{math.sqrt(3) / 2 * w * w:,.0f} m²/cell", loc="left", fontsize=10, color=INK)
    style(a)

    # 2. the region, coloured by the order it grew in
    a = ax[1]
    hexes(a, allc - sel, w, SURF, "#d8d7d2", lw=.4)
    R_ = w / math.sqrt(3)
    polys = [corners(*axial_centre(q, r, w), R_) for q, r in order]
    pc = PolyCollection(polys, array=np.arange(len(order)), cmap=ORDER, edgecolors=SURF,
                        linewidths=.8, zorder=2)
    a.add_collection(pc)
    a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.2, zorder=3))
    a.plot(0, 0, "*", ms=11, color=FRONTIER, mec=INK, mew=.6, zorder=4)
    cb = fig.colorbar(pc, ax=a, shrink=.55, pad=.01)
    cb.set_label("thứ tự được thêm vào vùng", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.outline.set_visible(False)
    frame(a, sel, w)
    a.set_title(f"② Chọn ngẫu nhiên {len(sel)} cell liền kề\nmọc từ cell gốc, mỗi bước thêm một "
                "cell kề", loc="left", fontsize=10, color=INK)
    style(a)

    # 3. the nodes
    a = ax[2]
    hexes(a, sel, w, REGION, "#ffffff", lw=.5, z=1)
    a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.2, zorder=3))
    nd = nodes[s_show]
    a.scatter([float(n["x"]) for n in nd], [float(n["y"]) for n in nd], s=4, color=INK,
              lw=0, zorder=4)
    frame(a, sel, w)
    area = len(sel) * math.sqrt(3) / 2 * w * w
    a.set_title(f"③ Rải node ngẫu nhiên, spacing {s_show} m\n{len(nd)} node = "
                f"{area / 1e6:.3f} km² ÷ {s_show}²", loc="left", fontsize=10, color=INK)
    style(a)

    # 4. check: nearest-neighbour distance against a uniform random field
    a = ax[3]
    a.set_aspect("auto")
    x = np.linspace(0, 1.6, 200)
    a.plot(x, 1 - np.exp(-math.pi * x ** 2), color=INK, lw=1.4, ls="--", zorder=3)
    for s in sorted(nodes):
        d = np.sort([float(n["nnM"]) for n in nodes[s]]) / s
        a.step(d, np.arange(1, len(d) + 1) / len(d), where="post", lw=1.8, color=SP_RAMP.get(s, INK2),
               label=f"spacing {s} m ({len(d)} node)")
    a.text(.82, .42, "nét đứt: lý thuyết cho\ntrường ngẫu nhiên đều\n1 − exp(−π d²/s²)",
           fontsize=7.5, color=INK, ha="left")
    a.set_xlim(0, 1.5)
    a.set_ylim(0, 1.01)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_xlabel("khoảng cách tới node gần nhất ÷ spacing", fontsize=8, color=INK2)
    a.set_ylabel("tỉ lệ node", fontsize=8, color=INK2)
    a.grid(color=GRID, lw=.6)
    a.legend(fontsize=7.5, frameon=False, loc="lower right", labelcolor=INK2)
    a.set_title("④ Kiểm tra: mật độ đúng như đặt\nkhoảng cách láng giềng khớp lý thuyết",
                loc="left", fontsize=10, color=INK)
    a.set_facecolor(SURF)
    for sp in a.spines.values():
        sp.set_visible(False)
    a.tick_params(colors=INK2, labelsize=7.5)

    fig.suptitle("Bước 1 của uav-coop: lưới lục giác → vùng cell liền kề ngẫu nhiên → node ngẫu "
                 "nhiên", x=.01, ha="left", fontsize=13, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ------------------------------------------------------------------ figure: growth step by step
def fig_growth(lat, gro, w, out):
    order = [(int(x["q"]), int(x["r"])) for x in gro]
    n = len(order)
    ks = sorted({1, 2, 5, 10, 20, 35, n} & set(range(1, n + 1)))
    allc = {(int(x["q"]), int(x["r"])) for x in lat}
    fig, ax = plt.subplots(1, len(ks), figsize=(2.9 * len(ks), 3.9), dpi=170, facecolor=SURF)
    for a, k in zip(ax, ks):
        cur = set(order[:k])
        fr = frontier(cur)
        hexes(a, allc - cur - fr, w, SURF, "#e2e1dc", lw=.35)
        hexes(a, fr, w, "#fbe7b5", FRONTIER, lw=.6, z=2)
        hexes(a, cur - {order[k - 1]}, w, "#5598e7", SURF, lw=.6, z=2)
        if k > 1:
            hexes(a, {order[k - 1]}, w, "#0d366b", SURF, lw=.6, z=3)
        else:
            hexes(a, {order[0]}, w, "#0d366b", SURF, lw=.6, z=3)
        a.plot(0, 0, "*", ms=7, color=FRONTIER, mec=INK, mew=.5, zorder=4)
        frame(a, set(order), w, pad=1.8)
        a.set_title(f"sau {k} cell\nbiên chờ chọn: {len(fr)}", loc="left", fontsize=9, color=INK)
        style(a)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle("② nhìn từng bước: vùng mọc từ cell gốc (★) — xanh đậm = cell vừa thêm, vàng = "
                 "các cell kề đang chờ (bước sau chọn đều một trong số đó)", x=.01, ha="left",
                 fontsize=11, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .9))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ------------------------------------------------------------------ figure: spacing
def fig_spacing(lat, nodes, w, out):
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    ss = sorted(nodes)
    fig, ax = plt.subplots(1, len(ss), figsize=(5.4 * len(ss), 5.6), dpi=170, facecolor=SURF)
    for a, s in zip(np.atleast_1d(ax), ss):
        hexes(a, sel, w, REGION, "#ffffff", lw=.5)
        a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.1, zorder=3))
        nd = nodes[s]
        a.scatter([float(n["x"]) for n in nd], [float(n["y"]) for n in nd],
                  s=max(2, 120 / math.sqrt(len(nd))), color=INK, lw=0, zorder=4)
        nn = np.array([float(n["nnM"]) for n in nd])
        a.set_title(f"spacing {s} m → {len(nd)} node · {len(nd) / len(sel):.1f} node/cell\n"
                    f"láng giềng gần nhất: trung vị {np.median(nn):.1f} m, nhỏ nhất "
                    f"{nn.min():.1f} m", loc="left", fontsize=10, color=INK)
        frame(a, sel, w, pad=1.0)
        style(a)
    fig.suptitle("③ cùng một vùng, ba mật độ — vùng giữ nguyên vì node và vùng dùng hai luồng "
                 "ngẫu nhiên riêng", x=.01, ha="left", fontsize=12, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .93))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ------------------------------------------------------------------ figure: other seeds
def fig_seeds(files, out):
    files = sorted(files, key=lambda f: int(re.search(r"seed(\d+)-", f).group(1)))
    fig, ax = plt.subplots(1, len(files), figsize=(3.3 * len(files), 3.9), dpi=170, facecolor=SURF)
    for a, f in zip(np.atleast_1d(ax), files):
        lat = list(csv.DictReader(open(f)))
        c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
        w = math.hypot(c[(1, 0)][0] - c[(0, 0)][0], c[(1, 0)][1] - c[(0, 0)][1]) if (1, 0) in c else W
        sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
        holes = {(int(x["q"]), int(x["r"])) for x in lat if x["hole"] == "1"}
        hexes(a, sel, w, REGION, "#ffffff", lw=.4)
        if holes:
            hexes(a, holes, w, HOLE, INK2, lw=.8, z=2)
        a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.0, zorder=3))
        a.plot(0, 0, "*", ms=7, color=FRONTIER, mec=INK, mew=.5, zorder=4)
        frame(a, sel, w, pad=.9)
        seed = re.search(r"seed(\d+)-", f).group(1)
        a.set_title(f"seed {seed}: {len(holes)} lỗ thủng", loc="left", fontsize=9.5, color=INK)
        style(a)
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle("Hình dạng vùng theo seed (60 cell) — ô xám = lỗ thủng: cell không được chọn "
                 "nằm kẹt giữa vùng", x=.01, ha="left", fontsize=11, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .9))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    prefix = sys.argv[3] if len(sys.argv) > 3 else "deploy"
    seeds = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(outdir, exist_ok=True)
    lat, gro, nodes, w = load(src, prefix)
    global W
    W = w
    show = 35 if 35 in nodes else sorted(nodes)[len(nodes) // 2]
    fig_steps(lat, gro, nodes, w, os.path.join(outdir, "deploy-steps.png"), show)
    fig_growth(lat, gro, w, os.path.join(outdir, "deploy-growth.png"))
    fig_spacing(lat, nodes, w, os.path.join(outdir, "deploy-spacing.png"))
    if seeds:
        fs = glob.glob(os.path.join(src, seeds))
        if fs:
            fig_seeds(fs, os.path.join(outdir, "deploy-seeds.png"))


if __name__ == "__main__":
    main()
