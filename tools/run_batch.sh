#!/usr/bin/env bash
# Batch runner for the SAR experiment. Runs N seeds x 3 schemes, collects every
# metrics.csv into one summary, and prints per-scheme aggregates.
#
# Usage (run from the ns-3 root that contains build/):
#   bash src/wsn-uav/tools/run_batch.sh [NSEEDS] [GRID] [NUMUAV] [NUMFRAG] [MAXFRAGB] [SIMTIME]
# Defaults: 100 seeds, grid 6, 4 UAVs, 8 frags, 4000 B, simTime 600.
set -u

NSEEDS=${1:-100}
GRID=${2:-6}
NUMUAV=${3:-4}
NUMFRAG=${4:-8}
MAXFRAGB=${5:-4000}
SIMTIME=${6:-600}

EXE="./build/src/wsn-uav/examples/ns3.46-scenario-sar-default"
if [[ ! -x "$EXE" ]]; then echo "exe not found: $EXE (build first)"; exit 1; fi

OUT="data/results/scenario-sar"
SUMMARY="$OUT/summary.csv"
mkdir -p "$OUT"
: > "$SUMMARY"
HEADER_DONE=0

echo "Running $NSEEDS seeds x {proposed,nocoop,single} ..."
for ((s=1; s<=NSEEDS; s++)); do
  for sch in proposed nocoop single; do
    "$EXE" --gridSize=$GRID --numUav=$NUMUAV --numFrag=$NUMFRAG \
           --maxFragBytes=$MAXFRAGB --seed=$s --scheme=$sch --simTime=$SIMTIME \
           >/dev/null 2>&1
    M="$OUT/$sch/run-$s/metrics.csv"
    if [[ -f "$M" ]]; then
      if [[ $HEADER_DONE -eq 0 ]]; then head -1 "$M" >> "$SUMMARY"; HEADER_DONE=1; fi
      tail -n +2 "$M" >> "$SUMMARY"
    fi
  done
  if (( s % 10 == 0 )); then echo "  ... $s/$NSEEDS seeds done"; fi
done

echo "Summary written: $SUMMARY"
echo ""
python3 - "$SUMMARY" <<'PY'
import csv, sys, statistics as st
rows=list(csv.DictReader(open(sys.argv[1])))
schemes={}
for r in rows:
    schemes.setdefault(r['scheme'],[]).append(r)
print(f"{'scheme':<10} {'runs':>5} {'compl%':>7} {'t_complete mean':>16} {'t_complete med':>15} {'pktRecv mean':>13}")
for sch,rs in sorted(schemes.items()):
    comp=[float(r['timeToCompleteData_s']) for r in rs if float(r['timeToCompleteData_s'])>=0]
    rate=100.0*len(comp)/len(rs) if rs else 0
    air=[float(r['pktRecv']) for r in rs]
    tmean=st.mean(comp) if comp else float('nan')
    tmed=st.median(comp) if comp else float('nan')
    print(f"{sch:<10} {len(rs):>5} {rate:>6.1f}% {tmean:>16.2f} {tmed:>15.2f} {st.mean(air):>13.0f}")
PY
