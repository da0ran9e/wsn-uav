#!/bin/bash
# River (prepared) again with --trace for every cluster of one mission folder (CLAUDE.md §8 item 164): same frozen
# binary, plan, pass bitmaps and ns-3 mission index as mission.py --mapRuns, so the results must match the
# campaign run; checked on the per-critical-cell columns.
#   trace.sh WORK CLUSTERS SEED
set -u
B=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN3
W=$1; KM=$2; SEED=$3
cd $W && mkdir -p tr
n=$(ls plan*.txt | wc -l)
for k in $(seq 1 $n); do
  R=$((100000 * KM + 100 * SEED + k))
  LD_LIBRARY_PATH=$B/lib $B/river-bin --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv \
    --gateways=c$k-gateways-s35.csv --plan=plan$k.txt --bits=pass$k-bits --firstRun=$R --runs=1 --limit=900 \
    --gwSelect=quality --colours=7 --scheme=river --prep=full --out=tr/r$k --trace=tr/t$k 2>&1 | tail -1 &
  [ $((k % 3)) -eq 0 ] && wait
done; wait
for k in $(seq 1 $n); do
  cmp -s <(cut -d, -f1-9 r$k-rf-crit.csv) <(cut -d, -f1-9 tr/r$k-crit.csv) && echo "c$k crit identical" || echo "c$k DIFFERS"
done
