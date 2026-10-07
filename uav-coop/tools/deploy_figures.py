"""Figures for steps 1-2: lattice -> region -> nodes -> CH, CLs -> flight path across the cluster.

    python3 tools/deploy_figures.py DIR OUTDIR [--prefix deploy] [--seeds "seed*-lattice.csv"]
                                    [--conv "conv*-lattice.csv"] [--sweep sweep.csv]
                                    [--picks 0,1,2] [--rhos 1,100,400]

DIR holds the output of uav-coop-deploy --out=PREFIX: PREFIX-lattice.csv,
PREFIX-growth.csv, PREFIX-region.csv, PREFIX-nodes-sS.csv. Optional:
  --seeds  regions other seeds give (free growth)       -> deploy-seeds.png
  --conv   one run per convexity, same seed (convK-*)   -> deploy-convexity.png
  --sweep  measured convexity over many seeds, per K     (panel of the same figure)
  --picks  flight paths for several entry/exit draws (pickK-*)  -> deploy-path.png
  --rhos   K,R1,R2: draw K at other turn radii (rhoR-*)          (panels of the same figure)
"""
import argparse, csv, glob, math, os, re, sys

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
    mp = os.path.join(src, f"{prefix}-region.csv")
    meta = next(csv.DictReader(open(mp))) if os.path.exists(mp) else {"convexityAsked": "0"}
    return lat, gro, nodes, w, meta


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
def fig_steps(lat, gro, nodes, w, out, s_show, meta):
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
    a.set_title(f"① Lưới lục giác đều từ gốc (★)\nR = {R:.0f} m · rộng mặt–mặt {w:.0f} m · "
                f"{math.sqrt(3) / 2 * w * w:,.0f} m²/cell", loc="left", fontsize=10, color=INK)
    style(a)

    # 2. the region: grown at random, then concavities filled
    a = ax[1]
    filled = {(int(x["q"]), int(x["r"])) for x in lat if x.get("filled") == "1"}
    hexes(a, allc - sel, w, SURF, "#d8d7d2", lw=.4)
    R_ = w / math.sqrt(3)
    polys = [corners(*axial_centre(q, r, w), R_) for q, r in order]
    pc = PolyCollection(polys, array=np.arange(len(order)), cmap=ORDER, edgecolors=SURF,
                        linewidths=.8, zorder=2)
    a.add_collection(pc)
    if filled:
        hexes(a, filled, w, "#fbe7b5", FRONTIER, lw=.8, z=2)
    a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.2, zorder=3))
    a.plot(0, 0, "*", ms=11, color=FRONTIER, mec=INK, mew=.6, zorder=4)
    cb = fig.colorbar(pc, ax=a, shrink=.55, pad=.01)
    cb.set_label("thứ tự mọc ngẫu nhiên", fontsize=7.5, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=INK2)
    cb.outline.set_visible(False)
    frame(a, sel, w)
    a.set_title(f"② {meta['cellsGrown']} cell mọc ngẫu nhiên (độ lồi {float(meta['rawConvexity']):.2f})"
                f"\n+ lấp {len(filled)} chỗ lõm (vàng) → độ lồi {float(meta['convexityMeasured']):.2f}",
                loc="left", fontsize=10, color=INK)
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


# ------------------------------------------------------------------ figure: capabilities and roles
STRENGTH = LinearSegmentedColormap.from_list("strength", ["#e3eefc", "#86b6ef", "#2a78d6", "#0d366b"])
C_CL, C_CH = "#eda100", "#e34948"


