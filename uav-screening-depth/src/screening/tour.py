"""Phase-1 tour length: BHH estimate and an actual Dubins tour.

Pipeline for the realised tour (task section 5):
  heading sampling -> GTSP -> Noon-Bean -> ATSP -> LKH

The Noon-Bean transformation is the standard one: inside each cluster the nodes
are joined by a zero-cost directed cycle, so an ATSP tour that enters the cluster
at w must traverse the whole cycle and leave from pred(w). An inter-cluster arc
out of u therefore has to be charged the true cost from u's SUCCESSOR:

    c(u, w) = d(succ_P(u), w) + M     for u in P, w in Q != P

with M large enough that no tour takes a surplus inter-cluster arc. Every tour
visiting all C clusters uses exactly C such arcs, so C*M is a constant offset and
is subtracted back out.
"""
from __future__ import annotations

import math
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

from . import dubins as DB

LKH_BIN_ENV = "LKH_BIN"
# LKH needs integer weights and stores them as C int, so every weight and every
# tour total must stay well inside 2^31. Weights are in METRES: the matrix only
# decides the tour ORDER, and the reported length is recomputed exactly in
# floating point from the recovered representatives, so 1 m quantisation costs
# nothing in the reported number.
_SCALE = 1
# Stand-in for +inf on forbidden (non-successor intra-cluster) arcs. Must exceed
# the cost of any tour built from allowed arcs, which is ~C*(M + max_arc).
_BIG = 10 ** 9


def find_lkh() -> str | None:
    cand = os.environ.get(LKH_BIN_ENV)
    if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
        return cand
    return shutil.which("LKH")


def _require_lkh(explicit: str | None) -> str:
    """Resolve the solver, failing with a clear message. An explicitly supplied
    path that does not exist is an error, not a reason to fall back: the task
    forbids quietly substituting a different solver for LKH."""
    if explicit is not None:
        if not (os.path.isfile(explicit) and os.access(explicit, os.X_OK)):
            raise RuntimeError(f"LKH not found at the given path: {explicit}")
        return explicit
    found = find_lkh()
    if found is None:
        raise RuntimeError("LKH not found; set LKH_BIN or put LKH on PATH")
    return found


def bhh_tour_length_m(n_stops: int, area_m2: float, beta: float) -> float:
    """Beardwood-Halton-Hammersley estimate: l ~ beta * sqrt(n * A).

    The task writes beta ~ 0.7; the configured default is the standard constant
    0.7124. Degenerate for n < 2.
    """
    if n_stops < 2:
        return 0.0
    return beta * math.sqrt(n_stops * area_m2)


@dataclass(frozen=True)
class TourResult:
    n_clusters: int
    n_headings: int
    length_m: float
    solver: str
    max_kappa_rho: float
    words: dict[str, int]
    wall_s: float


def _headings(n: int) -> list[float]:
    return [2.0 * math.pi * i / n for i in range(n)]


