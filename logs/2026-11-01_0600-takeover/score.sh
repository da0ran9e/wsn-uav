#!/bin/bash
# T* of River + takeover (rfT) at sigma 200, seed 1: a copy of the work folder where rfT files take the rf names.
set -e
L=$(cd $(dirname $0); pwd); S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
W=$S/WIND/s200/R1/k8-s1; T=$S/WIND/s200/R1/k8-s1-T
rm -rf $T; mkdir -p $T
for f in $W/*; do b=$(basename $f); case $b in *-rf-*|*-rf.log|*-rfT*) ;; *) ln -s $f $T/$b;; esac; done
for f in $W/*-rfT*; do b=$(basename $f); ln -s $f $T/${b/-rfT/-rf}; done
mkdir -p $L/results
python3 $L/../../uav-l2/tools/l1_rank.py --set r100 $T --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/results/l1
