"""Phase 1 planning: exact Dubins lane ordering, and the speed-exposure bound.

Two questions this answers, both with numbers rather than argument:

1. How much of the fixed-wing sweep is forced OUTSIDE the search area by the
   turn radius, and how much of that is avoidable by ORDERING the lanes well?
   The lane-ordering problem is an asymmetric TSP whose cities are lanes and
   whose two "modes" are the two directions a lane can be flown. At operational
   size (10-12 lanes) it is small enough to solve EXACTLY by Held-Karp, so what
   is reported is the true optimum, not a heuristic's output.

2. What is the fastest the scout can fly and still deposit a usable cue set?
   The scout does not sense; it seeds ground detectors with reference data, and
   a node discriminates only in proportion to how much of that data it holds.
   Exposure time is a chord over the broadcast disc divided by speed, so speed
   trades directly against discrimination -- a tension classical coverage path
   planning does not have, because there the swath is binary.

Self-checking: every Dubins length is verified by integrating the returned
control word forward and asserting the endpoint matches the requested
configuration. A closed-form Dubins implementation that is subtly wrong still
returns plausible numbers, so this is not optional.

Run:  python3 tools/dubins_lanes.py
"""
import itertools
import math

TWO_PI = 2.0 * math.pi


def mod2pi(t):
    return t - TWO_PI * math.floor(t / TWO_PI)


# --------------------------------------------------------------------------
# Dubins shortest path.  Configurations are (x, y, theta); R is the minimum
# turning radius.  Returns (length, word, (t, p, q)) with segment lengths in
# NORMALISED units (multiply by R for metres).
# --------------------------------------------------------------------------

def _lsl(a, b, d):
    tmp = math.atan2(math.cos(b) - math.cos(a), d + math.sin(a) - math.sin(b))
    p_sq = 2 + d * d - 2 * math.cos(a - b) + 2 * d * (math.sin(a) - math.sin(b))
    if p_sq < 0:
        return None
    t = mod2pi(tmp - a)
    q = mod2pi(b - tmp)
    return t, math.sqrt(p_sq), q


def _rsr(a, b, d):
    tmp = math.atan2(math.cos(a) - math.cos(b), d - math.sin(a) + math.sin(b))
    p_sq = 2 + d * d - 2 * math.cos(a - b) + 2 * d * (math.sin(b) - math.sin(a))
    if p_sq < 0:
        return None
    t = mod2pi(a - tmp)
    q = mod2pi(tmp - b)
    return t, math.sqrt(p_sq), q


def _lsr(a, b, d):
    p_sq = -2 + d * d + 2 * math.cos(a - b) + 2 * d * (math.sin(a) + math.sin(b))
    if p_sq < 0:
        return None
    p = math.sqrt(p_sq)
    tmp = math.atan2(-math.cos(a) - math.cos(b), d + math.sin(a) + math.sin(b)) - math.atan2(-2.0, p)
    t = mod2pi(tmp - a)
    q = mod2pi(tmp - mod2pi(b))
    return t, p, q


def _rsl(a, b, d):
    p_sq = -2 + d * d + 2 * math.cos(a - b) - 2 * d * (math.sin(a) + math.sin(b))
    if p_sq < 0:
        return None
    p = math.sqrt(p_sq)
    tmp = math.atan2(math.cos(a) + math.cos(b), d - math.sin(a) - math.sin(b)) - math.atan2(2.0, p)
    t = mod2pi(a - tmp)
    q = mod2pi(mod2pi(b) - tmp)
    return t, p, q


# The CCC words are built geometrically rather than from a remembered closed
# form. The textbook LRL/RSR-style expressions are easy to transcribe with a
# sign flipped, and a wrong one still returns plausible lengths -- the first
# version of this file did exactly that and the integration check caught it
# (208 m endpoint error on LRL, every other word exact). The construction below
# places the middle circle explicitly, so it is checkable by eye.

def _ang(v):
    return math.atan2(v[1], v[0])


