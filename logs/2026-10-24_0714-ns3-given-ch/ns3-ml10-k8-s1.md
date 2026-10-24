# ns3-ml10-k8-s1

- Bắt đầu: 2026-10-24 08:30:49, chạy 828 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --lane 10 --minAxe 2.1 --reach 1000 --parallel --trim 5 --chFrom /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T154/s1-K5/chord --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/ml10/k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 617 land cells, 5 clusters [66, 117, 157, 109, 168], 3 lanes, route 20.6 km, with BS 28.9 km
C1: 1.92 km, 3 critical, beyond reach 0 -> 0, mean distance 329 -> 260 m, shift <= 154 m, k*rho 0.50
C2: 1.98 km, 8 critical, beyond reach 0 -> 0, mean distance 444 -> 444 m, shift <= 162 m, k*rho 0.50
C3: 2.56 km, 11 critical, beyond reach 0 -> 0, mean distance 458 -> 458 m, shift <= 171 m, k*rho 0.50
C4: 2.26 km, 6 critical, beyond reach 0 -> 0, mean distance 376 -> 376 m, shift <= 64 m, k*rho 0.50
C5: 1.79 km, 11 critical, beyond reach 0 -> 0, mean distance 479 -> 473 m, shift <= 44 m, k*rho 0.50
tour: 24.0 km, 479 s, order [(3, 0), (2, 1), (1, 1), (4, 1), (5, 0)]
C1: cap 42.8 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 55.2 s
C2: cap 43.9 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 55.6 s
C3: cap 47.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 63.8 s
C4: cap 50.0 m/s, 0 loops, 4578 packets over its cells (need 4041), pass 55.3 s
C5: cap 50.0 m/s, 0 loops, 4249 packets over its cells (need 4041), pass 45.9 s
  run 1 river-full: D 4040, 3/3 critical done, sim 9.7 s, wall 3 s, 7573 hops, 258 MAC give-ups, 0/123 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 77.1 s, wall 194 s, 363273 hops, 11299 MAC give-ups, 0/209 gateway pairs with q < 0.5
  run 1 river-full: D 4578, 6/6 critical done, sim 33.2 s, wall 47 s, 83002 hops, 2871 MAC give-ups, 0/201 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 11/11 critical done, sim 41.6 s, wall 265 s, 273201 hops, 11229 MAC give-ups, 0/343 gateway pairs with q < 0.5
  run 1 river-full: D 4249, 11/11 critical done, sim 104.5 s, wall 415 s, 425741 hops, 18216 MAC give-ups, 0/336 gateway pairs with q < 0.5
```
