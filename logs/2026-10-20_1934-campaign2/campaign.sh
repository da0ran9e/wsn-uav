#!/bin/bash
# Round 2 of item 114, from uav-l2/: two (set, map) jobs at a time, two ns-3 jobs each.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
L=/home/user/wsn-uav/logs/2026-10-20_1934-campaign2
MAPS="k2-s3 $(ls $S/KF | grep -v k2-s3 | tr '\n' ' ')"
$L/job.sh KF k2-s3
for set_ in KW SW MW LW; do
  for m in $MAPS; do
    [ -e $S/$set_/$m ] && [ -L $S/$set_/$m ] && continue   # linked to an earlier run of the same map
    echo "$set_ $m"
  done
done | xargs -P 2 -n 2 $L/job.sh
echo "campaign done $(date +%H:%M:%S)" >> $L/done.txt
