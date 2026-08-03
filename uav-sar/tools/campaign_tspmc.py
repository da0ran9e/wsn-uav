import subprocess, csv, statistics as st, sys
BIN="build/src/uav-sar/examples/ns3.46-scenario-sar-optimized"
SP=sys.argv[1]; N=int(sys.argv[2])
def med(xs): xs=[x for x in xs if x>=0]; return st.median(xs) if xs else float('nan')
for scheme,extra,stime in [("tsp-mc",["--numUav=4"],400),("tsp-mc",["--numUav=1"],700),("proposed",[],300)]:
    tag=f"{scheme}-{extra[0][-1] if extra else '4'}"
    rep=[];cmp_=[];en=[];pk=[];vic=0;repok=0
    for seed in range(1,N+1):
        out=f"{SP}/t4-{tag}-{seed}"
        subprocess.run([BIN,f"--seed={seed}",f"--scheme={scheme}",f"--simTime={stime}",
                        f"--outputDir={out}"]+extra,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try: m=list(csv.DictReader(open(f"{out}/metrics.csv")))[0]
        except: continue
        r=float(m["timeToReportAtBS_s"]); c=float(m["timeToCompleteData_s"])
        rep.append(r); cmp_.append(c)
        if r>=0: repok+=1
        if c>=0: vic+=1
        en.append(float(m["uavEnergyJ"])); pk.append(int(m["pktSent"]))
    print(f"{tag:12s} N={N} | report {100*repok/N:.0f}% @ {med(rep):.1f}s | victim {100*vic/N:.0f}% @ {med(cmp_):.1f}s | energy {med(en)/1000:.1f}kJ | pkts {med(pk):.0f}")
