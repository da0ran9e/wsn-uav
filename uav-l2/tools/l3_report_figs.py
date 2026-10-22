"""Figures of the Layer-3 technical report (CLAUDE.md §8 item 125): each River algorithm drawn step by step on one
cluster, in the colours of the replays (anim/*.html, cluster_steps.py). No text on the figures (item 63); the
numbers the captions quote are printed.

    python3 tools/l3_report_figs.py --data docs/data/cap80-c3long --k 3 --bits PASS-bits-r1.bin \
        --trace "TRACE/{s}" --figs docs/figures --name tr-l3

DATA, BITS and TRACE as for cluster_steps.py (the River trace with Circles prepared, s = rf). Writes FIGS/NAME-*.png:
  alg1    Algorithm 1: packets along the track by index | each packet's owner cell | the Seg intervals
  alg2    Algorithm 2: sum vector u and one Axe cell's normal walked +-omega | every Axe cell's normal | River, Banks
  alg3    Algorithm 3: CL scores | their histogram with mu + sigma and mu + 2 sigma | outstanding cells and the
          2-ring areas of the local winners | the critical cells
  alg4    Algorithm 4 for one critical cell: members ordered along u | the Axe split into their groups | the Banks
          each member fetches from and the cell paths
  gather  Algorithm G: gathering links so far and each cell's CL share of D (light -> dark grey), at three instants
  run     Algorithms 5-7: frames of the last DT seconds by phase, CL shares of D, critical cells' fill, at six instants
"""
import argparse, csv, math, os, statistics as st, sys
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Circle, FancyArrowPatch, Wedge
import numpy as np

from map_gen import corners, strip_text
from cluster_river_figure import load_geo
from cluster_steps import AXE, BANK, CAT, GREY, INK, INK2, PH, RAMP, RIVER, SURF

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import hex_of, plan, ring  # noqa: E402

RED, ORANGE, SOFT = "#e34948", "#f3c06b", "#f1f0eb"
FILL = matplotlib.colors.LinearSegmentedColormap.from_list("f", ["#f4f3ef", "#c9cfd3", "#6f7d86"])   # CL share of D
ARROW = "#8b1a1a"


