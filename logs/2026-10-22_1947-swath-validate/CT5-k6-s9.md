# CT5-k6-s9

- Bắt đầu: 2026-10-22 22:55:34, chạy 217 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 9 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/CT5-k6-s9 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.5,0.6
```

**Kết quả**

```text
bearings: C1 174 deg (1940 m inside), C2 92 deg (2195 m inside), C3 146 deg (2265 m inside), C4 174 deg (2745 m inside), C5 76 deg (1880 m inside), C6 112 deg (1825 m inside)
chord-t: C1 24 deg, C2 132 deg, C3 88 deg, C4 14 deg, C5 16 deg, C6 32 deg
tour: 22.5 km, 449 s, order [(5, 1), (3, 0), (6, 0), (1, 0), (2, 1), (4, 1)]
  run 1 river-full: D 3973, 6/6 critical done, sim 22.7 s, wall 24 s, 43044 hops, 1387 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 4046, 7/7 critical done, sim 46.1 s, wall 39 s, 76817 hops, 2576 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 3106, 7/7 critical done, sim 76.1 s, wall 91 s, 207211 hops, 8314 MAC give-ups, 0/128 gateway pairs with q < 0.5
  run 1 river-full: D 4113, 4/4 critical done, sim 12.6 s, wall 6 s, 15276 hops, 269 MAC give-ups, 0/108 gateway pairs with q < 0.5
  run 1 river-full: D 3532, 4/4 critical done, sim 19.2 s, wall 5 s, 9093 hops, 329 MAC give-ups, 0/145 gateway pairs with q < 0.5
  run 1 river-full: D 3996, 7/7 critical done, sim 28.3 s, wall 45 s, 83474 hops, 2634 MAC give-ups, 0/142 gateway pairs with q < 0.5
```