def fig_roles(lat, nodes, w, out, s):
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    nd = nodes[s]
    X = np.array([float(n["x"]) for n in nd]); Y = np.array([float(n["y"]) for n in nd])
    S = np.array([float(n["score"]) for n in nd])
    cl = np.array([n["isCL"] == "1" for n in nd]); ch = np.array([n["isCH"] == "1" for n in nd])
    fig = plt.figure(figsize=(17, 7.6), dpi=170, facecolor=SURF)
    gs = fig.add_gridspec(3, 3, width_ratios=[2.3, 1, 1], hspace=.75, wspace=.32,
                          left=.03, right=.98, top=.86, bottom=.08)
    a = fig.add_subplot(gs[:, 0])
    hexes(a, sel, w, "#f3f2ee", "#ffffff", lw=.8)
    a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.2, zorder=3))
    o = np.argsort(S)
    sc = a.scatter(X[o], Y[o], c=S[o], cmap=STRENGTH, vmin=0, vmax=S.max(), s=14, lw=0, zorder=4)
    a.scatter(X[cl & ~ch], Y[cl & ~ch], s=58, facecolors="none", edgecolors=C_CL, linewidths=1.6, zorder=5)
    a.scatter(X[ch], Y[ch], s=340, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=6)
    c = [n for n in nd if n["isCH"] == "1"][0]
    a.annotate(f"CH #{c['id']}\nquan sát {float(c['obs']):.2f} · tính toán {float(c['cpu']):.2f} · "
               f"giao tiếp {float(c['comm']):.2f}\nđiểm = {float(c['score']):.3f}",
               (float(c["x"]), float(c["y"])), xytext=(18, 18), textcoords="offset points",
               fontsize=8.5, color=INK, bbox=dict(boxstyle="round,pad=.3", fc=SURF, ec=INK2, lw=.6),
               arrowprops=dict(arrowstyle="-", color=INK2, lw=.8), zorder=7)
    cb = fig.colorbar(sc, ax=a, shrink=.45, pad=.07, location="bottom")
    cb.set_label("điểm = quan sát × tính toán × giao tiếp", fontsize=8, color=INK2)
    cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
    a.scatter([], [], s=58, facecolors="none", edgecolors=C_CL, linewidths=1.6, label="CL: mạnh nhất cell")
    a.scatter([], [], s=200, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, label="CH: mạnh nhất vùng")
    a.legend(loc="lower left", fontsize=8.5, frameon=False, labelcolor=INK2)
    frame(a, sel, w, pad=1.0)
    empty = len(sel) - int(cl.sum())
    a.set_title(f"Spacing {s} m: {len(nd)} node · {int(cl.sum())} CL (một mỗi cell có node"
                f"{'' if not empty else f'; {empty} cell trống'}) · 1 CH",
                loc="left", fontsize=10.5, color=INK)
    style(a)
    # the three capabilities
    for k, (col, lab) in enumerate((("obs", "quan sát  ~ U[0, 1)"), ("cpu", "tính toán  ~ U[0, 1)"),
                                    ("comm", "giao tiếp  ~ U(0, 1]  (> 0)"))):
        b = fig.add_subplot(gs[k, 1])
        v = np.array([float(n[col]) for n in nd])
        b.hist(v, bins=20, range=(0, 1), color="#86b6ef", edgecolor=SURF, lw=1)
        b.hist(v[cl], bins=20, range=(0, 1), color=C_CL, edgecolor=SURF, lw=1, alpha=.9)
        b.axvline(float(c[col]), color=C_CH, lw=1.6)
        b.set_title(lab, loc="left", fontsize=9, color=INK)
        b.tick_params(colors=INK2, labelsize=7)
        b.set_facecolor(SURF)
        for sp in b.spines.values():
            sp.set_visible(False)
    # strength: everyone vs CLs vs CH
    b = fig.add_subplot(gs[:2, 2])
    b.hist(S, bins=30, range=(0, 1), color="#86b6ef", edgecolor=SURF, lw=1, label="mọi node")
    b.hist(S[cl], bins=30, range=(0, 1), color=C_CL, edgecolor=SURF, lw=1, label="CL")
    b.axvline(S[ch][0], color=C_CH, lw=1.8, label="CH")
    b.set_xlabel("điểm", fontsize=8, color=INK2)
    b.set_title("Điểm: tích ba thuộc tính\nphần lớn node yếu vì chỉ cần MỘT thuộc tính thấp",
                loc="left", fontsize=9.5, color=INK)
    b.legend(fontsize=8, frameon=False, labelcolor=INK2)
    b.tick_params(colors=INK2, labelsize=7); b.set_facecolor(SURF)
    for sp in b.spines.values():
        sp.set_visible(False)
    b = fig.add_subplot(gs[2, 2])
    b.axis("off")
    top = {col: max(float(n[col]) for n in nd) for col in ("obs", "cpu", "comm")}
    b.text(0, 1, "Không node nào đứng đầu cả ba cùng lúc.\n"
           f"Cao nhất từng thuộc tính:\n  quan sát {top['obs']:.3f}, tính toán {top['cpu']:.3f},\n"
           f"  giao tiếp {top['comm']:.3f}\n"
           f"CH: {float(c['obs']):.3f}, {float(c['cpu']):.3f}, {float(c['comm']):.3f}\n"
           "→ CH = tích lớn nhất,\n   không phải max từng thuộc tính.",
           fontsize=8.5, color=INK, va="top", transform=b.transAxes)
    fig.text(.03, .97, "Thuộc tính và vai trò của node — vạch dọc đỏ = CH, cột cam = phân bố của các CL",
             fontsize=12.5, color=INK, ha="left", va="top")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ------------------------------------------------------------------ figure: the convexity knob
