import subprocess, csv, math, statistics as st, os, sys
BIN=os.path.expanduser("build/src/uav-sar/examples/ns3.46-scenario-sar-default")
SP=sys.argv[1]; scheme=sys.argv[2]; N=int(sys.argv[3])
def victim_pos(tid, grid, numuav):
    k=tid-(1+numuav); return ((k%grid)*20.0, (k//grid)*20.0)
rows=[]
for seed in range(1,N+1):
    out=f"{SP}/{scheme}-{seed}"
    subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--outputDir={out}"],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    grid=int(m["gridSize"]); numuav=int(m["numUav"]); tid=int(m["targetNodeId"])
    vx,vy=victim_pos(tid,grid,numuav)
    rep=float(m["timeToReportAtBS_s"]); loc=float(m["timeToLocalize_s"]); cmp=float(m["timeToCompleteData_s"])
    # first summon target
    lerr=None
    try:
        for e in csv.DictReader(open(f"{out}/events.csv")):
            if e["event"]=="summon_start":
                lerr=math.hypot(float(e["x"])-vx, float(e["y"])-vy); break
    except FileNotFoundError: pass
    rows.append(dict(seed=seed,rep=rep,loc=loc,cmp=cmp,lerr=lerr,
                     energy=float(m["uavEnergyJ"]),rc=int(m["regionCells"]),
                     intra=int(m["intraShares"]),inter=int(m["interShares"])))
def frac(f): return sum(1 for r in rows if f(r))/len(rows)
def vals(k,filt=lambda r:True): return [r[k] for r in rows if filt(r) and r[k] is not None and r[k]>=0]
print(f"=== scheme={scheme}  N={len(rows)} ===")
print(f"localize fired : {frac(lambda r:r['loc']>=0)*100:.0f}%")
print(f"report @BS ok  : {frac(lambda r:r['rep']>=0)*100:.0f}%")
print(f"victim served  : {frac(lambda r:r['cmp']>=0)*100:.0f}%  (cmp != -1)")
le=vals('lerr',lambda r:r['loc']>=0)
if le:
    le.sort()
    print(f"localize error : mean {st.mean(le):.1f}m  median {st.median(le):.1f}m  p90 {le[int(0.9*len(le))-1]:.1f}m  max {max(le):.1f}m")
    print(f"  within 20m: {sum(1 for x in le if x<=20)/len(le)*100:.0f}%   within 40m: {sum(1 for x in le if x<=40)/len(le)*100:.0f}%")
for k,lbl in [('rep','report@BS s'),('loc','localize s'),('cmp','completeData s'),('energy','energy J')]:
    v=vals(k)
    if v: print(f"{lbl:16s}: mean {st.mean(v):.1f}  median {st.median(v):.1f}  (n={len(v)})")
print(f"region cells   : mean {st.mean(vals('rc')):.2f}   intra {st.mean(vals('intra')):.0f}  inter {st.mean(vals('inter')):.0f}")
