"""Figures and tables of the River trial (river_sim.py output), one per stage.

    python3 tools/river_figures.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
        --sim "OUTDIR/p*" --r1 OUTDIR/p0 --data docs/data --figs docs/figures

--sim   prefixes of river_sim.py outputs (several processes are merged)
--r1    the prefix holding run 1 (trace and per-cell files)
Writes DATA/river-crit.csv, DATA/river-runs.csv, DATA/river-load.csv (merged) and
DATA/river-r1-*.csv, and draws
  river-plan.png      stage 0: the plan (Axe order, River, Banks, critical cells, Circles)
  river-pass.png      stage 1: what each cell holds after the pass (its CL; all its nodes)
  river-load.png      stages 2-4: frames per cell medium, River vs direct (mean per run)
  river-timeline.png  stage 4: each critical CL's holding over time, run 1
  river-done.png      all runs: completion time per critical cell, River vs direct
"""
import argparse, csv, glob, math, os, shutil, statistics as S, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Patch
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import load, plan  # noqa: E402

INK, INK2, SURF, GREY, FAINT = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1", "#c9dcf3"
RIVER, DIRECT = "#1c5cab", "#eda100"
SEQ = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#f6c3c3", "#e34948", "#8f1d1b"])
RAMP = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#f1f0eb", "#86b6ef", "#3987e5", "#0d366b"])
HEAT = matplotlib.colors.LinearSegmentedColormap.from_list("h", ["#f1f0eb", "#f6c3c3", "#e34948", "#8f1d1b"])
CAT = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#52514e"]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def merge(prefixes, suffix, out):
    rows, head = [], None
    for p in sorted(prefixes):
        r = list(csv.reader(open(p + suffix)))
        head = r[0]
        rows += r[1:]
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(head)
        w.writerows(rows)
    return [dict(zip(head, x)) for x in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--sim")
    ap.add_argument("--r1")
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    D = a.data
    if a.sim:
        pre = sorted({p[:-len("-crit.csv")] for p in glob.glob(a.sim + "-crit.csv")})
        assert pre, a.sim
        merge(pre, "-crit.csv", os.path.join(D, "river-crit.csv"))
        merge(pre, "-runs.csv", os.path.join(D, "river-runs.csv"))
        tot = {}
        for p in pre:
            for r in csv.DictReader(open(p + "-load.csv")):
                key = tuple(r[k] for k in ("scheme", "kind", "a_q", "a_r", "b_q", "b_r"))
                tot[key] = tot.get(key, 0) + int(r["frames"])
        with open(os.path.join(D, "river-load.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["scheme", "kind", "a_q", "a_r", "b_q", "b_r", "frames"])
            for k, v in sorted(tot.items()):
                w.writerow(list(k) + [v])
        for s in ("river", "direct"):
            for kind in ("trace", "r1"):
                shutil.copy(f"{a.r1}-{kind}-{s}.csv", os.path.join(D, f"river-r1-{kind}-{s}.csv"))
    crit = list(csv.DictReader(open(os.path.join(D, "river-crit.csv"))))
    runs = list(csv.DictReader(open(os.path.join(D, "river-runs.csv"))))
    load_ = list(csv.DictReader(open(os.path.join(D, "river-load.csv"))))
    nrun = len({r["run"] for r in runs})

    geo = load(a.deploy, a.path)
    P = plan(geo)
    c, w, R, sel = geo["c"], geo["w"], geo["R"], geo["cells"]
    S_ = set(sel)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S_]
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    path = geo["path"]
    crits = P["crit"]
    cname = {k: f"({k[0]},{k[1]})" for k in crits}
    ccol = {k: CAT[i % len(CAT)] for i, k in enumerate(crits)}

    def frame(ax, col, title, track=.6):
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[col[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.7, zorder=0))
        ax.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=1))
        if track:
            ax.plot(path[:, 0], path[:, 1], color=INK, lw=1, alpha=track, zorder=6)
        ax.set_xlim(min(xs) - w, max(xs) + w); ax.set_ylim(min(ys) - w, max(ys) + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(title, loc="left", fontsize=9.5, color=INK)

    def bar(ax, cmap, lo, hi, label):
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(lo, hi))
        cb = plt.colorbar(sm, ax=ax, shrink=.6, pad=.01)
        cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
        cb.set_label(label, fontsize=8, color=INK2)

    def save(fig, name):
        out = os.path.join(a.figs, name)
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
        plt.close(fig)
        print(f"  {out}")

    # stage 0: plan
    fig, ax = plt.subplots(figsize=(6.2, 7.2), dpi=150, facecolor=SURF)
    rank = {h: i / (len(P["axe"]) - 1) for i, h in enumerate(P["axe"])}
    banks = {b for (x, s_), b in P["bank"].items() if b != x}
    col = {h: GREY for h in sel}
    col.update({h: FAINT for h in P["river"]})
    col.update({b: "#9fd8bf" for b in banks})
    col.update({h: SEQ(rank[h]) for h in P["axe"]})
    frame(ax, col, "Giai đoạn 0 — kế hoạch trước giờ bay\nAxe (đỏ, đậm dần theo thứ tự phát), River (xanh nhạt), "
                   "Bank (xanh lá)\nvòng tròn: critical cell; viền màu: Circle của nó")
    for k in crits:
        for m, G, src in P["circle"][k]:
            ax.add_patch(plt.Polygon(corners(*c[m], R * .82), fill=False, ec=ccol[k], lw=1.6, zorder=4))
        ax.scatter(*c[k], s=120, marker="*" if k == P["ch"] else "o", color=ccol[k], edgecolors=INK, lw=.7, zorder=7)
    ax.legend(handles=[Patch(color=ccol[k], label=cname[k] + (" CH" if k == P["ch"] else "")) for k in crits],
              loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=7.5, frameon=False, labelcolor=INK2)
    save(fig, "river-plan.png")

    # stage 1: after the pass (run 1)
    r1 = {(int(r["q"]), int(r["r"])): r for r in csv.DictReader(open(os.path.join(D, "river-r1-r1-river.csv")))}
    Dn = int(crit[0]["D"])
    fig, axs = plt.subplots(1, 2, figsize=(12, 7), dpi=150, facecolor=SURF)
    frame(axs[0], {h: RAMP(int(r1[h]["clHeld0"]) / Dn) for h in sel},
          f"Giai đoạn 1 — ngay sau lượt bay (lượt 1)\nphần của D (|D| = {Dn} gói) mà CL tự nhận được")
    bar(axs[0], RAMP, 0, 1, "tỉ lệ của D")
    frame(axs[1], {h: RAMP(int(r1[h]["cellHeld"]) / Dn) for h in sel},
          "… mà cả cell nhận được (gộp mọi node)\nsau khi gom về CL (quy ước 1), CL có đúng phần này")
    bar(axs[1], RAMP, 0, 1, "tỉ lệ của D")
    for ax in axs:
        for k in crits:
            ax.scatter(*c[k], s=90, marker="*" if k == P["ch"] else "o", color="#ffffff", edgecolors=INK, lw=1, zorder=7)
    save(fig, "river-pass.png")

    # stages 2-4: load per cell medium
    cl_load = {s: {h: 0.0 for h in sel} for s in ("river", "direct")}
    for r in load_:
        if r["kind"] == "cell":
            cl_load[r["scheme"]][(int(r["a_q"]), int(r["a_r"]))] += int(r["frames"]) / nrun
    hi = max(max(v.values()) for v in cl_load.values())
    fig, axs = plt.subplots(1, 2, figsize=(12, 7), dpi=150, facecolor=SURF)
    for ax, s, t in zip(axs, ("river", "direct"), ("River (Thuật toán 5–7)", "Kéo thẳng (so sánh)")):
        frame(ax, {h: HEAT(cl_load[s][h] / hi) for h in sel},
              f"Giai đoạn 2–4 — số khung trên môi trường của mỗi cell\n{t}, TB {nrun} lượt bay; "
              f"tổng {sum(cl_load[s].values()) / 1000:.0f} k khung trong cell")
        for k in crits:
            ax.scatter(*c[k], s=90, marker="*" if k == P["ch"] else "o", color="#ffffff", edgecolors=INK, lw=1, zorder=7)
    sm = plt.cm.ScalarMappable(cmap=HEAT, norm=plt.Normalize(0, hi))
    cb = fig.colorbar(sm, ax=list(axs), shrink=.6, pad=.01)
    cb.ax.tick_params(labelsize=7, colors=INK2); cb.outline.set_visible(False)
    cb.set_label("khung / lượt bay", fontsize=8, color=INK2)
    save(fig, "river-load.png")

    # stage 4: timeline (run 1)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8), dpi=150, facecolor=SURF, sharey=True)
    for ax, s, t in zip(axs, ("river", "direct"), ("River", "Kéo thẳng")):
        tr = list(csv.DictReader(open(os.path.join(D, f"river-r1-trace-{s}.csv"))))
        for k in crits:
            pts = [(float(r["t"]), int(r["held"]) / Dn) for r in tr if (int(r["q"]), int(r["r"])) == k]
            ax.step([p[0] for p in pts], [p[1] for p in pts], where="post", color=ccol[k], lw=1.5,
                    label=cname[k] + (" CH" if k == P["ch"] else ""))
        ax.set_title(f"Giai đoạn 4 — phần D mà CL của từng critical cell có theo thời gian (lượt 1)\n{t}",
                     loc="left", fontsize=9.5, color=INK)
        ax.set_xlabel("thời gian sau khi UAV rời cụm, s", fontsize=8.5, color=INK2)
        ax.grid(color="#e6e5e1", lw=.6); ax.set_facecolor(SURF); ax.tick_params(colors=INK2, labelsize=8)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axs[0].set_ylabel("tỉ lệ của D", fontsize=8.5, color=INK2)
    axs[1].legend(frameon=False, fontsize=7.5, labelcolor=INK2, loc="lower right")
    save(fig, "river-timeline.png")

    # all runs: completion time per critical cell
    fig, ax = plt.subplots(figsize=(12, 4.8), dpi=150, facecolor=SURF)
    x = np.arange(len(crits))
    for off, s, colr, t in ((-.18, "river", RIVER, "River"), (.18, "direct", DIRECT, "Kéo thẳng")):
        vals = [[float(r["doneS"]) for r in crit if r["scheme"] == s and (int(r["q"]), int(r["r"])) == k
                 and r["doneS"] != "nan"] for k in crits]
        bp = ax.boxplot(vals, positions=x + off, widths=.3, patch_artist=True, showfliers=True,
                        medianprops=dict(color=INK), flierprops=dict(marker=".", ms=3, mec=colr))
        for b in bp["boxes"]:
            b.set_facecolor(colr); b.set_alpha(.75); b.set_edgecolor(colr)
        ax.plot([], [], color=colr, lw=8, alpha=.75, label=t)
    gat = [[float(r["gatherDoneS"]) for r in crit if r["scheme"] == "river" and (int(r["q"]), int(r["r"])) == k]
           for k in crits]
    ax.scatter(x, [S.median(g) for g in gat], marker="_", s=500, color=INK, zorder=5,
               label="xong gom trong cell (trung vị)")
    ax.set_xticks(x)
    ax.set_xticklabels([cname[k] + (" CH" if k == P["ch"] else "") + ("\nRiver" if k in P["river"] else "")
                        for k in crits], fontsize=8, color=INK)
    ax.set_ylabel("thời gian tới khi CL có đủ D, s", fontsize=8.5, color=INK2)
    ax.set_yscale("log")
    ax.set_title(f"Thời gian hoàn tất của từng critical cell qua {nrun} lượt bay", loc="left", fontsize=10,
                 color=INK)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2)
    ax.grid(axis="y", color="#e6e5e1", lw=.6); ax.set_facecolor(SURF); ax.tick_params(colors=INK2, labelsize=8)
    for sp in ax.spines.values():
        sp.set_visible(False)
    save(fig, "river-done.png")

    # tables
    print(f"\n{nrun} runs; per critical cell, median (p90) [s]:")
    print(f"{'cell':>10} {'river':>6} {'lackCL':>7} {'lackCell':>8} {'gather':>14} {'River':>16} {'direct':>16} "
          f"{'R<D':>6}")
    for k in crits:
        rr = [r for r in crit if (int(r["q"]), int(r["r"])) == k]
        gR = [float(r["gatherDoneS"]) for r in rr if r["scheme"] == "river"]
        dR = {r["run"]: float(r["doneS"]) for r in rr if r["scheme"] == "river"}
        dD = {r["run"]: float(r["doneS"]) for r in rr if r["scheme"] == "direct"}
        wins = sum(dR[x_] < dD[x_] for x_ in dR if x_ in dD)
        f = lambda v: f"{S.median(v):6.1f} ({np.percentile(v, 90):6.1f})"
        print(f"{cname[k]:>10} {int(k in P['river']):>6} {S.median(int(r['lackCL']) for r in rr):7.0f} "
              f"{S.median(int(r['lackCell']) for r in rr):8.0f} {f(gR):>14} {f(list(dR.values())):>16} "
              f"{f(list(dD.values())):>16} {wins:>3}/{len(dR)}")
    for s in ("river", "direct"):
        rr = [r for r in runs if r["scheme"] == s]
        m = lambda k: S.mean(int(r[k]) for r in rr)
        print(f"{s:>7}: frames/run {m('frames'):.0f} = gather {m('gather'):.0f} + bankfill {m('bankfill'):.0f} + "
              f"circlefill {m('circlefill'):.0f} + pull {m('pull'):.0f} + control {m('control'):.0f}; "
              f"last critical done median {S.median(float(r['lastCritS']) for r in rr):.1f} s")
    miss = sum(int(r["missing"]) for r in crit)
    print(f"missing packets at the end, all runs and cells: {miss}")


if __name__ == "__main__":
    main()
