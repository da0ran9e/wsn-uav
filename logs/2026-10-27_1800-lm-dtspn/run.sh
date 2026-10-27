#!/bin/bash
# LM-Tour (--dtspn, weights cl, wmin 1) and DTSP-N + River (--dtspnRiver) on CHORD's clusters (CP of
# logs/2026-10-27_1330-chord-plain-vs-lm), k8-s1, passes and River in ns-3 (CLAUDE.md §8 item 187).
#   bash run.sh ENV        ENV in open r500 r200 r100
set -e
ENV=$1
ROOT=/Users/mophan/Github/ns3-uav-build
REPO=/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav
PY=$ROOT/.venv/bin/python
BIN=$ROOT/BIN
RUN=$ROOT/runs
T=$REPO/uav-l2/tools
FLAGS="--clusters 8 --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $ENV --riverRepair 20 --schemes rf --jobs 2"
OUT=$REPO/logs/2026-10-27_1800-lm-dtspn/$ENV
CP=$RUN/CP/$ENV/k8-s1
mkdir -p $OUT

# 1. plans (model level): LM-Tour and DTSP-N + River
$PY $T/lm_tour.py plan $CP --out $RUN/LMD/$ENV/k8-s1 --R 450 --xi auto --theta 1 --rounds 1 --dtspn --weight cl \
  --wmin 1 > $OUT/lmd-plan.log 2>&1
$PY $T/lm_tour.py plan $CP --out $RUN/DR/$ENV/k8-s1 --xi auto --dtspnRiver > $OUT/dr-plan.log 2>&1

# 2. their passes flown in ns-3 and River run
$PY $T/mission.py $FLAGS --work $RUN/LMD/$ENV/k8-s1 > $OUT/lmd-mission.log 2>&1
$PY $T/mission.py $FLAGS --work $RUN/DR/$ENV/k8-s1 > $OUT/dr-mission.log 2>&1

# 3. T*, 100 layer-1 draws: River from ns-3, and predicted
$PY $T/lm_tour.py score $CP,$RUN/LMD/$ENV/k8-s1,$RUN/DR/$ENV/k8-s1 --mode ns3 --out $OUT/score-ns3 > $OUT/score-ns3.log 2>&1
$PY $T/lm_tour.py score $CP,$RUN/LMD/$ENV/k8-s1,$RUN/DR/$ENV/k8-s1 --mode pred --out $OUT/score-pred \
  > $OUT/score-pred.log 2>&1
cp $RUN/LMD/$ENV/k8-s1/lm.json $OUT/lmd.json
cp $RUN/DR/$ENV/k8-s1/lm.json $OUT/dr.json
echo "$ENV done"
