# SWL-k8-s8

- Bắt đầu: 2026-10-22 20:39:54, chạy 339 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k8-s8 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 600 land cells, 12725 nodes, 8 clusters [80, 63, 80, 77, 74, 75, 78, 73], route 29.1 km over 5 lanes at 85 deg, BS 87,-3850
curves: C1 3.04 km, CH 9 m off, k*rho 0.16, C2 5.40 km, CH 69 m off, k*rho 0.33, C3 2.11 km, CH 110 m off, k*rho 0.17, C4 4.18 km, CH 57 m off, k*rho 0.33, C5 2.39 km, CH 35 m off, k*rho 0.17, C6 4.15 km, CH 64 m off, k*rho 0.33, C7 2.46 km, CH 150 m off, k*rho 0.17, C8 5.38 km, CH 75 m off, k*rho 0.36
tour: 43.5 km, 870 s, order [(7, 1), (8, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 4315, 3/3 critical done, sim 15.9 s, wall 8 s, 21893 hops, 443 MAC give-ups, 0/101 gateway pairs with q < 0.5
  run 1 river-full: D 4029, 5/5 critical done, sim 34.7 s, wall 37 s, 70990 hops, 2303 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 6069, 4/4 critical done, sim 12.5 s, wall 10 s, 17289 hops, 780 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 1 river-full: D 5362, 7/7 critical done, sim 8.2 s, wall 7 s, 10805 hops, 272 MAC give-ups, 0/157 gateway pairs with q < 0.5
  run 1 river-full: D 5492, 9/9 critical done, sim 47.5 s, wall 68 s, 126032 hops, 3923 MAC give-ups, 0/168 gateway pairs with q < 0.5
  run 1 river-full: D 6517, 6/6 critical done, sim 11.0 s, wall 10 s, 14800 hops, 584 MAC give-ups, 0/169 gateway pairs with q < 0.5
  run 1 river-full: D 5259, 4/4 critical done, sim 15.7 s, wall 7 s, 13487 hops, 396 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 8136, 4/4 critical done, sim 19.3 s, wall 6 s, 11001 hops, 607 MAC give-ups, 0/122 gateway pairs with q < 0.5
```
