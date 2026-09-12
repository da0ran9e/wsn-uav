"""Dubins shortest paths for a fixed-wing vehicle (AGENT-BRIEF 2.4).

State is (x, y, psi): position AND heading. Constant speed, no reverse, minimum
turning radius rho. The shortest path between two states is one of six words:
LSL, RSR, LSR, RSL, RLR, LRL.

Correctness is NOT taken on trust from the closed forms. Every candidate word is
verified by forward-integrating the control sequence from the start state and
checking that it lands on the goal state; a word that does not is discarded. So a
transcription error in any single formula degrades to "that word is unavailable"
rather than silently returning a wrong length.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

TWO_PI = 2.0 * math.pi
_POSE_TOL = 1e-6          # normalised units (multiples of rho)
_HEADING_TOL = 1e-6       # radians

WORDS = ("LSL", "RSR", "LSR", "RSL", "RLR", "LRL")


def mod2pi(x: float) -> float:
    return x - TWO_PI * math.floor(x / TWO_PI)


@dataclass(frozen=True)
class DubinsPath:
    word: str
    t: float          # first segment, normalised (radians if turn, length/rho if straight)
    p: float          # middle segment
    q: float          # final segment
    rho: float
    x0: float
    y0: float
    psi0: float

    @property
    def length(self) -> float:
        return (self.t + self.p + self.q) * self.rho

    def segment_types(self) -> tuple[str, str, str]:
        return (self.word[0], self.word[1], self.word[2])


# --- the six words, in normalised coordinates (d = D/rho) -----------------

def _lsl(a: float, b: float, d: float):
    tmp0 = d + math.sin(a) - math.sin(b)
    p_sq = 2 + d * d - 2 * math.cos(a - b) + 2 * d * (math.sin(a) - math.sin(b))
    if p_sq < 0:
        return None
    tmp1 = math.atan2(math.cos(b) - math.cos(a), tmp0)
    return mod2pi(-a + tmp1), math.sqrt(p_sq), mod2pi(b - tmp1)


def _rsr(a: float, b: float, d: float):
    tmp0 = d - math.sin(a) + math.sin(b)
    p_sq = 2 + d * d - 2 * math.cos(a - b) + 2 * d * (math.sin(b) - math.sin(a))
    if p_sq < 0:
        return None
    tmp1 = math.atan2(math.cos(a) - math.cos(b), tmp0)
    return mod2pi(a - tmp1), math.sqrt(p_sq), mod2pi(-b + tmp1)


def _lsr(a: float, b: float, d: float):
    p_sq = -2 + d * d + 2 * math.cos(a - b) + 2 * d * (math.sin(a) + math.sin(b))
    if p_sq < 0:
        return None
    p = math.sqrt(p_sq)
    tmp2 = math.atan2(-math.cos(a) - math.cos(b),
                      d + math.sin(a) + math.sin(b)) - math.atan2(-2.0, p)
    return mod2pi(-a + tmp2), p, mod2pi(-mod2pi(b) + tmp2)


def _rsl(a: float, b: float, d: float):
    p_sq = d * d - 2 + 2 * math.cos(a - b) - 2 * d * (math.sin(a) + math.sin(b))
    if p_sq < 0:
        return None
    p = math.sqrt(p_sq)
    tmp2 = math.atan2(math.cos(a) + math.cos(b),
                      d - math.sin(a) - math.sin(b)) - math.atan2(2.0, p)
    return mod2pi(a - tmp2), p, mod2pi(b - tmp2)


def _rlr(a: float, b: float, d: float):
    tmp = (6.0 - d * d + 2 * math.cos(a - b) + 2 * d * (math.sin(a) - math.sin(b))) / 8.0
    if abs(tmp) > 1.0:
        return None
    p = mod2pi(TWO_PI - math.acos(tmp))
    t = mod2pi(a - math.atan2(math.cos(a) - math.cos(b),
                              d - math.sin(a) + math.sin(b)) + p / 2.0)
    return t, p, mod2pi(a - b - t + p)


def _lrl(a: float, b: float, d: float):
    """LRL by mirror symmetry, not by a second transcription.

    Reflecting the canonical frame about the x-axis maps (0,0,a) -> (0,0,-a),
    (d,0,b) -> (d,0,-b), and exchanges left turns with right turns while leaving
    every arc length unchanged. Hence LRL(a,b,d) has exactly the same (t,p,q) as
    RLR(-a,-b,d). Deriving it this way means only one three-arc formula can be
    wrong, and that one is covered by the forward-integration check.
    """
    return _rlr(mod2pi(-a), mod2pi(-b), d)


_SOLVERS = {"LSL": _lsl, "RSR": _rsr, "LSR": _lsr, "RSL": _rsl,
            "RLR": _rlr, "LRL": _lrl}


def _step(x: float, y: float, psi: float, mode: str, s: float):
    """Advance a unit-radius state by arc length s under control mode."""
    if mode == "S":
        return x + s * math.cos(psi), y + s * math.sin(psi), psi
    sign = 1.0 if mode == "L" else -1.0
    npsi = psi + sign * s
    return (x + sign * (math.sin(npsi) - math.sin(psi)),
            y - sign * (math.cos(npsi) - math.cos(psi)),
            npsi)


def _word_reaches_goal(word: str, t: float, p: float, q: float,
                       a: float, b: float, d: float) -> bool:
    """Forward-integrate in normalised coordinates and compare to the goal.

    Start (0,0,a), goal (d,0,b) -- the canonical Dubins frame.
    """
    if min(t, p, q) < -1e-9:
        return False
    x, y, psi = 0.0, 0.0, a
    for mode, s in zip(word, (t, p, q)):
        x, y, psi = _step(x, y, psi, mode, s)
    dpsi = mod2pi(psi - b)
    dpsi = min(dpsi, TWO_PI - dpsi)
    return (abs(x - d) < _POSE_TOL and abs(y) < _POSE_TOL and dpsi < _HEADING_TOL)


def dubins_path(q0: tuple[float, float, float], q1: tuple[float, float, float],
                rho: float, *, words: tuple[str, ...] = WORDS) -> DubinsPath | None:
    """Shortest Dubins path from q0 to q1. None if no word verifies (should not
    happen for rho > 0, but it is never silently papered over)."""
    if rho <= 0:
        raise ValueError(f"rho must be positive, got {rho}")
    x0, y0, psi0 = q0
    x1, y1, psi1 = q1
    dx, dy = x1 - x0, y1 - y0
    D = math.hypot(dx, dy)
    d = D / rho
    theta = mod2pi(math.atan2(dy, dx)) if D > 0 else 0.0
    a = mod2pi(psi0 - theta)
    b = mod2pi(psi1 - theta)

    best = None
    for w in words:
        sol = _SOLVERS[w](a, b, d)
        if sol is None:
            continue
        t, p, q = sol
        if not _word_reaches_goal(w, t, p, q, a, b, d):
            continue
        if best is None or (t + p + q) < (best.t + best.p + best.q):
            best = DubinsPath(w, t, p, q, rho, x0, y0, psi0)
    return best


def sample_path(path: DubinsPath, ds: float) -> list[tuple[float, float, float, str]]:
    """Sample (x, y, psi, segment_type) along the path at arc-length step ds."""
    out: list[tuple[float, float, float, str]] = []
    # work in normalised units then scale back
    x, y, psi = 0.0, 0.0, path.psi0
    dsn = ds / path.rho
    for mode, seg in zip(path.word, (path.t, path.p, path.q)):
        n = max(1, int(math.ceil(seg / dsn))) if seg > 0 else 0
        for i in range(n):
            s = min(dsn, seg - i * dsn)
            if s <= 0:
                break
            x, y, psi = _step(x, y, psi, mode, s)
            out.append((path.x0 + x * path.rho, path.y0 + y * path.rho, psi, mode))
    return out


def max_abs_curvature(samples: list[tuple[float, float, float, str]],
                      rho: float) -> float:
    """Numeric |kappa| = |dpsi/ds| from the SAMPLED path, not from the segment
    labels. This is the check AGENT-BRIEF E5.2 asks for: a tour that violates
    |kappa| <= 1/rho is not a result.
    """
    worst = 0.0
    for (x0, y0, p0, _), (x1, y1, p1, _) in zip(samples, samples[1:]):
        ds = math.hypot(x1 - x0, y1 - y0)
        if ds < 1e-12:
            continue
        dp = abs(mod2pi(p1 - p0))
        dp = min(dp, TWO_PI - dp)
        # chord vs arc: for an arc of curvature 1/rho the chord underestimates
        # arc length, so dpsi/chord slightly OVERestimates curvature. Correct it.
        if dp > 1e-12:
            arc = ds * (dp / 2.0) / math.sin(dp / 2.0)
        else:
            arc = ds
        worst = max(worst, dp / arc)
    return worst
