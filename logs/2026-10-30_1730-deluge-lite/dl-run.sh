#!/bin/bash
# One (regime, seed) of the Deluge-lite experiment (SigDrop 2 backup design): map k12-s1, the LM-Tour tour of
# campaign 4 (lm_tour.py plan --dtspn --weight cl --wmin 1 on the CHORD geometry), simulation seed R. River (rf)
# always first, then the Trickle scheme TAG (dla: Imin 0.5 s, Imax 8 s; dlb: 2 s, 60 s; both Trickle over every
# cell of the cluster, k = 1, 64-packet pages broken at image and Seg starts). Exports results/<REG>-R<R>-<TAG>.
#   CAMP_S=<scratchpad> bash dl-run.sh REG R [TAG]      (TAG omitted: River only)
set -e
REG=$1; R=$2; TAG=${3:-}
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
T=$L/../../uav-l2/tools
BIN=$CAMP_S/CAMP-BIN9
CP=$CAMP_S/DL/CP/$REG/R$R/k12-s1
W=$CAMP_S/DL/LMD/$REG/R$R/k12-s1
O=$L/results
mkdir -p $O
if [ ! -d $CP ]; then
  mkdir -p $(dirname $CP)
  cp -a $CAMP_S/C4/CP/$REG/R1/k12-s1 $CP
  [ "$R" = 1 ] || echo $R > $CP/runseed.txt
fi
FLAGS="--clusters 12 --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $REG --riverRepair 20 --jobs ${JOBS:-4} --runSeed $R"
t0=$(date +%s)
[ -e $W/lm.json ] || python3 $T/lm_tour.py plan $CP --out $W --R 450 --xi auto --theta 1 --rounds 1 --dtspn \
  --weight cl --wmin 1 > $O/$REG-R$R-plan.log 2>&1
echo "[$(( $(date +%s) - t0 )) s] $REG R$R rf"
python3 $T/mission.py $FLAGS --schemes rf --work $W > $O/$REG-R$R-rf-mission.log 2>&1
grep -c "river-full" $O/$REG-R$R-rf-mission.log || tail -3 $O/$REG-R$R-rf-mission.log
python3 $L/dl_export.py $W $REG $R rf $O/$REG-R$R-rf
if [ -n "$TAG" ]; then
  python3 $T/page_breaks.py $W > $O/$REG-R$R-page-breaks.log
  echo "[$(( $(date +%s) - t0 )) s] $REG R$R $TAG"
  python3 $T/mission.py $FLAGS --schemes $TAG --work $W > $O/$REG-R$R-$TAG-mission.log 2>&1
  grep -E "^  run .*trickle" $O/$REG-R$R-$TAG-mission.log || tail -3 $O/$REG-R$R-$TAG-mission.log
  python3 $L/dl_export.py $W $REG $R $TAG $O/$REG-R$R-$TAG
fi
echo "[$(( $(date +%s) - t0 )) s] $REG R$R ${TAG:-rf} done"
