#!/bin/bash
# The twelve missions with River --repair (FIX/, river-fix.sh): CHORD with the fountain-coded clue set (-fcd),
# CHORD without it (CHORD-0), FC and DN; 100 layer-1 draws (CLAUDE.md §8 item 169).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0800-chord-win
cd /home/user/wsn-uav
sets=""
for e in r500 r200 r100 open; do sets="$sets --set $e $S/FIX/$e/k8-s1,$S/FIX/$e/k12-s1,$S/FIX/$e/k16-s1"; done
python3 tools/runlog.py $L/score-all.md "python3 uav-l2/tools/l1_rank.py$sets --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,P+prog-kin-puq-stage-zero-redir-kt,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir \
  --out $L/l1rank/all"
W=""; for m in k8 k12 k16; do for e in open r500 r200 r100; do W="$W $S/FIX/$e/$m-s1"; done; done
python3 tools/runlog.py $L/table-all.md "python3 uav-l2/tools/fc_table.py uav-l2/docs/data/results/chord-fc $L/l1rank/all$W"
