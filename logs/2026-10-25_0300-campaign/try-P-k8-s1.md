# try-P-k8-s1

- Bắt đầu: 2026-10-25 02:42:11, chạy 237 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --schemes rf,d --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k8-s1
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 8 clusters [78, 72, 70, 78, 80, 80, 79, 80], BS 173,-3550
bearings: C1 60 deg (1865 m inside), C2 20 deg (1955 m inside), C3 126 deg (2000 m inside), C4 160 deg (2115 m inside), C5 172 deg (2040 m inside), C6 170 deg (1750 m inside), C7 138 deg (2090 m inside), C8 136 deg (2025 m inside)
chord-t: C1 20 deg, C2 116 deg, C3 22 deg, C4 54 deg, C5 88 deg, C6 160 deg, C7 172 deg, C8 136 deg
tour: 30.6 km, 612 s, order [(2, 0), (3, 1), (7, 1), (6, 0), (1, 0), (8, 1), (5, 1), (4, 1)]
C1: cap 40.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 55.7 s
C2: cap 41.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 58.6 s
C3: cap 42.7 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 53.2 s
C4: cap 45.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 50.8 s
C5: cap 41.2 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 51.3 s
C6: cap 42.0 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 51.2 s
C7: cap 45.6 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 62.2 s
C8: cap 50.0 m/s, 0 loops, 4052 packets over its cells (need 4041), pass 56.4 s
  run 800101 direct: D 5153, 5/5 critical done, sim 12.6 s, wall 6 s, 12004 hops, 408 MAC give-ups, 0/165 gateway pairs with q < 0.5
  run 800101 river-full: D 5153, 5/5 critical done, sim 10.9 s, wall 7 s, 13739 hops, 418 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 800102 direct: D 5532, 9/9 critical done, sim 30.0 s, wall 17 s, 38225 hops, 1208 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 800103 river-full: D 4897, 7/7 critical done, sim 17.8 s, wall 6 s, 14029 hops, 538 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 800102 river-full: D 5532, 9/9 critical done, sim 34.6 s, wall 25 s, 51302 hops, 1560 MAC give-ups, 0/147 gateway pairs with q < 0.5
  run 800104 river-full: D 4717, 4/4 critical done, sim 18.6 s, wall 4 s, 9560 hops, 507 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 800103 direct: D 4897, 7/7 critical done, sim 18.8 s, wall 7 s, 16706 hops, 625 MAC give-ups, 0/126 gateway pairs with q < 0.5
  run 800104 direct: D 4717, 4/4 critical done, sim 18.9 s, wall 5 s, 12456 hops, 674 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 800105 river-full: D 4654, 4/4 critical done, sim 13.2 s, wall 4 s, 7873 hops, 175 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 800105 direct: D 4654, 4/4 critical done, sim 13.4 s, wall 2 s, 4826 hops, 69 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 800106 direct: D 4591, 6/6 critical done, sim 24.4 s, wall 4 s, 9238 hops, 460 MAC give-ups, 0/192 gateway pairs with q < 0.5
  run 800106 river-full: D 4591, 6/6 critical done, sim 23.2 s, wall 7 s, 12149 hops, 448 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800107 river-full: D 5833, 5/5 critical done, sim 4.9 s, wall 3 s, 5445 hops, 141 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800107 direct: D 5833, 5/5 critical done, sim 5.1 s, wall 2 s, 4036 hops, 159 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800108 river-full: D 5226, 5/5 critical done, sim 33.7 s, wall 13 s, 31569 hops, 1067 MAC give-ups, 0/120 gateway pairs with q < 0.5
  run 800108 direct: D 5226, 5/5 critical done, sim 22.5 s, wall 15 s, 40056 hops, 1168 MAC give-ups, 0/120 gateway pairs with q < 0.5
```
