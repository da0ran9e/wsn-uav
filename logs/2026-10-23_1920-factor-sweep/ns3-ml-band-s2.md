# ns3-ml-band-s2

- Bắt đầu: 2026-10-23 19:49:11, chạy 205 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS/ml/band-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 1.73 km, 6 critical, beyond the River half width 4 -> 4, mean distance 405 -> 398 m, shift <= 130 m, k*rho 1.01
C2: 1.81 km, 8 critical, beyond the River half width 4 -> 4, mean distance 410 -> 420 m, shift <= 118 m, k*rho 1.01
C3: 1.58 km, 6 critical, beyond the River half width 3 -> 3, mean distance 325 -> 316 m, shift <= 85 m, k*rho 1.01
C4: 3.22 km, 6 critical, beyond the River half width 1 -> 0, mean distance 123 -> 127 m, shift <= 114 m, k*rho 1.01
C5: 3.64 km, 7 critical, beyond the River half width 0 -> 0, mean distance 134 -> 83 m, shift <= 140 m, k*rho 1.01
C6: 1.83 km, 5 critical, beyond the River half width 2 -> 1, mean distance 237 -> 230 m, shift <= 103 m, k*rho 22.11
C7: 1.68 km, 4 critical, beyond the River half width 1 -> 1, mean distance 174 -> 165 m, shift <= 32 m, k*rho 22.11
C8: 1.19 km, 3 critical, beyond the River half width 0 -> 0, mean distance 125 -> 115 m, shift <= 156 m, k*rho 22.11
C9: 1.47 km, 4 critical, beyond the River half width 2 -> 2, mean distance 303 -> 236 m, shift <= 226 m, k*rho 22.11
C10: 4.34 km, 4 critical, beyond the River half width 1 -> 2, mean distance 194 -> 244 m, shift <= 273 m, k*rho 22.11
tour: 35.3 km, 705 s, order [(10, 1), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 3605, 6/6 critical done, sim 15.8 s, wall 11 s, 19286 hops, 541 MAC give-ups, 0/197 gateway pairs with q < 0.5
  run 1 river-full: D 3432, 8/8 critical done, sim 19.2 s, wall 17 s, 24994 hops, 735 MAC give-ups, 0/219 gateway pairs with q < 0.5
  run 1 river-full: D 3298, 6/6 critical done, sim 10.6 s, wall 7 s, 12001 hops, 167 MAC give-ups, 0/179 gateway pairs with q < 0.5
  run 1 river-full: D 5632, 6/6 critical done, sim 12.0 s, wall 10 s, 18392 hops, 607 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 2879, 5/5 critical done, sim 22.2 s, wall 10 s, 30468 hops, 1089 MAC give-ups, 0/86 gateway pairs with q < 0.5
  run 1 river-full: D 1894, 4/4 critical done, sim 5.2 s, wall 1 s, 4694 hops, 155 MAC give-ups, 0/76 gateway pairs with q < 0.5
  run 1 river-full: D 2345, 3/3 critical done, sim 1.0 s, wall 0 s, 750 hops, 29 MAC give-ups, 0/86 gateway pairs with q < 0.5
  run 1 river-full: D 2276, 4/4 critical done, sim 3.0 s, wall 1 s, 2317 hops, 86 MAC give-ups, 0/81 gateway pairs with q < 0.5
  run 1 river-full: D 2703, 4/4 critical done, sim 13.3 s, wall 2 s, 7390 hops, 342 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 7181, 7/7 critical done, sim 20.2 s, wall 27 s, 44234 hops, 1255 MAC give-ups, 0/188 gateway pairs with q < 0.5
```
