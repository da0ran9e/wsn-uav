# zigzag-open-k16

- Bắt đầu: 2026-10-28 02:36:13, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 logs/2026-10-28_0240-dtspn-check/zigzag_bound.py open 16
```

**Kết quả**

```text
open k16-s1, xi = 255 m: per cluster, critical cells, open TSP over their centres (m), lower bound on a pass entering every disc (m), its time at 50 m/s against the 40.4 s needed anyway
| k | crit | TSP m | bound m | bound s at 50 m/s | in-cluster time s (max of the two) |
|---|---|---|---|---|---|
| 1 | 5 | 2530 | 490 | 9.8 | 40.4 |
| 2 | 8 | 4123 | 554 | 11.1 | 40.4 |
| 3 | 5 | 2927 | 888 | 17.8 | 40.4 |
| 4 | 6 | 3710 | 1160 | 23.2 | 40.4 |
| 5 | 6 | 2699 | 149 | 3.0 | 40.4 |
| 6 | 6 | 3508 | 959 | 19.2 | 40.4 |
| 7 | 7 | 3327 | 268 | 5.4 | 40.4 |
| 8 | 7 | 3341 | 282 | 5.6 | 40.4 |
| 9 | 6 | 3018 | 469 | 9.4 | 40.4 |
| 10 | 8 | 3771 | 202 | 4.0 | 40.4 |
| 11 | 5 | 2017 | 0 | 0.0 | 40.4 |
| 12 | 4 | 1524 | 0 | 0.0 | 40.4 |
| 13 | 7 | 3466 | 407 | 8.1 | 40.4 |
| 14 | 6 | 2539 | 0 | 0.0 | 40.4 |
| 15 | 6 | 2083 | 0 | 0.0 | 40.4 |

Sum over clusters: at least 606 s in the clusters against 606 s for the delivery alone (+0 s).
```
