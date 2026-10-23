# MK-k8-s8

- Bắt đầu: 2026-10-23 08:03:33, chạy 268 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 8 --seed 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k8-s8 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 600 land cells, 12725 nodes, 8 clusters [80, 79, 74, 74, 80, 74, 80, 59], BS 87,-3850
curves: C1 2.75 km, CH 106 m off, k*rho 0.96, C2 2.63 km, CH 108 m off, k*rho 0.85, C3 2.20 km, CH 351 m off, k*rho 0.98, C4 2.27 km, CH 106 m off, k*rho 0.77, C5 3.67 km, CH 33 m off, k*rho 0.73, C6 3.17 km, CH 238 m off, k*rho 1.00, C7 4.06 km, CH 176 m off, k*rho 0.90, C8 2.98 km, CH 63 m off, k*rho 0.95
tour: 38.8 km, 775 s, order [(7, 0), (3, 1), (1, 0), (4, 0), (6, 1), (2, 1), (5, 0), (8, 1)]
  run 1 river-full: D 6104, 6/6 critical done, sim 12.4 s, wall 6 s, 10335 hops, 366 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 6513, 7/7 critical done, sim 13.4 s, wall 9 s, 15078 hops, 341 MAC give-ups, 0/166 gateway pairs with q < 0.5
  run 1 river-full: D 5314, 5/5 critical done, sim 22.7 s, wall 19 s, 35668 hops, 1210 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1 river-full: D 8352, 7/7 critical done, sim 15.2 s, wall 13 s, 20415 hops, 669 MAC give-ups, 0/176 gateway pairs with q < 0.5
  run 1 river-full: D 7217, 4/4 critical done, sim 4.3 s, wall 2 s, 4046 hops, 112 MAC give-ups, 0/123 gateway pairs with q < 0.5
  run 1 river-full: D 4777, 6/6 critical done, sim 29.1 s, wall 35 s, 64351 hops, 1616 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 1 river-full: D 5763, 3/3 critical done, sim 10.6 s, wall 4 s, 9103 hops, 265 MAC give-ups, 0/109 gateway pairs with q < 0.5
  run 1 river-full: D 7497, 5/5 critical done, sim 39.9 s, wall 30 s, 84894 hops, 3121 MAC give-ups, 0/101 gateway pairs with q < 0.5
```
