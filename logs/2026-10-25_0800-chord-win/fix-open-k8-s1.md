# fix-open-k8-s1

- Bắt đầu: 2026-10-25 11:24:02, chạy 45 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env open --riverRepair 20 --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k8-s1
```

**Kết quả**

```text
bearings: C1 20 deg (1625 m inside), C2 116 deg (1665 m inside), C3 22 deg (1725 m inside), C4 54 deg (1825 m inside), C5 88 deg (1660 m inside), C6 160 deg (1695 m inside), C7 172 deg (1840 m inside), C8 136 deg (2025 m inside)
  run 800101 river-full: D 5153, 5/5 critical done, sim 10.9 s, wall 7 s, 13739 hops, 418 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 800103 river-full: D 4897, 7/7 critical done, sim 17.8 s, wall 7 s, 14029 hops, 538 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 800104 river-full: D 4717, 4/4 critical done, sim 18.6 s, wall 4 s, 9560 hops, 507 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 800105 river-full: D 4654, 4/4 critical done, sim 13.2 s, wall 4 s, 7873 hops, 175 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 800102 river-full: D 5532, 9/9 critical done, sim 34.6 s, wall 28 s, 51302 hops, 1560 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 800106 river-full: D 4591, 6/6 critical done, sim 23.2 s, wall 7 s, 12149 hops, 448 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800107 river-full: D 5833, 5/5 critical done, sim 4.9 s, wall 3 s, 5445 hops, 141 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800108 river-full: D 5226, 5/5 critical done, sim 33.7 s, wall 14 s, 31569 hops, 1067 MAC give-ups, 0/120 gateway pairs with q < 0.5
```
