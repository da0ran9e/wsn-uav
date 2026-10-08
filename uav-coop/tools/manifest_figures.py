"""Figures for the base manifest phase (uav-coop-manifest).

    python3 tools/manifest_figures.py docs/data docs/figures

Reads deploy-lattice.csv, manifest-cells.csv, manifest-trace.csv (mission 1) and the
blank-cell scenarios manifest-blank{A,B}-{cells,trace}.csv, and draws
  manifest-map.png       who sent what to whom: roles, manifests, data, copies
  manifest-timeline.png  when, cell by cell; and the latency over 120 missions
  manifest-holdings.png  where the data sits afterwards (manifest-holdings.csv, mission 1)
"""
import argparse, csv, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

INK, INK2, SURF, GRIDC = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
ROLE = {0: ("cell biên chủ động", "#f6d38a"), 1: ("cell biên chờ", "#f3bdd3"),
        2: ("cell khác chờ", "#a8dcc6"), 3: ("cell khác", "#f1f0eb")}
C_MAN, C_REV, C_DATA, C_LACK, C_CH = "#0b0b0b", "#e34948", "#2a78d6", "#e34948", "#e34948"
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def load_lattice(data):
    lat = list(csv.DictReader(open(os.path.join(data, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    return c, w, sel


def ch_cell(data):
    for r in csv.DictReader(open(os.path.join(data, "deploy-nodes-s35.csv"))):
        if r["isCH"] == "1":
            return int(r["q"]), int(r["r"]), float(r["x"]), float(r["y"])


def arrow(a, p0, p1, color, lw, ls="-", off=0.0, label=None, fs=7.5, z=5, at=.5):
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * off, dx / L * off   # sideways, so both directions show
    s0 = (x0 + nx + dx * .08, y0 + ny + dy * .08)
    s1 = (x1 + nx - dx * .08, y1 + ny - dy * .08)
    a.annotate("", s1, s0, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, mutation_scale=12,
                                           shrinkA=0, shrinkB=0), zorder=z)
    if label:
        a.text(s0[0] + at * (s1[0] - s0[0]) + nx * 1.6, s0[1] + at * (s1[1] - s0[1]) + ny * 1.6, label, fontsize=fs, color=color,
               ha="center", va="center", zorder=z + 1, clip_on=True,
               bbox=dict(boxstyle="round,pad=.12", fc=SURF, ec="none", alpha=.9))


def map_panel(a, data, cells_csv, trace_csv, run, title, zoom=None, labels=True, origins=None):
    c, w, sel = load_lattice(data)
    R = w / math.sqrt(3)
    cells = {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(os.path.join(data, cells_csv)))
             if r["run"] == run}
    tr = list(csv.DictReader(open(os.path.join(data, trace_csv))))
    if origins:   # only what these cells started
        tr = [e for e in tr if (int(e["oq"]), int(e["or"])) in origins]
    polys, cols = [], []
    for h in sel:
        polys.append(corners(*c[h], R))
        cols.append(ROLE[int(cells[h]["role"])][1])
    a.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="#ffffff", linewidths=.8, zorder=1))
    segs = []
    for q, r in sel:
        v = corners(*c[(q, r)], R)
        for k, (dq, dr) in enumerate(EDGE_NB):
            if (q + dq, r + dr) not in sel:
                segs.append([v[k], v[(k + 1) % 6]])
    a.add_collection(LineCollection(segs, colors=INK2, linewidths=1.0, zorder=2))
    # cells that lacked: red outline and "lacks -> lacks after"
    for h, r in cells.items():
        if int(r["lacks0"]) == 0:
            continue
        a.add_collection(PolyCollection([corners(*c[h], R * .93)], facecolors="none", edgecolors=C_LACK,
                                        linewidths=1.8, zorder=3))
        if not labels:
            continue
        full = float(r["fullS"])
        a.text(c[h][0], c[h][1] + .5 * R, f"thiếu {r['lacks0']}→{r['lacksEnd']}" +
               (f"\nđủ {full:.2f} s" if full > 0 else ""), fontsize=7.5, color=INK, ha="center", va="center",
               zorder=7, clip_on=True, bbox=dict(boxstyle="round,pad=.12", fc=SURF, ec="none", alpha=.85))
    # data flows, summed per directed cell pair
    flows = {}
    for e in tr:
        if e["what"] == "data":
            k = ((int(e["fq"]), int(e["fr"])), (int(e["tq"]), int(e["tr"])))
            flows[k] = flows.get(k, 0) + int(e["chunks"])
    for (f, t), n in flows.items():
        # the data runs against the manifest: the same signed offset puts it on the other side
        arrow(a, c[f], c[t], C_DATA, 2.6, off=-.22 * R, label=f"{n} mảnh" if labels else None, at=.55, fs=8)
    for e in tr:
        f, t = (int(e["fq"]), int(e["fr"])), (int(e["tq"]), int(e["tr"]))
        if e["what"] == "manifest":
            arrow(a, c[f], c[t], C_MAN, 1.5, ls=(0, (3, 2)), off=-.22 * R,
                  label=f"manifest\nthiếu {e['chunks']}" if labels else None, at=.45)
        elif e["what"] == "reverse":
            # a reverse manifest runs with the data that answers its border cell's manifest: keep it apart
            arrow(a, c[f], c[t], C_REV, 1.7, ls=(0, (3, 2)), off=.45 * R,
                  label=f"ngược\nthiếu {e['chunks']}" if labels else None, at=.45)
        elif e["what"] == "copy" and labels:
            a.text(c[f][0], c[f][1] - .62 * R, f"giữ {e['chunks']} bản sao", fontsize=7.5, color=C_DATA, ha="center",
                   zorder=7, clip_on=True, bbox=dict(boxstyle="round,pad=.12", fc=SURF, ec="none", alpha=.85))
    q, r, x, y = ch_cell(data)
    a.scatter([x], [y], s=220, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=8)
    a.annotate("CH", (x, y), xytext=(8, 5), textcoords="offset points", fontsize=8, color=INK, zorder=8,
               annotation_clip=True)
    if zoom:
        xs = [c[h][0] for h in zoom]; ys = [c[h][1] for h in zoom]
        a.set_xlim(min(xs) - .8 * w, max(xs) + .8 * w); a.set_ylim(min(ys) - .8 * w, max(ys) + .8 * w)
    else:
        xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
        a.set_xlim(min(xs) - w, max(xs) + w); a.set_ylim(min(ys) - w, max(ys) + w)
    a.set_aspect("equal")
    a.set_title(title, loc="left", fontsize=10, color=INK)
    a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=7.5)
    for s in a.spines.values():
        s.set_visible(False)


