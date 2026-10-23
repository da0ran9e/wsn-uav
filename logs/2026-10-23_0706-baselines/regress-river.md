# regress-river

- Bắt đầu: 2026-10-23 07:10:20, chạy 24 s, mã thoát 0
- Thư mục: `/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k2-s4`

**Lệnh**

```bash
env LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN2/lib /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN2/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=plan1.txt --bits=pass1-bits --firstRun=1 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --out=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/tcheck/r1-rf
```

**Kết quả**

```text
  run 1 t=0 s: 0 hops, 0 MAC give-ups, 0/7 critical done
  run 1 t=10 s: 23222 hops, 809 MAC give-ups, 4/7 critical done
  run 1 t=20 s: 40003 hops, 1359 MAC give-ups, 6/7 critical done
  run 1 t=30 s: 43069 hops, 1439 MAC give-ups, 6/7 critical done
plan: 16 Axe, 7 critical, 75 cells and 1628 nodes simulated, 5660 packets
channels: cells 11-17 (7-colour grid), 173 gateway pairs on 18-26, 91 pairs share a channel with a pair within 300 m
run 1 river-full: D 5001, 7/7 critical done, sim 39.7 s, wall 24 s, 45176 hops, 1564 MAC give-ups, 0/173 gateway pairs with q < 0.5
```
