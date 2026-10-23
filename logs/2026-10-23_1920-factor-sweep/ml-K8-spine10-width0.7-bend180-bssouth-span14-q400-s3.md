# ml-K8-spine10-width0.7-bend180-bssouth-span14-q400-s3

- Bắt đầu: 2026-10-23 19:28:58, chạy 9 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 3 --shape spine=10,bend=180,width=0.7 --bs south --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine10-width0.7-bend180-bssouth-span14-q400-s3/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --geometry
```

**Kết quả**

```text
map: 872 land cells, 12 clusters [89, 90, 90, 90, 91, 92, 92, 92, 36, 37, 36, 37], 3 lanes, route 30.1 km, with BS 41.3 km
C1: 2.58 km, 8 critical, beyond the River half width 1 -> 1, mean distance 194 -> 191 m, shift <= 54 m, k*rho 1.11
C2: 2.99 km, 6 critical, beyond the River half width 1 -> 0, mean distance 142 -> 147 m, shift <= 107 m, k*rho 1.11
C3: 1.73 km, 5 critical, beyond the River half width 2 -> 2, mean distance 284 -> 236 m, shift <= 114 m, k*rho 1.11
C4: 2.17 km, 6 critical, beyond the River half width 3 -> 4, mean distance 391 -> 383 m, shift <= 106 m, k*rho 1.11
C5: 2.70 km, 4 critical, beyond the River half width 1 -> 1, mean distance 259 -> 233 m, shift <= 174 m, k*rho 0.83
C6: 2.57 km, 5 critical, beyond the River half width 1 -> 1, mean distance 120 -> 142 m, shift <= 187 m, k*rho 0.83
C7: 2.28 km, 7 critical, beyond the River half width 4 -> 2, mean distance 283 -> 246 m, shift <= 168 m, k*rho 0.83
C8: 2.39 km, 8 critical, beyond the River half width 4 -> 4, mean distance 248 -> 241 m, shift <= 140 m, k*rho 0.83
C9: 1.88 km, 3 critical, beyond the River half width 0 -> 0, mean distance 168 -> 94 m, shift <= 119 m, k*rho 1.01
C10: 2.27 km, 2 critical, beyond the River half width 0 -> 0, mean distance 88 -> 72 m, shift <= 102 m, k*rho 1.01
C11: 1.76 km, 5 critical, beyond the River half width 1 -> 1, mean distance 178 -> 161 m, shift <= 82 m, k*rho 1.01
C12: 1.87 km, 2 critical, beyond the River half width 1 -> 0, mean distance 214 -> 155 m, shift <= 93 m, k*rho 1.01
```
