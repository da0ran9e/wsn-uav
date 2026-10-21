#!/bin/bash
# Item 120: the River with a window per critical cell (river_export.py --windowAt crit) on the pilot strips,
# reusing their deploy and pass. Three at a time.
export S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
for w in w4.5-l2-s1 w6-l2-s1 w10-l4-s1; do echo $w; done | xargs -P 3 -I{} bash -c '
  cd /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/SAT/{} &&
  python3 /home/user/wsn-uav/uav-coop2/tools/river_export.py --deploy=d1 --path=c1-path-s35.csv --banks=parallel --windowKB=400 --windowAt=crit --out=plan1-crit.txt > plan1-crit.log 2>&1 &&
  LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/lib /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=plan1-crit.txt --bits=pass1-bits --firstRun=1 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --out=r1-rfc 2>/dev/null | tail -1 | sed "s/^/{}: /"'