def fig_convexity(files, sweep, out):
    def kap(f):
        return float(re.search(r"conv([\d.]+)-lattice\.csv$", f).group(1))
    files = sorted(files, key=kap)
    n = len(files) + (1 if sweep else 0)
    fig, ax = plt.subplots(1, n, figsize=(3.6 * n, 4.4), dpi=170, facecolor=SURF)
    for a, f in zip(ax, files):
        lat = list(csv.DictReader(open(f)))
        meta = next(csv.DictReader(open(f.replace("-lattice.csv", "-region.csv"))))
        c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
        w = math.hypot(c[(1, 0)][0] - c[(0, 0)][0], c[(1, 0)][1] - c[(0, 0)][1])
        sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
        filled = {(int(x["q"]), int(x["r"])) for x in lat if x["filled"] == "1"}
        holes = {(int(x["q"]), int(x["r"])) for x in lat if x["hole"] == "1"}
        hexes(a, sel - filled, w, REGION, "#ffffff", lw=.4)
        if filled:
            hexes(a, filled, w, "#fbe7b5", FRONTIER, lw=.7, z=2)
        if holes:
            hexes(a, holes, w, HOLE, INK2, lw=.7, z=2)
        a.add_collection(LineCollection(boundary(sel, w), colors=INK, linewidths=1.0, zorder=3))
        a.plot(0, 0, "*", ms=7, color=FRONTIER, mec=INK, mew=.5, zorder=5)
        frame(a, sel, w, pad=.9)
        k = float(meta["convexityAsked"])
        a.set_title(f"κ = {k:g}: +{len(filled)} cell lấp\nđộ lồi {float(meta['convexityMeasured']):.2f}"
                    f" · {meta['cells']} cell", loc="left", fontsize=9.5, color=INK)
        style(a); a.set_xticks([]); a.set_yticks([])
    if sweep:
        a = ax[-1]
        rows = list(csv.DictReader(open(sweep)))
        ks = sorted({float(r["kappa"]) for r in rows})
        add = [[int(r["cells"]) - int(r["cellsGrown"]) for r in rows if float(r["kappa"]) == k] for k in ks]
        a.fill_between(ks, [min(v) for v in add], [max(v) for v in add], color="#fbe7b5", lw=0)
        a.plot(ks, [np.mean(v) for v in add], "-o", color=FRONTIER, ms=5, lw=2)
        raw = [float(r["raw"]) for r in rows if float(r["kappa"]) == ks[-1]]
        a.set_xlabel("κ (độ lồi mục tiêu)", fontsize=8, color=INK2)
        a.set_ylabel("số cell được lấp", fontsize=8, color=INK2)
        a.set_title(f"30 seed: cell lấp thêm theo κ\n(độ lồi gốc {np.mean(raw):.2f} TB, "
                    f"{min(raw):.2f}–{max(raw):.2f})", loc="left", fontsize=9.5, color=INK)
        a.grid(color=GRID, lw=.6); a.set_facecolor(SURF)
        a.tick_params(colors=INK2, labelsize=7.5)
        for sp in a.spines.values():
            sp.set_visible(False)
    fig.suptitle("Tham số độ lồi κ: vùng mọc ngẫu nhiên, rồi lấp chỗ lõm (vàng) — cell bị vùng bao "
                 "nhiều nhất được lấp trước — cho tới khi độ lồi ≥ κ; κ = 1 lồi hoàn toàn",
                 x=.01, ha="left", fontsize=11, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .9))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


