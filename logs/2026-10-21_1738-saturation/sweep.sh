#!/bin/bash
# Item 120 campaign (to run only once the user agrees): strips WIDTH cells x LENGTH km, seeds 1..NSEED, deploy, pass and
# River (rf, 400 kB window), four at a time; a folder already done is skipped (the stages resume). From uav-l2/.
export S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
NSEED=${NSEED:-5}
for s in $(seq 1 $NSEED); do for w in 3 4.5 6 8 10; do for l in 1.5 2 3 4 6; do echo "$w $l $s"; done; done; done |
  xargs -P 4 -L 1 bash -c '
    python3 tools/sat_strip.py --width $0 --length $1 --seed $2 --work $S/SAT/w$0-l$1-s$2 --bin $S/BIN > $S/SAT/w$0-l$1-s$2.out 2>&1
    echo "w$0 l$1 s$2 exit $? $(date +%H:%M:%S)"'
python3 tools/sat_strip.py --summary "$S/SAT/w*-s*" --out docs/data/sat/strips.csv
