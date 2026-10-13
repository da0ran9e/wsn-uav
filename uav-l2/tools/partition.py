"""Phase 0 on a layer-2 domain: split its land cells into clusters of at most --cap cells (CLAUDE.md §8
items 38, 61). No CH yet.

    python3 tools/partition.py --domain docs/data/domain-lakes --caps 80,65 --figs docs/figures

Cells are the unit. Distance = hops between neighbouring land cells (so a lake is walked around, not
crossed). k = ceil(cells / cap). Capacitated k-medoids on that distance:
  1  medoids: farthest-point sampling from a random land cell;
  2  assign by growing all clusters at once from their medoids, in order of distance: a cell goes to the
     first cluster that reaches it while it still has room, so every cluster is connected by construction;
  3  cells left over (walled in by full clusters) go to the smallest touching cluster; then, while a
     cluster is over the cap, load is pushed along a chain of touching clusters to one with room: at each
     link one border cell moves to the next cluster, never one whose loss would split its cluster;
  4  medoid of each cluster = its cell with the least total distance to the others; repeat 2-4 until the
     medoids no longer move.
Writes DOMAIN-clusters-capC.csv (q, r, cluster) per cap and FIGS/partition.png.
"""
import argparse, csv, heapq, math, os, random
from collections import deque

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

from map_gen import AREA, NB, W, cell_at, centre, corners

INK, INK2, SURF, WATER = "#0b0b0b", "#52514e", "#fcfcfb", "#3987e5"
CAT = ["#1c5cab", "#1baf7a", "#eda100", "#e34948", "#8e5ad6", "#0d366b", "#52514e"]


def bfs(src, land):
    d, todo = {src: 0}, deque([src])
    while todo:
        h = todo.popleft()
        for dq, dr in NB:
            n = (h[0] + dq, h[1] + dr)
            if n in land and n not in d:
                d[n] = d[h] + 1
                todo.append(n)
    return d


def pieces(cells):
    S, seen, out = set(cells), set(), []
    for h in cells:
        if h in seen:
            continue
        comp, todo = [], [h]
        seen.add(h)
        while todo:
            x = todo.pop()
            comp.append(x)
            for dq, dr in NB:
                n = (x[0] + dq, x[1] + dr)
                if n in S and n not in seen:
                    seen.add(n)
                    todo.append(n)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def rebalance(owner, size, cap, land):
    """Push load from clusters over the cap to clusters with room, along chains of touching clusters."""
    moves = 0
    while max(size) > cap and moves < 10 * len(owner):
        src = max(range(len(size)), key=lambda i: size[i])
        adj = {}   # cluster adjacency
        for h, i in owner.items():
            for dq, dr in NB:
                n = (h[0] + dq, h[1] + dr)
                if n in owner and owner[n] != i:
                    adj.setdefault(i, set()).add(owner[n])
        prev, todo, dst = {src: None}, deque([src]), None
        while todo and dst is None:
            x = todo.popleft()
            for y in sorted(adj.get(x, ())):
                if y not in prev:
                    prev[y] = x
                    if size[y] < cap:
                        dst = y
                        break
                    todo.append(y)
        if dst is None:
            break
        chain = [dst]
        while prev[chain[-1]] is not None:
            chain.append(prev[chain[-1]])
        chain.reverse()   # src ... dst
        for x, y in zip(chain, chain[1:]):
            mine = [h for h in owner if owner[h] == x]
            best = None
            for h in mine:
                ny = sum((h[0] + dq, h[1] + dr) in owner and owner[(h[0] + dq, h[1] + dr)] == y for dq, dr in NB)
                if ny and (best is None or ny > best[0]) and len(pieces([c for c in mine if c != h])) == 1:
                    best = (ny, h)
            if best is None:
                return moves
            owner[best[1]] = y
            size[x] -= 1
            size[y] += 1
            moves += 1
    return moves


