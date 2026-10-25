#!/bin/bash
# LM-Tour step C sweep on map k8-s1: R in {200, 450, 800} m x the four channels, theta 1, one round
# (round 2 gave the same order on r200), then the model-level mission (pred) of each.
S=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad
L=/home/user/wsn-uav/logs/2026-10-25_1500-lm-tour
cd /home/user/wsn-uav/uav-l2/tools
job() {
  R=$1; e=$2
  python3 /home/user/wsn-uav/tools/runlog.py $L/c-plan-$e-k8-R$R.md \
    "python3 lm_tour.py plan $S/FIX/$e/k8-s1 --out $S/LM/R$R/$e/k8-s1 --R $R --rounds 1" --cwd . > /dev/null
  python3 /home/user/wsn-uav/tools/runlog.py $L/c-score-$e-k8-R$R.md \
    "python3 lm_tour.py score $S/LM/R$R/$e/k8-s1 --mode pred --out $S/LM/R$R-$e-k8" --cwd . > /dev/null
  echo "R$R $e done"
}
export -f job; export S L
for R in 200 450 800; do for e in open r500 r200 r100; do echo "$R $e"; done; done | xargs -P 4 -n 2 bash -c 'job "$@"' _