def build_cost_matrix(chs: list[tuple[float, float]], n_headings: int,
                      rho: float) -> tuple[list[list[int]], list[tuple[float, float, float]], int]:
    """Noon-Bean ATSP matrix over the (cluster x heading) ground set."""
    psis = _headings(n_headings)
    nodes: list[tuple[float, float, float]] = []
    cluster_of: list[int] = []
    for ci, (x, y) in enumerate(chs):
        for psi in psis:
            nodes.append((x, y, psi))
            cluster_of.append(ci)
    n = len(nodes)

    # True Dubins cost between every ordered pair in different clusters. Built
    # with the vectorised length matrix, which cross-checks itself against the
    # scalar forward-verified reference on every call: at 120 clusters x 8
    # headings this is a 960x960 matrix and the scalar loop dominated everything
    # else in the pipeline (27 s vs 1.9 s per instance).
    L = DB.length_matrix(nodes, rho)
    d = [[0] * n for _ in range(n)]
    total = 0
    for i in range(n):
        ci = cluster_of[i]
        row = L[i]
        di = d[i]
        for j in range(n):
            if ci == cluster_of[j]:
                continue
            v = row[j]
            w = int(round((v if v < 1e8 else 1e9) * _SCALE))
            di[j] = w
            total += w
    # The Noon-Bean penalty M is NOT optional. Forbidding non-successor
    # intra-cluster arcs is not enough to force one visit per cluster, because
    # re-ENTERING a cluster at a fresh node uses an ordinary inter-cluster arc
    # and so costs nothing extra: a tour may traverse part of a cluster's cycle,
    # leave, and come back to finish it (observed: 121 blocks for 120 clusters
    # with M = 0). Charging M per inter-cluster arc makes any surplus arc cost
    # more than the entire real tour can save, so the optimum uses exactly C of
    # them and C*M is a constant offset that is subtracted back out.
    max_arc = max((max(row) for row in d), default=0)
    M = len(chs) * max_arc + 1

    # successor inside each cluster's zero-cost cycle
    succ = list(range(n))
    for ci in range(len(chs)):
        idx = [i for i in range(n) if cluster_of[i] == ci]
        for a, b in zip(idx, idx[1:] + idx[:1]):
            succ[a] = b

    cost = [[_BIG] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if cluster_of[i] != cluster_of[j]:
                cost[i][j] = d[succ[i]][j] + M
        cost[i][i] = 0
    # zero-cost directed cycle inside each cluster, written last so it wins
    for ci in range(len(chs)):
        idx = [i for i in range(n) if cluster_of[i] == ci]
        for a, b in zip(idx, idx[1:] + idx[:1]):
            cost[a][b] = 0
    assert total >= 0
    return cost, nodes, M


def _run_lkh(cost: list[list[int]], lkh: str, runs: int = 1,
             seed: int | None = None) -> list[int]:
    n = len(cost)
    with tempfile.TemporaryDirectory() as td:
        prob = os.path.join(td, "p.atsp")
        par = os.path.join(td, "p.par")
        tour = os.path.join(td, "p.tour")
        with open(prob, "w") as fh:
            fh.write(f"NAME: gtsp\nTYPE: ATSP\nDIMENSION: {n}\n"
                     "EDGE_WEIGHT_TYPE: EXPLICIT\nEDGE_WEIGHT_FORMAT: FULL_MATRIX\n"
                     "EDGE_WEIGHT_SECTION\n")
            for row in cost:
                fh.write(" ".join(str(v) for v in row) + "\n")
            fh.write("EOF\n")
        with open(par, "w") as fh:
            # PRECISION = 1 is required: LKH's ATSP -> TSP transformation
            # asserts Gain % Precision == 0, which fails for arbitrary integer
            # weights under the default PRECISION = 100.
            fh.write(f"PROBLEM_FILE = {prob}\nTOUR_FILE = {tour}\n"
                     f"RUNS = {runs}\nPRECISION = 1\nTRACE_LEVEL = 0\n")
            if seed is not None:
                fh.write(f"SEED = {seed}\n")
        r = subprocess.run([lkh, par], capture_output=True, text=True, timeout=1800)
        if not os.path.exists(tour):
            raise RuntimeError(f"LKH produced no tour: {r.stdout[-400:]} {r.stderr[-400:]}")
        order, reading = [], False
        for line in open(tour):
            line = line.strip()
            if line == "TOUR_SECTION":
                reading = True
                continue
            if reading:
                if line in ("-1", "EOF", ""):
                    break
                order.append(int(line) - 1)
        return order


def dubins_tour(chs: list[tuple[float, float]], *, rho: float, n_headings: int,
                lkh: str | None = None, ds_m: float = 2.0,
                seed: int | None = None) -> TourResult:
    """Realised closed Dubins tour through every cluster head.

    Returns the tour length, the worst |kappa|*rho along the sampled path, and
    the Dubins word histogram. Raises if LKH is unavailable -- the task forbids
    substituting a stand-in for the specified solver without saying so.
    """
    import time
    t0 = time.time()
    C = len(chs)
    if C == 0:
        return TourResult(0, n_headings, 0.0, "trivial", 0.0, {}, 0.0)
    if C == 1:
        return TourResult(1, n_headings, 0.0, "trivial", 0.0, {}, time.time() - t0)

    lkh = _require_lkh(lkh)

    cost, nodes, M = build_cost_matrix(chs, n_headings, rho)
    order = _run_lkh(cost, lkh, seed=seed)
    if len(order) != len(nodes):
        raise RuntimeError(f"LKH returned {len(order)} of {len(nodes)} nodes")

    # Recover the chosen representative per cluster: the tour enters a cluster at
    # some node and leaves from its predecessor in the zero-cycle. Walk the tour
    # and keep the first node of each cluster block.
    reps: list[int] = []
    cl = [0] * len(nodes)
    for i, nd in enumerate(nodes):
        cl[i] = i // n_headings
    prev_cluster = cl[order[-1]]
    for idx in order:
        if cl[idx] != prev_cluster:
            reps.append(idx)
        prev_cluster = cl[idx]
    if len(reps) != C:
        raise RuntimeError(
            f"recovered {len(reps)} representatives for {C} clusters: the tour "
            f"split a cluster into several blocks, which means the Noon-Bean "
            f"penalty M is too small")
    n_inter = sum(1 for a, b in zip(order, order[1:] + order[:1]) if cl[a] != cl[b])
    if n_inter != C:
        raise RuntimeError(f"tour uses {n_inter} inter-cluster arcs, expected {C}")

    length = 0.0
    words: dict[str, int] = {}
    worst = 0.0
    for a, b in zip(reps, reps[1:] + reps[:1]):
        p = DB.dubins_path(nodes[a], nodes[b], rho)
        if p is None:
            raise RuntimeError("no Dubins path between consecutive representatives")
        length += p.length
        words[p.word] = words.get(p.word, 0) + 1
        worst = max(worst, DB.max_abs_curvature(DB.sample_path(p, ds_m), rho) * rho)
    return TourResult(C, n_headings, length, f"LKH({os.path.basename(lkh)})",
                      worst, words, time.time() - t0)
