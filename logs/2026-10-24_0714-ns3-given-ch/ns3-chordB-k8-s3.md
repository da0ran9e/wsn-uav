# ns3-chordB-k8-s3

- Bắt đầu: 2026-10-24 09:10:20, chạy 653 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 3 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS157/chordB/k8-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --banks local --kinPass --schemes rf --jobs 2
```

**Kết quả**

```text
map: 656 land cells, 13913 nodes, 5 clusters [132, 132, 132, 132, 128], BS 43,-3850
bearings: C1 100 deg (2470 m inside), C2 144 deg (2725 m inside), C3 74 deg (2320 m inside), C4 170 deg (2480 m inside), C5 140 deg (2895 m inside)
chord-t: C1 162 deg, C2 0 deg, C3 146 deg, C4 10 deg, C5 162 deg
C1: bent towards 3 critical cells, shift <= 173 m
C2: bent towards 5 critical cells, shift <= 310 m
C3: bent towards 2 critical cells, shift <= 173 m
C4: bent towards 4 critical cells, shift <= 173 m
C5: bent towards 9 critical cells, shift <= 354 m
tour: 25.0 km, 500 s, order [(4, 0), (1, 0), (5, 0), (3, 1), (2, 0)]
C1: cap 50.0 m/s, 0 loops, 4092 packets over its cells (need 4041), pass 51.3 s
C2: cap 50.0 m/s, 0 loops, 4315 packets over its cells (need 4041), pass 50.5 s
C3: cap 38.3 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 57.8 s
C4: cap 45.5 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 54.1 s
C5: cap 50.0 m/s, 0 loops, 4783 packets over its cells (need 4041), pass 53.3 s
  run 1 river-full: D 4976, 8/8 critical done, sim 35.1 s, wall 82 s, 98896 hops, 4104 MAC give-ups, 0/313 gateway pairs with q < 0.5
  run 1 river-full: D 4744, 7/7 critical done, sim 48.8 s, wall 181 s, 215385 hops, 9110 MAC give-ups, 0/319 gateway pairs with q < 0.5
  run 1 river-full: D 5153, 8/8 critical done, sim 54.5 s, wall 210 s, 262480 hops, 10020 MAC give-ups, 0/283 gateway pairs with q < 0.5
  run 1 river-full: D 5545, 9/9 critical done, sim 98.6 s, wall 318 s, 405149 hops, 14629 MAC give-ups, 0/310 gateway pairs with q < 0.5
  run 1 river-full: D 5089, 12/12 critical done, sim 26.1 s, wall 76 s, 101776 hops, 3138 MAC give-ups, 0/276 gateway pairs with q < 0.5
```
