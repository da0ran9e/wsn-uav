# System Model — keyword

Lời gốc: CLAUDE.md §8 mục 78; lớp 1 và mục tiêu pha 2 cập nhật theo mục 110–114. Số trong ngoặc là giá trị đang dùng trong mô phỏng.

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

## D. Dữ liệu truy vấn (lớp 1: `L1-MODEL-vi.md`, mục 110–114)
- UAV phát liên tục · một gói 99 B / 10 ms (0,5 m)
- bộ manh mối: L = 12 ảnh (2 mặt, 4 dáng, 6 bộ phận) · mỗi ảnh: độ nhận diện r ≈ 1, độ quan trọng w do BS chấm · Q ≈ 400 kB (4 036 gói)
- thứ tự phát xen kẽ khía cạnh · một bản sao trên cửa sổ Q gói Axe quanh CH, lặp lại hai bên
- Seg(a) = đoạn gói phát trên cell Axe a · BS tính trước từ d_track
- yêu cầu: mọi critical cell có đủ bộ manh mối (cửa sổ Q)

## E. Đội bay
- **Đội 1:** cánh bằng · 50 m/s · 100 m · bay qua mỗi cluster một lần · đường thẳng qua CH
- **Đội 2:** cánh quay · 15 m/s · hover · xác minh = ổn định + tệp lớn (1 MB, unicast) + đối sánh
- tour đội 1 tính trước tại BS

## F. Phản hồi và xác minh
- critical cell: điểm hai bước (từng khía cạnh, rồi gộp theo độ quan trọng) · báo điểm cao nhất + bitmap manh mối
- báo hai lần: sau gom nội cell (tự nghe) và sau River · critical cell → CH → LoRa → BS
- BS: điểm → phân phối điểm xác minh → P(cell là c\*), cell chưa báo theo tiên nghiệm
- đội 2: cất cánh cùng đội 1 · thăm mọi critical cell · chọn theo P / (bay + xác minh) · đi khi P ≥ β·P_U (β = 1/4; P_U = xác suất c\* chưa báo), không thì đón đầu về tâm xác suất
- xác minh = ổn định + bộ tham chiếu đầy đủ 1 MB + đối sánh ≈ 78 s · **pha 2 hoàn thành khi xác minh xong c\*** (cell có điểm xác minh cao nhất)

## G. Bài toán
- **Lớp 3:** min thời gian tới khi mọi critical cell có đủ D · phụ: số khung
- **Nhiệm vụ:** min T\*, thời điểm đội 2 xác minh xong c\* (mục 114)
- ràng buộc: một lượt bay · một gateway mỗi cặp cell · lịch lưới · duty cycle LoRa

## H. Giả định / ngoài phạm vi
- chưa xét năng lượng, bộ nhớ, quyền sở hữu, vật cản cứng
- fading không đổi trong một gói (A2G lạc quan)
- lớp 1: mô hình điểm từ cosine của từng ảnh (`L1-MODEL-vi.md`), tham số kịch bản giả định · không mô hình ảnh mục tiêu · đô thị
