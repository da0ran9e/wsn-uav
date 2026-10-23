# SK-k6-s13

- Bắt đầu: 2026-10-23 07:17:55, chạy 276 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 13 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k6-s13 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --partition subch --pairs --src /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/HK/k6-s13 --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 450 land cells, 9544 nodes, 6 clusters [76, 74, 79, 71, 74, 76], BS 520,-3100
bearings: C1 130 deg (1750 m inside), C2 104 deg (1815 m inside), C3 154 deg (1465 m inside), C4 118 deg (1490 m inside), C5 102 deg (1855 m inside), C6 130 deg (2220 m inside)
tour: 24.5 km, 491 s, order [(4, 0), (5, 0), (3, 1), (6, 0), (2, 1), (1, 1)]
  run 1 river-full: D 4529, 6/6 critical done, sim 10.3 s, wall 19 s, 18477 hops, 667 MAC give-ups, 0/124 gateway pairs with q < 0.5
  run 1 river-full: D 4130, 7/7 critical done, sim 18.2 s, wall 37 s, 31147 hops, 778 MAC give-ups, 0/157 gateway pairs with q < 0.5
  run 1 river-full: D 3984, 4/4 critical done, sim 15.8 s, wall 12 s, 14444 hops, 574 MAC give-ups, 0/120 gateway pairs with q < 0.5
  run 1 river-full: D 4895, 6/6 critical done, sim 17.4 s, wall 23 s, 18917 hops, 722 MAC give-ups, 0/146 gateway pairs with q < 0.5
  run 1 river-full: D 4596, 8/8 critical done, sim 26.9 s, wall 79 s, 64267 hops, 2114 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 5452, 5/5 critical done, sim 17.5 s, wall 31 s, 29196 hops, 878 MAC give-ups, 0/157 gateway pairs with q < 0.5
```
