# day4-theorem-a-cell

- Bắt đầu: 2026-11-10 04:05:11, chạy 6 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/theory/theorem_a.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/C4/CP logs/2026-10-27_1714-campaign4/score uav-l2/docs/data/results/campaign4.csv logs/2026-11-10_1000-nd1-week1/day4-theorem-a-cell --cell
```

**Kết quả**

```text
# Kiểm định lý A (ND1 ngày 3–4)

T_FC đo: thời gian đội 1 của FC + DTSP-N (C4, trung bình các seed). T_FC dự đoán: T_FC đo ở open, cộng phần thời gian
lượn thay đổi theo công thức của định lý A (chỉ dùng mô hình kênh ngày 2, không khớp thêm tham số). T_River: thời gian
đội 1 của CHORD + River cộng thời điểm sẵn sàng trung bình (ns-3).

| Bản đồ | Kênh | R50 (m) | Số critical cell | Lượn dự đoán (s) | T_FC đo (s) | T_FC dự đoán (s) | Sai lệch | T_River (s) | Tỉ số đo | Tỉ số dự đoán |
|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 1016 | 45 | 1230 | 669 | 669 | +0 % | 1144 | 0.58 | 0.58 |
| k8-s1 | r500 | 498 | 45 | 1230 | 1320 | 669 | -49 % | 1186 | 1.11 | 0.56 |
| k8-s1 | r200 | 199 | 45 | 1719 | 2687 | 1157 | -57 % | 1219 | 2.20 | 0.95 |
| k8-s1 | r100 | 99 | 45 | 2575 | 3305 | 2013 | -39 % | 1236 | 2.67 | 1.63 |
| k12-s1 | open | 1016 | 66 | 1527 | 913 | 913 | +0 % | 1858 | 0.49 | 0.49 |
| k12-s1 | r500 | 498 | 66 | 1528 | 2011 | 913 | -55 % | 1895 | 1.06 | 0.48 |
| k12-s1 | r200 | 199 | 66 | 2688 | 4016 | 2074 | -48 % | 1930 | 2.08 | 1.07 |
| k12-s1 | r100 | 99 | 66 | 4378 | 5078 | 3764 | -26 % | 1947 | 2.61 | 1.93 |
| k16-s1 | open | 1016 | 92 | 2419 | 1134 | 1134 | +0 % | 2138 | 0.53 | 0.53 |
| k16-s1 | r500 | 498 | 92 | 2419 | 2563 | 1134 | -56 % | 2183 | 1.17 | 0.52 |
| k16-s1 | r200 | 199 | 92 | 3586 | 5567 | 2302 | -59 % | 2215 | 2.51 | 1.04 |
| k16-s1 | r100 | 99 | 92 | 5422 | 6808 | 4138 | -39 % | 2233 | 3.05 | 1.85 |
```
