# Vòng 3: SWATH-K luồng 7 cell, k8-s10

- Bắt đầu: 2026-10-22 18:42:21, chạy 565 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW7-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --lane 7
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [79, 80, 80, 79, 80, 80, 75, 79], route 27.6 km over 5 lanes at 45 deg, BS 303,-3700
curves: C1 2.89 km, CH 79 m off, k*rho 0.17, C2 4.85 km, CH 26 m off, k*rho 0.33, C3 2.01 km, CH 11 m off, k*rho 0.16, C4 3.75 km, CH 92 m off, k*rho 0.33, C5 1.97 km, CH 89 m off, k*rho 0.17, C6 1.89 km, CH 75 m off, k*rho 0.17, C7 5.31 km, CH 16 m off, k*rho 0.33, C8 4.94 km, CH 7 m off, k*rho 0.33
tour: 42.0 km, 840 s, order [(4, 0), (5, 0), (8, 1), (7, 1), (6, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 2330, 5/5 critical done, sim 22.4 s, wall 25 s, 42125 hops, 1452 MAC give-ups, 0/118 gateway pairs with q < 0.5
  run 1 river-full: D 5081, 7/7 critical done, sim 38.8 s, wall 70 s, 91199 hops, 3178 MAC give-ups, 0/164 gateway pairs with q < 0.5
  run 1 river-full: D 4071, 7/7 critical done, sim 30.1 s, wall 49 s, 58381 hops, 1701 MAC give-ups, 0/185 gateway pairs with q < 0.5
  run 1 river-full: D 3513, 5/5 critical done, sim 20.4 s, wall 16 s, 21502 hops, 655 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 4051, 4/4 critical done, sim 18.4 s, wall 19 s, 21832 hops, 553 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 2355, 7/7 critical done, sim 13.1 s, wall 8 s, 11488 hops, 396 MAC give-ups, 0/143 gateway pairs with q < 0.5
  run 1 river-full: D 3843, 6/6 critical done, sim 30.6 s, wall 65 s, 86498 hops, 3359 MAC give-ups, 0/149 gateway pairs with q < 0.5
  run 1 river-full: D 3799, 6/6 critical done, sim 34.2 s, wall 83 s, 101268 hops, 3387 MAC give-ups, 0/172 gateway pairs with q < 0.5
```
