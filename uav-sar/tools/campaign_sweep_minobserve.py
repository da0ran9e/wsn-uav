# NOTE (S8): the error column below is the RETRACTED leader-cell metric
# (||summon_start - victim||, i.e. the region leader's own grid-quantized
# position, ~2.5x higher than the delivery error the docs report).  It is kept
# only for historical comparison and is NOT the localization metric.  For the
# real DELIVERY error use:  campaign_sweep2.py <dir> <N> minObserve 0,10,20,30,45
import subprocess, csv, math, statistics as st, sys
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def med(xs): xs=[x for x in xs if x>=0]; return st.median(xs) if xs else float('nan')
print("[S8] 'lcell_*' is the RETRACTED leader-cell error, not localization error")
print(f"{'minObs':>6} {'localize_s':>10} {'lcell_med':>9} {'lcell_p90':>9} {'victim%':>7} {'report_s':>8}")
for mo in [0,10,20,30,45]:
    loc=[];err=[];vic=0;rep=[]
    for seed in range(1,N+1):
        out=f"{SP}/sw-{mo}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--minObserve={mo}",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        vx,vy=victim_pos(m)
        loc.append(float(m["timeToLocalize_s"])); rep.append(float(m["timeToReportAtBS_s"]))
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort()
    p90v=p90(err) if err else float('nan')
    emed=st.median(err) if err else float('nan')
    print(f"{mo:>6} {med(loc):>10.1f} {emed:>9.1f} {p90v:>9.1f} {100*vic/N:>6.0f}% {med(rep):>8.1f}")
