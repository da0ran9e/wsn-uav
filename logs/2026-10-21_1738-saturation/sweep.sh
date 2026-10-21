#!/bin/bash
# Item 120 campaign (runs only once the user agrees): strips WIDTH cells x LENGTH km, seeds 1..NSEED; deploy, pass,
# River with a window per critical cell (rfc) everywhere, and the window around the CH (rf) where LENGTH <= 3 km
# (longer strips saturate it: 6 x 4 km took 14 min of CPU, 10 x 4 km did not finish in 25 min). Four at a time;
# a folder already done is skipped (the stages resume). From uav-l2/.
export S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
NSEED=${NSEED:-3}
for s in $(seq 1 $NSEED); do for w in 3 4.5 6 8 10; do for l in 1.5 2 3 4 6; do
  sch=rfc; [ "$(echo "$l <= 3" | bc)" = 1 ] && sch=rf,rfc
  echo "$w $l $s $sch"; done; done; done |
  xargs -P 4 -L 1 bash -c '
    python3 tools/sat_strip.py --width $0 --length $1 --seed $2 --schemes $3 --work $S/SAT/w$0-l$1-s$2 --bin $S/BIN > $S/SAT/w$0-l$1-s$2.out 2>&1
    echo "w$0 l$1 s$2 exit $? $(date +%H:%M:%S)"'
python3 tools/sat_strip.py --summary "$S/SAT/w*-s*" --out docs/data/sat/strips.csv
