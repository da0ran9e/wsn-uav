import subprocess, csv, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2]); R=sys.argv[3]
print(f"{'VBS_r':>6} {'#VBS':>5} {'GTcov%':>7} {'victim%':>8} {'mission_s':>10} {'energy_kJ':>10}")
for rad in [40,50,60,70,80]:
    cov=[];vic=0;rep=[];en=[];nvbs=[]
    for seed in range(1,N+1):
        out=f"{SP}/rad{rad}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=tsp-mc","--numUav=4",
                        f"--mcRedundancy={R}",f"--mcRadius={rad}","--simTime=800",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g=int(m["gridSize"]); total=g*g
        done=set(); hovers=0
        for e in csv.DictReader(open(f"{out}/events.csv")):
            if e["event"]=="gt_done": done.add(e["nodeId"])
        cov.append(100.0*len(done)/total)
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        r=float(m["timeToReportAtBS_s"])
        if r>=0: rep.append(r)
        en.append(float(m["uavEnergyJ"]))
    print(f"{rad:>6} {'-':>5} {st.mean(cov):>6.1f}% {100*vic/N:>7.0f}% "
          f"{st.median(rep) if rep else float('nan'):>10.1f} {st.median(en)/1000:>10.1f}")