def _ccc(a, b, d, left_outer):
    """LRL (left_outer=True) or RLR. Returns the better of the two branches."""
    s = 1.0 if left_outer else -1.0
    p1, p2 = (0.0, 0.0), (d, 0.0)
    # outer turn centres sit one radius to the left (LRL) / right (RLR)
    c1 = (p1[0] - s * math.sin(a), p1[1] + s * math.cos(a))
    c3 = (p2[0] - s * math.sin(b), p2[1] + s * math.cos(b))
    v = (c3[0] - c1[0], c3[1] - c1[1])
    D = math.hypot(*v)
    if D > 4.0 or D < 1e-12:
        return None
    theta, phi = _ang(v), math.acos(D / 4.0)
    best = None
    for sign in (+1.0, -1.0):
        ang = theta + sign * phi
        c2 = (c1[0] + 2 * math.cos(ang), c1[1] + 2 * math.sin(ang))
        # outer arcs turn with sign s, the middle arc turns against it
        t = mod2pi(s * (_ang((c2[0] - c1[0], c2[1] - c1[1])) -
                        _ang((p1[0] - c1[0], p1[1] - c1[1]))))
        p = mod2pi(-s * (_ang((c3[0] - c2[0], c3[1] - c2[1])) -
                         _ang((c1[0] - c2[0], c1[1] - c2[1]))))
        q = mod2pi(s * (_ang((p2[0] - c3[0], p2[1] - c3[1])) -
                        _ang((c2[0] - c3[0], c2[1] - c3[1]))))
        L = t + p + q
        if best is None or L < best[0]:
            best = (L, (t, p, q))
    return best[1]


def _rlr(a, b, d):
    return _ccc(a, b, d, left_outer=False)


def _lrl(a, b, d):
    return _ccc(a, b, d, left_outer=True)


_WORDS = [("LSL", _lsl), ("RSR", _rsr), ("LSR", _lsr),
          ("RSL", _rsl), ("RLR", _rlr), ("LRL", _lrl)]


def dubins(q0, q1, R):
    """Shortest Dubins path length in metres, plus its word and segments."""
    dx, dy = q1[0] - q0[0], q1[1] - q0[1]
    D = math.hypot(dx, dy)
    d = D / R
    theta = mod2pi(math.atan2(dy, dx)) if D > 1e-12 else 0.0
    a = mod2pi(q0[2] - theta)
    b = mod2pi(q1[2] - theta)
    best = None
    for name, fn in _WORDS:
        r = fn(a, b, d)
        if r is None:
            continue
        L = sum(r)
        if best is None or L < best[0]:
            best = (L, name, r)
    if best is None:
        raise RuntimeError("no Dubins path")
    return best[0] * R, best[1], best[2]


def integrate(q0, word, seg, R):
    """Fly the control word forward; used only to verify the closed form."""
    x, y, th = q0
    for kind, s in zip(word, seg):
        L = s * R
        if kind == "S":
            x += L * math.cos(th)
            y += L * math.sin(th)
        else:
            turn = 1.0 if kind == "L" else -1.0
            dth = turn * s
            cx = x - turn * R * math.sin(th)
            cy = y + turn * R * math.cos(th)
            th2 = th + dth
            x = cx + turn * R * math.sin(th2)
            y = cy - turn * R * math.cos(th2)
            th = mod2pi(th2)
    return x, y, mod2pi(th)


def verify_dubins(R=63.7, n=400):
    """Every closed-form answer must reproduce the requested endpoint."""
    rng = _Lcg(12345)
    worst = 0.0
    for _ in range(n):
        q0 = (rng.uniform(-300, 300), rng.uniform(-300, 300), rng.uniform(0, TWO_PI))
        q1 = (rng.uniform(-300, 300), rng.uniform(-300, 300), rng.uniform(0, TWO_PI))
        L, word, seg = dubins(q0, q1, R)
        x, y, th = integrate(q0, word, seg, R)
        err = math.hypot(x - q1[0], y - q1[1]) + R * abs(
            math.atan2(math.sin(th - q1[2]), math.cos(th - q1[2])))
        worst = max(worst, err)
        assert L >= math.hypot(q1[0] - q0[0], q1[1] - q0[1]) - 1e-6, "shorter than straight line"
    assert worst < 1e-6, f"Dubins closed form disagrees with integration: {worst:.3e} m"
    return worst


class _Lcg:
    """Deterministic RNG so the verification is reproducible without numpy."""

    def __init__(self, seed):
        self.s = seed

    def next(self):
        self.s = (1103515245 * self.s + 12345) % (1 << 31)
        return self.s / (1 << 31)

    def uniform(self, a, b):
        return a + (b - a) * self.next()


# --------------------------------------------------------------------------
# Lane ordering as an exact ATSP over (lane, direction).
# --------------------------------------------------------------------------

def build_lanes(x0, x1, y0, y1, spacing):
    """Boustrophedon lane geometry: lanes run along x, stacked along y."""
    n = max(1, int(math.ceil((y1 - y0) / spacing)) + 1)
    return [(x0, x1, min(y0 + i * spacing, y1)) for i in range(n)]


