"""Figures for the pre-built routes (PECEE elastic clustering).

    python3 tools/route_figures.py docs/data docs/figures [--prefix deploy] [--spacing 35]

Reads PREFIX-lattice.csv, PREFIX-nodes-sS.csv, PREFIX-routes-sS.csv and draws
  route-main.png    every node's main next hop toward the CH, hops to the CH, example
                    routes, and hops against the cell-free shortest route
  route-tables.png  one cell's stored tables: the tree to its CL and the next hops
                    toward each adjacent cell
"""
import argparse, csv, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

INK, INK2, SURF, GRIDC = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
C_CH, C_CL, C_BAD = "#e34948", "#eda100", "#e34948"
RAMP = LinearSegmentedColormap.from_list("hops", ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]
SIX = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#52514e"]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def load(src, prefix, s):
    lat = list(csv.DictReader(open(os.path.join(src, f"{prefix}-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    sel = {(int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1"}
    nodes = {r["id"]: r for r in csv.DictReader(open(os.path.join(src, f"{prefix}-nodes-s{s}.csv")))}
    routes = {r["id"]: r for r in csv.DictReader(open(os.path.join(src, f"{prefix}-routes-s{s}.csv")))}
    gws = list(csv.DictReader(open(os.path.join(src, f"{prefix}-gateways-s{s}.csv"))))
    bridges = list(csv.DictReader(open(os.path.join(src, f"{prefix}-bridges-s{s}.csv"))))
    return c, w, sel, nodes, routes, gws, bridges


def cells_layer(a, c, w, sel, fc="#f3f2ee", lw=.7):
    R = w / math.sqrt(3)
    a.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=fc,
                                    edgecolors="#ffffff", linewidths=lw, zorder=1))
    segs = []
    for q, r in sel:
        v = corners(*c[(q, r)], R)
        for k, (dq, dr) in enumerate(EDGE_NB):
            if (q + dq, r + dr) not in sel:
                segs.append([v[k], v[(k + 1) % 6]])
    a.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=2))


def cell_edges(a, c, w, cells, color="#c3c2b7", lw=.6):
    R = w / math.sqrt(3)
    segs = []
    for h in cells:
        v = corners(*c[h], R)
        segs += [[v[k], v[(k + 1) % 6]] for k in range(6)]
    a.add_collection(LineCollection(segs, colors=color, linewidths=lw, zorder=2))


def style(a):
    a.set_facecolor(SURF)
    a.set_aspect("equal")
    a.tick_params(colors=INK2, labelsize=7.5)
    for s in a.spines.values():
        s.set_visible(False)


def xy(n):
    return float(n["x"]), float(n["y"])


def cell_of(n):
    return int(n["q"]), int(n["r"])


def trace(routes, i):
    path = [i]
    while routes[path[-1]]["mainNext"] != "-1":
        path.append(routes[path[-1]]["mainNext"])
        assert len(path) < 10000
    return path


def free_path(nodes, routes, i, ch, rng, bridges):
    """One shortest path ignoring cells, following free hop counts down (lowest id)."""
    extra = {(b["a"], b["b"]) for b in bridges} | {(b["b"], b["a"]) for b in bridges}
    link = 0
    pos = {k: xy(v) for k, v in nodes.items()}
    path = [i]
    while path[-1] != ch:
        cur = path[-1]
        h = int(routes[cur]["freeHopsCH"])
        best = None
        for k, p in pos.items():
            if int(routes[k]["freeHopsCH"]) == h - 1 and (math.dist(p, pos[cur]) <= rng or (cur, k) in extra):
                if best is None or int(k) < int(best):
                    best = k
        path.append(best)
    return path


