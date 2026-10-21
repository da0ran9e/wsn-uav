#!/bin/bash
# Item 116, adjustments 2-3, geometry only (no ns-3): MEANDER with lane width L (cells) and fragment threshold F
# (x 80 cells) on the 40 campaign maps, meander_mission.py --geometry (map, deploy: CH and critical cells, the
# real curved paths). L4.5f0.25 is the campaign's MEANDER (MW), as a check. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
for cfg in "4.5 0.25" "6 0.25" "7.5 0.25" "9 0.25" "4.5 0.5" "6 0.5" "7.5 0.5" "9 0.5"; do
  set -- $cfg
  for w in $S/KW/k*; do
    m=$(basename $w); K=${m#k}; K=${K%%-*}; seed=${m##*-s}
    python3 tools/meander_mission.py --clusters $K --seed $seed --work $S/MG/L$1f$2/$m --bin $S/BIN --jobs 2 \
        --windowKB 400 --lane $1 --frag $2 --geometry > /dev/null 2>&1 || echo "FAIL L$1 f$2 $m"
  done
  echo "L$1 f$2 done $(date +%H:%M:%S)"
done
