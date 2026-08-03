# W1 ablation: does the evidence^2-weighted CENTROID actually beat the trivial
# "aim at the single strongest reporter" (ARGMAX) rule?
#
# Why this matters for the paper: in a noise-free clue field with exact GPS and
# a victim co-located with a sensor node, argmax is expected to WIN by
# construction -- the strongest reporter IS the victim node.  If the centroid
# only wins once sensing noise exists, the localization claim must be scoped to
# the noisy regime, not stated unconditionally.  Paired by seed.
import subprocess, csv, math, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaign_common import victim_pos, p90

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP = sys.argv[1]
N = int(sys.argv[2])
GRIDS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["8", "16"]


def run(out, grid, argmax, seed):
    subprocess.run([BIN, f"--seed={seed}", "--scheme=proposed", f"--gridSize={grid}",
                    f"--aimArgmax={1 if argmax else 0}", "--simTime=600",
                    f"--outputDir={out}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        m = list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    except Exception:
        return None
    vx, vy = victim_pos(m)
    for e in csv.DictReader(open(f"{out}/events.csv")):
        if e["event"] == "deliver_start":
            return math.hypot(float(e["x"]) - vx, float(e["y"]) - vy)
    return None


for grid in GRIDS:
    pairs = []
    for seed in range(1, N + 1):
        c = run(f"{SP}/g{grid}-cen-{seed}", grid, False, seed)
        a = run(f"{SP}/g{grid}-arg-{seed}", grid, True, seed)
        if c is not None and a is not None:
            pairs.append((c, a))
    if not pairs:
        print(f"{grid}x{grid}: no paired runs")
        continue
    cen = [p[0] for p in pairs]
    arg = [p[1] for p in pairs]
    wins = sum(1 for c, a in pairs if c < a)          # centroid strictly closer
    ties = sum(1 for c, a in pairs if c == a)
    # Cliff's delta of (argmax - centroid): >0 means centroid is closer overall
    gt = sum(1 for c in cen for a in arg if c < a)
    lt = sum(1 for c in cen for a in arg if c > a)
    delta = (gt - lt) / (len(cen) * len(arg))
    print(f"{grid}x{grid}  n={len(pairs)}")
    print(f"  centroid  med {st.median(cen):6.1f} m   p90 {p90(cen):6.1f} m")
    print(f"  argmax    med {st.median(arg):6.1f} m   p90 {p90(arg):6.1f} m")
    print(f"  centroid closer in {wins}/{len(pairs)} pairs ({ties} ties), "
          f"Cliff delta {delta:+.2f}")
