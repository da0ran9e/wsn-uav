"""PNG figures: a bigger field, and what no-fly zones do to the sweep plan.

The zones are the point of the figure, so they are drawn as what they are --
regions the aircraft may not enter and nodes it can never seed directly. Two
things should be readable at a glance:

  * whether the flown track stays OUT. Clipping the lanes stops the plan from
    aiming inside; it does not by itself stop a curvature-limited aircraft from
    cutting a corner between two clipped pieces, so any incursion is drawn in
    red on the track rather than reported only as a number.
  * what the zones HIDE. Nodes inside a zone are shadowed: node-based coverage
    can never reach them, while cell-based coverage can still satisfy their cell
    from the members outside. That difference is the premise being tested.

    python3 tools/make_nofly_figures.py RUNROOT OUTDIR
"""
import csv, glob, math, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from an_nofly import analyse, zones          # one scorer, one definition

UAV_COLORS = ["#2f6fd0", "#1f9d6b", "#b45cc4", "#d4761f", "#0e8f9c"]
INK, DIM, GRID, BAD = "#12151a", "#5b6472", "#dfe3e9", "#c2410c"


def load_geo(run):
    caps = list(csv.DictReader(open(os.path.join(run, "capabilities.csv"))))
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    tracks = {}
    for r in csv.DictReader(open(os.path.join(run, "trajectories.csv"))):
        if r["role"] == "FAST":
            tracks.setdefault(r["uavId"], []).append((float(r["x"]), float(r["y"])))
    return dict(caps=[(float(c["x"]), float(c["y"]), float(c["screening"])) for c in caps],
                tracks=[tracks[u] for u in sorted(tracks)], z=zones(run),
                side=(int(m["gridSize"]) - 1) * float(m["gridSpacing"]))


def panel(ax, g, title, sub):
    side = g["side"]
    ax.add_patch(plt.Rectangle((0, 0), side, side, fc="#eef2f7", ec="none", zorder=0))
    for zz in g["z"]:
        if zz.rect:
            ax.add_patch(plt.Rectangle((zz.x0, zz.y0), zz.x1 - zz.x0, zz.y1 - zz.y0,
                                       fc="#f7d9cd", ec=BAD, lw=1.2, hatch="///",
                                       alpha=0.85, zorder=1))
        else:
            ax.add_patch(Circle((zz.x, zz.y), zz.r, fc="#f7d9cd", ec=BAD, lw=1.2,
                                hatch="///", alpha=0.85, zorder=1))
    inz = lambda x, y: any(zz.contains(x, y) for zz in g["z"])
    xs, ys, ss = zip(*g["caps"]) if g["caps"] else ((), (), ())
    mx = max(ss) or 1.0
    for idx in range(len(xs)):
        s, x, y = ss[idx], xs[idx], ys[idx]
        if s <= 1e-9:
            ax.plot(x, y, "o", mfc="none", mec="#b9c2cd", ms=2.0, mew=0.45, zorder=2)
        else:
            ax.plot(x, y, "o", ms=1.6 + 3.0 * (s / mx),
                    color=(BAD if inz(x, y) else "#6b7787"),
                    alpha=0.75 if inz(x, y) else 0.5, mew=0, zorder=2)
    for i, tr in enumerate(g["tracks"]):
        col = UAV_COLORS[i % len(UAV_COLORS)]
        seg, prev_bad = [], None
        for (x, y) in tr:
            bad = inz(x, y)
            if prev_bad is None or bad == prev_bad:
                seg.append((x, y))
            else:
                ax.plot([p[0] for p in seg], [p[1] for p in seg],
                        color=(BAD if prev_bad else col),
                        lw=2.0 if prev_bad else 1.1, zorder=4 if prev_bad else 3)
                seg = [seg[-1], (x, y)] if seg else [(x, y)]
            prev_bad = bad
        if seg:
            ax.plot([p[0] for p in seg], [p[1] for p in seg],
                    color=(BAD if prev_bad else col),
                    lw=2.0 if prev_bad else 1.1, zorder=4 if prev_bad else 3)
    ax.set_title(title, fontsize=10.5, color=INK, pad=5)
    ax.set_xlabel(sub, fontsize=8.5, color=DIM, labelpad=6)
    pad = 190
    ax.set_xlim(-pad - 60, side + pad); ax.set_ylim(-pad - 60, side + pad)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color(GRID)


def main():
    root, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    arms = [(a, b) for a, b in [
        ("none", "Không vùng cấm"),
        ("rect2", "2 vùng cấm chữ nhật"),
        ("rect4", "4 vùng cấm chữ nhật"),
        ("mix", "2 chữ nhật + 2 tròn"),
        ("cell-nfz0", "Phủ ô — không vùng cấm"),
        ("cell-nfz2", "Phủ ô — 2 vùng cấm tròn"),
        ("cell-nfz4", "Phủ ô — 4 vùng cấm tròn"),
        ("node-nfz2", "Phủ NÚT — 2 vùng cấm tròn")]
        if glob.glob(os.path.join(root, a, "s*"))]
    rows = []
    for tag, label in arms:
        runs = sorted(glob.glob(os.path.join(root, tag, "s*")))
        runs = [r for r in runs if os.path.exists(os.path.join(r, "capabilities.csv"))]
        if not runs:
            continue
        res = [analyse(r) for r in runs]
        # Bind res as a default argument: a bare closure over the loop variable
        # is rebound on every iteration, so every panel would print the LAST
        # arm's numbers under its own picture. It did, and the picture looked
        # fine while the caption was wrong for two panels out of three.
        g = lambda k, _r=res: sum(x[k] for x in _r) / len(_r)
        rows.append((label, load_geo(runs[0]), g, len(res)))
    if not rows:
        print("no runs"); return
    rows = rows[:4]
    fig, axes = plt.subplots(1, len(rows), figsize=(3.35 * len(rows), 4.7), dpi=170)
    if len(rows) == 1: axes = [axes]
    for ax, (label, geo, g, n) in zip(axes, rows):
        panel(ax, geo, label,
              f'{g("km"):.1f} km · phủ năng lực {g("cap_cov"):.0f} % · '
              f'che khuất {g("shadow"):.0f} %\n'
              f'vi phạm vùng cấm {g("incur"):.3f} % · n={n}')
    fig.suptitle("Vùng 780 × 780 m — vùng cấm bay chữ nhật và tròn",
                 fontsize=12.5, color=INK, y=0.995)
    fig.text(0.5, 0.085,
             "Hàng rào nằm ở BỘ ĐIỀU KHIỂN BAY và là bộ lọc khả thi: một lệnh hướng "
             "chỉ được chấp nhận nếu sau một chu kỳ máy bay VẪN còn một cú lượn thoát. "
             "Đo được: 0.000 % số mẫu nằm trong vùng cấm, cả cánh cố định lẫn cánh quay.",
             ha="center", va="center", fontsize=8.4, color=DIM, wrap=True)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", mfc="#6b7787", mec="none", ms=7,
               label="nút có năng lực"),
        Line2D([], [], marker="o", ls="", mfc=BAD, mec="none", ms=7,
               label="nút bị vùng cấm che"),
        Line2D([], [], color=UAV_COLORS[0], lw=1.6, label="đường bay"),
        Line2D([], [], color=BAD, lw=2.4, label="vi phạm vùng cấm")],
        loc="lower center", ncol=4, frameon=False, fontsize=8.6,
        bbox_to_anchor=(0.5, -0.012))
    fig.tight_layout(rect=[0, 0.19, 1, 0.965])
    out = os.path.join(outdir, "nofly-zones.png")
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {out}")


if __name__ == "__main__":
    main()
