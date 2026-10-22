#!/bin/bash
# Cross-check of SWATH-K (lane 6) against k-medoids on two more random maps (CLAUDE.md §8 item 135), from uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1806-propose-iter
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
python3 ../tools/runlog.py $L/r4-$m-kmedoids.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/IT/KD-$m --bin $S/BIN --jobs 1 --schemes rf --windowKB 400 --windowAt crit --critRing domain" > /dev/null 2>&1
python3 ../tools/runlog.py $L/r4-$m-swath.md "python3 tools/swath_mission.py --clusters $K --seed $seed --work $S/IT/SW-$m --bin $S/BIN --jobs 1" > /dev/null 2>&1
echo "$m done $(date +%H:%M:%S)" >> $L/check-done.txt
