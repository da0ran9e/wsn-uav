import subprocess, csv, math, statistics as st, os, sys
from campaign_common import victim_pos, p90   # S9 (spacing), S15 (p90 index)
BIN=os.path.expanduser("build/src/uav-sar/examples/ns3.46-scenario-sar-optimized")
SP=sys.argv[1]; scheme=sys.argv[2]; N=int(sys.argv[3])
rows=[]
for seed in range(1,N+1):
    out=f"{SP}/{scheme}-{seed}"
    subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--outputDir={out}"],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    vx,vy=victim_pos(m)
    rep=float(m["timeToReportAtBS_s"]); loc=float(m["timeToLocalize_s"]); cmp=float(m["timeToCompleteData_s"])
    # S8: first summon target == the region LEADER's own grid-quantized cell,
    # not where data is delivered.  RETRACTED as a localization metric (reads
    # ~2.5x high); retained only for historical comparison.
    leader_cell_err=None
    try:
        for e in csv.DictReader(open(f"{out}/events.csv")):
            if e["event"]=="summon_start":
                leader_cell_err=math.hypot(float(e["x"])-vx, float(e["y"])-vy); break
    except FileNotFoundError: pass
    rows.append(dict(seed=seed,rep=rep,loc=loc,cmp=cmp,leader_cell_err=leader_cell_err,
                     energy=float(m["uavEnergyJ"]),rc=int(m["regionCells"]),
                     intra=int(m["intraShares"]),inter=int(m["interShares"])))
def frac(f): return sum(1 for r in rows if f(r))/len(rows)
def vals(k,filt=lambda r:True): return [r[k] for r in rows if filt(r) and r[k] is not None and r[k]>=0]
print(f"=== scheme={scheme}  N={len(rows)} ===")
print(f"localize fired : {frac(lambda r:r['loc']>=0)*100:.0f}%")
print(f"report @BS ok  : {frac(lambda r:r['rep']>=0)*100:.0f}%")
print(f"victim served  : {frac(lambda r:r['cmp']>=0)*100:.0f}%  (cmp != -1)")
le=vals('leader_cell_err',lambda r:r['loc']>=0)
if le:
    le.sort()
    print("leader_cell_error [RETRACTED metric (S8) - NOT the localization error;")
    print("                   it is the leader's own cell centre. DELIVERY error")
    print("                   is in campaign_analyze2.py / campaign_sweep2.py]")
    print(f"  mean {st.mean(le):.1f}m  median {st.median(le):.1f}m  p90 {p90(le):.1f}m  max {max(le):.1f}m")
    print(f"  within 20m: {sum(1 for x in le if x<=20)/len(le)*100:.0f}%   within 40m: {sum(1 for x in le if x<=40)/len(le)*100:.0f}%")
for k,lbl in [('rep','report@BS s'),('loc','localize s'),('cmp','completeData s'),('energy','energy J')]:
    v=vals(k)
    if v: print(f"{lbl:16s}: mean {st.mean(v):.1f}  median {st.median(v):.1f}  (n={len(v)})")
print(f"region cells   : mean {st.mean(vals('rc')):.2f}   intra {st.mean(vals('intra')):.0f}  inter {st.mean(vals('inter')):.0f}")
