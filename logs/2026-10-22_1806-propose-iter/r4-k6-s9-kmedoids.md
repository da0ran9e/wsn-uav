# r4-k6-s9-kmedoids

- Bắt đầu: 2026-10-22 19:15:13, chạy 519 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 9 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KD-k6-s9 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 1 --schemes rf --windowKB 400 --windowAt crit --critRing domain
```

**Kết quả**

```text
map: 446 land cells, 9459 nodes, 6 clusters [80, 80, 80, 75, 62, 69], BS -303,-3700
bearings: C1 174 deg (1940 m inside), C2 92 deg (2195 m inside), C3 146 deg (2265 m inside), C4 174 deg (2745 m inside), C5 76 deg (1880 m inside), C6 112 deg (1825 m inside)
tour: 28.0 km, 559 s, order [(4, 0), (3, 0), (6, 1), (5, 0), (1, 1), (2, 1)]
  run 1 river-full: D 3902, 6/6 critical done, sim 13.4 s, wall 13 s, 21625 hops, 741 MAC give-ups, 0/172 gateway pairs with q < 0.5
  run 1 river-full: D 4391, 7/7 critical done, sim 91.4 s, wall 161 s, 319731 hops, 13375 MAC give-ups, 0/129 gateway pairs with q < 0.5
  run 1 river-full: D 4541, 7/7 critical done, sim 26.2 s, wall 44 s, 72336 hops, 2293 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 5496, 7/7 critical done, sim 15.2 s, wall 24 s, 38062 hops, 1240 MAC give-ups, 0/151 gateway pairs with q < 0.5
  run 1 river-full: D 3767, 4/4 critical done, sim 12.2 s, wall 5 s, 11632 hops, 317 MAC give-ups, 0/115 gateway pairs with q < 0.5
  run 1 river-full: D 3657, 4/4 critical done, sim 17.0 s, wall 8 s, 14322 hops, 472 MAC give-ups, 0/156 gateway pairs with q < 0.5
```
