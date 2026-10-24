# ns3-ml8-k8-s2

- Bắt đầu: 2026-10-24 08:44:37, chạy 1588 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --lane 8 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s2-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml8/k8-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 596 land cells, 5 clusters [92, 224, 64, 109, 107], 4 lanes, route 25.1 km, with BS 30.7 km
C1: 1.83 km, 7 critical, beyond reach 0 -> 0, mean distance 574 -> 555 m, shift <= 69 m, k*rho 0.50
C2: 2.90 km, 14 critical, beyond reach 0 -> 0, mean distance 734 -> 743 m, shift <= 426 m, k*rho 0.50
C3: 1.86 km, 4 critical, beyond reach 0 -> 0, mean distance 401 -> 364 m, shift <= 154 m, k*rho 0.50
C4: 2.34 km, 7 critical, beyond reach 0 -> 0, mean distance 435 -> 449 m, shift <= 449 m, k*rho 0.50
C5: 2.04 km, 6 critical, beyond reach 0 -> 0, mean distance 461 -> 456 m, shift <= 34 m, k*rho 0.50
tour: 25.0 km, 499 s, order [(5, 1), (4, 1), (1, 0), (2, 0), (3, 1)]
C1: cap 32.7 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 65.7 s
C2: cap 50.0 m/s, 0 loops, 6229 packets over its cells (need 4041), pass 68.2 s
C3: cap 43.9 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 53.2 s
C4: cap 50.0 m/s, 0 loops, 4286 packets over its cells (need 4041), pass 57.1 s
C5: cap 50.0 m/s, 0 loops, 4305 packets over its cells (need 4041), pass 51.1 s
  run 1 river-full: D 4040, 7/7 critical done, sim 73.0 s, wall 183 s, 310312 hops, 15178 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 27.3 s, wall 16 s, 42384 hops, 1702 MAC give-ups, 0/124 gateway pairs with q < 0.5
  run 1 river-full: D 4286, 7/7 critical done, sim 33.0 s, wall 134 s, 185781 hops, 7605 MAC give-ups, 0/245 gateway pairs with q < 0.5
  run 1 river-full: D 4305, 6/6 critical done, sim 110.2 s, wall 107 s, 213694 hops, 7304 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 6229, 14/14 critical done, sim 195.4 s, wall 1405 s, 976072 hops, 43450 MAC give-ups, 0/494 gateway pairs with q < 0.5
```
