# b8-compare-seed1

- Bắt đầu: 2026-11-21 03:14:07, chạy 36 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/b4_compare.py logs/2026-11-18_1036-k9/data/b8-ns3-seed1 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r100/npu08 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r100/npu05 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r200/npu08 /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/B8/r200/npu05
```

**Kết quả**

```text
# K9 B4: River in ns-3 against the surrogate, on the chosen critical-cell sets (k8, seed 1)

Error = predicted minus measured, seconds, over the cells complete by the limit. T_k: last critical cell of the cluster (from leaving it). T1: last critical cell of the mission, from take-off. A cell not complete by the limit counts as 900 s, so its T_k and T1 are lower bounds (>=).

| channel | set | critical cells | not complete | cell MAE | cell bias | T_k MAE | T_k bias | T1 ns-3 | T1 model |
|---|---|---|---|---|---|---|---|---|---|
| r100 | npu08 | 39 | 0 | 20.4 | -11.1 | 20.6 | -17.2 | 689 | 674 |
| r100 | npu05 | 74 | 0 | 51.5 | +0.3 | 57.8 | -25.5 | 733 | 728 |
| r200 | npu08 | 39 | 0 | 20.1 | -6.9 | 23.3 | -16.5 | 658 | 665 |
| r200 | npu05 | 75 | 0 | 60.0 | -4.0 | 68.2 | -37.8 | 712 | 714 |

T_k per cluster, model / ns-3 (seconds; >= not complete by the limit)

| channel | set | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|---|
| r100 | npu08 | 84 / 75 | 93 / 108 | 74 / 85 | 87 / 89 | 80 / 76 | 82 / 89 | 81 / 121 | 80 / 156 |
| r100 | npu05 | 157 / 98 | 147 / 152 | 149 / 163 | 161 / 154 | 159 / 105 | 151 / 141 | 151 / 246 | 165 / 385 |
| r200 | npu08 | 74 / 61 | 84 / 76 | 67 / 80 | 78 / 77 | 67 / 60 | 69 / 75 | 66 / 153 | 66 / 121 |
| r200 | npu05 | 136 / 101 | 133 / 130 | 136 / 129 | 141 / 139 | 140 / 119 | 130 / 76 | 125 / 425 | 144 / 268 |
```
