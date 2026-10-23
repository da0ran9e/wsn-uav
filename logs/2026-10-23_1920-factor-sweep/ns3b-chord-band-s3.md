# ns3b-chord-band-s3

- Bắt đầu: 2026-10-23 20:22:38, chạy 426 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 3 --shape spine=10,bend=60,width=0.7 --bs end --count 7 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/chord/band-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8
```

**Kết quả**

```text
map: 719 land cells, 15249 nodes, 7 clusters [103, 102, 103, 103, 103, 103, 102], BS -1923,-6331
bearings: C1 66 deg (2000 m inside), C2 0 deg (2075 m inside), C3 136 deg (2230 m inside), C4 10 deg (2220 m inside), C5 112 deg (2445 m inside), C6 146 deg (2145 m inside), C7 114 deg (2165 m inside)
chord-t: C1 6 deg, C2 106 deg, C3 52 deg, C4 10 deg, C5 168 deg, C6 146 deg, C7 50 deg
tour: 33.8 km, 676 s, order [(7, 0), (3, 1), (5, 1), (1, 1), (6, 1), (4, 1), (2, 1)]
  run 1 river-full: D 4087, 4/4 critical done, sim 10.0 s, wall 7 s, 10104 hops, 278 MAC give-ups, 0/217 gateway pairs with q < 0.5
  run 1 river-full: D 4244, 8/8 critical done, sim 35.3 s, wall 71 s, 93155 hops, 3201 MAC give-ups, 0/259 gateway pairs with q < 0.5
  run 1 river-full: D 5100, 8/8 critical done, sim 28.1 s, wall 30 s, 47144 hops, 1682 MAC give-ups, 0/205 gateway pairs with q < 0.5
  run 1 river-full: D 4501, 10/10 critical done, sim 50.2 s, wall 154 s, 187745 hops, 6279 MAC give-ups, 0/235 gateway pairs with q < 0.5
  run 1 river-full: D 5046, 8/8 critical done, sim 26.7 s, wall 29 s, 44134 hops, 1935 MAC give-ups, 0/200 gateway pairs with q < 0.5
  run 1 river-full: D 4206, 4/4 critical done, sim 18.2 s, wall 14 s, 25440 hops, 801 MAC give-ups, 0/218 gateway pairs with q < 0.5
  run 1 river-full: D 5001, 9/9 critical done, sim 45.0 s, wall 117 s, 166326 hops, 6260 MAC give-ups, 0/240 gateway pairs with q < 0.5
```
