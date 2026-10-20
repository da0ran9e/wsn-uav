#!/bin/bash
# E2 (item 114, round 2): one layer-2 partition on the same 40 maps, River window 400 kB, 100 draws; paired with
# E1's pre-existing k-medoids clusters (same maps, same draw seeds), which has every method below (-redir: redir.sh).
#   bash e2.sh subch SW      subCH baseline (k-medoids clusters split around critical cells >= 6 cells apart)
#   bash e2.sh meander MW    MEANDER (layer 2)
# P*, its main ablations, team 2's threshold beta = 0 / 1 (P* has 1/4), P* with in-flight redirect (round-2 idea),
# the old policy, B1 and the oracle. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
M="P+prog-latency-puq-stage-zero,P+prog-latency-puq-stage,P-latency-puq-stage-zero,B4-latency-puq-stage-zero"
M="$M,P+prog-latency-stage-zero,P+prog-latency-pu-stage-zero,P+prog-latency-puq-stage-zero-redir,P,B1,B7"
python3 tools/l1_rank.py --set $1 "$S/$2/k*" --draws 100 --jobs ${JOBS:-2} --methods "$M" --out docs/data/l1rank/e2-$1
