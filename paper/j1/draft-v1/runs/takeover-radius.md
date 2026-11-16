---
status: history
updated: 2026-11-16
---
# takeover-radius

- Bắt đầu: 2026-11-16 05:28:12, chạy 10 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/draft-v1/analysis/takeover_radius.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/WIND paper/j1/draft-v1/figs/takeover-radius
```

**Kết quả**

```text
| sigma (m) | rule | activated cells with holders | farthest holder inside the flood | mean hops flooded | mean cells flooded | no estimate (fallback) |
|---|---|---|---|---|---|---|
| 100 | fixed 2 | 9 | 6 | 2.00 | 11.1 | 0 |
| 100 | fixed 3 | 9 | 9 | 3.00 | 20.8 | 0 |
| 100 | fixed 4 | 9 | 9 | 4.00 | 30.6 | 0 |
| 100 | fixed 5 | 9 | 9 | 5.00 | 39.4 | 0 |
| 100 | adaptive | 9 | 9 | 2.78 | 19.8 | 0 |
| 100 | adaptive (true e) | 9 | 9 | 2.78 | 19.8 | 0 |
| 200 | fixed 2 | 42 | 34 | 2.00 | 13.2 | 3 |
| 200 | fixed 3 | 42 | 40 | 3.00 | 23.2 | 3 |
| 200 | fixed 4 | 42 | 42 | 4.00 | 34.0 | 3 |
| 200 | fixed 5 | 42 | 42 | 5.00 | 44.4 | 3 |
| 200 | adaptive | 42 | 41 | 3.45 | 29.7 | 3 |
| 200 | adaptive (true e) | 42 | 42 | 3.40 | 29.2 | 3 |

sigma = 50 m: 0 activated cells with holders.
```
