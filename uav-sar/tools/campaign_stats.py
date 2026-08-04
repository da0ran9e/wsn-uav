#!/usr/bin/env python3
"""Publication-grade campaign: point estimates WITH uncertainty.

Reports, for each scheme: success rates with Wilson 95% CIs, median / IQR / p90
for every distribution with bootstrap 95% CIs on the median, and -- because the
design is matched-pairs (one seed == one channel realisation, replayed for every
scheme) -- a paired Wilcoxon signed-rank test with Cliff's delta as the primary
inference, with the unpaired Mann-Whitney U retained alongside it.

Deliberately dependency-free (no numpy/scipy) so a reviewer can rerun it
anywhere.

Audit findings fixed in this file:
  S10  p-value underflowed to exactly 0.0 above |z| ~ 8.29 (catastrophic
       cancellation in 2*(1-Phi(|z|))); now math.erfc, good to ~1e-300.
  S11  an unpaired test was applied to a paired design; Wilcoxon signed-rank,
       Cliff's delta, median paired difference and per-arm win counts added.
  S9   the victim position was reconstructed with a hard-coded 20 m spacing.
  S15  p90 was computed with a floored index.
  S2   the censoring horizon (--simTime) differed per scheme under one metric
       name; it is now printed, with the count of runs censored by it.

  B3   the localization output was only ever observed inside the simulator
       (the `deliver_start` position).  metrics.csv now also carries the fix
       the BS actually DECODED from a REPORT packet, and it is reported as a
       separate metric -- see `fixerr` below.

Usage:  campaign_stats.py <outdir> <N seeds> [--quick] [--grid=N]
"""
import csv, math, os, random, subprocess, sys, statistics as st

from campaign_common import victim_pos, p90, iqr, assert_one_build

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
random.seed(12345)  # bootstrap determinism

# scheme -> extra CLI args + sim-time budget (generous: must not truncate a run)
SCHEMES = {
    "proposed":   (["--numUav=4"], 300),
    "nocoop":     (["--numUav=4"], 400),
    "pure-uav":   ([], 700),
    "tsp-mc-x4":  (["--scheme=tsp-mc", "--numUav=4"], 600),
    "tsp-mc-x1":  (["--scheme=tsp-mc", "--numUav=1"], 900),
}

# S2/reporting: a run whose victim was never served is INCLUDED in the rate
# columns and EXCLUDED from every distribution.  Stated in the output header.
INCLUSION = "victim served (timeToCompleteData_s >= 0)"


def wilson(k, n, z=1.96):
    """Wilson score interval for a proportion -- correct at extremes (0%,100%)."""
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * p, 100 * max(0.0, c - h), 100 * min(1.0, c + h)


def boot_median_ci(xs, iters=5000, alpha=0.05):
    """Percentile bootstrap CI for the median."""
    if len(xs) < 2:
        return (st.median(xs) if xs else float("nan"),) * 3
    n, meds = len(xs), []
    for _ in range(iters):
        meds.append(st.median([xs[random.randrange(n)] for _ in range(n)]))
    meds.sort()
    lo = meds[int(alpha / 2 * iters)]
    hi = meds[min(iters - 1, int((1 - alpha / 2) * iters))]
    return st.median(xs), lo, hi


def _norm_sf2(z):
    """Two-sided tail probability of the standard normal, P(|Z| > |z|).

    S10: the previous form, 2*(1 - 0.5*(1+erf(|z|/sqrt2))), subtracts a number
    within 1e-16 of 1 from 1, so it hits the double-precision floor and returns
    EXACTLY 0.0 for |z| > 8.29 -- which is how the study came to report
    "p < 1e-16" for a z of 12.20 whose true p is 3.1e-34.  erfc is the same
    quantity evaluated without the cancellation and stays accurate to ~1e-300.
    """
    return math.erfc(abs(z) / math.sqrt(2.0))


def _avg_ranks(vals):
    """Mid-ranks of `vals` (list of comparable keys) plus sum(t^3-t) over ties.

    Returns (ranks_in_input_order, tie_term).
    """
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    tie_term = 0.0
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        t = j - i + 1
        if t > 1:
            tie_term += t ** 3 - t
        i = j + 1
    return ranks, tie_term


