# SWL-k8-s11

- Bắt đầu: 2026-10-22 20:32:17, chạy 512 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 11 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k8-s11 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 627 land cells, 13298 nodes, 8 clusters [80, 80, 79, 79, 80, 80, 80, 69], route 30.3 km over 5 lanes at 30 deg, BS -390,-4000
curves: C1 2.94 km, CH 75 m off, k*rho 0.17, C2 4.49 km, CH 124 m off, k*rho 0.34, C3 2.39 km, CH 33 m off, k*rho 0.17, C4 4.80 km, CH 31 m off, k*rho 0.33, C5 2.25 km, CH 50 m off, k*rho 0.17, C6 4.37 km, CH 63 m off, k*rho 0.33, C7 2.47 km, CH 38 m off, k*rho 0.17, C8 6.64 km, CH 137 m off, k*rho 0.39
tour: 45.6 km, 912 s, order [(2, 0), (6, 0), (7, 0), (8, 0), (5, 1), (4, 1), (3, 1), (1, 1)]
  run 1 river-full: D 6615, 7/7 critical done, sim 13.0 s, wall 13 s, 19146 hops, 654 MAC give-ups, 0/181 gateway pairs with q < 0.5
  run 1 river-full: D 4747, 5/5 critical done, sim 14.2 s, wall 15 s, 19049 hops, 736 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 4784, 5/5 critical done, sim 24.1 s, wall 37 s, 59996 hops, 2122 MAC give-ups, 0/186 gateway pairs with q < 0.5
  run 1 river-full: D 5374, 7/7 critical done, sim 51.9 s, wall 72 s, 126891 hops, 3615 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 4536, 4/4 critical done, sim 19.4 s, wall 20 s, 33756 hops, 1468 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5957, 8/8 critical done, sim 19.1 s, wall 20 s, 36327 hops, 1070 MAC give-ups, 0/151 gateway pairs with q < 0.5
  run 1 river-full: D 5011, 7/7 critical done, sim 12.3 s, wall 12 s, 18593 hops, 567 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 6159, 7/7 critical done, sim 45.1 s, wall 62 s, 129962 hops, 3484 MAC give-ups, 0/132 gateway pairs with q < 0.5
```
