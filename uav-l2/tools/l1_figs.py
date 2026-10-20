"""Figures of the layer-1 model (CLAUDE.md §8 items 110-114; paper/L1-MODEL-vi.md), no text (item 63).

    python3 tools/l1_figs.py --figs docs/figures

FIGS/l1-model.png, four panels:
  a  the clue stream, one copy: each clue a block, width = its packets, height = its importance, colour = its
     aspect (face red, body blue, part amber), shade = its recognizability (darker = closer to 1); top row grouped
     by aspect, bottom row interleaved; the grey band under each row is the first half of the stream (what a cell
     that heard only half of it holds)
  b  3 200 simulated cells: phase-1 score (x) against verified score (y), every clue held (dark) and the second
     half of a grouped stream held (amber)
  c  the share of maps (32 critical cells each) whose phase-1 top cell is c*, for: every clue; first, second half
     of the interleaved stream (light blue); first, second half of the grouped stream (amber); no face clue (red);
     every clue but equal weights (grey)
  d  how often c* is the phase-1 rank 1, 2, ..., 10 or worse (every clue: dark; second half grouped: amber)
"""
import argparse, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import l1_model as L
from map_gen import strip_text
from mission_report import GREY, INK, SURF

ASP = {"face": "#e34948", "body": "#1c5cab", "part": "#eda100"}


def shade(hexc, r):
    """Mix the aspect colour with white: r = 0.80 -> light, r = 0.99 -> full."""
    c = np.array(matplotlib.colors.to_rgb(hexc))
    f = (r - 0.75) / 0.25
    return tuple(1 - f * (1 - c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    C = L.clues()
    rng = np.random.default_rng(1)
    n = 3200
    st = L.stores(rng, n)
    mv = L.matches(rng, st, C)
    U = L.verified(st, C)
    full = np.ones(len(C), bool)
    def half(kind, second):
        # the clues lying wholly in the first (or second) half of the stream, by packets
        s0, e0, Q = L.layout(C, L.order(C, kind))
        return (s0 >= Q / 2) if second else (e0 <= Q / 2)

    cases = [("full", full, C), ("half-i1", half("interleaved", 0), C), ("half-i2", half("interleaved", 1), C),
             ("half-g1", half("grouped", 0), C), ("half-g2", half("grouped", 1), C),
             ("noface", np.array([c["aspect"] != "face" for c in C]), C),
             ("parts", np.array([c["aspect"] == "part" for c in C]), C), ("equal", full, [dict(c, w=1.0) for c in C])]
    S = {k: L.report(mv, w, m) for k, m, w in cases}
    g = U.reshape(100, 32)
    top = {k: float(np.mean(g.argmax(1) == S[k].reshape(100, 32).argmax(1))) for k in S}
    rank = {k: np.array([int(np.nonzero(np.argsort(-S[k].reshape(100, 32)[i]) == g[i].argmax())[0][0]) + 1
                         for i in range(100)]) for k in S}
    for k, m, w in cases:
        print(f"{k:8s} clues {''.join(c['aspect'][0] for c, h in zip(C, m) if h):12s} corr {np.corrcoef(S[k], U)[0, 1]:.3f}"
              f" top-1 {top[k]:.2f} mean rank {rank[k].mean():.2f}")
    top = {k: v for k, v in top.items() if k in ("full", "half-i1", "half-i2", "half-g1", "half-g2", "noface", "equal")}
    fig = plt.figure(figsize=(15, 9.5), dpi=150, facecolor=SURF)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15])
    ax = fig.add_subplot(gs[0, :])
    tot = L.layout(C, L.order(C))[2]
    for row, kind in enumerate(("grouped", "interleaved")):
        y0 = 1.0 - row * 1.4
        s0, e0, _ = L.layout(C, L.order(C, kind))
        for j, c in enumerate(C):
            h = 0.12 + 0.14 * c["w"]
            ax.add_patch(plt.Rectangle((s0[j], y0), e0[j] - s0[j], h, facecolor=shade(ASP[c["aspect"]], c["r"]),
                                       edgecolor=SURF, lw=1.5))
        ax.add_patch(plt.Rectangle((0, y0 - 0.16), tot / 2, 0.08, facecolor=GREY, edgecolor="none"))
    ax.set_xlim(-30, tot + 30)
    ax.set_ylim(-0.8, 2.0)
    ax.axis("off")
    ax = fig.add_subplot(gs[1, 0])
    for k, col, z in (("half-g2", "#eda100", 2), ("full", "#1c5cab", 3)):
        ax.scatter(S[k], U, s=4, color=col, alpha=.35, lw=0, zorder=z)
    lo, hi = min(U.min(), S["full"].min()), max(U.max(), S["full"].max())
    ax.plot([lo, hi], [lo, hi], color=INK, lw=.8, ls=(0, (3, 2)), zorder=4)
    ax = fig.add_subplot(gs[1, 1])
    cols = ["#1c5cab", "#86b6ef", "#86b6ef", "#eda100", "#eda100", "#e34948", "#52514e"]
    ax.bar(range(len(top)), list(top.values()), color=cols, width=.7)
    ax.set_ylim(0, 1)
    ax = fig.add_subplot(gs[1, 2])
    for k, col, off in (("full", "#1c5cab", -0.2), ("half-g2", "#eda100", 0.2)):
        cnt = np.bincount(np.minimum(rank[k], 10), minlength=11)[1:] / len(rank[k])
        ax.bar(np.arange(1, 11) + off, cnt, width=.4, color=col)
    ax.set_ylim(0, None)
    for ax in fig.axes[1:]:
        ax.grid(axis="y", color=GREY, lw=.6)
        ax.set_axisbelow(True)
        ax.set_facecolor(SURF)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    strip_text(fig)
    fig.savefig(os.path.join(a.figs, "l1-model.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)


if __name__ == "__main__":
    main()