def mannwhitney_u(a, b):
    """Two-sided Mann-Whitney U, normal approximation with tie correction.

    Returns (U, z, p).  Unpaired: retained for continuity with the published
    numbers, but see wilcoxon_signed_rank -- this design is paired (S11).
    """
    if not a or not b:
        return float("nan"), float("nan"), float("nan")
    combined = [(v, 0) for v in a] + [(v, 1) for v in b]
    ranks, tie_term = _avg_ranks([v for v, _ in combined])
    r1 = sum(r for r, (_, g) in zip(ranks, combined) if g == 0)
    n1, n2 = len(a), len(b)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sd = math.sqrt(max(1e-12, (n1 * n2 / 12.0) *
                       ((n1 + n2 + 1) - tie_term / ((n1 + n2) * (n1 + n2 - 1)))))
    z = (u1 - mu) / sd
    return u1, z, _norm_sf2(z)


def wilcoxon_signed_rank(pairs):
    """Two-sided Wilcoxon signed-rank test on matched pairs (S11).

    `pairs` is a list of (a_i, b_i).  Zero differences are discarded (Wilcoxon's
    original treatment) and n is reduced accordingly; |differences| are ranked
    with mid-ranks for ties; the normal approximation uses the tie-corrected
    variance and NO continuity correction (matching scipy's default
    `correction=False`).  p comes from erfc, so it does not underflow (S10).

    Returns dict(n, n_zero, w_plus, w_minus, z, p).

    VALIDATION (hand-computed, reproduced by the self-test at the bottom of
    this file -- run `python3 campaign_stats.py --selftest`):

      (a) no ties, d = [+1, +2, -3, +4, +5]
          ranks of |d| = 1,2,3,4,5 ; W+ = 1+2+4+5 = 12 ; W- = 3 ; n = 5
          mu = n(n+1)/4 = 7.5 ; var = n(n+1)(2n+1)/24 = 5*6*11/24 = 13.75
          z = (12 - 7.5)/sqrt(13.75) = +1.213560 ; p = erfc(z/sqrt2) = 0.2249159

      (b) with ties, d = [+1, -1, +2, -2, +3]
          |d| = 1,1,2,2,3 -> mid-ranks 1.5,1.5,3.5,3.5,5
          W+ = 1.5+3.5+5 = 10 ; W- = 1.5+3.5 = 5 ; n = 5
          tie correction = sum(t^3-t)/48 = (6+6)/48 = 0.25
          var = 13.75 - 0.25 = 13.5 ; z = (10-7.5)/sqrt(13.5) = +0.680414
          p = 0.4962425

      (c) zero handling, d = [0, +1, +2, +3]
          the zero is dropped, n = 3 ; W+ = 6 ; mu = 3 ; var = 3*4*7/24 = 3.5
          z = 3/sqrt(3.5) = +1.603567 ; p = 0.1088094
    """
    diffs = [a - b for a, b in pairs]
    n_zero = sum(1 for d in diffs if d == 0)
    nz = [d for d in diffs if d != 0]
    n = len(nz)
    if n == 0:
        return dict(n=0, n_zero=n_zero, w_plus=float("nan"),
                    w_minus=float("nan"), z=float("nan"), p=float("nan"))
    ranks, tie_term = _avg_ranks([abs(d) for d in nz])
    w_plus = sum(r for r, d in zip(ranks, nz) if d > 0)
    w_minus = sum(r for r, d in zip(ranks, nz) if d < 0)
    mu = n * (n + 1) / 4.0
    var = n * (n + 1) * (2 * n + 1) / 24.0 - tie_term / 48.0
    if var <= 0:
        return dict(n=n, n_zero=n_zero, w_plus=w_plus, w_minus=w_minus,
                    z=float("nan"), p=float("nan"))
    z = (w_plus - mu) / math.sqrt(var)
    return dict(n=n, n_zero=n_zero, w_plus=w_plus, w_minus=w_minus,
                z=z, p=_norm_sf2(z))


def cliffs_delta(a, b):
    """Cliff's delta effect size (S11): (#{a>b} - #{a<b}) / (|a|*|b|).

    Returns (delta, label).  Sign convention: delta > 0 means values in `a`
    tend to be LARGER than values in `b`.  Thresholds are Romano et al. (2006),
    the conventional mapping of Cohen's d cut-offs onto delta.

    VALIDATION (hand-computed):
      a=[1,2,3], b=[2,3,4] -> 9 pairs: a>b once (3,2); a<b six times
                              (1,2)(1,3)(1,4)(2,3)(2,4)(3,4); 2 ties (2,2)(3,3)
                              delta = (1-6)/9 = -0.5556 -> |d|>0.474 -> "large"
      a=[1,2,3], b=[1,2,3] -> delta = 0.0 -> "negligible"
      a=[4,5,6], b=[1,2,3] -> delta = +1.0 -> "large"
    """
    if not a or not b:
        return float("nan"), "n/a"
    gt = lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    d = (gt - lt) / float(len(a) * len(b))
    m = abs(d)
    label = ("negligible" if m < 0.147 else "small" if m < 0.33
             else "medium" if m < 0.474 else "large")
    return d, label