def fig_map(data, out):
    fig = plt.figure(figsize=(19, 13), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1.15, 1.15], hspace=.12, wspace=.06, left=.02, right=.99,
                          top=.9, bottom=.03)
    map_panel(fig.add_subplot(gs[:, 0]), data, "manifest-cells.csv", "manifest-trace.csv", "1",
              "(a) Lượt bay 1: vai trò của các cell,\n6 cell biên thiếu (viền đỏ) và manifest của chúng", labels=False)
    map_panel(fig.add_subplot(gs[0, 1:]), data, "manifest-cells.csv", "manifest-trace.csv", "1",
              "(b) Lượt bay 1, phóng to mũi phía bắc: mỗi cell biên thiếu gửi manifest sang cell kế tiếp, "
              "được trả ngay;\n(−5,8) cũng thiếu 1 mảnh nên manifest đi tiếp, (−5,8) giữ bản sao; (−4,8) chờ "
              "rồi gửi manifest ngược", zoom=[(-7, 8), (-5, 9), (-4, 8), (-2, 7), (-4, 7), (-6, 7), (-1, 6)])
    map_panel(fig.add_subplot(gs[1, 1]), data, "manifest-blankA-cells.csv", "manifest-blankA-trace.csv", "1",
              "(c) Kịch bản: cell biên (3,−5) và cell chờ (2,−4)\nkhông nhận được gói nào",
              zoom=[(3, -5), (2, -4), (2, -3)], origins={(3, -5), (2, -4)})
    map_panel(fig.add_subplot(gs[1, 2]), data, "manifest-blankB-cells.csv", "manifest-blankB-trace.csv", "1",
              "(d) Kịch bản: cell biên (−5,9) và cell biên chờ (−5,8)\nkhông nhận được gói nào",
              zoom=[(-5, 9), (-5, 8), (-4, 7)], origins={(-5, 9), (-5, 8)})
    h = [Patch(fc=col, ec="none", label=lab) for lab, col in ROLE.values()]
    h += [Patch(fc="none", ec=C_LACK, lw=1.8, label="cell thiếu lúc đầu"),
          Line2D([], [], color=C_MAN, lw=1.5, ls=(0, (3, 2)), label="manifest (số mảnh còn thiếu khi gửi)"),
          Line2D([], [], color=C_REV, lw=1.7, ls=(0, (3, 2)), label="manifest ngược"),
          Line2D([], [], color=C_DATA, lw=2.6, label="dữ liệu gửi trả"),
          Line2D([], [], marker="*", color=C_CH, mec=INK, ls="", ms=12, label="CH")]
    fig.legend(handles=h, loc="upper left", ncol=5, frameon=False, fontsize=9.5, bbox_to_anchor=(.02, .965),
               labelcolor=INK2)
    fig.suptitle("Pha manifest cơ sở (bản thử mức logic): manifest mô tả cái cell có; cell đi qua gửi trả "
                 "cái mình có, sửa manifest theo bản thân rồi chuyển tiếp; dữ liệu về được giữ ở cell thiếu",
                 x=.02, ha="left", fontsize=12.5, color=INK)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def timeline(a, data, cells_csv, trace_csv, title):
    cells = {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(os.path.join(data, cells_csv)))
             if r["run"] == "1"}
    tr = list(csv.DictReader(open(os.path.join(data, trace_csv))))
    involved = []
    for e in tr:
        for k in (("fq", "fr"), ("tq", "tr")):
            h = (int(e[k[0]]), int(e[k[1]]))
            if h not in involved:
                involved.append(h)
    ys = {h: i for i, h in enumerate(involved)}
    for h, y in ys.items():
        r = cells[h]
        ready, full = float(r["readyS"]), float(r["fullS"])
        a.plot([0, ready], [y, y], color=GRIDC, lw=6, solid_capstyle="butt", zorder=1)
        if int(r["lacks0"]) > 0 and full > 0:
            a.plot([ready, full], [y, y], color="#f6c3c3", lw=6, solid_capstyle="butt", zorder=1)
            a.scatter([full], [y], s=40, marker="|", color=C_LACK, lw=2, zorder=4)
        a.scatter([ready], [y], s=30, color=INK2, zorder=3)
    for e in tr:
        f, t = (int(e["fq"]), int(e["fr"])), (int(e["tq"]), int(e["tr"]))
        t0, t1 = float(e["sentS"]), float(e["atS"])
        col = {"manifest": C_MAN, "reverse": C_REV, "data": C_DATA}.get(e["what"])
        if col:
            a.annotate("", (t1, ys[t]), (t0, ys[f]), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3,
                       ls=(0, (3, 2)) if e["what"] != "data" else "-", mutation_scale=9), zorder=5)
    a.set_yticks(range(len(involved)))
    a.set_yticklabels([f"{h}  thiếu {cells[h]['lacks0']}" for h in involved], fontsize=8, color=INK)
    a.invert_yaxis()
    a.set_xlabel("thời gian sau khi UAV đi qua, s (thang log)", fontsize=9, color=INK2)
    a.set_xscale("symlog", linthresh=1)
    a.set_xlim(left=0)
    a.set_title(title, loc="left", fontsize=10, color=INK)
    a.grid(axis="x", color=GRIDC, lw=.6)
    a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=8)
    for s in a.spines.values():
        s.set_visible(False)


