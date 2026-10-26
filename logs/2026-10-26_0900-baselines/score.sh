#!/bin/bash
# Scoring (CLAUDE.md §8 item 182) on the twelve FIX missions, 100 layer-1 draws, sets named by channel:
#   part 1: CHORD (-fcd), FC, DN, B4 (-kt -fcd: same flight and coding, no River), B1, B7
#   part 2: Pd (direct pull in place of River, -fcd), once pd-run.sh has finished
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-26_0900-baselines
cd /home/user/wsn-uav
sets=""
for e in open r500 r200 r100; do sets="$sets --set $e $S/FIX/$e/k8-s1,$S/FIX/$e/k12-s1,$S/FIX/$e/k16-s1"; done
case "$1" in
  1) python3 tools/runlog.py $L/score-part1.md "python3 uav-l2/tools/l1_rank.py$sets --draws 100 --jobs ${2:-2} \
       --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir,B4-kin-puq-stage-zero-redir-kt-fcd,B1,B7 \
       --out $L/l1rank/part1" ;;
  2) python3 tools/runlog.py $L/score-part2.md "python3 uav-l2/tools/l1_rank.py$sets --draws 100 --jobs ${2:-4} \
       --methods Pd+prog-kin-puq-stage-zero-redir-kt-fcd --out $L/l1rank/part2" ;;
esac
