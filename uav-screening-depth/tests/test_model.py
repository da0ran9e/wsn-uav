"""Unit tests that reproduce the expected-value tables in AGENT-BRIEF.md.

These tables ARE the specification (Appendix C, step 4). If one of these fails,
the implementation is wrong, not the table.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from screening import model as M  # noqa: E402

P_REF, C_CONF = 0.3, 0.95


# ---- brief 3.1: the kernel table -----------------------------------------
# p | p | |ln(1-p)| | error
KERNEL_TABLE = [
    (0.05, 0.050, 0.051, 0.026),
    (0.10, 0.100, 0.105, 0.054),
    (0.20, 0.200, 0.223, 0.116),
    (0.30, 0.300, 0.357, 0.189),
    (0.50, 0.500, 0.693, 0.386),
]


@pytest.mark.parametrize("p,lin,log,err", KERNEL_TABLE)
def test_dose_kernel_table(p, lin, log, err):
    assert M.dose_kernel(p, "linear") == pytest.approx(lin, abs=5e-4)
    assert M.dose_kernel(p, "log") == pytest.approx(log, abs=5e-4)
    observed_err = (M.dose_kernel(p, "log") - M.dose_kernel(p, "linear")) / p
    assert observed_err == pytest.approx(err, abs=1e-3)


def test_kernel_log_exceeds_linear_everywhere():
    """The linearisation always UNDERSTATES the dose (brief 3.1)."""
    for i in range(1, 99):
        p = i / 100
        assert M.dose_kernel(p, "log") > M.dose_kernel(p, "linear")


def test_kernel_is_exactly_additive():
    """kappa is additive in the sense that the per-file miss probability
    factorises: (1-p1)(1-p2) == exp(-(kappa1+kappa2))."""
    p1, p2 = 0.2, 0.45
    assert (1 - p1) * (1 - p2) == pytest.approx(
        math.exp(-(M.dose_kernel(p1) + M.dose_kernel(p2))), rel=1e-12)


def test_kernel_rejects_unknown():
    with pytest.raises(ValueError):
        M.dose_kernel(0.3, "sqrt")


# ---- brief 3.2: theta, all-k vs m-of-k at k=10 ---------------------------
# requirement | theta | ratio vs all-k
THETA_K10 = [(10, 147.9, 1.0), (7, 53.2, 2.8), (5, 33.4, 4.4), (3, 19.8, 7.5), (2, 14.1, 10.5)]


@pytest.mark.parametrize("m,expected,ratio", THETA_K10)
def test_theta_k10_table(m, expected, ratio):
    th = M.theta_m_of_k(10, m, C_CONF, P_REF)
    assert th == pytest.approx(expected, abs=0.05)
    th_all = M.theta_all_k(10, C_CONF, P_REF)
    assert th_all / th == pytest.approx(ratio, abs=0.05)


def test_theta_all_k_default_point():
    assert M.theta_all_k(10, C_CONF, P_REF) == pytest.approx(147.9, abs=0.05)


def test_m_equals_k_reduces_to_regime_A():
    """theta_m_of_k(k, k) must agree with the closed form theta_all_k(k)."""
    for k in (2, 3, 4, 6, 10, 16, 25, 40):
        assert M.theta_m_of_k(k, k, C_CONF, P_REF) == pytest.approx(
            M.theta_all_k(k, C_CONF, P_REF), rel=1e-6)


# ---- brief 3.2: theta is FLAT in k at fixed m ----------------------------
# rows m=2,3,4 ; columns k=4,6,10,16,25,40
FLAT_TABLE = {
    2: {4: 15.6, 6: 14.7, 10: 14.1, 16: 13.7, 25: 13.6, 40: 13.5},
    3: {4: 26.1, 6: 21.9, 10: 19.8, 16: 18.9, 25: 18.4, 40: 18.1},
    4: {4: 48.9, 6: 31.6, 10: 26.2, 16: 24.2, 25: 23.2, 40: 22.6},
}


@pytest.mark.parametrize("m", sorted(FLAT_TABLE))
@pytest.mark.parametrize("k", [4, 6, 10, 16, 25, 40])
def test_theta_flat_table(m, k):
    assert M.theta_m_of_k(k, m, C_CONF, P_REF) == pytest.approx(
        FLAT_TABLE[m][k], abs=0.06)


@pytest.mark.parametrize("m", [2, 3, 4, 6])
def test_theta_fixed_m_is_decreasing_in_k(m):
    """At fixed m, theta does not grow with k -- so no ln k factor (brief 3.2)."""
    ks = list(range(m, 41))
    vals = [M.theta_m_of_k(k, m, C_CONF, P_REF) for k in ks]
    for a, b in zip(vals, vals[1:]):
        assert b <= a + 1e-9


def test_theta_all_k_matches_asymptotic_closed_form():
    """brief 3.2: theta_A ~ k*[ln k - ln|ln C_conf|] / |ln(1-p)|.

    Accurate to better than 0.1% already at k=4, because
    1 - C_conf^(1/k) -> |ln C_conf|/k quickly.
    """
    for k in (4, 8, 10, 16, 32, 40):
        asymptotic = k * (math.log(k) - math.log(abs(math.log(C_CONF)))) / abs(math.log(1 - P_REF))
        assert M.theta_all_k(k, C_CONF, P_REF) == pytest.approx(asymptotic, rel=2e-3)


def test_theta_all_k_is_superlinear_in_k():
    """The ln k factor IS present in Regime A: theta_A/k strictly increases."""
    per_file = [M.theta_all_k(k, C_CONF, P_REF) / k for k in range(2, 41)]
    for a, b in zip(per_file, per_file[1:]):
        assert b > a


def test_ln_k_factor_is_real_but_mild_over_the_operational_range():
    """Honest magnitude, for the E0 report: over k=4..40 the LINEAR factor
    contributes 10x while the ln k factor contributes only ~1.5x, because at
    C_conf=0.95 the constant -ln|ln C_conf| = 2.97 dominates ln k in [0.69, 3.69].

    This is why 'theta_A grows like k ln k' must not be read as 'theta_A is
    dominated by ln k' anywhere in the paper.
    """
    lo = M.theta_all_k(4, C_CONF, P_REF) / 4
    hi = M.theta_all_k(40, C_CONF, P_REF) / 40
    assert hi / lo == pytest.approx(1.53, abs=0.03)
    assert M.theta_all_k(40, C_CONF, P_REF) / M.theta_all_k(4, C_CONF, P_REF) == \
        pytest.approx(15.3, abs=0.3)


# ---- brief 3.2: the feasibility / passes-per-CH table --------------------
# theta | in-range seconds | passes over each CH
PASSES_TABLE = [(147.9, 29.6, 5.9), (33.4, 6.7, 1.3), (19.8, 4.0, 0.8)]


@pytest.mark.parametrize("th,in_range_s,passes", PASSES_TABLE)
def test_passes_per_ch_table(th, in_range_s, passes):
    lam, Rb, v = 5.0, 50.0, 20.0
    assert th / lam == pytest.approx(in_range_s, abs=0.1)
    assert M.passes_per_ch(th, lam, Rb, v) == pytest.approx(passes, abs=0.05)


def test_regime_A_needs_about_six_passes_at_default_point():
    """brief 3.2: Regime A requires flying over every cluster roughly six
    times -- which may be operationally infeasible."""
    th = M.theta_all_k(10, C_CONF, P_REF)
    assert M.passes_per_ch(th, 5.0, 50.0, 20.0) > 5.0


# ---- dimensional consistency: lambda is mandatory ------------------------
def test_dose_constraint_is_dimensionally_consistent():
    """theta is a COUNT of opportunities. lambda [1/s] times a time [s] gives a
    count; \\int p dt alone does not (brief 2.3, 13)."""
    lam, t_in_range = 5.0, 6.0
    delivered = lam * t_in_range * M.dose_kernel(P_REF) / M.dose_kernel(P_REF)
    assert delivered == pytest.approx(30.0)
    # and passes_per_ch must be inversely proportional to lambda
    th = 100.0
    assert M.passes_per_ch(th, 10.0, 50.0, 20.0) == pytest.approx(
        0.5 * M.passes_per_ch(th, 5.0, 50.0, 20.0))


# ---- vehicle: rho is derived, not asserted ------------------------------
@pytest.mark.parametrize("v,phi_deg,rho", [
    (15, 20, 63.0), (15, 30, 39.7), (15, 45, 22.9),
    (20, 20, 112.0), (20, 30, 70.6), (20, 45, 40.8),
    (25, 20, 175.0), (25, 30, 110.3), (25, 45, 63.7),
])
def test_turning_radius_table(v, phi_deg, rho):
    """rho = v^2/(g tan phi) -- brief 2.4 table."""
    g = 9.80665
    assert v ** 2 / (g * math.tan(math.radians(phi_deg))) == pytest.approx(rho, abs=0.2)


# ---- geometry: hex packing, and the 21% error in earlier drafts ----------
def test_hex_packing_vs_circle_packing_error():
    """brief E2: A/(pi R^2) is wrong by 21% relative to hexagonal packing."""
    A, R, hexc = 2.598076211e6, 100.0, 2.598076211
    C_hex = M.clusters_from_area(A, R, hexc)
    C_circ = A / (math.pi * R ** 2)
    assert C_hex == pytest.approx(100.0, rel=1e-9)
    # Hex cells of circumradius R have area 2.598 R^2 < pi R^2, so the correct
    # formula yields MORE clusters: C_hex / C_circ = pi / 2.598 = 1.209, i.e.
    # A/(pi R^2) UNDERCOUNTS by 20.9% -- the 21% of the brief's E2 note.
    assert C_hex / C_circ == pytest.approx(1.209, abs=0.002)
    assert (C_hex - C_circ) / C_hex == pytest.approx(0.173, abs=0.002)


def test_area_clusters_roundtrip():
    hexc = 2.598076211
    for R in (50.0, 100.0, 150.0):
        A = M.area_from_clusters(137.0, R, hexc)
        assert M.clusters_from_area(A, R, hexc) == pytest.approx(137.0, rel=1e-12)


# ---- r(k) / f(k) shape contracts ----------------------------------------
R_CASES = [("sat-exp", {"r_inf": 0.99, "k_r": 6.0}),
           ("logistic", {"r_inf": 0.99, "k0": 8.0, "s": 3.0}),
           ("hill", {"r_inf": 0.99, "k_r": 8.0, "a": 2.0})]
F_CASES = [("exp-decay", {"f0": 0.5, "k_f": 8.0}),
           ("power-law", {"f0": 0.5, "b": 1.2}),
           ("logistic-dec", {"f0": 0.5, "k0f": 12.0, "sf": 4.0})]


@pytest.mark.parametrize("fam,par", R_CASES)
def test_r_is_increasing_and_bounded(fam, par):
    vals = [M.r_of_k(k, fam, par) for k in range(2, 41)]
    assert all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))
    assert all(0.0 <= v <= par["r_inf"] + 1e-12 for v in vals)


@pytest.mark.parametrize("fam,par", F_CASES)
def test_f_is_decreasing_and_bounded(fam, par):
    vals = [M.f_of_k(k, fam, par) for k in range(2, 41)]
    assert all(b <= a + 1e-12 for a, b in zip(vals, vals[1:]))
    assert all(0.0 <= v <= 1.0 for v in vals)


def test_n_flagged_formula():
    assert M.n_flagged(0.9, 0.1, 100) == pytest.approx(0.9 + 0.1 * 99)


# ---- curve shape diagnostics --------------------------------------------
def test_curve_shape_detects_interior_minimum():
    ks = list(range(2, 11))
    vals = [(k - 6) ** 2 + 10 for k in ks]
    s = M.curve_shape(ks, vals, tol_rel=1e-9)
    assert s["k_star"] == 6 and s["interior"] and s["quasiconvex"]
    assert s["rel_depth"] > 0


def test_curve_shape_detects_boundary_minimum():
    ks = list(range(2, 11))
    s = M.curve_shape(ks, [float(k) for k in ks], tol_rel=1e-9)
    assert s["k_star"] == 2 and s["at_lower"] and not s["interior"]
    assert s["rel_depth"] == pytest.approx(0.0)


def test_curve_shape_rejects_bimodal():
    ks = list(range(2, 9))
    vals = [5.0, 1.0, 5.0, 1.0, 5.0, 1.0, 5.0]
    assert not M.curve_shape(ks, vals, tol_rel=1e-9)["quasiconvex"]


# ---- input validation ---------------------------------------------------
def test_rejects_bad_inputs():
    with pytest.raises(ValueError):
        M.theta_all_k(0, C_CONF, P_REF)
    with pytest.raises(ValueError):
        M.theta_m_of_k(10, 11, C_CONF, P_REF)
    with pytest.raises(ValueError):
        M.theta_all_k(10, 1.0, P_REF)
    with pytest.raises(ValueError):
        M.theta(10, regime="m-of-k", m=None, C_conf=C_CONF, p=P_REF)
    with pytest.raises(ValueError):
        M.theta(10, regime="bogus", m=3, C_conf=C_CONF, p=P_REF)


def test_m_for_policy():
    assert M.m_for_policy(10, m_policy="equal-k", m_fixed=None, m_frac=None) == 10
    assert M.m_for_policy(10, m_policy="fixed-3", m_fixed=3, m_frac=None) == 3
    assert M.m_for_policy(2, m_policy="fixed-3", m_fixed=3, m_frac=None) == 2  # capped at k
    assert M.m_for_policy(10, m_policy="proportional-50", m_fixed=None, m_frac=0.5) == 5
    assert M.m_for_policy(5, m_policy="proportional-50", m_fixed=None, m_frac=0.5) == 3


# ---- quasiconvexity violation magnitude, and the m=ceil(frac*k) sawtooth ----
def test_curve_shape_reports_violation_magnitude():
    ks = list(range(2, 9))
    vals = [10.0, 8.0, 6.0, 6.3, 6.0, 7.0, 8.0]   # one 4.8% dip after k*
    s = M.curve_shape(ks, vals, tol_rel=1e-9)
    assert not s["quasiconvex"]
    assert s["n_violations"] == 1
    assert s["max_violation_rel"] == pytest.approx(0.3 / 6.3, rel=1e-9)


def test_quasiconvex_curve_reports_zero_violations():
    ks = list(range(2, 11))
    s = M.curve_shape(ks, [(k - 6) ** 2 + 10 for k in ks], tol_rel=1e-9)
    assert s["quasiconvex"] and s["n_violations"] == 0
    assert s["max_violation_rel"] == 0.0


def test_proportional_m_policy_has_a_parity_sawtooth_in_theta():
    """MEASURED, not assumed. Under m = ceil(0.5k) the realised m/k ratio
    alternates with the parity of k, so theta zigzags: odd k costs more than
    the following even k. This is what breaks the strict quasiconvexity test
    for every proportional-50 curve in E0."""
    th = {}
    for k in range(3, 21):
        m = max(1, math.ceil(0.5 * k))
        th[k] = M.theta_m_of_k(k, m, C_CONF, P_REF)
    for k in range(3, 20, 2):          # odd k -> next even k is CHEAPER
        assert th[k + 1] < th[k], f"expected sawtooth drop at k={k}->{k+1}"
    for k in range(4, 19, 2):          # even k -> next odd k is dearer
        assert th[k + 1] > th[k]
    # the realised ratio m/k is what differs
    assert math.ceil(0.5 * 3) / 3 == pytest.approx(2 / 3)
    assert math.ceil(0.5 * 4) / 4 == pytest.approx(0.5)


def test_even_k_subsequence_removes_the_sawtooth():
    """On even k the m/k ratio is constant at 0.5, so theta is monotone."""
    vals = [M.theta_m_of_k(k, max(1, math.ceil(0.5 * k)), C_CONF, P_REF)
            for k in range(2, 41, 2)]
    for a, b in zip(vals, vals[1:]):
        assert b > a


def test_violation_metric_is_two_sided():
    """A bump BEFORE k* must be counted. Scanning only after k* would report
    zero violations whenever k* lands on the upper boundary."""
    ks = list(range(2, 9))
    vals = [10.0, 8.0, 9.0, 7.0, 5.0, 3.0, 1.0]   # rise at k=4, k* at the end
    s = M.curve_shape(ks, vals, tol_rel=1e-9)
    assert s["at_upper"] and not s["quasiconvex"]
    assert s["n_violations"] == 1
    assert s["max_violation_rel"] == pytest.approx(1.0 / 8.0)


def test_monotone_decreasing_to_upper_boundary_is_quasiconvex():
    ks = list(range(2, 9))
    s = M.curve_shape(ks, [10.0 - k for k in ks], tol_rel=1e-9)
    assert s["at_upper"] and s["quasiconvex"] and s["n_violations"] == 0


# ---- Appendix A.2 evidence model, and what it implies for m --------------
def test_fragment_evidence_matches_appendix_A2():
    """evidence_i = 1 - (1-0.90)^(pixelCount_i/totalPixels) -- matched exactly."""
    assert M.fragment_evidence(1.0) == pytest.approx(0.90)
    assert M.fragment_evidence(0.5) == pytest.approx(1 - 0.1 ** 0.5)
    assert M.fragment_evidence(1 / 28) == pytest.approx(1 - 0.1 ** (1 / 28))


def test_noisy_or_depends_only_on_m_over_k():
    for (m, k) in [(1, 2), (2, 4), (5, 10), (20, 40)]:
        assert M.noisy_or_confidence(m, k) == pytest.approx(
            M.noisy_or_confidence(1, 2), rel=1e-12)


def test_noisy_or_is_progressive_with_diminishing_returns():
    c = [M.noisy_or_confidence(m, 10) for m in range(1, 11)]
    assert all(b > a for a, b in zip(c, c[1:]))                 # progressive
    gains = [b - a for a, b in zip(c, c[1:])]
    assert all(b < a for a, b in zip(gains, gains[1:]))         # diminishing
    assert c[-1] == pytest.approx(0.90)


def test_m_over_k_inverts_the_noisy_or():
    for thr in (0.3, 0.5, 0.684, 0.75, 0.85):
        a = M.m_over_k_from_suspicion_threshold(thr)
        assert M.noisy_or_confidence(round(a * 1000), 1000) == pytest.approx(thr, abs=2e-3)


@pytest.mark.parametrize("thr,alpha", [
    (0.50, 0.301), (0.684, 0.500), (0.75, 0.602), (0.90, 1.000),
])
def test_alpha_from_threshold_table(thr, alpha):
    """alpha = log10(1/(1-thr)) when base = 0.90. thr = base gives alpha = 1,
    i.e. the regime collapses to all-k."""
    assert M.m_over_k_from_suspicion_threshold(thr) == pytest.approx(alpha, abs=1e-3)


def test_threshold_at_or_above_base_is_unreachable_from_a_subset():
    assert M.m_over_k_from_suspicion_threshold(0.90) == pytest.approx(1.0)
    assert M.m_over_k_from_suspicion_threshold(0.95) > 1.0


# ---- continuous-m relaxation (diagnostic) --------------------------------
@pytest.mark.parametrize("k,m", [(10, 7), (10, 5), (10, 3), (10, 2), (4, 2),
                                 (16, 8), (40, 20), (6, 3), (25, 4)])
def test_continuous_m_agrees_with_exact_binomial_at_integer_m(k, m):
    """I_q(m, k-m+1) == P(Bin(k,q) >= m) exactly at integer m, so the relaxed
    theta must reproduce the exact one."""
    assert M.theta_m_of_k_continuous(k, float(m), C_CONF, P_REF) == pytest.approx(
        M.theta_m_of_k(k, m, C_CONF, P_REF), rel=1e-6)


def test_continuous_m_is_monotone_in_m():
    vals = [M.theta_m_of_k_continuous(20, mm / 10, C_CONF, P_REF)
            for mm in range(10, 201, 7)]
    for a, b in zip(vals, vals[1:]):
        assert b > a


def test_continuous_relaxation_removes_the_sawtooth_at_fixed_alpha():
    """With m = alpha*k exactly (no ceiling), theta is smooth and monotone in k
    for every alpha -- not just alpha = 0.5. This is what isolates the
    integrality artifact from the shape of the objective."""
    for alpha in (0.155, 0.222, 0.301, 0.398, 0.5, 0.602, 0.699):
        vals = [M.theta_m_of_k_continuous(k, alpha * k, C_CONF, P_REF)
                for k in range(4, 41)]
        for a, b in zip(vals, vals[1:]):
            assert b > a, f"not monotone at alpha={alpha}"


def test_integer_ceiling_policy_does_oscillate_where_continuous_does_not():
    """The contrast, measured: same alpha, ceiling vs continuous."""
    alpha = 0.301
    ceil_vals = [M.theta_m_of_k(k, max(1, math.ceil(alpha * k)), C_CONF, P_REF)
                 for k in range(4, 41)]
    cont_vals = [M.theta_m_of_k_continuous(k, alpha * k, C_CONF, P_REF)
                 for k in range(4, 41)]
    assert any(b < a for a, b in zip(ceil_vals, ceil_vals[1:]))      # oscillates
    assert all(b > a for a, b in zip(cont_vals, cont_vals[1:]))      # does not
