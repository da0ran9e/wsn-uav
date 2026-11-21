# b8-cc-npu0.2

- Bắt đầu: 2026-11-21 02:04:00, chạy 318 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/cc_select.py /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/C4/CP/r100/R1/k8-s1 logs/2026-11-18_1036-k9/data/b8/npu0.2 --npu 0.2
```

**Kết quả**

```text
# Critical cells chosen for the hybrid option (NPU share 0.2, vector 532 B, crop 5000 B) on r100-R1-k8-s1

Mean record 4106 B per person, fcam 0.3, hmax 5 cells, River surrogate (formula). T1: last critical cell done, seconds from take-off (model). Algorithm 3: 45 critical cells. Check against the real plan: largest |T_k| difference 0.00 s.

| umax | rho (people/h) | critical cells | T1 (s) | coverage | farthest (cells) | Alg. 3 T1 (s) | Alg. 3 coverage |
|---|---|---|---|---|---|---|---|
| 0.1 | 20 | 114 | 813 | 1.00 | 4 | 753 | 0.00 |
| 0.1 | 50 | 334 | 1197 | 1.00 | 2 | 753 | 0.00 |
| 0.1 | 100 | 617 | 1786 | 0.82 | 0 | 753 | 0.00 |
| 0.1 | 200 | 617 | 1786 | 0.41 | 0 | 753 | 0.00 |
| 0.2 | 20 | 53 | 695 | 1.00 | 5 | 753 | 0.00 |
| 0.2 | 50 | 155 | 873 | 1.00 | 4 | 753 | 0.00 |
| 0.2 | 100 | 334 | 1197 | 1.00 | 2 | 753 | 0.00 |
| 0.2 | 200 | 617 | 1786 | 0.82 | 0 | 753 | 0.00 |
```
