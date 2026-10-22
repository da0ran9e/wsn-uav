# Tái tạo KW k2-s10 (River cửa sổ 400 kB) để kiểm chứng môi trường

- Bắt đầu: 2026-10-22 17:45:05, chạy 88 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 2 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/KW/k2-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2 --schemes rf --windowKB 400
```

**Kết quả**

```text
map: 155 land cells, 3287 nodes, 2 clusters [80, 75], BS -87,-2500
bearings: C1 120 deg (2320 m inside), C2 168 deg (2065 m inside)
tour: 10.3 km, 206 s, order [(2, 0), (1, 1)]
  run 1 river-full: D 4041, 7/7 critical done, sim 35.3 s, wall 34 s, 62585 hops, 2806 MAC give-ups, 0/156 gateway pairs with q < 0.5
  run 1 river-full: D 4041, 4/4 critical done, sim 22.6 s, wall 37 s, 62711 hops, 1986 MAC give-ups, 0/162 gateway pairs with q < 0.5
```
