"""Channel plan (7 / 3 colours) x River width (3.5 / 2.5 cells), one ns-3 mission.

    python3 tools/river_variants_figure.py --deploy ../uav-coop/docs/data --path docs/data/path-a180.csv \
        --runs PILOT --figs docs/figures

PILOT holds uav-coop2-river outputs named c{7,3}-w{3.5,2.5}-{full,ondemand}-*.csv and c{7,3}-d-*.csv.
Draws ns3-variants.png: the River at both widths, completion time per critical cell, frames per phase.
"""
import argparse, csv, math, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from river_plan import load, plan  # noqa: E402

INK, INK2, SURF, GREY, FAINT = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1", "#c9dcf3"
AXE, BANK = "#e34948", "#9fd8bf"
CONF = [("c7-w3.5", "7 màu, River 3,5", "#1c5cab", "o"), ("c7-w2.5", "7 màu, River 2,5", "#1baf7a", "o"),
        ("c3-w3.5", "3 màu, River 3,5", "#eda100", "^"), ("c3-w2.5", "3 màu, River 2,5", "#e34948", "^")]
PHASES = [("gather", "gom trong cell", "#3987e5"), ("circlefill", "Bank → Circle", "#eda100"),
          ("pull", "→ critical cell", "#e34948"), ("control", "yêu cầu", "#52514e")]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def main():
    ap = argparse.ArgumentParser()
    for k in ("deploy", "path", "runs", "figs"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    geo = load(a.deploy, a.path)
    c, w, R, sel = geo["c"], geo["w"], geo["R"], geo["cells"]
    S_ = set(sel)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S_]
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    rd = lambda f: list(csv.DictReader(open(os.path.join(a.runs, f))))

    fig = plt.figure(figsize=(17, 11), dpi=140, facecolor=SURF)
    gs = fig.add_gridspec(2, 4, height_ratios=[1.25, 1], hspace=.28, wspace=.25)
    for i, W in enumerate((3.5, 2.5)):
        ax = fig.add_subplot(gs[0, i])
        P = plan(geo, width=W)
        banks = {b for (x, s_), b in P["bank"].items() if b != x}
        col = {h: GREY for h in sel}
        col.update({h: FAINT for h in P["river"]})
        col.update({b: BANK for b in banks})
        col.update({h: AXE for h in P["axe"]})
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[col[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.7))
        ax.add_collection(LineCollection(segs, colors=INK2, linewidths=.9))
        for k in P["crit"]:
            ax.scatter(*c[k], s=90, marker="*" if k == P["ch"] else "o", color="#ffffff", edgecolors=INK, lw=1,
                       zorder=5)
        ax.set_xlim(min(xs) - w, max(xs) + w); ax.set_ylim(min(ys) - w, max(ys) + w)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"River rộng {W:.1f} cell (ω = {W / 2:.2f} cell)".replace(".", ",") + f"\n{len(P['river'])} cell River, "
                     f"Bank cách Axe ≈ {2 if W > 3 else 1} cell", loc="left", fontsize=9.5, color=INK)
    fig.axes[0].legend(
        handles=[Patch(color=AXE, label="Axe"), Patch(color=FAINT, label="River"), Patch(color=BANK, label="Bank")],
        loc="lower left", frameon=False, fontsize=8, labelcolor=INK2)

    # completion time per critical cell, River (Circle prepared)
    ax = fig.add_subplot(gs[0, 2:])
    base = rd("c7-w3.5-full-crit.csv")
    cells = [(r["q"], r["r"]) for r in base]
    for j, (cf, lab, colr, mk) in enumerate(CONF):
        rr = rd(f"{cf}-full-crit.csv")
        ax.scatter([i + (j - 1.5) * .12 for i in range(len(rr))], [float(r["doneS"]) for r in rr], s=42,
                   marker=mk, color=colr, edgecolors=SURF, lw=1, zorder=3, label=lab)
    dd = rd("c7-d-crit.csv")
    ax.scatter(range(len(dd)), [float(r["doneS"]) for r in dd], s=60, marker="_", color=INK2, lw=2, zorder=2,
               label="kéo thẳng, 7 màu")
    ax.set_xticks(range(len(cells)))
    ax.set_xticklabels([f"({q},{r_})" + (" CH" if (q, r_) == ("-3", "2") else "") for q, r_ in cells], fontsize=8,
                       color=INK)
    ax.set_ylabel("thời điểm CL có đủ D, s", fontsize=8.5, color=INK2)
    ax.set_title("Thời gian hoàn tất của từng critical cell — River, Circle chuẩn bị sẵn (lượt 1)", loc="left",
                 fontsize=9.5, color=INK)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc="upper left")

    # frames per phase
    ax = fig.add_subplot(gs[1, :])
    rows = []
    for prep, pl in (("full", "chuẩn bị sẵn"), ("ondemand", "khi được hỏi")):
        for cf, lab, _, _ in CONF:
            rows.append((f"{lab} · {pl}", rd(f"{cf}-{prep}-runs.csv")[0]))
    for cf, lab in (("c7", "7 màu"), ("c3", "3 màu")):
        rows.append((f"kéo thẳng · {lab}", rd(f"{cf}-d-runs.csv")[0]))
    for i, (lab, r) in enumerate(rows):
        left = 0
        for ph, pl_, colr in PHASES:
            v = int(r[ph]) / 1000
            ax.barh(i, v, left=left, color=colr, height=.62, edgecolor=SURF, lw=2, label=pl_ if i == 0 else None)
            left += v
        ax.text(left + .8, i, f"{left:.0f}k khung · xong lúc {float(r['simS']):.0f} s · MAC bỏ cuộc "
                              f"{int(r['macFail']) / 1000:.1f}k", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([x for x, _ in rows], fontsize=8, color=INK)
    ax.invert_yaxis(); ax.set_xlim(0, 135)
    ax.set_xlabel("khung truyền thành công (nghìn), lượt 1", fontsize=8.5, color=INK2)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2, ncol=4, loc="lower right", bbox_to_anchor=(1, 1.0))
    for x in fig.axes[2:]:
        x.grid(color=GREY, lw=.6); x.set_facecolor(SURF); x.tick_params(colors=INK2, labelsize=8)
        for sp in x.spines.values():
            sp.set_visible(False)
    out = os.path.join(a.figs, "ns3-variants.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")


if __name__ == "__main__":
    main()
