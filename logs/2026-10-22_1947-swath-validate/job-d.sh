#!/bin/bash
# Direct pull (kéo thẳng) River runs on the CHORD-T 0.6/0.8 work folders (CLAUDE.md §8 item 136), from uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1947-swath-validate
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/CT1d-$m.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/VA/CT1-$m --bin $S/BIN --jobs 2 --schemes d --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8" > /dev/null 2>&1
echo "CT1d $m exit $? $(date +%H:%M:%S)" >> $L/done-d.txt
