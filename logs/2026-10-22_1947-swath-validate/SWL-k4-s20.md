# SWL-k4-s20

- Bắt đầu: 2026-10-22 20:59:15, chạy 229 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 4 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k4-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 312 land cells, 6617 nodes, 4 clusters [78, 80, 78, 76], route 16.8 km over 4 lanes at 40 deg, BS -217,-3250
curves: C1 4.76 km, CH 50 m off, k*rho 0.33, C2 2.51 km, CH 25 m off, k*rho 0.17, C3 3.94 km, CH 67 m off, k*rho 0.33, C4 5.65 km, CH 94 m off, k*rho 0.33
tour: 25.1 km, 502 s, order [(3, 0), (4, 1), (2, 1), (1, 1)]
  run 1 river-full: D 5847, 6/6 critical done, sim 9.7 s, wall 7 s, 9824 hops, 291 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5728, 6/6 critical done, sim 18.5 s, wall 11 s, 16643 hops, 730 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 5010, 4/4 critical done, sim 13.1 s, wall 7 s, 11656 hops, 361 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 7852, 7/7 critical done, sim 66.1 s, wall 71 s, 148880 hops, 3664 MAC give-ups, 0/130 gateway pairs with q < 0.5
```
