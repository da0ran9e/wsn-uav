---
status: current
updated: 2026-11-20
---
# J1 · Bối cảnh bài toán (bản tóm tắt)

Tóm tắt những gì đã chốt qua thảo luận (chatlog mục 323–378). Chi tiết, số liệu và nguồn ở [CONTEXT-vi.md](CONTEXT-vi.md); số
trong ngoặc là mục của file đó. Dòng có nhãn **[chờ]** là đề xuất chưa được xác nhận, **[giả định]** là số chưa có nguồn trích.

## 1. Kịch bản

- Đô thị hiện đại: càng hiện đại thì mạng IoT càng dày, nhưng nhà cao tầng và hạ tầng làm kênh từ trên không xuống kém (mục 1).
- Mục tiêu điển hình là tìm người mất tích; nhiệm vụ không giới hạn thời gian, tìm tới khi thấy (mục 16).
- Vùng nhiệm vụ là một quận thật 5–60 km², vừa một chuyến bay của một UAV (mục 18–22).
- Một UAV ở pha 1. Nhiều UAV để sau, khi có cơ chế phối hợp thật; khi đó mục tiêu vẫn là min-max (mục 5).
- Tần suất: Singapore khoảng 1 300 báo cáo mất tích mỗi năm (khoảng 22 trên 100 000 dân); quy ra vài chục tới khoảng 150 vụ
  mỗi quận mỗi năm, một phần cần UAV (mục 23).

## 2. Vì sao cần UAV

- Node rẻ chỉ có radio 802.15.4, không nối Internet; dữ liệu ở lại thiết bị vì quyền riêng tư, chỉ điểm số vài byte rời node
  (mục 15).
- Gửi truy vấn 400 KB qua LoRa mất ít nhất 1,8 h (chu kỳ 10 %), 18 h (1 %) (mục 12).
- Qua mạng mặt đất từ trạm gốc: 50–95 chặng; giao thức CSMA mất 20 phút tới hơn một giờ; flood đồng bộ kiểu Pando 1,2–2,4 phút
  nếu giữ được tốc độ ở độ sâu đó (chưa có số đo). Lập luận đối đáp: không có sẵn đường mặt đất, flood khó bền ở độ sâu lớn,
  flood tốn năng lượng của mọi node (mục 12).
- Tiền lệ: Thread (802.15.4) trong nhà thông minh; Amazon Sidewalk là mạng dùng chung giữa thiết bị của nhiều chủ (mục 15).

## 3. Mạng và thiết bị

- Thiết bị cố định: chuông cửa, camera tường, camera cột, máy bán hàng; không xét camera hành trình (mục 20, 26).
- Mật độ chính 816 node/km² (hướng tới); 400 và 280 node/km² để xem độ nhạy (mục 4, 10).
- Đặt node: theo viền nhà mỗi 40 m, dọc phố mỗi 30 m, không trên nước (mục 20).
- Node pin: 45 % node trên nhà, 11–22 % tổng số; không chuyển tiếp, không là AI node, không tham gia pha 1 (mục 15, 25).
- Node chuyển tiếp trên cột đèn mỗi 35 m, chỉ ở cell cần (rỗng, đứt bên trong, thiếu gateway); node bị lạc làm node lá (mục 21).
- Sở hữu: mạng dùng chung kiểu Sidewalk; thành phố hoặc nhà cung cấp chạy pha 0 (mục 6, câu i).
- Lưới cell lục giác R = 100 m, mỗi cell một CL, mỗi cặp cell kề một cặp gateway, cụm tối đa 80 cell, CH có LoRa (mục 2).
- Giãn cách node tối đa để lưới còn liền khoảng 50–60 m; giới hạn do tầm G2G, không do R (mục 10).
- Trên bản đồ thật, lưới là một khối liền; lỗ hổng là cell nước (1–17 %) và cell không có node cắm điện (2–6 %) (mục 20).
- Vị trí node **[chờ]**: gán cell theo kết nối thật ở pha 0; nhãn ngoài trời/trong nhà; kế hoạch dùng toạ độ nhiễu σ = 10 m
  (mục 26).

