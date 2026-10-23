#!/bin/bash
# subCH-K with the P* configuration (CLAUDE.md §8 items 114, 118, 139): the K/2 k-medoids clusters of HK/<map>
# split in two; pass and River (rf) on ns-3. Work folder named by the map (paired worlds in l1_rank).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-23_0706-baselines
m=$1; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
cd /home/user/wsn-uav/uav-l2
python3 ../tools/runlog.py $L/SK-$m.md "python3 tools/mission.py --clusters $K --seed $seed --work $S/SK/$m --bin $S/BIN --jobs 2 --schemes rf --partition subch --pairs --src $S/HK/$m --windowKB 400 --windowAt crit --critRing domain --axeNear" > /dev/null 2>&1
echo "SK $m exit $? $(date +%H:%M:%S)" >> $L/done-subch.txt