def lane_configs(lane):
    """The two ways to fly a lane: (entry_config, exit_config)."""
    xa, xb, y = lane
    return [((xa, y, 0.0), (xb, y, 0.0)),            # west -> east
            ((xb, y, math.pi), (xa, y, math.pi))]    # east -> west


def solve_exact(lanes, R, start):
    """Held-Karp over lanes x directions. Returns (total_m, order)."""
    n = len(lanes)
    cfg = [lane_configs(l) for l in lanes]
    lane_len = [abs(l[1] - l[0]) for l in lanes]
    # transition[i][di][j][dj] = Dubins cost from exit of (i,di) to entry of (j,dj)
    trans = [[[[0.0] * 2 for _ in range(n)] for _ in range(2)] for _ in range(n)]
    for i in range(n):
        for di in range(2):
            for j in range(n):
                if i == j:
                    continue
                for dj in range(2):
                    trans[i][di][j][dj] = dubins(cfg[i][di][1], cfg[j][dj][0], R)[0]
    INF = float("inf")
    # dp[mask][i][di] = best cost having flown `mask`, currently at exit of (i,di)
    dp = [[[INF] * 2 for _ in range(n)] for _ in range(1 << n)]
    par = {}
    for i in range(n):
        for di in range(2):
            dp[1 << i][i][di] = dubins(start, cfg[i][di][0], R)[0] + lane_len[i]
    for mask in range(1 << n):
        for i in range(n):
            if not mask & (1 << i):
                continue
            for di in range(2):
                cur = dp[mask][i][di]
                if cur == INF:
                    continue
                for j in range(n):
                    if mask & (1 << j):
                        continue
                    nm = mask | (1 << j)
                    for dj in range(2):
                        cand = cur + trans[i][di][j][dj] + lane_len[j]
                        if cand < dp[nm][j][dj] - 1e-9:
                            dp[nm][j][dj] = cand
                            par[(nm, j, dj)] = (mask, i, di)
    full = (1 << n) - 1
    best, end = INF, None
    for i in range(n):
        for di in range(2):
            if dp[full][i][di] < best:
                best, end = dp[full][i][di], (i, di)
    order, st = [], (full, end[0], end[1])
    while st in par or st[0] != (1 << st[1]):
        order.append((st[1], st[2]))
        if st not in par:
            break
        m, i, di = par[st]
        st = (m, i, di)
    order.append((st[1], st[2]))
    order.reverse()
    return best, order


def fly(waypoints, R, step=2.0):
    """Fly a list of configurations in order, Dubins between consecutive ones.

    Both plans go through THIS function, so their lengths and their in-field
    fractions are produced by the same construction. They previously had one
    sampler each, which made the in-field percentages incomparable -- the same
    class of measurement error that has already mislabelled results twice in
    this project (FLOW-vi.md 19.7).
    """
    total, pts = 0.0, []
    for q0, q1 in zip(waypoints, waypoints[1:]):
        L, word, seg = dubins(q0, q1, R)
        total += L
        k = max(1, int(L / step))
        for s in range(k + 1):
            pts.append(_advance(q0, word, seg, R, s / k))
    return total, pts


def sequential_waypoints(lanes, R, start, turn_out):
    """The configuration sequence BuildMission() actually produces."""
    cfg = [lane_configs(l) for l in lanes]
    wps = [start]
    for idx, lane in enumerate(lanes):
        di = idx % 2
        entry, exit_ = cfg[idx][di]
        wps += [entry, exit_]
        if idx + 1 < len(lanes):
            y_next = lanes[idx + 1][2]
            direction = 1.0 if di == 0 else -1.0
            out_x = exit_[0] + direction * turn_out
            head = exit_[2]                       # still along the lane
            cross = math.pi / 2 if y_next > lane[2] else -math.pi / 2
            wps += [(out_x, lane[2], head), (out_x, y_next, cross)]
    return wps


def optimal_waypoints(order, lanes, start):
    cfg = [lane_configs(l) for l in lanes]
    wps = [start]
    for (i, di) in order:
        entry, exit_ = cfg[i][di]
        wps += [entry, exit_]
    return wps


def path_points(order, lanes, R, start, step=2.0):
    """Sample the flown path so the in-field fraction can be measured."""
    cfg = [lane_configs(l) for l in lanes]
    pts, q = [], start
    for (i, di) in order:
        entry, exit_ = cfg[i][di]
        L, word, seg = dubins(q, entry, R)
        k = max(1, int(L / step))
        for s in range(k + 1):
            f = s / k
            pts.append(_advance(q, word, seg, R, f))
        pts.append((entry[0], entry[1]))
        n = max(1, int(abs(exit_[0] - entry[0]) / step))
        for s in range(n + 1):
            f = s / n
            pts.append((entry[0] + f * (exit_[0] - entry[0]), entry[1]))
        q = exit_
    return pts


