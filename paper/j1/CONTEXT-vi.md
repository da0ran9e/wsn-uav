---
status: current
updated: 2026-11-14
---
# J1 · Bối cảnh, thực thể và tham số của bài toán

File mô tả chung cho J1 (chatlog mục 323–324). Đây là bản thử nghiệm, chốt dần qua thảo luận, không sửa đề cương. Phần
phát biểu bài toán tối ưu pha 1 (L1 trong `PLAN-TRACKS-vi.md`) dựa trên file này. Mỗi mục ghi trạng thái: **chốt**
(người dùng đã quyết), **đề xuất** (Claude đề xuất, chờ duyệt), **mở** (còn phải bàn).

## 1. Kịch bản

| Mục | Nội dung | Trạng thái |
|---|---|---|
| Vùng nhiệm vụ | Khu vực địa hình phức tạp (núi, rừng, thung lũng) cỡ một vườn quốc gia: vài trăm tới hơn một nghìn km². Ví dụ để tính: Cúc Phương khoảng 222 km², Phong Nha–Kẻ Bàng khoảng 1 233 km² (cần kiểm số liệu) | chốt (quy mô), mở (con số cụ thể) |
| Vì sao khó | Địa hình che khuất và tán rừng làm kênh từ trên không xuống yếu và biến động; vùng không có mạng di động | chốt |
| Thiết bị | Nhiều thiết bị IoT có sẵn: camera, cảm biến; phần lớn là node yếu, một số node mạnh chạy được AI | chốt |
| Sự cố | Bất kỳ sự cố nào cần tìm kiếm (người lạc, truy vết đối tượng); mạng phục vụ nhiều lượt truy vấn trong suốt vòng đời | chốt |
| Phân bố thiết bị | Rải ngẫu nhiên, càng đều càng tốt, phủ cả vùng (mục 325). Mật độ phải thấp hơn bản hội nghị, xem mục 4 | chốt (phân bố), mở (mật độ) |
| Vì sao cần UAV | Truy vấn khoảng 400 KB không đẩy được qua LoRa hay phát đa chặng từ trạm gốc trong thời gian chấp nhận được | đề xuất (cần một phép tính thời gian) |

## 2. Thực thể

| Thực thể | Mô tả | Trạng thái |
|---|---|---|
| Trạm gốc (BS) | Lập kế hoạch pha 0, pha 1 (tour và kế hoạch River), nhận kết quả qua LoRa | chốt |
| UAV cánh bằng (đội 1) | Nhiều UAV bay song song qua các cụm, phát truy vấn ở pha 1 (mục 325) | chốt (nhiều UAV); số chiếc, điểm cất hạ cánh, thời gian bay mỗi chuyến mở |
| UAV cánh quay (đội 2) | Đến xác minh các cell nghi vấn ở pha 2 | chốt (ngoài phạm vi J1) |
| Node thường | Camera hoặc cảm biến yếu, ghi dữ liệu và gửi dữ liệu về AI node phụ trách nó (trước khi có truy vấn); chuyển tiếp gói 802.15.4 | chốt (mục 325) |
| Node mạnh (AI node) | Node đủ năng lực chạy đối sánh; giữ dữ liệu cần đối sánh do các node thường gửi về | chốt (mục 325) |
| Cell | Ô lục giác bán kính R; mỗi cell có một CL | chốt |
| CL | Trưởng cell, gom gói từ node trong cell | chốt |
| CGW | Cặp gateway duy nhất giữa hai cell kề | chốt |
| Cụm, CH | Tối đa 80 cell một cụm; CH có thêm LoRa lên trạm gốc | chốt |
| Critical cell (CC) | Cell chứa ít nhất một AI node, phải nhận đủ truy vấn | chốt |
| Truy vấn | Bộ ảnh tham chiếu khoảng 400 KB, Q = 4 041 gói, chia thành các ảnh | chốt |
| SPINE, Bank, Ring | Vai trò cell trong River: cell dưới đường bay giữ một đoạn gói; dải cell nhận từ SPINE; vòng cell quanh CC | chốt |

## 3. Chọn critical cell

Trạm gốc chọn một số AI node trong số các node mạnh, ở pha 0. Tiêu chí: năng lực phần cứng, cùng các yếu tố tại chỗ
(cây che, địa hình, che khuất), và các AI node không được quá gần nhau. Cell chứa AI node được chọn là CC. Bài toán
chọn này giống bài toán đặt cơ sở (mở cửa hàng nhượng quyền sao cho tổng lợi ích lớn mà các cửa hàng không giành khách
của nhau). Trong tài liệu đây là họ facility location có ràng buộc khoảng cách tối thiểu, gần với p-dispersion và
maximum coverage (cần tra cứu thêm). **Trạng thái:** chốt (cách hiểu), mở (hàm mục tiêu cụ thể, J1 coi tập CC là đầu
vào hay giải luôn).

