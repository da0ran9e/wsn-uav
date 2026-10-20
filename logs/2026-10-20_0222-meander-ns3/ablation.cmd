# from uav-l2/; MEANDER with parallel Banks: copies of MM/k* without plans and River results (pass bitmaps reused)
set -e
for ks in "4 2" "6 4" "8 4"; do set -- $ks
  rm -rf /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1; mkdir -p /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp; cp -a /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k$1 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1
  rm -f /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1/plan*.txt /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1/plan*.log /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1/r*-rf-* /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1/r*-rf.log
  echo "== meander parallel k$1 $(date +%H:%M:%S)"
  python3 tools/meander_mission.py --clusters $1 --seed $2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMp/k$1 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --banks parallel
done
echo "== done $(date +%H:%M:%S)"
