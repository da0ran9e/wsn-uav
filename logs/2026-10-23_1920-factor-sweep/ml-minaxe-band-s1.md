# ml-minaxe-band-s1

- Bắt đầu: 2026-10-23 20:03:21, chạy 6 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 1 --shape spine=10,bend=60,width=0.7 --bs end --span 14 --lane 8 --minAxe 2.4 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/ml/band-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --geometry
```

**Kết quả**

```text
map: 703 land cells, 8 clusters [69, 118, 90, 31, 127, 130, 58, 80], 2 lanes, route 25.4 km, with BS 27.7 km
C1: 3.16 km, 4 critical, beyond the River half width 1 -> 1, mean distance 124 -> 133 m, shift <= 132 m, k*rho 1.15
C2: 3.02 km, 9 critical, beyond the River half width 5 -> 5, mean distance 326 -> 326 m, shift <= 186 m, k*rho 1.15
C3: 3.30 km, 8 critical, beyond the River half width 3 -> 2, mean distance 242 -> 242 m, shift <= 190 m, k*rho 1.15
C4: 2.58 km, 3 critical, beyond the River half width 0 -> 0, mean distance 96 -> 149 m, shift <= 101 m, k*rho 1.15
C5: 2.62 km, 9 critical, beyond the River half width 5 -> 4, mean distance 280 -> 271 m, shift <= 118 m, k*rho 0.99
C6: 3.01 km, 9 critical, beyond the River half width 4 -> 4, mean distance 324 -> 284 m, shift <= 132 m, k*rho 0.99
C7: 2.66 km, 4 critical, beyond the River half width 0 -> 0, mean distance 94 -> 86 m, shift <= 103 m, k*rho 0.99
C8: 3.23 km, 4 critical, beyond the River half width 0 -> 0, mean distance 107 -> 89 m, shift <= 72 m, k*rho 0.99
```