def fmt_p(p):
    """Print the real p-value.  S10: the old '<1e-16' floor hid a true 3.1e-34."""
    if p != p:
        return "n/a"
    return "%.3g" % p


def stars(p):
    if p != p:
        return "n/a"
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."


def run_scheme(tag, outdir, n_seeds):
    args, simtime = SCHEMES[tag]
    scheme = "tsp-mc" if tag.startswith("tsp-mc") else tag
    rows = []
    for seed in range(1, n_seeds + 1):
        out = os.path.join(outdir, f"{tag}-{seed}")
        cmd = [BIN, f"--seed={seed}", f"--simTime={simtime}", f"--outputDir={out}"]
        if not any(a.startswith("--scheme") for a in args):
            cmd.append(f"--scheme={scheme}")
        cmd += args
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            m = list(csv.DictReader(open(os.path.join(out, "metrics.csv"))))[0]
        except Exception:
            continue
        # S9: resolve the victim from the data, not from a hard-coded spacing.
        vx, vy = victim_pos(m)
        derr = None
        try:
            for e in csv.DictReader(open(os.path.join(out, "events.csv"))):
                if e["event"] == "deliver_start":
                    # DELIVERY error: where the data actually got put, vs the
                    # victim.  This is the localization metric.  The retracted
                    # summon_start metric (S8) is deliberately not computed here.
                    derr = math.hypot(float(e["x"]) - vx, float(e["y"]) - vy)
                    break
        except Exception:
            pass
        rows.append(dict(seed=seed,
                         rep=float(m["timeToReportAtBS_s"]),
                         cmp=float(m["timeToCompleteData_s"]),
                         loc=float(m["timeToLocalize_s"]),
                         derr=derr,
                         # B3: error of the fix the BS decoded off the radio.
                         # -1 when no UAV ever delivered a position, which is
                         # the correct and permanent outcome for every
                         # blind-coverage baseline -- their cell reads n/a.
                         fixerr=float(m.get("reportErr_m", -1) or -1),
                         tfix=float(m.get("timeToFixAtBS_s", -1) or -1),
                         energy=float(m["uavEnergyJ"]),
                         pkts=float(m["pktSent"])))
    return rows


# audit A2: gating the COST metrics on victim-served was survivorship bias.
# t_report / energy / packets are defined whenever the MISSION completes, which
# is a different and much more frequent event, so dropping runs for a
# victim-delivery failure drops them for a reason unrelated to the metric -- and
# the dropped runs are systematically the awkward ones. Measured at N=120, every
# such delta favoured the proposed scheme (0.4-2.8%). These are now reported
# intention-to-treat. The victim-served gate survives only where the metric
# genuinely does not exist otherwise.
ITT_KEYS = {"rep", "energy", "pkts", "tfix", "fixerr", "loc"}
GATED_KEYS = {"cmp", "derr"}


def included(rows):
    """Runs that reached the victim -- the gate for victim-dependent metrics."""
    return [r for r in rows if r["cmp"] >= 0]


def series(rows, key):
    """Defined values of `key`, intention-to-treat unless the metric needs the gate."""
    src = included(rows) if key in GATED_KEYS else rows
    out = []
    for r in src:
        v = r[key]
        if v is not None and v >= 0:
            out.append(v)
    return out


