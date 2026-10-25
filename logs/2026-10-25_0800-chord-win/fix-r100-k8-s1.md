# fix-r100-k8-s1

- Bắt đầu: 2026-10-25 10:42:07, chạy 1024 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env r100 --riverRepair 20 --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r100/k8-s1
```

**Kết quả**

```text
bearings: C1 20 deg (1625 m inside), C2 116 deg (1665 m inside), C3 22 deg (1725 m inside), C4 54 deg (1825 m inside), C5 88 deg (1660 m inside), C6 160 deg (1695 m inside), C7 172 deg (1840 m inside), C8 136 deg (2025 m inside)
  run 800101 river-full: D 4202, 5/5 critical done, sim 100.1 s, wall 216 s, 389357 hops, 18589 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 800103 river-full: D 4263, 7/7 critical done, sim 109.7 s, wall 212 s, 464381 hops, 20943 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 800102 river-full: D 4176, 9/9 critical done, sim 299.5 s, wall 494 s, 879300 hops, 47356 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 800104 river-full: D 4045, 4/4 critical done, sim 82.9 s, wall 115 s, 267790 hops, 12977 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 800105 river-full: D 4090, 4/4 critical done, sim 90.8 s, wall 125 s, 276101 hops, 10836 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 800107 river-full: D 4329, 5/5 critical done, sim 115.6 s, wall 149 s, 308808 hops, 17288 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800106 river-full: D 4116, 6/6 critical done, sim 83.4 s, wall 231 s, 368888 hops, 18550 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800108 river-full: D 4181, 5/5 critical done, sim 248.5 s, wall 255 s, 587704 hops, 21573 MAC give-ups, 0/116 gateway pairs with q < 0.5
```
