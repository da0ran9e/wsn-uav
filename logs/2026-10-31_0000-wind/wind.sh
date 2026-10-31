#!/bin/bash
# Trajectory error (CLAUDE.md §8 item 241): River plans on the planned CHORD path, the pass flies a wind-perturbed
# one (wind_path.py, cross-track sd SIGMA m). Map k8-s1, r100, seed R; scheme rf (River); WITH_TP=1 adds tp (Deluge, plan-free).
#   CAMP_S=<scratchpad> bash wind.sh R SIGMA
set -e
R=$1; SIG=$2
: "${CAMP_S:?set CAMP_S}"
L=$(cd "$(dirname "$0")" && pwd)
T=$L/../../uav-l2/tools
BIN=$CAMP_S/CAMP-BINW   # CAMP-BIN6 with pass-bin rebuilt with --offPlan (same bits on the planned path)
W=$CAMP_S/WIND/s$SIG/R$R/k8-s1
OUT=$L/results/s$SIG-R$R
mkdir -p $OUT
[ -d $W ] || { mkdir -p $(dirname $W); cp -a $CAMP_S/C4/CP/r100/R1/k8-s1 $W; [ "$R" = 1 ] || echo $R > $W/runseed.txt; }
LOSS=$(python3 -c "import sys; sys.path.insert(0,'$T'); from mission import ENV_LOSS; print(ENV_LOSS['r100'])")
cd $W
for k in 1 2 3 4 5 6 7 8; do
  RUN=$((800100 + k + 10000000 * (R - 1)))
  [ -e pass$k-bits-r1.bin ] && continue
  python3 $T/wind_path.py c$k-path-s35.csv c$k-path-wind.csv $SIG $((1000 * k + R)) >> $OUT/wind-paths.txt
  LD_LIBRARY_PATH=$BIN/pass-lib $BIN/pass-bin --nodes=c$k-nodes-s35.csv --path=c$k-path-wind.csv --speed=80 --offPlan=true \
    --firstRun=$RUN --runs=1 --bits --out=pass$k --lossDb=$LOSS > pass$k.log 2>&1 &
  [ $(jobs -r | wc -l) -ge ${JOBS:-4} ] && wait -n
done
wait
for k in 1 2 3 4 5 6 7 8; do RUN=$((800100 + k + 10000000 * (R - 1))); [ -e pass$k-bits-r1.bin ] || ln -s pass$k-bits-r$RUN.bin pass$k-bits-r1.bin; done
FLAGS="--clusters 8 --seed 1 --bin $BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass
       --mapRuns --env r100 --riverRepair 20 --jobs ${JOBS:-4} --runSeed $R"
python3 $T/mission.py $FLAGS --schemes rf --work $W > $OUT/rf-mission.log 2>&1
if [ -n "$WITH_TP" ]; then   # Deluge as the plan-free control, only when asked
  python3 $T/page_breaks.py $W > /dev/null
  python3 $T/mission.py $FLAGS --schemes tp --work $W > $OUT/tp-mission.log 2>&1
fi
cp $W/r*-rf-*.csv $OUT/; [ -z "$WITH_TP" ] || cp $W/r*-tp-*.csv $OUT/
touch $OUT/done
