"""PNG figures: how the Phase 1 sweep plan adapts to its parameters.

Two knobs are varied and each changes the plan for a different reason:

  capPriorityExp  how hard the planner leans toward capable nodes. 0 treats
                  every node that CAN see as equal; 3 chases the best ones and
                  lets mediocre ground go. The lane set should visibly migrate
                  toward the capability, not stay put.
  gridSpacing     node pitch. Raising it at fixed gridSize also enlarges the
                  field, so this axis moves area AND density together -- the
                  confound SIM-SPEC section 8 warns about, restated on the figure
                  rather than left for the reader to trip over.

    python3 tools/make_adapt_figures.py RUNROOT OUTDIR
"""
import csv, glob, math, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

RC = 50.0
UAV_COLORS = ["#2f6fd0", "#1f9d6b", "#b45cc4", "#d4761f", "#0e8f9c"]
INK, DIM, GRID = "#12151a", "#5b6472", "#dfe3e9"


def load(run):
    caps = list(csv.DictReader(open(os.path.join(run, "capabilities.csv"))))
    m = list(csv.DictReader(open(os.path.join(run, "metrics.csv"))))[0]
    tracks, prev, dist = {}, {}, {}
    for r in csv.DictReader(open(os.path.join(run, "trajectories.csv"))):
        if r["role"] != "FAST":
            continue
        u, x, y = r["uavId"], float(r["x"]), float(r["y"])
        tracks.setdefault(u, []).append((x, y))
        if u in prev:
            dist[u] = dist.get(u, 0.0) + math.hypot(x - prev[u][0], y - prev[u][1])
        prev[u] = (x, y)
    return dict(caps=[(float(c["x"]), float(c["y"]), float(c["screening"])) for c in caps],
                tracks=[tracks[u] for u in sorted(tracks)],
                km=sum(dist.values()) / 1000.0,
                dist=[dist[u] / 1000.0 for u in sorted(tracks)],
                spacing=float(m["gridSpacing"]), n=int(m["gridSize"]),
                loc=int(m["victimsLocated"]), vic=int(m["victimCount"]),
                kJ=float(m["uavEnergyJ"]) / 1000.0, tfix=float(m["timeToFixAtBS_s"]))


def cap_covered(d):
    tot = sum(s for _, _, s in d["caps"]) or 1.0
    seen = 0.0
    for cx, cy, s in d["caps"]:
        hit = False
        for tr in d["tracks"]:
            for k in range(1, len(tr)):
                ax, ay = tr[k - 1]; bx, by = tr[k]
                vx, vy = bx - ax, by - ay
                L2 = vx * vx + vy * vy
                t = ((cx - ax) * vx + (cy - ay) * vy) / L2 if L2 > 0 else 0.0
                t = max(0.0, min(1.0, t))
                if math.hypot(cx - (ax + t * vx), cy - (ay + t * vy)) <= RC:
                    hit = True; break
            if hit: break
        if hit: seen += s
    return 100.0 * seen / tot


def panel(ax, d, title, sub):
    side = (d["n"] - 1) * d["spacing"]
    ax.add_patch(plt.Rectangle((0, 0), side, side, fc="#eef2f7", ec="none", zorder=0))
    xs = [c[0] for c in d["caps"]]; ys = [c[1] for c in d["caps"]]
    ss = [c[2] for c in d["caps"]]
    mx = max(ss) or 1.0
    blind = [i for i, s in enumerate(ss) if s <= 1e-9]
    seen = [i for i, s in enumerate(ss) if s > 1e-9]
    ax.scatter([xs[i] for i in blind], [ys[i] for i in blind], s=7,
               facecolors="none", edgecolors="#c2410c", linewidths=0.5, zorder=2)
    ax.scatter([xs[i] for i in seen], [ys[i] for i in seen],
               s=[4 + 34 * (ss[i] / mx) for i in seen],
               c="#6b7787", alpha=0.55, linewidths=0, zorder=2)
    for i, tr in enumerate(d["tracks"]):
        ax.plot([p[0] for p in tr], [p[1] for p in tr],
                color=UAV_COLORS[i % len(UAV_COLORS)], lw=1.15, zorder=3)
    ax.set_title(title, fontsize=10.5, color=INK, pad=5)
    ax.set_xlabel(sub, fontsize=8.6, color=DIM, labelpad=6)
    pad = 150
    ax.set_xlim(-pad - 110, side + pad); ax.set_ylim(-pad - 110, side + pad)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_color(GRID)


def series(root, tag_fmt, values):
    out = []
    for v in values:
        runs = sorted(glob.glob(os.path.join(root, tag_fmt.format(v), "s*")))
        ds = [load(r) for r in runs if os.path.exists(os.path.join(r, "capabilities.csv"))]
        if not ds:
            out.append(None); continue
        cc = [cap_covered(d) for d in ds]
        tf = [d["tfix"] for d in ds if d["tfix"] > 0]
        out.append(dict(v=v, n=len(ds), first=ds[0],
                        km=sum(d["km"] for d in ds) / len(ds),
                        cap=sum(cc) / len(cc),
                        kJ=sum(d["kJ"] for d in ds) / len(ds),
                        tfix=(sum(tf) / len(tf)) if tf else float("nan"),
                        loc=sum(d["loc"] for d in ds), vic=sum(d["vic"] for d in ds),
                        imb=sum(100 * (max(d["dist"]) - min(d["dist"]))
                                / (sum(d["dist"]) / len(d["dist"])) for d in ds) / len(ds)))
    return [o for o in out if o]


