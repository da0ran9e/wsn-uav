"""Scenario comparison figures for the base manifest phase.

    python3 tools/scenario_figures.py DATA FIGS LABEL|CELLS.csv|MISSIONS.csv|PATH.csv ...

DATA holds deploy-lattice.csv and deploy-nodes-s35.csv; each scenario gives the
uav-coop-manifest cells/missions CSVs and the flight path it was flown on. Draws
  scenarios-maps.png     per scenario: how much each cell lacks before / after the phase,
                         and chunks held by no important node
  scenarios-summary.png  the key numbers side by side
"""
import csv, math, os, statistics as S, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection, LineCollection
import numpy as np

INK, INK2, SURF, GRIDC = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]
LACK = matplotlib.colors.LinearSegmentedColormap.from_list("l", ["#f1f0eb", "#f6c3c3", "#e34948", "#8f1d1b"])
KEEP = matplotlib.colors.LinearSegmentedColormap.from_list("k", ["#f1f0eb", "#86b6ef", "#3987e5", "#0d366b"])


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def main():
    data, figs = sys.argv[1], sys.argv[2]
    scen = [a.split("|") for a in sys.argv[3:]]
    lat = list(csv.DictReader(open(os.path.join(data, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    chn = next(r for r in csv.DictReader(open(os.path.join(data, "deploy-nodes-s35.csv"))) if r["isCH"] == "1")
    segs = []
    for q, r in sel:
        v = corners(*c[(q, r)], R)
        for k, (dq, dr) in enumerate(EDGE_NB):
            if (q + dq, r + dr) not in sel:
                segs.append([v[k], v[(k + 1) % 6]])
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]

    def draw(a, val, vmax, cmap, title, path, label=None):
        norm = matplotlib.colors.Normalize(0, max(vmax, 1e-9))
        a.add_collection(PolyCollection([corners(*c[h], R) for h in sel],
                                        facecolors=[cmap(norm(val[h])) for h in sel], edgecolors="#ffffff",
                                        linewidths=.6, zorder=1))
        a.add_collection(LineCollection(segs, colors=INK2, linewidths=.9, zorder=2))
        if path:
            P = list(csv.DictReader(open(path)))
            a.plot([float(p["x"]) for p in P], [float(p["y"]) for p in P], color=INK, lw=1, alpha=.7, zorder=3)
        if label:
            for h in sel:
                if label[h]:
                    a.text(c[h][0], c[h][1], label[h], fontsize=5.5, ha="center", va="center", color=INK, zorder=4)
        a.scatter([float(chn["x"])], [float(chn["y"])], s=90, marker="*", color="#e34948", edgecolors=INK,
                  linewidths=.6, zorder=5)
        a.set_xlim(min(xs) - w, max(xs) + w); a.set_ylim(min(ys) - w, max(ys) + w)
        a.set_aspect("equal"); a.set_facecolor(SURF)
        a.set_xticks([]); a.set_yticks([])
        for sp in a.spines.values():
            sp.set_visible(False)
        a.set_title(title, loc="left", fontsize=9, color=INK)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cb = plt.colorbar(sm, ax=a, shrink=.7, pad=.01)
        cb.ax.tick_params(labelsize=6.5, colors=INK2); cb.outline.set_visible(False)

    n = len(scen)
    fig, ax = plt.subplots(3, n, figsize=(3.9 * n, 13.5), dpi=150, facecolor=SURF)
    rows = []
    for j, (label, cells_csv, miss_csv, path) in enumerate(scen):
        cells = list(csv.DictReader(open(cells_csv)))
        miss = list(csv.DictReader(open(miss_csv)))
        nrun = len(miss)
        b = {h: 0.0 for h in sel}; a_ = {h: 0.0 for h in sel}; kg = {h: 0.0 for h in sel}; often = {h: 0 for h in sel}
        for r in cells:
            h = (int(r["q"]), int(r["r"]))
            b[h] += int(r["lacks0"]) / nrun
            a_[h] += int(r["lacksEnd"]) / nrun
            kg[h] += int(r["keepGapEnd"]) / nrun
            often[h] += int(r["lacks0"]) > 0
        vmax = max(b.values())
        draw(ax[0, j], b, vmax, LACK, f"{label}\nTRƯỚC: mảnh cell thiếu (TB)\nnhãn: % lượt bay cell đó thiếu",
             path, {h: (f"{100 * often[h] / nrun:.0f}" if often[h] else "") for h in sel})
        draw(ax[1, j], a_, vmax, LACK, f"SAU pha cơ sở: mảnh cell còn thiếu (TB)\n"
             f"{sum(int(r['lacksEnd']) > 0 for r in cells) / nrun:.1f} cell / lượt bay", path,
             {h: (f"{a_[h]:.0f}" if a_[h] >= .5 else "") for h in sel})
        draw(ax[2, j], kg, max(max(kg.values()), 1), KEEP, "mảnh cell có nhưng KHÔNG node quan trọng\n"
             "nào giữ (TB, sau pha cơ sở)", path, {h: (f"{kg[h]:.0f}" if kg[h] >= .5 else "") for h in sel})
        lack = [r for r in cells if int(r["lacks0"]) > 0]
        late = [float(r["fullS"]) - float(r["readyS"]) for r in lack if float(r["fullS"]) >= 0]
        rows.append({"label": label, "before": len(lack) / nrun,
                     "after": sum(int(r["lacksEnd"]) > 0 for r in cells) / nrun,
                     "latMed": S.median(late) if late else 0, "latP90": np.percentile(late, 90) if late else 0,
                     "perMan": sum(int(r["forwarded"]) for r in cells) / max(1, sum(int(r["manifests"]) for r in cells)),
                     "toCH": sum(int(m["toCH"]) for m in miss) / nrun,
                     "keep": sum(int(r["keepGapEnd"]) > 0 for r in cells) / nrun})
    fig.suptitle("Pha manifest cơ sở qua các kịch bản (mỗi cột 120 lượt bay; nét đen: đường bay; sao: CH)",
                 x=.01, ha="left", fontsize=12.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, .96))
    out = os.path.join(figs, "scenarios-maps.png")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")

    fig, ax = plt.subplots(1, 3, figsize=(17, 5), dpi=150, facecolor=SURF)
    x = np.arange(n)
    labs = [r["label"] for r in rows]
    a = ax[0]
    a.bar(x - .2, [r["before"] for r in rows], .4, color="#f6c3c3", label="cell thiếu trước")
    a.bar(x + .2, [r["after"] for r in rows], .4, color="#e34948", label="còn thiếu sau pha cơ sở")
    a.bar(x + .2, [r["keep"] for r in rows], .12, color="#2a78d6", label="cell có mảnh không ở node quan trọng")
    a.set_title("Số cell mỗi lượt bay (/109)", loc="left", fontsize=10.5, color=INK)
    a = ax[1]
    a.bar(x, [r["latMed"] for r in rows], .5, color="#1baf7a", label="trung vị")
    a.scatter(x, [r["latP90"] for r in rows], marker="_", s=400, color=INK, label="p90", zorder=3)
    a.set_title("Từ lúc cell sẵn sàng tới khi đủ, s (cận dưới lạc quan)", loc="left", fontsize=10.5, color=INK)
    a = ax[2]
    a.bar(x - .2, [r["perMan"] for r in rows], .4, color="#eda100", label="số cell mỗi manifest đi qua")
    a.bar(x + .2, [r["toCH"] for r in rows], .4, color="#52514e", label="manifest tới CH mà còn thiếu, mỗi lượt bay")
    a.set_title("Manifest đi xa tới đâu", loc="left", fontsize=10.5, color=INK)
    for a in ax:
        a.set_xticks(x); a.set_xticklabels(labs, fontsize=8.5, color=INK)
        a.legend(frameon=False, fontsize=8.5, labelcolor=INK2)
        a.grid(axis="y", color=GRIDC, lw=.6); a.set_facecolor(SURF)
        a.tick_params(colors=INK2, labelsize=8)
        for sp in a.spines.values():
            sp.set_visible(False)
    fig.tight_layout()
    out = os.path.join(figs, "scenarios-summary.png")
    fig.savefig(out, facecolor=SURF)
    print(f"  {out}")


if __name__ == "__main__":
    main()
