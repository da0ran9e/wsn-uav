# MK-k6-s20

- Bắt đầu: 2026-10-23 07:45:37, chạy 168 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 6 --seed 20 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k6-s20 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 462 land cells, 9798 nodes, 6 clusters [80, 80, 80, 80, 80, 62], BS -43,-3700
curves: C1 2.71 km, CH 72 m off, k*rho 0.97, C2 5.40 km, CH 82 m off, k*rho 0.93, C3 2.38 km, CH 65 m off, k*rho 0.98, C4 2.65 km, CH 327 m off, k*rho 0.99, C5 3.08 km, CH 5 m off, k*rho 0.93, C6 2.23 km, CH 122 m off, k*rho 0.68
tour: 30.8 km, 616 s, order [(2, 0), (4, 1), (1, 0), (3, 1), (5, 0), (6, 1)]
  run 1 river-full: D 11288, 7/7 critical done, sim 11.6 s, wall 8 s, 11049 hops, 288 MAC give-ups, 0/146 gateway pairs with q < 0.5
  run 1 river-full: D 6363, 7/7 critical done, sim 13.0 s, wall 12 s, 14702 hops, 456 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 6280, 6/6 critical done, sim 7.4 s, wall 5 s, 8888 hops, 277 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 1 river-full: D 5773, 6/6 critical done, sim 9.9 s, wall 10 s, 12905 hops, 438 MAC give-ups, 0/194 gateway pairs with q < 0.5
  run 1 river-full: D 7083, 6/6 critical done, sim 7.9 s, wall 7 s, 10751 hops, 279 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 5338, 5/5 critical done, sim 14.6 s, wall 8 s, 16543 hops, 491 MAC give-ups, 0/130 gateway pairs with q < 0.5
```
