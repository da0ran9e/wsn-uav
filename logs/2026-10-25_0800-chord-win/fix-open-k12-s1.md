# fix-open-k12-s1

- Bắt đầu: 2026-10-25 11:24:03, chạy 63 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 12 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env open --riverRepair 20 --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k12-s1
```

**Kết quả**

```text
bearings: C1 94 deg (1665 m inside), C2 146 deg (1980 m inside), C3 2 deg (1690 m inside), C4 94 deg (1775 m inside), C5 110 deg (1640 m inside), C6 114 deg (1760 m inside), C7 138 deg (1680 m inside), C8 162 deg (1725 m inside), C9 90 deg (1795 m inside), C10 114 deg (1820 m inside), C11 170 deg (2195 m inside), C12 144 deg (1685 m inside)
  run 1200101 river-full: D 4917, 7/7 critical done, sim 16.8 s, wall 8 s, 18010 hops, 491 MAC give-ups, 0/116 gateway pairs with q < 0.5
  run 1200102 river-full: D 5223, 6/6 critical done, sim 28.8 s, wall 16 s, 28943 hops, 1007 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1200104 river-full: D 4752, 3/3 critical done, sim 8.9 s, wall 3 s, 5978 hops, 209 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1200105 river-full: D 5602, 6/6 critical done, sim 13.1 s, wall 9 s, 17401 hops, 569 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1200106 river-full: D 4082, 4/4 critical done, sim 6.0 s, wall 2 s, 4333 hops, 89 MAC give-ups, 0/65 gateway pairs with q < 0.5
  run 1200107 river-full: D 4041, 3/3 critical done, sim 5.0 s, wall 2 s, 3730 hops, 46 MAC give-ups, 0/168 gateway pairs with q < 0.5
  run 1200103 river-full: D 4937, 5/5 critical done, sim 50.1 s, wall 32 s, 73518 hops, 2785 MAC give-ups, 0/159 gateway pairs with q < 0.5
  run 1200108 river-full: D 4588, 7/7 critical done, sim 15.5 s, wall 10 s, 17363 hops, 545 MAC give-ups, 0/150 gateway pairs with q < 0.5
  run 1200109 river-full: D 4668, 7/7 critical done, sim 10.9 s, wall 6 s, 11378 hops, 244 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1200110 river-full: D 4758, 6/6 critical done, sim 22.4 s, wall 9 s, 14685 hops, 551 MAC give-ups, 0/185 gateway pairs with q < 0.5
  run 1200111 river-full: D 5100, 7/7 critical done, sim 16.9 s, wall 11 s, 22990 hops, 725 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1200112 river-full: D 4581, 5/5 critical done, sim 23.4 s, wall 13 s, 28631 hops, 753 MAC give-ups, 0/151 gateway pairs with q < 0.5
```
