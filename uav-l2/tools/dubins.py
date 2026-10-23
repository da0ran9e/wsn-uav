"""Shortest path lengths of a fixed-wing at constant speed with a minimum turn radius r (Dubins 1957), for team 1's
transits between clusters (CLAUDE.md §8 item 117). Poses are (x, y, heading in radians).

    python3 tools/dubins.py      # checks against known cases
"""
import math

TAU = 2 * math.pi


def _mod(a):
    return a % TAU


def length(p0, p1, r):
    """Shortest of the six Dubins words (LSL, RSR, LSR, RSL, RLR, LRL) from pose p0 to pose p1, metres."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) / r
    th = math.atan2(dy, dx)
    a, b = _mod(p0[2] - th), _mod(p1[2] - th)
    sa, sb, ca, cb, cab = math.sin(a), math.sin(b), math.cos(a), math.cos(b), math.cos(a - b)
    best = math.inf
    tmp = 2 + d * d - 2 * cab + 2 * d * (sa - sb)                                   # LSL
    if tmp >= -1e-9:
        tmp = max(tmp, 0.0)
        y = math.atan2(cb - ca, d + sa - sb)
        best = min(best, _mod(-a + y) + math.sqrt(tmp) + _mod(b - y))
    tmp = 2 + d * d - 2 * cab + 2 * d * (sb - sa)                                   # RSR
    if tmp >= -1e-9:
        tmp = max(tmp, 0.0)
        y = math.atan2(ca - cb, d - sa + sb)
        best = min(best, _mod(a - y) + math.sqrt(tmp) + _mod(-b + y))
    tmp = -2 + d * d + 2 * cab + 2 * d * (sa + sb)                                  # LSR
    if tmp >= -1e-9:
        tmp = max(tmp, 0.0)
        p = math.sqrt(tmp)
        y = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p)
        best = min(best, _mod(-a + y) + p + _mod(-_mod(b) + y))
    tmp = d * d - 2 + 2 * cab - 2 * d * (sa + sb)                                   # RSL
    if tmp >= -1e-9:
        tmp = max(tmp, 0.0)
        p = math.sqrt(tmp)
        y = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, p)
        best = min(best, _mod(a - y) + p + _mod(_mod(b) - y))
    tmp = (6 - d * d + 2 * cab + 2 * d * (sa - sb)) / 8                             # RLR
    if abs(tmp) <= 1 + 1e-9:
        tmp = max(-1.0, min(1.0, tmp))
        p = _mod(TAU - math.acos(tmp))
        t = _mod(a - math.atan2(ca - cb, d - sa + sb) + p / 2)
        best = min(best, t + p + _mod(a - b - t + p))
    tmp = (6 - d * d + 2 * cab + 2 * d * (sb - sa)) / 8                             # LRL
    if abs(tmp) <= 1 + 1e-9:
        tmp = max(-1.0, min(1.0, tmp))
        p = _mod(TAU - math.acos(tmp))
        t = _mod(-a - math.atan2(ca - cb, d + sa - sb) + p / 2)
        best = min(best, t + p + _mod(_mod(b) - a - t + p))
    return best * r


def path(p0, p1, r, step=2.0):
    """Points every <= step m along the shortest of the six words from p0 to p1 (the path length() measures), and its
    length; for drawing team 1's transits."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) / r
    th = math.atan2(dy, dx)
    a, b = _mod(p0[2] - th), _mod(p1[2] - th)
    sa, sb, ca, cb, cab = math.sin(a), math.sin(b), math.cos(a), math.cos(b), math.cos(a - b)
    words = []
    tmp = 2 + d * d - 2 * cab + 2 * d * (sa - sb)
    if tmp >= -1e-9:
        y = math.atan2(cb - ca, d + sa - sb)
        words.append(("LSL", _mod(-a + y), math.sqrt(max(tmp, 0.0)), _mod(b - y)))
    tmp = 2 + d * d - 2 * cab + 2 * d * (sb - sa)
    if tmp >= -1e-9:
        y = math.atan2(ca - cb, d - sa + sb)
        words.append(("RSR", _mod(a - y), math.sqrt(max(tmp, 0.0)), _mod(-b + y)))
    tmp = -2 + d * d + 2 * cab + 2 * d * (sa + sb)
    if tmp >= -1e-9:
        q = math.sqrt(max(tmp, 0.0))
        y = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, q)
        words.append(("LSR", _mod(-a + y), q, _mod(-_mod(b) + y)))
    tmp = d * d - 2 + 2 * cab - 2 * d * (sa + sb)
    if tmp >= -1e-9:
        q = math.sqrt(max(tmp, 0.0))
        y = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, q)
        words.append(("RSL", _mod(a - y), q, _mod(_mod(b) - y)))
    tmp = (6 - d * d + 2 * cab + 2 * d * (sa - sb)) / 8
    if abs(tmp) <= 1 + 1e-9:
        q = _mod(TAU - math.acos(max(-1.0, min(1.0, tmp))))
        t = _mod(a - math.atan2(ca - cb, d - sa + sb) + q / 2)
        words.append(("RLR", t, q, _mod(a - b - t + q)))
    tmp = (6 - d * d + 2 * cab + 2 * d * (sb - sa)) / 8
    if abs(tmp) <= 1 + 1e-9:
        q = _mod(TAU - math.acos(max(-1.0, min(1.0, tmp))))
        t = _mod(-a - math.atan2(ca - cb, d + sa - sb) + q / 2)
        words.append(("LRL", t, q, _mod(_mod(b) - a - t + q)))
    word, *segs = min(words, key=lambda w: sum(w[1:]))
    x, y, h = p0
    pts = [(x, y)]
    for kind, u in zip(word, segs):
        n = max(1, math.ceil(u * r / step))
        for _ in range(n):
            v = u / n
            if kind == "S":
                x, y = x + r * v * math.cos(h), y + r * v * math.sin(h)
            else:
                sd = 1 if kind == "L" else -1
                x, y = x + sd * r * (math.sin(h + sd * v) - math.sin(h)), y - sd * r * (math.cos(h + sd * v) - math.cos(h))
                h += sd * v
            pts.append((x, y))
    return pts, sum(segs) * r


