# MK-k4-s21

- Bắt đầu: 2026-10-23 07:36:39, chạy 134 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 4 --seed 21 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k4-s21 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 305 land cells, 6469 nodes, 4 clusters [65, 80, 80, 80], BS -43,-3100
curves: C1 1.82 km, CH 74 m off, k*rho 0.78, C2 4.00 km, CH 108 m off, k*rho 0.96, C3 2.76 km, CH 208 m off, k*rho 0.96, C4 2.82 km, CH 13 m off, k*rho 0.87
tour: 21.3 km, 425 s, order [(2, 1), (3, 0), (1, 1), (4, 0)]
  run 1 river-full: D 8867, 5/5 critical done, sim 10.8 s, wall 5 s, 7597 hops, 147 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 1 river-full: D 6225, 6/6 critical done, sim 9.2 s, wall 6 s, 8567 hops, 314 MAC give-ups, 0/142 gateway pairs with q < 0.5
  run 1 river-full: D 6550, 10/10 critical done, sim 12.0 s, wall 15 s, 19459 hops, 645 MAC give-ups, 0/168 gateway pairs with q < 0.5
  run 1 river-full: D 4663, 7/7 critical done, sim 19.9 s, wall 27 s, 50402 hops, 1192 MAC give-ups, 0/134 gateway pairs with q < 0.5
```
