# Vòng 1: MEANDER-K, cửa sổ theo critical cell, k8-s10

- Bắt đầu: 2026-10-22 18:09:21, chạy 326 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/MK-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 4 --meanderK --windowKB 400 --windowAt crit
```

**Kết quả**

```text
curves: C1 4.56 km, CH 22 m off, k*rho 0.95, C2 2.90 km, CH 121 m off, k*rho 0.99, C3 2.41 km, CH 10 m off, k*rho 0.94, C4 2.57 km, CH 55 m off, k*rho 0.87, C5 3.48 km, CH 126 m off, k*rho 0.96, C6 2.37 km, CH 211 m off, k*rho 0.99, C7 1.75 km, CH 194 m off, k*rho 0.98, C8 3.15 km, CH 75 m off, k*rho 0.95
tour: 39.7 km, 793 s, order [(8, 0), (6, 1), (4, 0), (5, 0), (3, 1), (2, 1), (1, 0), (7, 1)]
  run 1 river-full: D 8648, 8/8 critical done, sim 6.4 s, wall 7 s, 11405 hops, 287 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1 river-full: D 6153, 5/5 critical done, sim 11.2 s, wall 9 s, 12148 hops, 405 MAC give-ups, 0/188 gateway pairs with q < 0.5
  run 1 river-full: D 6144, 9/9 critical done, sim 25.6 s, wall 25 s, 37713 hops, 1082 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 5039, 6/6 critical done, sim 37.8 s, wall 45 s, 65817 hops, 2272 MAC give-ups, 0/196 gateway pairs with q < 0.5
  run 1 river-full: D 3763, 6/6 critical done, sim 13.7 s, wall 13 s, 22096 hops, 946 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 4061, 8/8 critical done, sim 42.4 s, wall 95 s, 142555 hops, 5505 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 5007, 7/7 critical done, sim 63.1 s, wall 104 s, 183213 hops, 6373 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 4012, 8/8 critical done, sim 93.6 s, wall 204 s, 348816 hops, 13434 MAC give-ups, 0/154 gateway pairs with q < 0.5
```