def path_csc(p0, p1, r, step=2.0):
    """Points every <= step m along the shortest turn-straight-turn word (LSL, RSR, LSR, RSL) from p0 to p1, and its
    length; for SWATH-K's turns between lanes at least 2r apart, where a CSC word is the shortest path."""
    def centre(p, side):   # side +1: left circle, -1: right
        return (p[0] - side * r * math.sin(p[2]), p[1] + side * r * math.cos(p[2]))

    best = None
    for s0, s1 in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        c0, c1 = centre(p0, s0), centre(p1, s1)
        dx, dy = c1[0] - c0[0], c1[1] - c0[1]
        D, phi = math.hypot(dx, dy), math.atan2(dy, dx)
        if s0 == s1:
            th = phi
        elif D < 2 * r:
            continue
        else:
            th = phi + s0 * math.asin(2 * r / D)
        t0 = (c0[0] + s0 * r * math.sin(th), c0[1] - s0 * r * math.cos(th))
        t1 = (c1[0] + s1 * r * math.sin(th), c1[1] - s1 * r * math.cos(th))
        sl = (t1[0] - t0[0]) * math.cos(th) + (t1[1] - t0[1]) * math.sin(th)
        if sl < -1e-6:
            continue
        a0, a1 = _mod(s0 * (th - p0[2])), _mod(s1 * (p1[2] - th))
        L = r * (a0 + a1) + max(sl, 0.0)
        if best is None or L < best[0]:
            best = (L, s0, s1, c0, c1, th, a0, a1, t0, t1)
    L, s0, s1, c0, c1, th, a0, a1, t0, t1 = best
    pts = []

    def arc(c, side, h0, sweep):
        n = max(1, math.ceil(sweep * r / step))
        for i in range(n + 1):
            h = h0 + side * sweep * i / n
            pts.append((c[0] + side * r * math.sin(h), c[1] - side * r * math.cos(h)))

    arc(c0, s0, p0[2], a0)
    n = max(1, math.ceil(math.dist(t0, t1) / step))
    pts += [(t0[0] + (t1[0] - t0[0]) * i / n, t0[1] + (t1[1] - t0[1]) * i / n) for i in range(1, n + 1)]
    arc(c1, s1, th, a1)
    return pts, L


def free_start(q, p1, r, n=72):
    """Shortest path from point q, any heading (the BS: team 1 takes off towards its first leg), to pose p1."""
    return min(length((q[0], q[1], TAU * i / n), p1, r) for i in range(n))


def free_end(p0, q, r, n=72):
    """Shortest path from pose p0 to point q, any final heading (back at the BS)."""
    return min(length(p0, (q[0], q[1], TAU * i / n), r) for i in range(n))


if __name__ == "__main__":
    r = 255.0
    cases = [((0, 0, 0), (1000, 0, 0), 1000.0),                            # straight on
             ((0, 0, 0), (0, 2 * r, math.pi), math.pi * r),                # U-turn into the next lane, 2r away
             ((0, 0, 0), (r, r, math.pi / 2), math.pi * r / 2),            # quarter circle left
             ((0, 0, 0), (r, -r, -math.pi / 2), math.pi * r / 2),          # quarter circle right
             ((0, 0, 0), (2000, 0, math.pi), None)]                        # turn back after 2 km: > 2000
    for p0, p1, want in cases:
        got = length(p0, p1, r)
        print(f"{p0} -> {p1}: {got:.1f} m" + (f" (expected {want:.1f})" if want else ""))
        assert want is None and got > 2000 or abs(got - want) < 1e-6 * max(1.0, want)
    # symmetry under reversing the path: from p1 reversed to p0 reversed
    import random
    rng = random.Random(1)
    for _ in range(2000):
        p0 = (rng.uniform(-3e3, 3e3), rng.uniform(-3e3, 3e3), rng.uniform(0, TAU))
        p1 = (rng.uniform(-3e3, 3e3), rng.uniform(-3e3, 3e3), rng.uniform(0, TAU))
        a = length(p0, p1, r)
        b = length((p1[0], p1[1], p1[2] + math.pi), (p0[0], p0[1], p0[2] + math.pi), r)
        assert abs(a - b) < 1e-6 * a and a >= math.dist(p0[:2], p1[:2]) - 1e-6, (p0, p1, a, b)
    print("ok: known cases, reversal symmetry, never shorter than the straight line")
