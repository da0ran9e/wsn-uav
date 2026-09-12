"""Dubins paths: verified against analytic cases and by forward integration."""
import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from screening import dubins as D  # noqa: E402

RHO = 70.6


def test_straight_line_when_headings_aligned_along_the_segment():
    """Heading already pointing at the goal, goal heading the same -> the
    shortest Dubins path IS the straight line."""
    p = D.dubins_path((0, 0, 0), (500, 0, 0), RHO)
    assert p is not None
    assert p.length == pytest.approx(500.0, rel=1e-9)


def test_u_turn_costs_at_least_pi_rho():
    """Reversing heading in place cannot cost less than a half-circle."""
    p = D.dubins_path((0, 0, 0), (0, 0, math.pi), RHO)
    assert p is not None
    assert p.length >= math.pi * RHO - 1e-6


def test_full_circle_return_to_same_state():
    p = D.dubins_path((0, 0, 0), (0, 0, 0), RHO)
    assert p is not None
    assert p.length == pytest.approx(0.0, abs=1e-6)


def test_known_rsl_geometry():
    """Offset goal with opposite heading: path exists, verifies, and is longer
    than the Euclidean distance."""
    p = D.dubins_path((0, 0, 0), (300, 200, math.pi), RHO)
    assert p is not None
    assert p.length > math.hypot(300, 200)


@pytest.mark.parametrize("seed", range(60))
def test_random_paths_forward_integrate_to_the_goal(seed):
    """The load-bearing test: sample the returned path and confirm it actually
    ends at the requested state. Catches any transcription error in the closed
    forms rather than trusting them."""
    rng = random.Random(seed)
    q0 = (rng.uniform(-500, 500), rng.uniform(-500, 500), rng.uniform(0, D.TWO_PI))
    q1 = (rng.uniform(-500, 500), rng.uniform(-500, 500), rng.uniform(0, D.TWO_PI))
    p = D.dubins_path(q0, q1, RHO)
    assert p is not None, f"no word verified for seed {seed}"
    s = D.sample_path(p, 0.05)
    assert s, "empty sampling"
    xe, ye, pe, _ = s[-1]
    assert math.hypot(xe - q1[0], ye - q1[1]) < 1e-3
    dp = abs(D.mod2pi(pe - q1[2]))
    assert min(dp, D.TWO_PI - dp) < 1e-6


@pytest.mark.parametrize("seed", range(40))
def test_curvature_never_exceeds_one_over_rho(seed):
    """AGENT-BRIEF E5.2. Measured numerically from the sampled path."""
    rng = random.Random(1000 + seed)
    q0 = (rng.uniform(-400, 400), rng.uniform(-400, 400), rng.uniform(0, D.TWO_PI))
    q1 = (rng.uniform(-400, 400), rng.uniform(-400, 400), rng.uniform(0, D.TWO_PI))
    p = D.dubins_path(q0, q1, RHO)
    assert p is not None
    kmax = D.max_abs_curvature(D.sample_path(p, 0.5), RHO)
    assert kmax <= 1.0 / RHO * (1 + 1e-6), f"kappa*rho = {kmax*RHO}"


@pytest.mark.parametrize("seed", range(40))
def test_length_is_at_least_euclidean_and_at_most_euclidean_plus_2pi_rho(seed):
    rng = random.Random(2000 + seed)
    q0 = (0.0, 0.0, rng.uniform(0, D.TWO_PI))
    q1 = (rng.uniform(-600, 600), rng.uniform(-600, 600), rng.uniform(0, D.TWO_PI))
    p = D.dubins_path(q0, q1, RHO)
    euclid = math.hypot(q1[0], q1[1])
    assert p.length >= euclid - 1e-9
    assert p.length <= euclid + D.TWO_PI * RHO + 1e-6


def test_all_six_words_are_reachable_over_random_instances():
    """If a word never wins, its formula is probably wrong. RLR/LRL only win at
    short range, so sample short hops too."""
    seen = set()
    rng = random.Random(7)
    for _ in range(4000):
        scale = rng.choice([0.5, 1.0, 2.0, 6.0]) * RHO
        q0 = (0.0, 0.0, rng.uniform(0, D.TWO_PI))
        q1 = (rng.uniform(-scale, scale), rng.uniform(-scale, scale),
              rng.uniform(0, D.TWO_PI))
        p = D.dubins_path(q0, q1, RHO)
        if p:
            seen.add(p.word)
    assert seen == set(D.WORDS), f"words never optimal: {set(D.WORDS) - seen}"


def test_shortest_is_really_the_minimum_over_verified_words():
    rng = random.Random(11)
    for _ in range(200):
        q0 = (0.0, 0.0, rng.uniform(0, D.TWO_PI))
        q1 = (rng.uniform(-400, 400), rng.uniform(-400, 400), rng.uniform(0, D.TWO_PI))
        best = D.dubins_path(q0, q1, RHO)
        singles = [D.dubins_path(q0, q1, RHO, words=(w,)) for w in D.WORDS]
        lens = [s.length for s in singles if s is not None]
        assert best.length == pytest.approx(min(lens), rel=1e-12)


def test_rejects_nonpositive_rho():
    with pytest.raises(ValueError):
        D.dubins_path((0, 0, 0), (1, 1, 0), 0.0)


def test_mirror_symmetry_of_word_pairs():
    """Reflecting about the x-axis maps LSL<->RSR, LSR<->RSL, LRL<->RLR and
    preserves length. This is the invariant the LRL implementation is built on,
    so it is tested directly."""
    rng = random.Random(23)
    for _ in range(300):
        x, y = rng.uniform(-500, 500), rng.uniform(-500, 500)
        p0, p1 = rng.uniform(0, D.TWO_PI), rng.uniform(0, D.TWO_PI)
        a = D.dubins_path((0, 0, p0), (x, y, p1), RHO)
        b = D.dubins_path((0, 0, -p0), (x, -y, -p1), RHO)
        assert a is not None and b is not None
        assert a.length == pytest.approx(b.length, rel=1e-9)
        flip = str.maketrans({"L": "R", "R": "L"})
        assert a.word.translate(flip) == b.word


def test_word_win_counts_are_balanced_across_mirror_pairs():
    """A word that never wins means a wrong formula -- that is how the original
    LRL bug surfaced. Mirror pairs must win at comparable rates."""
    from collections import Counter
    rng = random.Random(7)
    c = Counter()
    for _ in range(4000):
        sc = rng.choice([0.5, 1.0, 2.0, 6.0]) * RHO
        p = D.dubins_path((0, 0, rng.uniform(0, D.TWO_PI)),
                          (rng.uniform(-sc, sc), rng.uniform(-sc, sc),
                           rng.uniform(0, D.TWO_PI)), RHO)
        if p:
            c[p.word] += 1
    assert set(c) == set(D.WORDS)
    for u, w in (("LSL", "RSR"), ("LSR", "RSL"), ("LRL", "RLR")):
        assert 0.7 < c[u] / c[w] < 1.43, f"{u}:{c[u]} vs {w}:{c[w]} unbalanced"
