#!/bin/bash
# One seed of the reviewer upgrade (CLAUDE.md §8 item 211): ground transport on the fixed CHORD passes of map k8-s1,
# channel r100, simulation seed R. Schemes: rf (River, campaign 4's), d (direct pull), t (Trickle/Deluge on River's
# plan cells), tp (Trickle only on the Axe, critical and direct-pull path cells); Trickle pages aligned to the clue
# images (page_breaks.py). Binaries: CAMP-BIN6 = campaign 4's CAMP-BIN5 with river-bin rebuilt with the per-node
# PHY state counters (-energy.csv), --tScope and --pageBreaks (same River/direct behaviour, checked on seed 1).
#   CAMP_S=<scratchpad> bash run.sh R [SCHEMES]      (SCHEMES default d,t,tp; rf always first)
set -e
R=$1; SCH=${2:-d,t,tp}
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$L/../.." && pwd)
T=$REPO/uav-l2/tools
BIN=$CAMP_S/CAMP-BIN6
W=$CAMP_S/DT/r100/R$R/k8-s1
OUT=$L/results/R$R
mkdir -p $OUT
if [ ! -d $W ]; then
  mkdir -p $(dirname $W)
  cp -a $CAMP_S/C4/CP/r100/R1/k8-s1 $W
  [ "$R" = 1 ] || echo $R > $W/runseed.txt
fi
FLAGS="--clusters 8 --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env r100 --riverRepair 20 --jobs ${JOBS:-4} --runSeed $R"
t0=$(date +%s)
echo "[0 s] R$R rf"
python3 $T/mission.py $FLAGS --schemes rf --work $W > $OUT/rf-mission.log 2>&1
grep "river-full" $OUT/rf-mission.log || tail -3 $OUT/rf-mission.log
python3 $T/page_breaks.py $W > $OUT/page-breaks.log
echo "[$(( $(date +%s) - t0 )) s] R$R $SCH"
python3 $T/mission.py $FLAGS --schemes $SCH --work $W > $OUT/other-mission.log 2>&1
grep -E "^  run " $OUT/other-mission.log || tail -3 $OUT/other-mission.log
cp $W/r*-*-crit.csv $W/r*-*-runs.csv $W/r*-*-energy.csv $W/pages*.txt $OUT/ 2>/dev/null || true
for f in $W/r*-t*.log $W/r*-d.log; do grep -h "^trickle:" $f 2>/dev/null | sed "s|^|$(basename $f): |"; done > $OUT/trickle-pages.txt || true
echo "[$(( $(date +%s) - t0 )) s] R$R done"
touch $OUT/done
