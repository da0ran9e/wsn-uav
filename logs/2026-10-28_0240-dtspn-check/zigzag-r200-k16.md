# zigzag-r200-k16

- Bắt đầu: 2026-10-28 02:36:11, chạy 1 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 logs/2026-10-28_0240-dtspn-check/zigzag_bound.py r200 16
```

**Kết quả**

```text
r200 k16-s1, xi = 199 m: per cluster, critical cells, open TSP over their centres (m), lower bound on a pass entering every disc (m), its time at 50 m/s against the 40.4 s needed anyway
| k | crit | TSP m | bound m | bound s at 50 m/s | in-cluster time s (max of the two) |
|---|---|---|---|---|---|
| 1 | 5 | 2530 | 938 | 18.8 | 40.4 |
| 2 | 8 | 4123 | 1337 | 26.7 | 40.4 |
| 3 | 5 | 2927 | 1335 | 26.7 | 40.4 |
| 4 | 6 | 3710 | 1720 | 34.4 | 40.4 |
| 5 | 6 | 2699 | 709 | 14.2 | 40.4 |
| 6 | 6 | 3508 | 1518 | 30.4 | 40.4 |
| 7 | 7 | 3327 | 939 | 18.8 | 40.4 |
| 8 | 7 | 3341 | 953 | 19.1 | 40.4 |
| 9 | 6 | 3018 | 1028 | 20.6 | 40.4 |
| 10 | 8 | 3771 | 985 | 19.7 | 40.4 |
| 11 | 5 | 2017 | 425 | 8.5 | 40.4 |
| 12 | 4 | 1524 | 330 | 6.6 | 40.4 |
| 13 | 7 | 3466 | 1078 | 21.6 | 40.4 |
| 14 | 6 | 2539 | 549 | 11.0 | 40.4 |
| 15 | 6 | 2083 | 93 | 1.9 | 40.4 |

Sum over clusters: at least 606 s in the clusters against 606 s for the delivery alone (+0 s).
```