## 4. Tham số

Các tham số vô tuyến, kênh và UAV đã có ở `params.yaml` (bảng ở `paper/PARAMS-vi.md`), kèm nguồn và nhãn. File này chỉ
ghi tham số của kịch bản mới và chỗ phải đổi.

| Tham số | Bản hội nghị (ICC) | J1 | Trạng thái |
|---|---|---|---|
| Diện tích vùng | 617 cell ≈ 16 km² (bản đồ k8) | 200–1 200 km² | chốt (cỡ), mở (con số) |
| Số cell nếu phủ kín | 617 | khoảng 8 000–47 000 (diện tích một cell ≈ 0,026 km²), nếu giữ R = 100 m | mở (giữ R hay tăng R) |
| Mật độ node | khoảng 21 node một cell (13 086 node) | giữ mật độ này mà phủ kín thì cần 0,2–1 triệu node, khó thực tế; cần chọn mật độ mục tiêu, giữ được liên thông G2G giữa các cell | mở |
| Số CC | 45 CC trên 8 cụm (k8) | theo bài toán chọn CC | mở |
| Kênh A2G | mô hình hai đoạn, thêm suy hao môi trường cố định, Rician K = 2 | thêm che khuất tương quan, fading tương quan, phụ thuộc góc ngẩng (việc K1) | đề xuất |
| UAV cánh bằng | 1 chiếc, 25–50 m/s, H = 100 m, ρ = 63,7 m | m chiếc, giữ động học; thêm thời gian bay tối đa một chuyến, điểm cất hạ cánh | chốt (nhiều UAV), mở (m, depot, thời gian bay) |
| Số truy vấn trong vòng đời mạng | 1 | nhiều; dùng để chia chi phí pha 0 | chốt (nhiều), mở (bao nhiêu) |

## 5. Hệ quả của các lựa chọn đã chốt

- Phủ đều ở quy mô vườn quốc gia buộc mật độ node thấp hơn nhiều. Mật độ quyết định số node mỗi cell, nên quyết định xác
  suất nhận ở mức cell P_k và dung lượng giữa các cell. Có thể phải tăng R; R bị chặn bởi tầm G2G để CGW còn nối được.
- Dữ liệu nằm ở AI node nên trước truy vấn đã có luồng nền từ node thường về AI node. Bài toán chọn CC (mục 3) có thêm
  ràng buộc phủ: mỗi node thường cách một AI node không quá h hop, và AI node có giới hạn bộ nhớ. Lập luận "bộ nhớ đầy
  thì dữ liệu bị ghi đè" đặt ở AI node.
- Nhiều UAV biến phần tour thành Dubins TSP nhiều xe: chia cụm cho từng UAV rồi xếp tour, mục tiêu thường là min-max
  (UAV về muộn nhất). Tài liệu có sẵn trong Drive: Rathinam 2007 (nhiều xe có ràng buộc quay), Sensors 23:6432 (Dubins
  MinMax mTSP), Xu–Liang–Lin 2015 (min-max cycle cover). Bổ đề NP-khó vẫn đúng vì bản một UAV là trường hợp riêng.
  River khi đó chạy trên các cụm được UAV khác nhau phục vụ ở những thời điểm khác nhau.

## 6. Câu hỏi mở

- a. Mật độ node mục tiêu (node mỗi km² hoặc node mỗi cell), và giữ R = 100 m hay tăng R?
- b. Số UAV m, điểm cất hạ cánh (một trạm hay nhiều trạm), thời gian bay tối đa mỗi chuyến?
- c. Mục tiêu khi nhiều UAV: thời điểm AI node cuối cùng sẵn sàng (min-max) hay trung bình qua các cụm?
- d. Mục tiêu tìm kiếm điển hình là gì (người lạc, động vật, đối tượng)? Câu trả lời quyết định mỗi phút chậm trễ đáng
  giá bao nhiêu.
- e. Vì sao không phát truy vấn từ trạm gốc qua mạng mặt đất (đa chặng 802.15.4) hay qua LoRa: cần một phép tính thời
  gian để đưa vào bài.
- f. Số sự cố trong vòng đời mạng (để chia chi phí pha 0).
