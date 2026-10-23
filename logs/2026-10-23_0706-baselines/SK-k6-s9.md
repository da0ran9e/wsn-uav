# SK-k6-s9

- Bắt đầu: 2026-10-23 07:22:31, chạy 205 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 9 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k6-s9 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --partition subch --pairs --src /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/HK/k6-s9 --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 446 land cells, 9459 nodes, 6 clusters [75, 74, 70, 78, 73, 76], BS -303,-3700
bearings: C1 118 deg (1720 m inside), C2 22 deg (2145 m inside), C3 108 deg (1925 m inside), C4 90 deg (2095 m inside), C5 118 deg (2075 m inside), C6 26 deg (1770 m inside)
tour: 24.5 km, 490 s, order [(5, 0), (6, 0), (2, 0), (1, 1), (3, 0), (4, 1)]
  run 1 river-full: D 4835, 5/5 critical done, sim 17.1 s, wall 14 s, 28846 hops, 1142 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 4333, 5/5 critical done, sim 24.4 s, wall 14 s, 27381 hops, 817 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 4781, 7/7 critical done, sim 17.5 s, wall 17 s, 32088 hops, 1078 MAC give-ups, 0/138 gateway pairs with q < 0.5
  run 1 river-full: D 4852, 4/4 critical done, sim 11.9 s, wall 5 s, 10227 hops, 351 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 4800, 7/7 critical done, sim 36.2 s, wall 32 s, 58830 hops, 1820 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 5401, 5/5 critical done, sim 27.4 s, wall 16 s, 36711 hops, 776 MAC give-ups, 0/130 gateway pairs with q < 0.5
```
