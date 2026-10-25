#!/bin/bash
# P* (CHORD-T) on k12-s1 and k16-s1 in the three item-163 channels (CLAUDE.md §8 item 166), River only; k8-s1 has
# them already (logs/2026-10-25_0330-env-modes). Two missions at a time, the harshest channel first.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0600-fc-baseline
cd /home/user/wsn-uav
run() { python3 tools/runlog.py $L/P-$2-k$1-s1.md "python3 uav-l2/tools/mission.py --clusters $1 --seed 1 --bin $S/CAMP-BIN3 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env $2 --schemes rf --jobs 2 --work $S/ENV/$2/k$1-s1" > /dev/null 2>&1; echo "$2 k$1 exit $? $(date +%H:%M:%S)" >> $L/done.txt; }
for e in r100 r200 r500; do run 12 $e & run 16 $e & wait; done
echo "all done $(date +%H:%M:%S)" >> $L/done.txt
