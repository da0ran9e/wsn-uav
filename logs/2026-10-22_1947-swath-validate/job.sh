#!/bin/bash
# SWATH-K vs k-medoids (CLAUDE.md §8 items 135-136), both with --critRing domain, --axeNear, --windowAt crit; from uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1947-swath-validate
p=$1; m=$2; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
if [ $p = KD ]; then
  cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/VA/KD-$m --bin $S/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear"
else
  cmd="python3 tools/swath_mission.py --clusters $K --seed $seed --work $S/VA/SW-$m --bin $S/BIN --jobs 2 --axeNear"
fi
python3 ../tools/runlog.py $L/$p-$m.md "$cmd" > /dev/null 2>&1
echo "$p $m exit $? $(date +%H:%M:%S)" >> $L/done.txt
