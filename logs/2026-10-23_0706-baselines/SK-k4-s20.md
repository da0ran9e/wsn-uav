# SK-k4-s20

- Bắt đầu: 2026-10-23 07:12:42, chạy 115 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 4 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k4-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --partition subch --pairs --src /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/HK/k4-s20 --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 312 land cells, 6617 nodes, 4 clusters [77, 79, 78, 78], BS -217,-3250
bearings: C1 106 deg (1870 m inside), C2 52 deg (2020 m inside), C3 102 deg (1715 m inside), C4 46 deg (2045 m inside)
tour: 16.1 km, 321 s, order [(3, 0), (4, 0), (2, 1), (1, 1)]
  run 1 river-full: D 6352, 4/4 critical done, sim 21.5 s, wall 15 s, 42619 hops, 1076 MAC give-ups, 0/97 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 28.9 s, wall 22 s, 48258 hops, 1683 MAC give-ups, 0/148 gateway pairs with q < 0.5
  run 1 river-full: D 4704, 5/5 critical done, sim 11.8 s, wall 6 s, 9987 hops, 359 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 3962, 6/6 critical done, sim 16.1 s, wall 15 s, 26553 hops, 718 MAC give-ups, 0/168 gateway pairs with q < 0.5
```
