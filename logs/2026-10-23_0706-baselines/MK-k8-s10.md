# MK-k8-s10

- Bắt đầu: 2026-10-23 07:55:38, chạy 236 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [80, 80, 80, 80, 80, 80, 72, 80], BS 303,-3700
curves: C1 4.56 km, CH 22 m off, k*rho 0.95, C2 2.90 km, CH 121 m off, k*rho 0.99, C3 2.41 km, CH 10 m off, k*rho 0.94, C4 2.57 km, CH 55 m off, k*rho 0.87, C5 3.48 km, CH 126 m off, k*rho 0.96, C6 2.37 km, CH 211 m off, k*rho 0.99, C7 1.75 km, CH 194 m off, k*rho 0.98, C8 3.15 km, CH 75 m off, k*rho 0.95
tour: 39.7 km, 793 s, order [(8, 0), (6, 1), (4, 0), (5, 0), (3, 1), (2, 1), (1, 0), (7, 1)]
  run 1 river-full: D 4659, 3/3 critical done, sim 4.2 s, wall 2 s, 3384 hops, 103 MAC give-ups, 0/159 gateway pairs with q < 0.5
  run 1 river-full: D 10036, 6/6 critical done, sim 5.6 s, wall 4 s, 6278 hops, 127 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1 river-full: D 5664, 6/6 critical done, sim 29.2 s, wall 19 s, 37261 hops, 1416 MAC give-ups, 0/196 gateway pairs with q < 0.5
  run 1 river-full: D 6043, 7/7 critical done, sim 14.3 s, wall 20 s, 38592 hops, 1280 MAC give-ups, 0/151 gateway pairs with q < 0.5
  run 1 river-full: D 7478, 8/8 critical done, sim 4.8 s, wall 5 s, 7604 hops, 136 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 5713, 7/7 critical done, sim 10.4 s, wall 8 s, 12769 hops, 377 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1 river-full: D 4423, 6/6 critical done, sim 12.3 s, wall 11 s, 20040 hops, 837 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 6653, 6/6 critical done, sim 12.4 s, wall 7 s, 13131 hops, 459 MAC give-ups, 0/156 gateway pairs with q < 0.5
```
