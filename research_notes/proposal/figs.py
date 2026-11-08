"""Schematic figures for the research proposal (no text, CLAUDE.md rule 63) -> docs/figures/proposal/.

    python3 research_notes/proposal/figs.py
"""
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, FancyArrowPatch, Circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../docs/figures/proposal")
R = 1.0
GREY, LIGHT, SPINE, HOLD, BANK, RING, CRIT = "#e6e6e6", "#f4f4f4", "#1f4e9c", "#e07b1a", "#7fa8e0", "#b9d3f2", "#c0392b"


def center(q, r):
    return (math.sqrt(3) * R * (q + r / 2), 1.5 * R * r)


def cells(Q, Rr):
    return [(q, r) for r in range(-Rr, Rr + 1) for q in range(-Q - (r // 2), Q - (r // 2) + 1)]


def hexa(ax, q, r, fc, ec="white", lw=1.2, z=1):
    ax.add_patch(RegularPolygon(center(q, r), 6, radius=R, orientation=0, fc=fc, ec=ec, lw=lw, zorder=z))


def arrow(ax, a, b, color, ls="-", lw=2, z=5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, color=color, lw=lw, ls=ls, zorder=z,
                                 shrinkA=6, shrinkB=6))


def nearest(x, y, cs):
    return min(cs, key=lambda c: (center(*c)[0] - x) ** 2 + (center(*c)[1] - y) ** 2)


def finish(ax, name):
    ax.set_aspect("equal"); ax.axis("off"); ax.autoscale_view()
    plt.savefig(f"{OUT}/{name}", dpi=160, bbox_inches="tight", pad_inches=0.05, facecolor="white"); plt.close()


def deviation():
    """Proposition B: planned track, flown track offset e, band w around SPINE, holders h hops away."""
    cs = cells(6, 5); fig, ax = plt.subplots(figsize=(8, 6))
    planned = lambda y: 0.15 * y
    flown = lambda y: 0.15 * y + 3.2 * math.exp(-((y - 1.0) / 2.6) ** 2)
    spine = {nearest(planned(y), y, cs) for y in [i * 0.2 for i in range(-40, 41)]}
    band = {c for c in cs if min(math.dist(center(*c), center(*s)) for s in spine) < 1.8 * R}
    holders = {nearest(flown(y), y, cs) for y in [i * 0.2 for i in range(-40, 41)]} - band
    for c in cs:
        hexa(ax, *c, SPINE if c in spine else HOLD if c in holders else BANK if c in band else GREY)
    ys = [i * 0.05 for i in range(-160, 161)]
    ax.plot([planned(y) for y in ys], ys, color="black", ls="--", lw=2, zorder=4)
    ax.plot([flown(y) for y in ys], ys, color="black", lw=2.5, zorder=4)
    a = nearest(planned(1.0), 1.0, cs); b = nearest(flown(1.0), 1.0, cs)
    arrow(ax, center(*b), center(*a), CRIT, lw=2.5)
    ax.annotate("", xy=(flown(1.0), 1.0 - 0.0), xytext=(planned(1.0), 1.0), arrowprops=dict(arrowstyle="<->", lw=1.5))
    finish(ax, "prop-b-deviation-threshold.png")


def takeover():
    """ND2: holder cell under the flown track reports to the SPINE cell (dotted), SPINE pulls data back (solid)."""
    cs = cells(5, 4); fig, ax = plt.subplots(figsize=(7, 5.5))
    planned = lambda y: -0.6 + 0.1 * y
    flown = lambda y: -0.6 + 0.1 * y + 4.6 * math.exp(-((y + 0.5) / 2.4) ** 2)
    spine = {nearest(planned(y), y, cs) for y in [i * 0.2 for i in range(-30, 31)]}
    under = {nearest(flown(y), y, cs) for y in [i * 0.2 for i in range(-30, 31)]} - spine
    crit = (-4, -3)
    for c in cs:
        fc = SPINE if c in spine else HOLD if c in under else GREY
        hexa(ax, *c, fc)
    hexa(ax, *crit, CRIT)
    ys = [i * 0.05 for i in range(-120, 121)]
    ax.plot([planned(y) for y in ys], ys, color="black", ls="--", lw=2, zorder=4)
    ax.plot([flown(y) for y in ys], ys, color="black", lw=2.5, zorder=4)
    b = max(under, key=lambda c: center(*c)[0])
    a = nearest(planned(center(*b)[1]), center(*b)[1], cs)
    pa, pb = center(*a), center(*b)
    arrow(ax, (pb[0], pb[1] + 0.45), (pa[0], pa[1] + 0.45), "black", ls=":", lw=2)
    arrow(ax, (pb[0], pb[1] - 0.45), (pa[0], pa[1] - 0.45), HOLD, lw=3)
    arrow(ax, pa, center(*crit), SPINE, lw=3)
    finish(ax, "nd2-takeover-header-report.png")


def phase0():
    """ND0: topology reports flow up to the BS, the plan flows back down to every cell before a mission."""
    cs = cells(4, 3); fig, ax = plt.subplots(figsize=(7, 5))
    for c in cs: hexa(ax, *c, LIGHT, ec="#bbbbbb")
    cls = {c: center(*c) for c in cs}
    for c, (x, y) in cls.items(): ax.add_patch(Circle((x, y), 0.18, fc="#555555", zorder=3))
    for c in cs:
        for dq, dr in [(1, 0), (0, 1), (-1, 1)]:
            n = (c[0] + dq, c[1] + dr)
            if n in cls:
                (x1, y1), (x2, y2) = cls[c], cls[n]
                ax.plot([x1 + (x2 - x1) * 0.38, x1 + (x2 - x1) * 0.62], [y1 + (y2 - y1) * 0.38, y1 + (y2 - y1) * 0.62],
                        color="black", lw=2.2, zorder=2)
    bs = (center(4, 3)[0] + 2.6, center(4, 3)[1] + 1.2)
    ax.add_patch(RegularPolygon(bs, 4, radius=0.55, fc="black", zorder=4))
    for c in [(-3, 1), (0, -2), (2, 2)]:
        arrow(ax, cls[c], bs, "#2e86c1", ls=":", lw=1.8)
    for c in [(-2, -1), (1, 0), (-1, 3)]:
        arrow(ax, bs, cls[c], "#c0392b", lw=1.8)
    finish(ax, "nd0-phase0-topology-and-plan-flow.png")


def phase2():
    """ND6: suspicious cells sized by score; the rotary UAV visits them by score from the BS."""
    import random
    rnd = random.Random(3); fig, ax = plt.subplots(figsize=(7, 5))
    cs = cells(6, 4)
    for c in cs: hexa(ax, *c, LIGHT, ec="#dddddd")
    sus = rnd.sample(cs, 7); score = sorted([rnd.random() for _ in sus], reverse=True)
    bs = (center(-7, 4)[0], center(-7, 4)[1] + 0.5)
    ax.add_patch(RegularPolygon(bs, 4, radius=0.55, fc="black", zorder=4))
    order = sorted(zip(score, sus), reverse=True)
    for s, c in order:
        hexa(ax, *c, plt.cm.Reds(0.35 + 0.6 * s), z=2)
        ax.add_patch(Circle(center(*c), 0.15 + 0.45 * s, fc="none", ec="black", lw=1.2, zorder=3))
    pts = [bs] + [center(*c) for _, c in order] + [bs]
    for p, q in zip(pts, pts[1:]): arrow(ax, p, q, "#1f4e9c", lw=1.6)
    finish(ax, "nd6-phase2-score-ordered-visits.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    deviation(); takeover(); phase0(); phase2()
