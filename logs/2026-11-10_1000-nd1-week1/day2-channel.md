# day2-channel

- Bắt đầu: 2026-11-10 04:01:10, chạy 23 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/theory/channel_check.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/ENVCAL logs/2026-11-10_1000-nd1-week1/day2-channel
```

**Kết quả**

```text
# Kiểm mô hình kênh A2G (ND1 ngày 2)

Ngưỡng hiệu dụng khớp chung cho 4 môi trường: S = -101.04 dBm (danh nghĩa −100 dBm).

| Môi trường | L (dB) | R50 đo (m) | R50 mô hình (m) | RMSE p(d) | Sai lệch lớn nhất |
|---|---|---|---|---|---|
| open | 0.00 | 1016 | 1013 | 0.003 | 0.008 |
| r500 | 9.03 | 498 | 499 | 0.003 | 0.007 |
| r200 | 19.77 | 199 | 200 | 0.001 | 0.007 |
| r100 | 25.74 | 99 | 100 | 0.001 | 0.008 |

**Giả định A1 (nhận gói độc lập)**, trên các cặp có xác suất mô hình trong [0,3; 0,7]:

| Môi trường | p trung bình | P(nhận s+1 \| nhận s) | P(nhận s+1 \| mất s) | P(nhận ở node kề \| nhận) | P(nhận ở node kề \| mất) |
|---|---|---|---|---|---|
| open | 0.515 | 0.541 | 0.487 | 0.538 | 0.489 |
| r500 | 0.498 | 0.525 | 0.471 | 0.524 | 0.478 |
| r200 | 0.487 | 0.516 | 0.461 | 0.507 | 0.466 |
| r100 | 0.493 | 0.518 | 0.469 | 0.519 | 0.479 |

Số cặp node cách nhau dưới 20 m: 818.
```
