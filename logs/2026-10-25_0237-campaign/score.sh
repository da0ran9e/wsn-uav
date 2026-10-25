#!/bin/bash
# Scoring of the final campaign (CLAUDE.md §8 item 161), run from /home/user/wsn-uav after campaign.sh:
# 100 layer-1 draws per map. P set: P*, its ablations and every baseline on all maps; Trickle on seeds 1-10 only.
# K set: the layer-2 ablation, both tour kinds (the better one per map is taken later, as before).
# l1_rank skips a folder whose runs are incomplete, so the map counts in the summaries must be checked (120 / 40).
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_0237-campaign
O=$S/CAMP/score
mkdir -p $O
T=puq-stage-zero-redir
M="P+prog-kin-$T-kt,Pd+prog-kin-$T-kt,B4-kin-$T-kt,B1,B2-300,B2-500,B3-300-$T,B3-500-$T,B6-$T,B8-300-$T,B8-500-$T,B5-$T,B7"
python3 tools/runlog.py $L/score-P.md "python3 uav-l2/tools/l1_rank.py --set P '$S/CAMP/P/k*' --draws 100 --jobs 3 --methods $M --out $O/P"
python3 tools/runlog.py $L/score-Pt.md "python3 uav-l2/tools/l1_rank.py --set Pt '$S/CAMP/P/k*-s[1-9],$S/CAMP/P/k*-s10' --draws 100 --jobs 3 --methods P+prog-kin-$T-kt,Pt+prog-kin-$T-kt --out $O/Pt"
python3 tools/runlog.py $L/score-K.md "python3 uav-l2/tools/l1_rank.py --set K '$S/CAMP/K/k*' --draws 100 --jobs 3 --methods P+prog-kin-$T-kt,P+prog-skin-$T-kt --out $O/K"
