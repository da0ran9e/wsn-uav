#!/bin/bash
# Tier 3 check: the variant passes of variants.py flown in ns-3 and River run (6 folders x 8 clusters).
#   bash run.sh ENV
set -e
ENV=$1
ROOT=/Users/mophan/Github/ns3-uav-build
HERE=/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/logs/2026-10-28_t3-surrogate
PY=$ROOT/.venv/bin/python
T=/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/uav-l2/tools
FLAGS="--clusters 8 --seed 1 --bin $ROOT/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $ENV --riverRepair 20 --schemes rf --jobs 4"
cd $HERE
mkdir -p $ENV
$PY variants.py $ENV > $ENV/variants.log 2>&1
for j in 0 1 2 3 4 5; do
  $PY $T/mission.py $FLAGS --work $ROOT/runs/T3v$j/$ENV/k8-s1 > $ENV/v$j-mission.log 2>&1
done
echo "$ENV done"
