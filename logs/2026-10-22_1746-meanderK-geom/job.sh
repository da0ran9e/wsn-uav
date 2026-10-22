#!/bin/bash
# MEANDER-K geometry (CLAUDE.md §8 items 118, 134): partition, deploy (roles, routes), curve; no pass, no River.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1746-meanderK-geom
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/$m.md "python3 tools/meander_mission.py --clusters $K --seed $seed --work $S/MKW/$m --bin $S/BIN --jobs 1 --meanderK --windowKB 400 --geometry" > /dev/null 2>&1
echo "$m exit $? $(date +%H:%M:%S)" >> $L/done.txt
