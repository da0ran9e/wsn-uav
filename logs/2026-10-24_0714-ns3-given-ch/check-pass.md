# Kiểm tra pass ns-3 có cột thời gian (mục 157)

Binary: `pass-bin-v1` (cũ, 2026-10-22) và `pass-bin-v2` (coop-pass.cc đọc thêm cột `t`), cluster c2 của `NS3/chord/k8-s1` (2 543 node, 5 502 gói), 1 lượt.

| so sánh | kết quả |
|---|---|
| v1 và v2, cùng đường không có `t` | bitmap giống hệt (`cmp`) |
| v1 không `t` và v2 với `t = s / 50` (7 chữ số) | 2 / 13 996 672 bit khác (vị trí lệch < 1 mm do làm tròn), `runs.csv` giống hệt |
| v2 trên c1 của `T157try/ml10-s2` sau `pass_speed.py` (3 vòng lượn, cap 35 m/s) | chạy qua mọi CHECK; 9 553 gói, khớp số gói và vị trí của `river_plan.packets` (lệch tối đa 5 mm) |

Lỗi gặp và sửa: lần đầu `t` nội suy theo chiều dài các dây cung 10 m (ngắn hơn đường gốc 0,012 m), đỉnh cuối bị kẹp thời gian nên đoạn cuối "bay" 152 m/s; CHECK tốc độ của pass bắt được. Sửa: chuẩn hoá chiều dài trước khi nội suy.
