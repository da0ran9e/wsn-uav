# ns3-ml-k8-s2

- Bắt đầu: 2026-10-24 04:23:06, chạy 592 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 2 --lane 8 --minAxe 2.4 --reach 5 --straight 0.5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS3/ml/k8-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2
```

**Kết quả**

```text
C1: 2.84 km, 7 critical, beyond reach 1 -> 1, mean distance 332 -> 330 m, shift <= 85 m, k*rho 0.56
C2: 3.32 km, 7 critical, beyond reach 0 -> 0, mean distance 267 -> 257 m, shift <= 40 m, k*rho 0.56
C3: 2.74 km, 8 critical, beyond reach 0 -> 0, mean distance 312 -> 311 m, shift <= 45 m, k*rho 0.74
C4: 3.19 km, 8 critical, beyond reach 0 -> 0, mean distance 367 -> 361 m, shift <= 32 m, k*rho 0.74
C5: 4.11 km, 13 critical, beyond reach 0 -> 0, mean distance 279 -> 274 m, shift <= 37 m, k*rho 0.95
tour: 27.9 km, 559 s, order [(5, 0), (4, 0), (1, 0), (2, 0), (3, 0)]
  run 1 river-full: D 5410, 7/7 critical done, sim 25.7 s, wall 27 s, 52522 hops, 1413 MAC give-ups, 0/173 gateway pairs with q < 0.5
  run 1 river-full: D 5139, 7/7 critical done, sim 17.9 s, wall 43 s, 60252 hops, 1731 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 4977, 8/8 critical done, sim 37.8 s, wall 81 s, 93823 hops, 2850 MAC give-ups, 0/273 gateway pairs with q < 0.5
  run 1 river-full: D 5034, 8/8 critical done, sim 56.0 s, wall 161 s, 177496 hops, 7052 MAC give-ups, 0/290 gateway pairs with q < 0.5
  run 1 river-full: D 6465, 13/13 critical done, sim 79.4 s, wall 236 s, 282712 hops, 11825 MAC give-ups, 0/232 gateway pairs with q < 0.5
```
