# Related Work — keyword

Lời gốc: CLAUDE.md §8 mục 77. Mỗi nhóm ghi: chủ đề · điểm khác biệt của ta. [tr] = cần tìm tài liệu cụ thể.

1. **UAV giao / thu dữ liệu cho WSN** [tr]
   - data ferrying · UAV-aided dissemination · data mule
   - khác ta: giả định hover, quay lại, hoặc phủ dày
2. **UAV broadcast / multicast, mã fountain** [tr]
   - phát quảng bá từ trên không · LT/Raptor · thiết kế đường bay cho multicast
   - khác ta: một lượt, không phát lại, không có phản hồi
3. **Lập đường bay UAV** [tr]
   - coverage path planning (quét luống) · TSP / Dubins TSP · miền không lồi
   - khác ta: đường bay chỉ là đầu vào; ta lập kế hoạch hợp tác *theo* đường bay
4. **Hợp tác mặt đất, D2D, gossip** [tr]
   - epidemic / gossip · D2D caching · network coding trong WSN · bù gói theo vùng lân cận
   - khác ta: không lập kế hoạch trước, không biết ai giữ gì
5. **Phân cụm, định tuyến theo cell, lập lịch kênh** [tr]
   - PECEE elastic clustering (công trình trước của nhóm) · TSCH / 6TiSCH · tô màu kênh dạng lưới
   - ta dùng làm nền: CL, CH, một cặp gateway mỗi cặp cell, lưới 7 màu
6. **Phân tích tại biên, truy vết phân tán** [tr]
   - edge video analytics · query-by-example · tìm người trên mạng camera · bảo vệ quyền riêng tư
   - khác ta: giả định có băng rộng hoặc đám mây
7. **Tìm kiếm và xác minh bằng đội UAV** [tr]
   - SAR · search theory · nhiều UAV phân vai
   - liên hệ: Pha 2 của ta (đi sớm, thăm theo điểm nghi vấn)
8. **Kênh truyền** [tr]
   - A2G (Qiu 2017, α 2,6–3,35) · G2G cận mặt đất, che khuất · LoRa duty cycle
   - dùng làm mô hình, không phải đóng góp

**Định vị bài (1 câu):** chưa có công trình nào lập kế hoạch hợp tác mặt đất từ một đường bay biết trước, để bù cho một lượt phát duy nhất.
