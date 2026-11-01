#!/bin/bash
# T* of River + takeover ($TG) at sigma S, seed R: a copy of the work folder where $TG files take the rf names.
#   score.sh S R
set -e
TG=${TG:-rfT}
L=$(cd $(dirname $0); pwd); S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
W=$S/WIND/s$1/R$2/k8-s1; T=$W-$TG
rm -rf $T; mkdir -p $T
for f in $W/*; do b=$(basename $f); case $b in *-rf-*|*-rf.log|*-$TG*) ;; *) ln -s $f $T/$b;; esac; done
for f in $W/*-$TG*; do b=$(basename $f); ln -s $f $T/${b/-$TG/-rf}; done
mkdir -p $L/results/$TG-s$1-R$2
cp $W/r*-$TG-*.csv $L/results/$TG-s$1-R$2/
python3 $L/../../uav-l2/tools/l1_rank.py --set r100 $T --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/results/$TG-s$1-R$2/l1 > /dev/null 2>&1
