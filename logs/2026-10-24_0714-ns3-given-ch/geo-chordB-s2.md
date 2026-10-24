# geo-chordB-s2

- Bắt đầu: 2026-10-24 07:14:56, chạy 19 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 2 --count 5 --chAnywhere --bendCrit 5 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/T156geo/chordB-s2 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry
```

**Kết quả**

```text
map: 596 land cells, 12640 nodes, 5 clusters [120, 116, 120, 120, 120], BS 0,-3850
bearings: C1 112 deg (2270 m inside), C2 96 deg (2260 m inside), C3 104 deg (2090 m inside), C4 42 deg (2425 m inside), C5 150 deg (2395 m inside)
chord-t: C1 176 deg, C2 130 deg, C3 28 deg, C4 66 deg, C5 100 deg
C1: bent towards 5 critical cells, shift <= 185 m
C2: bent towards 3 critical cells, shift <= 172 m
C3: bent towards 6 critical cells, shift <= 111 m
C4: bent towards 5 critical cells, shift <= 66 m
C5: bent towards 3 critical cells, shift <= 233 m
tour: 23.1 km, 462 s, order [(5, 0), (3, 1), (1, 1), (4, 1), (2, 1)]
```
