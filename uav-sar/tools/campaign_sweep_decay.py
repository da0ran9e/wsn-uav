# NOTE (S8): the error column below is the RETRACTED leader-cell metric
# (||summon_start - victim||, i.e. the region leader's own grid-quantized
# position, ~2.5x higher than the delivery error the docs report).  It is kept
# only for historical comparison and is NOT the localization metric.  For the
# real DELIVERY error use:  campaign_sweep2.py <dir> <N> clueDecay 30,45,60,90,120
import subprocess, csv, math, statistics as st, sys
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
print("[S8] 'lcell_*' is the RETRACTED leader-cell error, not localization error")
print(f"{'decay_m':>7} {'locFire%':>8} {'lcell_med':>9} {'lcell_mean':>10} {'lcell_p90':>9} {'err/decay':>9}")
for dec in [30,45,60,90,120]:
    err=[];fire=0
    for seed in range(1,N+1):
        out=f"{SP}/dec{dec}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--clueDecay={dec}",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        vx,vy=victim_pos(m)
        if float(m["timeToLocalize_s"])>=0: fire+=1
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort(); p90v=p90(err) if err else float('nan')
    em=st.median(err) if err else float('nan'); ea=st.mean(err) if err else float('nan')
    print(f"{dec:>7} {100*fire/N:>7.0f}% {em:>9.1f} {ea:>10.1f} {p90v:>9.1f} {ea/dec:>9.2f}")
