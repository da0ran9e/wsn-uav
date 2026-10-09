"""Concept sketches at cell level, no text: River set-up, River, Axe, Banks, Axe -> Banks,
critical cells, Circle.

    python3 tools/concept_cells.py --deploy ../uav-coop/docs/data --data docs/data --figs docs/figures \
        --path docs/data/path-a180.csv --width 3.5

  Axe            cells the track crosses, in order; each holds the stretch of the stream sent
                 above it
  River set-up   u = the Axe's sum vector (first -> last Axe cell); through the centre Axe cell
                 a line perpendicular to u; two points at omega = width/2 cell widths on it,
                 one each side: the cells there are the centre's two Banks. Every other Axe
                 cell does the same on a parallel line. A point outside the cluster gives the
                 last cluster cell on the way (the edge is the Bank).
  River          the Axe cells plus the cells each perpendicular crosses (= its cell path)
  critical       the CH's cell, CLs far above the rest (> mean + 2 sd), and CLs that are
                 the best within two rings and above mean + 1 sd
  Circle         the 6 neighbours of a critical cell; the Axe is cut into 6 consecutive
                 stretches, one per neighbour (further along the flight -> further along the
                 Axe); each neighbour fetches its stretch from the nearest of that stretch's
                 Banks, along a cell path that avoids the Axe and the critical cell, and hands
                 it over on request
"""
import argparse, csv, math, os
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch, Wedge
import numpy as np

SURF, INK, GREY, FAINT = "#fcfcfb", "#0b0b0b", "#e6e5e1", "#c9dcf3"
RAMP = matplotlib.colors.LinearSegmentedColormap.from_list("r", ["#86b6ef", "#3987e5", "#0d366b"])
SEQ = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#f6c3c3", "#e34948", "#8f1d1b"])
BANK = ["#1baf7a", "#eda100"]
CRIT = "#e34948"
CAT = ["#0d366b", "#3987e5", "#1baf7a", "#eda100", "#e34948", "#8e5ad6"]
NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
EDGE_NB = [(0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1), (1, 0)]


def corners(cx, cy, R):
    return [(cx + R * math.cos(math.radians(30 + 60 * k)), cy + R * math.sin(math.radians(30 + 60 * k)))
            for k in range(6)]


def hex_of(x, y, R):
    """Pointy-top axial cell containing (x, y)."""
    q, r = (math.sqrt(3) / 3 * x - y / 3) / R, (2 / 3 * y) / R
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return rq, rr


def ring(h, k):
    out, q, r = [], h[0] + NB[4][0] * k, h[1] + NB[4][1] * k
    for side in range(6):
        for _ in range(k):
            out.append((q, r))
            q, r = q + NB[side][0], r + NB[side][1]
    return out


