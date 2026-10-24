# ns3-ml10-k8-s3

- Bắt đầu: 2026-10-24 09:21:13, chạy 1153 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --lane 10 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s3-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml10/k8-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 656 land cells, 5 clusters [98, 253, 122, 108, 75], 4 lanes, route 23.8 km, with BS 32.8 km
C1: 1.85 km, 8 critical, beyond reach 0 -> 0, mean distance 650 -> 453 m, shift <= 735 m, k*rho 0.50
C2: 2.68 km, 15 critical, beyond reach 0 -> 0, mean distance 612 -> 584 m, shift <= 211 m, k*rho 0.50
C3: 1.44 km, 8 critical, beyond reach 0 -> 0, mean distance 560 -> 548 m, shift <= 184 m, k*rho 0.50
C4: 1.43 km, 7 critical, beyond reach 0 -> 0, mean distance 531 -> 539 m, shift <= 123 m, k*rho 0.50
C5: 1.56 km, 5 critical, beyond reach 0 -> 0, mean distance 424 -> 398 m, shift <= 85 m, k*rho 0.50
tour: 24.1 km, 482 s, order [(5, 1), (4, 1), (1, 0), (2, 0), (3, 0)]
C1: cap 50.0 m/s, 0 loops, 4700 packets over its cells (need 4041), pass 47.2 s
C2: cap 50.0 m/s, 0 loops, 5435 packets over its cells (need 4041), pass 63.7 s
C3: cap 41.8 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 45.9 s
C4: cap 41.5 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 45.9 s
C5: cap 41.2 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 49.0 s
  run 1 river-full: D 4700, 8/8 critical done, sim 72.9 s, wall 124 s, 228904 hops, 9882 MAC give-ups, 0/224 gateway pairs with q < 0.5
  run 1 river-full: D 4040, 8/8 critical done, sim 76.8 s, wall 110 s, 186707 hops, 5472 MAC give-ups, 0/264 gateway pairs with q < 0.5
  run 1 river-full: D 4040, 7/7 critical done, sim 51.7 s, wall 46 s, 83279 hops, 3379 MAC give-ups, 0/259 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 33.2 s, wall 38 s, 92238 hops, 3493 MAC give-ups, 0/129 gateway pairs with q < 0.5
  run 1 river-full: D 5435, 15/15 critical done, sim 136.4 s, wall 995 s, 798961 hops, 30529 MAC give-ups, 0/463 gateway pairs with q < 0.5
```
