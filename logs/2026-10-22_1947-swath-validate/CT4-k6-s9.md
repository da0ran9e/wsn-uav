# CT4-k6-s9

- Bắt đầu: 2026-10-22 22:30:49, chạy 218 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 9 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/CT4-k6-s9 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.5,0.8
```

**Kết quả**

```text
bearings: C1 174 deg (1940 m inside), C2 92 deg (2195 m inside), C3 146 deg (2265 m inside), C4 174 deg (2745 m inside), C5 76 deg (1880 m inside), C6 112 deg (1825 m inside)
chord-t: C1 4 deg, C2 62 deg, C3 88 deg, C4 14 deg, C5 96 deg, C6 96 deg
tour: 22.8 km, 456 s, order [(4, 0), (2, 0), (1, 1), (5, 1), (6, 0), (3, 1)]
  run 1 river-full: D 4322, 6/6 critical done, sim 14.9 s, wall 16 s, 26261 hops, 991 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 4046, 7/7 critical done, sim 46.1 s, wall 40 s, 76817 hops, 2576 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 5141, 7/7 critical done, sim 72.2 s, wall 85 s, 176177 hops, 6870 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 3883, 4/4 critical done, sim 9.3 s, wall 4 s, 9838 hops, 347 MAC give-ups, 0/117 gateway pairs with q < 0.5
  run 1 river-full: D 3854, 4/4 critical done, sim 18.1 s, wall 8 s, 15992 hops, 452 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 3996, 7/7 critical done, sim 28.3 s, wall 44 s, 83474 hops, 2634 MAC give-ups, 0/142 gateway pairs with q < 0.5
```
