# ns3-ml10-k8-s1

- Bắt đầu: 2026-10-24 07:20:35, chạy 762 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --lane 10 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s1-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T155l10/s1/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 1.92 km, 3 critical, beyond reach 0 -> 0, mean distance 329 -> 260 m, shift <= 154 m, k*rho 0.50
C2: 1.98 km, 8 critical, beyond reach 0 -> 0, mean distance 444 -> 444 m, shift <= 162 m, k*rho 0.50
C3: 2.56 km, 11 critical, beyond reach 0 -> 0, mean distance 458 -> 458 m, shift <= 171 m, k*rho 0.50
C4: 2.26 km, 6 critical, beyond reach 0 -> 0, mean distance 376 -> 376 m, shift <= 64 m, k*rho 0.50
C5: 1.79 km, 11 critical, beyond reach 0 -> 0, mean distance 479 -> 473 m, shift <= 44 m, k*rho 0.50
tour: 24.0 km, 479 s, order [(3, 0), (2, 1), (1, 1), (4, 1), (5, 0)]
  run 1 river-full: D 3459, 3/3 critical done, sim 7.9 s, wall 3 s, 6722 hops, 219 MAC give-ups, 0/123 gateway pairs with q < 0.5
  run 1 river-full: D 3546, 8/8 critical done, sim 67.0 s, wall 164 s, 316097 hops, 9683 MAC give-ups, 0/209 gateway pairs with q < 0.5
  run 1 river-full: D 4578, 6/6 critical done, sim 33.2 s, wall 45 s, 83002 hops, 2891 MAC give-ups, 0/201 gateway pairs with q < 0.5
  run 1 river-full: D 3820, 11/11 critical done, sim 44.8 s, wall 247 s, 259008 hops, 11107 MAC give-ups, 0/343 gateway pairs with q < 0.5
  run 1 river-full: D 4249, 11/11 critical done, sim 104.5 s, wall 403 s, 425741 hops, 18216 MAC give-ups, 0/336 gateway pairs with q < 0.5
```
