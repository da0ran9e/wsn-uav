#!/bin/bash
# Team-2 waiting rule, chosen on all 40 k-medoids maps (KF, River on the whole D), 50 draws: the threshold P >= beta * n_unreported * P_U
# with beta 1 / 0.5 / 0.25, the time-aware rule (only the cells whose first report comes while team 2 is busy), and greedy;
# all with progressive reports, latency tour, staging, take-off at t = 0. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
M="P+prog-latency-pu-stage-zero,P+prog-latency-puh-stage-zero,P+prog-latency-puq-stage-zero,P+prog-latency-put-stage-zero"
M="$M,P+prog-latency-stage-zero,B4-latency-puq-stage-zero,B4-latency-put-stage-zero,B4-latency-stage-zero"
python3 tools/l1_rank.py --set kmedoids "$S/KF/k*" --draws 50 --jobs ${JOBS:-1} --methods "$M" --out docs/data/l1rank/rule