def _advance(q0, word, seg, R, frac):
    total = sum(seg)
    want = total * frac
    x, y, th = q0
    for kind, s in zip(word, seg):
        take = min(s, want)
        L = take * R
        if kind == "S":
            x += L * math.cos(th)
            y += L * math.sin(th)
        else:
            turn = 1.0 if kind == "L" else -1.0
            cx = x - turn * R * math.sin(th)
            cy = y + turn * R * math.cos(th)
            th2 = th + turn * take
            x = cx + turn * R * math.sin(th2)
            y = cy - turn * R * math.cos(th2)
            th = mod2pi(th2)
        want -= take
        if want <= 1e-12:
            break
    return (x, y)


def in_field_fraction(pts, x0, x1, y0, y1):
    inside = sum(1 for x, y in pts if x0 <= x <= x1 and y0 <= y <= y1)
    return 100.0 * inside / len(pts)


def sequential_plan(lanes, R, start, turn_out):
    """What the shipping BuildMission() flies: lanes in order, turn outside."""
    cfg = [lane_configs(l) for l in lanes]
    total, q, pts = 0.0, start, []
    for idx, lane in enumerate(lanes):
        di = idx % 2
        entry, exit_ = cfg[idx][di]
        L, word, seg = dubins(q, entry, R)
        total += L
        k = max(1, int(L / 2.0))
        for s in range(k + 1):
            pts.append(_advance(q, word, seg, R, s / k))
        total += abs(exit_[0] - entry[0])
        n = max(1, int(abs(exit_[0] - entry[0]) / 2.0))
        for s in range(n + 1):
            f = s / n
            pts.append((entry[0] + f * (exit_[0] - entry[0]), entry[1]))
        q = exit_
        if idx + 1 < len(lanes):
            # two explicit waypoints beyond the lane end, as in BuildMission()
            direction = 1.0 if di == 0 else -1.0
            out_x = exit_[0] + direction * turn_out
            q = (out_x, lanes[idx + 1][2], math.pi if di == 0 else 0.0)
            total += turn_out + abs(lanes[idx + 1][2] - lane[2]) + turn_out
            for s in range(40):
                pts.append((exit_[0] + direction * turn_out * s / 39.0, lane[2]))
    return total, pts


# --------------------------------------------------------------------------
# The speed / exposure bound.
# --------------------------------------------------------------------------

def exposure_report(Rc, chunk_rate, n_chunks, speeds):
    need = n_chunks / chunk_rate
    print(f"  cue set = {n_chunks} chunk @ {chunk_rate:.1f} chunk/s -> {need:.1f} s exposure needed")
    print(f"  {'v (m/s)':>9} {'max chord':>10} {'max dwell':>10} {'chunks':>8} {'fraction':>9}")
    for v in speeds:
        dwell = 2.0 * Rc / v
        got = dwell * chunk_rate
        print(f"  {v:9.1f} {2*Rc:9.0f}m {dwell:9.2f}s {got:8.1f} {min(1.0, got/n_chunks)*100:8.1f}%")
    print(f"  => full cue set on ONE centred pass needs v <= {2*Rc/need:.1f} m/s")


