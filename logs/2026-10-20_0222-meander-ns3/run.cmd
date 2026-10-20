# from uav-l2/; MEANDER first, then LANE (mission.py --partition lane), River prepared only, 3 jobs
set -e
for ks in "4 2" "6 4" "8 4"; do set -- $ks
  echo "== meander k$1 seed $2 $(date +%H:%M:%S)"
  python3 tools/meander_mission.py --clusters $1 --seed $2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k$1 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --banks local
done
for ks in "4 2" "6 4" "8 4"; do set -- $ks
  echo "== lane k$1 seed $2 $(date +%H:%M:%S)"
  python3 tools/mission.py --clusters $1 --seed $2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/ML/k$1 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --partition lane --lane 4.5
done
echo "== done $(date +%H:%M:%S)"
