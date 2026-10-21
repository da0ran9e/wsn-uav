#!/bin/bash
# One MEANDER configuration (lane width $1 cells, fragment threshold $2 x 80 cells) on the 40 maps, geometry only.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
for w in $S/KW/k*; do
  m=$(basename $w); K=${m#k}; K=${K%%-*}; seed=${m##*-s}
  python3 tools/meander_mission.py --clusters $K --seed $seed --work $S/MG/L$1f$2/$m --bin $S/BIN --jobs 2 \
      --windowKB 400 --lane $1 --frag $2 --geometry > /dev/null 2>&1 || echo "FAIL L$1 f$2 $m"
done
echo "L$1 f$2 done $(date +%H:%M:%S)"
