# SWL-k6-s11

- Bắt đầu: 2026-10-22 20:50:21, chạy 265 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 6 --seed 11 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k6-s11 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 453 land cells, 9608 nodes, 6 clusters [70, 80, 76, 75, 77, 75], route 24.1 km over 5 lanes at 35 deg, BS -433,-3250
curves: C1 5.19 km, CH 70 m off, k*rho 0.33, C2 2.35 km, CH 12 m off, k*rho 0.16, C3 4.12 km, CH 52 m off, k*rho 0.33, C4 2.19 km, CH 38 m off, k*rho 0.17, C5 5.21 km, CH 94 m off, k*rho 0.33, C6 5.03 km, CH 6 m off, k*rho 0.33
tour: 35.0 km, 700 s, order [(1, 0), (2, 0), (3, 0), (6, 1), (5, 1), (4, 1)]
  run 1 river-full: D 5687, 7/7 critical done, sim 25.4 s, wall 25 s, 45556 hops, 1788 MAC give-ups, 0/166 gateway pairs with q < 0.5
  run 1 river-full: D 6070, 7/7 critical done, sim 31.1 s, wall 34 s, 73749 hops, 2540 MAC give-ups, 0/134 gateway pairs with q < 0.5
  run 1 river-full: D 5103, 7/7 critical done, sim 15.6 s, wall 19 s, 29626 hops, 923 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 6613, 5/5 critical done, sim 9.5 s, wall 7 s, 9458 hops, 280 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 6033, 7/7 critical done, sim 27.9 s, wall 35 s, 61362 hops, 2293 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 7182, 5/5 critical done, sim 13.0 s, wall 9 s, 14299 hops, 504 MAC give-ups, 0/141 gateway pairs with q < 0.5
```
