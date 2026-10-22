# SWL-k8-s10

- Bắt đầu: 2026-10-22 20:40:49, chạy 343 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/VA/SWL-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --axeNear --routeBy latency
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [80, 80, 80, 76, 80, 80, 77, 79], route 31.0 km over 6 lanes at 45 deg, BS 303,-3700
curves: C1 4.14 km, CH 26 m off, k*rho 0.17, C2 4.34 km, CH 65 m off, k*rho 0.33, C3 2.45 km, CH 35 m off, k*rho 0.17, C4 3.88 km, CH 110 m off, k*rho 0.33, C5 2.06 km, CH 104 m off, k*rho 0.17, C6 4.64 km, CH 5 m off, k*rho 0.33, C7 4.27 km, CH 19 m off, k*rho 0.33, C8 5.27 km, CH 63 m off, k*rho 0.33
tour: 44.7 km, 893 s, order [(4, 0), (5, 0), (6, 0), (7, 0), (8, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 7713, 5/5 critical done, sim 13.4 s, wall 10 s, 23464 hops, 627 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 5725, 6/6 critical done, sim 9.4 s, wall 8 s, 11975 hops, 418 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 6670, 7/7 critical done, sim 18.9 s, wall 23 s, 42000 hops, 1670 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1 river-full: D 4989, 4/4 critical done, sim 6.0 s, wall 4 s, 6110 hops, 209 MAC give-ups, 0/184 gateway pairs with q < 0.5
  run 1 river-full: D 3745, 5/5 critical done, sim 21.1 s, wall 18 s, 31340 hops, 859 MAC give-ups, 0/176 gateway pairs with q < 0.5
  run 1 river-full: D 7227, 7/7 critical done, sim 32.6 s, wall 19 s, 35134 hops, 1139 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 6760, 4/4 critical done, sim 15.1 s, wall 5 s, 8124 hops, 263 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 5388, 5/5 critical done, sim 19.5 s, wall 17 s, 28467 hops, 1006 MAC give-ups, 0/170 gateway pairs with q < 0.5
```
