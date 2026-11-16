---
status: history
updated: 2026-11-16
---
# tree-lb-b0.1

- Bắt đầu: 2026-11-16 11:36:57, chạy 287 s, mã thoát 0
- Thư mục: `$S/DT/r100/R1/k8-s1`

**Lệnh**

```bash
LD_LIBRARY_PATH=$S/CAMP-BINX/lib $S/CAMP-BINX/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=$S/TREE/plans/lb1-b0.1.txt --bits=pass1-bits --firstRun=800101 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --repair=20  --out=$S/TREE/lb/lb-b0.1
```

**Kết quả**

```text
  run 800101 t=0 s: 0 hops, 0 MAC give-ups, 0/5 critical done
  run 800101 t=10 s: 115381 hops, 4943 MAC give-ups, 0/5 critical done
  run 800101 t=20 s: 224750 hops, 10011 MAC give-ups, 0/5 critical done
  run 800101 t=30 s: 304610 hops, 13769 MAC give-ups, 0/5 critical done
  run 800101 t=40 s: 349199 hops, 15602 MAC give-ups, 0/5 critical done
  run 800101 t=50 s: 372844 hops, 16547 MAC give-ups, 0/5 critical done
  run 800101 t=60 s: 389886 hops, 17066 MAC give-ups, 4/5 critical done
  run 800101 t=70 s: 391895 hops, 17183 MAC give-ups, 4/5 critical done
  run 800101 t=80 s: 394035 hops, 17283 MAC give-ups, 4/5 critical done
plan: 21 Axe, 5 critical, 75 cells and 1584 nodes simulated, 5071 packets
channels: cells 11-17 (7-colour grid), 176 gateway pairs on 18-26, 101 pairs share a channel with a pair within 300 m
run 800101 river-full: D 4040, 5/5 critical done, sim 86.7 s, wall 286 s, 395643 hops, 17350 MAC give-ups, 0/176 gateway pairs with q < 0.5
```
