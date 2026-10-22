# SWL-k4-s2

- Bắt đầu: 2026-10-22 21:00:25, chạy 268 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k4-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 308 land cells, 6532 nodes, 4 clusters [68, 80, 80, 80], route 19.9 km over 4 lanes at 135 deg, BS -87,-2800
curves: C1 6.13 km, CH 63 m off, k*rho 0.33, C2 2.01 km, CH 39 m off, k*rho 0.17, C3 4.58 km, CH 39 m off, k*rho 0.33, C4 7.20 km, CH 55 m off, k*rho 0.33
tour: 27.9 km, 557 s, order [(4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 4041, 4/4 critical done, sim 12.0 s, wall 10 s, 19871 hops, 638 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 4470, 7/7 critical done, sim 42.1 s, wall 67 s, 126311 hops, 5210 MAC give-ups, 0/148 gateway pairs with q < 0.5
  run 1 river-full: D 5360, 7/7 critical done, sim 64.6 s, wall 79 s, 173438 hops, 7408 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 6118, 5/5 critical done, sim 9.8 s, wall 8 s, 13544 hops, 453 MAC give-ups, 0/146 gateway pairs with q < 0.5
```
