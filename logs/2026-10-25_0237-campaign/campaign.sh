#!/bin/bash
# The final campaign (CLAUDE.md §8 items 160-161): 120 maps (k2, k4, k6, k8 x seeds 1-30) x {P, K}, two jobs at a
# time, two ns-3 processes each. Seeds 1-10 of every size first, then 11-20, then 21-30, so a stop part-way still
# leaves whole blocks of maps.
L=/home/user/wsn-uav/logs/2026-10-25_0237-campaign
cd /home/user/wsn-uav
for lo in 1 11 21; do
  for s in $(seq $lo $((lo + 9))); do
    for k in 2 4 6 8; do
      for set_ in P K; do echo "$set_ k$k-s$s"; done
    done
  done
done | xargs -P 2 -n 2 $L/job.sh
echo "campaign done $(date +%H:%M:%S)" >> $L/done.txt
