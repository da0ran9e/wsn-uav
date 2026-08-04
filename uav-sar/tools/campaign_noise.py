# M9/W3/W7: how does the localization degrade as the sensing side stops being
# idealized, and does the CENTROID estimator finally earn its place over the
# trivial ARGMAX rule once it does?
#
# In the noise-free field with the victim on a node, the two rules were
# statistically indistinguishable (see campaign_ablation_aim.py) -- which is why
# no estimator claim was made. The hypothesis under test here is that averaging
# several noisy reports beats trusting the single loudest one, and that the gap
# should GROW with noise. If it does not, the centroid should be dropped.
#
# Every row is measured on the fix the BS actually decoded (reportErr_m), not on
# an internal event, and both estimator arms are paired by seed.
import subprocess, csv, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaign_common import p90

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP = sys.argv[1]
N = int(sys.argv[2])
GRID = sys.argv[3] if len(sys.argv) > 3 else "16"

# (senseSigma, gpsSigmaM, victimOnNode) -- row 0 is the published idealized case
POINTS = [
    (0.00, 0.0, 1),
    (0.00, 0.0, 0),
    (0.05, 2.0, 0),
    (0.10, 5.0, 0),
    (0.20, 10.0, 0),
]


def run(out, sense, gps, onnode, argmax, seed):
    simtime = 300 * max(1, (int(GRID) // 8) ** 2)
    subprocess.run([BIN, f"--seed={seed}", "--scheme=proposed", f"--gridSize={GRID}",
                    f"--senseSigma={sense}", f"--gpsSigma={gps}",
                    f"--victimOnNode={onnode}", f"--aimArgmax={1 if argmax else 0}",
                    f"--simTime={simtime}", f"--outputDir={out}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        m = list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    except Exception:
        return None
    return dict(err=float(m.get("reportErr_m", -1) or -1),
                rep=float(m["timeToReportAtBS_s"]),
                victim=float(m["timeToCompleteData_s"]))


def cliffs(a, b):
    gt = sum(1 for x in a for y in b if x > y)
    lt = sum(1 for x in a for y in b if x < y)
    return (gt - lt) / float(len(a) * len(b)) if a and b else float("nan")


print(f"# grid {GRID}x{GRID}, N={N} seeds, paired. err = BS-decoded fix error.")
print(f"{'senseSig':>8} {'gpsSig':>7} {'onNode':>7} | "
      f"{'centroid med':>12} {'p90':>7} | {'argmax med':>11} {'p90':>7} | "
      f"{'cen<arg':>8} {'Cliff d':>8} | {'mission%':>8} {'victim%':>8}")
print("-" * 108)
for sense, gps, onnode in POINTS:
    cen, arg, miss, vic = [], [], 0, 0
    for seed in range(1, N + 1):
        tag = f"s{sense}-g{gps}-n{onnode}-{seed}"
        c = run(f"{SP}/cen-{tag}", sense, gps, onnode, False, seed)
        a = run(f"{SP}/arg-{tag}", sense, gps, onnode, True, seed)
        if not c or not a:
            continue
        if c["rep"] >= 0:
            miss += 1
        if c["victim"] >= 0:
            vic += 1
        if c["err"] >= 0 and a["err"] >= 0:
            cen.append(c["err"])
            arg.append(a["err"])
    if not cen:
        print(f"{sense:>8.2f} {gps:>7.1f} {onnode:>7} | no paired fixes")
        continue
    wins = sum(1 for x, y in zip(cen, arg) if x < y)
    print(f"{sense:>8.2f} {gps:>7.1f} {onnode:>7} | "
          f"{st.median(cen):>12.1f} {p90(cen):>7.1f} | "
          f"{st.median(arg):>11.1f} {p90(arg):>7.1f} | "
          f"{wins:>4}/{len(cen):<3} {cliffs(cen, arg):>+8.2f} | "
          f"{100.0*miss/N:>7.0f}% {100.0*vic/N:>7.0f}%")
print("\nCliff d < 0 means the CENTROID's errors are smaller (it wins).")
