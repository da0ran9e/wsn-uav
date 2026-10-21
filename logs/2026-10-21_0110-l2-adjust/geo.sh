#!/bin/bash
# Item 116, adjustments 2-3, geometry only (no ns-3): MEANDER with lane width L (cells) and fragment threshold F
# (x 80 cells) on the 40 campaign maps, meander_mission.py --geometry (map, deploy: CH and critical cells, the
# real curved paths). L4.5f0.25 is the campaign's MEANDER (MW), as a check. Three configurations at a time
# (geo-one.sh L F); a folder already built is skipped (the stages resume). From uav-l2/.
L=/home/user/wsn-uav/logs/2026-10-21_0110-l2-adjust
printf "%s\n" "4.5 0.25" "6 0.25" "7.5 0.25" "9 0.25" "4.5 0.5" "6 0.5" "7.5 0.5" "9 0.5" | xargs -P 3 -L 1 bash $L/geo-one.sh
