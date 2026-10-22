# SWL-k4-s21

- Bắt đầu: 2026-10-22 20:54:47, chạy 268 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 4 --seed 21 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k4-s21 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 305 land cells, 6469 nodes, 4 clusters [80, 80, 80, 65], route 19.0 km over 4 lanes at 65 deg, BS -43,-3100
curves: C1 2.77 km, CH 54 m off, k*rho 0.17, C2 5.15 km, CH 55 m off, k*rho 0.33, C3 2.25 km, CH 114 m off, k*rho 0.17, C4 8.87 km, CH 54 m off, k*rho 0.33
tour: 26.6 km, 532 s, order [(4, 0), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 5927, 9/9 critical done, sim 13.6 s, wall 14 s, 23653 hops, 735 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 8123, 7/7 critical done, sim 24.0 s, wall 26 s, 45648 hops, 1816 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 4308, 5/5 critical done, sim 22.9 s, wall 28 s, 60922 hops, 2164 MAC give-ups, 0/142 gateway pairs with q < 0.5
  run 1 river-full: D 7766, 7/7 critical done, sim 62.1 s, wall 65 s, 156118 hops, 5155 MAC give-ups, 0/120 gateway pairs with q < 0.5
```
