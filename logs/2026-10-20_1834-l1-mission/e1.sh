#!/bin/bash
# E1 (item 114, round 2): pre-existing clusters (k-medoids) with River window 400 kB, 40 maps x 100 draws:
# the proposed policy, one-change ablations, no cooperation, the rotary baselines and the oracle. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
M="P+prog-latency-pu-stage,P+prog-latency-pu-stage-zero,P-latency-pu-stage,B4-latency-pu-stage"
M="$M,P+prog-pu-stage,P+prog-short-pu-stage,P+prog-latency,P+prog-latency-pu"
M="$M,P+prog-latency-pu-stage-grouped,B4-latency-pu-stage-grouped,P+prog-latency-pu-stage-equal,P,P-wait"
M="$M,B1,B2-300,B2-500,B3-300-pu-stage,B3-500-pu-stage,B6-pu-stage,B7"
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --draws 100 --jobs ${JOBS:-2} --methods "$M" --out docs/data/l1rank/e1
