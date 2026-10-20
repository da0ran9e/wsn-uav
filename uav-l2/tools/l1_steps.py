"""Step-by-step figure of one mission with the layer-1 model, from l1_anim.py's export (CLAUDE.md §8 item 114);
no text (item 63).

    python3 tools/l1_steps.py --json docs/anim/l1.json --out docs/figures/l1-steps.png

Panels (left to right, top to bottom):
  1 clusters (pale colours), CH (star), critical cells (rings), flight lines (black) and team 1's tour (dashed)
  2 just after the pass: each cell shaded by the share of its cluster's clue window it heard; around each critical
    cell its 12 clues in broadcast order (face red, body blue, part amber; grey: not held)
  3 after River: the clue rings again (every clue the cell holds at the end), River cells light blue
  4 layer 1: critical cells coloured by their verified score (light -> dark blue), c* red
  5 what the BS knows when team 2 leaves: discs sized by P(c*) of the reported cells
  6 phase 2: team 2's path until c* is verified (dashed: staging while waiting, solid: flights), verified cells
    grey, c* red
  7 (bottom row) timeline: team 1 (grey), each cluster's pass (blue) and River (green), reports at the BS (dots:
    light own reception, dark River; big: c*), team 2 (red flights, grey staging, black verifications, red c*)
"""
import argparse, json, math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from map_gen import strip_text
from mission_report import GREY, INK, INK2, SURF

ASP = ["#d6403a", "#1d5fa8", "#e0a019"]
CAT = ["#3b82d6", "#2f9e6e", "#e0a019", "#8a59cf", "#0e3d6e", "#c45a7a", "#5b6863", "#d6403a"]


def hexpoly(x, y, R=100, s=0.96):
    return [(x + R * s * math.cos(math.radians(30 + 60 * i)), y + R * s * math.sin(math.radians(30 + 60 * i))) for i in range(6)]


def base(ax, D, colours):
    cells = D["cells"]
    ax.add_collection(PolyCollection([hexpoly(c[0], c[1]) for c in cells], facecolors=colours, edgecolors=SURF,
                                     linewidths=.3, zorder=0))
    ax.scatter(*D["bs"], s=80, marker="s", color=INK, zorder=8)
    xs = [c[0] for c in cells] + [D["bs"][0]]
    ys = [c[1] for c in cells] + [D["bs"][1]]
    cx, cy, half = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 150
    ax.set_xlim(cx - half, cx + half); ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal"); ax.axis("off")
    ax.plot([cx + half - 1150, cx + half - 150], [cy - half + 60] * 2, color=INK, lw=2)