# ------------------------------------------------------------------ figure: the flight path
C_TURN, C_STRAIGHT = "#2a78d6", INK
C_GATE = "#eda100"


def path_panel(a, src, prefix, s, lat, nodes_s, w, title):
    pp = os.path.join(src, f"{prefix}-path-s{s}.csv")
    if not os.path.exists(pp):
        return False
    tr = list(csv.DictReader(open(pp)))
    wp = {r["point"]: r for r in csv.DictReader(open(os.path.join(src, f"{prefix}-pathwp-s{s}.csv")))}
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    hexes(a, sel, w, "#f3f2ee", "#ffffff", lw=.5)
    a.add_collection(LineCollection(boundary(sel, w), colors=INK2, linewidths=.9, zorder=2))
    a.scatter([float(n["x"]) for n in nodes_s], [float(n["y"]) for n in nodes_s], s=1.2,
              color="#b9b8b2", lw=0, zorder=2)
    # path, coloured by segment kind: the middle segment of LSL/RSR/LSR/RSL is straight;
    # the leads outside the cluster are dashed
    X = np.array([float(r["x"]) for r in tr]); Y = np.array([float(r["y"]) for r in tr])
    part = np.array([int(r["part"]) for r in tr]); seg = np.array([int(r["seg"]) for r in tr])
    words = {1: wp["entry"]["legWord"], 2: wp["CH"]["legWord"]}
    for i in range(len(tr) - 1):
        if part[i] != part[i + 1]:
            continue
        if seg[i] < 0:
            a.plot(X[i:i + 2], Y[i:i + 2], color=C_STRAIGHT, lw=1.4, ls=(0, (2, 2)), zorder=4)
            continue
        straight = words[part[i]][seg[i]] == "S"
        a.plot(X[i:i + 2], Y[i:i + 2], color=C_STRAIGHT if straight else C_TURN,
               lw=2.0 if straight else 1.6, zorder=4, solid_capstyle="round")
    # direction arrows every ~400 m
    d = np.concatenate(([0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))))
    for t in np.arange(150, d[-1], 400):
        i = int(np.searchsorted(d, t))
        if 0 < i < len(X) - 1 and part[i - 1] == part[i + 1]:
            a.annotate("", (X[i + 1], Y[i + 1]), (X[i - 1], Y[i - 1]),
                       arrowprops=dict(arrowstyle="-|>", color=INK, lw=0, mutation_scale=11), zorder=5)
    for key, lab in (("entry", "vào"), ("exit", "ra")):
        r = wp[key]
        a.scatter([float(r["x"])], [float(r["y"])], s=90, marker="D", color=C_GATE, edgecolors=INK,
                  linewidths=.8, zorder=6)
        a.annotate(lab, (float(r["x"]), float(r["y"])), xytext=(8, 6), textcoords="offset points",
                   fontsize=8, color=INK, zorder=7,
                   bbox=dict(boxstyle="round,pad=.15", fc=SURF, ec="none", alpha=.85))
    c = wp["CH"]
    a.scatter([float(c["x"])], [float(c["y"])], s=260, marker="*", color=C_CH, edgecolors=INK,
              linewidths=.8, zorder=6)
    a.annotate(f"CH #{c['id']}", (float(c["x"]), float(c["y"])), xytext=(9, 6), textcoords="offset points",
               fontsize=7.5, color=INK, zorder=7,
               bbox=dict(boxstyle="round,pad=.15", fc=SURF, ec="none", alpha=.85))
    rho, L = float(c["rho"]), float(c["lengthM"])
    xs = [float(x["cx"]) for x in lat if x["selected"] == "1"] + list(X)
    ys = [float(x["cy"]) for x in lat if x["selected"] == "1"] + list(Y)
    a.set_xlim(min(xs) - .6 * w, max(xs) + .6 * w)
    a.set_ylim(min(ys) - .6 * w, max(ys) + .6 * w)
    a.set_title(f"{title}\nρ = {rho:.0f} m · vào → CH → ra {L:,.0f} m = {L / 50:.0f} s ở 50 m/s\n"
                f"{wp['entry']['legWord']} {float(wp['entry']['legM']):.0f} · {wp['CH']['legWord']} "
                f"{float(wp['CH']['legM']):.0f}", loc="left", fontsize=8.5, color=INK)
    style(a)
    return True


