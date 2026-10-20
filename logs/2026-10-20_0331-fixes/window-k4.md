# window-k4

- Bắt đầu: 2026-10-20 04:37:57, chạy 345 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MKw/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --windowKB 400
    python3 tools/mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MLw/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --partition lane --lane 4.5 --windowKB 400
    python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KCw/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids --windowKB 400
    python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMw/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --windowKB 400
    python3 tools/meander_mission.py --clusters 4 --seed 2 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MCw/k4 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12 --windowKB 400
```

**Kết quả**

```text
bearings: C1 6 deg (1865 m inside), C2 52 deg (2270 m inside), C3 138 deg (2155 m inside), C4 0 deg (2070 m inside)
  run 1 river-full: D 4041, 7/7 critical done, sim 18.2 s, wall 23 s, 47661 hops, 1948 MAC give-ups, 0/179 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 52.1 s, wall 52 s, 127422 hops, 4880 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 31.2 s, wall 29 s, 79808 hops, 2879 MAC give-ups, 0/127 gateway pairs with q < 0.5
  run 1 river-full: D 3735, 7/7 critical done, sim 59.6 s, wall 73 s, 159546 hops, 6598 MAC give-ups, 0/157 gateway pairs with q < 0.5
bearings: C1 126 deg (1155 m inside), C2 126 deg (1410 m inside), C3 126 deg (1300 m inside), C4 126 deg (1820 m inside), C5 126 deg (1855 m inside), C6 126 deg (2550 m inside), C7 126 deg (925 m inside)
  run 1 river-full: D 2321, 2/2 critical done, sim 0.8 s, wall 0 s, 545 hops, 24 MAC give-ups, 0/32 gateway pairs with q < 0.5
  run 1 river-full: D 2597, 6/6 critical done, sim 16.0 s, wall 6 s, 23356 hops, 846 MAC give-ups, 0/59 gateway pairs with q < 0.5
  run 1 river-full: D 2821, 4/4 critical done, sim 18.1 s, wall 7 s, 24629 hops, 694 MAC give-ups, 0/86 gateway pairs with q < 0.5
  run 1 river-full: D 3720, 4/4 critical done, sim 18.6 s, wall 9 s, 26537 hops, 704 MAC give-ups, 0/117 gateway pairs with q < 0.5
  run 1 river-full: D 1861, 4/4 critical done, sim 0.9 s, wall 0 s, 785 hops, 40 MAC give-ups, 0/45 gateway pairs with q < 0.5
  run 1 river-full: D 3657, 7/7 critical done, sim 28.2 s, wall 32 s, 99484 hops, 3297 MAC give-ups, 0/101 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 69.2 s, wall 115 s, 280037 hops, 8451 MAC give-ups, 0/152 gateway pairs with q < 0.5
curves: C1 2.87 km, CH 177 m off, k*rho 0.96, C2 3.04 km, CH 31 m off, k*rho 0.99, C3 2.33 km, CH 269 m off, k*rho 0.85, C4 2.97 km, CH 219 m off, k*rho 0.97
  run 1 river-full: D 4041, 7/7 critical done, sim 19.5 s, wall 21 s, 38524 hops, 1749 MAC give-ups, 0/191 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 34.0 s, wall 26 s, 62776 hops, 2349 MAC give-ups, 0/127 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 55.7 s, wall 59 s, 140558 hops, 5388 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 46.0 s, wall 69 s, 143254 hops, 5354 MAC give-ups, 0/161 gateway pairs with q < 0.5
curves: C1 2.48 km, CH 75 m off, k*rho 0.85, C2 2.73 km, CH 120 m off, k*rho 0.92, C3 2.89 km, CH 78 m off, k*rho 1.00, C4 3.29 km, CH 47 m off, k*rho 0.98, C5 1.09 km, CH 35 m off, k*rho 0.96, C6 1.51 km, CH 370 m off, k*rho 0.57
  run 1 river-full: D 4041, 3/3 critical done, sim 30.0 s, wall 15 s, 62844 hops, 2469 MAC give-ups, 0/59 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 37.7 s, wall 30 s, 78246 hops, 2555 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1 river-full: D 2697, 4/4 critical done, sim 4.6 s, wall 1 s, 2300 hops, 60 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 2277, 2/2 critical done, sim 1.6 s, wall 0 s, 806 hops, 22 MAC give-ups, 0/24 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 39.9 s, wall 46 s, 114423 hops, 4204 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 64.4 s, wall 43 s, 112125 hops, 3435 MAC give-ups, 0/152 gateway pairs with q < 0.5
curves: C1 0.98 km, CH 12 m off, k*rho 0.16, C2 1.49 km, CH 131 m off, k*rho 0.78, C3 2.02 km, CH 121 m off, k*rho 0.96, C4 1.60 km, CH 104 m off, k*rho 0.75, C5 1.96 km, CH 7 m off, k*rho 0.97, C6 1.75 km, CH 44 m off, k*rho 0.96, C7 1.78 km, CH 142 m off, k*rho 0.97, C8 1.09 km, CH 35 m off, k*rho 0.96, C9 1.51 km, CH 370 m off, k*rho 0.57
  run 1 river-full: D 2320, 2/2 critical done, sim 1.0 s, wall 0 s, 552 hops, 22 MAC give-ups, 0/30 gateway pairs with q < 0.5
  run 1 river-full: D 3582, 2/2 critical done, sim 2.9 s, wall 1 s, 1484 hops, 24 MAC give-ups, 0/82 gateway pairs with q < 0.5
  run 1 river-full: D 2837, 4/4 critical done, sim 6.0 s, wall 1 s, 4754 hops, 109 MAC give-ups, 0/28 gateway pairs with q < 0.5
  run 1 river-full: D 3731, 3/3 critical done, sim 14.5 s, wall 3 s, 11829 hops, 383 MAC give-ups, 0/80 gateway pairs with q < 0.5
  run 1 river-full: D 3647, 3/3 critical done, sim 10.7 s, wall 3 s, 8311 hops, 241 MAC give-ups, 0/83 gateway pairs with q < 0.5
  run 1 river-full: D 2697, 4/4 critical done, sim 4.6 s, wall 1 s, 2300 hops, 60 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 2277, 2/2 critical done, sim 1.6 s, wall 0 s, 806 hops, 22 MAC give-ups, 0/24 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 3/3 critical done, sim 24.1 s, wall 8 s, 30379 hops, 1303 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 26.7 s, wall 13 s, 43016 hops, 1543 MAC give-ups, 0/85 gateway pairs with q < 0.5
```
