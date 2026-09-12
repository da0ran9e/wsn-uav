"""Scenario generation: node placement with a heterogeneity parameter eta.

Minimal on purpose -- this probe needs node positions only so that cluster heads
land somewhere realistic. The square region A = 1 km^2 has no holes, so no
polygon library is required.

Notation follows the task prompt: eta is deployment heterogeneity (0 = uniform,
1 = strongly clustered). NOTE: the brief called this h; the probe prompt calls it
eta, and KY-HIEU-vi.md -- which the prompt says fixes notation -- is not present
in this repository. eta is used throughout. See STATUS.md.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    seed: int
    eta: float
    side_m: float
    nodes: list[tuple[float, float]]

    @property
    def area_m2(self) -> float:
        return self.side_m ** 2


def generate(seed: int, *, n_nodes: int, side_m: float, eta: float,
             n_hotspots: int = 8, hotspot_sigma_m: float = 70.0) -> Scenario:
    """Place n_nodes in a square of the given side.

    eta mixes a uniform field with a Thomas-style clustered field: a fraction eta
    of nodes are drawn around n_hotspots Gaussian centres, the rest uniformly.
    eta = 0 is uniform; eta = 1 is fully clustered. Deterministic in seed.
    """
    if not 0.0 <= eta <= 1.0:
        raise ValueError(f"eta must be in [0,1], got {eta}")
    rng = random.Random(seed * 1_000_003 + 17)
    centres = [(rng.uniform(0, side_m), rng.uniform(0, side_m))
               for _ in range(n_hotspots)]
    pts: list[tuple[float, float]] = []
    for _ in range(n_nodes):
        if rng.random() < eta:
            cx, cy = centres[rng.randrange(n_hotspots)]
            x = min(side_m, max(0.0, rng.gauss(cx, hotspot_sigma_m)))
            y = min(side_m, max(0.0, rng.gauss(cy, hotspot_sigma_m)))
        else:
            x, y = rng.uniform(0, side_m), rng.uniform(0, side_m)
        pts.append((x, y))
    return Scenario(seed, eta, side_m, pts)


def density_gini(sc: Scenario, cell_m: float = 50.0) -> float:
    """Gini coefficient of the per-cell node count. AGENT-BRIEF E1 acceptance:
    must increase monotonically in eta."""
    n = max(1, int(math.ceil(sc.side_m / cell_m)))
    grid = [0] * (n * n)
    for x, y in sc.nodes:
        i = min(n - 1, int(x / cell_m))
        j = min(n - 1, int(y / cell_m))
        grid[j * n + i] += 1
    vals = sorted(grid)
    tot = sum(vals)
    if tot == 0:
        return 0.0
    m = len(vals)
    cum = sum((2 * (i + 1) - m - 1) * v for i, v in enumerate(vals))
    return cum / (m * tot)


# --------------------------------------------------------------------------
# Phase-0 stand-in: hexagonal tiling -> cluster head set
# --------------------------------------------------------------------------

def hex_centres(side_m: float, R_cluster_m: float) -> list[tuple[float, float]]:
    """Centres of a hexagonal tiling of circumradius R covering the square.

    Flat-to-flat spacing is sqrt(3)*R between columns and 1.5*R between rows,
    which is the packing whose cell area is (3*sqrt(3)/2) R^2 -- the same
    constant as model.clusters_from_area. A/(pi R^2) is WRONG by 21% and must
    not be used (task section 8).

    Only centres lying INSIDE the square are kept, which makes the cell count
    track A/(dx*dy) = A/((3 sqrt3 /2) R^2). Nodes in the outer band are absorbed
    by the nearest-centre assignment, so boundary clusters are slightly larger --
    a real boundary effect, and the realised count runs 1.1-1.3x the asymptotic
    formula at these R. Both numbers are reported rather than forced to agree.
    """
    dx = math.sqrt(3.0) * R_cluster_m
    dy = 1.5 * R_cluster_m
    out = []
    j = 0
    y = 0.0
    while y <= side_m:
        offset = 0.0 if j % 2 == 0 else dx / 2.0
        x = offset
        while x <= side_m:
            out.append((x, y))
            x += dx
        y += dy
        j += 1
    return out


def cluster_heads(sc: Scenario, R_cluster_m: float) -> tuple[list[tuple[float, float]],
                                                             list[int]]:
    """Elect one CH per occupied hex cell: the node nearest the cell centre.

    Returns (CH positions, member counts). Empty cells are dropped -- which is
    how eta enters the flight side: clustered deployments leave cells empty and
    so need fewer stops.
    """
    centres = hex_centres(sc.side_m, R_cluster_m)
    if not centres:
        return [], []
    assign: dict[int, list[int]] = {}
    for ni, (x, y) in enumerate(sc.nodes):
        best, bd = -1, float("inf")
        for ci, (cx, cy) in enumerate(centres):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d < bd:
                bd, best = d, ci
        assign.setdefault(best, []).append(ni)
    chs, counts = [], []
    for ci, members in sorted(assign.items()):
        cx, cy = centres[ci]
        best = min(members, key=lambda ni: (sc.nodes[ni][0] - cx) ** 2
                                           + (sc.nodes[ni][1] - cy) ** 2)
        chs.append(sc.nodes[best])
        counts.append(len(members))
    return chs, counts


def nodes_per_cluster(R_cluster_m: float, lattice_spacing_m: float,
                      hex_coeff: float = 2.598076211) -> float:
    """n_c: expected nodes in one hex cell of circumradius R on a lattice of the
    given spacing. Used by B4 to vary n_c independently of R."""
    return hex_coeff * R_cluster_m ** 2 / lattice_spacing_m ** 2
