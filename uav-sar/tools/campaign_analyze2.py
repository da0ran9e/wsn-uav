# Side-by-side of the RETRACTED leader-cell metric (S8) and the real DELIVERY
# error, on the same runs -- this is the script that documents the ~2.5x gap.
import subprocess, csv, math, statistics as st, os, sys
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2]); rerun=len(sys.argv)>3
cell=[];deliv=[];vic=0;fired=0
for seed in range(1,N+1):
    out=f"{SP}/proposed-{seed}"
    if rerun:
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--outputDir={out}"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    vx,vy=victim_pos(m)
    if float(m["timeToLocalize_s"])>=0: fired+=1
    if float(m["timeToCompleteData_s"])>=0: vic+=1
    sm=dl=None
    for e in csv.DictReader(open(f"{out}/events.csv")):
        if e["event"]=="summon_start" and sm is None: sm=(float(e["x"]),float(e["y"]))
        if e["event"]=="deliver_start" and dl is None: dl=(float(e["x"]),float(e["y"]))
    # S8: `sm` is the leader's own cell centre, NOT a localization estimate.
    if sm: cell.append(math.hypot(sm[0]-vx,sm[1]-vy))
    if dl: deliv.append(math.hypot(dl[0]-vx,dl[1]-vy))
def stats(name,xs):
    if not xs: print(f"{name}: none"); return
    xs=sorted(xs)
    print(f"{name:22s}: median {st.median(xs):5.1f}m  mean {st.mean(xs):5.1f}m  p90 {p90(xs):5.1f}m  <=20m {100*sum(1 for x in xs if x<=20)/len(xs):3.0f}%")
print(f"N={N}  localize fired {100*fired/N:.0f}%  victim served {100*vic/N:.0f}%")
stats("leader_cell_error", cell)   # RETRACTED (S8), historical comparison only
stats("DELIVERY error", deliv)     # <-- this is the localization metric
