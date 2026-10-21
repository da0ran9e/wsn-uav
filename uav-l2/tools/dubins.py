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
