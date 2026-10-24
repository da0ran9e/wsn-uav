# ns3-ml8-k8-s1

- Bắt đầu: 2026-10-24 07:16:09, chạy 914 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --lane 8 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s1-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s1-par-trim5-chord/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.30 km, 7 critical, beyond reach 0 -> 0, mean distance 376 -> 336 m, shift <= 284 m, k*rho 0.50
C2: 2.45 km, 11 critical, beyond reach 0 -> 0, mean distance 463 -> 517 m, shift <= 510 m, k*rho 0.50
C3: 3.40 km, 10 critical, beyond reach 0 -> 0, mean distance 457 -> 476 m, shift <= 291 m, k*rho 0.50
C4: 1.57 km, 2 critical, beyond reach 0 -> 0, mean distance 371 -> 173 m, shift <= 280 m, k*rho 0.50
C5: 2.64 km, 7 critical, beyond reach 0 -> 0, mean distance 337 -> 330 m, shift <= 51 m, k*rho 0.50
tour: 25.0 km, 500 s, order [(3, 0), (4, 0), (5, 0), (2, 1), (1, 1)]
  run 1 river-full: D 4163, 7/7 critical done, sim 51.8 s, wall 66 s, 161416 hops, 5075 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4441, 11/11 critical done, sim 73.7 s, wall 614 s, 620403 hops, 22588 MAC give-ups, 0/346 gateway pairs with q < 0.5
  run 1 river-full: D 2011, 2/2 critical done, sim 1.5 s, wall 0 s, 634 hops, 36 MAC give-ups, 0/43 gateway pairs with q < 0.5
  run 1 river-full: D 5397, 10/10 critical done, sim 74.6 s, wall 637 s, 542061 hops, 20712 MAC give-ups, 0/392 gateway pairs with q < 0.5
  run 1 river-full: D 4853, 7/7 critical done, sim 54.3 s, wall 127 s, 214673 hops, 6206 MAC give-ups, 0/245 gateway pairs with q < 0.5
```
