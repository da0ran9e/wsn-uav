# b6-high-rho

- Bắt đầu: 2026-11-20 04:33:24, chạy 289 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/cc_select.py /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/C4/CP/r100/R1/k8-s1 logs/2026-11-18_1036-k9/data/b6-high --rho 400,800,1500,3700
```

**Kết quả**

```text
# Critical cells chosen for D3 on r100-R1-k8-s1

fcam 0.3, hmax 5 cells, River surrogate (formula). T1: last critical cell done, seconds from take-off (model). Algorithm 3: 45 critical cells. Check against the real plan: largest |T_k| difference 0.00 s.

| umax | rho (people/h) | critical cells | T1 (s) | coverage | farthest (cells) | Alg. 3 T1 (s) | Alg. 3 coverage |
|---|---|---|---|---|---|---|---|
| 0.1 | 400 | 344 | 1217 | 1.00 | 2 | 753 | 0.00 |
| 0.1 | 800 | 617 | 1786 | 0.80 | 0 | 753 | 0.00 |
| 0.1 | 1500 | 617 | 1786 | 0.43 | 0 | 753 | 0.00 |
| 0.1 | 3700 | 617 | 1786 | 0.17 | 0 | 753 | 0.00 |
| 0.2 | 400 | 161 | 906 | 1.00 | 4 | 753 | 0.00 |
| 0.2 | 800 | 344 | 1217 | 1.00 | 2 | 753 | 0.00 |
| 0.2 | 1500 | 617 | 1786 | 0.85 | 0 | 753 | 0.00 |
| 0.2 | 3700 | 617 | 1786 | 0.35 | 0 | 753 | 0.00 |
```
