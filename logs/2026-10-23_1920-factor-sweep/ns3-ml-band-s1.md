# ns3-ml-band-s1

- Bắt đầu: 2026-10-23 19:45:16, chạy 236 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS/ml/band-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.36 km, 2 critical, beyond the River half width 0 -> 0, mean distance 55 -> 80 m, shift <= 123 m, k*rho 1.08
C2: 1.61 km, 4 critical, beyond the River half width 2 -> 1, mean distance 257 -> 233 m, shift <= 123 m, k*rho 1.08
C3: 1.34 km, 4 critical, beyond the River half width 1 -> 1, mean distance 151 -> 153 m, shift <= 54 m, k*rho 1.08
C4: 1.21 km, 6 critical, beyond the River half width 3 -> 3, mean distance 267 -> 268 m, shift <= 64 m, k*rho 1.08
C5: 1.60 km, 5 critical, beyond the River half width 2 -> 2, mean distance 281 -> 262 m, shift <= 151 m, k*rho 1.08
C6: 3.94 km, 5 critical, beyond the River half width 0 -> 0, mean distance 71 -> 159 m, shift <= 151 m, k*rho 1.08
C7: 1.85 km, 7 critical, beyond the River half width 4 -> 3, mean distance 286 -> 260 m, shift <= 149 m, k*rho 1.01
C8: 1.32 km, 5 critical, beyond the River half width 2 -> 2, mean distance 291 -> 276 m, shift <= 146 m, k*rho 1.01
C9: 1.72 km, 6 critical, beyond the River half width 2 -> 2, mean distance 256 -> 254 m, shift <= 142 m, k*rho 1.01
C10: 3.58 km, 4 critical, beyond the River half width 0 -> 0, mean distance 94 -> 84 m, shift <= 103 m, k*rho 1.01
C11: 3.10 km, 4 critical, beyond the River half width 0 -> 0, mean distance 107 -> 93 m, shift <= 58 m, k*rho 1.01
tour: 36.1 km, 722 s, order [(11, 1), (10, 1), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 2501, 4/4 critical done, sim 9.8 s, wall 2 s, 5651 hops, 304 MAC give-ups, 0/101 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 2/2 critical done, sim 8.5 s, wall 3 s, 7408 hops, 222 MAC give-ups, 0/107 gateway pairs with q < 0.5
  run 1 river-full: D 2458, 4/4 critical done, sim 3.7 s, wall 1 s, 2527 hops, 83 MAC give-ups, 0/89 gateway pairs with q < 0.5
  run 1 river-full: D 1906, 6/6 critical done, sim 2.6 s, wall 1 s, 3009 hops, 76 MAC give-ups, 0/109 gateway pairs with q < 0.5
  run 1 river-full: D 1479, 5/5 critical done, sim 10.5 s, wall 5 s, 10305 hops, 406 MAC give-ups, 0/103 gateway pairs with q < 0.5
  run 1 river-full: D 3921, 7/7 critical done, sim 25.3 s, wall 19 s, 37801 hops, 1048 MAC give-ups, 0/191 gateway pairs with q < 0.5
  run 1 river-full: D 2715, 5/5 critical done, sim 6.3 s, wall 3 s, 4419 hops, 59 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 3026, 6/6 critical done, sim 9.4 s, wall 5 s, 6798 hops, 291 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5360, 4/4 critical done, sim 11.5 s, wall 5 s, 10029 hops, 403 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 6418, 5/5 critical done, sim 49.2 s, wall 40 s, 122831 hops, 3366 MAC give-ups, 0/99 gateway pairs with q < 0.5
  run 1 river-full: D 5342, 4/4 critical done, sim 26.8 s, wall 19 s, 40933 hops, 1803 MAC give-ups, 0/159 gateway pairs with q < 0.5
```
