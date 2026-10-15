# System Model — keyword

Lời gốc: CLAUDE.md §8 mục 78. Số trong ngoặc là giá trị đang dùng trong mô phỏng.

## A. Mạng mặt đất
- N node không đồng nhất · 3 năng lực: quan sát, tính toán, giao tiếp
- lưới cell lục giác (R = 100 m) · miền không lồi, có hồ
- cluster ≤ 80 cell · CH mỗi cluster (cách biên ≥ 300 m) · CL mỗi cell
- critical cell: cell CH + CL vượt trội toàn cục / cục bộ

## B. Định tuyến và lập lịch nền
- PECEE: next hop về CL, tới mỗi cell kề
- một cặp gateway cho mỗi cặp cell kề · cell path cố định
- kênh theo lưới 7 màu · gateway kênh riêng
- MAC 802.15.4 (CSMA/CA, ACK) · một máy phát mỗi cell, mỗi cặp gateway tại một thời điểm

## C. Kênh truyền
- **A2G:** không gian tự do tới 100 m, sau đó α = 3 · Nakagami m = 1,8 mỗi gói · +10 dBm · −100 dBm
- **G2G:** n = 3,5 · che khuất σ = 7,8 dB (tĩnh) · Rayleigh theo khối 100 ms
- **LoRa:** airtime 0,4 s · duty cycle 1 % → một bản tin / 40 s

## D. Dữ liệu truy vấn
- UAV phát liên tục · một gói 99 B / 10 ms (0,5 m)
- D = tập gói cluster nhận được trong lượt bay
- Seg(a) = đoạn gói phát trên cell Axe a · BS tính trước từ d_track
- yêu cầu: critical cell có đủ D (lớp 1 sẽ thay bằng "đủ lượng")

## E. Đội bay
- **Đội 1:** cánh bằng · 50 m/s · 100 m · bay qua mỗi cluster một lần · đường thẳng qua CH
- **Đội 2:** cánh quay · 15 m/s · hover · xác minh = ổn định + tệp lớn (1 MB, unicast) + đối sánh
- tour đội 1 tính trước tại BS

## F. Phản hồi và xác minh
- critical cell → CH → LoRa → BS
- nghi vấn: 1 thật + 2–3 giả · điểm nghi vấn
- đội 2 xuất phát khi có nghi vấn đầu tiên · xác minh xong cell thật thì về BS

## G. Bài toán
- **Lớp 3:** min thời gian tới khi mọi critical cell có đủ D · phụ: số khung
- **Nhiệm vụ:** min thời điểm đội 2 xác minh cell thật và về BS
- ràng buộc: một lượt bay · một gateway mỗi cặp cell · lịch lưới · duty cycle LoRa

## H. Giả định / ngoài phạm vi
- chưa xét năng lượng, bộ nhớ, quyền sở hữu, vật cản cứng
- fading không đổi trong một gói (A2G lạc quan)
- lớp 1 (nhận dạng) là hộp đen · đô thị
