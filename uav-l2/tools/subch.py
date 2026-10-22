"""Baseline subCH (CLAUDE.md §8 item 114): the pre-existing clusters split around critical cells far apart.

    from subch import subch_partition; owner, seeds = subch_partition(SRC_WORK, dmin=6, minsize=20)

SRC_WORK is a mission.py work folder of the same map with k-medoids clusters, deployed (roles) and planned.
Per cluster:
  1 its critical cells (river_plan: the CH's cell, global and local outliers)
  2 seeds: the CH's cell, then repeatedly the critical cell farthest from the seeds while it is at least DMIN cells
    from every seed (critical cells closer than that share a sub-cluster)
  3 sub-clusters: multi-source breadth-first growth from the seeds over the cluster's cells (each cell joins the
    seed whose wave reaches it first, so every sub-cluster is connected); a sub-cluster smaller than MINSIZE cells
    joins the neighbouring one it shares the most cell edges with
The new clusters are then deployed and flown like any cluster (mission.py --partition subch): straight across their
CH, which uav-coop-deploy picks as the strongest node (the strongest critical cell of the sub-cluster).
"""
import csv, heapq, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../uav-coop2/tools"))
from river_plan import NB, hexdist, load, load_around, plan  # noqa: E402


def split(cells, crit, ch, dmin, minsize):
    seeds = [ch]
    while True:
        far = [c for c in crit if min(hexdist(c, s) for s in seeds) >= dmin]
        if not far:
            break
        seeds.append(max(sorted(far), key=lambda c: min(hexdist(c, s) for s in seeds)))
    lab = {s: i for i, s in enumerate(seeds)}
    front = list(seeds)
    while front:
        nxt = []
        for v in front:
            for d in NB:
                g = (v[0] + d[0], v[1] + d[1])
                if g in cells and g not in lab:
                    lab[g] = lab[v]
                    nxt.append(g)
        front = nxt
    assert len(lab) == len(cells), "cluster not connected"
    while True:
        size = {i: sum(1 for v in lab.values() if v == i) for i in set(lab.values())}
        small = [i for i in sorted(size, key=size.get) if size[i] < minsize]
        if not small or len(size) == 1:
            break
        i = small[0]
        border = {}
        for v, li in lab.items():
            if li != i:
                continue
            for d in NB:
                g = (v[0] + d[0], v[1] + d[1])
                if g in lab and lab[g] != i:
                    border[lab[g]] = border.get(lab[g], 0) + 1
        j = max(sorted(border), key=border.get)
        lab = {v: (j if li == i else li) for v, li in lab.items()}
    ids = {li: n for n, li in enumerate(sorted(set(lab.values())))}
    return {v: ids[li] for v, li in lab.items()}, [s for n, s in enumerate(seeds) if n in ids]


def split2(cells, crit, ch):
    """subCH-K (item 118): exactly two connected halves of equal size, grown from the two critical cells farthest
    apart (the CH and the cell farthest from it if the cluster has one critical cell); the smaller half takes the
    next unclaimed cell next to it, nearest its seed first."""
    crit = sorted(set(crit) | {ch})
    seeds = list(max(((x, y) for x in crit for y in crit), key=lambda p: (hexdist(*p), p)))
    if seeds[0] == seeds[1]:
        seeds[1] = max(sorted(cells), key=lambda c: hexdist(c, ch))
    lab, size, heap = {seeds[0]: 0, seeds[1]: 1}, [1, 1], [[], []]

    def push(v, i):
        for d in NB:
            g = (v[0] + d[0], v[1] + d[1])
            if g in cells and g not in lab:
                heapq.heappush(heap[i], (hexdist(g, seeds[i]), g))

    push(seeds[0], 0)
    push(seeds[1], 1)
    while len(lab) < len(cells):
        for i in sorted((0, 1), key=lambda i: size[i]):
            while heap[i] and heap[i][0][1] in lab:
                heapq.heappop(heap[i])
            if heap[i]:
                v = heapq.heappop(heap[i])[1]
                lab[v], size[i] = i, size[i] + 1
                push(v, i)
                break
        else:
            raise AssertionError("cluster not connected")
    return lab, seeds


def subch_partition(src, dmin=6, minsize=20, pairs=False):
    """{cell: new cluster index (0-based)}, and the seeds per original cluster. pairs: split2 (subCH-K)."""
    K = json.load(open(f"{src}/map.json"))["clusters"]
    owner, seeds, base = {}, {}, 0
    for k in range(1, K + 1):
        cells = {(int(r["q"]), int(r["r"])) for r in csv.DictReader(open(f"{src}/c{k}-cells.csv"))}
        geo = load(f"{src}/d{k}", f"{src}/c{k}-path-s35.csv")
        P = plan(geo, reentry=True, domain_sc=load_around(f"{src}/domain-cl.csv") if os.path.exists(f"{src}/domain-cl.csv")
                 else None)
        lab, sd = split2(cells, P["crit"], P["ch"]) if pairs else split(cells, P["crit"], P["ch"], dmin, minsize)
        for v, li in lab.items():
            owner[v] = base + li
        seeds[k] = sd
        base += max(lab.values()) + 1
    return owner, seeds
