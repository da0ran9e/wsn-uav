# ns3-ml10-k8-s2

- Bắt đầu: 2026-10-24 07:37:18, chạy 1232 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --lane 10 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s2-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T155l10/s2/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 1.32 km, 3 critical, beyond reach 0 -> 0, mean distance 593 -> 288 m, shift <= 401 m, k*rho 0.52
C2: 0.86 km, 2 critical, beyond reach 0 -> 0, mean distance 462 -> 447 m, shift <= 33 m, k*rho 0.52
C3: 2.07 km, 14 critical, beyond reach 0 -> 0, mean distance 643 -> 631 m, shift <= 537 m, k*rho 0.50
C4: 2.55 km, 16 critical, beyond reach 0 -> 0, mean distance 593 -> 613 m, shift <= 182 m, k*rho 0.50
C5: 1.42 km, 3 critical, beyond reach 0 -> 0, mean distance 122 -> 107 m, shift <= 46 m, k*rho 0.50
tour: 23.6 km, 472 s, order [(4, 0), (5, 0), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 844, 3/3 critical done, sim 2.3 s, wall 0 s, 1115 hops, 28 MAC give-ups, 0/53 gateway pairs with q < 0.5
  run 1 river-full: D 2377, 2/2 critical done, sim 15.5 s, wall 5 s, 17858 hops, 749 MAC give-ups, 0/88 gateway pairs with q < 0.5
  run 1 river-full: D 5433, 16/16 critical done, sim 86.0 s, wall 815 s, 559538 hops, 21009 MAC give-ups, 0/509 gateway pairs with q < 0.5
  run 1 river-full: D 2418, 3/3 critical done, sim 9.9 s, wall 4 s, 15312 hops, 427 MAC give-ups, 0/61 gateway pairs with q < 0.5
  run 1 river-full: D 3713, 14/14 critical done, sim 158.1 s, wall 1107 s, 895491 hops, 35776 MAC give-ups, 0/432 gateway pairs with q < 0.5
```