def maps_figure(rows, title, note, path, label):
    n = len(rows)
    fig, axes = plt.subplots(1, n, figsize=(3.3 * n, 4.6), dpi=170)
    if n == 1: axes = [axes]
    for ax, r in zip(axes, rows):
        d = r["first"]
        panel(ax, d, label(r),
              f'{r["km"]:.1f} km · phủ năng lực {r["cap"]:.0f} % · lệch {r["imb"]:.0f} %')
    fig.suptitle(title, fontsize=12.5, color=INK, y=0.995)
    fig.text(0.5, 0.095, note, ha="center", va="center", fontsize=8.4,
             color=DIM, wrap=True)
    fig.legend(handles=[
        Line2D([], [], marker="o", ls="", mfc="#6b7787", mec="none", ms=7,
               label="nút có năng lực (to = cao)"),
        Line2D([], [], marker="o", ls="", mfc="none", mec="#c2410c", ms=6,
               label="nút không camera"),
        Line2D([], [], color=UAV_COLORS[0], lw=1.6, label="đường bay từng UAV")],
        loc="lower center", ncol=3, frameon=False, fontsize=8.6,
        bbox_to_anchor=(0.5, -0.012))
    fig.tight_layout(rect=[0, 0.19, 1, 0.965])
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {path}")


def curves_figure(prio, sp, path):
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.05), dpi=170)
    specs = [("km", "quãng đường FAST (km)"), ("cap", "năng lực được phủ (%)"),
             ("tfix", "thời gian tới toạ độ (s)")]
    for ax, (key, ylab) in zip(axes, specs):
        ax.plot([r["v"] for r in prio], [r[key] for r in prio], "o-",
                color="#2f6fd0", lw=1.6, ms=4.5, label="ưu tiên năng lực (mũ)")
        ax2 = ax.twiny()
        ax2.plot([r["v"] for r in sp], [r[key] for r in sp], "s--",
                 color="#d4761f", lw=1.6, ms=4.5, label="spacing (m)")
        ax2.tick_params(axis="x", colors="#d4761f", labelsize=8)
        ax.tick_params(labelsize=8.5); ax.set_ylabel(ylab, fontsize=9, color=INK)
        ax.set_xlabel("mũ ưu tiên", fontsize=9, color="#2f6fd0")
        ax.grid(alpha=0.25, lw=0.6)
        for s in ax.spines.values(): s.set_color(GRID)
    fig.legend(handles=[Line2D([], [], color="#2f6fd0", marker="o", lw=1.6,
                               label="mũ ưu tiên năng lực (trục dưới)"),
                        Line2D([], [], color="#d4761f", marker="s", ls="--", lw=1.6,
                               label="grid spacing, m (trục trên)")],
               loc="lower center", ncol=2, frameon=False, fontsize=8.8,
               bbox_to_anchor=(0.5, -0.06))
    fig.suptitle("Kế hoạch quét thích nghi theo tham số", fontsize=12, color=INK)
    fig.tight_layout(rect=[0, 0.07, 1, 0.93])
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  {path}")


def main():
    root, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    prio = series(root, "prio{}", [0, 1, 2, 3])
    sp = series(root, "sp{}", [25, 30, 35])
    base = series(root, "prio{}", [1])
    sp = base and [dict(base[0], v=20)] + sp or sp
    # The priority knob is inert on a 460 m field: five lanes already span it, so
    # the minimum spanning set is forced by geometry and no weighting can move
    # it. It only has room once the field is large relative to the swath, which
    # is what this second series shows.
    big = series(root, "big-prio{}", [0, 1, 3])
    print("figures:")
    if prio:
        maps_figure(prio,
                    "Đường bay thích nghi theo TRỌNG SỐ ƯU TIÊN của nút",
                    "Mũ 0 = mọi nút có camera đều như nhau · mũ càng cao, kế hoạch càng "
                    "bám các nút năng lực cao và bỏ qua vùng yếu.",
                    os.path.join(outdir, "adapt-priority.png"),
                    lambda r: f'mũ ưu tiên = {r["v"]}')
    if sp:
        maps_figure(sp,
                    "Đường bay thích nghi theo GRID SPACING",
                    "Cảnh báo: tăng spacing ở cùng gridSize làm DIỆN TÍCH tăng và MẬT ĐỘ "
                    "giảm cùng lúc (SIM-SPEC §8) — không quy hiệu ứng cho riêng mật độ.",
                    os.path.join(outdir, "adapt-spacing.png"),
                    lambda r: f'spacing = {r["v"]} m')
    if big:
        maps_figure(big,
                    "Ưu tiên năng lực CÓ tác dụng — khi vùng đủ lớn (spacing 30 m, 690 m)",
                    "Ở vùng 460 m, 5 luống đã phủ kín nên tập luống tối thiểu bị HÌNH HỌC "
                    "ép cứng và mọi mũ ưu tiên cho cùng một kế hoạch. Phải đủ rộng thì "
                    "người lập kế hoạch mới có gì để chọn.",
                    os.path.join(outdir, "adapt-priority-bigfield.png"),
                    lambda r: f'mũ ưu tiên = {r["v"]} (690 m)')
    if prio and sp:
        curves_figure(prio, sp, os.path.join(outdir, "adapt-curves.png"))
    print("\ntable:")
    print(f"{'cấu hình':<16}{'n':>3}{'km':>7}{'cap%':>7}{'lệch%':>7}{'kJ':>7}{'tFix':>7}{'loc':>8}")
    for lbl, rows in (("mũ ưu tiên", prio), ("spacing", sp), ("mũ@690m", big)):
        for r in rows:
            print(f"{lbl+'='+str(r['v']):<16}{r['n']:>3}{r['km']:7.1f}{r['cap']:7.1f}"
                  f"{r['imb']:7.1f}{r['kJ']:7.0f}{r['tfix']:7.0f}{r['loc']:5d}/{r['vic']:<3}")


if __name__ == "__main__":
    main()
