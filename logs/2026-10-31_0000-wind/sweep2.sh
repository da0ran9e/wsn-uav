#!/bin/bash
# Seeds 2 and 3 at sigma 50 and 100 m (River), two runs at a time, then T* of each.
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
for R in 2 3; do
  for S in 50 100; do JOBS=2 bash $L/wind.sh $R $S > $L/results/sweep-s$S-R$R.txt 2>&1 & done
  wait
done
for R in 2 3; do for S in 50 100; do
  python3 $L/../../uav-l2/tools/l1_rank.py --set r100 $CAMP_S/WIND/s$S/R$R/k8-s1 --draws 100 --jobs 4 \
    --methods P+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/results/s$S-R$R/l1 > /dev/null 2>&1
done; done
touch $L/results/sweep2-done
