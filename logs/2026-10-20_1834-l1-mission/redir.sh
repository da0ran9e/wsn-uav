#!/bin/bash
# Round 2 idea check (after l1_state.py): at c*'s first report team 2 is flying to another cell in 13-23 % of the
# draws. -redir lets the rotary UAV change target in flight at each report. P* with and without it, and no
# cooperation with it, on E1's maps and draws (KW, 40 maps x 100 draws). From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --draws 100 --jobs 2 \
    --methods "P+prog-latency-puq-stage-zero,P+prog-latency-puq-stage-zero-redir,B4-latency-puq-stage-zero-redir" \
    --out docs/data/l1rank/redir
