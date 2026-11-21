# b8-summary

- Bắt đầu: 2026-11-21 02:14:40, chạy 0 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 paper/j1/analysis/b8_summary.py logs/2026-11-18_1036-k9/data logs/2026-11-18_1036-k9/data/b8/summary
```

**Kết quả**

```text
# K9 B8: hybrid option on k8 r100 (model level)

AI cells needed and T1 (River surrogate, s) per budget and rho; 'no' when even an AI node in every cell (617) cannot carry the flow (coverage in brackets). fcam 0.3, hop limit 5. The surrogate is reliable up to about 70 AI cells (B4).


## Budget 0.1

| option | rho 20 | rho 50 | rho 100 | rho 200 |
|---|---|---|---|---|
| D3 (all vectors, 528 B) | 24: 661 | 34: 675 | 69: 728 | 161: 907 |
| hybrid, NPU 0.8 | 39: 675 | 94: 772 | 212: 1014 | 479: 1536 |
| hybrid, NPU 0.5 | 74: 729 | 198: 1011 | 454: 1536 | no (0.61) |
| hybrid, NPU 0.2 | 114: 813 | 334: 1198 | no (0.82) | no (0.41) |
| crops only (5 kB) | 140: 848 | 414: 1394 | no (0.68) | no (0.34) |
| NPU 0.5, crop 15 kB | 237: 1052 | no (0.87) | no (0.44) | no (0.22) |
| NPU 0.5, vector 4.1 kB | 122: 827 | 372: 1291 | no (0.74) | no (0.37) |

## Budget 0.2

| option | rho 20 | rho 50 | rho 100 | rho 200 |
|---|---|---|---|---|
| D3 (all vectors, 528 B) | 23: 661 | 24: 661 | 34: 675 | 69: 728 |
| hybrid, NPU 0.8 | 26: 661 | 46: 693 | 94: 772 | 212: 1014 |
| hybrid, NPU 0.5 | 38: 675 | 92: 755 | 198: 1011 | 454: 1536 |
| hybrid, NPU 0.2 | 53: 695 | 155: 874 | 334: 1198 | no (0.82) |
| crops only (5 kB) | 62: 724 | 176: 942 | 414: 1394 | no (0.68) |
| NPU 0.5, crop 15 kB | 103: 816 | 319: 1200 | no (0.87) | no (0.44) |
| NPU 0.5, vector 4.1 kB | 57: 710 | 167: 936 | 372: 1291 | no (0.74) |

## Phase 2 at rho = 20, budget 0.1 (read off the B5 curve, r100, k = 1)

| option | AI cells | T, alarm 0.1 per AI cell (s) | T, 2.4 alarms system-wide (s) |
|---|---|---|---|
| D3 (all vectors, 528 B) | 24 | 823 | 823 |
| hybrid, NPU 0.8 | 39 | 870 | 832 |
| hybrid, NPU 0.5 | 74 | 949 | 889 |
| hybrid, NPU 0.2 | 114 | 1080 | 968 |
| crops only (5 kB) | 140 | 1165 | 1019 |
| NPU 0.5, crop 15 kB | 237 | outside the B5 range | outside the B5 range |
| NPU 0.5, vector 4.1 kB | 122 | 1106 | 984 |

## Matching with K models per AI node

The query stays images: an AI node embeds the L query images once per model it holds. Extra time over one model (s); the V1 visit is 78 s.

| device | K | first pass, L = 3 | V1, L = 20 |
|---|---|---|---|
| Pi 5 + Hailo-8L | 1 | 0.00 | 0.00 |
| Pi 5 + Hailo-8L | 3 | 0.02 | 0.16 |
| Pi 5 + Hailo-8L | 5 | 0.05 | 0.31 |
| Pi 5 CPU | 1 | 0.00 | 0.00 |
| Pi 5 CPU | 3 | 0.48 | 3.17 |
| Pi 5 CPU | 5 | 0.95 | 6.35 |
```
