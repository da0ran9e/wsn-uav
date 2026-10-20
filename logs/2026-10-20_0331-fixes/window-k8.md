# window-k8

- Bắt đầu: 2026-10-20 04:49:59, chạy 531 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MKw/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --windowKB 400
    python3 tools/mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MLw/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf --partition lane --lane 4.5 --windowKB 400
    python3 tools/meander_mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KCw/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids --windowKB 400
    python3 tools/meander_mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MMw/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --windowKB 400
    python3 tools/meander_mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MCw/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12 --windowKB 400
```

**Kết quả**

```text
bearings: C1 10 deg (1930 m inside), C2 152 deg (2120 m inside), C3 86 deg (2275 m inside), C4 8 deg (2265 m inside), C5 8 deg (1950 m inside), C6 146 deg (1965 m inside), C7 10 deg (1920 m inside), C8 166 deg (2180 m inside)
  run 1 river-full: D 3870, 7/7 critical done, sim 17.4 s, wall 14 s, 23902 hops, 736 MAC give-ups, 0/192 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 19.6 s, wall 21 s, 46745 hops, 1596 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 26.3 s, wall 27 s, 58980 hops, 1861 MAC give-ups, 0/169 gateway pairs with q < 0.5
  run 1 river-full: D 3905, 7/7 critical done, sim 26.6 s, wall 23 s, 54211 hops, 1918 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 34.5 s, wall 48 s, 96336 hops, 4187 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 3847, 6/6 critical done, sim 19.6 s, wall 11 s, 21035 hops, 798 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 25.5 s, wall 13 s, 29620 hops, 880 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 1 river-full: D 3939, 7/7 critical done, sim 46.1 s, wall 44 s, 107535 hops, 3193 MAC give-ups, 0/155 gateway pairs with q < 0.5
bearings: C1 120 deg (1555 m inside), C2 120 deg (2595 m inside), C3 120 deg (2420 m inside), C4 120 deg (1900 m inside), C5 120 deg (2560 m inside), C6 120 deg (2250 m inside), C7 120 deg (1940 m inside), C8 120 deg (1720 m inside), C9 120 deg (1900 m inside), C10 120 deg (2075 m inside), C11 120 deg (1555 m inside)
  run 1 river-full: D 4041, 4/4 critical done, sim 32.9 s, wall 17 s, 67278 hops, 2351 MAC give-ups, 0/74 gateway pairs with q < 0.5
  run 1 river-full: D 3118, 7/7 critical done, sim 32.1 s, wall 30 s, 86609 hops, 2543 MAC give-ups, 0/120 gateway pairs with q < 0.5
  run 1 river-full: D 3811, 6/6 critical done, sim 28.6 s, wall 15 s, 49480 hops, 1314 MAC give-ups, 0/110 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 42.7 s, wall 34 s, 90971 hops, 2830 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 3884, 5/5 critical done, sim 37.1 s, wall 27 s, 82665 hops, 3522 MAC give-ups, 0/102 gateway pairs with q < 0.5
  run 1 river-full: D 3464, 5/5 critical done, sim 18.6 s, wall 11 s, 28712 hops, 1282 MAC give-ups, 0/106 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 77.1 s, wall 111 s, 243534 hops, 11025 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 1 river-full: D 3811, 6/6 critical done, sim 20.4 s, wall 12 s, 34725 hops, 1121 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 60.1 s, wall 93 s, 254971 hops, 7700 MAC give-ups, 0/121 gateway pairs with q < 0.5
  run 1 river-full: D 3119, 4/4 critical done, sim 27.7 s, wall 7 s, 37942 hops, 1501 MAC give-ups, 0/41 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 40.6 s, wall 28 s, 81964 hops, 3784 MAC give-ups, 0/115 gateway pairs with q < 0.5
curves: C1 2.33 km, CH 256 m off, k*rho 0.99, C2 3.05 km, CH 185 m off, k*rho 0.99, C3 2.23 km, CH 63 m off, k*rho 0.95, C4 1.92 km, CH 67 m off, k*rho 0.91, C5 2.91 km, CH 326 m off, k*rho 0.86, C6 2.58 km, CH 50 m off, k*rho 0.95, C7 2.17 km, CH 54 m off, k*rho 0.93, C8 2.16 km, CH 152 m off, k*rho 0.81
  run 1 river-full: D 4041, 7/7 critical done, sim 18.7 s, wall 16 s, 29644 hops, 786 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 3760, 6/6 critical done, sim 19.3 s, wall 22 s, 50542 hops, 1495 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 8/8 critical done, sim 25.1 s, wall 23 s, 45694 hops, 1554 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 2527, 7/7 critical done, sim 30.4 s, wall 38 s, 80631 hops, 2683 MAC give-ups, 0/169 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 37.3 s, wall 33 s, 78944 hops, 2348 MAC give-ups, 0/151 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 35.3 s, wall 40 s, 92935 hops, 3613 MAC give-ups, 0/138 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 16.7 s, wall 12 s, 24617 hops, 827 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 18.4 s, wall 10 s, 23997 hops, 733 MAC give-ups, 0/146 gateway pairs with q < 0.5
