#!/bin/bash
# Mission T* of one seed after run.sh (100 paired layer-1 draws, l1_rank.py): the campaign-4 CHORD method with the
# River (rf), direct-pull (d), Trickle (t) and path-scoped Trickle (tp) ground runs of the same passes, and B4 (no
# cooperation). Writes results/R<R>/l1-{draws,summary,cells}.csv.
#   CAMP_S=<scratchpad> bash score.sh R
set -e
R=$1
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
T=$L/../../uav-l2/tools
W=$CAMP_S/DT/r100/R$R/k8-s1
O=kin-puq-stage-zero-redir-kt-fcd
python3 $T/l1_rank.py --set r100 $W --draws 100 --jobs ${JOBS:-4} \
  --methods P+prog-$O,Pd+prog-$O,Pt+prog-$O,Ptp+prog-$O,B4-$O --out $L/results/R$R/l1 > $L/results/R$R/l1.log 2>&1
tail -n 3 $L/results/R$R/l1.log
touch $L/results/R$R/scored