def hexdist(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) // 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--figs", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--width", type=float, default=3.5, help="River width across the track, cells")
    a = ap.parse_args()

    lat = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-lattice.csv"))))
    c = {(int(x["q"]), int(x["r"])): (float(x["cx"]), float(x["cy"])) for x in lat}
    w = math.dist(c[(0, 0)], c[(1, 0)])
    R = w / math.sqrt(3)
    for h, (x, y) in c.items():
        assert hex_of(x, y, R) == h
    sel = sorted((int(x["q"]), int(x["r"])) for x in lat if x["selected"] == "1")
    S = set(sel)
    segs = [[corners(*c[h], R)[k], corners(*c[h], R)[(k + 1) % 6]]
            for h in sel for k, (dq, dr) in enumerate(EDGE_NB) if (h[0] + dq, h[1] + dr) not in S]
    nodes = list(csv.DictReader(open(os.path.join(a.deploy, "deploy-nodes-s35.csv"))))
    P = np.array([[float(q["x"]), float(q["y"])] for q in csv.DictReader(open(a.path))])
    curve = list(csv.DictReader(open(os.path.join(a.data, "per-distance.csv"))))
    cd = np.array([(float(r["dLoM"]) + float(r["dHiM"])) / 2 for r in curve])
    cp = np.array([float(r["per"]) for r in curve])
    omega = a.width / 2 * w
    th = float(np.interp(omega, cd, cp))

    C = np.array([c[h] for h in sel])
    per = dict(zip(sel, np.interp(np.sqrt(((C[:, None, :] - P[None, :, :]) ** 2).sum(-1)).min(1), cd, cp)))
    axe = []
    for x, y in P:
        h = hex_of(x, y, R)
        if h in S and h not in axe:
            axe.append(h)
    rank = {h: i / max(1, len(axe) - 1) for i, h in enumerate(axe)}
    # River set-up: the Axe's sum vector, its normal, banks at +-omega on parallel lines
    u = np.array(c[axe[-1]]) - np.array(c[axe[0]])
    u /= np.linalg.norm(u)
    nrm = np.array([-u[1], u[0]])
    centre = axe[len(axe) // 2]
    pair = {}                         # (Axe cell, side) -> (Bank cell, cell path Axe -> Bank)
    for g in axe:
        z = np.array(c[g])
        for s_, sg in ((0, 1.0), (1, -1.0)):
            path = [g]
            for t in np.arange(0, omega + 1e-9, w / 20):
                h = hex_of(*(z + sg * t * nrm), R)
                if h not in S:
                    break               # left the cluster: the edge is the Bank
                if h != path[-1]:
                    path.append(h)
            pair[(g, s_)] = (path[-1], path)
    river = set(axe) | {h for _, p in pair.values() for h in p}
    banks = {b for (b, _) in pair.values() if b not in axe}
    side = {b: s_ for (g, s_), (b, _) in pair.items()}

    def cellpath(src, dst, allowed):
        """Shortest cell path src -> dst through allowed cells, the straightest among equals."""
        prev, seen, dq = {}, {src}, deque([src])
        while dq:
            v = dq.popleft()
            if v == dst:
                break
            for g in sorted(((v[0] + a_, v[1] + b_) for a_, b_ in NB),
                            key=lambda g: math.dist(c.get(g, (1e9, 1e9)), c[dst])):
                if g in allowed and g not in seen:
                    seen.add(g); prev[g] = v; dq.append(g)
        assert dst in seen, (src, dst)
        out = [dst]
        while out[-1] != src:
            out.append(prev[out[-1]])
        return out[::-1]

    # critical cells
    sc = {(int(r["q"]), int(r["r"])): float(r["score"]) for r in nodes if r["isCL"] == "1"}
    m, s = np.mean(list(sc.values())), np.std(list(sc.values()))
    chn = next(r for r in nodes if r["isCH"] == "1")
    chc = (int(chn["q"]), int(chn["r"]))
    crit = {chc} | {h for h, v in sc.items() if v > m + 2 * s}
    for h, v in sc.items():
        around = [sc[g] for g in ring(h, 1) + ring(h, 2) if g in sc]
        if v > m + s and v >= max(around):
            crit.add(h)
    clpos = {(int(r["q"]), int(r["r"])): (float(r["x"]), float(r["y"])) for r in nodes if r["isCL"] == "1"}
    xs = C[:, 0]; ys = C[:, 1]

    def frame(ax, colours, track=.8):
        ax.add_collection(PolyCollection([corners(*c[h], R) for h in sel], facecolors=[colours[h] for h in sel],
                                         edgecolors="#ffffff", linewidths=.8, zorder=0))
        ax.add_collection(LineCollection(segs, colors="#52514e", linewidths=.9, zorder=1))
        if track:
            ax.plot(P[:, 0], P[:, 1], color=INK, lw=1.2, alpha=track, zorder=6)
            ax.add_patch(FancyArrowPatch(P[-30], P[-1], arrowstyle="-|>", mutation_scale=12, color=INK,
                                         alpha=track, zorder=6))
        ax.set_xlim(xs.min() - w, xs.max() + w); ax.set_ylim(ys.min() - w, ys.max() + w)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

    def route(ax, cells, colour, lw=1.6, ls="-"):
        pts = np.array([c[h] for h in cells])
        ax.plot(pts[:-1, 0], pts[:-1, 1], color=colour, lw=lw, ls=ls, zorder=5, solid_capstyle="round")
        ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=11, color=colour, lw=lw,
                                     ls=ls, shrinkA=0, shrinkB=R * .25, zorder=5))

    def save(fig, name):
        out = os.path.join(a.figs, name)
        fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.05)
        plt.close(fig)
        print(f"  {out}")

    def one():
        return plt.subplots(figsize=(5.2, 6.6), dpi=150, facecolor=SURF)

    # 1. River set-up: sum vector, the centre's perpendicular and its two Banks, parallels
    fig, ax = one()
    col = {h: GREY for h in sel}
    col.update({h: FAINT for h in river})
    col.update({b: matplotlib.colors.to_rgba(BANK[side[b]], .5) for b in banks})
    col.update({h: SEQ(rank[h]) for h in axe})
    for s_ in (0, 1):
        col[pair[(centre, s_)][0]] = BANK[s_]
    frame(ax, col, 0)
    z0 = np.array(c[centre])
    for g in axe:
        z = np.array(c[g])
        lw, ls, al = (1.6, "-", 1) if g == centre else (.8, "--", .55)
        ax.plot(*np.array([z - omega * nrm, z + omega * nrm]).T, color=INK, lw=lw, ls=ls, alpha=al, zorder=5)
    for sg in (1, -1):
        ax.scatter(*(z0 + sg * omega * nrm), s=34, color=INK, zorder=7)
    ax.scatter(*z0, s=34, facecolors="#ffffff", edgecolors=INK, lw=1.2, zorder=7)
    ax.add_patch(FancyArrowPatch(np.array(c[axe[0]]) - (omega + w) * nrm, np.array(c[axe[-1]]) - (omega + w) * nrm,
                                 arrowstyle="-|>", mutation_scale=16, color="#8f1d1b", lw=2, zorder=6))
    save(fig, "concept-river-setup.png")
    # 2. River: shade = PER (darker = fewer losses)
    fig, ax = one()
    frame(ax, {h: RAMP(1 - min(1, per[h] / max(th, 1e-9))) if h in river else GREY for h in sel})
    save(fig, "concept-river.png")
    # 3. Axe: each cell holds the stretch of the stream sent above it (colour = order)
    fig, ax = one()
    frame(ax, {h: SEQ(rank[h]) if h in rank else (FAINT if h in river else GREY) for h in sel}, .5)
    save(fig, "concept-axe.png")
    # 4. Banks
    fig, ax = one()
    frame(ax, {h: BANK[side[h]] if h in banks else (FAINT if h in river else GREY) for h in sel}, .5)
    save(fig, "concept-banks.png")
    # 5. Axe -> Banks along the perpendicular cell paths (colour = the Axe cell's stretch)
    fig, ax = one()
    col = {h: GREY for h in sel}
    col.update({h: FAINT for h in river})
    col.update({h: matplotlib.colors.to_rgba(BANK[side[h]], .55) for h in banks})
    col.update({h: SEQ(rank[h]) for h in axe})
    frame(ax, col, .3)
    for (g, s_), (b, cells) in pair.items():
        if len(cells) > 1:
            route(ax, cells, SEQ(rank[g]), 1.4)
    save(fig, "concept-axe-banks.png")
    # 6. critical cells, each fed from its nearest Bank along a cell path
    fig, ax = one()
    frame(ax, {h: "#f6c3c3" if h in crit else (matplotlib.colors.to_rgba(BANK[side[h]], .55) if h in banks
                                                else (FAINT if h in river else GREY)) for h in sel}, .3)
    for h in crit:
        if h not in river:
            b = min(banks, key=lambda b: (hexdist(b, h), math.dist(c[b], c[h])))
            route(ax, cellpath(b, h, (S - river) | {b}), "#3987e5")
        ax.scatter(*clpos[h], s=90 if h == chc else 55, marker="*" if h == chc else "o", color=CRIT,
                   edgecolors=INK, lw=.6, zorder=7)
    save(fig, "concept-critical.png")
    # 7. Circle around the critical cell farthest from the River with all 6 neighbours outside it
    cand = [h for h in crit if h not in river and all(g in S and g not in river for g in ring(h, 1))]
    if not cand:
        cand = [h for h in sel if h not in river and all(g in S and g not in river for g in ring(h, 1))]
    cc = max(cand, key=lambda h: min(hexdist(h, g) for g in river))
    circ = ring(cc, 1)
    order = sorted(range(6), key=lambda j: np.dot(np.array(c[circ[j]]), u))
    owner = {g: order[min(5, i * 6 // len(axe))] for i, g in enumerate(axe)}
    fig, ax = one()
    col = {h: GREY for h in sel}
    col.update({h: FAINT for h in river})
    col.update({g: matplotlib.colors.to_rgba(CAT[owner[g]], .45) for g in axe})
    col.update({h: CAT[j] for j, h in enumerate(circ)})
    col[cc] = "#ffffff"
    used = {}
    for j, h in enumerate(circ):
        mine = [g for g in axe if owner[g] == j]
        if not mine:
            continue
        # the nearest of this stretch's Banks (either side) to the neighbour
        b = min({pair[(g, s_)][0] for g in mine for s_ in (0, 1)},
                key=lambda b: (hexdist(b, h), math.dist(c[b], c[h])))
        used[j] = (mine, b)
        col[b] = matplotlib.colors.to_rgba(CAT[j], .8)
    frame(ax, col, .3)
    share = [len(used[j][0]) if j in used else 0 for j in range(6)]
    a0 = 90.0
    for j in range(6):
        if share[j]:
            a1 = a0 + 360 * share[j] / len(axe)
            ax.add_patch(Wedge(c[cc], R * .62, a0, a1, facecolor=CAT[j], edgecolor="#ffffff", lw=.8, zorder=4))
            a0 = a1
    for j, (mine, b) in used.items():
        g, s_ = next((g, s_) for g in mine for s_ in (0, 1) if pair[(g, s_)][0] == b)
        if g != b:
            route(ax, pair[(g, s_)][1], CAT[j], 1.0, "--")
        route(ax, cellpath(b, circ[j], (S - set(axe) - {cc}) | {b}), CAT[j], 1.6)
        v = np.array(c[cc]) - np.array(c[circ[j]])
        v /= np.linalg.norm(v)
        ax.add_patch(FancyArrowPatch(np.array(c[circ[j]]) + v * R * .3, np.array(c[cc]) - v * R * .68,
                                     arrowstyle="-|>", mutation_scale=10, color=INK, lw=1, ls=":", zorder=5))
    ax.scatter(*clpos.get(cc, c[cc]), s=60, color=CRIT, edgecolors=INK, lw=.6, zorder=7)
    save(fig, "concept-circle.png")
    print(f"width {a.width} cells -> omega {omega:.0f} m, PER there {th:.4f}; Axe {len(axe)}, centre {centre}; "
          f"River {len(river)} cells, Banks {len(banks)} ({sum(side[b] == 0 for b in banks)} / "
          f"{sum(side[b] == 1 for b in banks)}), edge Banks {sum(len(p) - 1 < round(a.width / 2) for _, p in pair.values())}")
    print(f"critical {sorted(crit)} (CH {chc}); circle around {cc}, shares {share}")


if __name__ == "__main__":
    main()
