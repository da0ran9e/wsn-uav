# NOTE (S8): the error column below is the RETRACTED leader-cell metric
# (||summon_start - victim||, i.e. the region leader's own grid-quantized
# position, ~2.5x higher than the delivery error the docs report).  It is kept
# only for historical comparison and is NOT the localization metric.  For the
# real DELIVERY error use:  campaign_sweep2.py <dir> <N> gridSpacing 15,20,25,30,40
import subprocess, csv, math, statistics as st, sys
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def med(xs): xs=[x for x in xs if x is not None and x>=0]; return st.median(xs) if xs else float('nan')
print("[S8] 'lcell_*' is the RETRACTED leader-cell error, not localization error")
print(f"{'space':>5} {'locFire%':>8} {'loc_s':>6} {'lcell_med':>9} {'lcell_p90':>9} {'vic%':>5} {'rep%':>5} {'rc':>4} {'intra':>6} {'inter':>6}")
for sp in [15,20,25,30,40]:
    loc=[];err=[];vic=0;rep=[];fire=0;rc=[];intra=[];inter=[]
    for seed in range(1,N+1):
        out=f"{SP}/sp{sp}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--gridSpacing={sp}",
                        "--simTime=250",f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        # S9: the swept value is only the LAST resort; metrics.csv wins if it
        # carries victimX/victimY or gridSpacing.
        vx,vy=victim_pos(m, fallback_spacing=sp)
        l=float(m["timeToLocalize_s"]); r=float(m["timeToReportAtBS_s"])
        if l>=0: fire+=1; loc.append(l)
        if r>=0: rep.append(r)
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        rc.append(int(m["regionCells"])); intra.append(int(m["intraShares"])); inter.append(int(m["interShares"]))
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort(); p90v=p90(err) if err else float('nan')
    em=st.median(err) if err else float('nan')
    print(f"{sp:>5} {100*fire/N:>7.0f}% {med(loc):>6.1f} {em:>9.1f} {p90v:>9.1f} {100*vic/N:>4.0f}% {100*len(rep)/N:>4.0f}% {st.mean(rc):>4.1f} {st.mean(intra):>6.0f} {st.mean(inter):>6.1f}")
