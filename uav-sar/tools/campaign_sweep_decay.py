import subprocess, csv, math, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def vpos(tid,g,nu): k=tid-(1+nu); return ((k%g)*20.0,(k//g)*20.0)
print(f"{'decay_m':>7} {'locFire%':>8} {'lerr_med':>8} {'lerr_mean':>9} {'lerr_p90':>8} {'err/decay':>9}")
for dec in [30,45,60,90,120]:
    err=[];fire=0
    for seed in range(1,N+1):
        out=f"{SP}/dec{dec}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=proposed",f"--clueDecay={dec}",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g,nu,tid=int(m["gridSize"]),int(m["numUav"]),int(m["targetNodeId"]); vx,vy=vpos(tid,g,nu)
        if float(m["timeToLocalize_s"])>=0: fire+=1
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="summon_start": err.append(math.hypot(float(e["x"])-vx,float(e["y"])-vy)); break
        except: pass
    err.sort(); p90=err[int(0.9*len(err))-1] if err else float('nan')
    em=st.median(err); ea=st.mean(err)
    print(f"{dec:>7} {100*fire/N:>7.0f}% {em:>8.1f} {ea:>9.1f} {p90:>8.1f} {ea/dec:>9.2f}")
