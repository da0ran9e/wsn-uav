# River prepared with --trace for the 6 MEANDER clusters of k4 (same binary and plan as logs/2026-10-20_0222-meander-ns3)
cd /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k4
for k in 1 2 3 4 5 6; do
  echo "c$k"; LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/lib /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/river-bin --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv \
    --gateways=c$k-gateways-s35.csv --plan=plan$k.txt --bits=pass$k-bits --firstRun=1 --runs=1 --limit=900 \
    --gwSelect=quality --colours=7 --scheme=river --prep=full --out=tr/r$k --trace=tr/t$k 2>&1 | tail -1 &
  [ $k -eq 3 ] && wait
done; wait
for k in 1 2 3 4 5 6; do cmp <(cut -d, -f1-9 r$k-rf-crit.csv) <(cut -d, -f1-9 tr/r$k-crit.csv) && echo "c$k crit identical"; done
