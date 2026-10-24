# ns3-ml-k8-s1

- Bắt đầu: 2026-10-24 04:08:33, chạy 873 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --lane 8 --minAxe 2.4 --reach 5 --straight 0.5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS3/ml/k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 4.02 km, 10 critical, beyond reach 3 -> 1, mean distance 565 -> 487 m, shift <= 324 m, k*rho 0.90
C2: 2.49 km, 6 critical, beyond reach 0 -> 0, mean distance 350 -> 350 m, shift <= 6 m, k*rho 0.60
C3: 3.10 km, 10 critical, beyond reach 0 -> 0, mean distance 372 -> 369 m, shift <= 25 m, k*rho 0.60
C4: 5.44 km, 16 critical, beyond reach 1 -> 0, mean distance 392 -> 373 m, shift <= 162 m, k*rho 0.55
C5: 4.04 km, 2 critical, beyond reach 0 -> 0, mean distance 89 -> 65 m, shift <= 80 m, k*rho 0.50
tour: 31.7 km, 635 s, order [(5, 1), (1, 1), (3, 1), (2, 1), (4, 1)]
  run 1 river-full: D 4324, 6/6 critical done, sim 27.4 s, wall 47 s, 63224 hops, 2562 MAC give-ups, 0/229 gateway pairs with q < 0.5
  run 1 river-full: D 7042, 10/10 critical done, sim 56.3 s, wall 316 s, 249538 hops, 9760 MAC give-ups, 0/345 gateway pairs with q < 0.5
  run 1 river-full: D 4204, 10/10 critical done, sim 110.0 s, wall 454 s, 437529 hops, 17760 MAC give-ups, 0/307 gateway pairs with q < 0.5
  run 1 river-full: D 3806, 2/2 critical done, sim 5.0 s, wall 1 s, 2778 hops, 40 MAC give-ups, 0/52 gateway pairs with q < 0.5
  run 1 river-full: D 9165, 16/16 critical done, sim 42.1 s, wall 221 s, 159406 hops, 5554 MAC give-ups, 0/353 gateway pairs with q < 0.5
```
