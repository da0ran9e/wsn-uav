#!/bin/bash
# Trickle baseline runs (CLAUDE.md §8 items 134, 139) on the CHORD-T 0.6/0.8 work folders, binary BIN2/river-bin
# (coop2-river.cc with --scheme=trickle; its River output equals BIN/river-bin's, regress-river.md).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-23_0706-baselines
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/CT1t-$m.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/VA/CT1-$m --bin $S/BIN2 --jobs 2 --schemes t --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8" > /dev/null 2>&1
echo "CT1t $m exit $? $(date +%H:%M:%S)" >> $L/done-trickle.txt
