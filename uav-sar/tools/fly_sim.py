"""Fly a waypoint list through the SAME guidance law the simulation uses.

Why this exists rather than a geometric path model: two earlier attempts to
score the shipping sweep against a Dubins-ordered one were wrong in opposite
directions, and both looked plausible.

  - Approximating each turn-around as straight run-out + cross + run-back
    UNDERCOUNTED the shipping plan (it ignored the curvature of the reversal).
  - Modelling it as Dubins through the turn waypoints with imposed headings
    OVERCOUNTED it: the aircraft is never required to arrive at a waypoint on a
    particular heading, so pinning one invents work it does not do.

The only defensible comparison flies both waypoint lists through the guidance
law in SarFastUavApp::ControlTick + FlightController::Step, which is what this
does, tick for tick:

  * heading is commanded continuously toward the current waypoint,
  * the turn rate is limited to g*tan(phi)/v,
  * a waypoint is accepted within arriveR OR once abeam of it.

So the two plans differ ONLY in the waypoint list, which is the thing under
test. Ordering is scored by what the aircraft would actually fly.
"""
import math

CONTROL_TICK_S = 0.1     # params::kControlTickS
G = 9.81                 # params::kGravityMps2
BANK_DEG = 45.0          # params::kBankAngleDeg


def turn_radius(v, bank_deg=BANK_DEG):
    return v * v / (G * math.tan(math.radians(bank_deg)))


def max_turn_rate_deg(v, bank_deg=BANK_DEG):
    """FlightController::SetMaxTurnRateDegPerS as the FAST app sets it."""
    return G * math.tan(math.radians(bank_deg)) / max(1.0, v) * 180.0 / math.pi


def fly(waypoints, start_xy, v, start_heading_deg=None, max_ticks=400000):
    """Return (path_points, length_m, time_s, reached_count).

    waypoints: [(x, y), ...]  -- positions only. Heading is never imposed,
    exactly as in the app: the aircraft aims at the next waypoint and turns
    toward it as fast as the bank angle allows.
    """
    x, y = start_xy
    if start_heading_deg is None:
        tx, ty = waypoints[0]
        start_heading_deg = math.degrees(math.atan2(ty - y, tx - x))
    heading = start_heading_deg
    rate = max_turn_rate_deg(v)
    R = turn_radius(v)
    arrive_r = max(1.0, v * CONTROL_TICK_S * 1.5)

    pts = [(x, y)]
    ti, prev_d, length, t = 0, 0.0, 0.0, 0.0
    ticks = 0
    while ti < len(waypoints) and ticks < max_ticks:
        ticks += 1
        tx, ty = waypoints[ti]
        # --- FlightController::Step: rate-limited turn toward the command -----
        cmd = math.degrees(math.atan2(ty - y, tx - x))
        d_head = cmd - heading
        while d_head > 180.0:
            d_head -= 360.0
        while d_head < -180.0:
            d_head += 360.0
        lim = rate * CONTROL_TICK_S
        heading += max(-lim, min(lim, d_head))
        # --- integrate one tick ----------------------------------------------
        rad = math.radians(heading)
        nx, ny = x + v * CONTROL_TICK_S * math.cos(rad), y + v * CONTROL_TICK_S * math.sin(rad)
        length += math.hypot(nx - x, ny - y)
        t += CONTROL_TICK_S
        x, y = nx, ny
        pts.append((x, y))
        # --- waypoint acceptance ---------------------------------------------
        d_now = math.hypot(tx - x, ty - y)
        passed_abeam = prev_d > 0 and d_now > prev_d and d_now < 2.0 * R
        prev_d = d_now
        if d_now <= arrive_r or passed_abeam:
            prev_d = 0.0
            ti += 1
    return pts, length, t, ti


def in_field_fraction(pts, x0, x1, y0, y1):
    inside = sum(1 for px, py in pts if x0 <= px <= x1 and y0 <= py <= y1)
    return 100.0 * inside / len(pts)


def covered_fraction(pts, sensors, radius):
    """Share of sensor nodes that ever came within `radius` of the path.

    This is the metric that actually matters for Phase 1 -- a shorter path that
    misses nodes has not screened them -- so a plan is never scored on distance
    alone.
    """
    r2 = radius * radius
    seen = 0
    for sx, sy in sensors:
        for px, py in pts:
            if (px - sx) ** 2 + (py - sy) ** 2 <= r2:
                seen += 1
                break
    return 100.0 * seen / len(sensors)
