#!/bin/bash
# Item 117: team 1's transits as Dubins paths (radius 255 m at 50 m/s; tour kind kin = latency with Dubins legs,
# mission_policy.kin_links). P* and no cooperation with the kin tour, pre-existing clusters (KW), MEANDER (MW) and
# subCH (SW), 40 maps x 100 draws, on the existing ns-3 runs (inside a cluster the speed does not change: MEANDER's
# curves keep curvature <= 1/255 m, the k-medoids lines are straight). From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
python3 tools/l1_rank.py --set kmedoids "$S/KW/k*" --set meander "$S/MW/k*" --set subch "$S/SW/k*" --draws 100 --jobs 2 \
    --methods "P+prog-kin-puq-stage-zero,B4-kin-puq-stage-zero" --out docs/data/l2diag/kin
