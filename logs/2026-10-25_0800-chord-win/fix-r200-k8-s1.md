# fix-r200-k8-s1

- Bắt đầu: 2026-10-25 10:42:07, chạy 848 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env r200 --riverRepair 20 --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/r200/k8-s1
```

**Kết quả**

```text
bearings: C1 20 deg (1625 m inside), C2 116 deg (1665 m inside), C3 22 deg (1725 m inside), C4 54 deg (1825 m inside), C5 88 deg (1660 m inside), C6 160 deg (1695 m inside), C7 172 deg (1840 m inside), C8 136 deg (2025 m inside)
  run 800101 river-full: D 5054, 5/5 critical done, sim 81.7 s, wall 177 s, 325736 hops, 13041 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 800103 river-full: D 4802, 7/7 critical done, sim 93.3 s, wall 179 s, 394954 hops, 16564 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 800104 river-full: D 4467, 4/4 critical done, sim 69.2 s, wall 92 s, 218606 hops, 9844 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 800102 river-full: D 5185, 9/9 critical done, sim 311.3 s, wall 510 s, 966225 hops, 46281 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 800105 river-full: D 4566, 4/4 critical done, sim 88.2 s, wall 112 s, 246661 hops, 8539 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 800107 river-full: D 5713, 5/5 critical done, sim 82.7 s, wall 113 s, 236713 hops, 11404 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800106 river-full: D 4587, 6/6 critical done, sim 76.3 s, wall 196 s, 311923 hops, 13729 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800108 river-full: D 4827, 5/5 critical done, sim 122.6 s, wall 174 s, 406495 hops, 15316 MAC give-ups, 0/119 gateway pairs with q < 0.5
```