curves: C1 1.65 km, CH 167 m off, k*rho 0.84, C2 1.12 km, CH 73 m off, k*rho 0.62, C3 2.65 km, CH 82 m off, k*rho 0.96, C4 2.22 km, CH 17 m off, k*rho 0.89, C5 1.82 km, CH 302 m off, k*rho 0.99, C6 3.10 km, CH 34 m off, k*rho 0.91, C7 2.97 km, CH 68 m off, k*rho 0.94, C8 2.77 km, CH 34 m off, k*rho 0.98, C9 2.16 km, CH 5 m off, k*rho 0.93, C10 3.28 km, CH 35 m off, k*rho 0.87, C11 2.88 km, CH 109 m off, k*rho 0.46
  run 1 river-full: D 2595, 3/3 critical done, sim 2.4 s, wall 0 s, 1329 hops, 98 MAC give-ups, 0/66 gateway pairs with q < 0.5
  run 1 river-full: D 2939, 6/6 critical done, sim 20.2 s, wall 7 s, 25825 hops, 748 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 20.9 s, wall 15 s, 36825 hops, 1399 MAC give-ups, 0/138 gateway pairs with q < 0.5
  run 1 river-full: D 3266, 4/4 critical done, sim 27.7 s, wall 15 s, 62662 hops, 2023 MAC give-ups, 0/60 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 37.2 s, wall 48 s, 133128 hops, 3566 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 41.3 s, wall 28 s, 93274 hops, 3502 MAC give-ups, 0/104 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 10.1 s, wall 5 s, 11919 hops, 336 MAC give-ups, 0/125 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 77.5 s, wall 84 s, 211488 hops, 6567 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 111.2 s, wall 120 s, 318858 hops, 11969 MAC give-ups, 0/138 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 66.9 s, wall 38 s, 126911 hops, 5110 MAC give-ups, 0/74 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 7/7 critical done, sim 78.8 s, wall 81 s, 207706 hops, 6428 MAC give-ups, 0/145 gateway pairs with q < 0.5
curves: C1 1.65 km, CH 167 m off, k*rho 0.84, C2 1.12 km, CH 73 m off, k*rho 0.62, C3 1.25 km, CH 53 m off, k*rho 0.93, C4 1.16 km, CH 45 m off, k*rho 0.94, C5 1.07 km, CH 25 m off, k*rho 0.91, C6 1.09 km, CH 101 m off, k*rho 0.76, C7 1.82 km, CH 302 m off, k*rho 0.99, C8 2.03 km, CH 34 m off, k*rho 0.95, C9 1.89 km, CH 138 m off, k*rho 0.84, C10 2.20 km, CH 99 m off, k*rho 0.94, C11 2.77 km, CH 34 m off, k*rho 0.98, C12 2.16 km, CH 5 m off, k*rho 0.93, C13 1.56 km, CH 107 m off, k*rho 0.64, C14 1.57 km, CH 46 m off, k*rho 0.81, C15 2.88 km, CH 109 m off, k*rho 0.46
  run 1 river-full: D 2839, 3/3 critical done, sim 2.9 s, wall 1 s, 1756 hops, 60 MAC give-ups, 0/64 gateway pairs with q < 0.5
  run 1 river-full: D 2595, 3/3 critical done, sim 2.4 s, wall 1 s, 1329 hops, 98 MAC give-ups, 0/66 gateway pairs with q < 0.5
  run 1 river-full: D 2506, 2/2 critical done, sim 1.3 s, wall 0 s, 635 hops, 59 MAC give-ups, 0/61 gateway pairs with q < 0.5
  run 1 river-full: D 2657, 3/3 critical done, sim 4.0 s, wall 1 s, 2110 hops, 77 MAC give-ups, 0/60 gateway pairs with q < 0.5
  run 1 river-full: D 2561, 4/4 critical done, sim 1.7 s, wall 0 s, 1220 hops, 37 MAC give-ups, 0/63 gateway pairs with q < 0.5
  run 1 river-full: D 2939, 6/6 critical done, sim 20.2 s, wall 7 s, 25825 hops, 748 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 3670, 6/6 critical done, sim 24.2 s, wall 13 s, 49416 hops, 1528 MAC give-ups, 0/84 gateway pairs with q < 0.5
  run 1 river-full: D 3266, 4/4 critical done, sim 27.7 s, wall 15 s, 62662 hops, 2023 MAC give-ups, 0/60 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 18.9 s, wall 10 s, 30681 hops, 1352 MAC give-ups, 0/92 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 10.1 s, wall 5 s, 11919 hops, 336 MAC give-ups, 0/125 gateway pairs with q < 0.5
  run 1 river-full: D 3844, 2/2 critical done, sim 7.3 s, wall 1 s, 3107 hops, 119 MAC give-ups, 0/68 gateway pairs with q < 0.5
  run 1 river-full: D 3316, 5/5 critical done, sim 17.8 s, wall 6 s, 24180 hops, 939 MAC give-ups, 0/68 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 41.3 s, wall 24 s, 78026 hops, 2524 MAC give-ups, 0/89 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 5/5 critical done, sim 41.3 s, wall 30 s, 93274 hops, 3502 MAC give-ups, 0/104 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 6/6 critical done, sim 66.9 s, wall 39 s, 126911 hops, 5110 MAC give-ups, 0/74 gateway pairs with q < 0.5
```
