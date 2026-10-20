# full-k8

- Bắt đầu: 2026-10-20 04:25:50, chạy 723 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MK/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --schemes rf
    python3 tools/meander_mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KC/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --partition kmedoids
    python3 tools/meander_mission.py --clusters 8 --seed 4 --work /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/MC/k8 --bin /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/BIN --jobs 3 --span 12
```

**Kết quả**

```text
map: 595 land cells, 12619 nodes, 8 clusters [80, 80, 74, 78, 70, 72, 68, 73], BS -217,-4450
bearings: C1 10 deg (1930 m inside), C2 152 deg (2120 m inside), C3 86 deg (2275 m inside), C4 8 deg (2265 m inside), C5 8 deg (1950 m inside), C6 146 deg (1965 m inside), C7 10 deg (1920 m inside), C8 166 deg (2180 m inside)
tour: 32.0 km, 640 s, order [(6, 1), (3, 0), (1, 1), (5, 0), (7, 1), (8, 1), (4, 1), (2, 1)]
  run 1 river-full: D 3870, 7/7 critical done, sim 17.4 s, wall 14 s, 23902 hops, 736 MAC give-ups, 0/192 gateway pairs with q < 0.5
  run 1 river-full: D 4549, 6/6 critical done, sim 22.4 s, wall 28 s, 60440 hops, 1815 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4548, 7/7 critical done, sim 27.0 s, wall 35 s, 68020 hops, 2165 MAC give-ups, 0/169 gateway pairs with q < 0.5
  run 1 river-full: D 3905, 7/7 critical done, sim 26.6 s, wall 24 s, 54211 hops, 1918 MAC give-ups, 0/131 gateway pairs with q < 0.5
  run 1 river-full: D 3847, 6/6 critical done, sim 19.6 s, wall 11 s, 21035 hops, 798 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 4247, 8/8 critical done, sim 43.3 s, wall 65 s, 123480 hops, 5313 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 4369, 4/4 critical done, sim 32.6 s, wall 19 s, 43703 hops, 1229 MAC give-ups, 0/145 gateway pairs with q < 0.5
  run 1 river-full: D 3939, 7/7 critical done, sim 46.1 s, wall 48 s, 107535 hops, 3193 MAC give-ups, 0/155 gateway pairs with q < 0.5
map: 595 land cells, 12619 nodes, 8 clusters [80, 80, 74, 78, 70, 72, 68, 73], BS -217,-4450
curves: C1 2.33 km, CH 256 m off, k*rho 0.99, C2 3.05 km, CH 185 m off, k*rho 0.99, C3 2.23 km, CH 63 m off, k*rho 0.95, C4 1.92 km, CH 67 m off, k*rho 0.91, C5 2.91 km, CH 326 m off, k*rho 0.86, C6 2.58 km, CH 50 m off, k*rho 0.95, C7 2.17 km, CH 54 m off, k*rho 0.93, C8 2.16 km, CH 152 m off, k*rho 0.81
tour: 34.6 km, 692 s, order [(2, 1), (4, 0), (6, 1), (3, 1), (5, 0), (7, 1), (1, 0), (8, 0)]
  run 1 river-full: D 4817, 7/7 critical done, sim 20.2 s, wall 21 s, 37174 hops, 1116 MAC give-ups, 0/190 gateway pairs with q < 0.5
  run 1 river-full: D 3760, 6/6 critical done, sim 19.3 s, wall 23 s, 50542 hops, 1495 MAC give-ups, 0/152 gateway pairs with q < 0.5
  run 1 river-full: D 2527, 7/7 critical done, sim 30.4 s, wall 38 s, 80631 hops, 2683 MAC give-ups, 0/169 gateway pairs with q < 0.5
  run 1 river-full: D 4427, 7/7 critical done, sim 51.8 s, wall 55 s, 126733 hops, 5126 MAC give-ups, 0/143 gateway pairs with q < 0.5
  run 1 river-full: D 6472, 8/8 critical done, sim 57.9 s, wall 80 s, 155116 hops, 6075 MAC give-ups, 0/167 gateway pairs with q < 0.5
  run 1 river-full: D 4333, 6/6 critical done, sim 17.9 s, wall 14 s, 29647 hops, 972 MAC give-ups, 0/153 gateway pairs with q < 0.5
  run 1 river-full: D 4675, 4/4 critical done, sim 26.2 s, wall 20 s, 48310 hops, 1471 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 1 river-full: D 5505, 7/7 critical done, sim 57.3 s, wall 69 s, 158017 hops, 5804 MAC give-ups, 0/155 gateway pairs with q < 0.5
