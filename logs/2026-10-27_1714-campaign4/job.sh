#!/bin/bash
# One job of the campaign's queue (CLAUDE.md §8 item 199): scheme SCH (cp, lmd or dr) on simulation seed R, channel
# ENV, map kK-s1. task.sh ran the three schemes of a cell one after the other with --jobs 2, which left cores idle
# in the Python steps and the tail of each mission; here every job is one mission with --jobs 1 and camp2.sh keeps
# four of them running, seeds and schemes mixed. Same flags, plans and scores as task.sh; the CP geometry of R > 1 is
# prepared by camp2.sh, so the three schemes of a cell can start together.
#   cp   CHORD + River: mission; lm_tour score -> score-cp.csv; l1_rank (CHORD check, FC + DTSP-N, B1, B7)
#   lmd  LM-Tour + River: plan, mission, lm_tour score -> score-lmd.csv
#   dr   DTSP-N + River: plan, prefly.py, mission, lm_tour score -> score-dr.csv
# Markers done-cp, done-lmd, done-dr (done from task.sh stands for done-cp and done-lmd).
# Several sessions share the seeds (item 201): assigned/R<R> names the session (CAMP_ID, main here) that runs seed
# R; another session's seed exits 3 at once. CAMP_S is the session's scratchpad (binaries in CAMP-BIN5, runs in C4).
#   bash job.sh SCH R ENV K
set -e
SCH=$1; R=$2; ENV=$3; K=$4
REPO=$(cd "$(dirname "$0")/../.." && pwd)
S=${CAMP_S:-/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad}
BIN=$S/CAMP-BIN5
C=$S/C4
T=$REPO/uav-l2/tools
HERE=$REPO/logs/2026-10-27_1714-campaign4
OUT=$HERE/score/R$R/$ENV-k$K
FLAGS="--clusters $K --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env $ENV --riverRepair 20 --schemes rf --jobs 1 --runSeed $R"
CP=$C/CP/$ENV/R$R/k$K-s1
LMD=$C/LMD/$ENV/R$R/k$K-s1
DR=$C/DR/$ENV/R$R/k$K-s1
if [ -e $HERE/assigned/R$R ] && [ "$(cat $HERE/assigned/R$R)" != "${CAMP_ID:-main}" ]; then exit 3; fi
# the same job already running (a queue restarted around it): leave it to that one
if pgrep -f "job.sh $SCH $R $ENV $K\$" | grep -vqx -e "$$" -e "$PPID"; then exit 4; fi
mkdir -p $OUT
if [ -e $OUT/done-$SCH ] || { [ "$SCH" != dr ] && [ -e $OUT/done ]; }; then exit 0; fi
t0=$(date +%s)
step() { echo "[$(( $(date +%s) - t0 )) s] $SCH: $*"; }

case $SCH in
cp)
  step "mission"
  python3 $T/mission.py $FLAGS --work $CP > $OUT/cp-mission.log 2>&1
  tail -n 2 $OUT/cp-mission.log
  step "score"
  python3 $T/lm_tour.py score $CP --mode ns3 --out $OUT/score-cp > $OUT/score-cp.log 2>&1
  cat $OUT/score-cp.log
  python3 $T/l1_rank.py --set $ENV $CP --draws 100 --jobs 1 \
    --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,DN-puq-stage-zero-redir,B1,B7 --out $OUT/l1 > $OUT/l1.log 2>&1
  tail -n 1 $OUT/l1.log
  W=$CP ;;
lmd)
  step "plan + mission"
  [ -e $LMD/lm.json ] || python3 $T/lm_tour.py plan $CP --out $LMD --R 450 --xi auto --theta 1 --rounds 1 --dtspn \
    --weight cl --wmin 1 > $OUT/lmd-plan.log 2>&1
  python3 $T/mission.py $FLAGS --work $LMD > $OUT/lmd-mission.log 2>&1
  tail -n 2 $OUT/lmd-mission.log
  step "score"
  python3 $T/lm_tour.py score $LMD --mode ns3 --out $OUT/score-lmd > $OUT/score-lmd.log 2>&1
  cat $OUT/score-lmd.log
  cp $LMD/lm.json $OUT/lmd.json
  W=$LMD ;;
dr)
  step "plan + prefly + mission"
  [ -e $DR/lm.json ] || python3 $T/lm_tour.py plan $CP --out $DR --xi auto --dtspnRiver > $OUT/dr-plan.log 2>&1
  python3 $HERE/prefly.py $DR $ENV $K 1 $BIN > $OUT/dr-prefly.log 2>&1
  python3 $T/mission.py $FLAGS --work $DR > $OUT/dr-mission.log 2>&1
  tail -n 2 $OUT/dr-mission.log
  step "score"
  python3 $T/lm_tour.py score $DR --mode ns3 --out $OUT/score-dr > $OUT/score-dr.log 2>&1
  cat $OUT/score-dr.log
  cp $DR/lm.json $OUT/dr.json
  W=$DR ;;
esac
# the pass's per-packet traces are not read by River or the scoring (the bitmaps are)
rm -f $W/pass*-raw.csv $W/pass*-strip.csv $W/pass*-track.csv
touch $OUT/done-$SCH
step "done"
