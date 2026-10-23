# ns3b-ml-band-s1

- Bắt đầu: 2026-10-23 20:04:31, chạy 458 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --minAxe 2.4 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/ml/band-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 3.16 km, 4 critical, beyond the River half width 1 -> 1, mean distance 124 -> 133 m, shift <= 132 m, k*rho 1.15
C2: 3.02 km, 9 critical, beyond the River half width 5 -> 5, mean distance 326 -> 326 m, shift <= 186 m, k*rho 1.15
C3: 3.30 km, 8 critical, beyond the River half width 3 -> 2, mean distance 242 -> 242 m, shift <= 190 m, k*rho 1.15
C4: 2.58 km, 3 critical, beyond the River half width 0 -> 0, mean distance 96 -> 149 m, shift <= 101 m, k*rho 1.15
C5: 2.62 km, 9 critical, beyond the River half width 5 -> 4, mean distance 280 -> 271 m, shift <= 118 m, k*rho 0.99
C6: 3.01 km, 9 critical, beyond the River half width 4 -> 4, mean distance 324 -> 284 m, shift <= 132 m, k*rho 0.99
C7: 2.66 km, 4 critical, beyond the River half width 0 -> 0, mean distance 94 -> 86 m, shift <= 103 m, k*rho 0.99
C8: 3.23 km, 4 critical, beyond the River half width 0 -> 0, mean distance 107 -> 89 m, shift <= 72 m, k*rho 0.99
tour: 33.0 km, 661 s, order [(8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 4816, 4/4 critical done, sim 12.8 s, wall 6 s, 9754 hops, 323 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 4744, 8/8 critical done, sim 60.1 s, wall 118 s, 184457 hops, 6423 MAC give-ups, 0/194 gateway pairs with q < 0.5
  run 1 river-full: D 4353, 3/3 critical done, sim 10.1 s, wall 2 s, 5296 hops, 161 MAC give-ups, 0/56 gateway pairs with q < 0.5
  run 1 river-full: D 5387, 9/9 critical done, sim 68.7 s, wall 174 s, 199245 hops, 8387 MAC give-ups, 0/263 gateway pairs with q < 0.5
  run 1 river-full: D 5520, 9/9 critical done, sim 22.9 s, wall 57 s, 59782 hops, 2260 MAC give-ups, 0/333 gateway pairs with q < 0.5
  run 1 river-full: D 5347, 4/4 critical done, sim 10.5 s, wall 5 s, 10379 hops, 444 MAC give-ups, 0/135 gateway pairs with q < 0.5
  run 1 river-full: D 5341, 4/4 critical done, sim 20.6 s, wall 19 s, 42130 hops, 1610 MAC give-ups, 0/159 gateway pairs with q < 0.5
  run 1 river-full: D 5226, 9/9 critical done, sim 15.7 s, wall 41 s, 41946 hops, 1387 MAC give-ups, 0/303 gateway pairs with q < 0.5
```
