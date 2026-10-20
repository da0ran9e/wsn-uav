# from uav-l2/; item 106: the three fixes on the k4/k6/k8 mission maps (River prepared, 3 jobs)
set -e
S=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad
L=../logs/2026-10-20_0331-fixes
# 1 full D: k-medoids straight (re-run, checks the saved results), k-medoids curved, MEANDER with span 12
for ks in "4 2" "6 4" "8 4"; do set -- $ks
  python3 ../tools/runlog.py $L/full-k$1.md "
    python3 tools/mission.py --clusters $1 --seed $2 --work $S/MK/k$1 --bin $S/BIN --jobs 3 --schemes rf
    python3 tools/meander_mission.py --clusters $1 --seed $2 --work $S/KC/k$1 --bin $S/BIN --jobs 3 --partition kmedoids
    python3 tools/meander_mission.py --clusters $1 --seed $2 --work $S/MC/k$1 --bin $S/BIN --jobs 3 --span 12"
done
# 2 window Q = 400 kB: River again on copies (pass bitmaps reused) of all five
for ks in "4 2" "6 4" "8 4"; do set -- $ks
  for src in MK KC ML MM MC; do
    rm -rf $S/${src}w/k$1; mkdir -p $S/${src}w; cp -a $S/$src/k$1 $S/${src}w/k$1
    rm -rf $S/${src}w/k$1/plan*.txt $S/${src}w/k$1/plan*.log $S/${src}w/k$1/r*-rf-* $S/${src}w/k$1/r*-rf.log $S/${src}w/k$1/tr
  done
  python3 ../tools/runlog.py $L/window-k$1.md "
    python3 tools/mission.py --clusters $1 --seed $2 --work $S/MKw/k$1 --bin $S/BIN --jobs 3 --schemes rf --windowKB 400
    python3 tools/mission.py --clusters $1 --seed $2 --work $S/MLw/k$1 --bin $S/BIN --jobs 3 --schemes rf --partition lane --lane 4.5 --windowKB 400
    python3 tools/meander_mission.py --clusters $1 --seed $2 --work $S/KCw/k$1 --bin $S/BIN --jobs 3 --partition kmedoids --windowKB 400
    python3 tools/meander_mission.py --clusters $1 --seed $2 --work $S/MMw/k$1 --bin $S/BIN --jobs 3 --windowKB 400
    python3 tools/meander_mission.py --clusters $1 --seed $2 --work $S/MCw/k$1 --bin $S/BIN --jobs 3 --span 12 --windowKB 400"
done
echo "campaign done $(date +%H:%M:%S)"
