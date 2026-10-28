#!/bin/bash
# Check a campaign session's CHORD geometry (CLAUDE.md §8 item 203): every geometry file of CP/<channel>/R<R>/<map>
# (cells, nodes, deploy, path, speed caps, tour, map, env, plan options, River plans; logs left out) must match seed 1's
# (geometry-r1.sha256, made from the main session's CP/<channel>/R1). A cell whose cp job has not built it yet is
# "pending"; files still missing (a cp job in progress) are counted apart from those that differ.
#   CAMP_S=<scratchpad> bash child-geom-check.sh R
: "${CAMP_S:?}"
R=$1
L=$(cd "$(dirname "$0")" && pwd)
bad=0
for E in open r500 r200 r100; do for K in 8 12 16; do
  D=$CAMP_S/C4/CP/$E/R$R/k$K-s1
  if [ ! -e $D/map.json ]; then echo "$E k$K pending"; continue; fi
  n=0; miss=0; diff=0; first=""
  while read -r h f; do
    n=$((n + 1)); p=$D/${f#*/*/}
    if [ ! -e "$p" ]; then miss=$((miss + 1))
    elif [ "$(sha256sum < "$p" | cut -d' ' -f1)" != "$h" ]; then diff=$((diff + 1)); first=${first:-${f#*/*/}}
    fi
  done < <(grep "  $E/k$K-s1/" $L/geometry-r1.sha256)
  echo "$E k$K: $n files, $diff differ${first:+ (first: $first)}, $miss missing"
  [ $diff -gt 0 ] && bad=1
done; done
echo "GEOM $([ $bad = 0 ] && echo OK || echo FAIL)"
exit $bad
