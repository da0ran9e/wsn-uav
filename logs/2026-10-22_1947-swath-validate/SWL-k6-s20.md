# SWL-k6-s20

- Bắt đầu: 2026-10-22 20:46:32, chạy 309 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 6 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k6-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 462 land cells, 9798 nodes, 6 clusters [74, 80, 75, 80, 80, 73], route 25.2 km over 5 lanes at 40 deg, BS -43,-3700
curves: C1 5.96 km, CH 117 m off, k*rho 0.34, C2 2.12 km, CH 4 m off, k*rho 0.15, C3 4.13 km, CH 69 m off, k*rho 0.33, C4 2.79 km, CH 92 m off, k*rho 0.17, C5 3.87 km, CH 32 m off, k*rho 0.33, C6 6.40 km, CH 22 m off, k*rho 0.33
tour: 37.2 km, 743 s, order [(1, 0), (3, 0), (4, 0), (6, 1), (5, 1), (2, 0)]
  run 1 river-full: D 5043, 5/5 critical done, sim 16.1 s, wall 11 s, 18344 hops, 698 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 5877, 8/8 critical done, sim 18.0 s, wall 14 s, 25879 hops, 787 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 5366, 6/6 critical done, sim 6.0 s, wall 4 s, 8017 hops, 207 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 6587, 6/6 critical done, sim 11.7 s, wall 14 s, 24092 hops, 801 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 5011, 4/4 critical done, sim 10.7 s, wall 7 s, 11578 hops, 410 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4980, 8/8 critical done, sim 74.3 s, wall 86 s, 151830 hops, 5392 MAC give-ups, 0/170 gateway pairs with q < 0.5
```
