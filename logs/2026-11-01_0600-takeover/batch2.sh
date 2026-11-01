#!/bin/bash
# Sequenced takeover (rfS) at sigma 100, seeds 1-3. Clusters without takeover run the same code as rfT, so their rfT
# outputs are copied as rfS; only the clusters with takeover (s100: R1 c3 c8, R2 c7, R3 c2 c6) are simulated again.
L=$(cd $(dirname $0); pwd); S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
for R in 1 2 3; do
  W=$S/WIND/s100/R$R/k8-s1
  for k in 1 2 3 4 5 6 7 8; do
    grep -q '^takeover' $W/r$k-rfT.log && continue
    for x in crit runs energy; do cp $W/r$k-rfT-$x.csv $W/r$k-rfS-$x.csv; done; cp $W/r$k-rfT.log $W/r$k-rfS.log
  done
  python3 $L/../../tools/runlog.py $L/s100-R$R-rfS.md "python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin $S/CAMP-BINS --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass --mapRuns --env r100 --riverRepair 20 --jobs 4 --runSeed $R --schemes rfS --work $W" --cwd $L/../.. > /dev/null 2>&1
  TG=rfS $L/score2.sh 100 $R
done
touch $L/results/batch2-done
