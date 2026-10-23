# ns3b-ml-band-s2

- Bắt đầu: 2026-10-23 20:13:47, chạy 531 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --minAxe 2.4 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/ml/band-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.86 km, 12 critical, beyond the River half width 6 -> 6, mean distance 403 -> 411 m, shift <= 84 m, k*rho 1.05
C2: 2.86 km, 9 critical, beyond the River half width 6 -> 6, mean distance 353 -> 330 m, shift <= 185 m, k*rho 1.05
C3: 3.04 km, 5 critical, beyond the River half width 0 -> 0, mean distance 81 -> 166 m, shift <= 189 m, k*rho 1.05
C4: 3.03 km, 6 critical, beyond the River half width 0 -> 0, mean distance 95 -> 100 m, shift <= 28 m, k*rho 1.05
C5: 4.46 km, 10 critical, beyond the River half width 3 -> 3, mean distance 210 -> 221 m, shift <= 110 m, k*rho 1.04
C6: 5.79 km, 7 critical, beyond the River half width 3 -> 3, mean distance 272 -> 250 m, shift <= 110 m, k*rho 1.04
tour: 30.9 km, 618 s, order [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)]
  run 1 river-full: D 5586, 9/9 critical done, sim 19.9 s, wall 40 s, 38577 hops, 1107 MAC give-ups, 0/350 gateway pairs with q < 0.5
  run 1 river-full: D 5915, 12/12 critical done, sim 27.4 s, wall 87 s, 73125 hops, 2490 MAC give-ups, 0/369 gateway pairs with q < 0.5
  run 1 river-full: D 5967, 6/6 critical done, sim 21.9 s, wall 16 s, 32122 hops, 1387 MAC give-ups, 0/141 gateway pairs with q < 0.5
  run 1 river-full: D 4811, 5/5 critical done, sim 52.7 s, wall 63 s, 130174 hops, 3947 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 6237, 7/7 critical done, sim 29.2 s, wall 44 s, 74867 hops, 2649 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 6351, 10/10 critical done, sim 52.1 s, wall 184 s, 198399 hops, 7044 MAC give-ups, 0/279 gateway pairs with q < 0.5
```
