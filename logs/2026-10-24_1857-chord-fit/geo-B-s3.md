# geo-B-s3

- Bắt đầu: 2026-10-24 18:59:17, chạy 22 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry --chordFit 1.0 --bendCrit 5 --bendShort --banks local --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T159geo/B-s3
```

**Kết quả**

```text
map: 656 land cells, 13913 nodes, 9 clusters [80, 80, 63, 80, 66, 71, 80, 68, 68], BS 43,-3850
bearings: C1 44 deg (2095 m inside), C2 0 deg (1990 m inside), C3 98 deg (2000 m inside), C4 174 deg (1825 m inside), C5 128 deg (2095 m inside), C6 140 deg (2390 m inside), C7 6 deg (1825 m inside), C8 148 deg (1685 m inside), C9 54 deg (2435 m inside)
chord-t: C1 20 deg, C2 72 deg, C3 170 deg, C4 66 deg, C5 50 deg, C6 160 deg, C7 148 deg, C8 148 deg, C9 54 deg
C1: bent towards 4 critical cells, shift <= 135 m
C2: bent towards 5 critical cells, shift <= 264 m
C3: bent towards 3 critical cells, shift <= 129 m
C4: bent towards 5 critical cells, shift <= 151 m
C5: bent towards 8 critical cells, shift <= 278 m
C6: bent towards 3 critical cells, shift <= 156 m
C7: bent towards 2 critical cells, shift <= 173 m
C8: bent towards 3 critical cells, shift <= 173 m
tour: 31.6 km, 632 s, order [(6, 0), (5, 0), (1, 0), (9, 0), (2, 1), (3, 0), (8, 1), (7, 1), (4, 1)]
```
