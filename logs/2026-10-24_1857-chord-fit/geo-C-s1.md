# geo-C-s1

- Bắt đầu: 2026-10-24 18:57:37, chạy 24 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry --chordFit 1.3 --bendCrit 5 --bendShort --banks local --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T159geo/C-s1
```

**Kết quả**

```text
map: 617 land cells, 13086 nodes, 8 clusters [78, 72, 70, 78, 80, 80, 79, 80], BS 173,-3550
bearings: C1 60 deg (1865 m inside), C2 20 deg (1955 m inside), C3 126 deg (2000 m inside), C4 160 deg (2115 m inside), C5 172 deg (2040 m inside), C6 170 deg (1750 m inside), C7 138 deg (2090 m inside), C8 136 deg (2025 m inside)
chord-t: C1 72 deg, C2 116 deg, C3 22 deg, C4 160 deg, C5 2 deg, C6 150 deg, C7 172 deg, C8 136 deg
C1: bent towards 3 critical cells, shift <= 198 m
C2: bent towards 5 critical cells, shift <= 51 m
C3: bent towards 6 critical cells, shift <= 116 m
C5: bent towards 3 critical cells, shift <= 43 m
C6: bent towards 4 critical cells, shift <= 135 m
C7: bent towards 4 critical cells, shift <= 136 m
tour: 29.5 km, 590 s, order [(7, 0), (3, 0), (5, 0), (8, 0), (1, 1), (6, 1), (4, 0), (2, 1)]
```
