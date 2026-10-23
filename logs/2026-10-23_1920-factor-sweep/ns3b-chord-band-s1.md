# ns3b-chord-band-s1

- Bắt đầu: 2026-10-23 20:04:31, chạy 556 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --shape spine=10,bend=60,width=0.7 --bs end --count 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/chord/band-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8
```

**Kết quả**

```text
map: 703 land cells, 14910 nodes, 8 clusters [88, 88, 88, 88, 88, 88, 87, 88], BS -3395,-5581
bearings: C1 68 deg (2270 m inside), C2 58 deg (2075 m inside), C3 34 deg (2265 m inside), C4 46 deg (3400 m inside), C5 58 deg (1905 m inside), C6 160 deg (2020 m inside), C7 10 deg (2105 m inside), C8 14 deg (2135 m inside)
chord-t: C1 54 deg, C2 58 deg, C3 58 deg, C4 56 deg, C5 148 deg, C6 24 deg, C7 0 deg, C8 0 deg
tour: 32.3 km, 646 s, order [(3, 0), (1, 0), (7, 0), (6, 0), (2, 0), (8, 1), (4, 1), (5, 1)]
  run 1 river-full: D 4073, 6/6 critical done, sim 23.4 s, wall 31 s, 51850 hops, 1625 MAC give-ups, 0/182 gateway pairs with q < 0.5
  run 1 river-full: D 4640, 8/8 critical done, sim 23.5 s, wall 35 s, 59706 hops, 1764 MAC give-ups, 0/215 gateway pairs with q < 0.5
  run 1 river-full: D 4159, 5/5 critical done, sim 24.4 s, wall 23 s, 38578 hops, 1437 MAC give-ups, 0/208 gateway pairs with q < 0.5
  run 1 river-full: D 4139, 5/5 critical done, sim 18.4 s, wall 14 s, 25081 hops, 805 MAC give-ups, 0/157 gateway pairs with q < 0.5
  run 1 river-full: D 3854, 5/5 critical done, sim 10.9 s, wall 7 s, 10133 hops, 337 MAC give-ups, 0/191 gateway pairs with q < 0.5
  run 1 river-full: D 4503, 6/6 critical done, sim 21.6 s, wall 25 s, 39833 hops, 1664 MAC give-ups, 0/174 gateway pairs with q < 0.5
  run 1 river-full: D 4484, 6/6 critical done, sim 50.0 s, wall 82 s, 128832 hops, 4572 MAC give-ups, 0/212 gateway pairs with q < 0.5
  run 1 river-full: D 6258, 9/9 critical done, sim 165.2 s, wall 314 s, 536580 hops, 23878 MAC give-ups, 0/178 gateway pairs with q < 0.5
```
