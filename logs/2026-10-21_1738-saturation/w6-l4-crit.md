# w6-l4-crit

- Bắt đầu: 2026-10-21 18:13:11, chạy 86 s, mã thoát 0
- Thư mục: `/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/SAT/w6-l4-s1`

**Lệnh**

```bash
LD_LIBRARY_PATH=/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/lib /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=plan1-crit.txt --bits=pass1-bits --firstRun=1 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --out=r1-rfc
```

**Kết quả**

```text
  run 1 t=0 s: 0 hops, 0 MAC give-ups, 0/10 critical done
  run 1 t=10 s: 31019 hops, 1326 MAC give-ups, 8/10 critical done
  run 1 t=20 s: 40481 hops, 1694 MAC give-ups, 9/10 critical done
plan: 47 Axe, 10 critical, 160 cells and 3394 nodes simulated, 9227 packets
channels: cells 11-17 (7-colour grid), 420 gateway pairs on 18-26, 292 pairs share a channel with a pair within 300 m
run 1 river-full: D 8209, 10/10 critical done, sim 24.8 s, wall 86 s, 41354 hops, 1729 MAC give-ups, 0/420 gateway pairs with q < 0.5
```
