"""Step 4 report: the cell summary gathered up to each CL.

    python3 tools/summary_report.py DATA FIGS [--prefix summary] [--deploy deploy] [--spacing 35]

Reads DATA/PREFIX-cells.csv, DATA/PREFIX-nodes.csv and the deployment
(DEPLOY-lattice.csv, DEPLOY-nodes-sS.csv), prints the summary tables and draws
  summary-cells.png   two cells: the tree the summaries took, what each node sent
  summary-time.png    how fast every CL knew its cell, and at what cost
"""
import argparse, csv, math, os, statistics as S

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import LinearSegmentedColormap, LogNorm
import numpy as np

INK, INK2, SURF, GRIDC = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
C_CL, C_BLUE, C_RED = "#eda100", "#2a78d6", "#e34948"
RAMP = LinearSegmentedColormap.from_list("lacks", ["#f1f0eb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def style(a):
    a.set_facecolor(SURF)
    a.tick_params(colors=INK2, labelsize=8)
    for s in a.spines.values():
        s.set_visible(False)


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * len(v)))]


def tables(cells):
    runs = sorted({r["run"] for r in cells})
    t = [float(r["doneS"]) for r in cells if r["complete"] == "1"]
    exact = sum(r["exact"] == "1" and r["complete"] == "1" for r in cells)
    print(f"{len(runs)} missions x {len(cells) // len(runs)} cells = {len(cells)} cell summaries")
    print(f"  CL holds the exact cell summary: {exact} ({100 * exact / len(cells):.2f} %)")
    print(f"  time to the CL: median {S.median(t):.3f} s, p90 {pct(t, .9):.3f}, p99 {pct(t, .99):.3f}, "
          f"max {max(t):.3f}")
    for key, lab in (("frames", "frames per cell"), ("bytes", "bytes per cell")):
        v = [int(r[key]) for r in cells]
        print(f"  {lab}: median {S.median(v):.0f}, p90 {pct(v, .9)}, max {max(v)}")
    sw = [int(r["switches"]) for r in cells]
    print(f"  parent switches: {sum(sw)} in {sum(x > 0 for x in sw)} cell summaries")
    lk = [int(r["lacksTrue"]) for r in cells]
    print(f"  cells lacking something: {sum(x > 0 for x in lk)} ({100 * sum(x > 0 for x in lk) / len(lk):.1f} %), "
          f"lacks when > 0: median {S.median([x for x in lk if x > 0]) if any(lk) else 0}, max {max(lk)}")


