# b3-cc-select-r100-R1-k12-s1

- Bắt đầu: 2026-11-18 14:41:25, chạy 214 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/cc_select.py /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/C4/CP/r100/R1/k12-s1 logs/2026-11-18_1036-k9/data
```

**Kết quả**

```text
# Critical cells chosen for D3 on r100-R1-k12-s1

fcam 0.3, hmax 5 cells, River surrogate (formula). T1: last critical cell done, seconds from take-off (model). Algorithm 3: 66 critical cells. Check against the real plan: largest |T_k| difference 0.00 s.

| umax | rho (people/h) | critical cells | T1 (s) | coverage | farthest (cells) | Alg. 3 T1 (s) | Alg. 3 coverage |
|---|---|---|---|---|---|---|---|
| 0.1 | 20 | 32 | 992 | 1.00 | 5 | 1021 | 0.00 |
| 0.1 | 50 | 52 | 1005 | 1.00 | 5 | 1021 | 0.00 |
| 0.1 | 100 | 98 | 1061 | 1.00 | 5 | 1021 | 0.00 |
| 0.1 | 200 | 220 | 1147 | 1.00 | 5 | 1021 | 0.00 |
| 0.2 | 20 | 32 | 992 | 1.00 | 5 | 1021 | 0.00 |
| 0.2 | 50 | 32 | 992 | 1.00 | 5 | 1021 | 0.00 |
| 0.2 | 100 | 52 | 1005 | 1.00 | 5 | 1021 | 0.00 |
| 0.2 | 200 | 98 | 1061 | 1.00 | 5 | 1021 | 0.00 |
```