def main():
    R_VERIFY = verify_dubins()
    print(f"Dubins closed form verified against integration: worst error {R_VERIFY:.2e} m\n")

    # Operational geometry: gridSize 24 @ 20 m spacing, kUavBroadcastRadiusM 50.
    x0, x1, y0, y1 = 0.0, 460.0, 0.0, 460.0
    v = 25.0
    R = v * v / (9.81 * math.tan(math.radians(45.0)))
    spacing = 50.0
    lanes = build_lanes(x0, x1, y0, y1, spacing)
    start = (-200.0, -200.0, math.radians(45))   # BS corner, heading into the field

    print(f"field {x1-x0:.0f} x {y1-y0:.0f} m | v={v} m/s | R={R:.1f} m | "
          f"lane spacing={spacing:.0f} m | 2R/spacing={2*R/spacing:.2f}")
    print(f"lanes: {len(lanes)}\n")

    seq_len, seq_pts = fly(sequential_waypoints(lanes, R, start, 1.2 * R), R)
    seq_in = in_field_fraction(seq_pts, x0, x1, y0, y1)
    print(f"shipping plan (sequential + outside turn-arounds):")
    print(f"  length {seq_len/1000:6.2f} km   in-field {seq_in:5.1f} %")

    opt_cost, order = solve_exact(lanes, R, start)
    opt_len, opt_pts = fly(optimal_waypoints(order, lanes, start), R)
    opt_in = in_field_fraction(opt_pts, x0, x1, y0, y1)
    print(f"exact Dubins lane ordering (Held-Karp, {len(lanes)} lanes x 2 dir):")
    print(f"  length {opt_len/1000:6.2f} km   in-field {opt_in:5.1f} %")
    print(f"  order  {[(i, 'WE' if d == 0 else 'EW') for i, d in order]}")
    print(f"  saving {100*(seq_len-opt_len)/seq_len:5.1f} % of distance\n")

    print("speed vs cue exposure (single centred pass, Rc = 50 m):")
    exposure_report(50.0, 5.0, 30, [15.0, 16.7, 20.0, 25.0, 30.0])

    print("\nthe coupling: speed sets BOTH the turn radius and the exposure")
    speed_sweep(x0, x1, y0, y1, spacing, Rc=50.0, chunk_rate=5.0, n_chunks=30)


def speed_sweep(x0, x1, y0, y1, spacing, Rc, chunk_rate, n_chunks):
    """R grows as v^2 while exposure falls as 1/v -- so both costs move together.

    Screening is not finished when the area has been overflown; it is finished
    when the WORST-PLACED node holds enough of the cue set to discriminate. A
    node sitting directly under a lane is that worst case: its chord is the full
    2*Rc and it gets nothing from the neighbouring lanes. So the mission time is
    the number of sweeps that node needs, times the time one sweep takes.
    """
    lanes = build_lanes(x0, x1, y0, y1, spacing)
    lane_m = sum(abs(l[1] - l[0]) for l in lanes)
    print(f"  {'v':>5} {'R(v)':>7} {'2R/s':>6} {'plan':>8} {'overhd':>8} "
          f"{'chunk/pass':>11} {'sweeps':>7} {'T_screen':>9}")
    best = None
    for v in (12.0, 14.0, 16.0, 16.7, 18.0, 20.0, 22.0, 25.0, 28.0, 32.0):
        R = v * v / (9.81 * math.tan(math.radians(45.0)))
        start = (x0 - 200.0, y0 - 200.0, math.radians(45))
        length, _ = fly(sequential_waypoints(lanes, R, start, 1.2 * R), R)
        per_pass = (2.0 * Rc / v) * chunk_rate
        sweeps = math.ceil(n_chunks / per_pass)
        t_screen = sweeps * length / v
        flag = ""
        if best is None or t_screen < best[0]:
            best = (t_screen, v)
        print(f"  {v:5.1f} {R:6.1f}m {2*R/spacing:6.2f} {length/1000:7.2f}km "
              f"{(length-lane_m)/1000:7.2f}km {per_pass:11.1f} {sweeps:7d} {t_screen:8.0f}s{flag}")
    print(f"  => fastest screening at v = {best[1]:.1f} m/s ({best[0]:.0f} s), "
          f"NOT at the top speed")

    # The optimum above assumes a node needs the WHOLE cue set (C* = 1.0). It
    # does not: discrimination needs some fraction C*, and where the sweep-count
    # cliff sits depends on it. If the finding only survives at C* = 1.0 it is an
    # artifact of that assumption, so it is swept here rather than asserted.
    print("\n  sensitivity: optimal speed vs the discrimination threshold C*")
    print(f"  {'C*':>5} {'v*':>7} {'T_screen':>9} {'T at v=25':>11} {'gain':>7}")
    for cstar in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        need = n_chunks * cstar
        rows = []
        for v in [10.0 + 0.5 * k for k in range(50)]:
            R = v * v / (9.81 * math.tan(math.radians(45.0)))
            start = (x0 - 200.0, y0 - 200.0, math.radians(45))
            length, _ = fly(sequential_waypoints(lanes, R, start, 1.2 * R), R)
            sweeps = math.ceil(need / ((2.0 * Rc / v) * chunk_rate))
            rows.append((sweeps * length / v, v))
        t_best, v_best = min(rows)
        t_25 = min(t for t, v in rows if abs(v - 25.0) < 1e-9)
        print(f"  {cstar:5.2f} {v_best:6.1f}m/s {t_best:8.0f}s {t_25:10.0f}s "
              f"{100*(t_25-t_best)/t_25:6.1f}%")


if __name__ == "__main__":
    main()
