# ns3-chordB-k8-s1

- Bắt đầu: 2026-10-24 08:26:09, chạy 280 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/chordB/k8-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --banks local --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 5 clusters [124, 124, 124, 124, 121], BS 173,-3550
bearings: C1 56 deg (3035 m inside), C2 174 deg (2765 m inside), C3 66 deg (2570 m inside), C4 70 deg (2330 m inside), C5 30 deg (3095 m inside)
chord-t: C1 30 deg, C2 20 deg, C3 52 deg, C4 70 deg, C5 70 deg
C1: bent towards 5 critical cells, shift <= 314 m
C2: bent towards 4 critical cells, shift <= 143 m
C3: bent towards 6 critical cells, shift <= 173 m
C4: bent towards 5 critical cells, shift <= 197 m
C5: bent towards 4 critical cells, shift <= 106 m
tour: 22.8 km, 455 s, order [(4, 0), (5, 0), (1, 1), (3, 1), (2, 0)]
C1: cap 50.0 m/s, 0 loops, 4397 packets over its cells (need 4041), pass 70.8 s
C2: cap 50.0 m/s, 0 loops, 4499 packets over its cells (need 4041), pass 56.4 s
C3: cap 34.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 78.7 s
C4: cap 47.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 61.0 s
C5: cap 44.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 53.7 s
  run 1 river-full: D 6809, 6/6 critical done, sim 25.3 s, wall 22 s, 35153 hops, 1230 MAC give-ups, 0/235 gateway pairs with q < 0.5
  run 1 river-full: D 7702, 8/8 critical done, sim 14.1 s, wall 7 s, 12118 hops, 305 MAC give-ups, 0/199 gateway pairs with q < 0.5
  run 1 river-full: D 5488, 7/7 critical done, sim 29.6 s, wall 33 s, 50012 hops, 1881 MAC give-ups, 0/242 gateway pairs with q < 0.5
  run 1 river-full: D 5808, 8/8 critical done, sim 30.5 s, wall 32 s, 46329 hops, 1569 MAC give-ups, 0/256 gateway pairs with q < 0.5
  run 1 river-full: D 5223, 7/7 critical done, sim 32.3 s, wall 41 s, 68365 hops, 2588 MAC give-ups, 0/234 gateway pairs with q < 0.5
```
