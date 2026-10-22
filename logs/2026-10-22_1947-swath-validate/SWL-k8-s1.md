# SWL-k8-s1

- Bắt đầu: 2026-10-22 20:32:17, chạy 457 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 1 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 8 clusters [80, 79, 68, 80, 80, 80, 80, 70], route 31.3 km over 5 lanes at 40 deg, BS 173,-3550
curves: C1 2.84 km, CH 17 m off, k*rho 0.16, C2 4.28 km, CH 59 m off, k*rho 0.33, C3 4.81 km, CH 69 m off, k*rho 0.33, C4 2.23 km, CH 36 m off, k*rho 0.17, C5 2.71 km, CH 11 m off, k*rho 0.15, C6 4.47 km, CH 37 m off, k*rho 0.33, C7 2.58 km, CH 143 m off, k*rho 0.17, C8 7.42 km, CH 14 m off, k*rho 0.33
tour: 45.8 km, 917 s, order [(1, 0), (2, 0), (3, 0), (4, 0), (8, 1), (7, 1), (6, 1), (5, 1)]
  run 1 river-full: D 5051, 5/5 critical done, sim 27.5 s, wall 26 s, 48703 hops, 1919 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5740, 6/6 critical done, sim 9.3 s, wall 5 s, 9679 hops, 290 MAC give-ups, 0/123 gateway pairs with q < 0.5
  run 1 river-full: D 5198, 5/5 critical done, sim 19.2 s, wall 14 s, 24714 hops, 937 MAC give-ups, 0/155 gateway pairs with q < 0.5
  run 1 river-full: D 6253, 5/5 critical done, sim 8.6 s, wall 8 s, 10435 hops, 282 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 5952, 3/3 critical done, sim 16.7 s, wall 13 s, 17597 hops, 666 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 5401, 6/6 critical done, sim 22.2 s, wall 10 s, 21337 hops, 775 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 5338, 8/8 critical done, sim 49.5 s, wall 86 s, 151226 hops, 4515 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 6608, 7/7 critical done, sim 39.2 s, wall 57 s, 127327 hops, 3677 MAC give-ups, 0/118 gateway pairs with q < 0.5
```
