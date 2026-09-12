"""The GTSP -> Noon-Bean -> ATSP -> LKH pipeline, checked against brute force.

The Noon-Bean transformation is easy to get subtly wrong in a way that still
returns a plausible number: an earlier revision set the inter-cluster penalty
M = 0, reasoning that forbidding non-successor intra-cluster arcs was enough to
force one visit per cluster. It is not -- re-entering a cluster at a fresh node
uses an ordinary inter-cluster arc -- and the tour quietly split a cluster into
two blocks. These tests brute-force small instances so that class of error cannot
come back silently.
"""
import itertools
import math
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from screening import dubins as DB  # noqa: E402
from screening import tour as T  # noqa: E402

RHO = 70.6
pytestmark = pytest.mark.skipif(T.find_lkh() is None, reason="LKH not installed")


def brute_force_gtsp(chs, n_headings, rho):
    """Exact closed Dubins tour over (cluster x heading), by exhaustion."""
    C = len(chs)
    psis = [2 * math.pi * i / n_headings for i in range(n_headings)]
    best = float("inf")
    for order in itertools.permutations(range(1, C)):
        seq = (0,) + order
        for heads in itertools.product(range(n_headings), repeat=C):
            total = 0.0
            for a, b in zip(range(C), list(range(1, C)) + [0]):
                ca, cb = seq[a], seq[b]
                q0 = (chs[ca][0], chs[ca][1], psis[heads[a]])
                q1 = (chs[cb][0], chs[cb][1], psis[heads[b]])
                p = DB.dubins_path(q0, q1, rho)
                total += p.length
                if total >= best:
                    break
            best = min(best, total)
    return best


@pytest.mark.parametrize("seed", range(4))
def test_lkh_matches_brute_force_three_clusters(seed):
    rng = random.Random(seed)
    chs = [(rng.uniform(0, 600), rng.uniform(0, 600)) for _ in range(3)]
    got = T.dubins_tour(chs, rho=RHO, n_headings=4, seed=1)
    want = brute_force_gtsp(chs, 4, RHO)
    assert got.length_m == pytest.approx(want, rel=2e-3), \
        f"LKH {got.length_m:.2f} vs optimum {want:.2f}"


@pytest.mark.parametrize("seed", range(3))
def test_lkh_matches_brute_force_four_clusters(seed):
    rng = random.Random(100 + seed)
    chs = [(rng.uniform(0, 700), rng.uniform(0, 700)) for _ in range(4)]
    got = T.dubins_tour(chs, rho=RHO, n_headings=4, seed=1)
    want = brute_force_gtsp(chs, 4, RHO)
    assert got.length_m == pytest.approx(want, rel=2e-3), \
        f"LKH {got.length_m:.2f} vs optimum {want:.2f}"


def test_every_cluster_visited_exactly_once_at_scale():
    """The M = 0 bug manifested as more recovered representatives than clusters.
    dubins_tour raises in that case; this asserts it does not happen at a size
    where it actually did."""
    rng = random.Random(7)
    chs = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(40)]
    res = T.dubins_tour(chs, rho=RHO, n_headings=8, seed=1)
    assert res.n_clusters == 40
    assert sum(res.words.values()) == 40      # one Dubins leg per cluster


def test_noon_bean_matrix_structure():
    """Zero-cost successor cycle inside each cluster, forbidden elsewhere
    intra-cluster, and the penalty M strictly positive."""
    chs = [(0.0, 0.0), (400.0, 0.0), (200.0, 350.0)]
    nh = 4
    cost, nodes, M = T.build_cost_matrix(chs, nh, RHO)
    assert M > 0, "Noon-Bean penalty must be positive or clusters can be re-entered"
    n = len(nodes)
    assert n == len(chs) * nh
    cl = [i // nh for i in range(n)]
    for ci in range(len(chs)):
        idx = [i for i in range(n) if cl[i] == ci]
        for a, b in zip(idx, idx[1:] + idx[:1]):
            assert cost[a][b] == 0, "successor arc must be free"
        for a in idx:
            for b in idx:
                succ = idx[(idx.index(a) + 1) % len(idx)]
                if b not in (a, succ):
                    assert cost[a][b] >= T._BIG, "non-successor intra arc must be barred"
    # every inter-cluster arc carries the penalty
    for i in range(n):
        for j in range(n):
            if cl[i] != cl[j]:
                assert cost[i][j] >= M


def test_forbidden_arc_cost_exceeds_any_whole_tour():
    """_BIG must beat the cost of a complete tour, or LKH will buy one forbidden
    arc to save elsewhere."""
    rng = random.Random(3)
    chs = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(30)]
    cost, nodes, M = T.build_cost_matrix(chs, 8, RHO)
    worst_real = max(c for row in cost for c in row if c < T._BIG)
    assert T._BIG > len(nodes) * worst_real / 1.0 or T._BIG > 30 * worst_real
    res = T.dubins_tour(chs, rho=RHO, n_headings=8, seed=1)
    assert res.length_m < 1e6


def test_curvature_holds_on_a_full_tour():
    rng = random.Random(11)
    chs = [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(25)]
    res = T.dubins_tour(chs, rho=RHO, n_headings=8, ds_m=1.0, seed=1)
    assert res.max_kappa_rho <= 1.0 + 1e-6


def test_more_headings_never_hurts_much_and_usually_helps():
    """Monotone in expectation: finer heading sampling can only improve the
    attainable optimum, so a coarse sampling must not beat a fine one by much."""
    rng = random.Random(5)
    chs = [(rng.uniform(0, 800), rng.uniform(0, 800)) for _ in range(12)]
    coarse = T.dubins_tour(chs, rho=RHO, n_headings=2, seed=1).length_m
    fine = T.dubins_tour(chs, rho=RHO, n_headings=12, seed=1).length_m
    assert fine <= coarse * 1.02


def test_trivial_cases():
    assert T.dubins_tour([], rho=RHO, n_headings=8).length_m == 0.0
    assert T.dubins_tour([(1.0, 2.0)], rho=RHO, n_headings=8).length_m == 0.0


def test_bhh_estimate():
    assert T.bhh_tour_length_m(0, 1e6, 0.7124) == 0.0
    assert T.bhh_tour_length_m(1, 1e6, 0.7124) == 0.0
    assert T.bhh_tour_length_m(100, 1e6, 0.7124) == pytest.approx(
        0.7124 * math.sqrt(100 * 1e6))


def test_missing_lkh_raises_rather_than_substituting():
    """The task forbids quietly swapping in a different solver."""
    chs = [(0.0, 0.0), (300.0, 0.0), (150.0, 260.0)]
    with pytest.raises(RuntimeError, match="LKH not found"):
        T.dubins_tour(chs, rho=RHO, n_headings=4, lkh="/nonexistent/LKH")
