# screen

- Bắt đầu: 2026-10-21 03:27:31, chạy 1 s, mã thoát 1
- Thư mục: `/home/user/wsn-uav/uav-l2`

**Lệnh**

```bash
python3 tools/l2_lanes.py --maps '/tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/KW/k*' --lanes 4.5 6 7.5 9 --frags 0.25 0.5 --out docs/data/l2diag/screen
```

**Kết quả**

```text
Traceback (most recent call last):
  File "/home/user/wsn-uav/uav-l2/tools/l2_lanes.py", line 98, in <module>
    main()
  File "/home/user/wsn-uav/uav-l2/tools/l2_lanes.py", line 68, in main
    M = meander.run(K, seed, 0, L, g=g, frag=fr)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/meander.py", line 246, in run
    owner, lane, s, n, spines, st = partition_meander(R["land"], L, frag=frag)
                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/meander.py", line 119, in partition_meander
    small = [i for i in set(piece.values()) if size(piece, i) < cap * frag
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/user/wsn-uav/uav-l2/tools/meander.py", line 119, in <listcomp>
    small = [i for i in set(piece.values()) if size(piece, i) < cap * frag
                                                                ~~~~^~~~~~
TypeError: unsupported operand type(s) for *: 'int' and 'set'
```
