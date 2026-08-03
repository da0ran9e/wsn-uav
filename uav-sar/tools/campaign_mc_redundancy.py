# Fairness probe: what redundancy R does tsp-mc actually NEED to meet its own
# goal (every GT recovers the file)?  Their paper sizes connection time to just
# meet a target recovery probability, so the fair operating point is the
# smallest R reaching ~100% GT coverage — not an arbitrary constant.
import subprocess, csv, statistics as st, sys, os
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2]); NUAV=sys.argv[3] if len(sys.argv)>3 else "4"
print(f"{'R':>4} {'GTcov%':>7} {'victim%':>8} {'mission_s':>10} {'energy_kJ':>10} {'pkts':>7}")
for R in [1.0,1.5,2.0,3.0,4.0]:
    cov=[];vic=0;rep=[];en=[];pk=[]
    for seed in range(1,N+1):
        out=f"{SP}/r{R}-{seed}"
        subprocess.run([BIN,f"--seed={seed}","--scheme=tsp-mc",f"--numUav={NUAV}",
                        f"--mcRedundancy={R}","--simTime=600",f"--outputDir={out}"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        g=int(m["gridSize"]); total=g*g
        done=set()
        try:
            for e in csv.DictReader(open(f"{out}/events.csv")):
                if e["event"]=="gt_done": done.add(e["nodeId"])
        except: pass
        cov.append(100.0*len(done)/total)
        if float(m["timeToCompleteData_s"])>=0: vic+=1
        r=float(m["timeToReportAtBS_s"])
        if r>=0: rep.append(r)
        en.append(float(m["uavEnergyJ"])); pk.append(int(m["pktSent"]))
    print(f"{R:>4.1f} {st.mean(cov):>6.1f}% {100*vic/N:>7.0f}% "
          f"{st.median(rep) if rep else float('nan'):>10.1f} {st.median(en)/1000:>10.1f} {st.median(pk):>7.0f}")
