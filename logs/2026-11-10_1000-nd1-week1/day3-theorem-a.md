# day3-theorem-a

- Bắt đầu: 2026-11-10 04:04:39, chạy 5 s, mã thoát 0
- Thư mục: `/home/user/wsn-uav`

**Lệnh**

```bash
python3 uav-l2/tools/theory/theorem_a.py /tmp/claude-0/-home-user-wsn-uav/fd83db84-4832-5a0e-be6a-d1201f4d6a60/scratchpad/C4/CP logs/2026-10-27_1714-campaign4/score uav-l2/docs/data/results/campaign4.csv logs/2026-11-10_1000-nd1-week1/day3-theorem-a
```

**Kết quả**

```text
# Kiểm định lý A (ND1 ngày 3–4)

T_FC đo: thời gian đội 1 của FC + DTSP-N (C4, trung bình các seed). T_FC dự đoán: T_FC đo ở open, cộng phần thời gian
lượn thay đổi theo công thức của định lý A (chỉ dùng mô hình kênh ngày 2, không khớp thêm tham số). T_River: thời gian
đội 1 của CHORD + River cộng thời điểm sẵn sàng trung bình (ns-3).

| Bản đồ | Kênh | R50 (m) | Số critical cell | Lượn dự đoán (s) | T_FC đo (s) | T_FC dự đoán (s) | Sai lệch | T_River (s) | Tỉ số đo | Tỉ số dự đoán |
|---|---|---|---|---|---|---|---|---|---|---|
| k8-s1 | open | 1016 | 45 | 1240 | 669 | 669 | +0 % | 1144 | 0.58 | 0.58 |
| k8-s1 | r500 | 498 | 45 | 1342 | 1320 | 771 | -42 % | 1186 | 1.11 | 0.65 |
| k8-s1 | r200 | 199 | 45 | 2585 | 2687 | 2014 | -25 % | 1219 | 2.20 | 1.65 |
| k8-s1 | r100 | 99 | 45 | 11288 | 3305 | 10717 | +224 % | 1236 | 2.67 | 8.67 |
| k12-s1 | open | 1016 | 66 | 1547 | 913 | 913 | +0 % | 1858 | 0.49 | 0.49 |
| k12-s1 | r500 | 498 | 66 | 1767 | 2011 | 1133 | -44 % | 1895 | 1.06 | 0.60 |
| k12-s1 | r200 | 199 | 66 | 4346 | 4016 | 3712 | -8 % | 1930 | 2.08 | 1.92 |
| k12-s1 | r100 | 99 | 66 | 10614 | 5078 | 9980 | +97 % | 1947 | 2.61 | 5.13 |
| k16-s1 | open | 1016 | 92 | 2438 | 1134 | 1134 | +0 % | 2138 | 0.53 | 0.53 |
| k16-s1 | r500 | 498 | 92 | 2652 | 2563 | 1348 | -47 % | 2183 | 1.17 | 0.62 |
| k16-s1 | r200 | 199 | 92 | 5348 | 5567 | 4045 | -27 % | 2215 | 2.51 | 1.83 |
| k16-s1 | r100 | 99 | 92 | 24833 | 6808 | 23529 | +246 % | 2233 | 3.05 | 10.54 |
```