def main():
    ap = argparse.ArgumentParser()
    for k in ("data", "bits", "trace", "figs", "name"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--circle", default="9,-7", help="the critical cell of the Algorithm 4 figure, q,r")
    ap.add_argument("--dt", type=float, default=2.0, help="run figure: frames of the last DT seconds")
    a = ap.parse_args()
    geo = load_geo(a.data, a.k)
    P = plan(geo)
    c, sel, S, path, W, R = geo["c"], geo["cells"], geo["S"], geo["path"], geo["w"], geo["R"]
    uav, N = geo["uav"], len(geo["uav"])
    nodes = geo["nodes"]
    xy = np.array([[float(n["x"]), float(n["y"])] for n in nodes])
    cellof = [(int(n["q"]), int(n["r"])) for n in nodes]
    crits, axe, seg = P["crit"], P["axe"], P["seg"]
    ccol = {k: CAT[i % len(CAT)] for i, k in enumerate(crits)}
    na = len(axe)
    acol = {h: RAMP(.25 + .75 * i / max(1, na - 1)) for i, h in enumerate(axe)}
    xs = [c[h][0] for h in sel]; ys = [c[h][1] for h in sel]
    lim = (min(xs) - 1.5 * W, max(xs) + 1.5 * W, min(ys) - 1.5 * W, max(ys) + 1.5 * W)
    rows = lambda f: list(csv.DictReader(open(f)))

    def base(ax, col, edge=SURF):
        ax.add_collection(PolyCollection([corners(h) for h in sel], facecolors=[col.get(h, GREY) for h in sel],
                                         edgecolors=edge, linewidths=.5, zorder=0))
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def outline(ax, h, color, lw=1.8, scale=.82, ls="-", z=5):
        ax.add_patch(plt.Polygon([(c[h][0] + scale * (x - c[h][0]), c[h][1] + scale * (y - c[h][1])) for x, y in corners(h)],
                                 fill=False, ec=color, lw=lw, ls=ls, zorder=z))

    def marks(ax, ring_only=False):
        for k in crits:
            star = k == P["ch"]
            ax.scatter(*c[k], s=230 if star else 110, marker="*" if star else "o", color="#ffffff",
                       edgecolors=ccol[k] if ring_only else INK, lw=1.6 if ring_only else 1.1, zorder=8)

    def track(ax, alpha=.8, lw=1.1):
        ax.plot(*path.T, color=INK, lw=lw, alpha=alpha, zorder=6)

    def arrow(ax, p0, p1, color=ARROW):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=18, color=color, lw=2.2, zorder=9))

    def save(fig, tag):
        strip_text(fig)
        fig.savefig(os.path.join(a.figs, f"{a.name}-{tag}.png"), facecolor=SURF, bbox_inches="tight", pad_inches=.06)
        plt.close(fig)

    # ---------------- Algorithm 1: Axe and Seg
    own = [hex_of(x, y, R) for x, y in uav]
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.5), dpi=150, facecolor=SURF,
                            gridspec_kw=dict(width_ratios=[1, 1, .9]))
    base(axs[0], {}); track(axs[0], .25)
    step = 100
    idx = np.arange(0, N, step)
    axs[0].scatter(uav[idx, 0], uav[idx, 1], s=9, c=[RAMP(.25 + .75 * i / N) for i in idx], zorder=7)
    base(axs[1], acol); track(axs[1], .25)
    inside = [i for i in idx if own[i] in seg and i in set(seg[own[i]])]
    outside = [i for i in idx if i not in set(inside)]
    axs[1].scatter(uav[inside, 0], uav[inside, 1], s=9, c=[acol[own[i]] for i in inside], edgecolors=INK, lw=.3, zorder=7)
    axs[1].scatter(uav[outside, 0], uav[outside, 1], s=6, color=INK2, alpha=.35, zorder=7)
    ax = axs[2]
    ax.barh(0, N, left=0, height=.8, color=SOFT, zorder=1)
    for i, h in enumerate(axe):
        ax.barh(-(i + 1), seg[h][-1] - seg[h][0] + 1, left=seg[h][0], height=.8, color=acol[h], zorder=2)
    ax.set_xlim(0, N); ax.set_ylim(-(na + .8), .8)
    ax.set_xticks(np.arange(0, N, 1000)); ax.set_yticks([]); ax.grid(axis="x", color=GREY, lw=.6, zorder=0)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    save(fig, "alg1")
    print(f"alg1: {N} packets along the track, {sum(len(v) for v in seg.values())} over {na} Axe cells "
          f"(packets {seg[axe[0]][0]}-{seg[axe[-1]][-1]}); Seg sizes {[len(seg[h]) for h in axe]}")

    # ---------------- Algorithm 2: River and Banks
    u, om = P["u"], P["omega"]
    nrm = np.array([-u[1], u[0]])

    def walk(a_, sg):
        z, last = np.array(c[a_]), np.array(c[a_])
        for t in np.arange(0, om + 1e-9, W / 20):
            p = z + sg * t * nrm
            if hex_of(*p, R) not in S:
                break
            last = p
        return last
    banks = {b for (x, s_), b in P["bank"].items() if b != x}
    mid = axe[na // 2]
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.5), dpi=150, facecolor=SURF)
    col = {h: AXE for h in axe}
    col.update({h: RIVER for sg in (0, 1) for h in P["bpath"][(mid, sg)][1:]})
    col.update({P["bank"][(mid, sg)]: "#3fb98b" for sg in (0, 1) if P["bank"][(mid, sg)] != mid})
    base(axs[0], col); track(axs[0], .3)
    arrow(axs[0], c[axe[0]], c[axe[-1]])
    e0, e1 = np.array(c[mid]) - om * nrm, np.array(c[mid]) + om * nrm
    axs[0].plot(*np.c_[e0, e1], color=INK, lw=1.8, zorder=9)
    axs[0].scatter(*np.c_[e0, e1], s=40, color=INK, zorder=10)
    axs[0].scatter(*c[mid], s=60, color="#ffffff", edgecolors=INK, lw=1.2, zorder=10)
    base(axs[1], {h: AXE for h in axe}); track(axs[1], .3)
    for x in axe:
        for sg, sgn in ((0, 1.0), (1, -1.0)):
            p = walk(x, sgn)
            axs[1].plot([c[x][0], p[0]], [c[x][1], p[1]], color=INK, lw=1, ls=(0, (3, 2)), zorder=7)
            axs[1].scatter(*p, s=12, color=INK, zorder=8)
    col = {h: RIVER for h in P["river"]}
    col.update({b: BANK for b in banks}); col.update({h: AXE for h in axe})
    base(axs[2], col)
    axs[2].add_collection(LineCollection([[c[h] for h in p_] for p_ in P["bpath"].values() if len(p_) > 1],
                                         colors=INK, linewidths=1, zorder=3))
    track(axs[2], .4)
    save(fig, "alg2")
    print(f"alg2: u from {axe[0]} to {axe[-1]}; the shown Axe cell {mid}: paths "
          f"{[P['bpath'][(mid, s_)] for s_ in (0, 1)]}; River {len(P['river'])} cells, {len(banks)} Banks; omega {om:.0f} m")

    # ---------------- Algorithm 3: critical cells
    sc = {(int(x["q"]), int(x["r"])): float(x["score"]) for x in nodes if x["isCL"] == "1"}
    mu, sd = float(np.mean(list(sc.values()))), float(np.std(list(sc.values())))
    hi = max(sc.values())
    glob_ = [h for h in sel if sc[h] > mu + 2 * sd]
    cand = [h for h in sel if mu + sd < sc[h] <= mu + 2 * sd]
    local = [h for h in cand if sc[h] >= max(sc[g] for k_ in (1, 2) for g in ring(h, k_) if g in sc)]
    fig, axs = plt.subplots(1, 4, figsize=(20, 7.5), dpi=150, facecolor=SURF,
                            gridspec_kw=dict(width_ratios=[1, 1.1, 1, 1]))
    base(axs[0], {h: RAMP(sc[h] / hi) for h in sel}); track(axs[0], .3)
    ax = axs[1]
    ax.hist(list(sc.values()), bins=np.linspace(0, 1, 26), color="#b9c4cc", zorder=2)
    ax.axvline(mu + sd, color=ORANGE, lw=2, ls=(0, (4, 2)), zorder=3)
    ax.axvline(mu + 2 * sd, color=RED, lw=2, zorder=3)
    for k in crits:
        ax.plot([sc[k]], [-.6], marker="*" if k == P["ch"] else "o", ms=13 if k == P["ch"] else 9, color="#ffffff",
                mec=ccol[k], mew=1.8, zorder=4, clip_on=False)
    ax.set_xlim(0, 1); ax.set_xticks(np.arange(0, 1.01, .2)); ax.grid(axis="y", color=GREY, lw=.6, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    col = {h: RED for h in glob_}
    col.update({h: ORANGE for h in cand})
    base(axs[2], col)
    for h in local:
        for k_ in (1, 2):
            for g in ring(h, k_):
                if g in S:
                    outline(axs[2], g, ORANGE, lw=1.1, scale=.9, ls=(0, (2, 1.5)), z=4)
        outline(axs[2], h, INK, lw=1.8, scale=.82, z=6)
    for h in glob_:
        outline(axs[2], h, INK, lw=1.8, scale=.82, z=6)
    axs[2].scatter(*c[P["ch"]], s=230, marker="*", color="#ffffff", edgecolors=INK, lw=1.1, zorder=8)
    base(axs[3], {k: ccol[k] for k in crits}); marks(axs[3]); track(axs[3], .3)
    save(fig, "alg3")
    print(f"alg3: mu {mu:.3f}, sd {sd:.3f}; > mu+2sd ({mu + 2 * sd:.3f}): {glob_}; mu+sd..mu+2sd ({mu + sd:.3f}): "
          f"{len(cand)} cells, local winners {local}; CH {P['ch']}; critical {crits}")

    # ---------------- Algorithm 4: Circle of one critical cell
    k = tuple(int(v) for v in a.circle.split(","))
    tasks = P["circle"][k]
    q = len(tasks)
    mcol = {m: plt.cm.viridis(.1 + .8 * j / max(1, q - 1)) for j, (m, G, src) in enumerate(tasks)}
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.5), dpi=150, facecolor=SURF)
    col = {h: RIVER for h in P["river"]}
    col.update({h: AXE for h in axe}); col.update(mcol)
    base(axs[0], col); track(axs[0], .3)
    arrow(axs[0], c[axe[0]], c[axe[-1]])
    axs[0].scatter(*c[k], s=230 if k == P["ch"] else 120, marker="*" if k == P["ch"] else "o", color="#ffffff",
                   edgecolors=INK, lw=1.3, zorder=9)
    col = {h: RIVER for h in P["river"]}
    col.update({x: mcol[m] for m, G, src in tasks for x in G}); col.update(mcol)
    base(axs[1], col); track(axs[1], .3)
    axs[1].scatter(*c[k], s=120, color="#ffffff", edgecolors=INK, lw=1.3, zorder=9)
    col = {h: RIVER for h in P["river"]}
    col.update({h: AXE for h in axe}); col.update(mcol)
    base(axs[2], col); track(axs[2], .3)
    for m, G, src in tasks:
        for x, side, b, p_ in src:
            outline(axs[2], b, mcol[m], lw=2, scale=.7, z=6)
            if len(p_) > 1:
                axs[2].plot(*np.array([c[h] for h in p_]).T, color=mcol[m], lw=1.6, alpha=.9, zorder=5)
    axs[2].scatter(*c[k], s=120, color="#ffffff", edgecolors=INK, lw=1.3, zorder=9)
    save(fig, "alg4")
    for j, (m, G, src) in enumerate(tasks):
        L = [len(p_) - 1 for (_, _, _, p_) in src]
        print(f"alg4: {k} member {j + 1} {m}: Axe cells {G[0]}..{G[-1]} ({len(G)} Seg), Banks {sorted({b for _, _, b, _ in src})}, "
              f"paths {L} cells")

    # ---------------- ns-3 trace: gathering and the River flows
    tr = a.trace.format(s="rf")
    hops = rows(tr + "-hops.csv")
    held = defaultdict(list)
    for r in rows(tr + "-held.csv"):
        held[(int(r["q"]), int(r["r"]))].append(float(r["t"]))
    held = {h: np.sort(v) for h, v in held.items()}
    crow = {(int(r["q"]), int(r["r"])): r for r in rows(tr + "-crit.csv")}
    Dn = int(crow[crits[0]]["D"])
    share = lambda h, t: np.searchsorted(held[h], t, side="right") / Dn if h in held else None

    def fills(ax, t):
        base(ax, {h: FILL(share(h, t)) for h in held}); track(ax, .25)

    def pies(ax, t):
        for k_ in crits:
            f = min(1.0, share(k_, t))
            ax.add_patch(Circle(c[k_], .42 * W, color="#ffffff", ec=INK, lw=1, zorder=9))
            if f >= 1:
                ax.add_patch(Circle(c[k_], .42 * W, color=INK, zorder=10))
            elif f > 0:
                ax.add_patch(Wedge(c[k_], .42 * W, 90 - 360 * f, 90, color=ccol[k_], zorder=10))
            if k_ == P["ch"]:
                ax.scatter(*c[k_], s=60, marker="*", color="#ffffff", edgecolors=INK, lw=.6, zorder=11)

    def links(hh, hi_=None, lw=3.5):
        cnt = Counter((int(r["from"]), int(r["to"])) for r in hh)
        if not cnt:
            return [], []
        hi_ = hi_ or max(cnt.values())
        return [[xy[u_], xy[v_]] for u_, v_ in cnt], [.3 + lw * math.sqrt(n / hi_) for n in cnt.values()]

    g = [r for r in hops if r["phase"] == "gather"]
    gt = (1.0, 3.0, 10.0)
    fig, axs = plt.subplots(1, 3, figsize=(16, 7.5), dpi=150, facecolor=SURF)
    ghi = max(Counter((r["from"], r["to"]) for r in g).values())
    for ax, t in zip(axs, gt):
        fills(ax, t)
        L_, Wd = links([r for r in g if float(r["t"]) <= t], ghi)
        ax.add_collection(LineCollection(L_, colors=PH["gather"], linewidths=Wd, alpha=.85, zorder=3))
        pies(ax, t)
    save(fig, "gather")
    for t in gt:
        print(f"gather t={t:g} s: {sum(1 for r in g if float(r['t']) <= t)} of {len(g)} gather frames; critical CL shares " +
              ", ".join(f"{k_} {share(k_, t):.2f}" for k_ in crits))

    rt = (8.0, 12.0, 18.0, 25.0, 32.0, 37.2)
    fig, axs = plt.subplots(2, 3, figsize=(16, 15), dpi=150, facecolor=SURF)
    for ax, t in zip(axs.ravel(), rt):
        fills(ax, t)
        win = [r for r in hops if t - a.dt < float(r["t"]) <= t]
        for ph, z in (("control", 2), ("gather", 3), ("bankfill", 3), ("circlefill", 3), ("pull", 4)):
            hh = [r for r in win if r["phase"] == ph]
            L_, Wd = links(hh, None, 3)
            ax.add_collection(LineCollection(L_, colors=PH[ph], linewidths=.5 if ph == "control" else Wd,
                                             alpha=.5 if ph == "control" else .9, zorder=z))
        pies(ax, t)
    save(fig, "run")
    for t in rt:
        win = Counter(r["phase"] for r in hops if t - a.dt < float(r["t"]) <= t)
        print(f"run t={t:g} s, last {a.dt:g} s: {dict(win)}; critical CL shares " +
              ", ".join(f"{k_} {min(1, share(k_, t)):.2f}" for k_ in crits))
    print("done at: " + ", ".join(f"{k_} {float(crow[k_]['doneS']):.1f} s" for k_ in crits))


if __name__ == "__main__":
    main()
