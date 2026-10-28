# zigzag-r100-k16

- Bắt đầu: 2026-10-28 02:36:12, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 logs/2026-10-28_0240-dtspn-check/zigzag_bound.py r100 16
```

**Kết quả**

```text
r100 k16-s1, xi = 99 m: per cluster, critical cells, open TSP over their centres (m), lower bound on a pass entering every disc (m), its time at 50 m/s against the 40.4 s needed anyway
| k | crit | TSP m | bound m | bound s at 50 m/s | in-cluster time s (max of the two) |
|---|---|---|---|---|---|
| 1 | 5 | 2530 | 1738 | 34.8 | 40.4 |
| 2 | 8 | 4123 | 2737 | 54.7 | 54.7 |
| 3 | 5 | 2927 | 2135 | 42.7 | 42.7 |
| 4 | 6 | 3710 | 2720 | 54.4 | 54.4 |
| 5 | 6 | 2699 | 1709 | 34.2 | 40.4 |
| 6 | 6 | 3508 | 2518 | 50.4 | 50.4 |
| 7 | 7 | 3327 | 2139 | 42.8 | 42.8 |
| 8 | 7 | 3341 | 2153 | 43.1 | 43.1 |
| 9 | 6 | 3018 | 2028 | 40.6 | 40.6 |
| 10 | 8 | 3771 | 2385 | 47.7 | 47.7 |
| 11 | 5 | 2017 | 1225 | 24.5 | 40.4 |
| 12 | 4 | 1524 | 930 | 18.6 | 40.4 |
| 13 | 7 | 3466 | 2278 | 45.6 | 45.6 |
| 14 | 6 | 2539 | 1549 | 31.0 | 40.4 |
| 15 | 6 | 2083 | 1093 | 21.9 | 40.4 |

Sum over clusters: at least 664 s in the clusters against 606 s for the delivery alone (+58 s).
```
