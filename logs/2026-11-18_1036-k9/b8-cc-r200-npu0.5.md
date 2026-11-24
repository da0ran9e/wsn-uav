# b8-cc-r200-npu0.5

- Bắt đầu: 2026-11-21 02:24:37, chạy 53 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/cc_select.py /tmp/claude-0/-home-user-wsn-uav/98443ff4-47f6-50e4-8347-73e324c4e08a/scratchpad/k9/C4/CP/r200/R1/k8-s1 logs/2026-11-18_1036-k9/data/b8/r200-npu0.5 --npu 0.5 --rho 20 --umax 0.1
```

**Kết quả**

```text
# Critical cells chosen for the hybrid option (NPU share 0.5, vector 532 B, crop 5000 B) on r200-R1-k8-s1

Mean record 2766 B per person, fcam 0.3, hmax 5 cells, River surrogate (formula). T1: last critical cell done, seconds from take-off (model). Algorithm 3: 45 critical cells. Check against the real plan: largest |T_k| difference 0.00 s.

| umax | rho (people/h) | critical cells | T1 (s) | coverage | farthest (cells) | Alg. 3 T1 (s) | Alg. 3 coverage |
|---|---|---|---|---|---|---|---|
| 0.1 | 20 | 75 | 714 | 1.00 | 5 | 740 | 0.00 |
```
