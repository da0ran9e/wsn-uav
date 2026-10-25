#!/bin/bash
# River again with --repair 20 (CLAUDE.md §8 item 169) on the twelve CHORD missions of items 166-168: each mission
# folder copied to FIX/<channel>/<map> without its River (rf) results, then mission.py with the same options and
# CAMP-BIN4 (river-bin with --repair); only River runs (map, plans and pass bitmaps are kept). Two at a time.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0800-chord-win
cd /home/user/wsn-uav
src() { [ $1 = open ] && { [ $2 = 8 ] && echo $S/CTRY/P/k8-s1 || echo $S/ANIM/k$2-s1; } || echo $S/ENV/$1/k$2-s1; }
one() {   # ENV K
  local w=$S/FIX/$1/k$2-s1
  mkdir -p $S/FIX/$1 && rm -rf $w && cp -a $(src $1 $2) $w
  rm -rf $w/tr $w/r*-rf-* $w/r*-rf.log $w/fc-* $w/dn-* $w/chordfc-*
  python3 tools/runlog.py $L/fix-$1-k$2-s1.md "python3 uav-l2/tools/mission.py --clusters $2 --seed 1 --bin $S/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env $1 --riverRepair 20 --schemes rf --jobs 2 --work $w" > /dev/null 2>&1
  echo "$1 k$2 exit $? $(date +%H:%M:%S)" >> $L/fix-done.txt
}
for p in "r100 16:r100 12" "r200 16:r200 12" "r100 8:r200 8" "r500 16:r500 12" "r500 8:open 16" "open 12:open 8"; do
  one ${p%%:*} & one ${p##*:} & wait
done
echo "all done $(date +%H:%M:%S)" >> $L/fix-done.txt
