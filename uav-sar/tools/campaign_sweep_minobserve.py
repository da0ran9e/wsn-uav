import subprocess, csv, math, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def vpos(tid,g,nu): k=tid-(1+nu); return ((k%g)*20.0,(k//g)*20.0)
def med(xs): xs=[x for x in xs if x>=0]; return st.median(xs) if xs else float('nan')
print(f"{'minObs':>6} {'localize_s':>10} {'lerr_med':>8} {'lerr_p90':>8} {'victim%':>7} {'report_s':>8}")
for mo in [0,10,20,30,45]:
    loc=[];err=[];vic=0;rep=[]
    for seed in range(1,N+1):
        out=f"{SP}/sw-{mo}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--minObserve={mo}",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"]); vx,vy=vpos(tid,g,nu)
        loc.append(float(m["timeToLocalize_s"])); rep.append(float(m["timeToReportAtBS_s"]))
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort()
    p90=err[int(0.9*len(err))-1] if err else float('nan')
    print(f"{mo:>6} {med(loc):>10.1f} {st.median(err):>8.1f} {p90:>8.1f} {100*vic/N:>6.0f}% {med(rep):>8.1f}")
