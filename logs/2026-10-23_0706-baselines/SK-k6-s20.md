# SK-k6-s20

- Bắt đầu: 2026-10-23 07:19:55, chạy 255 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k6-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --partition subch --pairs --src /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/HK/k6-s20 --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 462 land cells, 9798 nodes, 6 clusters [76, 78, 77, 77, 77, 77], BS -43,-3700
bearings: C1 174 deg (2130 m inside), C2 18 deg (1995 m inside), C3 172 deg (1950 m inside), C4 76 deg (2015 m inside), C5 140 deg (2210 m inside), C6 68 deg (2095 m inside)
tour: 23.8 km, 476 s, order [(1, 0), (2, 0), (5, 0), (6, 1), (4, 1), (3, 1)]
  run 1 river-full: D 4914, 6/6 critical done, sim 17.4 s, wall 22 s, 18667 hops, 559 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 5175, 5/5 critical done, sim 7.9 s, wall 8 s, 9162 hops, 162 MAC give-ups, 0/146 gateway pairs with q < 0.5
  run 1 river-full: D 4881, 5/5 critical done, sim 20.9 s, wall 36 s, 38973 hops, 1266 MAC give-ups, 0/180 gateway pairs with q < 0.5
  run 1 river-full: D 4574, 5/5 critical done, sim 16.6 s, wall 13 s, 25297 hops, 991 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 5530, 6/6 critical done, sim 23.9 s, wall 19 s, 35827 hops, 1073 MAC give-ups, 0/164 gateway pairs with q < 0.5
  run 1 river-full: D 5055, 6/6 critical done, sim 23.0 s, wall 15 s, 25506 hops, 845 MAC give-ups, 0/166 gateway pairs with q < 0.5
```
