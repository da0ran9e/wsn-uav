# Các phần còn lại — keyword

Lời gốc: CLAUDE.md §8 mục 80. [ta] = số thăm dò (cần chạy lại, N ≥ 120).

## 4. Mission Overview
- Pha 0: chia cụm · bầu CH / CL · BS tính đường bay, bảng Axe, River
- Pha 1: đội 1 phát · River lấp thiếu · đối sánh tại critical cell
- phản hồi: critical cell → CH → LoRa → BS
- Pha 2: đội 2 xác minh nghi vấn → về BS
- ba lớp của Pha 1: nhận dạng (hộp đen) · đường bay · **định tuyến mặt đất (bài này)**
- hình tổng quan: bản đồ + đường bay + River + nghi vấn + đội 2

## 6. Mission-Level Policies
- **hướng bay qua CH:** quét 0–178° · đoạn trong cluster dài nhất · dự phòng hướng kế tiếp
- **tour đội 1:** Held–Karp · đường thẳng giữa các cluster · biến thể l3first (ưu tiên cluster tầng 3 dài)
- **LoRa qua CH:** gom kết quả · một bản tin / 40 s
- **đội 2:** đi sớm (nghi vấn đầu tiên) · chọn theo điểm / thời gian · xác minh = hover + tệp lớn + đối sánh

## 7. Evaluation Setup
- ns-3.46 · lr-wpan MAC đầy đủ · binary đóng băng
- bản đồ có hồ · 2 / 4 / 6 / 8 cluster · 10 bản đồ mỗi cỡ [ta] → N ≥ 120
- chỉ số: thời gian critical cell cuối đủ D · số khung · kết thúc nhiệm vụ · tỉ lệ tìm thấy · số lần thăm
- baseline:
  - kéo thẳng (ablation lớp 3)
  - B1 (không pha 1, unicast) · B2 (không pha 1, multicast)
  - B3 / B6 (pha 1 bằng cánh quay)
  - B4 (không hợp tác)
  - B5 (quét luống, chưa làm)
  - B7 (cận dưới lý tưởng)
- bảng tham số (kênh, MAC, UAV, LoRa, tệp)

## 8. Results
1. **lớp 3:** River vs kéo thẳng · thời gian, số khung · theo cluster [ta: −5…−18 % khung]
2. **độ nhạy:** số màu kênh · độ rộng River · số critical cell [ta, 20 lượt]
3. **hợp tác vs không hợp tác:** thời gian ≈ nhau · tỉ lệ tìm thấy khác hẳn [ta: mất 25–62 %] · theo ngưỡng lớp 1
4. **nhiệm vụ vs baseline:** theo cỡ mạng [ta: P nhanh hơn 1,5–3,7 lần] · khoảng cách tới cận dưới
5. **ablation chính sách:** đi sớm (lớn nhất) · theo điểm · l3first (chỉ khi chờ đủ)
6. **minh hoạ:** dòng thời gian một nhiệm vụ

## 9. Discussion and Limitations
- hợp tác mua **độ đầy đủ**, không mua thời gian
- lớp 1 là ngưỡng tạm · tệp lớn 1 MB là số tạm
- chỉ đường thẳng · chưa quét luống · chưa đường cong
- chưa năng lượng · một UAV mỗi đội
- fading không đổi trong gói (A2G lạc quan) · chỉ đô thị
- câu hỏi mở: độ rộng River tối ưu · ghép Circle · Bank với đường cong

## 10. Conclusion
- một lượt bay + River đủ giao truy vấn trọn bộ cho critical cell
- tốc độ đến từ cả kiến trúc nhiệm vụ
- hướng tiếp: mô hình lớp 1 · đường bay theo River (lớp 2) · nhiều UAV · thử nghiệm thực địa
