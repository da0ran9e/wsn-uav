# full-k6

- Bắt đầu: 2026-10-20 04:14:50, chạy 660 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MK/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf
    python3 tools/meander_mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KC/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids
    python3 tools/meander_mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MC/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12
```

**Kết quả**

```text
map: 465 land cells, 9862 nodes, 6 clusters [80, 80, 80, 80, 78, 67], BS -130,-4000
bearings: C1 104 deg (2160 m inside), C2 154 deg (1810 m inside), C3 76 deg (2290 m inside), C4 132 deg (2370 m inside), C5 50 deg (1930 m inside), C6 166 deg (2045 m inside)
tour: 26.0 km, 519 s, order [(6, 0), (1, 0), (5, 0), (4, 0), (2, 1), (3, 1)]
  run 1 river-full: D 4325, 7/7 critical done, sim 20.7 s, wall 29 s, 52214 hops, 1659 MAC give-ups, 0/194 gateway pairs with q < 0.5
  run 1 river-full: D 3631, 9/9 critical done, sim 32.8 s, wall 73 s, 142144 hops, 5392 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1 river-full: D 4580, 8/8 critical done, sim 37.3 s, wall 76 s, 146245 hops, 4948 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 3870, 7/7 critical done, sim 17.1 s, wall 15 s, 26221 hops, 708 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 4104, 7/7 critical done, sim 16.8 s, wall 12 s, 24320 hops, 693 MAC give-ups, 0/142 gateway pairs with q < 0.5
  run 1 river-full: D 4757, 7/7 critical done, sim 71.3 s, wall 87 s, 182383 hops, 6461 MAC give-ups, 0/162 gateway pairs with q < 0.5
map: 465 land cells, 9862 nodes, 6 clusters [80, 80, 80, 80, 78, 67], BS -130,-4000
curves: C1 2.49 km, CH 101 m off, k*rho 0.82, C2 2.00 km, CH 8 m off, k*rho 0.98, C3 2.53 km, CH 5 m off, k*rho 0.95, C4 3.66 km, CH 120 m off, k*rho 0.95, C5 1.79 km, CH 34 m off, k*rho 0.89, C6 2.28 km, CH 238 m off, k*rho 1.00
tour: 26.7 km, 535 s, order [(6, 1), (1, 0), (4, 0), (5, 1), (2, 0), (3, 1)]
  run 1 river-full: D 5324, 7/7 critical done, sim 35.2 s, wall 53 s, 91466 hops, 3062 MAC give-ups, 0/196 gateway pairs with q < 0.5
  run 1 river-full: D 3761, 9/9 critical done, sim 37.8 s, wall 54 s, 106930 hops, 3403 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 3946, 7/7 critical done, sim 15.1 s, wall 12 s, 22131 hops, 643 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 4593, 7/7 critical done, sim 18.8 s, wall 14 s, 31976 hops, 1170 MAC give-ups, 0/137 gateway pairs with q < 0.5
  run 1 river-full: D 4360, 8/8 critical done, sim 65.2 s, wall 103 s, 200494 hops, 7607 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 6744, 7/7 critical done, sim 108.4 s, wall 157 s, 330134 hops, 12002 MAC give-ups, 0/160 gateway pairs with q < 0.5
map: 465 land cells, 9862 nodes, 12 clusters [21, 36, 23, 37, 20, 45, 45, 45, 65, 47, 48, 33], BS -130,-4000
curves: C1 1.39 km, CH 169 m off, k*rho 0.74, C2 1.26 km, CH 135 m off, k*rho 0.98, C3 1.37 km, CH 64 m off, k*rho 0.98, C4 1.98 km, CH 49 m off, k*rho 0.95, C5 1.15 km, CH 96 m off, k*rho 0.93, C6 1.72 km, CH 95 m off, k*rho 0.94, C7 1.41 km, CH 137 m off, k*rho 0.75, C8 1.96 km, CH 22 m off, k*rho 0.89, C9 2.41 km, CH 25 m off, k*rho 0.37, C10 1.18 km, CH 56 m off, k*rho 0.99, C11 1.85 km, CH 43 m off, k*rho 0.93, C12 2.32 km, CH 9 m off, k*rho 0.47
tour: 37.1 km, 742 s, order [(12, 0), (6, 1), (4, 0), (3, 1), (1, 0), (2, 1), (5, 0), (8, 1), (7, 1), (9, 0), (11, 1), (10, 1)]
  run 1 river-full: D 1764, 2/2 critical done, sim 6.2 s, wall 0 s, 2157 hops, 68 MAC give-ups, 0/34 gateway pairs with q < 0.5
  run 1 river-full: D 2602, 4/4 critical done, sim 5.5 s, wall 1 s, 3675 hops, 92 MAC give-ups, 0/38 gateway pairs with q < 0.5
  run 1 river-full: D 2860, 4/4 critical done, sim 4.8 s, wall 1 s, 3320 hops, 70 MAC give-ups, 0/36 gateway pairs with q < 0.5
  run 1 river-full: D 2635, 5/5 critical done, sim 8.7 s, wall 2 s, 6534 hops, 237 MAC give-ups, 0/74 gateway pairs with q < 0.5
  run 1 river-full: D 3134, 5/5 critical done, sim 4.7 s, wall 1 s, 3516 hops, 140 MAC give-ups, 0/107 gateway pairs with q < 0.5
  run 1 river-full: D 3599, 4/4 critical done, sim 5.3 s, wall 2 s, 5502 hops, 162 MAC give-ups, 0/79 gateway pairs with q < 0.5
  run 1 river-full: D 4325, 4/4 critical done, sim 31.7 s, wall 11 s, 39218 hops, 1214 MAC give-ups, 0/76 gateway pairs with q < 0.5
  run 1 river-full: D 4278, 4/4 critical done, sim 14.8 s, wall 10 s, 29262 hops, 870 MAC give-ups, 0/98 gateway pairs with q < 0.5
  run 1 river-full: D 2549, 4/4 critical done, sim 15.6 s, wall 5 s, 15703 hops, 587 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 3445, 5/5 critical done, sim 46.6 s, wall 22 s, 90692 hops, 2914 MAC give-ups, 0/59 gateway pairs with q < 0.5
  run 1 river-full: D 4133, 6/6 critical done, sim 36.2 s, wall 25 s, 72509 hops, 2719 MAC give-ups, 0/109 gateway pairs with q < 0.5
  run 1 river-full: D 5663, 5/5 critical done, sim 65.3 s, wall 100 s, 218579 hops, 7088 MAC give-ups, 0/155 gateway pairs with q < 0.5
```