def fig_timeline(data, out):
    fig = plt.figure(figsize=(18, 9.5), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.3, 1], hspace=.35, wspace=.28, left=.09, right=.98, top=.88, bottom=.08)
    timeline(fig.add_subplot(gs[0, 0]), data, "manifest-cells.csv", "manifest-trace.csv",
             "(a) Lượt bay 1: chấm xám = CL xong tóm tắt; đỏ nhạt = đang thiếu; vạch đỏ = đủ")
    timeline(fig.add_subplot(gs[1, 0]), data, "manifest-blankA-cells.csv", "manifest-blankA-trace.csv",
             "(b) Kịch bản (3,−5) + (2,−4) trắng: chờ 2 s → manifest ngược → manifest → 2 000 mảnh")
    a = fig.add_subplot(gs[:, 1])
    cells = list(csv.DictReader(open(os.path.join(data, "manifest-cells.csv"))))
    for roles, lab, col in (("0", "cell biên chủ động", "#eda100"), ("12", "cell chờ (biên hoặc không)", "#1baf7a")):
        v = np.sort([float(r["fullS"]) - float(r["readyS"]) for r in cells
                     if r["role"] in roles and int(r["lacks0"]) > 0 and float(r["fullS"]) >= 0])
        early = (v <= 0).mean()   # done before its own summary: a passing manifest brought it
        a.plot(np.maximum(v, .01), np.arange(1, len(v) + 1) / len(v), color=col, lw=2.2,
               label=f"{lab} (n = {len(v)})" + (f"; {early:.0%} đủ trước cả khi\nchính nó sẵn sàng, nhờ "
                                                 f"manifest đi qua" if early >= .005 else ""))
        a.axvline(np.median(v), color=col, lw=.9, ls=(0, (3, 3)))
    a.set_xscale("log")
    a.set_xlim(left=.008)
    a.set_xlabel("từ lúc cell sẵn sàng tới khi đủ, s (≤ 0 vẽ ở 0,01)", fontsize=9, color=INK2)
    a.set_ylabel("tỉ lệ cell thiếu", fontsize=9, color=INK2)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.legend(frameon=False, fontsize=9, labelcolor=INK2, loc="upper left")
    a.set_title("(c) 120 lượt bay: mọi cell thiếu đều đủ\n(nét đứt: trung vị; cận dưới lạc quan, 10 ms mỗi frame-hop)",
                loc="left", fontsize=10, color=INK)
    a.grid(color=GRIDC, lw=.6)
    a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=8)
    for s in a.spines.values():
        s.set_visible(False)
    h = [Line2D([], [], color=C_MAN, lw=1.3, ls=(0, (3, 2)), label="manifest"),
         Line2D([], [], color=C_REV, lw=1.3, ls=(0, (3, 2)), label="manifest ngược"),
         Line2D([], [], color=C_DATA, lw=1.3, label="dữ liệu")]
    fig.legend(handles=h, loc="upper left", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(.09, .95),
               labelcolor=INK2)
    fig.suptitle("Pha manifest cơ sở theo thời gian", x=.01, ha="left", fontsize=12, color=INK)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def fig_holdings(data, out):
    """Where the data sits after the base manifest phase (mission 1)."""
    c, w, sel = load_lattice(data)
    R = w / math.sqrt(3)
    rows = list(csv.reader(open(os.path.join(data, "manifest-holdings.csv"))))[1:]
    pos = {r["id"]: r for r in csv.DictReader(open(os.path.join(data, "deploy-nodes-s35.csv")))}
    dpath = {r["id"]: float(r["dPathM"]) for r in csv.DictReader(open(os.path.join(data, "pass-nodes.csv")))}
    nodes = [r for r in rows if r[0] == "node"]
    cb = {(int(r[1]), int(r[2])): r for r in rows if r[0] == "cellBefore"}
    ca = {(int(r[1]), int(r[2])): r for r in rows if r[0] == "cellAfter"}
    K = 2000
    fig = plt.figure(figsize=(19, 12.5), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.25], hspace=.25, wspace=.12, left=.03, right=.98, top=.9,
                          bottom=.06)
    ramp = matplotlib.colors.LinearSegmentedColormap.from_list("h", ["#f1f0eb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

    def cells_bg(a, colors=None):
        polys, cols = [], []
        for h in sel:
            polys.append(corners(*c[h], R))
            cols.append(colors[h] if colors else "#f3f2ee")
        a.add_collection(PolyCollection(polys, facecolors=cols, edgecolors="#ffffff", linewidths=.7, zorder=1))
        xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
        a.set_xlim(min(xs) - w, max(xs) + w); a.set_ylim(min(ys) - w, max(ys) + w)
        a.set_aspect("equal"); a.set_facecolor(SURF)
        a.tick_params(colors=INK2, labelsize=7.5)
        for sp in a.spines.values():
            sp.set_visible(False)

    # (a) chunks per node after the phase
    a = fig.add_subplot(gs[0, 0])
    cells_bg(a)
    x = [float(pos[r[1]]["x"]) for r in nodes]; y = [float(pos[r[1]]["y"]) for r in nodes]
    v = [int(r[7]) for r in nodes]
    sc = a.scatter(x, y, c=v, cmap=ramp, vmin=0, vmax=K, s=6, lw=0, zorder=3)
    cl = [r for r in nodes if r[4] == "1"]
    a.scatter([float(pos[r[1]]["x"]) for r in cl], [float(pos[r[1]]["y"]) for r in cl], s=22, facecolors="none",
              edgecolors="#eda100", lw=1.1, zorder=4)
    gain = [r for r in nodes if int(r[7]) > int(r[6])]
    a.scatter([float(pos[r[1]]["x"]) for r in gain], [float(pos[r[1]]["y"]) for r in gain], s=90, marker="o",
              facecolors="none", edgecolors=C_LACK, lw=1.8, zorder=5)
    cb_ = fig.colorbar(sc, ax=a, shrink=.6, pad=.01)
    cb_.ax.tick_params(labelsize=7.5, colors=INK2); cb_.outline.set_visible(False)
    cb_.set_label("mảnh node đang giữ (/2000)", fontsize=8.5, color=INK2)
    a.set_title(f"(a) Mỗi node giữ bao nhiêu mảnh sau pha manifest\nvòng cam = CL; vòng đỏ = {len(gain)} node "
                f"nhận thêm qua manifest", loc="left", fontsize=10, color=INK)

    # (b) cells: copies of each chunk, at least / at most one
    a = fig.add_subplot(gs[0, 1])
    one = {h: int(ca[h][5]) for h in sel}
    m1 = max(one.values()) or 1
    col = {h: ("#f1f0eb" if one[h] == 0 else matplotlib.colors.to_hex(plt.cm.Reds(.25 + .65 * one[h] / m1))) for h in sel}
    cells_bg(a, col)
    for h in sel:
        if int(cb[h][4]) > 0:
            a.add_collection(PolyCollection([corners(*c[h], R * .9)], facecolors="none", edgecolors=INK, lw=1.4, zorder=3))
        if one[h]:
            a.text(c[h][0], c[h][1], str(one[h]), fontsize=7, ha="center", va="center", color=INK, zorder=4)
    a.set_title("(b) Số mảnh chỉ còn ĐÚNG MỘT bản trong cell (đỏ: càng nhiều càng mong manh)\n"
                "viền đen = cell thiếu trước manifest (giờ đều đủ ở mức cell)", loc="left", fontsize=10, color=INK)

    # (c) per node: before vs after, by distance from the path
    a = fig.add_subplot(gs[0, 2])
    d = np.array([dpath[r[1]] for r in nodes])
    b = np.array([int(r[6]) for r in nodes]); af = np.array([int(r[7]) for r in nodes])
    kind = np.array([2 if r[4] == "1" else 1 if r[5] == "1" else 0 for r in nodes])
    for k, lab, colr, sz in ((0, "node thường", "#b9b8b2", 4), (1, "node mạnh", "#2a78d6", 7), (2, "CL", "#eda100", 16)):
        m = kind == k
        a.scatter(d[m], af[m], s=sz, color=colr, lw=0, alpha=.8, label=lab, zorder=2 + k)
    for r in gain:
        a.annotate("", (dpath[r[1]], int(r[7])), (dpath[r[1]], int(r[6])),
                   arrowprops=dict(arrowstyle="-|>", color=C_LACK, lw=1.4, mutation_scale=9), zorder=6)
    a.axhline(K, color=INK2, lw=.8, ls=(0, (3, 3)))
    a.set_xlabel("khoảng cách từ node tới đường bay, m", fontsize=9, color=INK2)
    a.set_ylabel("mảnh node đang giữ", fontsize=9, color=INK2)
    a.legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="lower left")
    a.set_title("(c) Theo khoảng cách tới đường bay; mũi tên đỏ = phần nhận thêm qua manifest",
                loc="left", fontsize=10, color=INK)
    a.grid(color=GRIDC, lw=.6); a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=8)
    for sp in a.spines.values():
        sp.set_visible(False)

    # (d) per cell: cell union vs CL vs nodes, cells sorted by distance from the path
    a = fig.add_subplot(gs[1, :])
    cd = {}
    for r in nodes:
        cd.setdefault((int(r[2]), int(r[3])), []).append(r)
    order = sorted(cd, key=lambda h: np.mean([dpath[r[1]] for r in cd[h]]))
    xs = np.arange(len(order))
    union_b = [K - int(cb[h][4]) for h in order]
    clv = [int(next(r for r in cd[h] if r[4] == "1")[7]) for h in order]
    strong = [np.mean([int(r[7]) for r in cd[h] if r[5] == "1"] or [np.nan]) for h in order]
    mean_all = [np.mean([int(r[7]) for r in cd[h]]) for h in order]
    mx = [max(int(r[7]) for r in cd[h]) for h in order]
    mn = [min(int(r[7]) for r in cd[h]) for h in order]
    a.fill_between(xs, mn, mx, color="#d9e8fb", lw=0, label="node trong cell: thấp nhất – cao nhất", step="mid")
    a.plot(xs, mean_all, color="#3987e5", lw=1.6, label="trung bình mọi node", drawstyle="steps-mid")
    a.plot(xs, strong, color="#1c5cab", lw=1.2, ls=(0, (3, 2)), label="trung bình node mạnh", drawstyle="steps-mid")
    a.scatter(xs, clv, s=18, color="#eda100", edgecolors=INK, lw=.4, zorder=4, label="CL")
    a.plot(xs, [K] * len(xs), color="#1baf7a", lw=2, label="cả cell (hợp mọi node) sau manifest = 2000 ở mọi cell")
    lack = [i for i, u in enumerate(union_b) if u < K]
    a.scatter([xs[i] for i in lack], [union_b[i] for i in lack], marker="v", s=50, color=C_LACK, zorder=5,
              label="cả cell TRƯỚC manifest (chỉ các cell thiếu)")
    a.set_xlim(-1, len(xs))
    a.set_ylim(0, K * 1.06)
    a.set_xticks(xs[::6])
    a.set_xticklabels([f"{np.mean([dpath[r[1]] for r in cd[order[i]]]):.0f}" for i in xs[::6]], fontsize=7.5)
    a.set_xlabel("109 cell, xếp theo khoảng cách trung bình tới đường bay (m)", fontsize=9, color=INK2)
    a.set_ylabel("mảnh (/2000)", fontsize=9, color=INK2)
    a.legend(frameon=False, fontsize=8.5, labelcolor=INK2, loc="lower left", ncol=3)
    a.set_title("(d) Từng cell: CẢ CELL có đủ, nhưng từng node (kể cả CL) vẫn chỉ giữ phần mình nhận từ UAV",
                loc="left", fontsize=10, color=INK)
    a.grid(color=GRIDC, lw=.6); a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=8)
    for sp in a.spines.values():
        sp.set_visible(False)
    fig.suptitle("Phân bổ dữ liệu sau pha manifest cơ sở (lượt bay 1, K = 2000): pha manifest lấp chỗ thiếu "
                 "của CELL, không làm từng node đủ", x=.01, ha="left", fontsize=12.5, color=INK)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("figs")
    o = ap.parse_args()
    os.makedirs(o.figs, exist_ok=True)
    fig_map(o.data, os.path.join(o.figs, "manifest-map.png"))
    fig_timeline(o.data, os.path.join(o.figs, "manifest-timeline.png"))
    fig_holdings(o.data, os.path.join(o.figs, "manifest-holdings.png"))


if __name__ == "__main__":
    main()
