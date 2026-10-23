# ml-K8-spine7-width1-bend120-bssouth-span14-q400-s4

- Bắt đầu: 2026-10-23 19:32:07, chạy 6 s, mã thoát 1
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/meander_lane.py --clusters 8 --seed 4 --shape spine=7,bend=120,width=1 --bs south --span 14 --lane 8 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SW/K8-spine7-width1-bend120-bssouth-span14-q400-s4/ml --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --geometry
```

**Kết quả**

```text
map: 676 land cells, 9 clusters [53, 54, 72, 73, 73, 73, 93, 92, 93], 3 lanes, route 19.5 km, with BS 26.5 km
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
