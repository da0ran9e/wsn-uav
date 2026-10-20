# window-k6

- Bắt đầu: 2026-10-20 04:43:43, chạy 372 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MKw/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --windowKB 400
    python3 tools/mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MLw/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --partition lane --lane 4.5 --windowKB 400
    python3 tools/meander_mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KCw/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids --windowKB 400
    python3 tools/meander_mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMw/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --windowKB 400
    python3 tools/meander_mission.py --clusters 6 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MCw/k6 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12 --windowKB 400
```

**Kết quả**

```text
bearings: C1 104 deg (2160 m inside), C2 154 deg (1810 m inside), C3 76 deg (2290 m inside), C4 132 deg (2370 m inside), C5 50 deg (1930 m inside), C6 166 deg (2045 m inside)
  run 1 river-full: D 4041, 7/7 critical done, sim 19.1 s, wall 23 s, 43346 hops, 1411 MAC give-ups, 0/194 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 30.5 s, wall 43 s, 92115 hops, 2735 MAC give-ups, 0/155 gateway pairs with q < 0.5
  run 1 river-full: D 3870, 7/7 critical done, sim 17.1 s, wall 14 s, 26221 hops, 708 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 16.8 s, wall 11 s, 23660 hops, 727 MAC give-ups, 0/142 gateway pairs with q < 0.5
  run 1 river-full: D 3631, 9/9 critical done, sim 32.8 s, wall 70 s, 142144 hops, 5392 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 56.4 s, wall 50 s, 110982 hops, 4191 MAC give-ups, 0/162 gateway pairs with q < 0.5
bearings: C1 62 deg (1170 m inside), C2 62 deg (2405 m inside), C3 62 deg (2200 m inside), C4 62 deg (1850 m inside), C5 62 deg (2630 m inside), C6 62 deg (1985 m inside), C7 62 deg (2060 m inside), C8 62 deg (2075 m inside), C9 62 deg (1225 m inside)
  run 1 river-full: D 2353, 3/3 critical done, sim 8.8 s, wall 3 s, 13616 hops, 418 MAC give-ups, 0/46 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 37.2 s, wall 22 s, 83673 hops, 2990 MAC give-ups, 0/81 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 40.0 s, wall 28 s, 86784 hops, 3507 MAC give-ups, 0/101 gateway pairs with q < 0.5
  run 1 river-full: D 3706, 6/6 critical done, sim 38.9 s, wall 29 s, 75927 hops, 3416 MAC give-ups, 0/142 gateway pairs with q < 0.5
  run 1 river-full: D 3987, 5/5 critical done, sim 17.1 s, wall 8 s, 20622 hops, 663 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 29.2 s, wall 18 s, 64949 hops, 2023 MAC give-ups, 0/92 gateway pairs with q < 0.5
  run 1 river-full: D 2445, 6/6 critical done, sim 18.2 s, wall 9 s, 28353 hops, 839 MAC give-ups, 0/79 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 49.3 s, wall 47 s, 131090 hops, 4932 MAC give-ups, 0/128 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 80.8 s, wall 76 s, 200478 hops, 7789 MAC give-ups, 0/128 gateway pairs with q < 0.5
curves: C1 2.49 km, CH 101 m off, k*rho 0.82, C2 2.00 km, CH 8 m off, k*rho 0.98, C3 2.53 km, CH 5 m off, k*rho 0.95, C4 3.66 km, CH 120 m off, k*rho 0.95, C5 1.79 km, CH 34 m off, k*rho 0.89, C6 2.28 km, CH 238 m off, k*rho 1.00
  run 1 river-full: D 4041, 7/7 critical done, sim 29.5 s, wall 39 s, 71955 hops, 2520 MAC give-ups, 0/196 gateway pairs with q < 0.5
  run 1 river-full: D 3761, 9/9 critical done, sim 37.8 s, wall 49 s, 106930 hops, 3403 MAC give-ups, 0/162 gateway pairs with q < 0.5
  run 1 river-full: D 3946, 7/7 critical done, sim 15.1 s, wall 12 s, 22131 hops, 643 MAC give-ups, 0/195 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 18.2 s, wall 11 s, 25247 hops, 783 MAC give-ups, 0/137 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 44.3 s, wall 78 s, 156077 hops, 5348 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 44.8 s, wall 45 s, 97674 hops, 3226 MAC give-ups, 0/160 gateway pairs with q < 0.5
