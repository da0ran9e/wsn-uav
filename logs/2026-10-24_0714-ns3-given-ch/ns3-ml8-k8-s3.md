# ns3-ml8-k8-s3

- Bắt đầu: 2026-10-24 09:11:05, chạy 1020 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --lane 8 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s3-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml8/k8-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 656 land cells, 5 clusters [24, 127, 199, 212, 94], 5 lanes, route 27.9 km, with BS 36.3 km
C1: 1.38 km, 2 critical, beyond reach 0 -> 0, mean distance 308 -> 149 m, shift <= 278 m, k*rho 0.50
C2: 2.22 km, 7 critical, beyond reach 0 -> 0, mean distance 349 -> 388 m, shift <= 689 m, k*rho 0.50
C3: 2.48 km, 13 critical, beyond reach 0 -> 0, mean distance 646 -> 620 m, shift <= 238 m, k*rho 0.50
C4: 2.96 km, 13 critical, beyond reach 0 -> 0, mean distance 546 -> 518 m, shift <= 321 m, k*rho 0.50
C5: 2.94 km, 8 critical, beyond reach 0 -> 0, mean distance 428 -> 287 m, shift <= 660 m, k*rho 0.50
tour: 26.9 km, 539 s, order [(2, 1), (3, 1), (4, 1), (5, 1), (1, 1)]
C1: cap 28.0 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 63.0 s
C2: cap 50.0 m/s, 0 loops, 5166 packets over its cells (need 4041), pass 54.6 s
C3: cap 50.0 m/s, 0 loops, 5668 packets over its cells (need 4041), pass 59.7 s
C4: cap 50.0 m/s, 0 loops, 5973 packets over its cells (need 4041), pass 69.4 s
C5: cap 50.0 m/s, 0 loops, 6152 packets over its cells (need 4041), pass 69.0 s
  run 1 river-full: D 4040, 2/2 critical done, sim 4.8 s, wall 0 s, 1787 hops, 40 MAC give-ups, 0/28 gateway pairs with q < 0.5
  run 1 river-full: D 5166, 7/7 critical done, sim 22.5 s, wall 75 s, 99380 hops, 3633 MAC give-ups, 0/277 gateway pairs with q < 0.5
  run 1 river-full: D 5668, 13/13 critical done, sim 82.3 s, wall 682 s, 592479 hops, 20340 MAC give-ups, 0/432 gateway pairs with q < 0.5
  run 1 river-full: D 6152, 8/8 critical done, sim 26.4 s, wall 36 s, 65651 hops, 2015 MAC give-ups, 0/219 gateway pairs with q < 0.5
  run 1 river-full: D 5973, 13/13 critical done, sim 165.6 s, wall 773 s, 691354 hops, 28335 MAC give-ups, 0/400 gateway pairs with q < 0.5
```
