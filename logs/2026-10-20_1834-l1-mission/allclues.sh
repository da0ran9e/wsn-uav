#!/bin/bash
# Round 2 idea check: 45 % of the k-medoids clusters have an Axe shorter than the clue set (4036 packets ~ 2 km), and
# none of their critical cells gets all 12 clues. Upper bound: P* with every River report holding all 12 clues
# (River timing unchanged), on E1's maps and draws (KW, 40 maps x 100 draws). From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --draws 100 --jobs 2 \
    --methods "P+prog-latency-puq-stage-zero,P+prog-latency-puq-stage-zero-allclues" --out docs/data/l1rank/allclues
