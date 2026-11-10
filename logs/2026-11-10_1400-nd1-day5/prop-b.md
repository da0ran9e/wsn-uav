# prop-b

- Bắt đầu: 2026-11-10 04:17:33, chạy 16 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/theory/prop_b.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/WIND /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/propb
```

**Kết quả**

```text
# Mệnh đề B, thử nghiệm (ND1 ngày 5)

SPINE cell: 840; bán kính cell ước lượng R = 100.3 m; kênh r100 (R50 ≈ 99 m).

| e (m) | số SPINE cell | tỉ lệ kích hoạt đo | tỉ lệ kích hoạt mô hình | hop xa nhất đo |
|---|---|---|---|---|
| 0–25 | 170 | 0.00 | 0.00 | 0 |
| 25–50 | 163 | 0.02 | 0.01 | 0 |
| 50–75 | 150 | 0.03 | 0.03 | 0 |
| 75–100 | 79 | 0.01 | 0.02 | 0 |
| 100–150 | 132 | 0.05 | 0.05 | 2 |
| 150–200 | 52 | 0.08 | 0.09 | 2 |
| 200–300 | 69 | 0.36 | 0.42 | 3 |
| 300–800 | 25 | 0.92 | 0.91 | 4 |

σ = 50: kích hoạt đo 3 (có cell khác giữ gói 0, gói không ai nghe 3), tổng xác suất mô hình 2.0, e lớn nhất 173 m, hop xa nhất 0

σ = 100: kích hoạt đo 17 (có cell khác giữ gói 9, gói không ai nghe 8), tổng xác suất mô hình 18.2, e lớn nhất 346 m, hop xa nhất 3

σ = 200: kích hoạt đo 48 (có cell khác giữ gói 42, gói không ai nghe 6), tổng xác suất mô hình 51.7, e lớn nhất 691 m, hop xa nhất 4

Hiệu chỉnh xác suất mô hình (chia 5 nhóm theo P_model):

| P_model trung bình | tỉ lệ đo | n |
|---|---|---|
| 0.000 | 0.000 | 168 |
| 0.000 | 0.000 | 168 |
| 0.000 | 0.000 | 168 |
| 0.000 | 0.000 | 168 |
| 0.428 | 0.405 | 168 |

e nhỏ nhất có kích hoạt: 25 m. Khoảng cách xa nhất (gói tệ nhất tới node gần nhất của a+N(a)) mà P_model < 0,1: 106 m.
Kích hoạt khi khoảng cách gói tệ nhất ≤ 106 m: 12/778.
Chặn số hop h(e) = ⌈e/(√3R)⌉ + 1 (w = 0): vi phạm 0/51 SPINE cell có người giữ; chặt (bằng nhau) 9/51; cặp (h đo, chặn): [((2, 2), 5), ((2, 3), 26), ((2, 4), 9), ((3, 3), 3), ((3, 4), 4), ((3, 5), 2), ((4, 4), 1), ((4, 5), 1)]
```
