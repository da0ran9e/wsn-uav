# MK-k4-s2

- Bắt đầu: 2026-10-23 07:32:32, chạy 124 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k4-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 308 land cells, 6532 nodes, 4 clusters [79, 75, 74, 80], BS -87,-2800
curves: C1 4.67 km, CH 201 m off, k*rho 0.98, C2 2.27 km, CH 48 m off, k*rho 0.61, C3 2.68 km, CH 206 m off, k*rho 0.78, C4 3.31 km, CH 154 m off, k*rho 0.93
tour: 22.7 km, 454 s, order [(3, 1), (2, 1), (1, 0), (4, 1)]
  run 1 river-full: D 5412, 4/4 critical done, sim 10.1 s, wall 4 s, 7533 hops, 250 MAC give-ups, 0/154 gateway pairs with q < 0.5
  run 1 river-full: D 10355, 8/8 critical done, sim 4.1 s, wall 6 s, 8190 hops, 143 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 6303, 3/3 critical done, sim 11.5 s, wall 5 s, 10419 hops, 405 MAC give-ups, 0/135 gateway pairs with q < 0.5
  run 1 river-full: D 7629, 8/8 critical done, sim 12.9 s, wall 10 s, 17220 hops, 691 MAC give-ups, 0/150 gateway pairs with q < 0.5
```
