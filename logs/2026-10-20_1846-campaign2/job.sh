#!/bin/bash
# One (set, map) of the round-2 campaign (CLAUDE.md §8 item 114), run from uav-l2/. Logged by tools/runlog.py.
#   KF  k-medoids, full D (only k2-s3 is new: its saved copy has no pass bitmaps)
#   KW  k-medoids, River window 400 kB (River again on a copy of KF: the pass bitmaps are reused)
#   SW  subCH baseline: KF's clusters split around critical cells >= 6 cells apart, window 400 kB
#   MW  MEANDER (layer 2), window 400 kB
#   LW  LANE 4.5 (layer 2), window 400 kB
set -u
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
L=/home/user/wsn-uav/logs/2026-10-20_1846-campaign2
set_=$1; m=$2; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
# LANE dropped at 19:12 to save about 2.5 h of machine time: on k4-s2 / k6-s4 / k8-s4 it trailed k-medoids and
# MEANDER (round 1); its three maps stay in LW through the links to MLw
[ "$set_" = LW ] && { echo "$set_ $m skipped $(date +%H:%M:%S)" >> $L/done.txt; exit 0; }
B="--bin $S/BIN --jobs 2 --schemes rf"
case $set_ in
  KF) cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/KF/$m $B" ;;
  KW) if [ ! -e $S/KW/$m ]; then
        cp -a $S/KF/$m/. $S/KW/$m.tmp && rm -f $S/KW/$m.tmp/plan*.txt $S/KW/$m.tmp/plan*.log $S/KW/$m.tmp/r*-rf-* $S/KW/$m.tmp/r*-rf.log && mv $S/KW/$m.tmp $S/KW/$m
      fi
      cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/KW/$m $B --windowKB 400" ;;
  SW) cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/SW/$m $B --partition subch --src $S/KF/$m --windowKB 400" ;;
  MW) cmd="python3 tools/meander_mission.py --clusters $K --seed $seed --work $S/MW/$m --bin $S/BIN --jobs 2 --windowKB 400" ;;
  LW) cmd="python3 tools/mission.py --clusters $K --seed $seed --work $S/LW/$m $B --partition lane --lane 4.5 --windowKB 400" ;;
esac
mkdir -p $L/$set_
python3 ../tools/runlog.py $L/$set_/$m.md "$cmd" > /dev/null 2>&1
rc=$?
echo "$set_ $m exit $rc $(date +%H:%M:%S)" >> $L/done.txt
