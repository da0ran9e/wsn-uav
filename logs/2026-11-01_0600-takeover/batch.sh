#!/bin/bash
# Wind table again with takeover: wait for s200 R1, score it, then rfT on s50 and s100 seeds 1-3 (passes reused).
L=$(cd $(dirname $0); pwd); S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
while pgrep -f "mission.py.*rfT" > /dev/null; do sleep 30; done
$L/score.sh 200 1
for SIG in 50 100; do for R in 1 2 3; do
  python3 $L/../../tools/runlog.py $L/s$SIG-R$R-rfT.md "python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin $S/CAMP-BINT --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass --mapRuns --env r100 --riverRepair 20 --jobs 4 --runSeed $R --schemes rfT --work $S/WIND/s$SIG/R$R/k8-s1" --cwd $L/../.. > /dev/null 2>&1
  $L/score.sh $SIG $R
done; done
touch $L/results/batch-done
