# ns3-chordB-k8-s2

- Bắt đầu: 2026-10-24 08:41:26, chạy 378 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 2 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/chordB/k8-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --banks local --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 596 land cells, 12640 nodes, 5 clusters [120, 116, 120, 120, 120], BS 0,-3850
bearings: C1 112 deg (2270 m inside), C2 96 deg (2260 m inside), C3 104 deg (2090 m inside), C4 42 deg (2425 m inside), C5 150 deg (2395 m inside)
chord-t: C1 176 deg, C2 130 deg, C3 28 deg, C4 66 deg, C5 100 deg
C1: bent towards 5 critical cells, shift <= 185 m
C2: bent towards 3 critical cells, shift <= 172 m
C3: bent towards 6 critical cells, shift <= 111 m
C4: bent towards 5 critical cells, shift <= 66 m
C5: bent towards 3 critical cells, shift <= 233 m
tour: 23.1 km, 462 s, order [(5, 0), (3, 1), (1, 1), (4, 1), (2, 1)]
C1: cap 39.7 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 66.0 s
C2: cap 41.8 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 61.7 s
C3: cap 49.0 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 46.5 s
C4: cap 38.8 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 62.7 s
C5: cap 50.0 m/s, 0 loops, 4100 packets over its cells (need 4041), pass 67.2 s
  run 1 river-full: D 5787, 5/5 critical done, sim 16.3 s, wall 9 s, 11333 hops, 293 MAC give-ups, 0/196 gateway pairs with q < 0.5
  run 1 river-full: D 6125, 7/7 critical done, sim 34.2 s, wall 28 s, 37453 hops, 1303 MAC give-ups, 0/211 gateway pairs with q < 0.5
  run 1 river-full: D 5748, 8/8 critical done, sim 70.3 s, wall 65 s, 86845 hops, 2118 MAC give-ups, 0/267 gateway pairs with q < 0.5
  run 1 river-full: D 4471, 9/9 critical done, sim 59.7 s, wall 133 s, 165086 hops, 5669 MAC give-ups, 0/261 gateway pairs with q < 0.5
  run 1 river-full: D 6056, 8/8 critical done, sim 41.9 s, wall 90 s, 125148 hops, 4679 MAC give-ups, 0/235 gateway pairs with q < 0.5
```
