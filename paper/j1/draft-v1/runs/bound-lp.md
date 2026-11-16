---
status: history
updated: 2026-11-16
---
# bound-lp

- Bắt đầu: 2026-11-16 06:29:29, chạy 178 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/draft-v1/analysis/bound_lp.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/C4/CP paper/j1/draft-v1/figs/bound-nc.csv paper/j1/draft-v1/figs/bound-lp --nofly
```

**Kết quả**

```text
{'map': 'k8-s1', 'env': 'open', 'R50': 1016, 'clusters': 8, 'ncrit': 45, 'Lambda': 4.0, 'fine_max': 1.002, 'LB_cover': 146, 'LB_pack': 123, 'FC': 669, 'CHORD_fly': 784, 'LM_fly': 698, 'CHORD_ready': 360, 'LM_ready': 302}
{'map': 'k8-s1', 'env': 'r500', 'R50': 498, 'clusters': 8, 'ncrit': 45, 'Lambda': 9.96, 'fine_max': 1.018, 'LB_cover': 362, 'LB_pack': 256, 'FC': 1320, 'CHORD_fly': 784, 'LM_fly': 699, 'CHORD_ready': 402, 'LM_ready': 337}
{'map': 'k8-s1', 'env': 'r200', 'R50': 199, 'clusters': 8, 'ncrit': 45, 'Lambda': 23.16, 'fine_max': 1.084, 'LB_cover': 842, 'LB_pack': 610, 'FC': 2687, 'CHORD_fly': 784, 'LM_fly': 697, 'CHORD_ready': 436, 'LM_ready': 375}
{'map': 'k8-s1', 'env': 'r100', 'R50': 99, 'clusters': 8, 'ncrit': 45, 'Lambda': 35.27, 'fine_max': 1.056, 'LB_cover': 1283, 'LB_pack': 880, 'FC': 3305, 'CHORD_fly': 784, 'LM_fly': 708, 'CHORD_ready': 452, 'LM_ready': 389}
{'map': 'k12-s1', 'env': 'open', 'R50': 1016, 'clusters': 12, 'ncrit': 66, 'Lambda': 5.54, 'fine_max': 1.002, 'LB_cover': 201, 'LB_pack': 157, 'FC': 913, 'CHORD_fly': 1292, 'LM_fly': 1085, 'CHORD_ready': 566, 'LM_ready': 473}
{'map': 'k12-s1', 'env': 'r500', 'R50': 498, 'clusters': 12, 'ncrit': 66, 'Lambda': 14.06, 'fine_max': 1.016, 'LB_cover': 511, 'LB_pack': 339, 'FC': 2011, 'CHORD_fly': 1292, 'LM_fly': 1085, 'CHORD_ready': 603, 'LM_ready': 504}
{'map': 'k12-s1', 'env': 'r200', 'R50': 199, 'clusters': 12, 'ncrit': 66, 'Lambda': 33.54, 'fine_max': 1.05, 'LB_cover': 1220, 'LB_pack': 865, 'FC': 4016, 'CHORD_fly': 1292, 'LM_fly': 1083, 'CHORD_ready': 638, 'LM_ready': 543}
{'map': 'k12-s1', 'env': 'r100', 'R50': 99, 'clusters': 12, 'ncrit': 66, 'Lambda': 53.64, 'fine_max': 1.08, 'LB_cover': 1951, 'LB_pack': 1375, 'FC': 5078, 'CHORD_fly': 1292, 'LM_fly': 1082, 'CHORD_ready': 655, 'LM_ready': 552}
{'map': 'k16-s1', 'env': 'open', 'R50': 1016, 'clusters': 15, 'ncrit': 92, 'Lambda': 6.99, 'fine_max': 1.001, 'LB_cover': 254, 'LB_pack': 163, 'FC': 1134, 'CHORD_fly': 1437, 'LM_fly': 1394, 'CHORD_ready': 701, 'LM_ready': 612}
{'map': 'k16-s1', 'env': 'r500', 'R50': 498, 'clusters': 15, 'ncrit': 92, 'Lambda': 18.02, 'fine_max': 1.013, 'LB_cover': 655, 'LB_pack': 400, 'FC': 2563, 'CHORD_fly': 1437, 'LM_fly': 1308, 'CHORD_ready': 747, 'LM_ready': 657}
{'map': 'k16-s1', 'env': 'r200', 'R50': 199, 'clusters': 15, 'ncrit': 92, 'Lambda': 47.1, 'fine_max': 1.067, 'LB_cover': 1713, 'LB_pack': 1051, 'FC': 5567, 'CHORD_fly': 1437, 'LM_fly': 1293, 'CHORD_ready': 778, 'LM_ready': 694}
{'map': 'k16-s1', 'env': 'r100', 'R50': 99, 'clusters': 15, 'ncrit': 92, 'Lambda': 76.41, 'fine_max': 1.051, 'LB_cover': 2779, 'LB_pack': 1731, 'FC': 6808, 'CHORD_fly': 1437, 'LM_fly': 1291, 'CHORD_ready': 796, 'LM_ready': 704}
| open | 0 | 0 | 4.00 | 146 |
| open | 400 | 2 | 4.00 | 146 |
| open | 700 | 4 | 3.98 | 145 |
| r500 | 0 | 0 | 9.96 | 362 |
| r500 | 400 | 2 | 9.96 | 362 |
| r500 | 700 | 4 | 9.98 | 363 |
| r200 | 0 | 0 | 23.16 | 842 |
| r200 | 400 | 2 | 23.16 | 842 |
| r200 | 700 | 4 | 94.34 | 3431 |
| r100 | 0 | 0 | 35.27 | 1283 |
| r100 | 400 | 2 | 35.28 | 1283 |
| r100 | 700 | 4 | inf | inf |
| Map | Env | clusters | critical cells | Lambda* | LB covering (s) | LB packing (s) | FC+DTSP-N measured (s) | CHORD flight (s) | LM-Tour flight (s) |
|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 8 | 45 | 4.0 | 146 | 123 | 669 | 784 | 698 |
| k8-s1 | r500 | 8 | 45 | 9.96 | 362 | 256 | 1320 | 784 | 699 |
| k8-s1 | r200 | 8 | 45 | 23.16 | 842 | 610 | 2687 | 784 | 697 |
| k8-s1 | r100 | 8 | 45 | 35.27 | 1283 | 880 | 3305 | 784 | 708 |
| k12-s1 | open | 12 | 66 | 5.54 | 201 | 157 | 913 | 1292 | 1085 |
| k12-s1 | r500 | 12 | 66 | 14.06 | 511 | 339 | 2011 | 1292 | 1085 |
| k12-s1 | r200 | 12 | 66 | 33.54 | 1220 | 865 | 4016 | 1292 | 1083 |
| k12-s1 | r100 | 12 | 66 | 53.64 | 1951 | 1375 | 5078 | 1292 | 1082 |
| k16-s1 | open | 15 | 92 | 6.99 | 254 | 163 | 1134 | 1437 | 1394 |
| k16-s1 | r500 | 15 | 92 | 18.02 | 655 | 400 | 2563 | 1437 | 1308 |
| k16-s1 | r200 | 15 | 92 | 47.1 | 1713 | 1051 | 5567 | 1437 | 1293 |
| k16-s1 | r100 | 15 | 92 | 76.41 | 2779 | 1731 | 6808 | 1437 | 1291 |
```
