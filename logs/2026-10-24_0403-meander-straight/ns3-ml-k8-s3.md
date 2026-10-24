# ns3-ml-k8-s3

- Bắt đầu: 2026-10-24 04:32:58, chạy 569 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --lane 8 --minAxe 2.4 --reach 5 --straight 0.5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS3/ml/k8-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.21 km, 9 critical, beyond reach 1 -> 1, mean distance 474 -> 443 m, shift <= 173 m, k*rho 0.90
C2: 2.41 km, 8 critical, beyond reach 1 -> 1, mean distance 367 -> 339 m, shift <= 104 m, k*rho 0.90
C3: 2.95 km, 6 critical, beyond reach 0 -> 0, mean distance 240 -> 231 m, shift <= 114 m, k*rho 0.87
C4: 3.10 km, 9 critical, beyond reach 0 -> 0, mean distance 218 -> 224 m, shift <= 118 m, k*rho 0.87
C5: 4.34 km, 10 critical, beyond reach 0 -> 0, mean distance 247 -> 243 m, shift <= 37 m, k*rho 0.50
C6: 2.79 km, 7 critical, beyond reach 0 -> 0, mean distance 222 -> 214 m, shift <= 33 m, k*rho 0.66
tour: 33.3 km, 667 s, order [(6, 1), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 4318, 8/8 critical done, sim 22.7 s, wall 67 s, 85556 hops, 2352 MAC give-ups, 0/251 gateway pairs with q < 0.5
  run 1 river-full: D 4178, 9/9 critical done, sim 32.4 s, wall 130 s, 158254 hops, 5529 MAC give-ups, 0/256 gateway pairs with q < 0.5
  run 1 river-full: D 4339, 6/6 critical done, sim 33.1 s, wall 87 s, 114808 hops, 4287 MAC give-ups, 0/251 gateway pairs with q < 0.5
  run 1 river-full: D 4819, 9/9 critical done, sim 27.0 s, wall 37 s, 72147 hops, 2769 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 7574, 10/10 critical done, sim 69.2 s, wall 137 s, 139709 hops, 5850 MAC give-ups, 0/366 gateway pairs with q < 0.5
  run 1 river-full: D 4589, 7/7 critical done, sim 69.0 s, wall 139 s, 254617 hops, 9485 MAC give-ups, 0/151 gateway pairs with q < 0.5
```
