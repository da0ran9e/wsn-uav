---
status: history
updated: 2026-11-16
---
# ground-lb

- Bắt đầu: 2026-11-16 05:27:16, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/draft-v1/analysis/ground_lb.py logs/2026-10-30_1545-deluge-r100/results /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/C4/CP/r100/R1/k8-s1/tour.json paper/j1/draft-v1/figs/ground-lb
```

**Kết quả**

```text
| Scheme | completions | median doneS / bound | 90th pct | cells at the bound within 1.5x | last completion from take-off (s), per seed |
|---|---|---|---|---|---|
| River | 225 | 5.07 | 9.06 | 0 % | 770, 760, 746, 729, 727 (mean 746) |
| Direct pull (planned) | 90 | 4.96 | 9.35 | 0 % | 827, 794 (mean 810) |
| Deluge (River cells) | 225 | 7.58 | 9.19 | 0 % | 749, 744, 730, 754, 737 (mean 743) |
| Deluge (path cells) | 225 | 7.33 | 8.84 | 0 % | 746, 748, 724, 738, 733 (mean 738) |

River fit: doneS = -2.48 ms x lackCell + 2.47 ms x (lack of the other critical cells of the cluster) + 65.1 s; R2 = 0.18, n = 225.
Mean lackCell 3744 packets; mean doneS 102.8 s; mean bound 18.0 s; critical cells per cluster 6.1 (weighted by cell).
Tour leave times (s): 7: 76, 3: 170, 5: 257, 8: 331, 1: 394, 6: 449, 4: 512, 2: 582.
```
