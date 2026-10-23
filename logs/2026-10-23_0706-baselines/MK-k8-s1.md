# MK-k8-s1

- Bắt đầu: 2026-10-23 07:51:50, chạy 228 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/meander_mission.py --clusters 8 --seed 1 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/MK16/k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --meanderK --windowKB 400 --windowAt crit --critRing domain --axeNear
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 8 clusters [80, 80, 80, 80, 80, 80, 80, 57], BS 173,-3550
curves: C1 2.78 km, CH 222 m off, k*rho 0.93, C2 4.02 km, CH 19 m off, k*rho 0.99, C3 3.45 km, CH 223 m off, k*rho 0.70, C4 3.29 km, CH 46 m off, k*rho 0.97, C5 2.97 km, CH 16 m off, k*rho 0.97, C6 3.17 km, CH 80 m off, k*rho 0.90, C7 3.10 km, CH 24 m off, k*rho 0.93, C8 1.79 km, CH 118 m off, k*rho 0.98
tour: 41.7 km, 834 s, order [(7, 0), (5, 1), (3, 0), (6, 0), (4, 1), (1, 1), (2, 0), (8, 1)]
  run 1 river-full: D 6496, 5/5 critical done, sim 8.8 s, wall 5 s, 9173 hops, 315 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 9018, 6/6 critical done, sim 11.4 s, wall 6 s, 12356 hops, 387 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 7290, 5/5 critical done, sim 4.9 s, wall 3 s, 5911 hops, 198 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 6788, 5/5 critical done, sim 8.9 s, wall 4 s, 5900 hops, 207 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 6725, 6/6 critical done, sim 9.1 s, wall 5 s, 8630 hops, 290 MAC give-ups, 0/177 gateway pairs with q < 0.5
  run 1 river-full: D 7309, 8/8 critical done, sim 28.0 s, wall 15 s, 31200 hops, 862 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 7102, 8/8 critical done, sim 14.2 s, wall 11 s, 18157 hops, 670 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 4600, 4/4 critical done, sim 7.2 s, wall 3 s, 5934 hops, 257 MAC give-ups, 0/116 gateway pairs with q < 0.5
```
