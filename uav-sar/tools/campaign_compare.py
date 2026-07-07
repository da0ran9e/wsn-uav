import subprocess, csv, math, statistics as st, os, sys, json
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-default"
SP=sys.argv[1]; N=int(sys.argv[2])
def vpos(tid,grid,nu): k=tid-(1+nu); return ((k%grid)*20.0,(k//grid)*20.0)
def run(scheme):
    R=[]
    for seed in range(1,N+1):
        out=f"{SP}/{scheme}-{seed}"
        subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--outputDir={out}",
                        "--simTime=200"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        grid,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"])
        vx,vy=vpos(tid,grid,nu)
        rep,loc,cmp=float(m["timeToReportAtBS_s"]),float(m["timeToLocalize_s"]),float(m["timeToCompleteData_s"])
        lerr=None
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": lerr=math.hypot(float(e["x"])-vx,float(e["y"])-vy); break
        except: pass
        R.append(dict(rep=rep,loc=loc,cmp=cmp,lerr=lerr,energy=float(m["uavEnergyJ"]),
                      sent=int(m["pktSent"])))
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
        le=sorted([r['lerr'] for r in R if r['lerr'] is not None])
        print(f"  localize error      : median {st.median(le):.1f}m  p90 {le[int(0.9*len(le))-1]:.1f}m")
    print(f"  UAV energy (median) : {med([r['energy'] for r in R])/1000:.1f} kJ")
    print(f"  pkts sent (median)  : {med([r['sent'] for r in R]):.0f}")
json.dump({k:[{kk:(vv if vv is not None else -1) for kk,vv in r.items()} for r in v] for k,v in res.items()},
          open(f"{SP}/results.json","w"))
print("\n[saved results.json]")
