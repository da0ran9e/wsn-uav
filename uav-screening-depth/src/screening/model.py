"""Core analytical model for the screening-depth campaign.

Every formula here traces to AGENT-BRIEF.md sections 2-3. The four known model
corrections of section 3 are implemented in their CORRECTED form:

  3.1  dose kernel is |ln(1-p)|, NOT p.          -> dose_kernel()
  3.2  two dose regimes; default is m-of-k.      -> theta_all_k(), theta_m_of_k()
  3.3  greedy bound is Wolsey 1+ln(.), not 1-1/e. (cover.py / tests; not used here)
  3.4  there is NO end-to-end guarantee on mission time. Nothing here returns one.

Notation (Appendix B). C == cluster count. C_conf == confidence level. They are
deliberately never the same symbol, in code or in output.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

# --------------------------------------------------------------------------
# 3.1  Dose kernel
# --------------------------------------------------------------------------

def dose_kernel(p: float, kernel: str = "log") -> float:
    """Integral kernel kappa(p) for the dose constraint.

    CORRECTION (brief 3.1). The design document wrote the dose as \\int p dt.
    That is the small-p linearisation. The probability of missing a given file
    entirely along the path is exp(-(lambda/k) \\int |ln(1-p)| dt), so the
    exactly-additive quantity is

        kappa(p) = -ln(1 - p)

    Using p instead understates the contribution of the high-p segments, which
    are exactly the ones near the UAV: +11.6% at p=0.2, +38.6% at p=0.5.

    kernel="linear" selects the (wrong) linearisation so the gap can be
    measured as a reportable ablation. It is never the default.
    """
    if not 0.0 <= p < 1.0:
        raise ValueError(f"p must be in [0,1), got {p}")
    if kernel == "log":
        return -math.log1p(-p)
    if kernel == "linear":
        return p
    raise ValueError(f"unknown kernel {kernel!r}; expected 'log' or 'linear'")


# --------------------------------------------------------------------------
# 3.2  Required dose theta, two regimes
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def theta_all_k(k: int, C_conf: float, p: float) -> float:
    """Regime A: every CH must end the flight holding ALL k files.

    Round-robin over k files gives each file D/k opportunities, so per-file
    success is q = 1 - (1-p)^(D/k) and all-k success is q^k. Requiring
    q^k >= C_conf and solving for D:

        theta_A = k * ln(1 - C_conf^(1/k)) / ln(1 - p)

    Both logs are negative, so theta_A > 0. Grows like k*ln k.
    """
    _check_k(k)
    _check_conf(C_conf)
    _check_p(p)
    per_file = C_conf ** (1.0 / k)
    return k * math.log(1.0 - per_file) / math.log(1.0 - p)


def _binom_sf_ge(k: int, m: int, q: float) -> float:
    """P(Bin(k, q) >= m), exact, in plain floating point."""
    if m <= 0:
        return 1.0
    if m > k:
        return 0.0
    # Sum the smaller tail for accuracy.
    if m - 1 <= k - m:
        lower = sum(math.comb(k, i) * q ** i * (1.0 - q) ** (k - i) for i in range(0, m))
        return 1.0 - lower
    return sum(math.comb(k, i) * q ** i * (1.0 - q) ** (k - i) for i in range(m, k + 1))


@lru_cache(maxsize=None)
def theta_m_of_k(k: int, m: int, C_conf: float, p: float, *, tol: float = 1e-12) -> float:
    """Regime B: a CH crosses threshold on ANY m of the k files.

    CORRECTION (brief 3.2). The group's prior ICCE confidence model is a
    noisy-OR over fragments with equal contributions, so a node crosses
    threshold from a SUBSET of m < k fragments. The constraint is therefore

        P( Bin(k, q) >= m ) >= C_conf,    q = 1 - (1-p)^(D/k)

    Solve for the minimal q by bisection (the left side is strictly increasing
    in q), then invert to D. This is not cosmetic: with m held fixed while k
    grows, theta is essentially FLAT in k, so the paper's headline k*ln k
    factor exists only in Regime A.

    m == k reduces exactly to theta_all_k (asserted in tests).
    """
    _check_k(k)
    _check_conf(C_conf)
    _check_p(p)
    if not 1 <= m <= k:
        raise ValueError(f"need 1 <= m <= k, got m={m}, k={k}")

    lo, hi = 0.0, 1.0 - 1e-15
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if _binom_sf_ge(k, m, mid) >= C_conf:
            hi = mid
        else:
            lo = mid
    q = hi
    return k * math.log1p(-q) / math.log1p(-p)


def theta(k: int, *, regime: str, m: int | None, C_conf: float, p: float) -> float:
    """Dispatch on regime. The regime is ALWAYS explicit -- never defaulted
    silently to A (brief 13)."""
    if regime == "all-k":
        return theta_all_k(k, C_conf, p)
    if regime == "m-of-k":
        if m is None:
            raise ValueError("regime 'm-of-k' requires m")
        return theta_m_of_k(k, min(m, k), C_conf, p)
    raise ValueError(f"unknown regime {regime!r}")


def m_for_policy(k: int, *, m_policy: str, m_fixed: int | None, m_frac: float | None) -> int:
    """Resolve m from the policy. m is capped at k and floored at 1."""
    if m_policy == "equal-k":
        return k
    if m_policy.startswith("fixed"):
        if m_fixed is None:
            raise ValueError("fixed m_policy requires m_fixed")
        return max(1, min(m_fixed, k))
    if m_policy.startswith("proportional"):
        if m_frac is None:
            raise ValueError("proportional m_policy requires m_frac")
        return max(1, min(k, int(math.ceil(m_frac * k))))
    raise ValueError(f"unknown m_policy {m_policy!r}")


# --------------------------------------------------------------------------
# Geometry: clusters, area, sweep length
# --------------------------------------------------------------------------

def clusters_from_area(area_m2: float, R_cluster_m: float, hex_coeff: float) -> float:
    """C = A / (hex_coeff * R^2), hex_coeff = 3*sqrt(3)/2 ~ 2.598.

    NOTE (E2): A/(pi R^2) appears in earlier drafts and is wrong by 21%
    (pi/2.598 = 1.2092). Hexagonal packing is the correct reference.
    """
    return area_m2 / (hex_coeff * R_cluster_m ** 2)


def area_from_clusters(C: float, R_cluster_m: float, hex_coeff: float) -> float:
    return C * hex_coeff * R_cluster_m ** 2


@lru_cache(maxsize=None)
def sweep_length_m(area_m2: float, track_spacing_m: float, rho_m: float,
                   turn_penalty_coeff_rho: float) -> float:
    """Length of ONE full lawnmower sweep of the deployment area, including the
    Dubins turnaround penalty at the end of each track.

    L = A / spacing  +  n_tracks * turn_coeff * rho,   n_tracks = sqrt(A)/spacing

    A square region is assumed, so n_tracks = sqrt(A)/spacing. This is a stated
    modelling choice, not a measurement; E5 replaces it with a realised tour.
    """
    n_tracks = math.sqrt(area_m2) / track_spacing_m
    return area_m2 / track_spacing_m + n_tracks * turn_penalty_coeff_rho * rho_m


# --------------------------------------------------------------------------
# r(k) and f(k) families
# --------------------------------------------------------------------------

def r_of_k(k: int, family: str, par: dict) -> float:
    """True accept rate (== TAR). Increasing, concave, saturating."""
    if family == "sat-exp":
        return par["r_inf"] * (1.0 - math.exp(-k / par["k_r"]))
    if family == "logistic":
        return par["r_inf"] / (1.0 + math.exp(-(k - par["k0"]) / par["s"]))
    if family == "hill":
        ka = k ** par["a"]
        return par["r_inf"] * ka / (ka + par["k_r"] ** par["a"])
    raise ValueError(f"unknown r family {family!r}")


def f_of_k(k: int, family: str, par: dict) -> float:
    """False alarm rate (== FAR). Decreasing, convex."""
    floor = par.get("f_floor", 0.0)
    if family == "exp-decay":
        v = par["f0"] * math.exp(-k / par["k_f"])
    elif family == "power-law":
        v = par["f0"] * k ** (-par["b"])
    elif family == "logistic-dec":
        v = par["f0"] / (1.0 + math.exp((k - par["k0f"]) / par["sf"]))
    else:
        raise ValueError(f"unknown f family {family!r}")
    return max(floor, min(1.0, v))


def n_flagged(r: float, f: float, C: float) -> float:
    """Expected number of clusters flagged: r + f*(C-1)  (brief 2.2)."""
    return r + f * (C - 1.0)


# --------------------------------------------------------------------------
# Phase times and the objective
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Times:
    T1_s: float
    T2_s: float
    T_miss_s: float
    T_total_s: float
    passes_per_ch: float
    L_sweep_m: float
    N_flagged: float
    theta_required: float


def passes_per_ch(theta_req: float, lambda_ops: float, broadcast_radius_m: float,
                  v_mps: float) -> float:
    """How many straight passes over a CH the dose demand implies.

    One straight pass through a disc of radius R_b at speed v spends
    t_pass = 2*R_b/v seconds in range, delivering lambda*t_pass opportunities
    (at the reference p). So passes = theta / (lambda * t_pass).

    This is the feasibility figure of brief 3.2 and it is reported verbatim.
    """
    t_pass = 2.0 * broadcast_radius_m / v_mps
    return theta_req / (lambda_ops * t_pass)


def phase1_time_s(theta_req: float, cfg: dict, area_m2: float) -> tuple[float, float, float]:
    """Returns (T1_s, L_sweep_m, passes_per_ch).

    T1 = max(1, passes) * L_sweep / v. The floor of one pass is physical: the
    UAV must cover the area at least once regardless of how small theta is.
    """
    veh, rad, ph1 = cfg["vehicle"], cfg["radio"], cfg["phase1"]
    L = sweep_length_m(area_m2, ph1["track_spacing_m"], veh["rho_m"],
                       ph1["turn_penalty_coeff_rho"])
    n = passes_per_ch(theta_req, rad["lambda_ops_per_s"], rad["broadcast_radius_m"],
                      veh["v_mps"])
    return max(1.0, n) * L / veh["v_mps"], L, n


def phase2_time_s(N: float, cfg: dict, area_m2: float) -> float:
    """Verification flight over N flagged clusters.

    L2 = beta*sqrt(N*A) + N*dubins_hop_coeff*rho   (BHH tour + a per-visit
    Dubins penalty), then T2 = L2/v + N*dwell. The Dubins penalty is a stated
    modelling coefficient, NOT a bound -- see brief 3.4.
    """
    veh, ph2 = cfg["vehicle"], cfg["phase2"]
    if N <= 0:
        return 0.0
    L2 = ph2["tsp_constant_beta"] * math.sqrt(N * area_m2) \
        + N * ph2["dubins_hop_coeff_rho"] * veh["rho_m"]
    return L2 / veh["v_mps"] + N * ph2["verify_dwell_s"]


def t_total(k: int, cfg: dict, *, regime: str, m_policy: str, m_fixed: int | None,
            m_frac: float | None, r_family: str, r_par: dict, f_family: str,
            f_par: dict, R_cluster_m: float, T_miss_mult: float,
            area_m2: float | None = None, C: float | None = None,
            continuous_m: bool = False) -> Times:
    """T_total(k) = T1(k) + r(k)*T2(k) + (1-r(k))*T_miss   (brief 2.2).

    Exactly one of area_m2 / C may be pinned; the other follows from hex packing.
    T_miss is expressed as a multiple of one full single-sweep time, so it is
    dimensionally a time and scales with the scenario.

    continuous_m=True uses the real-valued m = m_frac*k relaxation. That is a
    DIAGNOSTIC path only (see theta_m_of_k_continuous); physical m is integer.
    """
    dep, sig, rad = cfg["deployment"], cfg["signature"], cfg["radio"]
    hexc = dep["hex_packing_coeff"]
    if area_m2 is None and C is None:
        area_m2 = dep["area_m2"]
    if C is None:
        C = clusters_from_area(area_m2, R_cluster_m, hexc)
    if area_m2 is None:
        area_m2 = area_from_clusters(C, R_cluster_m, hexc)

    if continuous_m:
        if m_frac is None:
            raise ValueError("continuous_m requires m_frac")
        m = m_frac * k
        th = theta_m_of_k_continuous(k, m, sig["C_conf"], rad["p_ref"])
    else:
        m = m_for_policy(k, m_policy=m_policy, m_fixed=m_fixed, m_frac=m_frac)
        th = theta(k, regime=regime, m=m, C_conf=sig["C_conf"], p=rad["p_ref"])

    T1, L_sweep, n_pass = phase1_time_s(th, cfg, area_m2)
    r = r_of_k(k, r_family, r_par)
    f = f_of_k(k, f_family, f_par)
    N = n_flagged(r, f, C)
    T2 = phase2_time_s(N, cfg, area_m2)
    T_miss = T_miss_mult * L_sweep / cfg["vehicle"]["v_mps"]
    return Times(T1, T2, T_miss, T1 + r * T2 + (1.0 - r) * T_miss,
                 n_pass, L_sweep, N, th)


# --------------------------------------------------------------------------
# Shape diagnostics on a T_total(k) curve
# --------------------------------------------------------------------------

def curve_shape(ks: list[int], vals: list[float], *, tol_rel: float) -> dict:
    """Classify a T_total(k) curve.

    k_star        argmin over the evaluated grid
    interior      k_star is strictly inside [k_min, k_max]
    rel_depth     how far k_star beats the BETTER of the two boundaries,
                  relative to T(k_star). A tiny depth means the interior
                  optimum is cosmetic, so it is reported, not hidden.
    quasiconvex   the sequence is non-increasing then non-decreasing
                  (the paper's central structural claim)
    """
    i_star = min(range(len(vals)), key=lambda i: vals[i])
    best_boundary = min(vals[0], vals[-1])
    rel_depth = (best_boundary - vals[i_star]) / vals[i_star] if vals[i_star] > 0 else 0.0

    # quasiconvex == unimodal with a single descent then a single ascent
    tol = tol_rel * max(abs(v) for v in vals)
    i, n = 0, len(vals)
    while i + 1 < n and vals[i + 1] <= vals[i] + tol:
        i += 1
    while i + 1 < n and vals[i + 1] >= vals[i] - tol:
        i += 1
    quasiconvex = (i == n - 1)

    # Magnitude of the quasiconvexity violation, not just a boolean. A curve
    # can fail the strict test by a sawtooth of 1% while its trend is textbook
    # quasiconvex, and a bare False would hide that.
    # A quasiconvex sequence is non-increasing BEFORE k* and non-decreasing
    # AFTER it. Scan both sides: scanning only after k* reports zero violations
    # whenever k* sits at the upper boundary, which is exactly the case that
    # needs measuring.
    n_viol, max_viol_rel = 0, 0.0
    for j in range(0, i_star):                  # before k*: a rise is a violation
        if vals[j + 1] > vals[j] + tol:
            n_viol += 1
            max_viol_rel = max(max_viol_rel, (vals[j + 1] - vals[j]) / vals[j])
    for j in range(i_star, n - 1):              # after k*: a fall is a violation
        if vals[j + 1] < vals[j] - tol:
            n_viol += 1
            max_viol_rel = max(max_viol_rel, (vals[j] - vals[j + 1]) / vals[j])

    # Quasiconvexity of the even-k subsequence. Under an m = ceil(frac*k) policy
    # the realised m/k ratio alternates with the parity of k (k=3 -> m/k=0.67,
    # k=4 -> 0.50), which injects a sawtooth into theta. Restricting to even k
    # holds m/k constant and so separates the POLICY artifact from the shape of
    # the objective itself. For policies without that parity coupling this is
    # simply a coarser grid and should agree with the full test.
    def _quasiconvex(seq: list[float]) -> bool:
        t = tol_rel * max(abs(v) for v in seq)
        i2, n2 = 0, len(seq)
        while i2 + 1 < n2 and seq[i2 + 1] <= seq[i2] + t:
            i2 += 1
        while i2 + 1 < n2 and seq[i2 + 1] >= seq[i2] - t:
            i2 += 1
        return i2 == n2 - 1

    even = [v for k_, v in zip(ks, vals) if k_ % 2 == 0]
    even_ks = [k_ for k_ in ks if k_ % 2 == 0]
    i_even = min(range(len(even)), key=lambda i: even[i]) if even else 0

    return {
        "k_star": ks[i_star],
        "T_at_kstar": vals[i_star],
        "at_lower": i_star == 0,
        "at_upper": i_star == len(vals) - 1,
        "interior": 0 < i_star < len(vals) - 1,
        "rel_depth": rel_depth,
        "quasiconvex": quasiconvex,
        "n_violations": n_viol,
        "max_violation_rel": max_viol_rel,
        "quasiconvex_even_k": _quasiconvex(even) if len(even) > 2 else quasiconvex,
        "k_star_even_k": even_ks[i_even] if even else ks[i_star],
    }


# --------------------------------------------------------------------------

def _check_k(k: int) -> None:
    if not isinstance(k, int) or k < 1:
        raise ValueError(f"k must be a positive int, got {k!r}")


def _check_conf(c: float) -> None:
    if not 0.0 < c < 1.0:
        raise ValueError(f"C_conf must be in (0,1), got {c}")


def _check_p(p: float) -> None:
    if not 0.0 < p < 1.0:
        raise ValueError(f"p must be in (0,1), got {p}")


# --------------------------------------------------------------------------
# Which m-policy is physically real? Derived from the Appendix A.2 evidence
# model. NOT stated in the brief -- see docs/AUDIT-E0.md, assumption A1.
# --------------------------------------------------------------------------

def fragment_evidence(pixel_fraction: float, base: float = 0.90) -> float:
    """Appendix A.2, matched exactly:

        evidence_i = 1 - (1 - 0.90)^(pixelCount_i / totalPixels)

    With pixel-stride interleaving over k equal files, pixel_fraction = 1/k.
    """
    return 1.0 - (1.0 - base) ** pixel_fraction


def noisy_or_confidence(m: int, k: int, base: float = 0.90) -> float:
    """Noisy-OR over m of k equal-contribution fragments (brief 3.2, A.2):

        C = 1 - prod(1 - u_i),  u_i = 1 - (1-base)^(1/k)
          = 1 - (1-base)^(m/k)

    Note the consequence: the accumulated confidence depends ONLY on the ratio
    m/k, not on k itself.
    """
    return 1.0 - (1.0 - base) ** (m / k)


def m_over_k_from_suspicion_threshold(thr: float, base: float = 0.90) -> float:
    """The fraction alpha = m/k implied by a screening threshold thr.

    Inverting noisy_or_confidence: 1 - (1-base)^(m/k) >= thr gives

        alpha = ln(1 - thr) / ln(1 - base)

    This is the key structural consequence for E0: because the k files
    partition one fixed payload, each fragment's evidence SHRINKS as k grows,
    so m must grow PROPORTIONALLY to k to reach the same confidence. m is
    therefore not a free policy knob -- it is set by the screening threshold,
    and the proportional-m policy is the physically implied one.

    alpha >= 1 (thr >= base) means the threshold is unreachable from a strict
    subset: the regime collapses to all-k (Regime A) or is infeasible.
    """
    if not 0.0 < thr < 1.0:
        raise ValueError(f"thr must be in (0,1), got {thr}")
    return math.log(1.0 - thr) / math.log(1.0 - base)


# --------------------------------------------------------------------------
# Continuous-m relaxation -- a DIAGNOSTIC, not the physical model.
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def theta_m_of_k_continuous(k: int, m_real: float, C_conf: float, p: float, *,
                            tol: float = 1e-12) -> float:
    """theta for real-valued m, via the regularized incomplete beta function.

        P(Bin(k, q) >= m) = I_q(m, k - m + 1)

    which is exact at integer m and continuous in between. Used ONLY to
    separate the shape of the objective from the integrality of m: under an
    m = ceil(alpha*k) policy the realised ratio m/k oscillates with k, which
    injects a sawtooth into theta. Physically m is an integer, so this
    relaxation is never the reported cost -- it answers the different question
    "is the underlying objective quasiconvex?".
    """
    from scipy.special import betainc  # local import: diagnostic path only

    _check_k(k)
    _check_conf(C_conf)
    _check_p(p)
    if not 0.0 < m_real <= k:
        raise ValueError(f"need 0 < m_real <= k, got m_real={m_real}, k={k}")

    a, b = m_real, k - m_real + 1.0
    lo, hi = 0.0, 1.0 - 1e-15
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if float(betainc(a, b, mid)) >= C_conf:
            hi = mid
        else:
            lo = mid
    return k * math.log1p(-hi) / math.log1p(-p)