def fig_main(src, prefix, s, out, rng):
    c, w, sel, nodes, routes, gws, bridges = load(src, prefix, s)
    ch = [k for k, n in nodes.items() if n["isCH"] == "1"][0]
    fig = plt.figure(figsize=(18, 13.5), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], height_ratios=[1, 1], hspace=.18, wspace=.08,
                          left=.04, right=.98, top=.91, bottom=.05)
    hmax = max(int(r["hopsCH"]) for r in routes.values())
    # (a) every node's main next hop
    a = fig.add_subplot(gs[:, 0])
    cells_layer(a, c, w, sel)
    segs, cols = [], []
    for k, r in routes.items():
        if r["mainNext"] == "-1":
            continue
        segs.append([xy(nodes[k]), xy(nodes[r["mainNext"]])])
        cols.append(RAMP(int(r["hopsCH"]) / hmax))
    a.add_collection(LineCollection(segs, colors=cols, linewidths=.9, zorder=3))
    assert all(r["hopsCH"] != "-1" for r in routes.values())   # nobody is cut off
    a.add_collection(LineCollection([[xy(nodes[g["gwA"]]), xy(nodes[g["gwB"]])] for g in gws], colors=INK,
                                    linewidths=2.2, zorder=4))
    a.plot([], [], color=INK, lw=2.2, label=f"gateway: liên kết duy nhất giữa hai cell kề ({len(gws)})")
    for kind, col, lab in (("0", C_BAD, "bắc cầu trong cell"), ("1", "#eb6834", "gateway bắc cầu")):
        bs = [b for b in bridges if b["gateway"] == kind]
        if bs:
            a.add_collection(LineCollection([[xy(nodes[b["a"]]), xy(nodes[b["b"]])] for b in bs], colors=col,
                                            linewidths=1.6, linestyles=(0, (2, 1.5)), zorder=5))
            a.plot([], [], color=col, lw=1.6, ls=(0, (2, 1.5)),
                   label=f"{lab} > {rng:.0f} m ({len(bs)}, dài nhất {max(float(b['metres']) for b in bs):.0f} m)")
    cls = [k for k, n in nodes.items() if n["isCL"] == "1" and n["isCH"] != "1"]
    a.scatter([xy(nodes[k])[0] for k in cls], [xy(nodes[k])[1] for k in cls], s=26, facecolors="none",
              edgecolors=C_CL, linewidths=1.3, zorder=4, label="CL")
    a.scatter(*xy(nodes[ch]), s=320, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=6,
              label=f"CH #{ch}")
    sm = plt.cm.ScalarMappable(cmap=RAMP, norm=plt.Normalize(0, hmax))
    cb = fig.colorbar(sm, ax=a, shrink=.5, pad=.01)
    cb.set_label("số hop tới CH theo đường chính", fontsize=8.5, color=INK2)
    cb.ax.tick_params(labelsize=8, colors=INK2)
    cb.outline.set_visible(False)
    a.legend(loc="upper left", bbox_to_anchor=(0, -0.035), ncol=3, fontsize=8.5, frameon=False, labelcolor=INK2)
    a.set_title(f"(a) Next hop chính của mọi node (một đoạn thẳng node → next hop), spacing {s} m, "
                f"liên kết ≤ {rng:.0f} m", loc="left", fontsize=10.5, color=INK)
    style(a)
    # (b) example routes: the farthest node in six directions
    b = fig.add_subplot(gs[0, 1])
    cells_layer(b, c, w, sel)
    cx, cy = xy(nodes[ch])
    ex = []
    for k in range(6):
        ang = math.radians(60 * k + 30)
        cand = list(routes)
        ex.append(max(cand, key=lambda i: (xy(nodes[i])[0] - cx) * math.cos(ang) + (xy(nodes[i])[1] - cy) * math.sin(ang)))
    ex = list(dict.fromkeys(ex))
    for j, i in enumerate(ex):
        p = trace(routes, i)
        f = free_path(nodes, routes, i, ch, rng, bridges)
        b.plot([xy(nodes[k])[0] for k in f], [xy(nodes[k])[1] for k in f], color=INK2, lw=.9,
               ls=(0, (2, 2)), zorder=3, label="ngắn nhất bỏ qua cell" if j == 0 else None)
        b.plot([xy(nodes[k])[0] for k in p], [xy(nodes[k])[1] for k in p], color=SIX[j % 6], lw=1.8,
               marker="o", ms=2.5, zorder=4)
        b.annotate(f"#{i}: {len(p) - 1} hop (tối thiểu {routes[i]['freeHopsCH']})", xy(nodes[i]),
                   xytext=(5, 5), textcoords="offset points", fontsize=7.5, color=INK, zorder=6,
                   bbox=dict(boxstyle="round,pad=.15", fc=SURF, ec="none", alpha=.85))
    b.scatter(*xy(nodes[ch]), s=260, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=6)
    b.legend(loc="lower right", fontsize=8, frameon=False, labelcolor=INK2)
    b.set_title("(b) Đường chính thực đi (lần theo next hop) từ các node xa nhất theo 6 hướng",
                loc="left", fontsize=10.5, color=INK)
    style(b)
    # (c) hops vs cell-free hops
    d = fig.add_subplot(gs[1, 1])
    ok = list(routes.values())
    fh = np.array([int(r["freeHopsCH"]) for r in ok]); hh = np.array([int(r["hopsCH"]) for r in ok])
    m = max(hh.max(), fh.max()) + 1
    H = np.zeros((m, m))
    for x0, y0 in zip(fh, hh):
        H[y0, x0] += 1
    yy, xx = np.nonzero(H)
    d.scatter(xx, yy, s=6 + 2.2 * H[yy, xx], color="#3987e5", alpha=.75, lw=0, zorder=3)
    d.plot([0, m], [0, m], color=INK2, lw=.9, ls=(0, (3, 3)), zorder=2)
    d.text(m * .98, m * .93, "bằng nhau", ha="right", fontsize=8, color=INK2)
    extra = hh - fh
    d.set_xlabel("số hop tối thiểu tới CH nếu bỏ qua cell", fontsize=9, color=INK2)
    d.set_ylabel("số hop theo đường chính", fontsize=9, color=INK2)
    d.set_title(f"(c) Giá của việc đi theo cell: TB +{extra.mean():.1f} hop (+{100 * (hh.sum() / fh.sum() - 1):.0f} %); "
                f"{100 * (extra == 0).mean():.0f} % node bằng tối thiểu; nhiều nhất +{extra.max()}",
                loc="left", fontsize=10.5, color=INK)
    d.set_aspect("auto")
    d.grid(color=GRIDC, lw=.6)
    d.set_facecolor(SURF)
    d.tick_params(colors=INK2, labelsize=8)
    for sp in d.spines.values():
        sp.set_visible(False)
    fig.suptitle("Routing dựng sẵn tại BS (PECEE elastic clustering): next hop tới CL, tới từng cell kề qua "
                 "một gateway duy nhất, đường chính ngắn nhất tới CH — không node nào bị bỏ sót",
                 x=.04, ha="left", fontsize=13, color=INK)
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def fig_tables(src, prefix, s, out, rng):
    c, w, sel, nodes, routes, gws, bridges = load(src, prefix, s)
    ch = [k for k, n in nodes.items() if n["isCH"] == "1"][0]
    chc = cell_of(nodes[ch])
    # a cell next to the CH's cell with all six neighbours in the region
    A = next(h for h in [(chc[0] + dq, chc[1] + dr) for dq, dr in EDGE_NB]
             if h in sel and all((h[0] + dq, h[1] + dr) in sel for dq, dr in EDGE_NB))
    nbs = [(A[0] + dq, A[1] + dr) for dq, dr in EDGE_NB]
    memA = [k for k, n in nodes.items() if cell_of(n) == A]
    fig, ax = plt.subplots(2, 4, figsize=(19, 10), dpi=150, facecolor=SURF)
    ax = ax.flat
    view = [A] + nbs

    def base(a):
        cell_edges(a, c, w, view)
        R = w / math.sqrt(3)
        a.add_collection(PolyCollection([corners(*c[A], R)], facecolors="#f3f2ee", edgecolors=INK2,
                                        linewidths=1.2, zorder=1))
        near = [k for k, n in nodes.items() if cell_of(n) in view]
        a.scatter([xy(nodes[k])[0] for k in near], [xy(nodes[k])[1] for k in near], s=6, color="#b9b8b2",
                  lw=0, zorder=3)
        xs = [c[h][0] for h in view]; ys = [c[h][1] for h in view]
        a.set_xlim(min(xs) - .7 * w, max(xs) + .7 * w); a.set_ylim(min(ys) - .7 * w, max(ys) + .7 * w)
        style(a)

    def arrows(a, pairs, color):
        for u, v in pairs:
            a.annotate("", xy(nodes[v]), xy(nodes[u]),
                       arrowprops=dict(arrowstyle="-|>", color=color, lw=1.1, mutation_scale=8,
                                       shrinkA=2, shrinkB=2), zorder=4)

    # panel 0: tree to the CL
    a = ax[0]
    base(a)
    cl = [k for k in memA if nodes[k]["isCL"] == "1"][0]
    arrows(a, [(k, routes[k]["toCL"]) for k in memA if routes[k]["toCL"] != "-1"], "#1c5cab")
    a.scatter(*xy(nodes[cl]), s=90, facecolors="none", edgecolors=C_CL, linewidths=2, zorder=5)
    a.set_title(f"cell {A}: next hop tới CL #{cl}\n({len(memA)} node, TB "
                f"{np.mean([int(routes[k]['hopsCL']) for k in memA]):.1f} hop)",
                loc="left", fontsize=9.5, color=INK)
    # panels 1..6: next hops toward each adjacent cell
    for j, B in enumerate(nbs):
        a = ax[j + 1]
        base(a)
        R = w / math.sqrt(3)
        a.add_collection(PolyCollection([corners(*c[B], R)], facecolors=SIX[j] + "22", edgecolors=SIX[j],
                                        linewidths=1.2, zorder=1))
        key = f"{B[0]}:{B[1]}"
        pairs, hops = [], []
        for k in memA:
            ent = dict(e.split(">") for e in routes[k]["toCells"].split("|") if e)
            nx, h = ent[key].split("/")
            pairs.append((k, nx)); hops.append(int(h))
        arrows(a, pairs, SIX[j])
        g = next(g for g in gws if {(int(g["qA"]), int(g["rA"])), (int(g["qB"]), int(g["rB"]))} == {A, B})
        ga, gb = (g["gwA"], g["gwB"]) if (int(g["qA"]), int(g["rA"])) == A else (g["gwB"], g["gwA"])
        for k in (ga, gb):
            a.scatter(*xy(nodes[k]), s=70, marker="D", color=SIX[j], edgecolors=INK, linewidths=1, zorder=6)
        main = sum(1 for k in memA if routes[k]["mainVia"] == key)
        a.set_title(f"next hop tới cell kề {B}: qua gateway #{ga} → #{gb} ({float(g['metres']):.0f} m"
                    f"{', bắc cầu' if g['bridge'] == '1' else ''})\nTB {np.mean(hops):.1f} hop; "
                    f"{main} node chọn làm đường chính", loc="left", fontsize=9.5, color=INK)
        if B == chc:
            a.scatter(*xy(nodes[ch]), s=200, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=6)
    # panel 7: the main choice of each node in A
    a = ax[7]
    base(a)
    colof = {f"{B[0]}:{B[1]}": SIX[j] for j, B in enumerate(nbs)}
    colof["CL"] = "#1c5cab"
    for k in memA:
        via = routes[k]["mainVia"]
        if via == "-":
            continue
        arrows(a, [(k, routes[k]["mainNext"])], colof.get(via, INK))
    a.scatter(*xy(nodes[ch]), s=200, marker="*", color=C_CH, edgecolors=INK, linewidths=.8, zorder=6)
    a.set_title("đường chính của từng node trong cell\n(màu = bảng được chọn; đỏ sao = CH)", loc="left",
                fontsize=9.5, color=INK)
    fig.suptitle(f"Bảng routing của một cell (cell {A}, kề cell của CH): mỗi node lưu 1 next hop tới CL và 1 "
                 f"next hop tới mỗi cell kề, luôn qua gateway duy nhất (♦) — spacing {s} m, liên kết ≤ {rng:.0f} m",
                 x=.01, ha="left", fontsize=12.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .95))
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("outdir")
    ap.add_argument("--prefix", default="deploy")
    ap.add_argument("--spacing", type=int, default=35)
    ap.add_argument("--range", type=float, default=50.0, help="link range the routes were built with, m")
    o = ap.parse_args()
    os.makedirs(o.outdir, exist_ok=True)
    fig_main(o.src, o.prefix, o.spacing, os.path.join(o.outdir, "route-main.png"), o.range)
    fig_tables(o.src, o.prefix, o.spacing, os.path.join(o.outdir, "route-tables.png"), o.range)


if __name__ == "__main__":
    main()
