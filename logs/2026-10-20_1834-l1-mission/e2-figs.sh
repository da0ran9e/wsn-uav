#!/bin/bash
# E2 tables and figures (item 114, round 2): the three partitions, paired on the same maps and draws. From uav-l2/.
#   e2-all        every partition x method against P* on pre-existing clusters (table only)
#   l1-e2-tstar   P*, no cooperation and the oracle per partition;  l1-e2-breakdown  P* per partition
D=docs/data/l1rank; P=P+prog-latency-puq-stage-zero
DR="$D/e1-draws.csv $D/e2-subch-draws.csv"
[ -f $D/e2-meander-draws.csv ] && DR="$DR $D/e2-meander-draws.csv"
ROWS=()
for s in kmedoids subch meander; do
  for m in "P*=$P" "leave at first report=P+prog-latency-puq-stage" "River report only=P-latency-puq-stage-zero" \
           "B4=B4-latency-puq-stage-zero" "beta 0=P+prog-latency-stage-zero" "beta 1=P+prog-latency-pu-stage-zero" \
           "P old=P" "B1=B1" "B7=B7"; do
    ROWS+=(--row "$s ${m%%=*}=$s:${m#*=}")
  done
done
python3 tools/l1_compare.py --draws $DR --ref "kmedoids:$P" "${ROWS[@]}" --out $D/e2-all
python3 tools/l1_compare.py --draws $DR --ref "kmedoids:$P" --figs docs/figures --tag l1-e2 --breakdown --out $D/e2-main \
  --row "kmedoids P*=kmedoids:$P" --row "subch P*=subch:$P" --row "meander P*=meander:$P" \
  --row "kmedoids B4=kmedoids:B4-latency-puq-stage-zero" --row "subch B4=subch:B4-latency-puq-stage-zero" \
  --row "meander B4=meander:B4-latency-puq-stage-zero" \
  --row "kmedoids B7=kmedoids:B7" --row "subch B7=subch:B7" --row "meander B7=meander:B7" \
  --colour "kmedoids P*=#1c5cab" --colour "subch P*=#8a59cf" --colour "meander P*=#2f9e6e" \
  --colour "kmedoids B4=#86b6ef" --colour "subch B4=#c3a6ea" --colour "meander B4=#8fd1b0" \
  --colour "kmedoids B7=#1c5cab" --colour "subch B7=#8a59cf" --colour "meander B7=#2f9e6e" \
  --marker "kmedoids B4=s" --marker "subch B4=s" --marker "meander B4=s" \
  --marker "kmedoids B7=^" --marker "subch B7=^" --marker "meander B7=^"
