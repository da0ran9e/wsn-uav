# ns3-ml10-k8-s2

- Bắt đầu: 2026-10-24 08:47:44, chạy 1357 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --lane 10 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s2-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml10/k8-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 596 land cells, 5 clusters [39, 50, 214, 220, 73], 4 lanes, route 22.5 km, with BS 28.8 km
C1: 1.32 km, 3 critical, beyond reach 0 -> 0, mean distance 593 -> 288 m, shift <= 401 m, k*rho 0.52
C2: 0.86 km, 2 critical, beyond reach 0 -> 0, mean distance 462 -> 447 m, shift <= 33 m, k*rho 0.52
C3: 2.07 km, 14 critical, beyond reach 0 -> 0, mean distance 643 -> 631 m, shift <= 537 m, k*rho 0.50
C4: 2.55 km, 16 critical, beyond reach 0 -> 0, mean distance 593 -> 613 m, shift <= 182 m, k*rho 0.50
C5: 1.42 km, 3 critical, beyond reach 0 -> 0, mean distance 122 -> 107 m, shift <= 46 m, k*rho 0.50
tour: 23.6 km, 472 s, order [(4, 0), (5, 0), (3, 1), (2, 1), (1, 1)]
C1: cap 35.0 m/s, 3 loops, 4041 packets over its cells (need 4041), pass 95.5 s
C2: cap 29.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 45.5 s
C3: cap 45.9 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 55.1 s
C4: cap 50.0 m/s, 0 loops, 5433 packets over its cells (need 4041), pass 61.3 s
C5: cap 29.9 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 61.0 s
  run 1 river-full: D 1652, 3/3 critical done, sim 3.1 s, wall 0 s, 1733 hops, 55 MAC give-ups, 0/53 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 2/2 critical done, sim 24.9 s, wall 8 s, 29710 hops, 1165 MAC give-ups, 0/88 gateway pairs with q < 0.5
  run 1 river-full: D 5433, 16/16 critical done, sim 84.2 s, wall 812 s, 559466 hops, 20928 MAC give-ups, 0/509 gateway pairs with q < 0.5
  run 1 river-full: D 4040, 3/3 critical done, sim 16.4 s, wall 7 s, 25875 hops, 711 MAC give-ups, 0/64 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 14/14 critical done, sim 171.3 s, wall 1188 s, 973301 hops, 38923 MAC give-ups, 0/432 gateway pairs with q < 0.5
```
