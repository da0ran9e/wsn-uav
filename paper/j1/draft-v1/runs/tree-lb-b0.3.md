---
status: history
updated: 2026-11-16
---
# tree-lb-b0.3

- Bắt đầu: 2026-11-16 11:36:57, chạy 268 s, mã thoát 0
- Thư mục: `$S/DT/r100/R1/k8-s1`

**Lệnh**

```bash
LD_LIBRARY_PATH=$S/CAMP-BINX/lib $S/CAMP-BINX/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=$S/TREE/plans/lb1-b0.3.txt --bits=pass1-bits --firstRun=800101 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --repair=20  --out=$S/TREE/lb/lb-b0.3
```

**Kết quả**

```text
  run 800101 t=0 s: 0 hops, 0 MAC give-ups, 0/5 critical done
  run 800101 t=10 s: 115104 hops, 4691 MAC give-ups, 0/5 critical done
  run 800101 t=20 s: 220140 hops, 9092 MAC give-ups, 0/5 critical done
  run 800101 t=30 s: 290417 hops, 12114 MAC give-ups, 0/5 critical done
  run 800101 t=40 s: 330804 hops, 13648 MAC give-ups, 0/5 critical done
  run 800101 t=50 s: 353861 hops, 14505 MAC give-ups, 0/5 critical done
  run 800101 t=60 s: 371176 hops, 15124 MAC give-ups, 0/5 critical done
  run 800101 t=70 s: 375920 hops, 15400 MAC give-ups, 4/5 critical done
  run 800101 t=80 s: 378038 hops, 15503 MAC give-ups, 4/5 critical done
plan: 21 Axe, 5 critical, 75 cells and 1584 nodes simulated, 5071 packets
channels: cells 11-17 (7-colour grid), 176 gateway pairs on 18-26, 101 pairs share a channel with a pair within 300 m
run 800101 river-full: D 4040, 5/5 critical done, sim 83.2 s, wall 268 s, 378890 hops, 15534 MAC give-ups, 0/176 gateway pairs with q < 0.5
```
