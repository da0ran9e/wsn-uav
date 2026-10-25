#!/bin/bash
# River (prepared) again with --trace for the clusters of k16-s1 r100 whose critical cells end one packet short
# (item 168 scoring): same frozen binary, plan, pass bitmaps and mission index as mission.py --mapRuns, so the run
# must match; then which packet each stalled cell lacks, who holds it, and how River tried to move it.
B=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN3
W=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENV/r100/k16-s1
cd $W && mkdir -p tr
for k in 1 9; do
  LD_LIBRARY_PATH=$B/lib $B/river-bin --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv \
    --gateways=c$k-gateways-s35.csv --plan=plan$k.txt --bits=pass$k-bits --firstRun=$((1600100 + k)) --runs=1 --limit=900 \
    --gwSelect=quality --colours=7 --scheme=river --prep=full --out=tr/r$k --trace=tr/t$k 2>&1 | tail -1 &
done; wait
for k in 1 9; do
  cmp -s <(cut -d, -f1-9 r$k-rf-crit.csv) <(cut -d, -f1-9 tr/r$k-crit.csv) && echo "c$k crit identical" || echo "c$k DIFFERS"
done