def partition(land, cap, rng):
    cells = sorted(land)
    k = math.ceil(len(cells) / cap)
    med = [rng.choice(cells)]
    dist = {med[0]: bfs(med[0], land)}
    while len(med) < k:   # farthest point
        far = max(cells, key=lambda h: (min(dist[m][h] for m in med), h))
        med.append(far)
        dist[far] = bfs(far, land)
    for it in range(1, 101):
        owner, size = {}, [0] * k
        heap = [(0, i, m) for i, m in enumerate(med)]
        while heap:
            d, i, h = heapq.heappop(heap)
            if h in owner or size[i] >= cap:
                continue
            owner[h] = i
            size[i] += 1
            for dq, dr in NB:
                n = (h[0] + dq, h[1] + dr)
                if n in land and n not in owner:
                    heapq.heappush(heap, (d + 1, i, n))
        over = 0
        left = [h for h in cells if h not in owner]
        while left:   # walled in by full clusters: join the smallest touching cluster
            for h in list(left):
                nbrs = {owner[(h[0] + dq, h[1] + dr)] for dq, dr in NB if (h[0] + dq, h[1] + dr) in owner}
                if nbrs:
                    j = min(nbrs, key=lambda j: (size[j], j))
                    owner[h] = j
                    size[j] += 1
                    over += 1
                    left.remove(h)
        rebalance(owner, size, cap, land)
        over = sum(max(0, s_ - cap) for s_ in size)
        new = []
        for i in range(k):
            mine = [h for h in cells if owner[h] == i]
            sub = set(mine)
            new.append(min(mine, key=lambda c: (sum(bfs(c, sub).values()), c)))
        if new == med:
            break
        med = new
        for m in med:
            if m not in dist:
                dist[m] = bfs(m, land)
    return owner, med, it, over


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, help="prefix of map_gen / domain_gallery outputs")
    ap.add_argument("--caps", default="80,65", help="upper bounds on cluster size, cells")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--figs", required=True)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.domain + "-cells.csv")))
    land = {(int(r["q"]), int(r["r"])) for r in rows if r["type"] == "land"}
    water = [(int(r["q"]), int(r["r"])) for r in rows if r["type"] != "land"]
    nodes = [(float(r["x"]), float(r["y"]), (int(r["q"]), int(r["r"]))) for r in csv.DictReader(open(a.domain + "-nodes.csv"))]
    caps = [int(c) for c in a.caps.split(",")]
    fig, axs = plt.subplots(1, len(caps), figsize=(7.5 * len(caps), 8.2), dpi=140, facecolor=SURF)
    axs = [axs] if len(caps) == 1 else axs
    xs = [centre(h)[0] for h in land | set(water)]; ys = [centre(h)[1] for h in land | set(water)]
    for ax, cap in zip(axs, caps):
        owner, med, it, over = partition(land, cap, random.Random(a.seed))
        k = len(med)
        with open(f"{a.domain}-clusters-cap{cap}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["q", "r", "cluster"])
            for h in sorted(owner):
                w.writerow([h[0], h[1], owner[h]])
        ax.add_collection(PolyCollection([corners(h) for h in land], facecolors=[CAT[owner[h] % len(CAT)] for h in land],
                                         alpha=.32, edgecolors=SURF, linewidths=.3, zorder=0))
        ax.add_collection(PolyCollection([corners(h) for h in water], facecolors="#dbe9f8", edgecolors=WATER,
                                         hatch="////", linewidths=0, zorder=0))
        segs = []   # borders: between clusters, and with water / outside
        for h in land:
            v = corners(h)
            cx, cy = centre(h)
            for j in range(6):
                p, q = v[j], v[(j + 1) % 6]
                n = cell_at(p[0] + q[0] - cx, p[1] + q[1] - cy)
                if n not in land or owner[n] != owner[h]:
                    segs.append((p, q))
        ax.add_collection(LineCollection(segs, colors=INK, linewidths=1.4, zorder=3))
        ax.scatter([x for x, y, h in nodes], [y for x, y, h in nodes], s=.25, color=INK2, alpha=.5, zorder=1,
                   rasterized=True)
        stats = []
        for i, m in enumerate(med):
            mine = [h for h in land if owner[h] == i]
            nn = sum(1 for _, _, h in nodes if owner.get(h) == i)
            ecc = max(bfs(m, set(mine)).values())
            ax.text(*centre(m), f"C{i + 1}", ha="center", va="center", fontsize=11, fontweight="bold", color=INK,
                    zorder=5, bbox=dict(boxstyle="round,pad=.25", facecolor=SURF, edgecolor=CAT[i % len(CAT)], lw=1.5))
            stats.append(f"C{i + 1}: {len(mine)} cell, {len(mine) * AREA / 1e6:.2f} km², {nn} node, "
                         f"bán kính {ecc} bước".replace(".", ","))
            print(f"cap {cap}: C{i + 1} {len(mine)} cells, {nn} nodes, radius {ecc} hops, medoid {m}")
        print(f"cap {cap}: k = {k}, {it} iterations, {over} cells placed over the cap, "
              f"pieces per cluster {[len(pieces([h for h in land if owner[h] == i])) for i in range(k)]}")
        ax.set_xlim(min(xs) - W, max(xs) + W); ax.set_ylim(min(ys) - W, max(ys) + W)
        ax.set_aspect("equal"); ax.set_facecolor(SURF); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(f"Chặn trên {cap} cell / cluster → {k} cluster\n" + "\n".join(stats), loc="left", fontsize=9,
                     color=INK)
        ax.plot([max(xs) - 1000, max(xs)], [min(ys) - .4 * W] * 2, color=INK, lw=2)
        ax.text(max(xs) - 500, min(ys) - .2 * W, "1 km", ha="center", fontsize=8, color=INK)
    fig.suptitle(f"Chia cluster trên miền có hồ ({len(land)} cell đất): k-medoids theo số bước đi vòng qua hồ, "
                 "có chặn trên, cluster liền mạch; gạch chéo = hồ; chưa chọn CH", x=.01, y=1.05, ha="left",
                 fontsize=11, color=INK)
    out = os.path.join(a.figs, "partition.png")
    fig.savefig(out, facecolor=SURF, bbox_inches="tight", pad_inches=.08)
    print(f"  {out}")


if __name__ == "__main__":
    main()
