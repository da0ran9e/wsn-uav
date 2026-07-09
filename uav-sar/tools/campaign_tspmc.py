import subprocess, csv, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-default"
SP=sys.argv[1]; N=int(sys.argv[2])
def med(xs): xs=[x for x in xs if x>=0]; return st.median(xs) if xs else float('nan')
for scheme,stime in [("tsp-mc",600),("proposed",300)]:
    rep=[];cmp_=[];en=[];pk=[];vic=0;repok=0
    for seed in range(1,N+1):
        out=f"{SP}/tm-{scheme}-{seed}"
        subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--simTime={stime}",
                        f"--outputDir={out}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        r=float(m["timeToReportAtBS_s"]); c=float(m["timeToCompleteData_s"])
        rep.append(r); cmp_.append(c)
        if r>=0: repok+=1
        if c>=0: vic+=1
        en.append(float(m["uavEnergyJ"])); pk.append(int(m["pktSent"]))
    print(f"{scheme:9s} N={N}  report@BS {100*repok/N:.0f}% @ {med(rep):.1f}s | victim {100*vic/N:.0f}% @ {med(cmp_):.1f}s | energy {med(en)/1000:.1f}kJ | pkts {med(pk):.0f}")
