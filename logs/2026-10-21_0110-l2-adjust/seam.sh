#!/bin/bash
# Item 116, adjustment 1: seamless junctions (mission_policy.seams, tour kind seam) on the existing ns-3 runs:
# P* with its latency tour and with the seam tour, pre-existing clusters (KW) and MEANDER (MW), 40 maps x 100 draws.
# A cluster's pass and River do not depend on the tour, so the ns-3 results are reused. From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --set meander "$S/MW/k*" --draws 100 --jobs 2 \
    --methods "P+prog-latency-puq-stage-zero,P+prog-seam-puq-stage-zero" --out docs/data/l2diag/seam
