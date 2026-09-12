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


# --------------------------------------------------------------------------
# Vectorised all-pairs length matrix.
#
# The scalar dubins_path() above verifies every candidate word by forward
# integration, which is what caught the LRL transcription bug. That check cannot
# be vectorised cheaply, so this fast path CROSS-CHECKS itself against the scalar
# implementation on random pairs every time it is called, and raises on any
# disagreement. The scalar path remains the reference.
#
# Why it exists: a 120-cluster instance with 8 headings needs a 960x960 matrix,
# i.e. ~922,000 scalar calls, which dominated the entire tour computation.
# --------------------------------------------------------------------------

def length_matrix(nodes: list[tuple[float, float, float]], rho: float, *,
                  check_samples: int = 400, rtol: float = 1e-7,
                  rng_seed: int = 0):
    """All-pairs Dubins path lengths as a numpy array of shape (n, n).

    Diagonal is 0. Raises AssertionError if the vectorised result disagrees with
    the scalar reference on the sampled pairs.
    """
    import numpy as np

    n = len(nodes)
    arr = np.asarray(nodes, dtype=float)
    x, y, psi = arr[:, 0], arr[:, 1], arr[:, 2]
    dx = x[None, :] - x[:, None]
    dy = y[None, :] - y[:, None]
    D = np.hypot(dx, dy)
    theta = np.where(D > 0, np.mod(np.arctan2(dy, dx), TWO_PI), 0.0)
    d = D / rho
    a = np.mod(psi[:, None] - theta, TWO_PI)
    b = np.mod(psi[None, :] - theta, TWO_PI)

    sa, ca, sb, cb = np.sin(a), np.cos(a), np.sin(b), np.cos(b)
    cab = np.cos(a - b)
    d2 = d * d
    best = np.full((n, n), np.inf)

    def upd(t, p, q, ok):
        np.minimum(best, np.where(ok, t + p + q, np.inf), out=best)

    with np.errstate(invalid="ignore", divide="ignore"):
        # LSL
        psq = 2 + d2 - 2 * cab + 2 * d * (sa - sb)
        ok = psq >= 0
        tmp1 = np.arctan2(cb - ca, d + sa - sb)
        upd(np.mod(-a + tmp1, TWO_PI), np.sqrt(np.where(ok, psq, 0.0)),
            np.mod(b - tmp1, TWO_PI), ok)
        # RSR
        psq = 2 + d2 - 2 * cab + 2 * d * (sb - sa)
        ok = psq >= 0
        tmp1 = np.arctan2(ca - cb, d - sa + sb)
        upd(np.mod(a - tmp1, TWO_PI), np.sqrt(np.where(ok, psq, 0.0)),
            np.mod(-b + tmp1, TWO_PI), ok)
        # LSR
        psq = -2 + d2 + 2 * cab + 2 * d * (sa + sb)
        ok = psq >= 0
        p = np.sqrt(np.where(ok, psq, 0.0))
        tmp2 = np.arctan2(-ca - cb, d + sa + sb) - np.arctan2(-2.0, p)
        upd(np.mod(-a + tmp2, TWO_PI), p,
            np.mod(-np.mod(b, TWO_PI) + tmp2, TWO_PI), ok)
        # RSL
        psq = d2 - 2 + 2 * cab - 2 * d * (sa + sb)
        ok = psq >= 0
        p = np.sqrt(np.where(ok, psq, 0.0))
        tmp2 = np.arctan2(ca + cb, d - sa - sb) - np.arctan2(2.0, p)
        upd(np.mod(a - tmp2, TWO_PI), p, np.mod(b - tmp2, TWO_PI), ok)
        # RLR, then LRL by the same mirror symmetry the scalar path uses
        for mirror in (False, True):
            aa = np.mod(-a, TWO_PI) if mirror else a
            bb = np.mod(-b, TWO_PI) if mirror else b
            saa, caa, sbb, cbb = np.sin(aa), np.cos(aa), np.sin(bb), np.cos(bb)
            tmp = (6.0 - d2 + 2 * np.cos(aa - bb) + 2 * d * (saa - sbb)) / 8.0
            ok = np.abs(tmp) <= 1.0
            p = np.mod(TWO_PI - np.arccos(np.clip(tmp, -1.0, 1.0)), TWO_PI)
            t = np.mod(aa - np.arctan2(caa - cbb, d - saa + sbb)
                       + np.mod(p / 2.0, TWO_PI), TWO_PI)
            q = np.mod(aa - bb - t + np.mod(p, TWO_PI), TWO_PI)
            upd(t, p, q, ok)

    out = best * rho
    np.fill_diagonal(out, 0.0)

    import random
    rnd = random.Random(rng_seed)
    checked = 0
    for _ in range(min(check_samples, max(0, n * (n - 1)))):
        i, j = rnd.randrange(n), rnd.randrange(n)
        if i == j:
            continue
        ref = dubins_path(nodes[i], nodes[j], rho)
        if ref is None:
            continue
        got = float(out[i, j])
        if not abs(got - ref.length) <= rtol * max(1.0, ref.length):
            raise AssertionError(
                f"vectorised Dubins length disagrees with the scalar reference at "
                f"({i},{j}): {got} vs {ref.length}")
        checked += 1
    if check_samples > 0 and n > 1 and checked == 0:
        # Only a failure when checks were ASKED for; check_samples=0 is a
        # deliberate opt-out used by tests that verify every pair exhaustively.
        raise AssertionError("vectorised Dubins matrix was never cross-checked")
    return out
