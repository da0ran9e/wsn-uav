#!/bin/bash
# subCH-K geometry (CLAUDE.md §8 items 118, 134): k-medoids with K/2 clusters (HK), each split in two (SKW); no pass, no River.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1750-subchK-geom
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/$m-half.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/HK/$m --bin $S/BIN --count $((K / 2)) --geometry" > /dev/null 2>&1  && python3 ../tools/runlog.py $L/$m.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/SKW/$m --bin $S/BIN --partition subch --pairs --src $S/HK/$m --windowKB 400 --geometry" > /dev/null 2>&1
echo "$m exit $? $(date +%H:%M:%S)" >> $L/done.txt
