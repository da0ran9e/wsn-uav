# Introduction — keyword

Lời gốc: CLAUDE.md §8 mục 75–76. [ta] = số của ta (cần chạy lại, N ≥ 120). [tr] = cần trích.

1. **Bối cảnh:** camera IoT đô thị dày đặc · nhiều chủ · bằng chứng đã ghi sẵn · không biết tìm ai · bộ nhớ ghi đè → chạy đua thời gian
2. **Không kéo dữ liệu về:** LoRa/vệ tinh vài trăm B/h · pháp lý, quyền riêng tư [tr] → đưa truy vấn xuống biên · đối sánh tại chỗ · báo về vài byte
3. **UAV và một lượt bay:**
   - cánh bằng: nhanh, không hover, bay qua một lần
   - cánh quay: chậm, tầm ngắn
   - xa đường bay → gói rời rạc, thiếu trọn bộ
   - chuỗi liên tục 850 / 245 / 50 / 14 ở 0 / 300 / 600 / 900 m [ta, A2G-RUN]
4. **Hợp tác mặt đất:**
   - hàng xóm bù cho nhau [tr: gossip, D2D, network coding]
   - nhưng 802.15.4 nhiều hop chậm, hop yếu nhất quyết định [ta, G2G-CHAIN]
   - **khoảng trống:** công trình trước bỏ qua đường bay biết trước
5. **Nhận xét then chốt:** đường bay biết trước → biết cell nào giữ đoạn nào → hợp tác lập kế hoạch trước → **River** (Axe · Bank · critical cell · Circle)
6. **Đóng góp:**
   - kiến trúc ba pha (lớp 3 của Pha 1)
   - River
   - chính sách nhiệm vụ (hướng bay qua CH · báo hai lần qua LoRa · đội 2 cất cánh cùng đội 1, đón đầu, thăm theo xác suất)
   - ns-3 với MAC 802.15.4 đầy đủ, so với các baseline
7. **Kết quả:**
   - hợp tác làm xếp hạng đúng hơn: T\* nhanh hơn không hợp tác 26–68 s [ta, mô hình lớp 1 mới]
   - cả kiến trúc nhanh hơn 1,9–2,8 lần so với UAV cánh quay tốt nhất [ta]
   - River ít khung hơn kéo thẳng 5–18 % [ta]
8. **Bố cục bài**
