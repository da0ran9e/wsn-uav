# fix-open-k16-s1

- Bắt đầu: 2026-10-25 11:16:48, chạy 142 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 16 --seed 1 --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN4 --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env open --riverRepair 20 --schemes rf --jobs 2 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/FIX/open/k16-s1
```

**Kết quả**

```text
bearings: C1 24 deg (1700 m inside), C2 48 deg (2110 m inside), C3 18 deg (1725 m inside), C4 124 deg (1805 m inside), C5 96 deg (1910 m inside), C6 24 deg (1745 m inside), C7 70 deg (1880 m inside), C8 174 deg (1995 m inside), C9 140 deg (2055 m inside), C10 150 deg (1875 m inside), C11 104 deg (1875 m inside), C12 172 deg (1655 m inside), C13 14 deg (1865 m inside), C14 14 deg (1860 m inside), C15 36 deg (1800 m inside)
  run 1600101 river-full: D 4532, 5/5 critical done, sim 14.4 s, wall 7 s, 10571 hops, 398 MAC give-ups, 0/192 gateway pairs with q < 0.5
  run 1600103 river-full: D 4864, 5/5 critical done, sim 20.7 s, wall 8 s, 15912 hops, 610 MAC give-ups, 0/132 gateway pairs with q < 0.5
  run 1600102 river-full: D 5667, 8/8 critical done, sim 21.1 s, wall 19 s, 31077 hops, 976 MAC give-ups, 0/137 gateway pairs with q < 0.5
  run 1600105 river-full: D 4904, 6/6 critical done, sim 18.7 s, wall 14 s, 26900 hops, 1024 MAC give-ups, 0/160 gateway pairs with q < 0.5
  run 1600104 river-full: D 4794, 6/6 critical done, sim 68.7 s, wall 32 s, 65599 hops, 2166 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1600107 river-full: D 6109, 7/7 critical done, sim 7.7 s, wall 8 s, 12196 hops, 432 MAC give-ups, 0/133 gateway pairs with q < 0.5
  run 1600106 river-full: D 4854, 6/6 critical done, sim 55.1 s, wall 36 s, 64317 hops, 2950 MAC give-ups, 0/140 gateway pairs with q < 0.5
  run 1600108 river-full: D 4704, 7/7 critical done, sim 14.0 s, wall 16 s, 22890 hops, 792 MAC give-ups, 0/184 gateway pairs with q < 0.5
  run 1600110 river-full: D 4748, 8/8 critical done, sim 34.2 s, wall 24 s, 47093 hops, 1488 MAC give-ups, 0/143 gateway pairs with q < 0.5
  run 1600111 river-full: D 4632, 5/5 critical done, sim 14.3 s, wall 7 s, 13253 hops, 379 MAC give-ups, 0/161 gateway pairs with q < 0.5
  run 1600112 river-full: D 4584, 4/4 critical done, sim 16.9 s, wall 5 s, 10143 hops, 323 MAC give-ups, 0/136 gateway pairs with q < 0.5
  run 1600109 river-full: D 4362, 6/6 critical done, sim 39.8 s, wall 54 s, 105616 hops, 3788 MAC give-ups, 0/158 gateway pairs with q < 0.5
  run 1600114 river-full: D 4820, 6/6 critical done, sim 14.6 s, wall 4 s, 10309 hops, 378 MAC give-ups, 0/110 gateway pairs with q < 0.5
  run 1600115 river-full: D 4747, 6/6 critical done, sim 7.5 s, wall 4 s, 8739 hops, 229 MAC give-ups, 0/122 gateway pairs with q < 0.5
  run 1600113 river-full: D 4661, 7/7 critical done, sim 41.8 s, wall 33 s, 72136 hops, 2598 MAC give-ups, 0/133 gateway pairs with q < 0.5
```