def clue_ring(ax, x, y, has, order, clue, r=80):
    n = len(order)
    for i, j in enumerate(order):
        a0 = 90 - 360 * (i + 1) / n + 4
        ax.add_patch(matplotlib.patches.Arc((x, y), 2 * r, 2 * r, theta1=a0, theta2=a0 + 360 / n - 8,
                                            color=ASP[clue[j][0]] if has[j] else GREY, lw=2.2, zorder=6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    D = json.load(open(a.json))
    cells, CL = D["cells"], D["clusters"]
    land = lambda c: "#dbe9f8" if c[2] else "#e6e5e1"
    crit = {int(c): dict(v, k=int(k)) for k, cl in CL.items() for c, v in cl["crit"].items()}
    for c in crit:
        crit[c].update(D["crit"][str(c)])
    fig = plt.figure(figsize=(18, 15), dpi=130, facecolor=SURF)
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 0.42])
    axs = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(6)]
    # 1 clusters, roles, lines, tour
    ax = axs[0]
    base(ax, D, [land(c) if c[2] or not c[3] else matplotlib.colors.to_rgba(CAT[(c[3] - 1) % 8], .3) for c in cells])
    pos = D["bs"]
    for l in D["legs"]:
        ax.plot([pos[0], l[1][0]], [pos[1], l[1][1]], color=INK2, lw=.9, ls=(0, (3, 2)), zorder=4)
        p = np.array(CL[str(l[0])]["path"])
        ax.plot(*p.T, color=INK, lw=1.8, zorder=5)
        pos = l[2]
    ax.plot([pos[0], D["bs"][0]], [pos[1], D["bs"][1]], color=INK2, lw=.9, ls=(0, (3, 2)), zorder=4)
    for c in crit:
        ax.scatter(cells[c][0], cells[c][1], s=55, facecolor=SURF, edgecolor=INK, lw=1.1, zorder=6)
    for k, cl in CL.items():
        ax.scatter(*cl["ch"], s=170, marker="*", color=SURF, edgecolor=INK, lw=1, zorder=7)
    # 2 after the pass
    ax = axs[1]
    share = {int(c): v[-1] for cl in CL.values() for c, v in cl["passShare"].items()}
    ramp = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#f1f0eb", "#86b6ef", "#1d5fa8"])
    base(ax, D, [land(c) if c[2] or i not in share else ramp(share[i]) for i, c in enumerate(cells)])
    for c, v in crit.items():
        clue_ring(ax, cells[c][0], cells[c][1], v["direct"], D["order"], D["clue"])
    # 3 after River
    ax = axs[2]
    riv = {i for cl in CL.values() for i in cl["river"]}
    base(ax, D, [land(c) if c[2] else ("#c9dcf3" if i in riv else "#e6e5e1") for i, c in enumerate(cells)])
    for c, v in crit.items():
        has = [bool(d) or r >= 0 for d, r in zip(v["direct"], v["riverAt"])]
        clue_ring(ax, cells[c][0], cells[c][1], has, D["order"], D["clue"])
    # 4 verified scores
    ax = axs[3]
    base(ax, D, [land(c) for c in cells])
    U = np.array([v["U"] for v in crit.values()])
    blues = matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#cde2fb", "#3987e5", "#0d366b"])
    for c, v in crit.items():
        star = c == D["star"]
        ax.scatter(cells[c][0], cells[c][1], s=200 if star else 90, color="#d6403a" if star else blues((v["U"] - U.min()) / (U.max() - U.min())),
                   edgecolor=INK, lw=.8, zorder=6)
    # 5 the BS at team 2's departure
    ax = axs[4]
    base(ax, D, [land(c) for c in cells])
    snap = next((p for t, p in D["psnap"] if t >= D["dep"] - 1e-6), D["psnap"][0][1])
    for c, v in crit.items():
        known = any(r[0] <= D["dep"] + 1e-6 for r in v["reports"])
        pc = snap.get(str(c))
        if known and pc is not None:
            ax.scatter(cells[c][0], cells[c][1], s=30 + 2500 * pc, color="#e09a1c", alpha=.8, edgecolor=INK, lw=.6, zorder=6)
        else:
            ax.scatter(cells[c][0], cells[c][1], s=30, facecolor=SURF, edgecolor=INK2, lw=.8, zorder=6)
    # 6 phase 2
    ax = axs[5]
    base(ax, D, [land(c) for c in cells])
    for m in D["team2"]:
        if m[1] >= D["Tstar"] - 1e-6 or m[0] == "verify":
            continue
        ax.plot([m[3][0], m[4][0]], [m[3][1], m[4][1]], color="#d6403a", lw=2,
                ls=(0, (3, 2)) if m[0] == "stage" else "-", zorder=6)
    done = [m[5] for m in D["team2"] if m[0] == "verify" and m[2] <= D["Tstar"] + 1e-6]
    for c in crit:
        if c in done:
            ax.scatter(cells[c][0], cells[c][1], s=220 if c == D["star"] else 90, color="#d6403a" if c == D["star"] else INK2,
                       edgecolor=INK, lw=.8, zorder=7)
        else:
            ax.scatter(cells[c][0], cells[c][1], s=30, facecolor=SURF, edgecolor=INK2, lw=.8, zorder=6)
    # 7 timeline
    ax = fig.add_subplot(gs[2, :])
    T = D["Tstar"] + 120
    legs = D["legs"]
    ax.barh(0, D["back"], left=0, height=.35, color=GREY)
    for i, l in enumerate(legs):
        cl = CL[str(l[0])]
        y = -(i + 1)
        last = max(v["doneS"] for v in cl["crit"].values())
        ax.barh(y, l[4] - l[3], left=l[3], height=.6, color="#1d5fa8")
        ax.barh(y, last, left=l[4], height=.3, color="#3aa37a")
        for c, v in cl["crit"].items():
            for r in D["crit"][c]["reports"]:
                big = int(c) == D["star"]
                ax.scatter(r[0], y, s=60 if big else 14, color="#d6403a" if big else (INK if r[1] else INK2),
                           alpha=1 if r[1] else .45, zorder=4)
    y = -(len(legs) + 1)
    for m in D["team2"]:
        if m[1] > T:
            continue
        colr = {"fly": "#f3b9b9", "stage": INK2, "back": "#f3b9b9"}.get(m[0], "#d6403a" if m[5] == D["star"] else INK)
        ax.barh(y, min(m[2], T) - m[1], left=m[1], height=.6 if m[0] == "verify" else .3, color=colr)
    ax.axvline(D["Tstar"], color="#d6403a", lw=1.5, ls=(0, (3, 2)))
    ax.set_xlim(0, T)
    ax.set_xticks(np.arange(0, T, 60))
    ax.grid(axis="x", color=GREY, lw=.6)
    ax.set_axisbelow(True)
    ax.set_yticks([])
    ax.set_facecolor(SURF)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(a.out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
    plt.close(fig)


if __name__ == "__main__":
    main()
