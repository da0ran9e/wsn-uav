#!/bin/bash
# Layer-1 sensitivity (item 114, round 3): the proposed policy and no cooperation, k-medoids River full D (KF),
# 40 maps x 50 draws, one layer-1 parameter changed per run. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
M="P+prog-latency-pu-stage,P-latency-pu-stage,B4-latency-pu-stage,B1,B7"
for v in "base:" "dim64:--dim 64" "dim256:--dim 256" "rho0:--rho 0" "rho05:--rho 0.05" "m105:--m 105" "m693:--m 693"; do
  tag=${v%%:*}; opt=${v#*:}
  python3 tools/l1_rank.py --set $tag "$S/KF/k*" --draws 50 --jobs 2 --methods "$M" $opt --out docs/data/l1rank/sens-$tag
done
