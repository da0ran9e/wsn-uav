# ml-K6-spine8.66-width0.61-bend120-bssouth-span14-q400-s4

- Bắt đầu: 2026-10-23 19:21:24, chạy 6 s, mã thoát 1
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 6 --seed 4 --shape spine=8.66,bend=120,width=0.61 --bs south --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K6-spine8.66-width0.61-bend120-bssouth-span14-q400-s4/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --geometry
```

**Kết quả**

```text
map: 649 land cells, 9 clusters [76, 76, 76, 77, 68, 69, 69, 69, 69], 2 lanes, route 21.8 km, with BS 25.1 km
Traceback (most recent call last):
  File "/home/user/wsn-uav/uav-l2/tools/meander_lane.py", line 345, in <module>
    main()
    ~~~~^^
  File "/home/user/wsn-uav/uav-l2/tools/meander_lane.py", line 333, in main
    stage_deploy(a, W_, K)
    ~~~~~~~~~~~~^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/swath_mission.py", line 87, in stage_deploy
    margin, pick = next((m, p) for m in (300, 200, 100, 0) for p in range(10)
                   ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                        if sh(base + [f"--chMargin={m}", f"--pick={p}"], f"c{k}-deploy.log", env, ok=True))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
StopIteration
```
