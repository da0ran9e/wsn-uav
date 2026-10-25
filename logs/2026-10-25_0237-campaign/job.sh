#!/bin/bash
# One (set, map) of the final campaign (CLAUDE.md §8 items 160-161), run from /home/user/wsn-uav. Logged by
# tools/runlog.py; one line per job in done.txt. Do not edit while the campaign runs (bash reads it as it goes).
#   P  P*: k-medoids clusters, CHORD-T (FRAC 60 %, CLUE 80 %), River window 400 kB per critical cell; schemes River
#      (rf) and direct pull (d), plus Trickle (t) on seeds 1-10
#   K  layer-2 ablation: the same clusters, the longest line through each CH; River only
# Both: the pass flies team 1's speed profile (--kinPass); ns-3 mission per map and cluster (--mapRuns), shared by
# P and K on one map; frozen binaries in CAMP-BIN.
set -u
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0237-campaign
set_=$1; m=$2; K=${m#k}; K=${K%%-*}; seed=${m##*-s}
B="--clusters $K --seed $seed --bin $S/CAMP-BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass --mapRuns --jobs 2"
case $set_ in
  P) sch=rf,d; [ "$seed" -le 10 ] && sch=rf,d,t
     cmd="python3 uav-l2/tools/mission.py $B --chordTour 0.6,0.8 --schemes $sch --work $S/CAMP/P/$m" ;;
  K) cmd="python3 uav-l2/tools/mission.py $B --schemes rf --work $S/CAMP/K/$m" ;;
esac
mkdir -p $L/$set_
python3 tools/runlog.py $L/$set_/$m.md "$cmd" > /dev/null 2>&1
rc=$?
echo "$set_ $m exit $rc $(date +%H:%M:%S)" >> $L/done.txt
