# geo-chordB-s1

- Bắt đầu: 2026-10-24 07:14:56, chạy 17 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T156geo/chordB-s1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry
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
```
