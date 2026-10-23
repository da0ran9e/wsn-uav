# MK-k6-s11

- Bắt đầu: 2026-10-23 07:38:54, chạy 197 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 6 --seed 11 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k6-s11 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 453 land cells, 9608 nodes, 6 clusters [80, 80, 80, 77, 67, 69], BS -433,-3250
curves: C1 2.50 km, CH 44 m off, k*rho 0.88, C2 1.65 km, CH 73 m off, k*rho 0.99, C3 3.32 km, CH 20 m off, k*rho 0.85, C4 2.86 km, CH 22 m off, k*rho 0.97, C5 2.39 km, CH 164 m off, k*rho 0.95, C6 5.10 km, CH 41 m off, k*rho 1.00
tour: 30.9 km, 618 s, order [(2, 0), (3, 1), (6, 0), (5, 1), (4, 1), (1, 0)]
  run 1 river-full: D 5442, 6/6 critical done, sim 17.2 s, wall 14 s, 28256 hops, 894 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 7598, 8/8 critical done, sim 27.1 s, wall 26 s, 35859 hops, 1391 MAC give-ups, 0/177 gateway pairs with q < 0.5
  run 1 river-full: D 6107, 4/4 critical done, sim 6.9 s, wall 5 s, 5403 hops, 169 MAC give-ups, 0/166 gateway pairs with q < 0.5
  run 1 river-full: D 4323, 8/8 critical done, sim 34.3 s, wall 47 s, 67344 hops, 2065 MAC give-ups, 0/186 gateway pairs with q < 0.5
  run 1 river-full: D 10619, 5/5 critical done, sim 3.8 s, wall 4 s, 4577 hops, 154 MAC give-ups, 0/104 gateway pairs with q < 0.5
  run 1 river-full: D 5318, 4/4 critical done, sim 10.1 s, wall 6 s, 7144 hops, 252 MAC give-ups, 0/137 gateway pairs with q < 0.5
```
