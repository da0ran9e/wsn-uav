# MK-k8-s11

- Bắt đầu: 2026-10-23 07:59:34, chạy 239 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 8 --seed 11 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k8-s11 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 627 land cells, 13298 nodes, 8 clusters [65, 80, 80, 80, 81, 80, 80, 81], BS -390,-4000
curves: C1 3.33 km, CH 14 m off, k*rho 0.96, C2 3.40 km, CH 58 m off, k*rho 0.96, C3 3.27 km, CH 92 m off, k*rho 0.88, C4 2.62 km, CH 122 m off, k*rho 1.00, C5 2.87 km, CH 311 m off, k*rho 1.00, C6 2.22 km, CH 74 m off, k*rho 0.97, C7 2.70 km, CH 197 m off, k*rho 0.98, C8 2.90 km, CH 80 m off, k*rho 0.96
tour: 38.9 km, 778 s, order [(8, 0), (7, 1), (5, 0), (3, 1), (1, 1), (2, 0), (4, 1), (6, 0)]
  run 1 river-full: D 7683, 7/7 critical done, sim 8.9 s, wall 6 s, 11103 hops, 331 MAC give-ups, 0/129 gateway pairs with q < 0.5
  run 1 river-full: D 7658, 7/7 critical done, sim 17.6 s, wall 11 s, 18685 hops, 517 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 7461, 8/8 critical done, sim 10.1 s, wall 9 s, 12617 hops, 357 MAC give-ups, 0/159 gateway pairs with q < 0.5
  run 1 river-full: D 6256, 7/7 critical done, sim 19.1 s, wall 11 s, 17515 hops, 563 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 6652, 6/6 critical done, sim 16.3 s, wall 10 s, 15349 hops, 490 MAC give-ups, 0/181 gateway pairs with q < 0.5
  run 1 river-full: D 6024, 4/4 critical done, sim 8.1 s, wall 3 s, 5112 hops, 143 MAC give-ups, 0/185 gateway pairs with q < 0.5
  run 1 river-full: D 5308, 5/5 critical done, sim 8.1 s, wall 6 s, 9768 hops, 322 MAC give-ups, 0/180 gateway pairs with q < 0.5
  run 1 river-full: D 6776, 5/5 critical done, sim 19.2 s, wall 20 s, 41821 hops, 2032 MAC give-ups, 0/156 gateway pairs with q < 0.5
```
