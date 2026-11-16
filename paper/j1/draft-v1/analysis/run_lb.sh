#!/usr/bin/env bash
# River variants of the J1 draft on the DLG missions (k8, r100): same pass, same mission index, same binary;
# only the plan's Bank -> member paths (river_lb.py) and the forwarding (--tree) change.
#
#   run_lb.sh BIN DT OUT "SEEDS" "CLUSTERS" "TAGS" [JOBS]
#
# BIN: directory with river-bin and lib/ (a build of uav-coop2/examples/coop2-river.cc that has --tree)
# DT:  directory with R<seed>/k8-s1/ of the DLG experiment (plans, passes, deploy files)
# OUT: results, OUT/R<seed>/r<k>-<tag>-{crit,runs,energy}.csv, the plan used and the simulator's log
# TAGS: rf (plan as is)  rfX (plan as is, --tree)  lb (balanced plan)  lbs (balanced plan with shared hops, --tree)
set -eu
BIN=$1; DT=$2; OUT=$3; SEEDS=$4; CLUSTERS=$5; TAGS=$6; JOBS=${7:-4}
HERE=$(cd "$(dirname "$0")" && pwd); LB=$HERE/../../../../uav-coop2/tools/river_lb.py
one() {
  R=$1; k=$2; tag=$3; W=$DT/R$R/k8-s1; O=$OUT/R$R; mkdir -p "$O"
  plan=$W/plan$k.txt; extra=
  case $tag in
    rfX) extra=--tree=true ;;
    lb)  plan=$O/plan$k-lb.txt;  python3 "$LB" "$W" "$k" "$plan" --beta 0.1 > "$O/plan$k-lb.log" ;;
    lbs) plan=$O/plan$k-lbs.txt; python3 "$LB" "$W" "$k" "$plan" --beta 0.1 --shared > "$O/plan$k-lbs.log"; extra=--tree=true ;;
  esac
  mission=$((800100 + k + 10000000 * (R - 1)))
  (cd "$W" && LD_LIBRARY_PATH=$BIN/lib "$BIN/river-bin" --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv \
     --gateways=c$k-gateways-s35.csv --plan="$plan" --bits=pass$k-bits --firstRun=$mission --runs=1 --limit=900 \
     --gwSelect=quality --colours=7 --scheme=river --prep=full --repair=20 $extra --out="$O/r$k-$tag" > "$O/r$k-$tag.log" 2>&1)
  echo "R$R c$k $tag: $(tail -n 1 "$O/r$k-$tag-runs.csv" | cut -d, -f4,6,13)   (simS, hops, MAC give-ups)"
}
export -f one; export BIN DT OUT LB
for R in $SEEDS; do for k in $CLUSTERS; do for t in $TAGS; do echo "$R $k $t"; done; done; done |
  xargs -P "$JOBS" -L 1 bash -c 'one $0 $1 $2'
