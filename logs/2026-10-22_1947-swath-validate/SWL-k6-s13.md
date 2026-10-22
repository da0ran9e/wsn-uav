# SWL-k6-s13

- Bắt đầu: 2026-10-22 20:45:33, chạy 288 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 6 --seed 13 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k6-s13 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 450 land cells, 9544 nodes, 6 clusters [74, 80, 80, 76, 80, 60], route 24.1 km over 5 lanes at 45 deg, BS 520,-3100
curves: C1 2.81 km, CH 84 m off, k*rho 0.17, C2 4.87 km, CH 7 m off, k*rho 0.33, C3 2.69 km, CH 84 m off, k*rho 0.17, C4 3.92 km, CH 77 m off, k*rho 0.33, C5 2.20 km, CH 38 m off, k*rho 0.17, C6 7.60 km, CH 84 m off, k*rho 0.33
tour: 35.6 km, 713 s, order [(4, 0), (6, 1), (5, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 6535, 8/8 critical done, sim 15.9 s, wall 16 s, 29881 hops, 1292 MAC give-ups, 0/134 gateway pairs with q < 0.5
  run 1 river-full: D 5947, 7/7 critical done, sim 21.9 s, wall 17 s, 32547 hops, 1224 MAC give-ups, 0/151 gateway pairs with q < 0.5
  run 1 river-full: D 5900, 7/7 critical done, sim 23.3 s, wall 20 s, 42050 hops, 1622 MAC give-ups, 0/123 gateway pairs with q < 0.5
  run 1 river-full: D 6342, 7/7 critical done, sim 23.1 s, wall 30 s, 52034 hops, 2040 MAC give-ups, 0/173 gateway pairs with q < 0.5
  run 1 river-full: D 5529, 5/5 critical done, sim 5.7 s, wall 4 s, 6784 hops, 174 MAC give-ups, 0/119 gateway pairs with q < 0.5
  run 1 river-full: D 5139, 9/9 critical done, sim 27.6 s, wall 44 s, 75580 hops, 2588 MAC give-ups, 0/162 gateway pairs with q < 0.5
```
