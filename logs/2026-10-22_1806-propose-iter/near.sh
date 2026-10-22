#!/bin/bash
# Round 5 (CLAUDE.md §8 item 135): River again with --axeNear (pass bitmaps reused), k-medoids and SWATH-K, from uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-22_1806-propose-iter
p=$1; m=$2; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
if [ $p = KD ]; then
  cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/IT/KDN-$m --bin $S/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear"
else
  cmd="python3 tools/swath_mission.py --clusters $K --seed $seed --work $S/IT/SWN-$m --bin $S/BIN --jobs 2 --axeNear"
fi
python3 ../tools/runlog.py $L/r5-$p-$m.md "$cmd" > /dev/null 2>&1
echo "$p $m exit $? $(date +%H:%M:%S)" >> $L/near-done.txt
