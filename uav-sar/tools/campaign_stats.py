#!/usr/bin/env python3
"""Publication-grade campaign: point estimates WITH uncertainty.

Reports, for each scheme: success rates with Wilson 95% CIs, median latencies
with bootstrap 95% CIs, and a Mann-Whitney U test (normal approximation with
tie correction) of the headline difference against the proposed scheme.

Deliberately dependency-free (no numpy/scipy) so a reviewer can rerun it
anywhere.  Failed runs (metric == -1) are reported as failures and EXCLUDED
from latency statistics -- and the failure rate is reported alongside, so the
reader can see survivorship effects instead of them hiding in a median.

Usage:  campaign_stats.py <outdir> <N seeds> [--quick]
"""
import csv, math, os, random, subprocess, sys, statistics as st

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


def mannwhitney_u(a, b):
    """Two-sided Mann-Whitney U, normal approximation with tie correction.

    Returns (U, z, p).  Non-parametric: no normality assumption, appropriate
    for these skewed latency distributions.
    """
    if not a or not b:
        return float("nan"), float("nan"), float("nan")
    combined = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks, i, n = [0.0] * len(combined), 0, len(combined)
    tie_term = 0.0
    while i < n:                                    # average ranks within ties
        j = i
        while j + 1 < n and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        t = j - i + 1
        if t > 1:
            tie_term += t ** 3 - t
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, combined) if g == 0)
    n1, n2 = len(a), len(b)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sd = math.sqrt(max(1e-12, (n1 * n2 / 12.0) *
                       ((n1 + n2 + 1) - tie_term / ((n1 + n2) * (n1 + n2 - 1)))))
    z = (u1 - mu) / sd
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return u1, z, p


def victim_pos(tid, grid, nuav, spacing=20.0):
    k = tid - (1 + nuav)
    return (k % grid) * spacing, (k // grid) * spacing


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
        grid, nuav = int(m["gridSize"]), int(m["numUav"])
        vx, vy = victim_pos(int(m["targetNodeId"]), grid, nuav)
        derr = None
        try:
            for e in csv.DictReader(open(os.path.join(out, "events.csv"))):
                if e["event"] == "deliver_start":
                    derr = math.hypot(float(e["x"]) - vx, float(e["y"]) - vy)
                    break
        except Exception:
            pass
        rows.append(dict(rep=float(m["timeToReportAtBS_s"]),
                         cmp=float(m["timeToCompleteData_s"]),
                         loc=float(m["timeToLocalize_s"]),
                         derr=derr,
                         energy=float(m["uavEnergyJ"]),
                         pkts=int(m["pktSent"])))
    return rows


def main():
    outdir, n = sys.argv[1], int(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    tags = list(SCHEMES) if "--quick" not in sys.argv else ["proposed", "tsp-mc-x4"]
    data = {}
    for tag in tags:
        data[tag] = run_scheme(tag, outdir, n)
        print(f"  [{tag}] {len(data[tag])} runs collected", file=sys.stderr)

    print(f"\n### Campaign with 95% confidence intervals (N={n} seeds/scheme) ###\n")
    hdr = f"{'scheme':<11} {'mission ok (Wilson CI)':<26} {'t_report med [CI]':<24} " \
          f"{'victim ok (CI)':<24} {'t_victim med [CI]':<22}"
    print(hdr)
    print("-" * len(hdr))
    for tag in tags:
        R = data[tag]
        n_ok = sum(1 for r in R if r["rep"] >= 0)
        v_ok = sum(1 for r in R if r["cmp"] >= 0)
        p1, l1, h1 = wilson(n_ok, len(R))
        p2, l2, h2 = wilson(v_ok, len(R))
        m1, a1, b1 = boot_median_ci([r["rep"] for r in R if r["rep"] >= 0])
        m2, a2, b2 = boot_median_ci([r["cmp"] for r in R if r["cmp"] >= 0])
        print(f"{tag:<11} {p1:5.1f}% [{l1:5.1f},{h1:5.1f}]{'':<7} "
              f"{m1:6.1f} [{a1:5.1f},{b1:6.1f}]{'':<3} "
              f"{p2:5.1f}% [{l2:5.1f},{h2:5.1f}]{'':<5} "
              f"{m2:6.1f} [{a2:5.1f},{b2:6.1f}]")

    print(f"\n{'scheme':<11} {'energy kJ med [CI]':<24} {'packets med [CI]':<24} "
          f"{'delivery err m med [CI]':<24}")
    print("-" * 84)
    for tag in tags:
        R = data[tag]
        e, el, eh = boot_median_ci([r["energy"] / 1000 for r in R])
        k, kl, kh = boot_median_ci([float(r["pkts"]) for r in R])
        de = [r["derr"] for r in R if r["derr"] is not None]
        d, dl, dh = boot_median_ci(de) if de else (float("nan"),) * 3
        print(f"{tag:<11} {e:6.1f} [{el:5.1f},{eh:6.1f}]{'':<5} "
              f"{k:7.0f} [{kl:6.0f},{kh:7.0f}]{'':<2} "
              f"{d:6.1f} [{dl:5.1f},{dh:6.1f}]")

    if "proposed" in data:
        print("\n### Mann-Whitney U vs proposed (two-sided) — mission completion time ###")
        base = [r["rep"] for r in data["proposed"] if r["rep"] >= 0]
        for tag in tags:
            if tag == "proposed":
                continue
            other = [r["rep"] for r in data[tag] if r["rep"] >= 0]
            if not other:
                print(f"  proposed vs {tag:<11} n/a - scheme has no BS-report "
                      f"stage by design (never completes the mission)")
                continue
            _, z, p = mannwhitney_u(base, other)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."
            pstr = "<1e-16" if p < 1e-16 else f"{p:.3g}"   # avoid printing a bare 0
            print(f"  proposed vs {tag:<11} z={z:+7.2f}  p={pstr:<7} {sig}   "
                  f"(medians {st.median(base):.1f}s vs {st.median(other):.1f}s)")


if __name__ == "__main__":
    main()
