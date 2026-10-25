#!/bin/bash
# CHORD (P*) and FC on k8/k12/k16-s1 in r500, r200, r100 (+ open for reference), 100 layer-1 draws (item 166).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0600-fc-baseline
cd /home/user/wsn-uav
python3 tools/runlog.py $L/score-all.md "python3 uav-l2/tools/l1_rank.py \
  --set r500 $S/ENV/r500/k8-s1,$S/ENV/r500/k12-s1,$S/ENV/r500/k16-s1 \
  --set r200 $S/ENV/r200/k8-s1,$S/ENV/r200/k12-s1,$S/ENV/r200/k16-s1 \
  --set r100 $S/ENV/r100/k8-s1,$S/ENV/r100/k12-s1,$S/ENV/r100/k16-s1 \
  --set open $S/CTRY/P/k8-s1,$S/ANIM/k12-s1,$S/ANIM/k16-s1 \
  --draws 100 --jobs 4 --methods P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir --out $L/l1rank/all"