def fig_cells(data, prefix, deploy, s, figs):
    cells = list(csv.DictReader(open(os.path.join(data, f"{prefix}-cells.csv"))))
    run1 = [r for r in cells if r["run"] == cells[0]["run"]]
    nd = {r["id"]: r for r in csv.DictReader(open(os.path.join(data, f"{prefix}-nodes.csv")))}
    pos = {r["id"]: r for r in csv.DictReader(open(os.path.join(data, f"{deploy}-nodes-s{s}.csv")))}
    lat = list(csv.DictReader(open(os.path.join(data, f"{deploy}-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    # a cell that holds everything, and the one that lacks the most
    full = [r for r in run1 if r["lacksTrue"] == "0"]
    pick = [sorted(full, key=lambda r: float(r["doneS"]))[len(full) // 2],
            max(run1, key=lambda r: int(r["lacksTrue"]))]
    fig, ax = plt.subplots(1, 2, figsize=(16.5, 8.2), dpi=150, facecolor=SURF)
    for a, row in zip(ax, pick):
        h = (int(row["q"]), int(row["r"]))
        mem = [i for i, p in pos.items() if (int(p["q"]), int(p["r"])) == h]
        a.add_collection(PolyCollection([corners(*c[h], R)], facecolors="#f3f2ee", edgecolors=INK2,
                                        linewidths=1.2, zorder=1))
        xy = {i: (float(pos[i]["x"]), float(pos[i]["y"])) for i in mem}
        sent = [int(nd[i]["lacksSent"]) for i in mem]
        norm = LogNorm(vmin=1, vmax=max(2, int(row["nodes"]) and 2000))
        for i in mem:
            par = nd[i]["parent"]
            if par == i:
                continue
            b = int(nd[i]["bytes"])
            a.annotate("", xy[par], xy[i], arrowprops=dict(arrowstyle="-|>", color=INK2,
                       lw=0.8 + 2.2 * min(1, b / 200), mutation_scale=10, shrinkA=6, shrinkB=6), zorder=2)
            mx, my = (xy[i][0] + xy[par][0]) / 2, (xy[i][1] + xy[par][1]) / 2
            a.text(mx, my, f"{b} B", fontsize=6.5, color=INK2, ha="center", va="center", zorder=3,
                   bbox=dict(boxstyle="round,pad=.1", fc=SURF, ec="none", alpha=.8))
        for i in mem:
            ls = int(nd[i]["lacksSent"]) if nd[i]["parent"] != i else int(row["lacksAtCL"])
            col = RAMP(norm(max(1, ls))) if ls > 0 else "#ffffff"
            is_cl = pos[i]["isCL"] == "1"
            a.scatter(*xy[i], s=230 if is_cl else 120, color=col, edgecolors=C_CL if is_cl else INK,
                      linewidths=2.2 if is_cl else .8, zorder=4)
            a.annotate(f"{nd[i]['lacksSelf']}→{ls}", xy[i], xytext=(7, -10), textcoords="offset points",
                       fontsize=6.8, color=INK, zorder=5)
        a.set_xlim(c[h][0] - 1.1 * R, c[h][0] + 1.1 * R)
        a.set_ylim(c[h][1] - 1.15 * R, c[h][1] + 1.15 * R)
        a.set_aspect("equal")
        a.set_title(f"cell {h}: {row['nodes']} node, sâu {row['depth']} hop — CL biết cell thiếu "
                    f"{row['lacksAtCL']}/2000 mảnh sau {float(row['doneS']) * 1000:.0f} ms\n"
                    f"{row['frames']} frame, {row['bytes']} B, {row['retries']} lần gửi lại, "
                    f"{row['switches']} lần đổi cha", loc="left", fontsize=10, color=INK)
        style(a)
    sm = plt.cm.ScalarMappable(cmap=RAMP, norm=LogNorm(vmin=1, vmax=2000))
    cb = fig.colorbar(sm, ax=ax, shrink=.6, pad=.01)
    cb.set_label("mảnh nhánh cây còn thiếu (đã gửi lên); trắng = 0", fontsize=8.5, color=INK2)
    cb.ax.tick_params(labelsize=8, colors=INK2)
    cb.outline.set_visible(False)
    fig.suptitle("Tóm tắt gộp dần về CL (lượt bay 1): mỗi node gửi lên cha các mảnh mà cả nhánh của nó cùng thiếu "
                 "— nhãn node: tự thiếu → nhánh thiếu; nhãn mũi tên: số byte đã gửi; viền cam = CL",
                 x=.01, ha="left", fontsize=11.5, color=INK)
    out = os.path.join(figs, "summary-cells.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight")
    print(f"  {out}")


def fig_time(data, prefix, figs):
    cells = list(csv.DictReader(open(os.path.join(data, f"{prefix}-cells.csv"))))
    t = np.sort([float(r["doneS"]) for r in cells if r["complete"] == "1"])
    fig, ax = plt.subplots(1, 3, figsize=(17, 5.2), dpi=150, facecolor=SURF)
    a = ax[0]
    a.plot(t, np.arange(1, len(t) + 1) / len(cells), color=C_BLUE, lw=2)
    for q in (.5, .9, .99):
        v = pct(list(t), q)
        a.axvline(v, color=INK2, lw=.8, ls=(0, (3, 3)))
        a.text(v, .03 + .1 * [.5, .9, .99].index(q), f" P{int(q * 100)} = {v:.2f} s", fontsize=8, color=INK2)
    a.set_xscale("log")
    a.set_xlabel("thời gian tới khi CL nắm tóm tắt đủ của cell, s", fontsize=9, color=INK2)
    a.set_ylabel("tỉ lệ cell (mọi lượt bay)", fontsize=9, color=INK2)
    a.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a.set_title("Tốc độ", loc="left", fontsize=10.5, color=INK)
    a.grid(color=GRIDC, lw=.6)
    style(a)
    a = ax[1]
    d = np.array([int(r["depth"]) for r in cells]); tt = np.array([float(r["doneS"]) for r in cells])
    for k in sorted(set(d)):
        v = tt[d == k]
        a.scatter(np.full(len(v), k) + np.random.default_rng(k).uniform(-.25, .25, len(v)), v, s=3,
                  color=C_BLUE, alpha=.25, lw=0)
        a.plot([k - .3, k + .3], [np.median(v)] * 2, color=INK, lw=2)
    a.set_yscale("log")
    a.set_xlabel("độ sâu cây trong cell (hop tới CL)", fontsize=9, color=INK2)
    a.set_ylabel("thời gian, s", fontsize=9, color=INK2)
    a.set_title("Theo độ sâu cây (vạch đen: trung vị)", loc="left", fontsize=10.5, color=INK)
    a.grid(color=GRIDC, lw=.6)
    style(a)
    a = ax[2]
    b = np.array([int(r["bytes"]) for r in cells]); n = np.array([int(r["nodes"]) for r in cells])
    a.hist(b / n, bins=60, color=C_BLUE, alpha=.85)
    a.axvline(np.median(b / n), color=INK, lw=1.2)
    a.text(np.median(b / n), a.get_ylim()[1] * .92, f"  trung vị {np.median(b / n):.0f} B/node", fontsize=8.5, color=INK)
    a.set_xlabel("byte tóm tắt mỗi node (tổng byte của cell / số node)", fontsize=9, color=INK2)
    a.set_ylabel("số cell", fontsize=9, color=INK2)
    a.set_title("Chi phí", loc="left", fontsize=10.5, color=INK)
    a.grid(color=GRIDC, lw=.6)
    style(a)
    nm = len({r["run"] for r in cells})
    fig.suptitle(f"Tóm tắt nội cell về CL: {nm} lượt bay × {len(cells) // nm} cell, K = 2000 mảnh, kênh G2G "
                 f"(che khuất tĩnh 7,8 dB, Rayleigh), khe 10 ms", x=.01, ha="left", fontsize=11.5, color=INK)
    fig.tight_layout()
    out = os.path.join(figs, "summary-time.png")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("figs")
    ap.add_argument("--prefix", default="summary"); ap.add_argument("--deploy", default="deploy")
    ap.add_argument("--spacing", type=int, default=35)
    o = ap.parse_args()
    tables(list(csv.DictReader(open(os.path.join(o.data, f"{o.prefix}-cells.csv")))))
    fig_cells(o.data, o.prefix, o.deploy, o.spacing, o.figs)
    fig_time(o.data, o.prefix, o.figs)


if __name__ == "__main__":
    main()
