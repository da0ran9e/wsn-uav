#!/bin/bash
# One task of the campaign (CLAUDE.md §8 items 187-188): simulation seed R, channel ENV, map kK-s1.
#   CP   CHORD + River       mission.py, plain CHORD (no --chordTour)
#   LMD  LM-Tour + River     lm_tour.py plan --dtspn --weight cl --wmin 1, its passes in ns-3, River
#   DR   DTSP-N + River      lm_tour.py plan --dtspnRiver, prefly.py (the CH off the path), ns-3, River; paused at the
#                            user's request (item 191, a suspected bug): run only with WITH_DR=1
#   FC + DTSP-N (DN), no broadcast (B1) and oracle (B7): l1_rank on CP's clusters
# Flags and plans as logs/2026-10-27_1800-lm-dtspn/run.sh and run-dr.sh; --runSeed R shifts every ns-3 mission
# index by 10^7 (R - 1), the reception realisations and the block of layer-1 draws (100 per seed).
#   bash task.sh R ENV K
set -e
R=$1; ENV=$2; K=$3
REPO=/home/user/wsn-uav
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
BIN=$S/CAMP-BIN5
C=$S/C4
T=$REPO/uav-l2/tools
HERE=$REPO/logs/2026-10-27_1714-campaign4
OUT=$HERE/score/R$R/$ENV-k$K
FLAGS="--clusters $K --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $ENV --riverRepair 20 --schemes rf --jobs 2 --runSeed $R"
CP=$C/CP/$ENV/R$R/k$K-s1
LMD=$C/LMD/$ENV/R$R/k$K-s1
DR=$C/DR/$ENV/R$R/k$K-s1
mkdir -p $OUT
t0=$(date +%s)
step() { echo "[$(( $(date +%s) - t0 )) s] $*"; }

# CHORD: the map, deploy and tour do not depend on R, so seed R > 1 starts from seed 1's geometry if it is there
CP1=$C/CP/$ENV/R1/k$K-s1
if [ "$R" != 1 ] && [ ! -e $CP/map.json ] && [ -e $HERE/score/R1/$ENV-k$K/done ]; then
  mkdir -p $(dirname $CP)
  cp -a $CP1 $CP
  find $CP -maxdepth 1 \( -name 'pass[0-9]*' -o -name 'r[0-9]*-*' -o -name 'chordfc-*' -o -name 'fc-*' -o -name 'dn-*' \
       -o -name runseed.txt \) -exec rm -f {} +
  step "CP geometry copied from R1"
fi
step "CP mission"
python3 $T/mission.py $FLAGS --work $CP > $OUT/cp-mission.log 2>&1
tail -n 3 $OUT/cp-mission.log

step "LMD plan + mission"
[ -e $LMD/lm.json ] || python3 $T/lm_tour.py plan $CP --out $LMD --R 450 --xi auto --theta 1 --rounds 1 --dtspn \
  --weight cl --wmin 1 > $OUT/lmd-plan.log 2>&1
python3 $T/mission.py $FLAGS --work $LMD > $OUT/lmd-mission.log 2>&1
tail -n 3 $OUT/lmd-mission.log

WORKS=$CP,$LMD
if [ -n "$WITH_DR" ]; then
  step "DR plan + prefly + mission"
  [ -e $DR/lm.json ] || python3 $T/lm_tour.py plan $CP --out $DR --xi auto --dtspnRiver > $OUT/dr-plan.log 2>&1
  python3 $HERE/prefly.py $DR $ENV $K 1 $BIN > $OUT/dr-prefly.log 2>&1
  python3 $T/mission.py $FLAGS --work $DR > $OUT/dr-mission.log 2>&1
  tail -n 3 $OUT/dr-mission.log
  WORKS=$WORKS,$DR
fi

step "score"
python3 $T/lm_tour.py score $WORKS --mode ns3 --out $OUT/score-ns3 > $OUT/score-ns3.log 2>&1
cat $OUT/score-ns3.log
python3 $T/l1_rank.py --set $ENV $CP --draws 100 --jobs 1 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,DN-puq-stage-zero-redir,B1,B7 --out $OUT/l1 > $OUT/l1.log 2>&1
tail -n 2 $OUT/l1.log
cp $LMD/lm.json $OUT/lmd.json
[ -z "$WITH_DR" ] || cp $DR/lm.json $OUT/dr.json

# the pass's per-packet traces are not read by River or the scoring (the bitmaps are)
for w in ${WORKS//,/ }; do rm -f $w/pass*-raw.csv $w/pass*-strip.csv $w/pass*-track.csv; done
step "done"
touch $OUT/done
