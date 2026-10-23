# ns3-ml-band-s3

- Bắt đầu: 2026-10-23 19:53:11, chạy 313 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS/ml/band-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 1.50 km, 3 critical, beyond the River half width 2 -> 1, mean distance 270 -> 267 m, shift <= 168 m, k*rho 1.02
C2: 1.18 km, 6 critical, beyond the River half width 3 -> 4, mean distance 332 -> 276 m, shift <= 182 m, k*rho 1.02
C3: 1.41 km, 3 critical, beyond the River half width 1 -> 1, mean distance 345 -> 328 m, shift <= 183 m, k*rho 1.02
C4: 1.70 km, 5 critical, beyond the River half width 1 -> 1, mean distance 238 -> 225 m, shift <= 74 m, k*rho 1.02
C5: 5.86 km, 3 critical, beyond the River half width 0 -> 0, mean distance 83 -> 112 m, shift <= 97 m, k*rho 1.02
C6: 2.21 km, 10 critical, beyond the River half width 6 -> 5, mean distance 417 -> 372 m, shift <= 353 m, k*rho 0.88
C7: 1.42 km, 7 critical, beyond the River half width 5 -> 5, mean distance 667 -> 613 m, shift <= 320 m, k*rho 0.88
C8: 1.18 km, 7 critical, beyond the River half width 4 -> 4, mean distance 470 -> 402 m, shift <= 205 m, k*rho 0.88
C9: 1.60 km, 5 critical, beyond the River half width 3 -> 3, mean distance 290 -> 279 m, shift <= 191 m, k*rho 0.88
C10: 5.50 km, 6 critical, beyond the River half width 1 -> 1, mean distance 183 -> 171 m, shift <= 114 m, k*rho 0.88
tour: 35.0 km, 700 s, order [(10, 1), (9, 1), (8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 2498, 6/6 critical done, sim 3.9 s, wall 2 s, 3863 hops, 161 MAC give-ups, 0/146 gateway pairs with q < 0.5
  run 1 river-full: D 3390, 3/3 critical done, sim 7.2 s, wall 3 s, 4176 hops, 109 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 1 river-full: D 2874, 3/3 critical done, sim 7.4 s, wall 2 s, 3475 hops, 93 MAC give-ups, 0/119 gateway pairs with q < 0.5
  run 1 river-full: D 3654, 3/3 critical done, sim 4.1 s, wall 1 s, 2572 hops, 70 MAC give-ups, 0/89 gateway pairs with q < 0.5
  run 1 river-full: D 2989, 5/5 critical done, sim 23.1 s, wall 14 s, 35731 hops, 972 MAC give-ups, 0/137 gateway pairs with q < 0.5
  run 1 river-full: D 2267, 7/7 critical done, sim 14.8 s, wall 10 s, 16267 hops, 672 MAC give-ups, 0/164 gateway pairs with q < 0.5
  run 1 river-full: D 2491, 7/7 critical done, sim 12.6 s, wall 6 s, 11122 hops, 351 MAC give-ups, 0/179 gateway pairs with q < 0.5
  run 1 river-full: D 2746, 5/5 critical done, sim 12.8 s, wall 3 s, 6047 hops, 233 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 5214, 6/6 critical done, sim 64.9 s, wall 32 s, 121836 hops, 3124 MAC give-ups, 0/69 gateway pairs with q < 0.5
  run 1 river-full: D 3942, 10/10 critical done, sim 39.1 s, wall 121 s, 163421 hops, 4644 MAC give-ups, 0/227 gateway pairs with q < 0.5
```
