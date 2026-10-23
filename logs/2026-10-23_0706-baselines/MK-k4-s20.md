# MK-k4-s20

- Bắt đầu: 2026-10-23 07:34:37, chạy 123 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 4 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k4-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 312 land cells, 6617 nodes, 4 clusters [72, 80, 80, 80], BS -217,-3250
curves: C1 1.96 km, CH 288 m off, k*rho 0.88, C2 3.35 km, CH 4 m off, k*rho 0.94, C3 5.65 km, CH 21 m off, k*rho 0.96, C4 2.17 km, CH 249 m off, k*rho 0.92
tour: 20.8 km, 415 s, order [(2, 1), (1, 0), (4, 1), (3, 0)]
  run 1 river-full: D 4947, 4/4 critical done, sim 8.0 s, wall 4 s, 6826 hops, 159 MAC give-ups, 0/157 gateway pairs with q < 0.5
  run 1 river-full: D 7347, 6/6 critical done, sim 10.5 s, wall 7 s, 11810 hops, 479 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 11882, 7/7 critical done, sim 8.5 s, wall 6 s, 10547 hops, 310 MAC give-ups, 0/106 gateway pairs with q < 0.5
  run 1 river-full: D 5362, 6/6 critical done, sim 15.0 s, wall 13 s, 22450 hops, 581 MAC give-ups, 0/178 gateway pairs with q < 0.5
```
