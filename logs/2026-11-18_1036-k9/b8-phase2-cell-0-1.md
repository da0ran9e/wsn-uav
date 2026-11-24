# b8-phase2-cell-0-1

- Bắt đầu: 2026-11-21 03:14:51, chạy 16 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/b5_phase2.py logs/2026-11-18_1036-k9/data/b8-phase2-cell-0-1 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r100/npu08 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r100/npu05 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r200/npu08 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r200/npu05 --draws 300 --rho 20 --fa cell:0.1
```

**Kết quả**

```text
r100 npu08: 39 AI cells, rho_max 54, T1 689
r100 npu05: 74 AI cells, rho_max 105, T1 733
r200 npu08: 39 AI cells, rho_max 54, T1 658
r200 npu05: 75 AI cells, rho_max 105, T1 712
# K9 B5: both phases on the B4 sets, option D3 (k8, River seed 1), false alarms cell:0.1

300 paired draws per row. T: time from take-off to V1 confirming the true AI cell, over the missions where it answers YES (success). yes: AI cells answering YES. index: vectors at the busiest AI cell. feasible: rho <= rho_max of the set (10 % budget). hops: true node to its AI cell (cells). alpha: probability that an AI cell holding strangers only answers YES.

| channel | set | AI cells | alpha | T1 | rho_max | hops mean / max | rho | feasible | index | k | success | yes | visits | T mean | T p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r100 | npu08 | 39 | 0.1 | 689 | 54 | 2.1 / 5 | 20 | yes | 5112 | 1 | 0.640 | 4.4 | 2.16 | 879 | 1203 |
| r100 | npu08 | 39 | 0.1 | 689 | 54 | 2.1 / 5 | 20 | yes | 5112 | 3 | 0.943 | 4.7 | 2.01 | 855 | 1139 |
| r100 | npu05 | 74 | 0.1 | 733 | 105 | 1.5 / 5 | 20 | yes | 2628 | 1 | 0.690 | 7.7 | 2.80 | 1008 | 1425 |
| r100 | npu05 | 74 | 0.1 | 733 | 105 | 1.5 / 5 | 20 | yes | 2628 | 3 | 0.973 | 7.9 | 2.39 | 936 | 1198 |
| r200 | npu08 | 39 | 0.1 | 658 | 54 | 2.2 / 5 | 20 | yes | 5112 | 1 | 0.623 | 4.4 | 2.13 | 862 | 1166 |
| r200 | npu08 | 39 | 0.1 | 658 | 54 | 2.2 / 5 | 20 | yes | 5112 | 3 | 0.933 | 4.7 | 2.04 | 848 | 1127 |
| r200 | npu05 | 75 | 0.1 | 712 | 105 | 1.6 / 5 | 20 | yes | 2640 | 1 | 0.693 | 7.8 | 2.69 | 1002 | 1466 |
| r200 | npu05 | 75 | 0.1 | 712 | 105 | 1.6 / 5 | 20 | yes | 2640 | 3 | 0.970 | 8.0 | 2.30 | 937 | 1170 |
```
