# try-P-k2-s4

- Bắt đầu: 2026-10-25 02:37:31, chạy 66 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 2 --seed 4 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --schemes rf,d --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/P/k2-s4
```

**Kết quả**

```text
map: 152 land cells, 3224 nodes, 2 clusters [80, 72], BS -43,-2650
bearings: C1 82 deg (2130 m inside), C2 138 deg (1970 m inside)
chord-t: C1 104 deg, C2 128 deg
tour: 9.1 km, 182 s, order [(2, 0), (1, 1)]
C1: cap 42.4 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 51.1 s
C2: cap 44.7 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 64.0 s
  run 200401 river-full: D 4721, 7/7 critical done, sim 28.8 s, wall 16 s, 33168 hops, 710 MAC give-ups, 0/178 gateway pairs with q < 0.5
  run 200401 direct: D 4721, 7/7 critical done, sim 29.3 s, wall 17 s, 39059 hops, 886 MAC give-ups, 0/178 gateway pairs with q < 0.5
  run 200402 river-full: D 6012, 6/6 critical done, sim 10.5 s, wall 4 s, 11642 hops, 360 MAC give-ups, 0/91 gateway pairs with q < 0.5
  run 200402 direct: D 6012, 6/6 critical done, sim 12.3 s, wall 5 s, 14449 hops, 467 MAC give-ups, 0/91 gateway pairs with q < 0.5
```
