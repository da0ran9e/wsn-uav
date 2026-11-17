---
status: history
updated: 2026-11-17
---
# lb-compare-seed1

- Bắt đầu: 2026-11-17 10:37:49, chạy 6 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/draft-v1/analysis/lb_compare.py logs/2026-10-30_1545-deluge-r100/results $S/LB $S/C4/CP/r100/R1/k8-s1/tour.json paper/j1/draft-v1/figs/lb-seed1
```

**Kết quả**

```text
| Variant | missions | critical cells complete | doneS mean (s): River → variant | per cell, geometric mean of the ratio | cells faster | last cell of the cluster (s): River → variant | median doneS / single-radio bound | frames | MAC give-ups | radio-on time |
|---|---|---|---|---|---|---|---|---|---|---|
| River + shared trees | 8 | 45/45 | 101.2 → 84.9 (-16 %) | 0.87 | 69 % | 125.7 → 98.1 (-22 %) | 4.65 | -23 % | -16 % | -21 % |
| River-LB (balanced paths) | 8 | 45/45 | 101.2 → 83.2 (-18 %) | 0.82 | 87 % | 125.7 → 95.7 (-24 %) | 4.23 | -0 % | +3 % | -22 % |
| River-LB + shared trees | 8 | 45/45 | 101.2 → 74.9 (-26 %) | 0.77 | 93 % | 125.7 → 86.3 (-31 %) | 4.06 | -24 % | -12 % | -29 % |

Last completion of the mission from take-off (s), River → variant, per seed with all clusters run:
- River + shared trees: seed 1: 770 → 693; mean 770 → 693
- River-LB (balanced paths): seed 1: 770 → 707; mean 770 → 707
- River-LB + shared trees: seed 1: 770 → 703; mean 770 → 703

Last critical cell per cluster (s), seed: cluster River → variant:
- River + shared trees: 1:1 90 → 93; 1:2 188 → 111; 1:3 111 → 104; 1:4 86 → 84; 1:5 90 → 90; 1:6 71 → 71; 1:7 121 → 108; 1:8 248 → 123
- River-LB (balanced paths): 1:1 90 → 87; 1:2 188 → 125; 1:3 111 → 100; 1:4 86 → 74; 1:5 90 → 82; 1:6 71 → 60; 1:7 121 → 89; 1:8 248 → 149
- River-LB + shared trees: 1:1 90 → 84; 1:2 188 → 121; 1:3 111 → 97; 1:4 86 → 76; 1:5 90 → 88; 1:6 71 → 65; 1:7 121 → 79; 1:8 248 → 80
```
