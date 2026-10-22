# Vòng 3: SWATH-K luồng 8 cell, k8-s10

- Bắt đầu: 2026-10-22 18:42:21, chạy 676 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW8-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --lane 8
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [80, 78, 80, 78, 79, 79, 79, 79], route 24.3 km over 4 lanes at 120 deg, BS 303,-3700
curves: C1 2.64 km, CH 41 m off, k*rho 0.17, C2 4.62 km, CH 58 m off, k*rho 0.33, C3 1.60 km, CH 19 m off, k*rho 0.16, C4 4.36 km, CH 54 m off, k*rho 0.33, C5 1.96 km, CH 99 m off, k*rho 0.17, C6 1.61 km, CH 42 m off, k*rho 0.17, C7 4.81 km, CH 80 m off, k*rho 0.33, C8 2.74 km, CH 94 m off, k*rho 0.17
tour: 36.8 km, 736 s, order [(8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 3141, 6/6 critical done, sim 31.5 s, wall 50 s, 90543 hops, 3038 MAC give-ups, 0/127 gateway pairs with q < 0.5
  run 1 river-full: D 3121, 4/4 critical done, sim 5.3 s, wall 3 s, 3922 hops, 104 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 4171, 7/7 critical done, sim 84.0 s, wall 173 s, 226922 hops, 9403 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 5015, 9/9 critical done, sim 103.7 s, wall 234 s, 280478 hops, 12525 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 2459, 7/7 critical done, sim 10.4 s, wall 8 s, 12074 hops, 495 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 2782, 5/5 critical done, sim 12.1 s, wall 5 s, 8340 hops, 267 MAC give-ups, 0/163 gateway pairs with q < 0.5
  run 1 river-full: D 3841, 5/5 critical done, sim 22.3 s, wall 23 s, 45051 hops, 1405 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 1 river-full: D 3489, 5/5 critical done, sim 58.9 s, wall 118 s, 203814 hops, 5493 MAC give-ups, 0/150 gateway pairs with q < 0.5
```
