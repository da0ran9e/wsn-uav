#!/bin/bash
# T* of River + takeover (rfT) at sigma S, seed R: a copy of the work folder where rfT files take the rf names.
#   score.sh S R
set -e
L=$(cd $(dirname $0); pwd); S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
W=$S/WIND/s$1/R$2/k8-s1; T=$W-T
rm -rf $T; mkdir -p $T
for f in $W/*; do b=$(basename $f); case $b in *-rf-*|*-rf.log|*-rfT*) ;; *) ln -s $f $T/$b;; esac; done
for f in $W/*-rfT*; do b=$(basename $f); ln -s $f $T/${b/-rfT/-rf}; done
mkdir -p $L/results/s$1-R$2
cp $W/r*-rfT-*.csv $L/results/s$1-R$2/
python3 $L/../../uav-l2/tools/l1_rank.py --set r100 $T --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/results/s$1-R$2/l1 > /dev/null 2>&1
