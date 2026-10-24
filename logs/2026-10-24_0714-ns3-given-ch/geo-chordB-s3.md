# geo-chordB-s3

- Bắt đầu: 2026-10-24 07:14:56, chạy 21 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 3 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T156geo/chordB-s3 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry
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
```