def main():
    outdir, n = sys.argv[1], int(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    # W8: the scaling claim needs the same campaign at two densities, so the
    # grid is a parameter of the campaign rather than a rebuild.
    # M9/W3/W7: pass realism knobs through to EVERY arm, so the comparison can be
    # made at a common operating point instead of the proposed scheme alone being
    # re-measured under noise. (The blind-coverage arms ignore the clue field, so
    # only --victimOnNode can move them -- which is exactly why it must be set
    # identically for all of them rather than assumed away.)
    passthrough = [a for a in sys.argv[3:]
                   if a.startswith(("--senseSigma=", "--gpsSigma=", "--victimOnNode="))]
    if passthrough:
        for tag in list(SCHEMES):
            args, t = SCHEMES[tag]
            SCHEMES[tag] = (args + passthrough, t)
    for a in sys.argv[3:]:
        if a.startswith("--grid="):
            g = int(a.split("=", 1)[1])
            # S2: the horizon must grow with the area or the slow arms get
            # censored and their "failures" would be a truncation artifact.
            scale = max(1.0, (g / 8.0) ** 2)
            for tag in list(SCHEMES):
                args, t = SCHEMES[tag]
                SCHEMES[tag] = (args + [f"--gridSize={g}"], int(t * scale))
    tags = list(SCHEMES) if "--quick" not in sys.argv else ["proposed", "tsp-mc-x4"]
    data = {}
    for tag in tags:
        data[tag] = run_scheme(tag, outdir, n)
        # Refuse to aggregate a campaign that spans binaries (audit meta-finding).
        assert_one_build([os.path.join(outdir, f"{tag}-{s_}")
                          for s_ in range(1, n + 1)], label=f"scheme '{tag}'")
        print(f"  [{tag}] {len(data[tag])} runs collected", file=sys.stderr)

    print(f"\n### Campaign with 95% confidence intervals (N={n} seeds/scheme) ###")
    print(f"""
INCLUSION RULE (one rule, applied to EVERY distribution in this report --
latency, energy, packets and delivery error alike; energy and packets used to
include failed runs while latencies excluded them, which made the columns
mutually incomparable):
  cost metrics (t_report, energy, packets, t_fix, fix error) are reported
  INTENTION-TO-TREAT over every run -- they are defined whenever the MISSION
  completes, so gating them on {INCLUSION} would drop runs for an unrelated
  reason and, measured, always in the proposed scheme's favour (audit A2).
  Only victim-dependent metrics (t_victim, delivery error) keep that gate.
  Rates are over ALL runs.  Within the included set a metric that is still -1
  means the stage does not exist for that scheme (see M1) -- its cell reads
  n/a and the per-cell n shows how many runs contributed.
Delivery error = || deliver_start position - victim position ||.  The
summon_start metric is RETRACTED (S8) and is not computed anywhere here.""")

    # S2: horizons differed per scheme under one metric name; make them visible.
    print("\n### Censoring horizon per scheme (S2) ###")
    print(f"{'scheme':<11} {'--simTime':>9} {'runs':>5} {'victim censored':>16} "
          f"{'max t_victim':>13} {'max t_report':>13}")
    print("-" * 74)
    for tag in tags:
        R = data[tag]
        cens = sum(1 for r in R if r["cmp"] < 0)
        mc = max([r["cmp"] for r in R if r["cmp"] >= 0], default=float("nan"))
        mr = max([r["rep"] for r in R if r["rep"] >= 0], default=float("nan"))
        print(f"{tag:<11} {SCHEMES[tag][1]:>9} {len(R):>5} "
              f"{cens:>7} ({100.0*cens/max(1,len(R)):>4.0f}%) "
              f"{mc:>13.1f} {mr:>13.1f}")
    print("  A censored run is indistinguishable from a failed run in metrics.csv;"
          "\n  if 'max' is close to '--simTime' the rate above is a truncation"
          " artifact, not a failure rate.")

    print("\n### Success rates over ALL runs (Wilson 95% CI) ###")
    print(f"{'scheme':<11} {'mission ok (report@BS)':<28} {'victim served':<28}")
    print("-" * 68)
    for tag in tags:
        R = data[tag]
        p1, l1, h1 = wilson(sum(1 for r in R if r["rep"] >= 0), len(R))
        p2, l2, h2 = wilson(sum(1 for r in R if r["cmp"] >= 0), len(R))
        print(f"{tag:<11} {p1:5.1f}% [{l1:5.1f},{h1:5.1f}]{'':<9} "
              f"{p2:5.1f}% [{l2:5.1f},{h2:5.1f}]")

    print(f"\n### Distributions over included runs ({INCLUSION}) ###")
    print(f"{'scheme':<11} {'metric':<16} {'median [95% CI]':<27} "
          f"{'IQR p25-p75 (width)':<26} {'p90':>9} {'n':>4}")
    print("-" * 96)
    METRICS = [("rep", "t_report s", 1.0), ("cmp", "t_victim s", 1.0),
               ("loc", "t_localize s", 1.0), ("energy", "energy kJ", 1e-3),
               ("pkts", "packets", 1.0), ("derr", "delivery err m", 1.0),
               ("tfix", "t_fix@BS s", 1.0), ("fixerr", "BS fix err m", 1.0)]
    for tag in tags:
        for key, lbl, scale in METRICS:
            xs = [v * scale for v in series(data[tag], key)]
            if not xs:
                print(f"{tag:<11} {lbl:<16} {'n/a (stage absent for this scheme)':<27}"
                      f" {'':<26} {'':>9} {0:>4}")
                continue
            m, lo, hi = boot_median_ci(xs)
            q1, q3, w = iqr(xs)
            print(f"{tag:<11} {lbl:<16} "
                  f"{m:8.1f} [{lo:7.1f},{hi:8.1f}]{'':<3} "
                  f"{q1:8.1f}-{q3:<8.1f} ({w:6.1f}){'':<1} "
                  f"{p90(xs):9.1f} {len(xs):>4}")
        print()

    if "proposed" not in data:
        return

    # ---- S11: paired inference is PRIMARY -------------------------------
    print("### PRIMARY: paired tests vs proposed ###")
    print("  Design is matched-pairs: seed k gives the same channel realisation")
    print("  to every scheme, so a paired test is the correct one.  Pairs where")
    print("  either arm has no value are dropped (count reported).")
    print("  Reported for all three cost metrics -- a scheme that is faster only")
    print("  by spending more energy or airtime has not actually won.")
    base_vals = [r["rep"] for r in data["proposed"] if r["rep"] >= 0]
    for key, lbl, scale, unit in [("rep", "mission time", 1.0, "s"),
                                  ("energy", "UAV energy", 1e-3, "kJ"),
                                  ("pkts", "app packets", 1.0, "")]:
        print(f"\n-- {lbl} --")
        print(f"{'comparison':<24} {'pairs':>6} {'W+':>9} {'z':>8} {'p':>11} {'sig':<5} "
              f"{'median diff':>12} {'wins P/other':>13} {'Cliff d':>9} {'':<11}")
        print("-" * 118)
        base_rows = included(data["proposed"]) if key in GATED_KEYS else data["proposed"]
        base_by_seed = {r["seed"]: r[key] * scale for r in base_rows if r[key] >= 0}
        for tag in tags:
            if tag == "proposed":
                continue
            other_rows = included(data[tag]) if key in GATED_KEYS else data[tag]
            other_by_seed = {r["seed"]: r[key] * scale for r in other_rows if r[key] >= 0}
            if not other_by_seed:
                print(f"{'proposed vs ' + tag:<24} n/a - stage absent by design "
                      f"(M1: metric is 0%-by-construction for this arm)")
                continue
            seeds = sorted(set(base_by_seed) & set(other_by_seed))
            pairs = [(base_by_seed[s], other_by_seed[s]) for s in seeds]
            if not pairs:
                print(f"{'proposed vs ' + tag:<24} n/a - no seed produced a value in both arms")
                continue
            w = wilcoxon_signed_rank(pairs)
            diffs = [a - b for a, b in pairs]
            n_prop = sum(1 for d in diffs if d < 0)   # proposed cheaper/faster
            n_oth = sum(1 for d in diffs if d > 0)
            d, lab = cliffs_delta([a for a, _ in pairs], [b for _, b in pairs])
            print(f"{'proposed vs ' + tag:<24} {len(pairs):>6} {w['w_plus']:>9.1f} "
                  f"{w['z']:>+8.2f} {fmt_p(w['p']):>11} {stars(w['p']):<5} "
                  f"{st.median(diffs):>+11.1f}{unit:<1} {n_prop:>6}/{n_oth:<6} "
                  f"{d:>+9.3f} {lab:<11}")
    print("\n  median diff = median(proposed - other), negative = proposed cheaper.")
    print("  wins P/other = pairs where proposed / the other arm was faster.")
    print("  Cliff d sign: negative = proposed's times are smaller.")
    print("  |d|<0.147 negligible, <0.33 small, <0.474 medium, else large.")
    print("  Caveat: the normal approximation is only asymptotic; below ~20 pairs")
    print("  read p as indicative and prefer an exact signed-rank test.")
    print("  Caveat: an IQR of 0.0 above means that arm is deterministic across")
    print("  seeds, so the 'pairing' carries no channel information for it.")

    # ---- unpaired, kept for continuity with the published numbers -------
    print("\n### SECONDARY: Mann-Whitney U vs proposed (unpaired, two-sided) ###")
    print("  Ignores the pairing.  Where the comparator has ~zero variance across")
    print("  seeds this can report a SMALLER p than the paired test; that is the")
    print("  comparator being degenerate, not extra evidence.  Kept only because")
    print("  the published table quotes it.")
    for tag in tags:
        if tag == "proposed":
            continue
        other = series(data[tag], "rep")
        if not other:
            print(f"  proposed vs {tag:<11} n/a - no BS-report stage by design")
            continue
        _, z, p = mannwhitney_u(base_vals, other)
        print(f"  proposed vs {tag:<11} z={z:+7.2f}  p={fmt_p(p):<11} {stars(p):<5} "
              f"(medians {st.median(base_vals):.1f}s vs {st.median(other):.1f}s)")


def selftest():
    """Validates the S10/S11/S15 implementations against hand-computed values."""
    ok = True

    def chk(name, got, want, tol=5e-5):
        nonlocal ok
        good = (want != 0 and abs(got - want) / abs(want) < tol) or abs(got - want) < tol
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {name:<34} got {got!r:>24}  want {want!r}")

    print("S10  p-value no longer underflows")
    chk("erfc: z=12.20", _norm_sf2(12.20), 3.108e-34, tol=1e-3)
    chk("old formula at z=12.20", 2 * (1 - 0.5 * (1 + math.erf(12.20 / math.sqrt(2)))), 0.0)
    chk("erfc: z=1.959964 -> 0.05", _norm_sf2(1.959964), 0.05, tol=1e-5)
    chk("erfc: z=25 (old form gives 0)", _norm_sf2(25.0), 6.1134e-138, tol=1e-3)
    chk("erfc: z=38 (near the double floor)", _norm_sf2(38.0), 5.7709e-316, tol=1e-3)

    print("S11  Wilcoxon signed-rank (hand-computed, see docstring)")
    a = wilcoxon_signed_rank([(1, 0), (2, 0), (-3, 0), (4, 0), (5, 0)])
    chk("(a) no ties  W+", a["w_plus"], 12.0)
    chk("(a) no ties  z", a["z"], 4.5 / math.sqrt(13.75))
    chk("(a) no ties  p", a["p"], 0.2249159, tol=1e-6)
    b = wilcoxon_signed_rank([(1, 0), (-1, 0), (2, 0), (-2, 0), (3, 0)])
    chk("(b) ties     W+", b["w_plus"], 10.0)
    chk("(b) ties     z", b["z"], 2.5 / math.sqrt(13.5))
    chk("(b) ties     p", b["p"], 0.4962425, tol=1e-6)
    c = wilcoxon_signed_rank([(0, 0), (1, 0), (2, 0), (3, 0)])
    chk("(c) zeros dropped n", float(c["n"]), 3.0)
    chk("(c) zeros dropped z", c["z"], 3.0 / math.sqrt(3.5))
    chk("(c) zeros dropped p", c["p"], 0.1088094, tol=1e-6)

    print("S11  Cliff's delta (hand-computed, see docstring)")
    chk("delta([1,2,3],[2,3,4])", cliffs_delta([1, 2, 3], [2, 3, 4])[0], -5 / 9.0)
    chk("delta identical", cliffs_delta([1, 2, 3], [1, 2, 3])[0], 0.0)
    chk("delta disjoint", cliffs_delta([4, 5, 6], [1, 2, 3])[0], 1.0)
    # 25 pairs: a>b 10 times, a<b 11 times, 4 ties -> (10-11)/25 = -0.04
    chk("delta negligible", cliffs_delta([1, 2, 3, 4, 5], [1, 2, 3, 4, 6])[0], -1 / 25.0)
    chk("label negligible", 0.0 if cliffs_delta([1, 2, 3, 4, 5], [1, 2, 3, 4, 6])[1]
        == "negligible" else 1.0, 0.0)
    print("  label(-0.556) =", cliffs_delta([1, 2, 3], [2, 3, 4])[1])

    print("S15  nearest-rank p90")
    chk("p90 of 1..15", p90(list(range(1, 16))), 14.0)   # ceil(13.5)=14th value
    chk("p90 of 1..10", p90(list(range(1, 11))), 9.0)
    chk("p90 of 1..30", p90(list(range(1, 31))), 27.0)
    chk("old index on 1..15", float(sorted(range(1, 16))[int(0.9 * 15) - 1]), 13.0)

    print("Mann-Whitney sanity (known example)")
    # a=[1,2,3,4], b=[5,6,7,8] -> U=0, complete separation
    u, z, p = mannwhitney_u([1, 2, 3, 4], [5, 6, 7, 8])
    chk("U (complete separation)", u, 0.0)
    print("\n" + ("ALL SELF-TESTS PASSED" if ok else "SELF-TEST FAILURES"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
