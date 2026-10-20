# trace

**Lệnh**

```bash
# River prepared with --trace for the 6 MEANDER clusters of k4 (same binary and plan as logs/2026-10-20_0222-meander-ns3)
cd /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MM/k4
for k in 1 2 3 4 5 6; do
  echo "c$k"; LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/lib /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/river-bin --nodes=c$k-nodes-s35.csv --routes=c$k-routes-s35.csv \
    --gateways=c$k-gateways-s35.csv --plan=plan$k.txt --bits=pass$k-bits --firstRun=1 --runs=1 --limit=900 \
    --gwSelect=quality --colours=7 --scheme=river --prep=full --out=tr/r$k --trace=tr/t$k 2>&1 | tail -1 &
  [ $k -eq 3 ] && wait
done; wait
for k in 1 2 3 4 5 6; do cmp <(cut -d, -f1-9 r$k-rf-crit.csv) <(cut -d, -f1-9 tr/r$k-crit.csv) && echo "c$k crit identical"; done
```

**Kết quả**

```text
c1
c2
c3
run 1 river-full: D 4655, 3/3 critical done, sim 39.8 s, wall 29 s, 104033 hops, 3581 MAC give-ups, 0/60 gateway pairs with q < 0.5
run 1 river-full: D 5706, 7/7 critical done, sim 70.1 s, wall 77 s, 168572 hops, 5757 MAC give-ups, 0/139 gateway pairs with q < 0.5
run 1 river-full: D 5427, 4/4 critical done, sim 77.3 s, wall 90 s, 195068 hops, 7664 MAC give-ups, 0/131 gateway pairs with q < 0.5
c4
c5
c6
run 1 river-full: D 2277, 2/2 critical done, sim 1.6 s, wall 0 s, 806 hops, 22 MAC give-ups, 0/24 gateway pairs with q < 0.5
run 1 river-full: D 2697, 4/4 critical done, sim 4.6 s, wall 1 s, 2300 hops, 60 MAC give-ups, 0/77 gateway pairs with q < 0.5
run 1 river-full: D 6836, 6/6 critical done, sim 115.0 s, wall 211 s, 367602 hops, 12394 MAC give-ups, 0/172 gateway pairs with q < 0.5
c1 crit identical
c2 crit identical
c3 crit identical
c4 crit identical
c5 crit identical
c6 crit identical
```
