#!/bin/bash
# sigma 100 and 200 m on seed 1, two cores each, then T* of each (l1_rank, the CHORD method).
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
for S in 100 200; do JOBS=2 bash $L/wind.sh 1 $S > $L/results/sweep-s$S.txt 2>&1 & done
wait
for S in 100 200; do
  python3 $L/../../uav-l2/tools/l1_rank.py --set r100 $CAMP_S/WIND/s$S/R1/k8-s1 --draws 100 --jobs 4 \
    --methods P+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/results/s$S-R1/l1 > /dev/null 2>&1
done
touch $L/results/sweep-done