## 4. Kênh truyền

- A2G hiện tại: hai đoạn + suy hao môi trường cố định, Rician K = 2; R50 = 1016 / 498 / 199 / 99 m; về tầm phủ khớp dải ngoại ô
  tới cao tầng của Al-Hourani, lệch về hình dạng theo góc ngẩng (mục 9).
- G2G hiện tại: 3GPP UMi NLoS (n = 3,5, σ = 7,8 dB, Rayleigh) (mục 9).
- Làm phức tạp dần theo việc K1: K1a LoS A2G theo góc ngẩng hoặc hình học nhà thật; K1b fading tương quan theo thời gian; K1c
  G2G có LoS/NLoS theo nhà (bước đầu: 15 dB mỗi toà **[giả định]**); K1d nhiễu 2,4 GHz (mục 9, 20, 24).
- Thiết bị trong nhà: trừ 15–20 dB với A2G (mục 26).
- Nhiễu: lượt bay chuyển sang kênh 26; ba kênh sạch 15, 20, 25 cho môi trường bận nhất; kênh trùng WiFi có độ bận u = 0, 0,2, 0,5
  **[giả định]**; UAV điều khiển ngoài 2,4 GHz (mục 24).

## 5. Truy vấn và dữ liệu

- Truy vấn là ảnh, khoảng 400 KB, Q = 4 041 gói; mã hoá cho AI node và ký bởi trạm gốc (mục 27).
- Báo thêm theo Q = 400 và 1 000: với truy vấn nhỏ, chặn dưới không hợp tác chỉ 150–320 s và lý thuyết không còn chứng nhận
  lợi thế của hợp tác (mục 27).
- Dữ liệu về AI node theo phương án lai: node có NPU gửi vector mô hình nhẹ (khoảng 0,5 KB mỗi người), node yếu gửi ảnh cắt nhỏ
  (khoảng 5 KB); mỗi AI node giữ K mô hình (K = 1, 3, 5); D0 làm đối chứng (mục 28, 29).
- Luồng nền mỗi AI node 1–2 KB/s (10–20 % thời gian kênh) **[giả định]**; đây là ràng buộc chính của bài chọn critical cell
  (mục 28).
- Không có chuẩn vector người dùng chung (MPEG CDVA loại trừ người và khuôn mặt); số mô hình trong một mạng biết được qua khai
  báo lúc tham gia (mục 29).
- Cửa sổ truy vấn mặc định 2 giờ (quét 1–24 giờ); cửa sổ dài không làm chậm việc tìm nhưng làm giảm độ phân biệt (một ảnh: 0,59
  ở 1 h, 0,38 ở 24 h) (mục 16).
- Bộ nhớ: thẻ SD không chật; giữ ảnh theo thời gian, ưu tiên khung có người; truy vấn được ghim tới khi nhiệm vụ xong (mục 14).
- Camera trả lời "thấy người trông giống mục tiêu": điểm giống kèm thời điểm thấy; trạm gốc xếp hạng theo độ giống và độ mới
  (mục 16).

## 6. Chọn critical cell

- J1 giải bài này: chọn AI node trong node mạnh và giao node thường cho AI node (mục 13).
- Ràng buộc: không quá H chặng, bộ nhớ, luồng nền; không dùng khoảng cách tối thiểu D_min (mục 13, 28).
- Mục tiêu: tối thiểu tổng thời gian pha 1 + pha 2 (mục 13).
- Đánh đổi: ít critical cell thì pha 1 nhẹ nhưng luồng nền và đối sánh nặng; nhiều thì ngược lại (mục 13).

## 7. Pha 0

