#!/bin/bash
# The campaign of CLAUDE.md §8 item 188: 10 simulation seeds x 3 maps (k8-s1, k12-s1, k16-s1) x 4 channels, each task
# (task.sh) the four schemes. Two tasks at a time (each mission --jobs 2: four cores), seed by seed, the largest map
# and the harshest channel first. One Markdown log per task (tools/runlog.py), one line per finished task in done.txt.
# A task is finished when both done (CHORD, LM-Tour, FC + DTSP-N, B1, B7) and done-dr (DTSP-N + River) exist.
#   nohup bash camp.sh [FIRST_SEED] [LAST_SEED] &
cd /home/user/wsn-uav
L=logs/2026-10-27_1714-campaign4
for R in $(seq ${1:-1} ${2:-10}); do for K in 16 12 8; do for E in r100 r200 r500 open; do echo "$R $E $K"; done; done; done |
  xargs -P 2 -L 1 bash -c 'mkdir -p '$L'/R$0; [ -e '$L'/score/R$0/$1-k$2/done ] && [ -e '$L'/score/R$0/$1-k$2/done-dr ] && exit 0;
    python3 tools/runlog.py '$L'/R$0/$1-k$2.md "bash '$L'/task.sh $0 $1 $2" > /dev/null 2>&1;
    echo "R$0 $1 k$2 exit $? $(date -u +%F_%T)" >> '$L'/done.txt'
echo "all done $(date -u +%F_%T)" >> $L/done.txt
