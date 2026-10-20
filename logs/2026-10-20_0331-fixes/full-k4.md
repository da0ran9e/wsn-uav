# full-k4

- Bắt đầu: 2026-10-20 04:07:53, chạy 417 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MK/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf
    python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KC/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids
    python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MC/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12
```

**Kết quả**

```text
map: 308 land cells, 6532 nodes, 4 clusters [80, 80, 80, 68], BS -87,-2800
bearings: C1 6 deg (1865 m inside), C2 52 deg (2270 m inside), C3 138 deg (2155 m inside), C4 0 deg (2070 m inside)
tour: 16.3 km, 327 s, order [(3, 0), (1, 0), (4, 0), (2, 1)]
  run 1 river-full: D 4324, 7/7 critical done, sim 21.5 s, wall 35 s, 67577 hops, 2719 MAC give-ups, 0/179 gateway pairs with q < 0.5
  run 1 river-full: D 4548, 7/7 critical done, sim 60.0 s, wall 63 s, 148189 hops, 5668 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 4157, 6/6 critical done, sim 36.3 s, wall 36 s, 92028 hops, 3109 MAC give-ups, 0/127 gateway pairs with q < 0.5
  run 1 river-full: D 3735, 7/7 critical done, sim 59.6 s, wall 78 s, 159546 hops, 6598 MAC give-ups, 0/157 gateway pairs with q < 0.5
map: 308 land cells, 6532 nodes, 4 clusters [80, 80, 80, 68], BS -87,-2800
curves: C1 2.87 km, CH 177 m off, k*rho 0.96, C2 3.04 km, CH 31 m off, k*rho 0.99, C3 2.33 km, CH 269 m off, k*rho 0.85, C4 2.97 km, CH 219 m off, k*rho 0.97
tour: 20.0 km, 401 s, order [(3, 0), (1, 0), (4, 1), (2, 1)]
  run 1 river-full: D 4778, 7/7 critical done, sim 32.7 s, wall 37 s, 67208 hops, 2829 MAC give-ups, 0/191 gateway pairs with q < 0.5
  run 1 river-full: D 5128, 7/7 critical done, sim 78.4 s, wall 101 s, 235539 hops, 8744 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 5559, 6/6 critical done, sim 62.8 s, wall 72 s, 170223 hops, 6321 MAC give-ups, 0/129 gateway pairs with q < 0.5
  run 1 river-full: D 5525, 7/7 critical done, sim 83.6 s, wall 137 s, 273928 hops, 9992 MAC give-ups, 0/161 gateway pairs with q < 0.5
map: 308 land cells, 6532 nodes, 9 clusters [18, 19, 44, 45, 45, 39, 39, 37, 22], BS -87,-2800
curves: C1 0.98 km, CH 12 m off, k*rho 0.16, C2 1.49 km, CH 131 m off, k*rho 0.78, C3 2.02 km, CH 121 m off, k*rho 0.96, C4 1.60 km, CH 104 m off, k*rho 0.75, C5 1.96 km, CH 7 m off, k*rho 0.97, C6 1.75 km, CH 44 m off, k*rho 0.96, C7 1.78 km, CH 142 m off, k*rho 0.97, C8 1.09 km, CH 35 m off, k*rho 0.96, C9 1.51 km, CH 370 m off, k*rho 0.57
tour: 26.7 km, 533 s, order [(6, 0), (8, 0), (5, 1), (2, 1), (1, 1), (3, 0), (4, 0), (7, 1), (9, 1)]
  run 1 river-full: D 2320, 2/2 critical done, sim 1.0 s, wall 0 s, 552 hops, 22 MAC give-ups, 0/30 gateway pairs with q < 0.5
  run 1 river-full: D 3582, 2/2 critical done, sim 2.9 s, wall 1 s, 1484 hops, 24 MAC give-ups, 0/82 gateway pairs with q < 0.5
  run 1 river-full: D 2837, 4/4 critical done, sim 6.0 s, wall 1 s, 4754 hops, 109 MAC give-ups, 0/28 gateway pairs with q < 0.5
  run 1 river-full: D 3731, 3/3 critical done, sim 14.5 s, wall 3 s, 11829 hops, 383 MAC give-ups, 0/80 gateway pairs with q < 0.5
  run 1 river-full: D 3647, 3/3 critical done, sim 10.7 s, wall 2 s, 8311 hops, 241 MAC give-ups, 0/83 gateway pairs with q < 0.5
  run 1 river-full: D 2697, 4/4 critical done, sim 4.6 s, wall 1 s, 2300 hops, 60 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 2277, 2/2 critical done, sim 1.6 s, wall 0 s, 806 hops, 22 MAC give-ups, 0/24 gateway pairs with q < 0.5
  run 1 river-full: D 4042, 3/3 critical done, sim 24.0 s, wall 8 s, 30382 hops, 1273 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 4086, 6/6 critical done, sim 27.2 s, wall 13 s, 44781 hops, 1502 MAC give-ups, 0/85 gateway pairs with q < 0.5
```
