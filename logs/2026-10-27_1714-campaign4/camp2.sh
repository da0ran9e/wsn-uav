#!/bin/bash
# The campaign's queue (CLAUDE.md §8 item 199): every (scheme, seed, channel, map) a job (job.sh), four at a time,
# seeds and schemes mixed so the four cores stay busy. Before the queue, the CHORD geometry of every seed R > 1 is
# copied from seed 1 (map, deploy, tour and River plans do not depend on R) with runseed.txt written, so LM-Tour and
# DTSP-N + River do not wait for CHORD's mission. Order: seed, then the largest map, the harshest channel; per cell
# LM-Tour, CHORD, DTSP-N + River. One Markdown log per job, one line per finished job in done.txt.
# Several sessions (item 201): CAMP_S their scratchpad, CAMP_DONE their own done file, CAMP_ID their name in assigned/.
#   nohup bash camp2.sh FIRST_SEED LAST_SEED &
cd "$(dirname "$0")/../.."
L=logs/2026-10-27_1714-campaign4
C=${CAMP_S:-/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad}/C4
D=${CAMP_DONE:-done.txt}
for R in $(seq $1 $2); do
  [ "$R" = 1 ] && continue
  for K in 16 12 8; do for E in r100 r200 r500 open; do
    CP=$C/CP/$E/R$R/k$K-s1
    if [ ! -e $CP/map.json ]; then
      mkdir -p $(dirname $CP)
      cp -a $C/CP/$E/R1/k$K-s1 $CP
      find $CP -maxdepth 1 \( -name 'pass[0-9]*' -o -name 'r[0-9]*-*' -o -name 'chordfc-*' -o -name 'fc-*' \
           -o -name 'dn-*' -o -name runseed.txt \) -exec rm -f {} +
    fi
    [ -e $CP/runseed.txt ] || [ -e $CP/pass1-bits-r1.bin ] || echo $R > $CP/runseed.txt
  done; done
done
for R in $(seq $1 $2); do for K in 16 12 8; do for E in r100 r200 r500 open; do for S in lmd cp dr; do
  echo "$S $R $E $K"; done; done; done; done |
  xargs -P 4 -L 1 bash -c 'o='$L'/score/R$1/$2-k$3   # a job already done keeps its log when the queue restarts
    { [ -e $o/done-$0 ] || { [ $0 != dr ] && [ -e $o/done ]; }; } && exit 0; mkdir -p '$L'/R$1;
    python3 tools/runlog.py '$L'/R$1/$2-k$3-$0.md "bash '$L'/job.sh $0 $1 $2 $3" > /dev/null 2>&1;
    echo "R$1 $2 k$3 $0 exit $? $(date -u +%F_%T)" >> '$L'/'$D
echo "queue done $(date -u +%F_%T)" >> $L/$D
