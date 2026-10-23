"""Phase 0 rebuilt for the mission (CLAUDE.md §8 item 84): clusters cut as lanes, so that River gets long,
narrow clusters, consecutive flight lines join up across the domain, and the visit order is known before
the clusters are made.

    python3 tools/restructure.py --clusters 4 --seed 2 --figs docs/figures            # one map, step figures
    python3 tools/restructure.py --campaign --out docs/data/restructure               # 40 maps, both partitions

Algorithm LANE(land, cap, lane width L cells, policy):
  1  direction: for every bearing th (0-178 deg, step 2) and lane offset (0, 1/3, 2/3 of a lane), cut the
     land into parallel lanes L*W wide along th; a lane's land falls into pieces where lakes or bays
     interrupt it. Cost = clusters the pieces need (sum ceil(piece/cap)) + fragments (pieces < cap/4).
     Keep the cheapest (fewer lanes, then the smaller bearing, break ties).
  2  fragments: a piece under cap/4 cells joins, whole, the touching piece it shares most border with
     (smallest first, repeated), so no lane leaves a sliver behind.
  3  cut: each piece into ceil(piece/cap) chunks of equal size along th (by the cells' position along th);
     a chunk in several parts keeps its largest, the other parts join the touching chunk of the same
     piece with room and the most shared border.
  4  order: boustrophedon over the lanes, clusters along each lane in turn, alternating direction; of
     the four (first lane, first direction) choices keep the one that suits --policy:
       short  shortest tour;   big  big clusters first;   dense  most nodes first;
       weak   clusters with the weakest nodes (lowest mean obs + cpu + comm) first
     (minimise sum of weight x entry time, weight normalised to mean 1, ties to the shorter tour).
The flight line of each cluster runs along th through its CH; the CH here is a proxy (the cell farthest
from the cluster's edge, nearest the centroid on ties), the real one comes from uav-coop-deploy.

Compared with partition.py (capacitated k-medoids + longest line through the CH + Held-Karp tour), per map:
clusters, cells, in-cluster flight (D = 2 packets per metre), River coverage (cells within omega = 1.75 W of
the line, River width 3.5 cells), farthest cell from the line, transit outside clusters, total turning.
"""
import argparse, csv, heapq, math, os, random
from collections import deque

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch

from map_gen import NB, W, add_args, cell_at, centre, corners, generate, strip_text
from partition import partition, pieces

