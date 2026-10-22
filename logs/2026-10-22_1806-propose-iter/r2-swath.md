# Vòng 2: SWATH-K đầy đủ (lượt bay + River), k8-s10

- Bắt đầu: 2026-10-22 18:30:51, chạy 619 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/swath_mission.py --clusters 8 --seed 10 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/IT/SW-k8-s10 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --jobs 2
```

**Kết quả**

```text
map: 632 land cells, 13404 nodes, 8 clusters [80, 80, 80, 76, 80, 80, 77, 79], route 31.0 km over 6 lanes at 45 deg, BS 303,-3700
curves: C1 4.14 km, CH 26 m off, k*rho 0.17, C2 4.34 km, CH 65 m off, k*rho 0.33, C3 2.45 km, CH 35 m off, k*rho 0.17, C4 3.88 km, CH 110 m off, k*rho 0.33, C5 2.06 km, CH 104 m off, k*rho 0.17, C6 4.64 km, CH 5 m off, k*rho 0.33, C7 4.27 km, CH 19 m off, k*rho 0.33, C8 5.27 km, CH 63 m off, k*rho 0.33
tour: 44.7 km, 893 s, order [(4, 0), (5, 0), (6, 0), (7, 0), (8, 1), (3, 1), (2, 1), (1, 1)]
  run 1 river-full: D 4708, 7/7 critical done, sim 77.2 s, wall 122 s, 205409 hops, 8984 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1 river-full: D 4105, 5/5 critical done, sim 56.3 s, wall 134 s, 237040 hops, 7382 MAC give-ups, 0/139 gateway pairs with q < 0.5
  run 1 river-full: D 3177, 5/5 critical done, sim 15.3 s, wall 10 s, 18256 hops, 527 MAC give-ups, 0/176 gateway pairs with q < 0.5
  run 1 river-full: D 4344, 4/4 critical done, sim 8.8 s, wall 7 s, 10163 hops, 296 MAC give-ups, 0/184 gateway pairs with q < 0.5
  run 1 river-full: D 4918, 6/6 critical done, sim 17.0 s, wall 30 s, 40249 hops, 1422 MAC give-ups, 0/175 gateway pairs with q < 0.5
  run 1 river-full: D 3179, 5/5 critical done, sim 20.5 s, wall 37 s, 56372 hops, 1830 MAC give-ups, 0/168 gateway pairs with q < 0.5
  run 1 river-full: D 5415, 4/4 critical done, sim 29.8 s, wall 10 s, 18443 hops, 915 MAC give-ups, 0/168 gateway pairs with q < 0.5
  run 1 river-full: D 4281, 7/7 critical done, sim 101.6 s, wall 125 s, 225771 hops, 10758 MAC give-ups, 0/153 gateway pairs with q < 0.5
```
