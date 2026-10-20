#!/bin/bash
# River prepared again on every cluster of a mission work folder, with --trace (the animations need the hops and
# the CL arrivals; the results are identical to the folder's own run). Usage: river_trace.sh WORK TRACE BIN
set -e
W=$(cd "$1" && pwd); T=$(mkdir -p "$2" && cd "$2" && pwd); B=$(cd "$3" && pwd)
K=$(python3 -c "import json; print(json.load(open('$W/map.json'))['clusters'])")
cd "$W"
for k in $(seq 1 $K); do
  LD_LIBRARY_PATH=$B/lib $B/river-bin --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv --gateways=c$k-gateways-s35.csv \
    --plan=plan$k.txt --bits=pass$k-bits --firstRun=1 --runs=1 --limit=900 --gwSelect=quality --colours=7 \
    --scheme=river --prep=full --out=$T/r$k --trace=$T/t$k > $T/r$k.log 2>&1 &
done
wait
for k in $(seq 1 $K); do tail -1 $T/r$k.log; cmp <(cut -d, -f1-11 $T/r$k-crit.csv) <(cut -d, -f1-11 $W/r$k-rf-crit.csv) && echo "  C$k identical to the folder's run"; done
