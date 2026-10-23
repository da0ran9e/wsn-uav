#!/bin/bash
# Waits for the subCH-K jobs, then runs Trickle on the 16 maps, two at a time.
L=/home/user/wsn-uav/logs/2026-10-23_0706-baselines
while [ $(cat $L/done-subch.txt 2>/dev/null | wc -l) -lt 16 ]; do sleep 20; done
xargs -P 2 -I{} bash $L/job-trickle.sh {} < $L/maps.txt
