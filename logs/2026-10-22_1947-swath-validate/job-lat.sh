#!/bin/bash
# SWATH-K with --routeBy latency (route over the likely critical cells earliest), same maps; from uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1947-swath-validate
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/SWL-$m.md "python3 tools/swath_mission.py --clusters $K --seed $seed --work $S/VA/SWL-$m --bin $S/BIN --jobs 2 --axeNear --routeBy latency" > /dev/null 2>&1
echo "SWL $m exit $? $(date +%H:%M:%S)" >> $L/done-lat.txt
