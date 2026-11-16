---
status: history
updated: 2026-11-16
---
# tree-lbs-b0.1

- Bắt đầu: 2026-11-16 11:37:48, chạy 252 s, mã thoát 0
- Thư mục: `$S/DT/r100/R1/k8-s1`

**Lệnh**

```bash
LD_LIBRARY_PATH=$S/CAMP-BINX/lib $S/CAMP-BINX/river-bin --nodes=c1-nodes-s35.csv --routes=c1-routes-s35.csv --gateways=c1-gateways-s35.csv --plan=$S/TREE/plans/lbs1-b0.1.txt --bits=pass1-bits --firstRun=800101 --runs=1 --limit=900 --gwSelect=quality --colours=7 --scheme=river --prep=full --repair=20 --tree=true --out=$S/TREE/lb/lbs-b0.1
```

**Kết quả**

```text
  run 800101 t=0 s: 0 hops, 0 MAC give-ups, 0/5 critical done
  run 800101 t=10 s: 106994 hops, 4942 MAC give-ups, 0/5 critical done
  run 800101 t=20 s: 184816 hops, 8674 MAC give-ups, 0/5 critical done
  run 800101 t=30 s: 230964 hops, 11073 MAC give-ups, 0/5 critical done
  run 800101 t=40 s: 268540 hops, 13037 MAC give-ups, 0/5 critical done
  run 800101 t=50 s: 302638 hops, 14649 MAC give-ups, 0/5 critical done
  run 800101 t=60 s: 327753 hops, 15649 MAC give-ups, 0/5 critical done
  run 800101 t=70 s: 340616 hops, 16299 MAC give-ups, 2/5 critical done
  run 800101 t=80 s: 344476 hops, 16490 MAC give-ups, 4/5 critical done
plan: 21 Axe, 5 critical, 75 cells and 1584 nodes simulated, 5071 packets
channels: cells 11-17 (7-colour grid), 176 gateway pairs on 18-26, 101 pairs share a channel with a pair within 300 m
tree: 37 trees, 146 relays below the roots, 549 cell hops as member paths, 398 as trees
run 800101 river-full: D 4040, 5/5 critical done, sim 84.2 s, wall 252 s, 345512 hops, 16530 MAC give-ups, 0/176 gateway pairs with q < 0.5
```
