#!/bin/bash
# CHORD-T (CLAUDE.md §8 item 136): k-medoids clusters, bearings chosen jointly with the tour; copy of the k-medoids
# run of the same map (deploy and pass reused where the bearing stays), from uav-l2/.  Args: TAG FRAC,CLUE MAP
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1947-swath-validate
t=$1; fc=$2; m=$3; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
W=$S/VA/$t-$m
rm -rf $W && cp -a $(readlink -f $S/VA/KD-$m)/. $W && rm -f $W/plan*.txt $W/plan*.log $W/r*-rf* $W/tour.json
python3 ../tools/runlog.py $L/$t-$m.md "python3 tools/mission.py --clusters $K --seed $seed --work $W --bin $S/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour $fc" > /dev/null 2>&1
echo "$t $m exit $? $(date +%H:%M:%S)" >> $L/done-ct.txt
