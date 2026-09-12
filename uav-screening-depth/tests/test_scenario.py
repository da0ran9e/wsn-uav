import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from screening import scenario as SC  # noqa: E402
from screening import model as M  # noqa: E402

SIDE = 1000.0
N = 2500


def test_deterministic_in_seed():
    a = SC.generate(42, n_nodes=N, side_m=SIDE, eta=0.5)
    b = SC.generate(42, n_nodes=N, side_m=SIDE, eta=0.5)
    assert a.nodes == b.nodes
    c = SC.generate(43, n_nodes=N, side_m=SIDE, eta=0.5)
    assert a.nodes != c.nodes


def test_all_nodes_inside_region():
    sc = SC.generate(1, n_nodes=N, side_m=SIDE, eta=1.0)
    assert all(0 <= x <= SIDE and 0 <= y <= SIDE for x, y in sc.nodes)
    assert len(sc.nodes) == N


def test_gini_increases_monotonically_in_eta():
    """AGENT-BRIEF E1 acceptance. Averaged over seeds so it is not one draw."""
    etas = [0.0, 0.25, 0.5, 0.75, 1.0]
    g = []
    for eta in etas:
        vals = [SC.density_gini(SC.generate(s, n_nodes=N, side_m=SIDE, eta=eta))
                for s in range(12)]
        g.append(sum(vals) / len(vals))
    for a, b in zip(g, g[1:]):
        assert b > a, f"Gini not increasing in eta: {g}"


def test_hex_tiling_cell_count_matches_the_area_formula():
    """Number of hex cells must track A/((3 sqrt3 /2) R^2), not A/(pi R^2)."""
    for R in (60.0, 94.0, 150.0, 250.0):
        n = len(SC.hex_centres(SIDE, R))
        predicted = M.clusters_from_area(SIDE ** 2, R, 2.598076211)
        # Realised count exceeds the asymptotic formula by a boundary overhead
        # that shrinks as R shrinks. Both are reported downstream; neither is
        # forced to match the other.
        ratio = n / predicted
        assert 1.0 <= ratio <= 1.40, \
            f"R={R}: {n} cells vs asymptotic {predicted:.1f} (ratio {ratio:.2f})"


def test_circle_packing_formula_would_undercount():
    R = 150.0
    hexn = M.clusters_from_area(SIDE ** 2, R, 2.598076211)
    circ = SIDE ** 2 / (math.pi * R ** 2)
    assert hexn / circ == pytest.approx(1.209, abs=0.002)


def test_cluster_heads_are_real_nodes_and_one_per_occupied_cell():
    sc = SC.generate(3, n_nodes=N, side_m=SIDE, eta=0.3)
    chs, counts = SC.cluster_heads(sc, 150.0)
    nodeset = set(sc.nodes)
    assert all(c in nodeset for c in chs)
    assert len(chs) == len(counts) and all(c >= 1 for c in counts)
    assert sum(counts) == len(sc.nodes)


def test_clustered_deployments_leave_cells_empty():
    """This is how eta reaches the flight side: fewer occupied cells."""
    uni = SC.cluster_heads(SC.generate(5, n_nodes=N, side_m=SIDE, eta=0.0), 94.0)[0]
    clu = SC.cluster_heads(SC.generate(5, n_nodes=N, side_m=SIDE, eta=1.0), 94.0)[0]
    assert len(clu) < len(uni)


@pytest.mark.parametrize("R,spacing,expected", [
    (94.0, 20.0, 2.598076211 * 94 ** 2 / 400),
    (150.0, 15.0, 2.598076211 * 150 ** 2 / 225),
    (300.0, 30.0, 2.598076211 * 300 ** 2 / 900),
])
def test_nodes_per_cluster(R, spacing, expected):
    assert SC.nodes_per_cluster(R, spacing) == pytest.approx(expected)
