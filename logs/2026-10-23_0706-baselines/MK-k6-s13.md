# MK-k6-s13

- Bắt đầu: 2026-10-23 07:42:11, chạy 206 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 6 --seed 13 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k6-s13 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 450 land cells, 9544 nodes, 6 clusters [70, 80, 60, 80, 80, 80], BS 520,-3100
curves: C1 2.96 km, CH 109 m off, k*rho 0.95, C2 2.89 km, CH 43 m off, k*rho 0.93, C3 2.03 km, CH 112 m off, k*rho 1.00, C4 3.22 km, CH 107 m off, k*rho 0.99, C5 4.11 km, CH 209 m off, k*rho 1.00, C6 3.53 km, CH 65 m off, k*rho 0.96
tour: 31.3 km, 626 s, order [(4, 0), (3, 0), (5, 1), (6, 0), (1, 1), (2, 1)]
  run 1 river-full: D 6804, 6/6 critical done, sim 8.0 s, wall 6 s, 9028 hops, 246 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 6947, 9/9 critical done, sim 18.4 s, wall 10 s, 17373 hops, 496 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 5005, 5/5 critical done, sim 9.4 s, wall 4 s, 9309 hops, 275 MAC give-ups, 0/121 gateway pairs with q < 0.5
  run 1 river-full: D 9201, 7/7 critical done, sim 5.5 s, wall 4 s, 7442 hops, 205 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 1 river-full: D 6335, 5/5 critical done, sim 28.0 s, wall 9 s, 20124 hops, 674 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 1 river-full: D 8017, 8/8 critical done, sim 14.1 s, wall 11 s, 19454 hops, 544 MAC give-ups, 0/152 gateway pairs with q < 0.5
```
