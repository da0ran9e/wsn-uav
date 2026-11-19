#!/usr/bin/env bash
# K9 step B4: phase 1 in ns-3 (pass + River, campaign 4's frozen binaries CAMP-BIN5 and flags) on map k8-s1 with the
# critical cells chosen by cc_select.py, to check the River surrogate on sets far from Algorithm 3's.
#
#   b4_run.sh S DATA OUT "CHANNELS" "TAGS" SEED [JOBS]
#
# S:    folder with CAMP-BIN5/ and C4/CP/<channel>/R1/k8-s1 (logs/2026-10-27_1714-campaign4/child-setup.sh)
# DATA: folder with cc_select.py's crit-<channel>-R1-k8-s1-u0.1-rho<rho>.csv
# OUT:  work folders OUT/<channel>/<tag>/ (a copy of the C4 geometry, no plan, pass or River output)
# TAGS: alg3 (Algorithm 3, as campaign 4) or rho<rho> (the set chosen for that rho at a 10 % budget)
set -eu
S=$1; DATA=$2; OUT=$3; CHANNELS=$4; TAGS=$5; SEED=$6; JOBS=${7:-4}
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
one() {
  ch=$1; tag=$2; W=$OUT/$ch/$tag
  if [ ! -e "$W/done" ]; then
    rm -rf "$W"; mkdir -p "$W"
    (cd "$S/C4/CP/$ch/R1/k8-s1" && tar cf - --exclude='plan*.txt' --exclude='plan*.log' --exclude='pass*' \
       --exclude='r[0-9]*-*' --exclude='crit.csv' .) | (cd "$W" && tar xf -)
    crit=; [ "$tag" = alg3 ] || crit="--crit $DATA/crit-$ch-R1-k8-s1-u0.1-${tag}.csv"
    python3 "$REPO/uav-l2/tools/mission.py" --clusters 8 --seed 1 --bin "$S/CAMP-BIN5" --windowKB 400 --windowAt crit \
      --critRing domain --axeNear --kinPass --mapRuns --env "$ch" --riverRepair 20 --schemes rf --jobs 1 \
      --runSeed "$SEED" --work "$W" $crit > "$W/mission.log" 2>&1
    touch "$W/done"
  fi
  echo "$ch $tag: $(grep -c . "$W"/r*-rf-crit.csv | awk -F: '{s += $2 - 1} END {print s}') critical cells run"
}
export -f one; export S DATA OUT SEED REPO
for ch in $CHANNELS; do for t in $TAGS; do echo "$ch $t"; done; done | xargs -P "$JOBS" -L 1 bash -c 'one $0 $1'
