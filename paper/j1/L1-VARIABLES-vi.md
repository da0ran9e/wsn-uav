---
status: current
updated: 2026-11-21
---
# J1 · Biến quyết định (bản bàn, chatlog mục 389)

Đầu vào là [bản tóm tắt bối cảnh](CONTEXT-SUMMARY-vi.md). File này liệt kê các thứ có thể chọn được trong hệ thống, chia theo lúc
quyết định, và đề xuất cái nào là biến của bài toán L1, cái nào cố định hay để thuật toán xử lý. Chưa chốt.

## 1. Quyết định trước sự cố (pha 0)

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| y_v ∈ {0, 1} | node mạnh v có làm AI node không (tập critical cell K suy ra từ y) | biến của L1 |
| x_uv ∈ {0, 1} | node thường u giao cho AI node v | biến của L1 |
| lưới cell, CL, cặp gateway | cấu trúc mạng | cố định (thủ tục pha 0) |
| cột đèn chuyển tiếp | đặt ở cell cần | cố định (quy tắc đã chốt) |
| lịch kênh | 7 màu cell, kênh cặp gateway, kênh 26 cho lượt bay | cố định (K1d) |

## 2. Quyết định cho pha 1 (tính sẵn ở pha 0, dùng khi có sự cố)

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| π | thứ tự các cụm trong tour | biến của L1 |
| q(t), v(t) | quỹ đạo và tốc độ UAV (Dubins, độ cao 100 m, tránh vùng cấm) | biến của L1 |
| s(t) | gói nào được phát lúc nào (từ đó suy ra đoạn gói mỗi cell SPINE giữ) | biến của L1 |
| vai trò River (SPINE, Bank, Ring) | cell nào giữ, nhận, chuyển gì | do thuật toán River sinh từ (K, q, s) |
| luồng Bank → Ring, cây dùng chung | đường đi trên đồ thị cell | do thuật toán (lập kế hoạch cân tải) sinh; có thể viết thành bài luồng nhiều hàng có sức chứa |
| T_fb, phân công vá | hạn và cách vá cell bị sót | tham số (quét) |

## 3. Quyết định ở pha 2

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| t₂ | lúc đội 2 cất cánh | theo chính sách (cất cánh khi có báo cáo đầu tiên) |
| thứ tự thăm | cell nào xác minh trước | chính sách thích nghi theo xác suất (đã có trong repo) |

## 4. Đại lượng ngẫu nhiên và cho trước

- Ngẫu nhiên: kênh A2G và G2G, MAC, nhiễu, lần thấy của camera, báo cáo LoRa.
- Xấu nhất: vị trí người cần tìm (cell thật), lấy max.
- Cho trước: bản đồ, node, Q, tham số UAV, ρ, tỉ lệ NPU, K mô hình.

## 5. Câu hỏi cần quyết

1. L1 gồm cả biến pha 0 (y, x) và biến pha 1 (π, q, s) trong một bài, hay tách hai tầng (chọn critical cell rồi lập tour)?
2. Kế hoạch River là biến tường minh (luồng trên đồ thị cell) hay là một hàm thời gian mặt đất T_g(K, q, s) do thuật toán cho?
3. Pha 2 là chính sách cố định, hay đưa t₂ vào làm biến?
