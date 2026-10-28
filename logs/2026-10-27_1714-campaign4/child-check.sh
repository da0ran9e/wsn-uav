#!/bin/bash
# Check a campaign session (CLAUDE.md §8 item 201): CHORD + River on seed 1, 1 km, k8 flown again here must give the
# T* of the main session's run (score/R1/open-k8/score-ns3.csv) on every one of its 100 draws.
#   CAMP_S=<scratchpad> bash child-check.sh
set -e
: "${CAMP_S:?}"
L=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$L/../.." && pwd)
T=$REPO/uav-l2/tools
W=$CAMP_S/CHECK/open/k8-s1
rm -rf "${W:?}"
mkdir -p "$(dirname "$W")"
cp -a "$CAMP_S/C4/CP/open/R1/k8-s1" "$W"
python3 $T/mission.py --clusters 8 --seed 1 --bin $CAMP_S/CAMP-BIN5 --windowKB 400 --windowAt crit --critRing domain \
  --axeNear --kinPass --mapRuns --env open --riverRepair 20 --schemes rf --jobs 4 --work $W > $CAMP_S/check-mission.log 2>&1
python3 $T/lm_tour.py score $W --mode ns3 --out $CAMP_S/check-cp > $CAMP_S/check-score.log 2>&1
python3 - "$L/score/R1/open-k8/score-ns3.csv" "$CAMP_S/check-cp.csv" <<'PY'
import csv, sys
ref = {r["draw"]: float(r["Tstar"]) for r in csv.DictReader(open(sys.argv[1])) if "/CP/" in r["work"]}
got = {r["draw"]: float(r["Tstar"]) for r in csv.DictReader(open(sys.argv[2]))}
bad = [d for d in ref if abs(ref[d] - got.get(d, -1)) > 0.05]
print(f"CHECK {'OK' if not bad and len(got) == len(ref) == 100 else 'FAIL'}: {len(ref)} draws, {len(bad)} differ")
sys.exit(1 if bad or len(got) != len(ref) else 0)
PY
