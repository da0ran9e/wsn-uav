#!/bin/bash
# E1 (item 114, round 2): pre-existing clusters (k-medoids) with River window 400 kB, 40 maps x 100 draws:
# the proposed policy, one-change ablations, no cooperation, the rotary baselines and the oracle. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
# P* = P+prog-latency-puq-stage-zero (round 1b, E1 preview, rule.sh); each ablation changes one part of it
M="P+prog-latency-puq-stage-zero,P+prog-latency-puq-stage,P-latency-puq-stage-zero,B4-latency-puq-stage-zero"
M="$M,P+prog-puq-stage-zero,P+prog-short-puq-stage-zero"
M="$M,P+prog-latency-stage-zero,P+prog-latency-puh-stage-zero,P+prog-latency-pu-stage-zero,P+prog-latency-put-stage-zero"
M="$M,P+prog-latency-puq-zero,P+prog-latency"
M="$M,P+prog-latency-puq-stage-zero-grouped,B4-latency-puq-stage-zero-grouped,P+prog-latency-puq-stage-zero-equal,P,P-wait"
M="$M,B1,B2-300,B2-500,B3-300-puq-stage-zero,B3-500-puq-stage-zero,B6-puq-stage-zero,B7"
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --draws 100 --jobs ${JOBS:-2} --methods "$M" --out docs/data/l1rank/e1
