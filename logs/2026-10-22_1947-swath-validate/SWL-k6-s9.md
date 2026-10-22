# SWL-k6-s9

- Bắt đầu: 2026-10-22 20:51:42, chạy 305 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 6 --seed 9 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k6-s9 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 446 land cells, 9459 nodes, 6 clusters [70, 80, 80, 76, 75, 65], route 24.2 km over 5 lanes at 25 deg, BS -303,-3700
curves: C1 5.42 km, CH 151 m off, k*rho 0.33, C2 4.53 km, CH 138 m off, k*rho 0.34, C3 2.33 km, CH 56 m off, k*rho 0.17, C4 3.91 km, CH 26 m off, k*rho 0.33, C5 1.97 km, CH 68 m off, k*rho 0.17, C6 6.15 km, CH 42 m off, k*rho 0.33
tour: 36.1 km, 722 s, order [(3, 0), (4, 0), (6, 1), (5, 1), (2, 1), (1, 1)]
  run 1 river-full: D 7100, 8/8 critical done, sim 36.6 s, wall 52 s, 94585 hops, 3474 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1 river-full: D 6385, 7/7 critical done, sim 61.1 s, wall 74 s, 147281 hops, 5767 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 5365, 6/6 critical done, sim 23.9 s, wall 29 s, 53094 hops, 1734 MAC give-ups, 0/163 gateway pairs with q < 0.5
  run 1 river-full: D 4473, 5/5 critical done, sim 16.3 s, wall 13 s, 23189 hops, 951 MAC give-ups, 0/163 gateway pairs with q < 0.5
  run 1 river-full: D 6690, 6/6 critical done, sim 12.8 s, wall 7 s, 15287 hops, 450 MAC give-ups, 0/112 gateway pairs with q < 0.5
  run 1 river-full: D 4602, 6/6 critical done, sim 17.5 s, wall 13 s, 24194 hops, 941 MAC give-ups, 0/161 gateway pairs with q < 0.5
```
