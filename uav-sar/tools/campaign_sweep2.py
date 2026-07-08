# unified sweep with the CORRECT metric: delivery error (deliver_start -> victim)
import subprocess, csv, math, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-default"
SP=sys.argv[1]; N=int(sys.argv[2]); knob=sys.argv[3]; vals=[float(v) for v in sys.argv[4].split(",")]
def vpos(tid,g,nu,sp=20.0): k=tid-(1+nu); return ((k%g)*sp,(k//g)*sp)
print(f"{'val':>6} {'fire%':>5} {'deliv_med':>9} {'deliv_p90':>9} {'<=20m':>6} {'vic%':>5} {'rep_s':>6}")
for v in vals:
    dl=[];vic=0;fired=0;rep=[]
    for seed in range(1,N+1):
        out=f"{SP}/u-{knob}{v}-{seed}"
        args=[BIN,f"--seed={seed}","--scheme=proposed",f"--{knob}={v}",f"--outputDir={out}"]
        if knob=="gridSpacing": args.append("--simTime=250")
        subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"])
        sp=v if knob=="gridSpacing" else 20.0
        vx,vy=vpos(tid,g,nu,sp)
        if float(m["timeToLocalize_s"])>=0: fired+=1
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        r=float(m["timeToReportAtBS_s"]);
        if r>=0: rep.append(r)
        for e in csv.DictReader(open(f"{out}/events.csv")):
            if e["event"]=="deliver_start": dl.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
    dl.sort()
    med=st.median(dl) if dl else float('nan'); p90=dl[int(0.9*len(dl))-1] if dl else float('nan')
    within=100*sum(1 for x in dl if x<=20)/len(dl) if dl else 0
    print(f"{v:>6.0f} {100*fired/N:>4.0f}% {med:>9.1f} {p90:>9.1f} {within:>5.0f}% {100*vic/N:>4.0f}% {st.median(rep) if rep else float('nan'):>6.1f}")