map: 595 land cells, 12619 nodes, 15 clusters [39, 31, 29, 30, 30, 31, 35, 42, 43, 43, 59, 60, 35, 36, 52], BS -217,-4450
curves: C1 1.65 km, CH 167 m off, k*rho 0.84, C2 1.12 km, CH 73 m off, k*rho 0.62, C3 1.25 km, CH 53 m off, k*rho 0.93, C4 1.16 km, CH 45 m off, k*rho 0.94, C5 1.07 km, CH 25 m off, k*rho 0.91, C6 1.09 km, CH 101 m off, k*rho 0.76, C7 1.82 km, CH 302 m off, k*rho 0.99, C8 2.03 km, CH 34 m off, k*rho 0.95, C9 1.89 km, CH 138 m off, k*rho 0.84, C10 2.20 km, CH 99 m off, k*rho 0.94, C11 2.77 km, CH 34 m off, k*rho 0.98, C12 2.16 km, CH 5 m off, k*rho 0.93, C13 1.56 km, CH 107 m off, k*rho 0.64, C14 1.57 km, CH 46 m off, k*rho 0.81, C15 2.88 km, CH 109 m off, k*rho 0.46
tour: 46.4 km, 929 s, order [(15, 0), (14, 1), (11, 1), (8, 0), (9, 0), (6, 0), (10, 1), (7, 1), (3, 0), (2, 1), (1, 0), (4, 1), (5, 0), (12, 1), (13, 1)]
  run 1 river-full: D 2595, 3/3 critical done, sim 2.4 s, wall 0 s, 1329 hops, 98 MAC give-ups, 0/66 gateway pairs with q < 0.5
  run 1 river-full: D 2839, 3/3 critical done, sim 2.9 s, wall 0 s, 1756 hops, 60 MAC give-ups, 0/64 gateway pairs with q < 0.5
  run 1 river-full: D 2506, 2/2 critical done, sim 1.3 s, wall 0 s, 635 hops, 59 MAC give-ups, 0/61 gateway pairs with q < 0.5
  run 1 river-full: D 2657, 3/3 critical done, sim 4.0 s, wall 1 s, 2110 hops, 77 MAC give-ups, 0/60 gateway pairs with q < 0.5
  run 1 river-full: D 2561, 4/4 critical done, sim 1.7 s, wall 0 s, 1220 hops, 37 MAC give-ups, 0/63 gateway pairs with q < 0.5
  run 1 river-full: D 2939, 6/6 critical done, sim 20.2 s, wall 7 s, 25825 hops, 748 MAC give-ups, 0/77 gateway pairs with q < 0.5
  run 1 river-full: D 3670, 6/6 critical done, sim 24.2 s, wall 12 s, 49416 hops, 1528 MAC give-ups, 0/84 gateway pairs with q < 0.5
  run 1 river-full: D 3266, 4/4 critical done, sim 27.7 s, wall 14 s, 62662 hops, 2023 MAC give-ups, 0/60 gateway pairs with q < 0.5
  run 1 river-full: D 4132, 6/6 critical done, sim 19.4 s, wall 11 s, 35885 hops, 1524 MAC give-ups, 0/92 gateway pairs with q < 0.5
  run 1 river-full: D 4706, 5/5 critical done, sim 16.7 s, wall 13 s, 35274 hops, 1083 MAC give-ups, 0/124 gateway pairs with q < 0.5
  run 1 river-full: D 3844, 2/2 critical done, sim 7.3 s, wall 1 s, 3107 hops, 119 MAC give-ups, 0/68 gateway pairs with q < 0.5
  run 1 river-full: D 3316, 5/5 critical done, sim 17.8 s, wall 6 s, 24180 hops, 939 MAC give-ups, 0/68 gateway pairs with q < 0.5
  run 1 river-full: D 4156, 6/6 critical done, sim 42.5 s, wall 26 s, 84900 hops, 2767 MAC give-ups, 0/89 gateway pairs with q < 0.5
  run 1 river-full: D 5296, 5/5 critical done, sim 70.5 s, wall 59 s, 172119 hops, 6979 MAC give-ups, 0/110 gateway pairs with q < 0.5
  run 1 river-full: D 5522, 6/6 critical done, sim 163.8 s, wall 138 s, 422644 hops, 15325 MAC give-ups, 0/89 gateway pairs with q < 0.5
```
