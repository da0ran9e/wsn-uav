"""Team 1's tour over many cluster segments (more than Held-Karp can take): BS -> every segment, either way round
-> BS, shortest transit. Directions are exact for a given order (two-state dynamic programme); the order starts
from the nearest-end greedy tour and is improved by 2-opt and single moves until neither helps.

    from tour_heur import order_segments; order = order_segments(bs, seg)   # seg {k: (start, end, length)}
"""
import math


def directions(bs, seg, ks, weight=None, link=None):
    """Best directions for the order ks: (cost, [direction per segment]); direction 0 flies start -> end.
    cost: transit metres (weight None), or the latency sum_k weight_k * leave_k in metres of flight (each leg's
    length times the weight of the clusters not yet left, the one being flown included; no return leg).
    link {(k, d, k2, e): metres}: transits that replace the straight one (mission_policy.seams)."""
    ends = lambda k, d: (seg[k][0], seg[k][1]) if d == 0 else (seg[k][1], seg[k][0])
    rem = [sum(weight[k] for k in ks[i:]) for i in range(len(ks))] if weight else None

    def gap(p, i, e):   # p: the (segment, direction) flown before, None for the BS
        if p is None:
            return math.dist(bs, ends(ks[i], e)[0])
        return (link or {}).get((p[0], p[1], ks[i], e), math.dist(ends(*p)[1], ends(ks[i], e)[0]))
    leg = lambda i, p, e: (gap(p, i, e) + (seg[ks[i]][2] if weight else 0)) * (rem[i] if weight else 1)
    best = [(leg(0, None, d), [d]) for d in (0, 1)]
    for i in range(1, len(ks)):
        nb = []
        for e in (0, 1):
            c, p = min((best[d][0] + leg(i, (ks[i - 1], d), e), best[d][1]) for d in (0, 1))
            nb.append((c, p + [e]))
        best = nb
    back = (lambda d: 0.0) if weight else (lambda d: math.dist(ends(ks[-1], d)[1], bs))
    return min((best[d][0] + back(d), best[d][1]) for d in (0, 1))


def order_segments(bs, seg, weight=None, link=None):
    """[(k, direction)] of a short tour (weight None), or of a low-latency one (see directions)."""
    left, ks, pos = set(seg), [], bs
    while left:
        k = min(sorted(left), key=lambda k: min(math.dist(pos, seg[k][0]), math.dist(pos, seg[k][1])))
        ks.append(k)
        left.remove(k)
        pos = seg[k][1] if math.dist(pos, seg[k][0]) <= math.dist(pos, seg[k][1]) else seg[k][0]
    cost = directions(bs, seg, ks, weight, link)[0]
    better = True
    while better:
        better = False
        for i in range(len(ks) - 1):
            for j in range(i + 2, len(ks) + 1):
                cand = ks[:i] + ks[i:j][::-1] + ks[j:]
                c = directions(bs, seg, cand, weight, link)[0]
                if c < cost - 1e-6:
                    ks, cost, better = cand, c, True
        for i in range(len(ks)):
            for j in range(len(ks)):
                if i == j:
                    continue
                rest = ks[:i] + ks[i + 1:]
                cand = rest[:j] + [ks[i]] + rest[j:]
                c = directions(bs, seg, cand, weight, link)[0]
                if c < cost - 1e-6:
                    ks, cost, better = cand, c, True
                    break
    return list(zip(ks, directions(bs, seg, ks, weight, link)[1]))