curves: C1 1.39 km, CH 169 m off, k*rho 0.74, C2 1.26 km, CH 135 m off, k*rho 0.98, C3 1.37 km, CH 64 m off, k*rho 0.98, C4 1.98 km, CH 49 m off, k*rho 0.95, C5 1.15 km, CH 96 m off, k*rho 0.93, C6 2.29 km, CH 94 m off, k*rho 0.95, C7 2.58 km, CH 109 m off, k*rho 1.00, C8 2.41 km, CH 25 m off, k*rho 0.37, C9 1.18 km, CH 56 m off, k*rho 0.99, C10 1.85 km, CH 43 m off, k*rho 0.93, C11 2.32 km, CH 9 m off, k*rho 0.47
  run 1 river-full: D 1764, 2/2 critical done, sim 6.2 s, wall 0 s, 2157 hops, 68 MAC give-ups, 0/34 gateway pairs with q < 0.5
  run 1 river-full: D 2602, 4/4 critical done, sim 5.5 s, wall 1 s, 3675 hops, 92 MAC give-ups, 0/38 gateway pairs with q < 0.5
  run 1 river-full: D 2860, 4/4 critical done, sim 4.8 s, wall 1 s, 3320 hops, 70 MAC give-ups, 0/36 gateway pairs with q < 0.5
  run 1 river-full: D 2635, 5/5 critical done, sim 8.7 s, wall 2 s, 6534 hops, 237 MAC give-ups, 0/74 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 24.9 s, wall 8 s, 28456 hops, 870 MAC give-ups, 0/76 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 26.8 s, wall 31 s, 73388 hops, 2224 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 30.4 s, wall 34 s, 82359 hops, 3449 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 2549, 4/4 critical done, sim 15.6 s, wall 5 s, 15703 hops, 587 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 31.4 s, wall 47 s, 118042 hops, 3728 MAC give-ups, 0/155 gateway pairs with q < 0.5
  run 1 river-full: D 3445, 5/5 critical done, sim 46.6 s, wall 19 s, 90692 hops, 2914 MAC give-ups, 0/59 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 34.2 s, wall 22 s, 69665 hops, 2552 MAC give-ups, 0/109 gateway pairs with q < 0.5
curves: C1 1.39 km, CH 169 m off, k*rho 0.74, C2 1.26 km, CH 135 m off, k*rho 0.98, C3 1.37 km, CH 64 m off, k*rho 0.98, C4 1.98 km, CH 49 m off, k*rho 0.95, C5 1.15 km, CH 96 m off, k*rho 0.93, C6 1.72 km, CH 95 m off, k*rho 0.94, C7 1.41 km, CH 137 m off, k*rho 0.75, C8 1.96 km, CH 22 m off, k*rho 0.89, C9 2.41 km, CH 25 m off, k*rho 0.37, C10 1.18 km, CH 56 m off, k*rho 0.99, C11 1.85 km, CH 43 m off, k*rho 0.93, C12 2.32 km, CH 9 m off, k*rho 0.47
  run 1 river-full: D 1764, 2/2 critical done, sim 6.2 s, wall 0 s, 2157 hops, 68 MAC give-ups, 0/34 gateway pairs with q < 0.5
  run 1 river-full: D 2602, 4/4 critical done, sim 5.5 s, wall 1 s, 3675 hops, 92 MAC give-ups, 0/38 gateway pairs with q < 0.5
  run 1 river-full: D 2860, 4/4 critical done, sim 4.8 s, wall 1 s, 3320 hops, 70 MAC give-ups, 0/36 gateway pairs with q < 0.5
  run 1 river-full: D 2635, 5/5 critical done, sim 8.7 s, wall 2 s, 6534 hops, 237 MAC give-ups, 0/74 gateway pairs with q < 0.5
  run 1 river-full: D 3134, 5/5 critical done, sim 4.7 s, wall 1 s, 3516 hops, 140 MAC give-ups, 0/107 gateway pairs with q < 0.5
  run 1 river-full: D 3599, 4/4 critical done, sim 5.3 s, wall 2 s, 5502 hops, 162 MAC give-ups, 0/79 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 24.9 s, wall 8 s, 28456 hops, 870 MAC give-ups, 0/76 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 11.9 s, wall 7 s, 20513 hops, 607 MAC give-ups, 0/98 gateway pairs with q < 0.5
  run 1 river-full: D 2549, 4/4 critical done, sim 15.6 s, wall 5 s, 15703 hops, 587 MAC give-ups, 0/85 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 34.2 s, wall 21 s, 69665 hops, 2552 MAC give-ups, 0/109 gateway pairs with q < 0.5
  run 1 river-full: D 3445, 5/5 critical done, sim 46.6 s, wall 19 s, 90692 hops, 2914 MAC give-ups, 0/59 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 31.4 s, wall 47 s, 118042 hops, 3728 MAC give-ups, 0/155 gateway pairs with q < 0.5
```
