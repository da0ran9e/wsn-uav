---
status: current
updated: 2026-11-26
---
# J1 · Bối cảnh bài toán, phiên bản rừng và khu bảo tồn (v2)

Bắt đầu lại từ bước bối cảnh theo yêu cầu ở chatlog mục 408: kịch bản chuyển từ đô thị sang vùng thiếu kết nối như rừng quốc gia, khu
bảo tồn. Phiên bản đô thị được đóng gói ở [archive/urban-v1](archive/urban-v1/README.md). File này chốt dần qua thảo luận như lần
trước; mỗi ý ghi trạng thái **chốt**, **đề xuất** hoặc **mở**. Nhãn nguồn: [repo] lấy từ tài liệu trong repo, [web] tra trên internet,
[chung] kiến thức chung chưa đối chiếu nguồn.

## 1. Vì sao đổi kịch bản

Lập luận của bản đô thị có mấy chỗ phản biện dễ hỏi (urban-v1 mục 12, 15):
- Đô thị có sẵn mạng di động và Internet, nên phải giải thích dài vì sao node không gửi qua 4G.
- Ảnh camera trong khu dân cư vướng quyền riêng tư; phải dựng mạng dùng chung kiểu Sidewalk mới có chủ vận hành.
- Nhà cao tầng làm kênh A2G khó mô hình; vùng cấm bay và giấy phép bay trên khu đông người là rào cản lớn.

Ở rừng quốc gia và khu bảo tồn, mấy chỗ này nhẹ đi:
- Lõi rừng thường không có sóng di động, nên LoRa và UAV là đường liên lạc thực tế duy nhất [chung].
- Thiết bị do ban quản lý rừng sở hữu và vận hành; ảnh chủ yếu là động vật, người đi rừng và người xâm nhập [chung].
- Không có nhà cao tầng, ít nhiễu 2,4 GHz, bay ngoài tầm nhìn trên vùng ít người dễ được cấp phép hơn [chung].
- Đã có triển khai thật để dẫn chứng [repo, urban-v1 CONTEXT mục 7–8]:
  - Dryad Silvanet: cảm biến cháy rừng nối mesh, khoảng 1 node mỗi ha;
  - 65 camera bẫy ảnh 4G chạy pin mặt trời trên 34 km² (Kissling 2024);
  - camera bẫy ảnh thông minh gửi qua LoRa rồi Iridium (Gabon);
  - GreenOrbs, mạng TelosB tới 330 node trong rừng (Liu 2013).
- Bản ICC và bản đồ tổng hợp C4 vốn được mô tả là "rừng, camera và cảm biến" [repo, urban-v1 CONTEXT mục 8], nên các kết quả kỹ thuật
  đã có (T\*, River, cân tải, takeover, K9) dùng lại được.

## 2. Mang sang từ phiên bản trước (đề xuất giữ)

- Cơ chế: UAV cánh bằng phát truy vấn một lượt; mạng mặt đất chuyển phần còn thiếu theo kế hoạch tính trước (River, cân tải, cây
  dùng chung); takeover khi UAV lệch đường.
- Cấu trúc ba pha và ba bài toán (P0) chọn AI cell, (P1) pha 1, (P2) pha 2 xác minh (urban-v1 PROBLEMS); mục tiêu phân vị 0,9 của T\*.
- Lý thuyết: Định lý 1 (NP-khó), Định lý 2 (chặn phủ cho cách không hợp tác), chặn một radio cho lớp mặt đất.
- Một UAV ở pha 1; nhiều UAV để sau, khi có cơ chế phối hợp thật.

## 3. Lỗ hổng mới của kịch bản rừng (mở)

1. **Mật độ.** Triển khai thật trong rừng chỉ khoảng 0,01–100 node/km² (camera bẫy ảnh 0,01–1, ô nghiên cứu ForestGEO khoảng 50,
   Dryad 100–120), trong khi bài đang dùng khoảng 820 node/km² [repo, urban-v1 CONTEXT mục 8]. Đây là chỗ phản biện sẽ hỏi đầu tiên.
2. **Kênh qua tán rừng.** Sóng 2,4 GHz suy hao mạnh qua lá và thân cây, cả A2G lẫn G2G [chung, cần nguồn]. Đã có trong repo: tầm A2G
   802.15.4 thực tế khi UAV di chuyển chỉ còn khoảng 1/3 tầm danh định (Bacco 2018), độ cao tốt nhất khoảng 45 m (Nekrasov 2019)
   [repo, `research_notes/literature/2026-11-12/06-deployment.md`].
3. **Năng lượng.** Không có điện lưới; mọi node chạy pin hoặc pin mặt trời. Node phải ngủ phần lớn thời gian, nên đánh thức, ngân
   sách năng lượng cho luồng nền và cho River thành ràng buộc chính. Bản đô thị coi phần lớn node cắm điện.
4. **Loại nhiệm vụ và nội dung truy vấn.** Tìm người đi lạc, phát hiện người săn trộm, nhận dạng một cá thể động vật, hay việc khác.
   Mỗi loại cho truy vấn, dữ liệu nền và tiên nghiệm vị trí khác nhau.
5. **Địa hình.** Đồi núi làm khuất tầm nhìn, UAV phải bay theo độ cao địa hình, cell ở sườn khuất nhận kém.
6. **Quy mô vùng.** Vườn quốc gia thường rộng vài trăm km² [chung], trong khi một chuyến bay ước làm được khoảng 50 cụm, khoảng
   100 km² nếu cụm giống bản đồ k8 [repo, urban-v1 CONTEXT mục 7].
7. **Trạm gốc.** Trạm kiểm lâm ở bìa rừng; quãng bay tới vùng nhiệm vụ dài hơn bản đô thị.

## 4. Câu hỏi cần quyết trước

| Mã | Câu hỏi | Trạng thái |
|---|---|---|
| a | Nhiệm vụ điển hình: tìm người đi lạc, săn trộm, cá thể động vật, hay loại khác | mở |
| b | Thiết bị và mật độ: camera bẫy ảnh thưa cộng cảm biến dày hơn dọc tuyến (đường mòn, suối, ranh giới), hay rải đều; mức mật độ mục tiêu | mở |
| c | Băng tần mặt đất: giữ 802.15.4 2,4 GHz (cell nhỏ, cần mạng dày) hay chuyển sub-GHz (cell lớn, mạng thưa được) | mở |
| d | Vùng mẫu: khu thật nào để cắt bản đồ (ranh giới vườn quốc gia, đường mòn, suối, địa hình) | mở |
| e | Giữ cơ chế và cấu trúc ba pha như mục 2 | đề xuất |
