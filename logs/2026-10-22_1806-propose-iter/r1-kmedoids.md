# Vòng 1: k-medoids + đường thẳng qua CH (bản trước), cửa sổ theo critical cell, k8-s10

- Bắt đầu: 2026-10-22 18:06:22, chạy 178 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/KC-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 4 --schemes rf --windowKB 400 --windowAt crit
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [77, 80, 80, 80, 80, 79, 80, 76], BS 303,-3700
bearings: C1 74 deg (2260 m inside), C2 68 deg (2260 m inside), C3 56 deg (2135 m inside), C4 142 deg (1840 m inside), C5 86 deg (2105 m inside), C6 46 deg (2205 m inside), C7 50 deg (1930 m inside), C8 48 deg (2245 m inside)
tour: 31.5 km, 631 s, order [(4, 0), (6, 0), (5, 0), (2, 1), (7, 0), (3, 0), (1, 1), (8, 1)]
  run 1 river-full: D 4370, 4/4 critical done, sim 22.8 s, wall 13 s, 20104 hops, 754 MAC give-ups, 0/176 gateway pairs with q < 0.5
  run 1 river-full: D 3687, 6/6 critical done, sim 18.8 s, wall 18 s, 28027 hops, 993 MAC give-ups, 0/191 gateway pairs with q < 0.5
  run 1 river-full: D 4218, 5/5 critical done, sim 10.1 s, wall 7 s, 9790 hops, 232 MAC give-ups, 0/188 gateway pairs with q < 0.5
  run 1 river-full: D 4280, 7/7 critical done, sim 19.0 s, wall 26 s, 43071 hops, 1594 MAC give-ups, 0/148 gateway pairs with q < 0.5
  run 1 river-full: D 4522, 5/5 critical done, sim 29.9 s, wall 32 s, 72353 hops, 2400 MAC give-ups, 0/110 gateway pairs with q < 0.5
  run 1 river-full: D 3870, 6/6 critical done, sim 16.2 s, wall 14 s, 19739 hops, 650 MAC give-ups, 0/204 gateway pairs with q < 0.5
  run 1 river-full: D 4414, 6/6 critical done, sim 20.1 s, wall 21 s, 31214 hops, 958 MAC give-ups, 0/181 gateway pairs with q < 0.5
  run 1 river-full: D 4512, 6/6 critical done, sim 29.2 s, wall 46 s, 91229 hops, 3081 MAC give-ups, 0/148 gateway pairs with q < 0.5
```
