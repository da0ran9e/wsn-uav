# SK-k6-s11

- Bắt đầu: 2026-10-23 07:14:38, chạy 318 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 11 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SK/k6-s11 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --partition subch --pairs --src /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/HK/k6-s11 --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 453 land cells, 9608 nodes, 6 clusters [68, 83, 76, 75, 77, 74], BS -433,-3250
bearings: C1 90 deg (2095 m inside), C2 78 deg (2000 m inside), C3 14 deg (1700 m inside), C4 144 deg (1950 m inside), C5 30 deg (1855 m inside), C6 86 deg (2250 m inside)
tour: 24.4 km, 487 s, order [(5, 0), (6, 0), (2, 1), (3, 1), (4, 1), (1, 1)]
  run 1 river-full: D 5039, 4/4 critical done, sim 24.8 s, wall 28 s, 35155 hops, 1179 MAC give-ups, 0/128 gateway pairs with q < 0.5
  run 1 river-full: D 4662, 5/5 critical done, sim 21.1 s, wall 35 s, 28141 hops, 986 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 1 river-full: D 5139, 4/4 critical done, sim 7.5 s, wall 8 s, 6667 hops, 209 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 4439, 7/7 critical done, sim 16.9 s, wall 28 s, 22869 hops, 651 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 4077, 7/7 critical done, sim 32.1 s, wall 65 s, 56734 hops, 1912 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5134, 6/6 critical done, sim 17.2 s, wall 33 s, 34531 hops, 715 MAC give-ups, 0/175 gateway pairs with q < 0.5
```
