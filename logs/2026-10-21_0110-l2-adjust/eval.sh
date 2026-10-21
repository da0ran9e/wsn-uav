#!/bin/bash
# Items 116-117: T* of the adjusted MEANDER (lanes 7.5, fragments 0.5) with P*, no cooperation, P* + redirect and the
# oracle, also with the kinematic (Dubins) tour, 40 maps x 100 draws, paired with E1 (pre-existing clusters) and E2 (original MEANDER). From uav-l2/.
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
D=docs/data/l1rank; P=P+prog-latency-puq-stage-zero
python3 tools/l1_rank.py --set meanderAdj "$S/MG/L7.5f0.5/k*" --draws 100 --jobs 3 \
    --methods "$P,B4-latency-puq-stage-zero,$P-redir,B7,P+prog-kin-puq-stage-zero,B4-kin-puq-stage-zero" \
    --out docs/data/l2diag/adj
python3 tools/l1_compare.py --draws $D/e1-draws.csv $D/e2-meander-draws.csv docs/data/l2diag/adj-draws.csv $D/redir-draws.csv \
    docs/data/l2diag/kin-draws.csv \
    --ref "kmedoids:$P" --out docs/data/l2diag/adj \
    --row "kmedoids P*=kmedoids:$P" --row "meander P*=meander:$P" --row "meanderAdj P*=meanderAdj:$P" \
    --row "kmedoids B4=kmedoids:B4-latency-puq-stage-zero" --row "meander B4=meander:B4-latency-puq-stage-zero" \
    --row "meanderAdj B4=meanderAdj:B4-latency-puq-stage-zero" \
    --row "kmedoids P* redirect=kmedoids:$P-redir" --row "meander P* redirect=meander:$P-redir" \
    --row "meanderAdj P* redirect=meanderAdj:$P-redir" \
    --row "kmedoids B7=kmedoids:B7" --row "meanderAdj B7=meanderAdj:B7" \
    --row "kmedoids P* kin=kmedoids:P+prog-kin-puq-stage-zero" --row "meander P* kin=meander:P+prog-kin-puq-stage-zero" \
    --row "meanderAdj P* kin=meanderAdj:P+prog-kin-puq-stage-zero"
