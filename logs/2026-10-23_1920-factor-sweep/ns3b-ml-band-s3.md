# ns3b-ml-band-s3

- Bắt đầu: 2026-10-23 20:22:38, chạy 902 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --minAxe 2.4 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/ml/band-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.65 km, 8 critical, beyond the River half width 5 -> 5, mean distance 343 -> 306 m, shift <= 166 m, k*rho 1.02
C2: 3.13 km, 7 critical, beyond the River half width 2 -> 3, mean distance 307 -> 301 m, shift <= 164 m, k*rho 1.02
C3: 5.78 km, 3 critical, beyond the River half width 0 -> 0, mean distance 83 -> 112 m, shift <= 97 m, k*rho 1.02
C4: 3.73 km, 17 critical, beyond the River half width 13 -> 12, mean distance 571 -> 545 m, shift <= 427 m, k*rho 0.93
C5: 2.69 km, 11 critical, beyond the River half width 7 -> 5, mean distance 449 -> 345 m, shift <= 256 m, k*rho 0.93
C6: 2.72 km, 5 critical, beyond the River half width 0 -> 0, mean distance 114 -> 106 m, shift <= 129 m, k*rho 0.93
C7: 2.42 km, 1 critical, beyond the River half width 0 -> 0, mean distance 30 -> 32 m, shift <= 62 m, k*rho 0.93
tour: 31.4 km, 628 s, order [(7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 5828, 8/8 critical done, sim 22.7 s, wall 35 s, 39688 hops, 1462 MAC give-ups, 0/331 gateway pairs with q < 0.5
  run 1 river-full: D 3654, 3/3 critical done, sim 3.8 s, wall 1 s, 2474 hops, 111 MAC give-ups, 0/87 gateway pairs with q < 0.5
  run 1 river-full: D 5048, 7/7 critical done, sim 26.8 s, wall 64 s, 68041 hops, 2924 MAC give-ups, 0/296 gateway pairs with q < 0.5
  run 1 river-full: D 4931, 11/11 critical done, sim 24.5 s, wall 78 s, 81753 hops, 2497 MAC give-ups, 0/328 gateway pairs with q < 0.5
  run 1 river-full: D 4706, 5/5 critical done, sim 41.2 s, wall 19 s, 78864 hops, 3120 MAC give-ups, 0/57 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 1/1 critical done, sim 3.5 s, wall 0 s, 1389 hops, 45 MAC give-ups, 0/62 gateway pairs with q < 0.5
  run 1 river-full: D 5968, 17/17 critical done, sim 68.4 s, wall 610 s, 396392 hops, 16886 MAC give-ups, 0/456 gateway pairs with q < 0.5
```
