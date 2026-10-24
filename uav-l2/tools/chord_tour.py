"""CHORD-T, layer 2 (CLAUDE.md §8 item 136): each cluster still flown straight across its CH, but the bearings chosen
jointly with team 1's tour instead of each cluster's longest in-cluster line on its own.

The longest line of every cluster points anywhere, so team 1 spends much of its tour turning (Dubins, radius RHO)
between them. CHORD-T keeps the clusters and the CH and lets the BS pick, per cluster, among the bearings whose
in-cluster flight is at least FRAC of the longest and at least CLUE of one copy of the clue set, the combination and
visiting order with the least sum_k n_k leave_k (n_k the cluster's critical cells: the mean time a critical cell is
left behind, mission_policy's latency tour), Dubins transits, free heading at the BS. Exact Held-Karp over
(cluster, bearing, direction) up to EXACT clusters, choose_heur beyond (item 149).

    from chord_tour import choose; picks = choose(bs, cands, n)   # cands[k] = [leg, ...], leg = dict(L, poses)
"""
import itertools

import dubins
from tour_heur import order_segments

RHO, V1 = 50.0 ** 2 / 9.80665, 50.0
EXACT = 13


def choose(bs, cands, n, lam=0.0):
    """cands[k]: legs dict(L=metres, poses=[(start pose, end pose) flown one way, (...) the other]; optional fix:
    seconds the leg's delivery still lacks, added to its time, and tail: its estimated River time); n[k] critical
    cells. lam > 0 (item 159): the objective also counts lam x sum_k n_k x the latest leave + tail, so clusters
    whose River takes long go earlier (heuristic in Held-Karp: per state the best of the summed objective). Returns
    {k: index of the chosen leg} and the order [(k, leg, direction)]."""
    ks = sorted(cands)
    if len(ks) > EXACT:
        return choose_heur(bs, cands, n)
    N = sum(n.values())
    T = {(k, c): cands[k][c]["L"] / V1 + cands[k][c].get("fix", 0.0) for k in ks for c in range(len(cands[k]))}
    tail = {(k, c): cands[k][c].get("tail", 0.0) for k in ks for c in range(len(cands[k]))}
    nodes = [(k, c, d) for k in ks for c in range(len(cands[k])) for d in (0, 1)]
    start = {x: cands[x[0]][x[1]]["poses"][x[2]][0] for x in nodes}
    end = {x: cands[x[0]][x[1]]["poses"][x[2]][1] for x in nodes}
    link = {(x, y): dubins.length(end[x], start[y], RHO) for x, y in itertools.product(nodes, nodes) if x[0] != y[0]}
    idx = {k: i for i, k in enumerate(ks)}
    st = {}   # (mask, last) -> (objective, time, previous state, summed latency, latest leave + tail)
    for x in nodes:
        t = dubins.free_start(bs, start[x], RHO) / V1 + T[x[:2]]
        mx = t + tail[x[:2]]
        st[(1 << idx[x[0]], x)] = (n[x[0]] * t + lam * N * mx, t, None, n[x[0]] * t, mx)
    for mask in range(1, 1 << len(ks)):   # a transition only adds clusters: increasing masks
        for x in nodes:
            if (mask, x) not in st:
                continue
            _, t, _, lat, mx = st[(mask, x)]
            for y in nodes:
                if mask >> idx[y[0]] & 1:
                    continue
                t2 = t + link[(x, y)] / V1 + T[y[:2]]
                lat2, mx2 = lat + n[y[0]] * t2, max(mx, t2 + tail[y[:2]])
                key, val = (mask | 1 << idx[y[0]], y), lat2 + lam * N * mx2
                if key not in st or val < st[key][0]:
                    st[key] = (val, t2, (mask, x), lat2, mx2)
    full = (1 << len(ks)) - 1
    best = min((st[(full, x)][0], (full, x)) for x in nodes if (full, x) in st)[1]
    order, s = [], best
    while s:
        order.append(s[1])
        s = st[s][2]
    order.reverse()
    return {k: c for k, c, _ in order}, order


def choose_heur(bs, cands, n):
    """Beyond EXACT clusters (Held-Karp's 2^K states): an order, then every cluster's candidate and direction exact
    for it (a dynamic programme over (candidate, direction), each leg's metres times the critical cells not yet left:
    the latency sum, as tour_heur.directions). The order starts from tour_heur.order_segments over each cluster's
    first candidate (its longest line) and is improved by single moves and 2-opt reversals, each scored by the
    programme, until neither helps."""
    ks = sorted(cands)
    nodes = {k: [(c, d) for c in range(len(cands[k])) for d in (0, 1)] for k in ks}
    pose = lambda k, c, d, j: cands[k][c]["poses"][d][j]
    start = {(k, *x): dubins.free_start(bs, pose(k, *x, 0), RHO) for k in ks for x in nodes[k]}
    link = {(k, *x, k2, *y): dubins.length(pose(k, *x, 1), pose(k2, *y, 0), RHO)
            for k in ks for k2 in ks if k != k2 for x in nodes[k] for y in nodes[k2]}

    def dp(order):
        rem = [sum(n[k] for k in order[i:]) for i in range(len(order))]
        k0 = order[0]
        best = {x: ((start[(k0, *x)] + cands[k0][x[0]]["L"]) * rem[0], [x]) for x in nodes[k0]}
        for i in range(1, len(order)):
            kp, k = order[i - 1], order[i]
            best = {y: min((v + (link[(kp, *x, k, *y)] + cands[k][y[0]]["L"]) * rem[i], p + [y])
                           for x, (v, p) in best.items()) for y in nodes[k]}
        return min(best.values())

    seg = {k: (cands[k][0]["poses"][0][0][:2], cands[k][0]["poses"][0][1][:2], cands[k][0]["L"]) for k in ks}
    order = [k for k, _ in order_segments(bs, seg, n)]
    cost, path = dp(order)
    improved = True
    while improved:
        improved = False
        moves = [order[:i] + order[i + 1:j] + [order[i]] + order[j:] for i in range(len(order)) for j in range(len(order) + 1)
                 if j not in (i, i + 1)] + \
                [order[:i] + order[i:j][::-1] + order[j:] for i in range(len(order)) for j in range(i + 2, len(order) + 1)]
        for o in moves:
            c, p = dp(o)
            if c < cost - 1e-6:
                order, cost, path, improved = o, c, p, True
                break
    out = [(k, c, d) for k, (c, d) in zip(order, path)]
    return {k: c for k, c, _ in out}, out