INK, INK2, SURF, LAND, WATER = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1", "#3987e5"
CAT = ["#1c5cab", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#0d366b", "#86b6ef", "#b0761d", "#2f8f5b"]
OMEGA = 1.75 * W          # River half-width (river_plan: width 3.5 cells)
CAP, V1 = 80, 50.0
ORIG = {2: 3, 4: 2, 6: 4, 8: 4}   # clusters -> seed of the first four mission maps


def domain(K, seed, shape=""):
    """shape: map_gen options as "spine=8.8,bend=220,width=1" (CLAUDE.md §8 item 147), on top of the defaults."""
    p = argparse.ArgumentParser()
    add_args(p)
    g = p.parse_args([])
    g.seed, g.cells, g.lakes, g.lakeCells = seed, 80 * K, K, 10
    for kv in filter(None, shape.split(",")):
        k, v = kv.split("=")
        setattr(g, k, float(v))
    return generate(g, random.Random(seed))


def lanes_of(land, th, L, off):
    n = (-math.sin(th), math.cos(th))
    pn = {h: centre(h)[0] * n[0] + centre(h)[1] * n[1] for h in land}
    lo = min(pn.values())
    return {h: int(math.floor((pn[h] - lo) / (L * W) + off)) for h in land}


def lane_pieces(land, lane):
    out = []
    for l in sorted(set(lane.values())):
        out += [(l, p) for p in pieces([h for h in land if lane[h] == l])]
    return out


def scan(land, cap, L):
    """Step 1: (cost, lanes, bearing deg, offset) for every bearing and offset, cheapest first."""
    rows = []
    for b in range(0, 180, 2):
        for off in (0, 1 / 3, 2 / 3):
            lane = lanes_of(land, math.radians(b), L, off)
            ps = lane_pieces(land, lane)
            cost = sum(math.ceil(len(p) / cap) for _, p in ps) + sum(len(p) < cap / 4 for _, p in ps)
            rows.append((cost, len(set(lane.values())), b, off))
    return sorted(rows)


def touching(owner, cells):
    nb = {}
    for h in cells:
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n in owner and owner[n] != owner[h]:
                nb[owner[n]] = nb.get(owner[n], 0) + 1
    return nb


def lane_partition(land, cap, L):
    """Steps 1-3. Returns owner (cell -> cluster), bearing (rad), lane (cell -> lane), and the stages."""
    cost, nl, b, off = scan(land, cap, L)[0]
    th = math.radians(b)
    u = (math.cos(th), math.sin(th))
    pu = lambda h: centre(h)[0] * u[0] + centre(h)[1] * u[1]
    lane = lanes_of(land, th, L, off)
    piece = {}
    for i, (l, p) in enumerate(lane_pieces(land, lane)):
        for h in p:
            piece[h] = i
    cut = dict(piece)
    size = lambda own, i: sum(1 for c in own.values() if c == i)
    frag = set()
    while True:                                      # step 2: fragments join a touching piece
        small = [i for i in set(piece.values()) if size(piece, i) < cap / 4]
        small = [i for i in small if touching(piece, [h for h in piece if piece[h] == i])]
        if not small:
            break
        i = min(small, key=lambda i: (size(piece, i), i))
        mine = [h for h in piece if piece[h] == i]
        nb = touching(piece, mine)
        j = max(nb, key=lambda j: (nb[j], -j))
        frag |= set(mine)
        for h in mine:
            piece[h] = j
    owner, k = {}, 0
    for i in sorted(set(piece.values())):            # step 3: equal chunks along the lane
        p = sorted((h for h in piece if piece[h] == i), key=pu)
        m = math.ceil(len(p) / cap)
        ids = list(range(k, k + m))
        for j in range(m):
            for h in p[j * len(p) // m:(j + 1) * len(p) // m]:
                owner[h] = k + j
        k += m
        for c in ids:                                # a chunk in parts keeps its largest
            for part in pieces([h for h in owner if owner[h] == c])[1:]:
                nb = {j: n for j, n in touching(owner, part).items() if j in ids}
                if nb:
                    j = max(nb, key=lambda j: (size(owner, j) + len(part) <= cap, nb[j]))
                    for h in part:
                        owner[h] = j
    ids = {c: i for i, c in enumerate(sorted(set(owner.values())))}
    owner = {h: ids[c] for h, c in owner.items()}
    return owner, th, lane, dict(cut=cut, frag=frag, scan=scan(land, cap, L), off=off)


def ch_proxy(cells):
    """The cell farthest (in hops) from the cluster's edge; ties: nearest the centroid."""
    S = set(cells)
    edge = [h for h in cells if any((h[0] + dq, h[1] + dr) not in S for dq, dr in NB)]
    d, todo = {h: 0 for h in edge}, deque(edge)
    while todo:
        h = todo.popleft()
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n in S and n not in d:
                d[n] = d[h] + 1
                todo.append(n)
    cx, cy = np.mean([centre(h) for h in cells], axis=0)
    return max(cells, key=lambda h: (d[h], -math.dist(centre(h), (cx, cy))))


def line(cells, ch, th):
    """Straight flight through the CH at bearing th: entry, exit, metres inside the cluster."""
    S, (cx, cy) = set(cells), centre(ch)
    c, s = math.cos(th), math.sin(th)
    far = [max([t for t in range(0, 8000, 5) if cell_at(cx + sg * t * c, cy + sg * t * s) in S] or [0])
           for sg in (1, -1)]
    inside = sum(5 for t in range(-far[1], far[0], 5) if cell_at(cx + t * c, cy + t * s) in S)
    return (cx - far[1] * c, cy - far[1] * s), (cx + far[0] * c, cy + far[0] * s), inside


def best_line(cells, ch):
    return max((line(cells, ch, math.radians(b)) + (math.radians(b),) for b in range(0, 180, 2)),
               key=lambda t: t[2])


def held_karp(bs, seg):
    """Shortest tour BS -> every segment (either way) -> BS; seg: list of (a, b). Returns [(i, rev)]."""
    K = len(seg)
    st = lambda i, d: seg[i][d]
    en = lambda i, d: seg[i][1 - d]
    best = {(1 << i, i, d): (math.dist(bs, st(i, d)), None) for i in range(K) for d in (0, 1)}
    for mask in range(1, 1 << K):
        for i in range(K):
            for d in (0, 1):
                if (mask, i, d) not in best:
                    continue
                c0 = best[(mask, i, d)][0]
                for j in range(K):
                    if not mask >> j & 1:
                        for e in (0, 1):
                            key, c = (mask | 1 << j, j, e), c0 + math.dist(en(i, d), st(j, e))
                            if key not in best or c < best[key][0]:
                                best[key] = (c, (mask, i, d))
    full = (1 << K) - 1
    s = min(((full, i, d) for i in range(K) for d in (0, 1)), key=lambda s: best[s][0] + math.dist(en(s[1], s[2]), bs))
    out = []
    while s:
        out.append((s[1], s[2]))
        s = best[s][1]
    return out[::-1]


def tour_stats(bs, seg, order):
    """Transit metres outside clusters, entry times, total turning (deg) along the tour."""
    pts, t, pos, enter, transit = [bs], 0.0, bs, {}, 0.0
    for i, d in order:
        a, b = seg[i][d], seg[i][1 - d]
        transit += math.dist(pos, a)
        t += math.dist(pos, a) / V1
        enter[i] = t
        t += math.dist(a, b) / V1
        pts += [a, b]
        pos = b
    transit += math.dist(pos, bs)
    pts.append(bs)
    turn = 0.0
    hd = [math.atan2(q[1] - p[1], q[0] - p[0]) for p, q in zip(pts, pts[1:]) if math.dist(p, q) > 1]
    for x, y in zip(hd, hd[1:]):
        turn += abs(math.degrees(math.remainder(y - x, 2 * math.pi)))
    return transit, enter, turn, pts


def serpentine(owner, lane, th, seg, nodes, bs, policy):
    """Step 4: the four boustrophedon tours; the one the policy prefers."""
    u = (math.cos(th), math.sin(th))
    ks = sorted(set(owner.values()))
    cl = {k: [h for h in owner if owner[h] == k] for k in ks}
    ln = {k: max(set(lane[h] for h in cl[k]), key=[lane[h] for h in cl[k]].count) for k in ks}
    pu = {k: np.mean([centre(h)[0] * u[0] + centre(h)[1] * u[1] for h in cl[k]]) for k in ks}
    w = {"short": {k: 1.0 for k in ks}, "big": {k: len(cl[k]) for k in ks},
         "dense": {k: sum(1 for v in nodes if owner.get((v[3], v[4])) == k) for k in ks},
         "weak": {k: 1 - np.mean([(v[5] + v[6] + v[7]) / 3 for v in nodes if owner.get((v[3], v[4])) == k]) for k in ks}}[policy]
    mw = np.mean(list(w.values()))
    cands = []
    for first in (min, max):
        for dir0 in (1, -1):
            order, dirn = [], dir0
            ls = sorted(set(ln.values()), reverse=first is max)
            for l in ls:
                row = sorted([k for k in ks if ln[k] == l], key=lambda k: dirn * pu[k])
                for k in row:   # fly the segment the way the lane goes
                    a, b = seg[k]
                    fwd = (b[0] - a[0]) * u[0] + (b[1] - a[1]) * u[1] >= 0
                    order.append((k, 0 if fwd == (dirn > 0) else 1))
                dirn = -dirn
            transit, enter, turn, _ = tour_stats(bs, seg, order)
            score = 0.0 if policy == "short" else sum(w[k] / mw * enter[k] for k in ks)
            cands.append((score, transit, order))
    return min(cands, key=lambda c: (c[0], c[1]))[2]


def evaluate(owner, th_of, nodes, bs, order_fn):
    """Per-cluster geometry and the tour. th_of(cells, ch) -> (entry, exit, inside, bearing)."""
    ks = sorted(set(owner.values()))
    seg, rows = {}, []
    for k in ks:
        cells = [h for h in owner if owner[h] == k]
        ch = ch_proxy(cells)
        a, b, inside, th = th_of(cells, ch)
        seg[k] = (a, b)
        c, s = math.cos(th), math.sin(th)
        perp = [abs(-(centre(h)[0] - centre(ch)[0]) * s + (centre(h)[1] - centre(ch)[1]) * c) for h in cells]
        rows.append(dict(k=k, cells=len(cells), nodes=sum(1 for v in nodes if owner.get((v[3], v[4])) == k),
                         inside=inside, D=2 * inside, cover=sum(p <= OMEGA for p in perp) / len(cells),
                         farthest=max(perp) / W, pieces=len(pieces(cells)), bearing=round(math.degrees(th)), ch=ch))
    order = order_fn(seg)
    transit, enter, turn, pts = tour_stats(bs, seg, order)
    return rows, dict(transit=transit, turn=turn, inside=sum(r["inside"] for r in rows), order=order, pts=pts,
                      seg=seg)


def run_map(K, seed, L, policy, g=None):
    g = g or domain(K, seed)
    land = set(g["domain"])
    nodes = [v for v in g["nodes"] if (v[3], v[4]) in land]
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    bs = ((min(xs) + max(xs)) / 2, min(ys) - 1000.0)
    km, _, _, _ = partition(land, CAP, random.Random(seed))
    hk = lambda seg: [(sorted(seg)[i], d) for i, d in held_karp(bs, [seg[k] for k in sorted(seg)])]
    base = evaluate(km, lambda c, ch: best_line(c, ch), nodes, bs, hk)
    lo, th, lane, st = lane_partition(land, CAP, L)
    along = lambda c, ch: line(c, ch, th) + (th,)
    ln = evaluate(lo, along, nodes, bs, lambda seg: serpentine(lo, lane, th, seg, nodes, bs, policy))
    lhk = evaluate(lo, along, nodes, bs, hk) if len(set(lo.values())) <= 12 else None
    return dict(g=g, land=land, nodes=nodes, bs=bs, km=km, base=base, lo=lo, th=th, lane=lane, st=st, lane_=ln,
                lane_hk=lhk)


# ---------------------------------------------------------------- figures (no text, CLAUDE.md §8 item 63)
def frame(ax, land):
    xs, ys = [centre(h)[0] for h in land], [centre(h)[1] for h in land]
    ax.set_xlim(min(xs) - W, max(xs) + W)
    ax.set_ylim(min(ys) - 1.25 * 1000 - W, max(ys) + W)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.plot([max(xs) - 1000, max(xs)], [min(ys) - .6 * W] * 2, color=INK, lw=2)


def cells(ax, hs, col, **kw):
    ax.add_collection(PolyCollection([corners(h) for h in hs], facecolors=col, edgecolors=SURF, linewidths=.3,
                                     **kw))


def borders(ax, owner, lw=1.3):
    segs = []
    for h in owner:
        v, (cx, cy) = corners(h), centre(h)
        for j in range(6):
            p, q = v[j], v[(j + 1) % 6]
            n = cell_at(p[0] + q[0] - cx, p[1] + q[1] - cy)
            if n not in owner or owner[n] != owner[h]:
                segs.append((p, q))
    ax.add_collection(LineCollection(segs, colors=INK, linewidths=lw, zorder=3))


def water(ax, g):
    hs = [h for h in g["final"] if h not in set(g["domain"])]
    ax.add_collection(PolyCollection([corners(h) for h in hs], facecolors="#dbe9f8", edgecolors=WATER, hatch="////",
                                     linewidths=0, zorder=0))


def tourplot(ax, ev, bs):
    pts = ev["pts"]
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        inside = i % 2 == 1 and i < len(pts) - 2
        ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, lw=2.2 if inside else 1.1,
                                     color=INK if inside else INK2, ls="-" if inside else (0, (3, 2)), zorder=6))
    ax.scatter(*bs, marker="s", s=60, color=INK, zorder=7)


