#!/bin/bash
# E2 (item 114, round 2): the layer-2 partitions on the same 40 maps, River window 400 kB, 100 draws:
# pre-existing k-medoids clusters (KW), MEANDER (MW, layer 2), subCH baseline (SW). From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
M="P+prog-latency-pu-stage-zero,P+prog-latency-pu-stage,P-latency-pu-stage-zero,B4-latency-pu-stage-zero,P,B1,B7"
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --set meander "$S/MW/k*" --set subch "$S/SW/k*" \
    --draws 100 --jobs ${JOBS:-2} --methods "$M" --out docs/data/l1rank/e2
