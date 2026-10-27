#!/bin/bash
# CHORD (plain) vs LM-Tour (best: bend, R = 450 m, xi auto, theta 1, one round), k8-s1, one ns-3 run per cluster
# (CLAUDE.md §8 item 186). Also CHORD-T (the archived P*, FIX/) re-run locally as the reference and as a check that
# the local binaries reproduce the cloud runs.
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
OUT=$REPO/logs/2026-10-27_1330-chord-plain-vs-lm/$ENV
mkdir -p $OUT

# 0. reference: CHORD-T from the archive (FIX), pass bitmaps re-flown, River re-run (archived results kept as *.cloud)
mkdir -p $RUN/REF/$ENV
if [ ! -d $RUN/REF/$ENV/k8-s1 ]; then
  cp -R $RUN/FIX/$ENV/k8-s1 $RUN/REF/$ENV/k8-s1
  for f in $RUN/REF/$ENV/k8-s1/r*-rf-*.csv; do mv "$f" "$f.cloud"; done
  rm -f $RUN/REF/$ENV/k8-s1/r*-d-*.csv
fi
$PY $T/mission.py $FLAGS --chordTour 0.6,0.8 --work $RUN/REF/$ENV/k8-s1 > $OUT/ref-mission.log 2>&1

# 1. CHORD (plain): the longest flyable chord through each CH, chosen per cluster; same delivery fix (slow down or
#    loop until one clue-set copy is sent over the cluster), River, coding and team 2 as P*
$PY $T/mission.py $FLAGS --work $RUN/CP/$ENV/k8-s1 > $OUT/cp-mission.log 2>&1

# 2. LM-Tour on CHORD's chords (model level, step C), then its passes flown in ns-3 and River run (step D)
$PY $T/lm_tour.py plan $RUN/CP/$ENV/k8-s1 --out $RUN/LM/$ENV/k8-s1 --R 450 --xi auto --theta 1 --rounds 1 \
  > $OUT/lm-plan.log 2>&1
$PY $T/mission.py $FLAGS --work $RUN/LM/$ENV/k8-s1 > $OUT/lm-mission.log 2>&1

# 3. T* of the three, 100 layer-1 draws, River from ns-3 (l1_rank's P+prog-kin-puq-stage-zero-redir-kt-fcd);
#    LM-Tour also with River predicted, as the plan saw it
$PY $T/lm_tour.py score $RUN/REF/$ENV/k8-s1,$RUN/CP/$ENV/k8-s1,$RUN/LM/$ENV/k8-s1 --mode ns3 --out $OUT/score-ns3 \
  > $OUT/score-ns3.log 2>&1
$PY $T/lm_tour.py score $RUN/CP/$ENV/k8-s1,$RUN/LM/$ENV/k8-s1 --mode pred --out $OUT/score-pred \
  > $OUT/score-pred.log 2>&1
cp $RUN/LM/$ENV/k8-s1/lm.json $OUT/lm.json
echo "$ENV done"
