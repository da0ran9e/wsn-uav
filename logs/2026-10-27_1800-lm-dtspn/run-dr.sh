#!/bin/bash
# DTSP-N + River after run.sh stopped at its pass (the CH off the path): prefly.py, then the mission and the
# scores of run.sh (CLAUDE.md §8 item 187).
#   bash run-dr.sh ENV
set -e
ENV=$1
ROOT=/Users/mophan/Github/ns3-uav-build
REPO=/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav
PY=$ROOT/.venv/bin/python
BIN=$ROOT/BIN
RUN=$ROOT/runs
T=$REPO/uav-l2/tools
HERE=$REPO/logs/2026-10-27_1800-lm-dtspn
FLAGS="--clusters 8 --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $ENV --riverRepair 20 --schemes rf --jobs 2"
OUT=$HERE/$ENV
CP=$RUN/CP/$ENV/k8-s1
DR=$RUN/DR/$ENV/k8-s1
rm -f $DR/pass*-bits-r*.bin
$PY $HERE/prefly.py $DR $ENV 8 1 $BIN > $OUT/dr-prefly.log 2>&1
$PY $T/mission.py $FLAGS --work $DR > $OUT/dr-mission.log 2>&1
$PY $T/lm_tour.py score $CP,$RUN/LMD/$ENV/k8-s1,$DR --mode ns3 --out $OUT/score-ns3 > $OUT/score-ns3.log 2>&1
$PY $T/lm_tour.py score $CP,$RUN/LMD/$ENV/k8-s1,$DR --mode pred --out $OUT/score-pred > $OUT/score-pred.log 2>&1
cp $RUN/LMD/$ENV/k8-s1/lm.json $OUT/lmd.json
cp $DR/lm.json $OUT/dr.json
echo "$ENV done"
