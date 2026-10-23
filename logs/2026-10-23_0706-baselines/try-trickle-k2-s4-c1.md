# try-trickle-k2-s4-c1

- Bắt đầu: 2026-10-23 07:10:50, chạy 157 s, mã thoát 0
- Thư mục: `/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VB/chordT1/k2-s4`

**Lệnh**

```bash
env LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN2/lib /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN2/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=plan1.txt --bits=pass1-bits --firstRun=1 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=trickle --out=/tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/tcheck/r1-t
```

**Kết quả**

```text
  run 1 t=0 s: 0 hops, 0 MAC give-ups, 0/7 critical done
  run 1 t=10 s: 118717 hops, 4575 MAC give-ups, 1/7 critical done
  run 1 t=20 s: 180684 hops, 7220 MAC give-ups, 6/7 critical done
  run 1 t=30 s: 201178 hops, 8036 MAC give-ups, 6/7 critical done
  run 1 t=40 s: 209920 hops, 8306 MAC give-ups, 6/7 critical done
plan: 13 Axe, 7 critical, 76 cells and 1603 nodes simulated, 4442 packets
channels: cells 11-17 (7-colour grid), 178 gateway pairs on 18-26, 104 pairs share a channel with a pair within 300 m
trickle: 4051 packets in 64 pages over 76 cells
run 1 trickle: D 4051, 7/7 critical done, sim 41.3 s, wall 157 s, 210292 hops, 8329 MAC give-ups, 0/178 gateway pairs with q < 0.5
```
