#!/bin/bash
# MEANDER-K with the P* configuration (CLAUDE.md §8 items 118, 134, 140): exactly K clusters on curved lanes,
# local Banks; pass and River (rf). Work folder named by the map (paired worlds in l1_rank).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-23_0706-baselines
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/MK-$m.md "python3 tools/meander_mission.py --clusters $K --seed $seed --work $S/MK16/$m --bin $S/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear" > /dev/null 2>&1
echo "MK $m exit $? $(date +%H:%M:%S)" >> $L/done-meanderK.txt
