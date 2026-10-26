#!/bin/bash
# Direct pull (River's scheme d, baseline Pd; CLAUDE.md §8 item 182) on the twelve FIX missions with CAMP-BIN4:
# mission.py with the same options as River's re-run (logs/2026-10-25_0800-chord-win/river-fix.sh) and --schemes d;
# only the d runs are missing, so only they run (map, plans, pass bitmaps and River results are kept). The k8
# folders already hold d runs made with CAMP-BIN3 (whose river-bin differs only by --repair, off for d): one of them
# (r200 k8-s1, cluster 1) is re-run with CAMP-BIN4 in a copy to check they are the same. Four at a time (xargs).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-26_0900-baselines
cd /home/user/wsn-uav
one() {   # ENV K [WORK]
  local w=${3:-$S/FIX/$1/k$2-s1}
  python3 tools/runlog.py $L/pd-$1-k$2-s1$4.md "python3 uav-l2/tools/mission.py --clusters $2 --seed 1 --bin $S/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env $1 --riverRepair 20 --schemes d --jobs 1 --work $w" > /dev/null 2>&1
  echo "$1 k$2$4 exit $? $(date +%H:%M:%S)" >> $L/pd-done.txt
}
V=$S/PDCHECK/k8-s1; rm -rf $S/PDCHECK; mkdir -p $S/PDCHECK && cp -a $S/FIX/r200/k8-s1 $V && rm -f $V/r1-d-*
export -f one; export S L V
printf "%s\n" "r200 8 $V -check" "r100 16" "r200 16" "r500 16" "open 16" "r100 12" "r200 12" "r500 12" "open 12" | \
  xargs -P 4 -L 1 bash -c 'one $0 $1 $2 $3'
echo "all done $(date +%H:%M:%S)" >> $L/pd-done.txt
