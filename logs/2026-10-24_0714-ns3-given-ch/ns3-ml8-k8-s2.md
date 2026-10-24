# ns3-ml8-k8-s2

- Bắt đầu: 2026-10-24 07:33:18, chạy 1531 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --lane 8 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s2-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s2-par-trim5-chord/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 1.83 km, 7 critical, beyond reach 0 -> 0, mean distance 574 -> 555 m, shift <= 69 m, k*rho 0.50
C2: 2.90 km, 14 critical, beyond reach 0 -> 0, mean distance 734 -> 743 m, shift <= 426 m, k*rho 0.50
C3: 1.86 km, 4 critical, beyond reach 0 -> 0, mean distance 401 -> 364 m, shift <= 154 m, k*rho 0.50
C4: 2.34 km, 7 critical, beyond reach 0 -> 0, mean distance 435 -> 449 m, shift <= 449 m, k*rho 0.50
C5: 2.04 km, 6 critical, beyond reach 0 -> 0, mean distance 461 -> 456 m, shift <= 34 m, k*rho 0.50
tour: 25.0 km, 499 s, order [(5, 1), (4, 1), (1, 0), (2, 0), (3, 1)]
  run 1 river-full: D 2645, 7/7 critical done, sim 49.4 s, wall 108 s, 203735 hops, 9919 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 3551, 4/4 critical done, sim 23.6 s, wall 13 s, 35986 hops, 1344 MAC give-ups, 0/124 gateway pairs with q < 0.5
  run 1 river-full: D 4286, 7/7 critical done, sim 33.0 s, wall 126 s, 185574 hops, 7491 MAC give-ups, 0/245 gateway pairs with q < 0.5
  run 1 river-full: D 4305, 6/6 critical done, sim 99.0 s, wall 105 s, 213643 hops, 7989 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 6229, 14/14 critical done, sim 196.6 s, wall 1395 s, 976040 hops, 43432 MAC give-ups, 0/494 gateway pairs with q < 0.5
```
