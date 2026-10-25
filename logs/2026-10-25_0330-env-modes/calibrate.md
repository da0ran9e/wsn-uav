# calibrate

- Bắt đầu: 2026-10-25 03:07:42, chạy 83 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/a2g_env.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/CAMP-BIN3 /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENVCAL
```

**Kết quả**

```text
loss  0.00 dB: R50  1015 m, R10  1366 m
loss  9.03 dB: R50   498 m, R10   678 m
loss 19.77 dB: R50   199 m, R10   284 m
loss 25.74 dB: R50    99 m, R10   162 m

| excess loss (dB) | R50 (m) | R10 (m) | p(0) | p(100 m) | p(200 m) | p(500 m) |
|---|---|---|---|---|---|---|
| 0.00 | 1015 | 1366 | 0.999 | 0.999 | 0.996 | 0.950 |
| 9.03 | 498 | 678 | 0.998 | 0.993 | 0.968 | 0.494 |
| 19.77 | 199 | 284 | 0.960 | 0.887 | 0.495 | 0.000 |
| 25.74 | 99 | 162 | 0.838 | 0.496 | 0.014 | 0.000 |

R50 500 m: 9.03 dB (measured 498 m), R50 200 m: 19.77 dB (measured 199 m), R50 100 m: 25.74 dB (measured 99 m)
```
