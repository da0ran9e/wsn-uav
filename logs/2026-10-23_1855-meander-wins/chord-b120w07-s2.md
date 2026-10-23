# chord-b120w07-s2

- Bắt đầu: 2026-10-23 18:59:52, chạy 1 s, mã thoát 1
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/mission.py --clusters 8 --seed 2 --shape spine=10,bend=120,width=0.7 --count 14 --work /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/SCR/b120w07-s2/chord --bin /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/BIN --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --geometry
```

**Kết quả**

```text
Traceback (most recent call last):
  File "/home/user/wsn-uav/uav-l2/tools/mission.py", line 365, in <module>
    main()
    ~~~~^^
  File "/home/user/wsn-uav/uav-l2/tools/mission.py", line 350, in main
    stage_map(a, W_)
    ~~~~~~~~~^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/mission.py", line 74, in stage_map
    owner, med, it, over = partition(land, math.ceil(len(land) / count) if count else 80, random.Random(a.seed))
                           ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/partition.py", line 112, in partition
    far = max(cells, key=lambda h: (min(dist[m][h] for m in med), h))
  File "/home/user/wsn-uav/uav-l2/tools/partition.py", line 112, in <lambda>
    far = max(cells, key=lambda h: (min(dist[m][h] for m in med), h))
                                    ~~~^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/partition.py", line 112, in <genexpr>
    far = max(cells, key=lambda h: (min(dist[m][h] for m in med), h))
                                        ~~~~~~~^^^
KeyError: (-7, 0)
```
