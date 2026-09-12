#!/usr/bin/env python3.10
"""Statistics helpers. AGENT-BRIEF 8 and A.4.

  Wilson intervals for rates
  bootstrap (10,000 resamples) for medians and quantiles
  paired win counts, Cliff's delta, and a paired permutation p-value

`campaign_stats.py --selftest` validates every routine against instances with
known answers, as the brief requires.
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass

DEFAULT_RESAMPLES = 10_000


@dataclass(frozen=True)
class CI:
    point: float
    lo: float
    hi: float

    def __str__(self) -> str:
        return f"{self.point:.4g} [{self.lo:.4g}, {self.hi:.4g}]"


def wilson(successes: int, n: int, z: float = 1.959963985) -> CI:
    """Wilson score interval for a binomial rate."""
    if n <= 0:
        return CI(float("nan"), float("nan"), float("nan"))
    p = successes / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return CI(p, max(0.0, centre - half), min(1.0, centre + half))


def bootstrap_ci(xs: list[float], stat=None, *, resamples: int = DEFAULT_RESAMPLES,
                 alpha: float = 0.05, seed: int = 20260912) -> CI:
    """Percentile bootstrap CI. stat defaults to the median."""
    if stat is None:
        stat = median
    xs = [float(x) for x in xs]
    if not xs:
        return CI(float("nan"), float("nan"), float("nan"))
    if len(xs) == 1:
        return CI(xs[0], xs[0], xs[0])
    rng = random.Random(seed)
    n = len(xs)
    reps = []
    for _ in range(resamples):
        reps.append(stat([xs[rng.randrange(n)] for _ in range(n)]))
    reps.sort()
    lo = reps[int(math.floor(alpha / 2 * resamples))]
    hi = reps[min(resamples - 1, int(math.ceil((1 - alpha / 2) * resamples)) - 1)]
    return CI(stat(xs), lo, hi)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def median(xs: list[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return float("nan")
    m = n // 2
    return s[m] if n % 2 else 0.5 * (s[m - 1] + s[m])


def quantile(xs: list[float], q: float) -> float:
    """Linear-interpolation quantile (type 7, as in numpy's default)."""
    s = sorted(xs)
    if not s:
        return float("nan")
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(len(s) - 1, lo + 1)
    return s[lo] + (pos - lo) * (s[hi] - s[lo])


def mean_ci_t(xs: list[float], z: float = 1.959963985) -> CI:
    """Normal-approximation CI on the mean."""
    n = len(xs)
    if n == 0:
        return CI(float("nan"), float("nan"), float("nan"))
    if n == 1:
        return CI(xs[0], xs[0], xs[0])
    m = mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    half = z * math.sqrt(var / n)
    return CI(m, m - half, m + half)


def cliffs_delta(a: list[float], b: list[float]) -> float:
    """Cliff's delta in [-1, 1]: P(a>b) - P(a<b). 0 means no dominance."""
    if not a or not b:
        return float("nan")
    gt = lt = 0
    sb = sorted(b)
    n = len(sb)
    import bisect
    for x in a:
        lt += bisect.bisect_left(sb, x)      # b strictly below x
        gt += n - bisect.bisect_right(sb, x)  # b strictly above x
    return (lt - gt) / (len(a) * n)


def paired_wins(a: list[float], b: list[float], *, lower_is_better: bool = True
                ) -> tuple[int, int, int]:
    """(a wins, b wins, ties) over identical-index pairs."""
    if len(a) != len(b):
        raise ValueError("paired comparison needs equal lengths")
    aw = bw = tie = 0
    for x, y in zip(a, b):
        if x == y:
            tie += 1
        elif (x < y) == lower_is_better:
            aw += 1
        else:
            bw += 1
    return aw, bw, tie


def paired_permutation_p(a: list[float], b: list[float], *, resamples: int = DEFAULT_RESAMPLES,
                         seed: int = 20260912) -> float:
    """Two-sided paired permutation test on the mean difference (sign flips)."""
    if len(a) != len(b):
        raise ValueError("paired test needs equal lengths")
    d = [x - y for x, y in zip(a, b)]
    obs = abs(mean(d))
    rng = random.Random(seed)
    count = 0
    for _ in range(resamples):
        s = mean([x if rng.random() < 0.5 else -x for x in d])
        if abs(s) >= obs - 1e-15:
            count += 1
    return (count + 1) / (resamples + 1)


def loglog_slope(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """OLS fit of log y = a + b log x. Returns (exponent b, intercept a, R^2).

    This is how the exponent of T_hop in R is measured -- not assumed.
    """
    pts = [(math.log(x), math.log(y)) for x, y in zip(xs, ys) if x > 0 and y > 0]
    if len(pts) < 2:
        return (float("nan"),) * 3
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    if sxx == 0:
        return (float("nan"),) * 3
    b = sxy / sxx
    a = my - b * mx
    sst = sum((p[1] - my) ** 2 for p in pts)
    ssr = sum((p[1] - (a + b * p[0])) ** 2 for p in pts)
    r2 = 1.0 - ssr / sst if sst > 0 else float("nan")
    return b, a, r2


def ols_linear(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """OLS fit y = a + b x. Returns (intercept a, slope b, R^2)."""
    n = len(xs)
    if n < 2:
        return (float("nan"),) * 3
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return (float("nan"),) * 3
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    sst = sum((y - my) ** 2 for y in ys)
    ssr = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    return a, b, (1.0 - ssr / sst if sst > 0 else float("nan"))


def bootstrap_linear_ci(xs: list[float], ys: list[float], *, resamples: int = 2000,
                        alpha: float = 0.05, seed: int = 20260912
                        ) -> tuple[CI, CI, float]:
    """CIs on the intercept and slope of y = a + b x, by resampling pairs.

    Used to separate the fixed protocol startup latency (a) from the marginal
    per-hop cost (b) in T_spread = a + b * h_max. The ratio T_spread/h_max
    conflates the two and inflates as h_max -> 0.
    """
    pts = list(zip(xs, ys))
    a0, b0, r2 = ols_linear(xs, ys)
    if len(pts) < 3:
        return CI(a0, float("nan"), float("nan")), CI(b0, float("nan"), float("nan")), r2
    rng = random.Random(seed)
    A, B = [], []
    for _ in range(resamples):
        s = [pts[rng.randrange(len(pts))] for _ in range(len(pts))]
        a, b, _ = ols_linear([q[0] for q in s], [q[1] for q in s])
        if not (math.isnan(a) or math.isnan(b)):
            A.append(a); B.append(b)
    A.sort(); B.sort()
    lo_i = int(math.floor(alpha / 2 * len(A)))
    hi_i = min(len(A) - 1, int(math.ceil((1 - alpha / 2) * len(A))) - 1)
    return (CI(a0, A[lo_i], A[hi_i]), CI(b0, B[lo_i], B[hi_i]), r2)


def bootstrap_slope_ci(xs: list[float], ys: list[float], *,
                       resamples: int = 2000, alpha: float = 0.05,
                       seed: int = 20260912) -> CI:
    """CI on the log-log slope by resampling (x, y) pairs."""
    pts = [(x, y) for x, y in zip(xs, ys) if x > 0 and y > 0]
    if len(pts) < 3:
        b = loglog_slope(xs, ys)[0]
        return CI(b, float("nan"), float("nan"))
    rng = random.Random(seed)
    reps = []
    for _ in range(resamples):
        s = [pts[rng.randrange(len(pts))] for _ in range(len(pts))]
        b = loglog_slope([p[0] for p in s], [p[1] for p in s])[0]
        if not math.isnan(b):
            reps.append(b)
    reps.sort()
    lo = reps[int(math.floor(alpha / 2 * len(reps)))]
    hi = reps[min(len(reps) - 1, int(math.ceil((1 - alpha / 2) * len(reps))) - 1)]
    return CI(loglog_slope([p[0] for p in pts], [p[1] for p in pts])[0], lo, hi)


# ----------------------------------------------------------------- selftest
def _selftest() -> int:
    fails = []

    def check(name, cond, detail=""):
        if not cond:
            fails.append(f"{name}: {detail}")

    # Wilson against the published worked example: 0.05 level, x=2, n=10
    w = wilson(2, 10)
    check("wilson point", abs(w.point - 0.2) < 1e-12)
    check("wilson bounds", abs(w.lo - 0.05668) < 1e-4 and abs(w.hi - 0.50979) < 1e-4,
          f"{w.lo:.5f},{w.hi:.5f}")
    # a rate of 0 and 1 must stay inside [0,1]
    check("wilson 0", wilson(0, 20).lo == 0.0)
    check("wilson 1", wilson(20, 20).hi == 1.0)

    # median / quantile against hand-computed values
    check("median odd", median([3, 1, 2]) == 2)
    check("median even", median([4, 1, 2, 3]) == 2.5)
    check("q50 == median", abs(quantile([1, 2, 3, 4], 0.5) - 2.5) < 1e-12)
    check("q0", quantile([5, 1, 3], 0.0) == 1)
    check("q100", quantile([5, 1, 3], 1.0) == 5)

    # bootstrap: CI of a constant sample is degenerate; CI must cover the median
    c = bootstrap_ci([7.0] * 30, resamples=500)
    check("bootstrap constant", c.lo == c.hi == 7.0)
    xs = [float(i) for i in range(1, 101)]
    c = bootstrap_ci(xs, resamples=2000)
    check("bootstrap covers median", c.lo <= median(xs) <= c.hi, str(c))

    # mean CI on a known sample: mean 3, sd 1.5811 (n=5) -> half width 1.386
    m = mean_ci_t([1, 2, 3, 4, 5])
    check("mean point", abs(m.point - 3) < 1e-12)
    check("mean CI half", abs((m.hi - m.lo) / 2 - 1.3859) < 1e-3, f"{(m.hi-m.lo)/2:.4f}")

    # Cliff's delta: total dominance is +-1, identical samples 0
    check("cliff +1", abs(cliffs_delta([5, 6, 7], [1, 2, 3]) - 1.0) < 1e-12)
    check("cliff -1", abs(cliffs_delta([1, 2, 3], [5, 6, 7]) + 1.0) < 1e-12)
    check("cliff 0", abs(cliffs_delta([1, 2, 3], [1, 2, 3])) < 1e-12)
    # half-overlap case, computed by hand: a=[1,3], b=[2,4] -> pairs
    # (1<2),(1<4),(3>2),(3<4) -> lt=1, gt=3 -> delta=(1-3)/4=-0.5
    check("cliff hand", abs(cliffs_delta([1, 3], [2, 4]) + 0.5) < 1e-12,
          str(cliffs_delta([1, 3], [2, 4])))

    # paired wins
    aw, bw, tie = paired_wins([1, 5, 3], [2, 4, 3])
    check("paired wins", (aw, bw, tie) == (1, 1, 1), f"{aw},{bw},{tie}")

    # permutation test: identical samples -> p near 1; separated -> p small
    p_same = paired_permutation_p([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], resamples=500)
    check("perm identical", p_same > 0.9, f"{p_same}")
    p_diff = paired_permutation_p([10] * 12, [1] * 12, resamples=2000)
    check("perm separated", p_diff < 0.01, f"{p_diff}")

    # log-log slope on an exact power law y = 3 x^2
    xs = [1.0, 2.0, 4.0, 8.0, 16.0]
    ys = [3 * x ** 2 for x in xs]
    b, a, r2 = loglog_slope(xs, ys)
    check("slope exact", abs(b - 2.0) < 1e-9, f"{b}")
    check("intercept exact", abs(math.exp(a) - 3.0) < 1e-9, f"{math.exp(a)}")
    check("r2 exact", abs(r2 - 1.0) < 1e-12, f"{r2}")
    # a flat relationship must give exponent 0
    b0 = loglog_slope([1, 2, 4, 8], [5, 5, 5, 5])[0]
    check("slope flat", abs(b0) < 1e-12, f"{b0}")
    # linear fit on an exact line y = 4 + 3x
    a, b, r2 = ols_linear([1.0, 2.0, 3.0, 4.0], [7.0, 10.0, 13.0, 16.0])
    check("linear exact a", abs(a - 4.0) < 1e-9, f"{a}")
    check("linear exact b", abs(b - 3.0) < 1e-9, f"{b}")
    check("linear exact r2", abs(r2 - 1.0) < 1e-12, f"{r2}")
    ca, cb, _ = bootstrap_linear_ci([1.0, 2.0, 3.0, 4.0, 5.0],
                                    [7.0, 10.0, 13.0, 16.0, 19.0], resamples=300)
    check("linear CI degenerate", abs(cb.point - 3.0) < 1e-9 and cb.lo <= 3.0 <= cb.hi,
          str(cb))
    # a flat line must give slope 0 and intercept = the level
    a0, b0, _ = ols_linear([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])
    check("linear flat", abs(b0) < 1e-12 and abs(a0 - 5.0) < 1e-12, f"{a0},{b0}")

    # slope CI must bracket the truth on a noisy power law
    rng = random.Random(1)
    xs2 = [float(x) for x in range(2, 40)]
    ys2 = [2.0 * x ** 1.5 * rng.uniform(0.9, 1.1) for x in xs2]
    ci = bootstrap_slope_ci(xs2, ys2, resamples=400)
    check("slope CI brackets", ci.lo <= 1.5 <= ci.hi, str(ci))

    if fails:
        print("SELFTEST FAILED")
        for f in fails:
            print("  -", f)
        return 1
    print("campaign_stats selftest: all checks passed")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    sys.exit(0)
