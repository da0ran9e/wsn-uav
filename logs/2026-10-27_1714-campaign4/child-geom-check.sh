#!/bin/bash
# Check a campaign session's CHORD geometry (CLAUDE.md §8 item 203): every geometry file of CP/<channel>/R<R>/<map>
# (cells, nodes, deploy, path, speed caps, tour, map, env, plan options, River plans; logs left out) must match seed 1's
# (geometry-r1.sha256, made from the main session's CP/<channel>/R1). A cell whose cp job has not built it yet is
# "pending"; files still missing (a cp job in progress) are counted apart from those that differ. A JSON file that
# differs only by float round-off (|a - b| <= 1e-9 (1 + |b|), json_close.py, against the unpacked R1 copy) matches.
#   CAMP_S=<scratchpad> bash child-geom-check.sh R
: "${CAMP_S:?}"
R=$1
L=$(cd "$(dirname "$0")" && pwd)
bad=0
for E in open r500 r200 r100; do for K in 8 12 16; do
  D=$CAMP_S/C4/CP/$E/R$R/k$K-s1
  if [ ! -e $D/map.json ]; then echo "$E k$K pending"; continue; fi
  n=0; miss=0; diff=0; round=0; first=""
  while read -r h f; do
    n=$((n + 1)); p=$D/${f#*/*/}
    if [ ! -e "$p" ]; then miss=$((miss + 1))
    elif [ "$(sha256sum < "$p" | cut -d' ' -f1)" != "$h" ]; then
      # a JSON file whose numbers differ from seed 1's by float round-off only (tour.json of a geometry the cp job
      # built itself: 1e-12 s) counts as matching
      if [[ $p == *.json ]] && python3 "$L/json_close.py" "$p" "$CAMP_S/C4/CP/$E/R1/k$K-s1/${f#*/*/}" 2>/dev/null; then
        round=$((round + 1))
      else diff=$((diff + 1)); first=${first:-${f#*/*/}}; fi
    fi
  done < <(grep "  $E/k$K-s1/" $L/geometry-r1.sha256)
  echo "$E k$K: $n files, $diff differ${first:+ (first: $first)}, $round round-off only, $miss missing"
  [ $diff -gt 0 ] && bad=1
done; done
echo "GEOM $([ $bad = 0 ] && echo OK || echo FAIL)"
exit $bad
