#!/bin/bash
# E1 tables and figures (item 114, round 2), pre-existing k-medoids clusters, River window 400 kB. From uav-l2/.
#   e1-all      every method against P* (table only)
#   l1-e1-abl   P* and its main ablations;  l1-e1-base  P*, no cooperation, the baselines and the oracle (log scale)
#   l1-e1-breakdown  c*'s first report at the BS (light) and the rest until c* is verified, per row and size
D=docs/data/l1rank; K=kmedoids; P="$K:P+prog-latency-puq-stage-zero"
ALL=(--row "P*=$P" --row "leave at first report=$K:P+prog-latency-puq-stage"
  --row "River report only=$K:P-latency-puq-stage-zero" --row "no cooperation B4=$K:B4-latency-puq-stage-zero"
  --row "tour l3first=$K:P+prog-puq-stage-zero" --row "tour short=$K:P+prog-short-puq-stage-zero"
  --row "beta 0=$K:P+prog-latency-stage-zero" --row "beta 1/2=$K:P+prog-latency-puh-stage-zero"
  --row "beta 1=$K:P+prog-latency-pu-stage-zero" --row "time-aware=$K:P+prog-latency-put-stage-zero"
  --row "no staging=$K:P+prog-latency-puq-zero" --row "greedy old team 2=$K:P+prog-latency"
  --row "grouped=$K:P+prog-latency-puq-stage-zero-grouped" --row "B4 grouped=$K:B4-latency-puq-stage-zero-grouped"
  --row "equal weights=$K:P+prog-latency-puq-stage-zero-equal" --row "P old=$K:P" --row "P old wait=$K:P-wait"
  --row "B1=$K:B1" --row "B2-300=$K:B2-300" --row "B2-500=$K:B2-500" --row "B3-300=$K:B3-300-puq-stage-zero"
  --row "B3-500=$K:B3-500-puq-stage-zero" --row "B6=$K:B6-puq-stage-zero" --row "B7=$K:B7")
python3 tools/l1_compare.py --draws $D/e1-draws.csv --ref "$P" "${ALL[@]}" --out $D/e1-all
python3 tools/l1_compare.py --draws $D/e1-draws.csv --ref "$P" --figs docs/figures --tag l1-e1-abl --out $D/e1-abl \
  --row "P*=$P" --row "leave at first report=$K:P+prog-latency-puq-stage" \
  --row "River report only=$K:P-latency-puq-stage-zero" --row "no cooperation B4=$K:B4-latency-puq-stage-zero" \
  --row "tour l3first=$K:P+prog-puq-stage-zero" --row "tour short=$K:P+prog-short-puq-stage-zero" \
  --row "beta 0=$K:P+prog-latency-stage-zero" --row "beta 1=$K:P+prog-latency-pu-stage-zero" \
  --row "no staging=$K:P+prog-latency-puq-zero" --row "greedy old team 2=$K:P+prog-latency" --row "P old=$K:P" \
  --colour "P*=#1c5cab" --colour "leave at first report=#86b6ef" --colour "River report only=#4a90d9" \
  --colour "no cooperation B4=#eda100" --colour "tour l3first=#2f9e6e" --colour "tour short=#8fd1b0" \
  --colour "beta 0=#8a59cf" --colour "beta 1=#c3a6ea" --colour "no staging=#c45a7a" \
  --colour "greedy old team 2=#d6403a" --colour "P old=#52514e"
python3 tools/l1_compare.py --draws $D/e1-draws.csv --ref "$P" --figs docs/figures --tag l1-e1-base --out $D/e1-base --log \
  --row "P*=$P" --row "no cooperation B4=$K:B4-latency-puq-stage-zero" --row "B3-300=$K:B3-300-puq-stage-zero" \
  --row "B3-500=$K:B3-500-puq-stage-zero" --row "B6=$K:B6-puq-stage-zero" --row "B2-300=$K:B2-300" \
  --row "B2-500=$K:B2-500" --row "B1=$K:B1" --row "B7=$K:B7" \
  --colour "P*=#1c5cab" --colour "no cooperation B4=#eda100" --colour "B3-300=#8a59cf" --colour "B3-500=#c3a6ea" \
  --colour "B6=#c45a7a" --colour "B2-300=#7a7a76" --colour "B2-500=#a9a8a3" --colour "B1=#2b2a28" --colour "B7=#2f9e6e"
python3 tools/l1_compare.py --draws $D/e1-draws.csv --ref "$P" --figs docs/figures --tag l1-e1 --breakdown --out $D/e1-bd \
  --row "P*=$P" --row "River report only=$K:P-latency-puq-stage-zero" --row "no cooperation B4=$K:B4-latency-puq-stage-zero" \
  --row "greedy old team 2=$K:P+prog-latency" --row "P old=$K:P" \
  --colour "P*=#1c5cab" --colour "River report only=#4a90d9" --colour "no cooperation B4=#eda100" \
  --colour "greedy old team 2=#d6403a" --colour "P old=#52514e"
