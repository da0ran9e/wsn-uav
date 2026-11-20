---
status: history
updated: 2026-11-20
---
# bound-nc-Q400

- Bắt đầu: 2026-11-20 08:45:05, chạy 43 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 $S/bound_q.py 400 $S/C4/CP uav-l2/docs/data/results/campaign4.csv logs/2026-10-27_1714-campaign4/score $S/bound-nc-Q400
```

**Kết quả**

```text
{'map': 'k8-s1', 'env': 'open', 'R50': 1016, 'ncrit': 45, 'pbar_min': 1.0, 'LB': 30, 'D': 1700, 'S': 2, 'FC': 669, 'CHORD_fly': 784, 'LM_fly': 698, 'CHORD_ready': 360, 'LM_ready': 302}
{'map': 'k8-s1', 'env': 'r500', 'R50': 498, 'ncrit': 45, 'pbar_min': 1.0, 'LB': 81, 'D': 1050, 'S': 4, 'FC': 1320, 'CHORD_fly': 784, 'LM_fly': 699, 'CHORD_ready': 402, 'LM_ready': 337}
{'map': 'k8-s1', 'env': 'r200', 'R50': 199, 'ncrit': 45, 'pbar_min': 1.0, 'LB': 146, 'D': 500, 'S': 10, 'FC': 2687, 'CHORD_fly': 784, 'LM_fly': 697, 'CHORD_ready': 436, 'LM_ready': 375}
{'map': 'k8-s1', 'env': 'r100', 'R50': 99, 'ncrit': 45, 'pbar_min': 1.0, 'LB': 201, 'D': 350, 'S': 19, 'FC': 3305, 'CHORD_fly': 784, 'LM_fly': 708, 'CHORD_ready': 452, 'LM_ready': 389}
{'map': 'k12-s1', 'env': 'open', 'R50': 1016, 'ncrit': 66, 'pbar_min': 1.0, 'LB': 66, 'D': 1800, 'S': 3, 'FC': 913, 'CHORD_fly': 1292, 'LM_fly': 1085, 'CHORD_ready': 566, 'LM_ready': 473}
{'map': 'k12-s1', 'env': 'r500', 'R50': 498, 'ncrit': 66, 'pbar_min': 1.0, 'LB': 108, 'D': 1000, 'S': 5, 'FC': 2011, 'CHORD_fly': 1292, 'LM_fly': 1085, 'CHORD_ready': 603, 'LM_ready': 504}
{'map': 'k12-s1', 'env': 'r200', 'R50': 199, 'ncrit': 66, 'pbar_min': 1.0, 'LB': 192, 'D': 500, 'S': 19, 'FC': 4016, 'CHORD_fly': 1292, 'LM_fly': 1083, 'CHORD_ready': 638, 'LM_ready': 543}
{'map': 'k12-s1', 'env': 'r100', 'R50': 99, 'ncrit': 66, 'pbar_min': 1.0, 'LB': 285, 'D': 350, 'S': 29, 'FC': 5078, 'CHORD_fly': 1292, 'LM_fly': 1082, 'CHORD_ready': 655, 'LM_ready': 552}
{'map': 'k16-s1', 'env': 'open', 'R50': 1016, 'ncrit': 92, 'pbar_min': 1.0, 'LB': 67, 'D': 1800, 'S': 3, 'FC': 1134, 'CHORD_fly': 1437, 'LM_fly': 1394, 'CHORD_ready': 701, 'LM_ready': 612}
{'map': 'k16-s1', 'env': 'r500', 'R50': 498, 'ncrit': 92, 'pbar_min': 1.0, 'LB': 132, 'D': 1050, 'S': 7, 'FC': 2563, 'CHORD_fly': 1437, 'LM_fly': 1308, 'CHORD_ready': 747, 'LM_ready': 657}
{'map': 'k16-s1', 'env': 'r200', 'R50': 199, 'ncrit': 92, 'pbar_min': 1.0, 'LB': 231, 'D': 500, 'S': 20, 'FC': 5567, 'CHORD_fly': 1437, 'LM_fly': 1293, 'CHORD_ready': 778, 'LM_ready': 694}
{'map': 'k16-s1', 'env': 'r100', 'R50': 99, 'ncrit': 92, 'pbar_min': 1.0, 'LB': 329, 'D': 350, 'S': 41, 'FC': 6808, 'CHORD_fly': 1437, 'LM_fly': 1291, 'CHORD_ready': 796, 'LM_ready': 704}
| Map | Env | R50 (m) | critical cells | min pbar | LB non-coop (s) | D (m) | \|S\| | FC+DTSP-N measured (s) | CHORD flight / mean ready (s) | LM-Tour flight / mean ready (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 1016 | 45 | 1.0 | 30 | 1700 | 2 | 669 | 784 / 360 | 698 / 302 |
| k8-s1 | r500 | 498 | 45 | 1.0 | 81 | 1050 | 4 | 1320 | 784 / 402 | 699 / 337 |
| k8-s1 | r200 | 199 | 45 | 1.0 | 146 | 500 | 10 | 2687 | 784 / 436 | 697 / 375 |
| k8-s1 | r100 | 99 | 45 | 1.0 | 201 | 350 | 19 | 3305 | 784 / 452 | 708 / 389 |
| k12-s1 | open | 1016 | 66 | 1.0 | 66 | 1800 | 3 | 913 | 1292 / 566 | 1085 / 473 |
| k12-s1 | r500 | 498 | 66 | 1.0 | 108 | 1000 | 5 | 2011 | 1292 / 603 | 1085 / 504 |
| k12-s1 | r200 | 199 | 66 | 1.0 | 192 | 500 | 19 | 4016 | 1292 / 638 | 1083 / 543 |
| k12-s1 | r100 | 99 | 66 | 1.0 | 285 | 350 | 29 | 5078 | 1292 / 655 | 1082 / 552 |
| k16-s1 | open | 1016 | 92 | 1.0 | 67 | 1800 | 3 | 1134 | 1437 / 701 | 1394 / 612 |
| k16-s1 | r500 | 498 | 92 | 1.0 | 132 | 1050 | 7 | 2563 | 1437 / 747 | 1308 / 657 |
| k16-s1 | r200 | 199 | 92 | 1.0 | 231 | 500 | 20 | 5567 | 1437 / 778 | 1293 / 694 |
| k16-s1 | r100 | 99 | 92 | 1.0 | 329 | 350 | 41 | 6808 | 1437 / 796 | 1291 / 704 |
```