- Trạm gốc tính sẵn tập critical cell, tour và kế hoạch River ở pha 0, phát trước xuống mọi cell (mục 25).
- Chính sách cập nhật **[chờ]**: dựng đầy đủ một lần; cập nhật nhẹ mỗi đêm; điểm danh trước mỗi nhiệm vụ, chọn lại CL và gateway
  nếu node cũ vắng; mỗi cạnh một cặp gateway dự phòng (mục 23).
- Mạng thay đổi: lưới vẫn liền khi 30 % thiết bị vắng; chỗ yếu là vai trò gắn với node cụ thể (CL, gateway) (mục 23). Tỉ lệ vắng
  0, 10, 20 % là tham số **[giả định]**.

## 8. Pha 1

- Trạm gốc là đội chữa cháy và cứu nạn cứu hộ của khu vực, có sân cất hạ cánh và LoRa gateway (mục 22).
- Một UAV cánh bằng VTOL, 25–50 m/s, bay 100 m so với mặt đất, sức bền 1–3 h (mục 22).
- Vật cản: nhà từ 100 m nới 50 m là vùng cấm cho tour; địa hình cao (đồi) thì bay theo mặt đất (mục 22).
- Vùng cấm bay chính thức là dữ liệu mật; dùng vùng ước theo OSM (sân bay, đất quân sự); nhiệm vụ là bay công vụ (mục 19).
- Giấy phép **[chờ]**: đội cứu nạn có giấy phép thường trực, tiền lệ EU coi UAV cứu nạn là hoạt động nhà nước (mục 30).
- Khởi động: một bản tin LoRa vài byte (mã nhiệm vụ, giờ cất cánh); node cắm điện tự tính cửa sổ chuyển sang kênh 26 (10–15 s
  mỗi cell); đồng bộ đồng hồ mỗi đêm (mục 25).
- Phân phối: CHORD hoặc LM-Tour + River; thêm cây dùng chung và lập kế hoạch cân tải (thử trên một seed: nhanh hơn 26 %) (bản
  thảo J1 mục 9, việc K11).

## 9. Pha 2

- UAV cánh quay, xác minh theo V1: mang bộ tham chiếu R (1 MB) tới node nghi vấn, node đối sánh lại và chỉ báo điểm; lơ lửng gần
  đúng trên node (khu cao tầng: gói qua 0,87 khi lệch 0 m, 0,73 khi lệch 20 m) (mục 17).
- Thứ tự thăm theo xác suất từ pha 1, nên chất lượng pha 1 hiện ra trong thời gian pha 2 (mục 17).
- Pha 2 kết thúc khi V1 xác nhận đúng lần thấy; V4 (UAV tới chỗ thấy lần cuối, nhìn bằng camera của nó) là bước sau (mục 17).

## 10. Ngoài phạm vi và giới hạn

- Nhiều sự cố cùng lúc; node gian lận hay báo sai (mục 6, câu q).
- Camera hành trình và thiết bị di động (mục 6, câu w).
- Thời tiết đưa vào làm cận trên: kịch bản xấu nhất về gió, mưa (mục 6, câu x).
- Nhiều UAV (mục 5).

## 11. Giả định chưa có nguồn trích (cần kiểm trước khi vào bài)

- Luồng nền được dùng 10–20 % thời gian kênh.
- Cỡ ảnh cắt (5–15 KB) và lưu lượng người qua camera (khảo sát ở K12, `K9-PARAMS-vi.md`).
- Tỉ lệ camera có NPU; số mô hình K mỗi AI node.
- Suy hao 15 dB mỗi toà nhà cho G2G; 15–20 dB cho thiết bị trong nhà với A2G.
- Độ bận WiFi u; tỉ lệ thiết bị vắng.
- Sai số vị trí cột đèn; độ lệch đồng hồ thạch anh.
- Dân số Nam Từ Liêm (chưa có số 2019).
- Thời hạn cấp phép bay ở Việt Nam.

## 12. Còn chờ quyết

- Chính sách cập nhật pha 0 (người dùng đang cân nhắc).
- Giấy phép bay thường trực; cách xử lý vị trí node.
- Chạy B8 (phương án lai) của K9.
