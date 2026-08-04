# Where does the ~20 m localization error actually come from?
#
# The noise sweep produced a surprise: the median BS fix error is ~18-21 m in
# EVERY configuration, including the fully idealized one (noise-free detector,
# exact GPS, victim on a node). Noise moves the p90 but barely touches the
# median. So the floor is NOT a measurement-quality problem -- improving the
# detector or the GPS cannot fix it.
#
# The remaining candidate is the DECISION TIME. A leader aims at the strongest
# reporter it has heard from so far, and a node only reports once its evidence
# (possessed-cue confidence x clue quality) crosses the cooperation threshold --
# which depends on the FAST UAVs' cue sweep having reached it. Fire early and
# you aim from a sparse, biased sample of the evidence field.
#
# This sweeps the observation window at the REALISTIC operating point to test
# that: if the floor is observation-limited, --minObserve should move it and
# nothing else should.
import subprocess, csv, statistics as st, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaign_common import p90

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP = sys.argv[1]
N = int(sys.argv[2])
GRID = sys.argv[3] if len(sys.argv) > 3 else "16"
VALS = [float(v) for v in (sys.argv[4] if len(sys.argv) > 4
                           else "0,10,20,30,45,60").split(",")]
REAL = ["--senseSigma=0.10", "--gpsSigma=5", "--victimOnNode=0"]

simtime = 300 * max(1, (int(GRID) // 8) ** 2)
print(f"# grid {GRID}x{GRID}, N={N}, realistic sensing ({' '.join(REAL)})")
print(f"{'minObserve':>10} {'fix med':>8} {'fix p90':>8} {'<=20m':>6} "
      f"{'t_report':>9} {'t_fix@BS':>9} {'victim%':>8} {'energy kJ':>10}")
for v in VALS:
    errs, reps, fixes, vic, en = [], [], [], 0, []
    for seed in range(1, N + 1):
        out = f"{SP}/m{v}-{seed}"
        subprocess.run([BIN, f"--seed={seed}", "--scheme=proposed",
                        f"--gridSize={GRID}", f"--minObserve={v}",
                        f"--simTime={simtime}", f"--outputDir={out}"] + REAL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            m = list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except Exception:
            continue
        e = float(m.get("reportErr_m", -1) or -1)
        if e >= 0:
            errs.append(e)
        r = float(m["timeToReportAtBS_s"])
        if r >= 0:
            reps.append(r)
        f = float(m.get("timeToFixAtBS_s", -1) or -1)
        if f >= 0:
            fixes.append(f)
        if float(m["timeToCompleteData_s"]) >= 0:
            vic += 1
        en.append(float(m["uavEnergyJ"]) / 1000.0)
    if not errs:
        print(f"{v:>10.0f}  no fixes")
        continue
    within = 100.0 * sum(1 for x in errs if x <= 20) / len(errs)
    print(f"{v:>10.0f} {st.median(errs):>8.1f} {p90(errs):>8.1f} {within:>5.0f}% "
          f"{st.median(reps) if reps else float('nan'):>9.1f} "
          f"{st.median(fixes) if fixes else float('nan'):>9.1f} "
          f"{100.0*vic/N:>7.0f}% {st.median(en):>10.1f}")
