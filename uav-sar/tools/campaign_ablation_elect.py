# B2 ablation: what does the distributed election actually BUY?
#
# With --electSuppress=0 no leader ever hears another leader's stand-down, so
# every cell that crosses the alert threshold summons its own UAV -- which is
# exactly what the simulation did before the RCLAIM flood was added (SUMMON is
# one-hop; leaders sit 63-156 m apart on a ~37 m radio, so the stand-down could
# never arrive). That makes the pre-fix behaviour the ablation arm, and lets the
# election be measured rather than asserted.
#
# Paired by seed: seed k is the same channel realisation in both arms.
import subprocess, csv, math, statistics as st, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campaign_common import victim_pos, p90

BIN = "build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP = sys.argv[1]
N = int(sys.argv[2])
GRIDS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["8", "16"]


def run(out, grid, suppress, seed):
    simtime = 300 * max(1, (int(grid) // 8) ** 2)
    subprocess.run([BIN, f"--seed={seed}", "--scheme=proposed", f"--gridSize={grid}",
                    f"--electSuppress={1 if suppress else 0}", f"--simTime={simtime}",
                    f"--outputDir={out}"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        m = list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    except Exception:
        return None
    vx, vy = victim_pos(m)
    summons = yields = 0
    try:
        for e in csv.DictReader(open(f"{out}/events.csv")):
            if e["event"] == "summon_start":
                summons += 1
            elif e["event"] == "elect_yield":
                yields += 1
    except Exception:
        pass
    return dict(rep=float(m["timeToReportAtBS_s"]),
                pkts=float(m["pktSent"]),
                energy=float(m["uavEnergyJ"]) / 1000.0,
                fixerr=float(m.get("reportErr_m", -1) or -1),
                summons=summons, yields=yields)


def med(rows, k):
    xs = [r[k] for r in rows if r[k] is not None and r[k] >= 0]
    return st.median(xs) if xs else float("nan")


for grid in GRIDS:
    on, off = [], []
    for seed in range(1, N + 1):
        a = run(f"{SP}/g{grid}-on-{seed}", grid, True, seed)
        b = run(f"{SP}/g{grid}-off-{seed}", grid, False, seed)
        if a and b:
            on.append(a)
            off.append(b)
    if not on:
        print(f"{grid}x{grid}: no paired runs")
        continue
    print(f"\n### {grid}x{grid}  n={len(on)} paired seeds")
    print(f"{'arm':<22} {'summons':>8} {'yields':>7} {'t_report':>9} "
          f"{'energy kJ':>10} {'packets':>9} {'fix err m':>10} {'mission%':>9}")
    for lbl, rows in [("election ON", on), ("election OFF (pre-fix)", off)]:
        ok = 100.0 * sum(1 for r in rows if r["rep"] >= 0) / len(rows)
        print(f"{lbl:<22} {med(rows,'summons'):>8.1f} {med(rows,'yields'):>7.1f} "
              f"{med(rows,'rep'):>9.1f} {med(rows,'energy'):>10.1f} "
              f"{med(rows,'pkts'):>9.0f} {med(rows,'fixerr'):>10.1f} {ok:>8.0f}%")
    # paired win counts on the three cost metrics
    for k, lbl in [("rep", "mission time"), ("energy", "energy"), ("pkts", "packets")]:
        pairs = [(a[k], b[k]) for a, b in zip(on, off) if a[k] >= 0 and b[k] >= 0]
        wins = sum(1 for a, b in pairs if a < b)
        print(f"  {lbl:<14} election ON cheaper in {wins}/{len(pairs)} pairs "
              f"(median diff {st.median([a - b for a, b in pairs]):+.1f})")
