# Audit: the reliability numbers are the weakest claim in the study.
#
# "victim served 75%" at 16x16 rested on N=20, whose Wilson 95% interval is
# [53.1, 88.8] -- wide enough to be consistent with anything from "half the time"
# to "almost always". Rates need far more seeds than medians do, and the proposed
# arm is cheap to run, so there is no excuse for leaving it at 20.
#
# Reports the victim-served and mission-complete rates with Wilson intervals at
# whatever N you can afford, plus the intention-to-treat medians (over ALL runs,
# not only the ones that succeeded) so the survivorship question is answerable
# from the same output.
import subprocess, csv, statistics as st, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaign_stats import wilson

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP = sys.argv[1]
N = int(sys.argv[2])
GRID = sys.argv[3] if len(sys.argv) > 3 else "16"
EXTRA = sys.argv[4:] if len(sys.argv) > 4 else [
    "--senseSigma=0.10", "--gpsSigma=5", "--victimOnNode=0"]

simtime = 300 * max(1, (int(GRID) // 8) ** 2)
rows = []
for seed in range(1, N + 1):
    out = f"{SP}/p-{seed}"
    subprocess.run([BIN, f"--seed={seed}", "--scheme=proposed", f"--gridSize={GRID}",
                    f"--simTime={simtime}", f"--outputDir={out}"] + EXTRA,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        m = list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    except Exception:
        continue
    rows.append(dict(rep=float(m["timeToReportAtBS_s"]),
                     cmp=float(m["timeToCompleteData_s"]),
                     loc=float(m["timeToLocalize_s"]),
                     err=float(m.get("reportErr_m", -1) or -1),
                     en=float(m["uavEnergyJ"]) / 1000.0,
                     pk=float(m["pktSent"])))

n = len(rows)
print(f"# grid {GRID}x{GRID}, N={n}, args {' '.join(EXTRA)}")
for lbl, ok in [("mission complete (report@BS)", lambda r: r["rep"] >= 0),
                ("victim served (full dataset)", lambda r: r["cmp"] >= 0),
                ("localization fired", lambda r: r["loc"] >= 0),
                ("fix decoded at BS", lambda r: r["err"] >= 0)]:
    k = sum(1 for r in rows if ok(r))
    p, lo, hi = wilson(k, n)
    print(f"  {lbl:<30} {k:>4}/{n:<4} {p:5.1f}%  [{lo:5.1f}, {hi:5.1f}]")

print("\n# Intention-to-treat vs included-only (survivorship check).")
print("# t_report/energy/packets are defined whenever the MISSION completes, so")
print("# gating them on victim-served drops runs for a reason unrelated to them.")
print(f"  {'metric':<12} {'ALL runs':>22} {'victim-served only':>24} {'delta':>8}")
for k, nm in [("rep", "t_report s"), ("en", "energy kJ"), ("pk", "packets")]:
    a = [r[k] for r in rows if r[k] >= 0]
    i = [r[k] for r in rows if r[k] >= 0 and r["cmp"] >= 0]
    if not a or not i:
        continue
    ma, mi = st.median(a), st.median(i)
    print(f"  {nm:<12} {ma:>12.1f} (n={len(a):>3}) {mi:>16.1f} (n={len(i):>3}) "
          f"{100*(mi-ma)/ma:>+7.1f}%")

errs = sorted(r["err"] for r in rows if r["err"] >= 0)
if errs:
    print(f"\n  BS fix error: median {st.median(errs):.1f} m, "
          f"p90 {errs[min(len(errs)-1, math.ceil(0.9*len(errs))-1)]:.1f} m, n={len(errs)}")
