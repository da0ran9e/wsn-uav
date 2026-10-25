#!/bin/bash
# Round trip of one archive (item 167): unpack r200-k8-s1, run its mission.py command again (only the pass bitmaps
# are missing, so only the ns-3 pass runs), and check the bitmaps, plans and River results against the originals.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
cd /home/user/wsn-uav
nice python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin $S/CAMP-BIN3 --windowKB 400 --windowAt crit \
  --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env r200 --schemes rf,d --jobs 1 \
  --work $S/RT/k8-s1 > /dev/null 2>&1; echo "mission.py exit $?"
cd $S/RT/k8-s1
for f in pass*-bits-r8*.bin plan*.txt r*-rf-crit.csv r*-d-crit.csv; do
  cmp -s $f $S/ENV/r200/k8-s1/$f && echo "same $f" || echo "DIFFERS $f"
done | sort | uniq -c -w 4