def step_figures(R, figs, tag):
    g, land, lo, lane, th, st = R["g"], R["land"], R["lo"], R["lane"], R["th"], R["st"]
    os.makedirs(figs, exist_ok=True)
    fig, axs = plt.subplots(2, 3, figsize=(18, 13), dpi=130, facecolor=SURF)
    axs = axs.ravel()
    # 1 the domain and its nodes
    ax = axs[0]; frame(ax, land); water(ax, g); cells(ax, list(land), LAND)
    ax.scatter([v[1] for v in R["nodes"]], [v[2] for v in R["nodes"]], s=.3, color=INK2, alpha=.5, rasterized=True)
    ax.scatter(*R["bs"], marker="s", s=60, color=INK)
    # 2 direction scan: cost per bearing (best offset), polar, the chosen bearing marked
    ax = fig.add_subplot(2, 3, 2, projection="polar"); axs[1].remove()
    cost = {}
    for c, nl, b, off in st["scan"]:
        cost[b] = min(cost.get(b, 1e9), c + nl / 100)
    bb = np.array(sorted(cost)); cc = np.array([cost[b] for b in bb])
    r_ = cc.max() + 1 - cc   # longer = better
    ang = np.radians(np.r_[bb, bb + 180, bb[:1]])
    ax.plot(ang, np.r_[r_, r_, r_[:1]], color=CAT[0], lw=1.8)
    ax.fill(ang, np.r_[r_, r_, r_[:1]], color=CAT[0], alpha=.15)
    ax.plot([th, th + math.pi], [r_.max()] * 2, "o", color=CAT[3], ms=8)
    ax.plot([th, th + math.pi], [0, 0], color=CAT[3])
    ax.set_yticklabels([]); ax.set_xticklabels([])
    # 3 lanes at the chosen bearing and offset (alternating shades)
    ax = axs[2]; frame(ax, land); water(ax, g)
    cells(ax, list(land), [["#c9dcf3", "#9fc3ea"][lane[h] % 2] for h in land])
    # 4 chunks along each lane piece, before repair; fragments hatched
    ax = axs[3]; frame(ax, land); water(ax, g)
    cut = st["cut"]
    cells(ax, list(cut), [CAT[cut[h] % len(CAT)] for h in cut], alpha=.45)
    borders(ax, cut, lw=1.0)
    if st["frag"]:
        ax.add_collection(PolyCollection([corners(h) for h in st["frag"]], facecolors="none", edgecolors=INK,
                                         hatch="xxx", linewidths=0, zorder=4))
    # 5 final lane clusters, coloured in visit order (dark first), lines and the boustrophedon tour
    ax = axs[4]; frame(ax, land); water(ax, g)
    ev = R["lane_"][1]
    rank = {k: i for i, (k, d) in enumerate(ev["order"])}
    cm = plt.get_cmap("Blues")
    nK = len(rank)
    cells(ax, list(lo), [cm(.85 - .6 * rank[lo[h]] / max(1, nK - 1)) for h in lo], alpha=.75)
    borders(ax, lo)
    tourplot(ax, ev, R["bs"])
    for r in R["lane_"][0]:
        ax.scatter(*centre(r["ch"]), marker="*", s=110, color=CAT[2], edgecolor=INK, lw=.5, zorder=8)
    # 6 the k-medoids partition of partition.py with its longest lines and Held-Karp tour, same colouring
    ax = axs[5]; frame(ax, land); water(ax, g)
    evb = R["base"][1]
    rank = {k: i for i, (k, d) in enumerate(evb["order"])}
    km = R["km"]
    cells(ax, list(km), [cm(.85 - .6 * rank[km[h]] / max(1, len(rank) - 1)) for h in km], alpha=.75)
    borders(ax, km)
    tourplot(ax, evb, R["bs"])
    for r in R["base"][0]:
        ax.scatter(*centre(r["ch"]), marker="*", s=110, color=CAT[2], edgecolor=INK, lw=.5, zorder=8)
    strip_text(fig)
    out = os.path.join(figs, f"restructure-{tag}-steps.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    plt.close(fig)
    # River coverage: cells within omega of the line (dark), outside (light); lane left, k-medoids right
    fig, axs = plt.subplots(1, 2, figsize=(14, 7.5), dpi=130, facecolor=SURF)
    for ax, own, (rows, ev) in ((axs[0], lo, R["lane_"]), (axs[1], R["km"], R["base"])):
        frame(ax, land); water(ax, g)
        bear = {r["k"]: math.radians(r["bearing"]) for r in rows}
        chs = {r["k"]: r["ch"] for r in rows}
        col = []
        for h in own:
            k = own[h]; t = bear[k]
            p = abs(-(centre(h)[0] - centre(chs[k])[0]) * math.sin(t) + (centre(h)[1] - centre(chs[k])[1]) * math.cos(t))
            col.append(CAT[0] if p <= OMEGA else "#c9dcf3")
        cells(ax, list(own), col, alpha=.8)
        borders(ax, own)
        for k, (a, b) in ev["seg"].items():
            ax.plot([a[0], b[0]], [a[1], b[1]], color=CAT[3], lw=2, zorder=6)
    strip_text(fig)
    out2 = os.path.join(figs, f"restructure-{tag}-river.png")
    fig.savefig(out2, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    plt.close(fig)
    return out, out2


def policy_figure(R, figs, tag):
    """The same lane clusters ordered by each policy: visit rank as shade (dark first), the tour."""
    g, land, lo = R["g"], R["land"], R["lo"]
    fig, axs = plt.subplots(1, 4, figsize=(24, 7.5), dpi=120, facecolor=SURF)
    cm = plt.get_cmap("Blues")
    along = lambda c, ch: line(c, ch, R["th"]) + (R["th"],)
    out = {}
    for ax, pol in zip(axs, ("short", "big", "dense", "weak")):
        rows, ev = evaluate(lo, along, R["nodes"], R["bs"],
                            lambda seg: serpentine(lo, R["lane"], R["th"], seg, R["nodes"], R["bs"], pol))
        rank = {k: i for i, (k, d) in enumerate(ev["order"])}
        frame(ax, land); water(ax, g)
        cells(ax, list(lo), [cm(.85 - .6 * rank[lo[h]] / max(1, len(rank) - 1)) for h in lo], alpha=.8)
        borders(ax, lo)
        tourplot(ax, ev, R["bs"])
        out[pol] = [k for k, d in ev["order"]]
    strip_text(fig)
    f = os.path.join(figs, f"restructure-{tag}-policy.png")
    fig.savefig(f, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    plt.close(fig)
    return f, out


def summary(R):
    out = {}
    for name in ("base", "lane_", "lane_hk"):
        if R[name] is None:
            continue
        rows, ev = R[name]
        n = sum(r["cells"] for r in rows)
        out[name] = dict(clusters=len(rows), cells_max=max(r["cells"] for r in rows),
                         cells_min=min(r["cells"] for r in rows),
                         D_mean=np.mean([r["D"] for r in rows]), D_min=min(r["D"] for r in rows),
                         cover=sum(r["cover"] * r["cells"] for r in rows) / n,
                         farthest=max(r["farthest"] for r in rows), inside_km=ev["inside"] / 1000,
                         transit_km=ev["transit"] / 1000, turn=ev["turn"],
                         pieces=max(r["pieces"] for r in rows))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clusters", type=int, default=4)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--lane", type=float, default=4.5, help="lane width, cells (River: 3.5)")
    ap.add_argument("--policy", default="short", choices=("short", "big", "dense", "weak"))
    ap.add_argument("--figs")
    ap.add_argument("--campaign", action="store_true", help="the 40 mission maps, lane widths 3.5 / 4.5 / 6")
    ap.add_argument("--out", help="campaign: folder for restructure-maps.csv")
    a = ap.parse_args()
    if not a.campaign:
        R = run_map(a.clusters, a.seed, a.lane, a.policy)
        R["L"] = a.lane
        for name, s in summary(R).items():
            print(name, {k: round(v, 3) if isinstance(v, float) else v for k, v in s.items()})
        print("bearing", round(math.degrees(R["th"])), "offset", round(R["st"]["off"], 2),
              "order", R["lane_"][1]["order"])
        if a.figs:
            print(*step_figures(R, a.figs, f"k{a.clusters}-s{a.seed}"))
            print(*policy_figure(R, a.figs, f"k{a.clusters}-s{a.seed}"))
            for r in R["lane_"][0]:
                print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
        return
    maps = [(K, s) for K, s in ORIG.items()]
    for f in sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../docs/data/mission/camp"))):
        K, s = f[1:].split("-s")
        maps.append((int(K), int(s)))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "restructure-maps.csv"), "w", newline="") as fo:
        w = None
        for K, s in maps:
            g = domain(K, s)
            for L in (3.5, 4.5, 6.0):
                R = run_map(K, s, L, a.policy, g)
                for name, d in summary(R).items():
                    row = dict(map=f"k{K}-s{s}", K=K, seed=s,
                               partition={"base": "kmedoids", "lane_": "lane", "lane_hk": "lane-hk"}[name],
                               lane=L if name != "base" else "", bearing=round(math.degrees(R["th"])) if name != "base" else "")
                    row.update({k: round(v, 4) if isinstance(v, float) else v for k, v in d.items()})
                    if name == "base" and L != 3.5:
                        continue
                    if w is None:
                        w = csv.DictWriter(fo, fieldnames=list(row))
                        w.writeheader()
                    w.writerow(row)
            print(f"k{K}-s{s} done", flush=True)


if __name__ == "__main__":
    main()
