#!/bin/bash
# CLAUDE.md §8 item 194: model-level estimate of the fixed DTSP-N + River on one cell (seed 1) while its ns-3 run
# waits in the campaign: its plan (C4/DRT, not the campaign's C4/DR) and T* with River predicted
# (lm_tour.py score --mode pred), for DRT and, as a check of the model against ns-3, for CHORD (CP) and LM-Tour (LMD).
#   bash est.sh ENV K
set -e
ENV=$1; K=$2
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/C4
T=/home/user/wsn-uav/uav-l2/tools
OUT=/home/user/wsn-uav/logs/2026-10-28_0310-dtspn-fix/est/$ENV-k$K
mkdir -p $OUT
[ -e $S/DRT/$ENV/R1/k$K-s1/lm.json ] || python3 $T/lm_tour.py plan $S/CP/$ENV/R1/k$K-s1 --out $S/DRT/$ENV/R1/k$K-s1 \
  --xi auto --dtspnRiver > $OUT/plan.log 2>&1
tail -n 1 $OUT/plan.log 2>/dev/null || true
python3 $T/lm_tour.py score $S/CP/$ENV/R1/k$K-s1,$S/LMD/$ENV/R1/k$K-s1,$S/DRT/$ENV/R1/k$K-s1 --mode pred \
  --out $OUT/score-pred > $OUT/score-pred.log 2>&1
cat $OUT/score-pred.log
