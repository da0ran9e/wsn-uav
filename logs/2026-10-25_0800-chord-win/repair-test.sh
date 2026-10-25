#!/bin/bash
# River --repair (CLAUDE.md §8 item 169): (1) off, the new binary must match the frozen river-bin on one cluster;
# (2) on (20 s), the three clusters whose critical cells stalled must finish (k16-s1 r100 C1, C9; k16-s1 open C6).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
B=$S/CAMP-BIN3; NEW=/home/user/ns3-dev/build/src/uav-coop2/examples/ns3.46-uav-coop2-river-optimized; O=$S/RFIX
run() {   # BIN WORK K MISSION OUT [extra]
  (cd $2 && LD_LIBRARY_PATH=$B/lib $1 --nodes=c$3-nodes-s35.csv --routes=c$3-routes-s35.csv --gateways=c$3-gateways-s35.csv \
    --plan=plan$3.txt --bits=pass$3-bits --firstRun=$4 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river \
    --prep=full --out=$5 ${@:6} 2>&1 | tail -1)
}
run $NEW $S/CTRY/P/k8-s1 1 800101 $O/off-k8-c1 &
run $NEW $S/ENV/r100/k16-s1 1 1600101 $O/rep-r100-c1 --repair=20 &
run $NEW $S/ENV/r100/k16-s1 9 1600109 $O/rep-r100-c9 --repair=20 &
wait
run $NEW $S/ANIM/k16-s1 6 1600106 $O/rep-open-c6 --repair=20
cmp -s <(cut -d, -f1-11 $S/CTRY/P/k8-s1/r1-rf-crit.csv) <(cut -d, -f1-11 $O/off-k8-c1-crit.csv) \
  && echo "repair off: k8-s1 open C1 identical to the frozen binary" || echo "repair off: DIFFERS"
for f in rep-r100-c1 rep-r100-c9 rep-open-c6; do
  echo "$f: $(awk -F, 'NR>1{n++; if($9<0)s++; if($9>m)m=$9} END{printf "%d crit, %d not done, max doneS %.1f", n, s, m}' $O/$f-crit.csv)"
done
