import subprocess, csv, math, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-default"
SP=sys.argv[1]; N=int(sys.argv[2])
def vpos(tid,g,nu,sp): k=tid-(1+nu); return ((k%g)*sp,(k//g)*sp)
def med(xs): xs=[x for x in xs if x is not None and x>=0]; return st.median(xs) if xs else float('nan')
print(f"{'space':>5} {'locFire%':>8} {'loc_s':>6} {'lerr_med':>8} {'lerr_p90':>8} {'vic%':>5} {'rep%':>5} {'rc':>4} {'intra':>6} {'inter':>6}")
for sp in [15,20,25,30,40]:
    loc=[];err=[];vic=0;rep=[];fire=0;rc=[];intra=[];inter=[]
    for seed in range(1,N+1):
        out=f"{SP}/sp{sp}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--gridSpacing={sp}",
                        "--simTime=250",f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"]); vx,vy=vpos(tid,g,nu,sp)
        l=float(m["timeToLocalize_s"]); r=float(m["timeToReportAtBS_s"])
        if l>=0: fire+=1; loc.append(l)
        if r>=0: rep.append(r)
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        rc.append(int(m["regionCells"])); intra.append(int(m["intraShares"])); inter.append(int(m["interShares"]))
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort(); p90=err[int(0.9*len(err))-1] if err else float('nan')
    em=st.median(err) if err else float('nan')
    print(f"{sp:>5} {100*fire/N:>7.0f}% {med(loc):>6.1f} {em:>8.1f} {p90:>8.1f} {100*vic/N:>4.0f}% {100*len(rep)/N:>4.0f}% {st.mean(rc):>4.1f} {st.mean(intra):>6.0f} {st.mean(inter):>6.1f}")
