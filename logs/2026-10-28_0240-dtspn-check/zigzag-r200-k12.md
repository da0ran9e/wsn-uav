# zigzag-r200-k12

- Bắt đầu: 2026-10-28 02:36:13, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 logs/2026-10-28_0240-dtspn-check/zigzag_bound.py r200 12
```

**Kết quả**

```text
r200 k12-s1, xi = 199 m: per cluster, critical cells, open TSP over their centres (m), lower bound on a pass entering every disc (m), its time at 50 m/s against the 40.4 s needed anyway
| k | crit | TSP m | bound m | bound s at 50 m/s | in-cluster time s (max of the two) |
|---|---|---|---|---|---|
| 1 | 7 | 3788 | 1400 | 28.0 | 40.4 |
| 2 | 6 | 2877 | 887 | 17.7 | 40.4 |
| 3 | 5 | 2884 | 1292 | 25.8 | 40.4 |
| 4 | 3 | 1540 | 744 | 14.9 | 40.4 |
| 5 | 6 | 3256 | 1266 | 25.3 | 40.4 |
| 6 | 4 | 1090 | 0 | 0.0 | 40.4 |
| 7 | 3 | 978 | 182 | 3.6 | 40.4 |
| 8 | 7 | 3263 | 875 | 17.5 | 40.4 |
| 9 | 7 | 2714 | 326 | 6.5 | 40.4 |
| 10 | 6 | 2414 | 424 | 8.5 | 40.4 |
| 11 | 7 | 3018 | 630 | 12.6 | 40.4 |
| 12 | 5 | 2141 | 549 | 11.0 | 40.4 |

Sum over clusters: at least 485 s in the clusters against 485 s for the delivery alone (+0 s).
```
