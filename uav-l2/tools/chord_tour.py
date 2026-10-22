"""CHORD-T, layer 2 (CLAUDE.md §8 item 136): each cluster still flown straight across its CH, but the bearings chosen
jointly with team 1's tour instead of each cluster's longest in-cluster line on its own.

The longest line of every cluster points anywhere, so team 1 spends much of its tour turning (Dubins, radius RHO)
between them. CHORD-T keeps the clusters and the CH and lets the BS pick, per cluster, among the bearings whose
in-cluster flight is at least FRAC of the longest and at least CLUE of one copy of the clue set, the combination and
visiting order with the least sum_k n_k leave_k (n_k the cluster's critical cells: the mean time a critical cell is
left behind, mission_policy's latency tour), Dubins transits, free heading at the BS. Exact Held-Karp over
(cluster, bearing, direction).

    from chord_tour import choose; picks = choose(bs, cands, n)   # cands[k] = [leg, ...], leg = dict(L, poses)
"""
import itertools

import dubins

RHO, V1 = 50.0 ** 2 / 9.80665, 50.0


def choose(bs, cands, n):
    """cands[k]: legs dict(L=metres, poses=[(start pose, end pose) flown one way, (...) the other]); n[k] critical
    cells. Returns {k: index of the chosen leg} and the order [(k, leg, direction)]."""
    ks = sorted(cands)
    nodes = [(k, c, d) for k in ks for c in range(len(cands[k])) for d in (0, 1)]
    start = {x: cands[x[0]][x[1]]["poses"][x[2]][0] for x in nodes}
    end = {x: cands[x[0]][x[1]]["poses"][x[2]][1] for x in nodes}
    link = {(x, y): dubins.length(end[x], start[y], RHO) for x, y in itertools.product(nodes, nodes) if x[0] != y[0]}
    idx = {k: i for i, k in enumerate(ks)}
    st = {}
    for x in nodes:
        t = (dubins.free_start(bs, start[x], RHO) + cands[x[0]][x[1]]["L"]) / V1
        st[(1 << idx[x[0]], x)] = (n[x[0]] * t, t, None)
    for mask in range(1, 1 << len(ks)):   # a transition only adds clusters: increasing masks
        for x in nodes:
            if (mask, x) not in st:
                continue
            lat, t, _ = st[(mask, x)]
            for y in nodes:
                if mask >> idx[y[0]] & 1:
                    continue
                t2 = t + (link[(x, y)] + cands[y[0]][y[1]]["L"]) / V1
                key, val = (mask | 1 << idx[y[0]], y), lat + n[y[0]] * t2
                if key not in st or val < st[key][0]:
                    st[key] = (val, t2, (mask, x))
    full = (1 << len(ks)) - 1
    best = min((st[(full, x)][0], (full, x)) for x in nodes if (full, x) in st)[1]
    order, s = [], best
    while s:
        order.append(s[1])
        s = st[s][2]
    order.reverse()
    return {k: c for k, c, _ in order}, order
