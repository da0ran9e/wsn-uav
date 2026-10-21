#!/bin/bash
# Item 116: the best adjusted MEANDER (lanes 7.5 cells, fragments under 0.5 x 80 cells merged) through ns-3 (pass,
# River window 400 kB) on the 40 maps, from its geometry-only folders (the stages resume). Two maps at a time,
# two ns-3 jobs each. Log per map in ns3/<map>.md. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
L=/home/user/wsn-uav/logs/2026-10-21_0110-l2-adjust
mkdir -p $L/ns3
ls $S/MG/L7.5f0.5 | xargs -P 2 -I{} bash -c '
  m={}; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
  python3 ../tools/runlog.py '$L'/ns3/$m.md "python3 tools/meander_mission.py --clusters $K --seed $seed --work '$S'/MG/L7.5f0.5/$m --bin '$S'/BIN --jobs 2 --windowKB 400 --lane 7.5 --frag 0.5" --cwd . > /dev/null 2>&1
  echo "$m exit $? $(date +%H:%M:%S)" >> '$L'/ns3/done.txt'
echo "all done $(date +%H:%M:%S)" >> $L/ns3/done.txt
