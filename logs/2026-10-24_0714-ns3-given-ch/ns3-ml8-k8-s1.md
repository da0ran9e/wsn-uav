# ns3-ml8-k8-s1

- Bắt đầu: 2026-10-24 08:26:09, chạy 916 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --lane 8 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s1-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml8/k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 617 land cells, 5 clusters [96, 171, 199, 24, 127], 4 lanes, route 23.5 km, with BS 28.8 km
C1: 2.30 km, 7 critical, beyond reach 0 -> 0, mean distance 376 -> 336 m, shift <= 284 m, k*rho 0.50
C2: 2.45 km, 11 critical, beyond reach 0 -> 0, mean distance 463 -> 517 m, shift <= 510 m, k*rho 0.50
C3: 3.40 km, 10 critical, beyond reach 0 -> 0, mean distance 457 -> 476 m, shift <= 291 m, k*rho 0.50
C4: 1.57 km, 2 critical, beyond reach 0 -> 0, mean distance 371 -> 173 m, shift <= 280 m, k*rho 0.50
C5: 2.64 km, 7 critical, beyond reach 0 -> 0, mean distance 337 -> 330 m, shift <= 51 m, k*rho 0.50
tour: 25.0 km, 500 s, order [(3, 0), (4, 0), (5, 0), (2, 1), (1, 1)]
C1: cap 50.0 m/s, 0 loops, 4163 packets over its cells (need 4041), pass 56.2 s
C2: cap 50.0 m/s, 0 loops, 4441 packets over its cells (need 4041), pass 59.2 s
C3: cap 50.0 m/s, 0 loops, 5397 packets over its cells (need 4041), pass 78.1 s
C4: cap 50.0 m/s, 1 loops, 4182 packets over its cells (need 4041), pass 63.3 s
C5: cap 50.0 m/s, 0 loops, 4853 packets over its cells (need 4041), pass 63.0 s
  run 1 river-full: D 4163, 7/7 critical done, sim 51.6 s, wall 72 s, 161451 hops, 5047 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4441, 11/11 critical done, sim 74.0 s, wall 623 s, 620406 hops, 22526 MAC give-ups, 0/346 gateway pairs with q < 0.5
  run 1 river-full: D 3428, 2/2 critical done, sim 2.3 s, wall 0 s, 1012 hops, 13 MAC give-ups, 0/43 gateway pairs with q < 0.5
  run 1 river-full: D 5397, 10/10 critical done, sim 74.6 s, wall 644 s, 542082 hops, 20995 MAC give-ups, 0/392 gateway pairs with q < 0.5
  run 1 river-full: D 4853, 7/7 critical done, sim 53.9 s, wall 126 s, 214676 hops, 6206 MAC give-ups, 0/245 gateway pairs with q < 0.5
```
