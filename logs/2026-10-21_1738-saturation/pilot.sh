#!/bin/bash
# Item 120 pilot: four strips (cells across x km), seed 1, through deploy, pass and River (rf, 400 kB window), to time
# the runs and see whether a saturation signal shows. Four at a time (4 CPUs). From uav-l2/.
export S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
printf "%s\n" "4.5 2" "6 2" "6 4" "10 4" | xargs -P 4 -L 1 bash -c '
  python3 tools/sat_strip.py --width $0 --length $1 --seed 1 --work $S/SAT/w$0-l$1-s1 --bin $S/BIN > $S/SAT/w$0-l$1-s1.out 2>&1
  echo "w$0 l$1 exit $? $(date +%H:%M:%S)"'
