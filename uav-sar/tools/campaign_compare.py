import subprocess, csv, math, statistics as st, os, sys, json
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def run(scheme):
    R=[]
    for seed in range(1,N+1):
        out=f"{SP}/{scheme}-{seed}"
        subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--outputDir={out}",
                        "--simTime=200"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        vx,vy=victim_pos(m)
        rep,loc,cmp=float(m["timeToReportAtBS_s"]),float(m["timeToLocalize_s"]),float(m["timeToCompleteData_s"])
        # S8: ||summon_start - victim|| is the region LEADER's own grid-quantized
        # cell centre, NOT where data is delivered.  It was labelled "localize
        # error" and reads ~2.5x higher than the delivery error the docs report.
        # RETRACTED as a localization metric; kept only for historical comparison.
        leader_cell_err=None
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": leader_cell_err=math.hypot(float(e["x"])-vx,float(e["y"])-vy); break
        except: pass
        R.append(dict(rep=rep,loc=loc,cmp=cmp,leader_cell_err=leader_cell_err,
                      energy=float(m["uavEnergyJ"]),sent=int(m["pktSent"])))
    return R
def med(xs): xs=[x for x in xs if x is not None and x>=0]; return st.median(xs) if xs else float('nan')
def rate(R,f): return 100*sum(1 for r in R if f(r))/len(R)
res={}
for sc in ["proposed","nocoop","pure-uav"]:
    R=run(sc); res[sc]=R
    print(f"\n### {sc}  (N={len(R)})")
    print(f"  victim served       : {rate(R,lambda r:r['cmp']>=0):.0f}%")
    print(f"  median t-victim-data: {med([r['cmp'] for r in R]):.1f}s")
    if sc=="proposed":
        print(f"  localize fired      : {rate(R,lambda r:r['loc']>=0):.0f}%   median {med([r['loc'] for r in R]):.1f}s")
        print(f"  report@BS           : {rate(R,lambda r:r['rep']>=0):.0f}%   median {med([r['rep'] for r in R]):.1f}s")
        le=sorted([r['leader_cell_err'] for r in R if r['leader_cell_err'] is not None])
        if le:
            print(f"  leader_cell_error   : median {st.median(le):.1f}m  p90 {p90(le):.1f}m"
                  f"   [RETRACTED metric (S8) - NOT the localization error;"
                  f" use campaign_analyze2.py for DELIVERY error]")
    print(f"  UAV energy (median) : {med([r['energy'] for r in R])/1000:.1f} kJ")
    print(f"  pkts sent (median)  : {med([r['sent'] for r in R]):.0f}")
json.dump({k:[{kk:(vv if vv is not None else -1) for kk,vv in r.items()} for r in v] for k,v in res.items()},
          open(f"{SP}/results.json","w"))
print("\n[saved results.json]")
