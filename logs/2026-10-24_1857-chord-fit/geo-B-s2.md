# geo-B-s2

- Bắt đầu: 2026-10-24 18:58:55, chạy 22 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry --chordFit 1.0 --bendCrit 5 --bendShort --banks local --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T159geo/B-s2
```

**Kết quả**

```text
map: 596 land cells, 12640 nodes, 8 clusters [80, 80, 49, 80, 75, 78, 80, 74], BS 0,-3850
bearings: C1 128 deg (2335 m inside), C2 54 deg (2400 m inside), C3 102 deg (1710 m inside), C4 48 deg (1940 m inside), C5 132 deg (2030 m inside), C6 174 deg (2000 m inside), C7 140 deg (2140 m inside), C8 48 deg (2000 m inside)
chord-t: C1 116 deg, C2 80 deg, C3 102 deg, C4 118 deg, C5 122 deg, C6 4 deg, C7 162 deg, C8 76 deg
C1: bent towards 3 critical cells, shift <= 64 m
C3: bent towards 5 critical cells, shift <= 60 m
C4: bent towards 4 critical cells, shift <= 75 m
C5: bent towards 6 critical cells, shift <= 64 m
C6: bent towards 2 critical cells, shift <= 173 m
C7: bent towards 6 critical cells, shift <= 125 m
C8: bent towards 4 critical cells, shift <= 166 m
tour: 29.7 km, 595 s, order [(5, 0), (1, 0), (6, 0), (8, 1), (4, 1), (2, 1), (7, 0), (3, 1)]
```
