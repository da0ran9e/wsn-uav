# try-K-k2-s4

- Bắt đầu: 2026-10-25 02:38:47, chạy 52 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 2 --seed 4 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --kinPass --mapRuns --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CTRY/K/k2-s4
```

**Kết quả**

```text
map: 152 land cells, 3224 nodes, 2 clusters [80, 72], BS -43,-2650
bearings: C1 82 deg (2130 m inside), C2 138 deg (1970 m inside)
tour: 9.4 km, 189 s, order [(1, 0), (2, 1)]
C1: cap 50.0 m/s, 0 loops, 4272 packets over its cells (need 4041), pass 52.9 s
C2: cap 49.0 m/s, 0 loops, 4041 packets over its cells (need 4041), pass 57.1 s
  run 200402 river-full: D 5490, 6/6 critical done, sim 13.7 s, wall 9 s, 19476 hops, 729 MAC give-ups, 0/101 gateway pairs with q < 0.5
  run 200401 river-full: D 4835, 7/7 critical done, sim 20.9 s, wall 14 s, 27210 hops, 823 MAC give-ups, 0/183 gateway pairs with q < 0.5
```
