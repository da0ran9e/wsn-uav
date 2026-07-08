import subprocess, csv, math, statistics as st, os, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-default"
SP=sys.argv[1]; N=int(sys.argv[2]); rerun=len(sys.argv)>3
def vpos(tid,g,nu): k=tid-(1+nu); return ((k%g)*20.0,(k//g)*20.0)
cell=[];deliv=[];vic=0;fired=0
for seed in range(1,N+1):
    out=f"{SP}/proposed-{seed}"
    if rerun:
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--outputDir={out}"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
    g,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"]); vx,vy=vpos(tid,g,nu)
    if float(m["timeToLocalize_s"])>=0: fired+=1
    if float(m["timeToCompleteData_s"])>=0: vic+=1
    sm=dl=None
    for e in csv.DictReader(open(f"{out}/events.csv")):
        if e["event"]=="summon_start" and sm is None: sm=(float(e["x"]),float(e["y"]))
        if e["event"]=="deliver_start" and dl is None: dl=(float(e["x"]),float(e["y"]))
    if sm: cell.append(math.hypot(sm[0]-vx,sm[1]-vy))
    if dl: deliv.append(math.hypot(dl[0]-vx,dl[1]-vy))
def stats(name,xs):
    if not xs: print(f"{name}: none"); return
    xs=sorted(xs)
    print(f"{name:22s}: median {st.median(xs):5.1f}m  mean {st.mean(xs):5.1f}m  p90 {xs[int(0.9*len(xs))-1]:5.1f}m  <=20m {100*sum(1 for x in xs if x<=20)/len(xs):3.0f}%")
print(f"N={N}  localize fired {100*fired/N:.0f}%  victim served {100*vic/N:.0f}%")
stats("LEADER-cell error", cell)
stats("DELIVERY error", deliv)
