# ns3b-chord-band-s2

- Bắt đầu: 2026-10-23 20:13:47, chạy 474 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 2 --shape spine=10,bend=60,width=0.7 --bs end --count 6 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/NS2/chord/band-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --schemes rf --jobs 2 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8
```

**Kết quả**

```text
map: 655 land cells, 13892 nodes, 6 clusters [110, 108, 110, 110, 110, 107], BS 5387,-3931
bearings: C1 26 deg (2245 m inside), C2 120 deg (2240 m inside), C3 76 deg (2150 m inside), C4 122 deg (2100 m inside), C5 20 deg (2425 m inside), C6 20 deg (2295 m inside)
chord-t: C1 80 deg, C2 120 deg, C3 104 deg, C4 28 deg, C5 60 deg, C6 116 deg
tour: 28.6 km, 572 s, order [(2, 0), (5, 1), (3, 0), (4, 1), (6, 0), (1, 1)]
  run 1 river-full: D 5184, 5/5 critical done, sim 13.3 s, wall 13 s, 17332 hops, 417 MAC give-ups, 0/246 gateway pairs with q < 0.5
  run 1 river-full: D 4334, 7/7 critical done, sim 19.6 s, wall 33 s, 42801 hops, 1318 MAC give-ups, 0/247 gateway pairs with q < 0.5
  run 1 river-full: D 4231, 9/9 critical done, sim 82.2 s, wall 133 s, 195450 hops, 6354 MAC give-ups, 0/228 gateway pairs with q < 0.5
  run 1 river-full: D 4467, 10/10 critical done, sim 34.0 s, wall 76 s, 91616 hops, 3242 MAC give-ups, 0/272 gateway pairs with q < 0.5
  run 1 river-full: D 4250, 8/8 critical done, sim 83.2 s, wall 272 s, 354762 hops, 11454 MAC give-ups, 0/231 gateway pairs with q < 0.5
  run 1 river-full: D 5349, 7/7 critical done, sim 20.0 s, wall 35 s, 43136 hops, 1317 MAC give-ups, 0/253 gateway pairs with q < 0.5
```
