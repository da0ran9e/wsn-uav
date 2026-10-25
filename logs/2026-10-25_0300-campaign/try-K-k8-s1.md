# try-K-k8-s1

- Bắt đầu: 2026-10-25 02:42:11, chạy 210 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass --mapRuns --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/K/k8-s1
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 8 clusters [78, 72, 70, 78, 80, 80, 79, 80], BS 173,-3550
bearings: C1 60 deg (1865 m inside), C2 20 deg (1955 m inside), C3 126 deg (2000 m inside), C4 160 deg (2115 m inside), C5 172 deg (2040 m inside), C6 170 deg (1750 m inside), C7 138 deg (2090 m inside), C8 136 deg (2025 m inside)
tour: 30.3 km, 606 s, order [(7, 0), (3, 1), (5, 1), (8, 0), (1, 1), (6, 1), (4, 1), (2, 1)]
C1: cap 46.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 50.7 s
C2: cap 48.6 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 51.5 s
C3: cap 49.6 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 54.1 s
C4: cap 50.0 m/s, 0 loops, 4240 packets over its cells (need 4041), pass 52.6 s
C5: cap 50.0 m/s, 0 loops, 4081 packets over its cells (need 4041), pass 52.2 s
C6: cap 43.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 51.0 s
C7: cap 50.0 m/s, 0 loops, 4195 packets over its cells (need 4041), pass 53.2 s
C8: cap 50.0 m/s, 0 loops, 4052 packets over its cells (need 4041), pass 56.4 s
  run 800101 river-full: D 4745, 5/5 critical done, sim 24.1 s, wall 9 s, 18520 hops, 719 MAC give-ups, 0/171 gateway pairs with q < 0.5
  run 800103 river-full: D 5031, 7/7 critical done, sim 43.0 s, wall 15 s, 33410 hops, 1057 MAC give-ups, 0/144 gateway pairs with q < 0.5
  run 800102 river-full: D 4643, 9/9 critical done, sim 29.4 s, wall 35 s, 61931 hops, 2354 MAC give-ups, 0/149 gateway pairs with q < 0.5
  run 800104 river-full: D 4554, 4/4 critical done, sim 27.2 s, wall 14 s, 30508 hops, 1021 MAC give-ups, 0/170 gateway pairs with q < 0.5
  run 800105 river-full: D 4098, 4/4 critical done, sim 22.7 s, wall 8 s, 22741 hops, 605 MAC give-ups, 0/122 gateway pairs with q < 0.5
  run 800106 river-full: D 4702, 6/6 critical done, sim 21.1 s, wall 7 s, 12000 hops, 442 MAC give-ups, 0/189 gateway pairs with q < 0.5
  run 800107 river-full: D 4938, 5/5 critical done, sim 12.3 s, wall 5 s, 9386 hops, 383 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 800108 river-full: D 5226, 5/5 critical done, sim 33.7 s, wall 14 s, 31569 hops, 1067 MAC give-ups, 0/120 gateway pairs with q < 0.5
```
