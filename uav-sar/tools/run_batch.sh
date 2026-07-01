#!/usr/bin/env bash
# Batch runner: N seeds x {proposed,nocoop,pure-uav}. Collects every metrics.csv
# into one summary and prints per-scheme aggregates.
# Run from the ns-3 root that contains build/.
#   bash src/uav-sar/tools/run_batch.sh [N] [GRID] [NUMUAV] [SIMTIME]
set -u
N=${1:-100}; GRID=${2:-8}; NUMUAV=${3:-4}; SIMTIME=${4:-500}
EXE="./build/src/uav-sar/examples/ns3.46-scenario-sar-default"
[[ -x "$EXE" ]] || { echo "build first: $EXE not found"; exit 1; }
OUT="data/results/uav-sar"; SUM="$OUT/summary.csv"; mkdir -p "$OUT"; : > "$SUM"; H=0

echo "Running $N seeds x 3 schemes (grid $GRID, $NUMUAV UAVs)..."
for ((s=1; s<=N; s++)); do
  for sch in proposed nocoop pure-uav; do
    "$EXE" --gridSize=$GRID --numUav=$NUMUAV --seed=$s --scheme=$sch --simTime=$SIMTIME >/dev/null 2>&1
    M="$OUT/$sch/run-$s/metrics.csv"
    if [[ -f "$M" ]]; then
      [[ $H -eq 0 ]] && { head -1 "$M" >> "$SUM"; H=1; }
      tail -n +2 "$M" >> "$SUM"
    fi
  done
  (( s % 10 == 0 )) && echo "  ... $s/$N"
done
echo "summary: $SUM"; echo ""
python3 - "$SUM" <<'PY'
import csv, sys, statistics as st
rows=list(csv.DictReader(open(sys.argv[1])))
by={}
for r in rows: by.setdefault(r['scheme'],[]).append(r)
def f(x):
    try: return float(x)
    except: return -1
print(f"{'scheme':<10}{'runs':>5}{'compl%':>8}{'complete mean':>15}{'median':>9}{'report mean':>13}{'pktRecv':>10}{'regCells':>9}")
for sch,rs in sorted(by.items()):
    comp=[f(r['timeToCompleteData_s']) for r in rs if f(r['timeToCompleteData_s'])>=0]
    rep=[f(r['timeToReportAtBS_s']) for r in rs if f(r['timeToReportAtBS_s'])>=0]
    air=[f(r['pktRecv']) for r in rs]
    reg=[f(r['regionCells']) for r in rs if f(r['regionCells'])>0]
    rate=100.0*len(comp)/len(rs) if rs else 0
    cm=st.mean(comp) if comp else float('nan'); cmed=st.median(comp) if comp else float('nan')
    rm=st.mean(rep) if rep else float('nan')
    print(f"{sch:<10}{len(rs):>5}{rate:>7.1f}%{cm:>15.2f}{cmed:>9.2f}{rm:>13.2f}{st.mean(air):>10.0f}{(st.mean(reg) if reg else 0):>9.2f}")
PY
