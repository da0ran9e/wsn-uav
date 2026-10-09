"""Concept sketches of the River idea, drawn on the real deployment and base path, no text.

    python3 tools/concept_figures.py --deploy ../uav-coop/docs/data --data docs/data --figs docs/figures

  concept-river.png    River: nodes likely to hold at least one whole file (P >= --river)
  concept-axe.png      Axe: the nodes the UAV flies right over (within --axe m of the track)
  concept-banks.png    Banks: the River's two edges, one colour per side of the track
  concept-critical.png critical cells (outstanding CLs and the CH) fed from the River
  concept-circle.png   the Circle around one critical cell: 6 neighbours, 12, shifted to the River;
                       each serving cell's colour = its share of what the critical cell lacks
"""
import argparse, csv, math, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch, Wedge
import numpy as np

SURF, INK, GREY, FAINT = "#fcfcfb", "#0b0b0b", "#d9d8d3", "#c9dcf3"
RIVER, AXE, BANK_L, BANK_R = "#3987e5", "#0d366b", "#1baf7a", "#eda100"
CRIT, CELL = "#e34948", "#f1f0eb"
SHARE = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8e5ad6",
         "#1c5cab", "#86b6ef", "#0e7d57", "#b77a00", "#8f1d1b", "#c3a6ee"]
NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def ring(h, k):
    """Hex cells exactly k steps from h."""
    if k == 0:
        return [h]
    out, q, r = [], h[0] + NB[4][0] * k, h[1] + NB[4][1] * k
    for side in range(6):
        for _ in range(k):
            out.append((q, r))
            q, r = q + NB[side][0], r + NB[side][1]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--river", type=float, default=0.1, help="P(whole file of 1000) to be River")
    ap.add_argument("--axe", type=float, default=30.0, help="Axe: within this many m of the track")
    ap.add_argument("--link", type=float, default=50.0, help="G2G link range, m")
    ap.add_argument("--critical", type=float, default=2.0, help="critical CL: strength > mean + this x sd")
    a = ap.parse_args()

    lat = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    S = set(sel)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S]
    nodes = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-nodes-s35.csv"))))
    xy = np.array([[float(r["x"]), float(r["y"])] for r in nodes])
    cell = [(int(r["q"]), int(r["r"])) for r in nodes]
    runs = {r["id"]: r for r in csv.DictReader(open(os.path.join(a.data, "runs-nodes.csv")))
            if r["path"].startswith("cơ sở")}
    assert len(runs) == len(nodes)
    p = np.array([float(runs[r["id"]]["p1000"]) for r in nodes])
    d = np.array([float(runs[r["id"]]["dPathM"]) for r in nodes])
    P = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(os.path.join(a.data, "path-base.csv")))])
    river = p >= a.river
    axe = d <= a.axe
    # Banks: River nodes with a non-River node within link range; side = which side of the track
    D2 = ((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1)
    nb = D2 <= a.link ** 2
    bank = river & (nb & ~river[None, :]).any(1)
    k = ((xy[:, None, :] - P[None, :, :]) ** 2).sum(-1).argmin(1)
    k = np.clip(k, 0, len(P) - 2)
    t = P[k + 1] - P[k]
    side = np.sign(t[:, 0] * (xy[:, 1] - P[k, 1]) - t[:, 1] * (xy[:, 0] - P[k, 0]))
    # Critical cells: outstanding CLs, plus the CH's cell
    sc = {cell[i]: float(nodes[i]["score"]) for i in range(len(nodes)) if nodes[i]["isCL"] == "1"}
    m, s = np.mean(list(sc.values())), np.std(list(sc.values()))
    chi = next(i for i, r in enumerate(nodes) if r["isCH"] == "1")
    crit = sorted({h for h, v in sc.items() if v > m + a.critical * s} | {cell[chi]})
    clpos = {cell[i]: xy[i] for i in range(len(nodes)) if nodes[i]["isCL"] == "1"}
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]

    def base(ax, cells=True, colours=None):
        if cells:
            ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel],
                                             facecolors=[(colours or {}).get(h, CELL) for h in sel],
                                             edgecolors="#ffffff", linewidths=.7, zorder=0))
        ax.add_collection(LineCollection(segs, colors="#52514e", linewidths=.9, zorder=1))
        ax.set_xlim(min(xs) - w, max(xs) + w); ax.set_ylim(min(ys) - w, max(ys) + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def track(ax, alpha=.85):
        ax.plot(P[:, 0], P[:, 1], color=INK, lw=1.2, alpha=alpha, zorder=6)
        ax.add_patch(FancyArrowPatch(P[-30], P[-1], arrowstyle="-|>", mutation_scale=12, color=INK,
                                     alpha=alpha, zorder=6))

    def save(fig, name):
        out = os.path.join(a.figs, name)
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
        plt.close(fig)
        print(f"  {out}")

    # 1. River
    fig, ax = plt.subplots(figsize=(6, 7), dpi=150, facecolor=SURF)
    base(ax)
    ax.scatter(*xy[~river].T, s=5, color=GREY, lw=0, zorder=2)
    ax.scatter(*xy[river].T, s=9, color=RIVER, lw=0, zorder=3)
    track(ax)
    save(fig, "concept-river.png")
    # 2. Axe
    fig, ax = plt.subplots(figsize=(6, 7), dpi=150, facecolor=SURF)
    base(ax)
    ax.scatter(*xy[~river].T, s=5, color=GREY, lw=0, zorder=2)
    ax.scatter(*xy[river & ~axe].T, s=8, color=FAINT, lw=0, zorder=3)
    ax.scatter(*xy[axe].T, s=14, color=AXE, lw=0, zorder=4)
    track(ax, .5)
    save(fig, "concept-axe.png")
    # 3. Banks
    fig, ax = plt.subplots(figsize=(6, 7), dpi=150, facecolor=SURF)
    base(ax)
    ax.scatter(*xy[~river].T, s=5, color=GREY, lw=0, zorder=2)
    ax.scatter(*xy[river & ~bank].T, s=8, color=FAINT, lw=0, zorder=3)
    ax.scatter(*xy[bank & (side > 0)].T, s=14, color=BANK_L, lw=0, zorder=4)
    ax.scatter(*xy[bank & (side <= 0)].T, s=14, color=BANK_R, lw=0, zorder=4)
    track(ax, .5)
    save(fig, "concept-banks.png")
    # 4. Critical cells fed from the River (each from its nearest Bank node)
    fig, ax = plt.subplots(figsize=(6, 7), dpi=150, facecolor=SURF)
    base(ax, colours={h: "#f6c3c3" for h in crit})
    ax.scatter(*xy[~river].T, s=4, color=GREY, lw=0, zorder=2)
    ax.scatter(*xy[river].T, s=7, color=FAINT, lw=0, zorder=3)
    bi = np.flatnonzero(bank)
    for h in crit:
        tgt = clpos[h]
        src = xy[bi[((xy[bi] - tgt) ** 2).sum(1).argmin()]]
        if math.dist(src, tgt) > 30:
            ax.add_patch(FancyArrowPatch(src, tgt, arrowstyle="-|>", mutation_scale=14, color=RIVER,
                                         lw=1.6, connectionstyle="arc3,rad=.15", zorder=5))
        ax.scatter(*tgt, s=70, color=CRIT, edgecolors=INK, lw=.6, zorder=7,
                   marker="*" if h == cell[chi] else "o")
    track(ax, .35)
    save(fig, "concept-critical.png")
    # 5. Circle: an example critical cell off the River with both rings inside the cluster
    #    (the one with the strongest CL)
    rcells = {cell[i] for i in np.flatnonzero(river)}
    whole = [h for h in sel if h not in rcells and all(g in S for g in ring(h, 1) + ring(h, 2))]
    far = max(whole, key=lambda h: sc.get(h, 0))
    rv = xy[river].mean(0) if river.any() else np.array(c[far])
    toward = np.array(rv) - np.array(c[far])
    r1 = [h for h in ring(far, 1) if h in S]
    r2 = [h for h in ring(far, 2) if h in S]
    # shifted: the 6 cells of rings 1-2 nearest the River
    sh = sorted(r1 + r2, key=lambda h: math.dist(c[h], rv))[:6]
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.6), dpi=150, facecolor=SURF)
    for ax, serve in zip(axs, [r1, r2, sh]):
        cols = {h: SHARE[j % len(SHARE)] for j, h in enumerate(serve)}
        relay = {min(r1, key=lambda x: math.dist(c[x], c[h])) for h in serve if h not in r1} - set(serve)
        cols.update({h: FAINT for h in relay})
        cols[far] = "#ffffff"
        base(ax, colours=cols)
        ax.scatter(*xy[river].T, s=5, color=FAINT, lw=0, zorder=2)
        cx, cy = c[far]
        # the critical cell's missing data, split into one share per serving cell
        n = len(serve)
        for j in range(n):
            ax.add_patch(Wedge((cx, cy), R * .62, 90 + 360 * j / n, 90 + 360 * (j + 1) / n,
                               facecolor=cols[serve[j]], edgecolor="#ffffff", lw=.8, zorder=4))
        def arrow(h, g, cut):
            v = np.array(c[g]) - np.array(c[h])
            L = np.linalg.norm(v)
            ax.add_patch(FancyArrowPatch(np.array(c[h]) + v / L * R * .35, np.array(c[g]) - v / L * R * cut,
                                         arrowstyle="-|>", mutation_scale=11, color=INK, lw=1, zorder=5))
        for h in serve:
            if h in r1:
                arrow(h, far, .7)
            else:   # not adjacent: in through the nearest ring-1 cell (one gateway per cell pair)
                g = min(r1, key=lambda x: math.dist(c[x], c[h]))
                arrow(h, g, .35)
                if g not in serve:
                    arrow(g, far, .7)
        ax.scatter(*clpos[far], s=90, color=CRIT, edgecolors=INK, lw=.7, zorder=7)
        span = 3.4 * w
        ax.set_xlim(cx - span, cx + span); ax.set_ylim(cy - span, cy + span)
    save(fig, "concept-circle.png")
    print(f"River {river.sum()}, Axe {axe.sum()}, Banks {bank.sum()} ({(bank & (side > 0)).sum()} / "
          f"{(bank & (side <= 0)).sum()}), critical cells {len(crit)}: {crit}; circle around {far}, "
          f"toward River {toward.round(0)}")


if __name__ == "__main__":
    main()