def fig_path(src, lat, nodes, w, out, picks, rhos):
    s = 35 if 35 in nodes else sorted(nodes)[0]
    panels = [(f"pick{k}", f"lần bốc {k}") for k in picks] + \
             [(f"rho{r}", f"lần bốc {rhos[0]}, ρ = {r} m") for r in rhos[1:]]
    panels = [(p, t) for p, t in panels if os.path.exists(os.path.join(src, f"{p}-path-s{s}.csv"))]
    cols = 3
    rows = (len(panels) + cols - 1) // cols
    fig, ax = plt.subplots(rows, cols, figsize=(16.5, 6.1 * rows), dpi=150, facecolor=SURF, squeeze=False)
    for a in ax.flat:
        a.axis("off")
    for a, (pfx, title) in zip(ax.flat, panels):
        a.axis("on")
        path_panel(a, src, pfx, s, lat, nodes[s], w, title)
    h = [plt.Line2D([], [], color=C_TURN, lw=1.6), plt.Line2D([], [], color=C_STRAIGHT, lw=2),
         plt.Line2D([], [], color=C_STRAIGHT, lw=1.4, ls=(0, (2, 2))),
         plt.Line2D([], [], marker="D", color=C_GATE, mec=INK, ls="", ms=8),
         plt.Line2D([], [], marker="*", color=C_CH, mec=INK, ls="", ms=12)]
    fig.legend(h, ["đoạn quay (bán kính ρ)", "đoạn thẳng", "bay thẳng ngoài cụm (dài ρ)",
                   "điểm vào / ra (ngẫu nhiên trên biên)", "CH"],
               loc="upper left", ncol=5, frameon=False, fontsize=9, bbox_to_anchor=(.01, .975),
               labelcolor=INK2)
    fig.suptitle(f"Đường bay Dubins xuyên cụm: vào ở một điểm biên ngẫu nhiên → qua CH → ra ở một điểm "
                 f"biên ngẫu nhiên khác (spacing {s} m) — hướng tại mỗi điểm chọn cho ngắn nhất", x=.01,
                 ha="left", fontsize=12, color=INK, y=1.0)
    fig.tight_layout(rect=(0, 0, 1, .955), h_pad=3.0)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("outdir")
    ap.add_argument("--prefix", default="deploy")
    ap.add_argument("--seeds"); ap.add_argument("--conv"); ap.add_argument("--sweep")
    ap.add_argument("--picks", help="entry/exit draws pickK-path-sS.csv to show, e.g. 0,1,2")
    ap.add_argument("--rhos", help="K,R1,R2: draw K again from rhoR1-/rhoR2-path-sS.csv")
    o = ap.parse_args()
    os.makedirs(o.outdir, exist_ok=True)
    lat, gro, nodes, w, meta = load(o.src, o.prefix)
    global W
    W = w
    show = 35 if 35 in nodes else sorted(nodes)[len(nodes) // 2]
    fig_steps(lat, gro, nodes, w, os.path.join(o.outdir, "deploy-steps.png"), show, meta)
    fig_growth(lat, gro, w, os.path.join(o.outdir, "deploy-growth.png"))
    fig_spacing(lat, nodes, w, os.path.join(o.outdir, "deploy-spacing.png"))
    if "score" in nodes[show][0]:
        fig_roles(lat, nodes, w, os.path.join(o.outdir, "deploy-roles.png"), show)
    if o.picks:
        picks = [int(k) for k in o.picks.split(",")]
        rhos = [int(r) for r in o.rhos.split(",")] if o.rhos else [picks[0]]
        fig_path(o.src, lat, nodes, w, os.path.join(o.outdir, "deploy-path.png"), picks, rhos)
    if o.seeds:
        fs = glob.glob(os.path.join(o.src, o.seeds))
        if fs:
            fig_seeds(fs, os.path.join(o.outdir, "deploy-seeds.png"))
    if o.conv:
        fs = glob.glob(os.path.join(o.src, o.conv))
        if fs:
            fig_convexity(fs, os.path.join(o.src, o.sweep) if o.sweep else None,
                          os.path.join(o.outdir, "deploy-convexity.png"))


if __name__ == "__main__":
    main()
