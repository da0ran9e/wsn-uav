# CT2-k8-s8

- Bắt đầu: 2026-10-22 21:37:04, chạy 150 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 8 --seed 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/CT2-k8-s8 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.7,0.9
```

**Kết quả**

```text
bearings: C1 66 deg (1900 m inside), C2 50 deg (1930 m inside), C3 46 deg (2135 m inside), C4 136 deg (1860 m inside), C5 10 deg (1925 m inside), C6 42 deg (1875 m inside), C7 100 deg (2010 m inside), C8 108 deg (1770 m inside)
chord-t: C1 6 deg, C2 50 deg, C3 86 deg, C4 136 deg, C5 152 deg, C6 42 deg, C7 30 deg, C8 108 deg
tour: 30.0 km, 600 s, order [(7, 0), (5, 0), (8, 1), (1, 1), (6, 0), (4, 1), (2, 1), (3, 1)]
  run 1 river-full: D 4302, 5/5 critical done, sim 12.4 s, wall 7 s, 13300 hops, 438 MAC give-ups, 0/143 gateway pairs with q < 0.5
  run 1 river-full: D 4596, 5/5 critical done, sim 15.9 s, wall 11 s, 20817 hops, 601 MAC give-ups, 0/157 gateway pairs with q < 0.5
  run 1 river-full: D 4571, 4/4 critical done, sim 24.7 s, wall 26 s, 51294 hops, 1569 MAC give-ups, 0/149 gateway pairs with q < 0.5
  run 1 river-full: D 4332, 7/7 critical done, sim 18.5 s, wall 17 s, 27203 hops, 1022 MAC give-ups, 0/184 gateway pairs with q < 0.5
  run 1 river-full: D 4121, 6/6 critical done, sim 18.0 s, wall 12 s, 19885 hops, 475 MAC give-ups, 0/159 gateway pairs with q < 0.5
  run 1 river-full: D 4717, 4/4 critical done, sim 12.0 s, wall 7 s, 16222 hops, 539 MAC give-ups, 0/111 gateway pairs with q < 0.5
  run 1 river-full: D 4141, 6/6 critical done, sim 14.3 s, wall 13 s, 19734 hops, 718 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 4458, 6/6 critical done, sim 37.4 s, wall 28 s, 52805 hops, 1599 MAC give-ups, 0/173 gateway pairs with q < 0.5
```
