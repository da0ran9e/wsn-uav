---
status: current
updated: 2026-11-17
---
# J1 · Bối cảnh, thực thể và tham số của bài toán

File mô tả chung cho J1 (chatlog mục 323–327). Đây là bản thử nghiệm, chốt dần qua thảo luận, không sửa đề cương. Phần
phát biểu bài toán tối ưu pha 1 (L1 trong `PLAN-TRACKS-vi.md`) dựa trên file này. Mỗi mục ghi trạng thái: **chốt**
(người dùng đã quyết), **đề xuất** (Claude đề xuất, chờ duyệt), **mở** (còn phải bàn).

## 1. Kịch bản

| Mục | Nội dung | Trạng thái |
|---|---|---|
| Vùng nhiệm vụ | Khu vực địa hình phức tạp (núi, rừng, thung lũng) trong một vườn quốc gia. Vì J1 chỉ xét một UAV, vùng thử nghiệm thu lại vừa đủ cho một UAV làm trong một chuyến bay (mục 327); ước lượng ở mục 7 | chốt |
| Vì sao khó | Địa hình che khuất và tán rừng làm kênh từ trên không xuống yếu và biến động; vùng không có mạng di động | chốt |
| Thiết bị | Nhiều thiết bị IoT có sẵn: camera, cảm biến; phần lớn là node yếu, một số node mạnh chạy được AI | chốt |
| Sự cố | Bất kỳ sự cố nào cần tìm kiếm (người lạc, truy vết đối tượng); mạng phục vụ nhiều lượt truy vấn trong suốt vòng đời | chốt |
| Phân bố thiết bị | Rải ngẫu nhiên, càng đều càng tốt, phủ cả vùng (mục 325). Mật độ tạm giữ như bản hội nghị, xem mục 4 | chốt |
| Vì sao cần UAV | Truy vấn khoảng 400 KB không đẩy được qua LoRa hay phát đa chặng từ trạm gốc trong thời gian chấp nhận được | đề xuất (cần một phép tính thời gian) |

## 2. Thực thể

| Thực thể | Mô tả | Trạng thái |
|---|---|---|
| Trạm gốc (BS) | Lập kế hoạch pha 0, pha 1 (tour và kế hoạch River), nhận kết quả qua LoRa | chốt |
| UAV cánh bằng (đội 1) | J1 xét một UAV phát truy vấn ở pha 1. Nhiều UAV để sau, chỉ khi có cơ chế phối hợp thật (mục 326), xem mục 5 | chốt |
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
| Diện tích vùng | 617 cell ≈ 16 km² (bản đồ k8) | vừa một chuyến bay của một UAV; ước lượng thô khoảng 100 km², cỡ 50 cụm (mục 7) | chốt (nguyên tắc), mở (con số) |
| Số cell | 617 | khoảng 4 000 nếu 100 km² và giữ R = 100 m | mở (giữ R hay tăng R) |
| Mật độ node | khoảng 21 node một cell (13 086 node) | tạm giữ như bản hội nghị; chỉnh dần theo kết quả thực nghiệm, hoặc chạy và công bố kết quả ở vài mức mật độ (mục 326) | chốt (tạm thời) |
| Số CC | 45 CC trên 8 cụm (k8) | theo bài toán chọn CC | mở |
| Kênh A2G | mô hình hai đoạn, thêm suy hao môi trường cố định, Rician K = 2 | thêm che khuất tương quan, fading tương quan, phụ thuộc góc ngẩng (việc K1) | đề xuất |
| UAV cánh bằng | 1 chiếc, 25–50 m/s, H = 100 m, ρ = 63,7 m | vẫn 1 chiếc, giữ động học; thời gian bay tối đa một chuyến và điểm cất hạ cánh còn mở | chốt (1 UAV) |
| Số truy vấn trong vòng đời mạng | 1 | nhiều; dùng để chia chi phí pha 0 | chốt (nhiều), mở (bao nhiêu) |

## 5. Hệ quả của các lựa chọn đã chốt

- Phủ đều ở quy mô vườn quốc gia buộc mật độ node thấp hơn nhiều. Mật độ quyết định số node mỗi cell, nên quyết định xác
  suất nhận ở mức cell P_k và dung lượng giữa các cell. Có thể phải tăng R; R bị chặn bởi tầm G2G để CGW còn nối được.
- Dữ liệu nằm ở AI node nên trước truy vấn đã có luồng nền từ node thường về AI node. Bài toán chọn CC (mục 3) có thêm
  ràng buộc phủ: mỗi node thường cách một AI node không quá h hop, và AI node có giới hạn bộ nhớ. Lập luận "bộ nhớ đầy
  thì dữ liệu bị ghi đè" đặt ở AI node.
- Một UAV vẫn là bài toán chính (mục 326): chia vùng cho từng UAV rồi mỗi chiếc bay một tour (Dubins mTSP min-max) là
  cách làm thông thường, không giải quyết điểm khó vốn nằm ở bài một UAV. Khi bàn tới nhiều UAV, mục tiêu vẫn là min-max
  (thời điểm AI node cuối cùng sẵn sàng), và các UAV phải phối hợp với nhau chứ không chia phần việc. Tài liệu chia việc
  trong Drive (Rathinam 2007, Sensors 23:6432, Xu–Liang–Lin 2015) chỉ dùng làm baseline khi đó.

## 6. Câu hỏi mở

- a. Giữ R = 100 m hay tăng R? (mật độ đã trả lời ở mục 326: tạm giữ, thử vài mức)
- b. Đã trả lời (mục 327): một chuyến bay, vùng thu lại cho vừa. Còn mở: chọn sức bền bao nhiêu (mục 7 gợi ý 1,5 h).
- c. Đã trả lời (mục 326): một UAV; nhiều UAV để sau, mục tiêu min-max, phối hợp chứ không chia việc.
- d. Mục tiêu tìm kiếm điển hình là gì (người lạc, động vật, đối tượng)? Câu trả lời quyết định mỗi phút chậm trễ đáng
  giá bao nhiêu.
- e. Vì sao không phát truy vấn từ trạm gốc qua mạng mặt đất (đa chặng 802.15.4) hay qua LoRa: cần một phép tính thời
  gian để đưa vào bài.
- f. Số sự cố trong vòng đời mạng (để chia chi phí pha 0).
- g. Môi trường như bài giả định có thật không, mỗi cụm thường rộng bao nhiêu (mục 327), mật độ node thường gặp (mục 329).
  Đối chiếu ở mục 7 và 8.

## 7. Đối chiếu với triển khai thật (2026-11-17, tra nhanh trên web, số của nhà sản xuất chưa kiểm độc lập)

Mật độ và cụm của bài: bản đồ k8 có 13 086 node trên 617 cell (≈ 16 km²), tức khoảng 820 node mỗi km² hay một node trên
0,12 ha; 8 cụm, mỗi cụm khoảng 77 cell ≈ 2 km² và 1 600 node.

| Hệ thống thật | Mật độ, khoảng cách | Đơn vị giống "cụm" | Kết nối lên trên | Nguồn |
|---|---|---|---|---|
| Dryad Silvanet (cảm biến cháy rừng, mesh) | khoảng 1 node mỗi ha (100 node/km²), cách nhau tới 300 m; thí điểm Lebanon 91 node trên 78 ha | mesh gateway phục vụ khoảng 100 node (≈ 1 km²); 20 mesh gateway mỗi border gateway | LoRa mesh 2–10 km giữa các gateway | dryad.net (datasheet Mesh Gateway, Wildfire Sensor) |
| GreenOrbs (WSN rừng, Trung Quốc) | tới 330 node trong rừng | — | — | Liu et al., IEEE TPDS 2013 |
| Lưới camera bẫy ảnh | 1 camera/km² (cảnh quan), 50/km² (ô nghiên cứu ForestGEO, cách 140 m), 1 camera/2 km² (TEAM), 1 camera/100 km² (Parks Canada) | — | phần lớn không nối mạng; Natura 2000 Hà Lan có 65 camera 4G cách 1 km | Apostle Islands (arXiv 1703.10726), LJMU 2024 |
| Camera AI tại biên (TrailGuard AI, Instant Detect 2.0) | không tìm thấy số lượng triển khai | một gateway LoRa gom nhiều camera rồi lên vệ tinh | LoRa, Iridium hoặc 4G | resolve.ngo, zsl.org |
| UAV cánh bằng VTOL loại nhỏ | sức bền 1–3 h, bay 60–75 km/h, 100–200 km mỗi chuyến | — | — | trang sản phẩm JOUAV CW-15, YANGDA Mapird |

Nhận xét:
- Kiến trúc của bài (cell có CL, cụm có CH nối LoRa lên trạm) có bản tương ứng thật ở Dryad: một gateway gom khoảng 100
  node trên chừng 1 km², gateway nối nhau bằng LoRa vài km. Cụm 1–2 km² vì vậy là cỡ hợp lý cho "vùng một gateway phục
  vụ".
- Mật độ của bài cao hơn Dryad khoảng 8 lần và cao hơn mọi lưới camera rất nhiều. Tôi chưa tìm thấy triển khai thật nào
  vừa dày cỡ 800 node/km² vừa có camera nối mesh 802.15.4. Kịch bản của bài vì vậy là giả định hướng tới, cần lập luận
  trong bài (node rẻ dày đặc cộng một ít camera AI), hoặc chạy thêm mức mật độ kiểu Dryad.
- Ở mật độ Dryad (1 node/ha), cell R = 100 m chỉ còn khoảng 2–3 node, quá ít cho P_k và cho cặp gateway. Muốn giữ
  khoảng 20 node một cell thì R phải lên khoảng 250–300 m, mà tầm G2G 2,4 GHz trong rừng ngắn hơn thế; Dryad dùng băng
  sub-GHz. Đây là chỗ câu hỏi a (giữ hay tăng R) dính với mật độ và băng tần.
- Tài liệu sẵn trong repo (`research_notes/literature/2026-11-12/06-deployment.md`) bổ sung: camera bẫy ảnh thông minh
  gửi qua LoRa rồi Iridium (Gabon) và camera phân loại loài tại biên gửi qua LoRaWAN (Computers 2022) là tiền lệ thật cho
  camera AI nối mạng trong rừng; tầm A2G 802.15.4 thực tế khi UAV di chuyển chỉ còn khoảng 1/3 tầm danh định (Bacco 2018)
  và độ cao tốt nhất khoảng 45 m (Nekrasov 2019). Repo chưa có tài liệu nào về mật độ node của triển khai thật.
- Sức bền một chuyến: tour k8 dài 30,3 km cho 8 cụm, bay khoảng 760 s. Với 1,5 h bay (trừ quãng về) thì một UAV làm được
  cỡ 50 cụm, khoảng 100 km², nếu các cụm giống k8. Đây là ngoại suy tuyến tính, chưa chạy bộ lập tour để kiểm.

## 8. Mật độ node trong triển khai thật (2026-11-17, mục 329)

Repo chưa có tài liệu nào về mật độ triển khai, nên mọi số dưới đây lấy từ internet (đoạn trích tìm kiếm, chưa đọc toàn
văn). Mật độ do tôi chia số node cho diện tích nêu trong nguồn. Để so: bài dùng khoảng 820 node/km² (21 node một cell
R = 100 m, diện tích cell 0,026 km²).

| Triển khai | Loại | Số node, diện tích | Mật độ (node/km²) | Nguồn |
|---|---|---|---|---|
| Ô vườn táo Trentino | nông nghiệp, ô nhỏ | 27 điểm đo trên 0,5 ha | khoảng 5 400 | sites.unipa.it (CSBE 2010) |
| ExScal (Florida, 2004) | quân sự, phát hiện xâm nhập, chạy ngắn ngày | hơn 1 000 node trên 1,3 km × 0,3 km | khoảng 2 600 | Arora et al., Computer Networks 2005 |
| SmartSantander (lõi, giai đoạn thí điểm) | đô thị | hơn 10 000 node dự kiến trên 6 km² | khoảng 1 700 | rcrwireless.com |
| **Bài này (k8)** | rừng, camera và cảm biến | 13 086 node trên 16 km² | **khoảng 820** | — |
| SmartSantander (toàn thành phố) | đô thị | 15 000–20 000 node trên khoảng 35 km² | 430–570 | telecomstechnews.com, nesta.org.uk |
| Camera CCTV, thành phố dày nhất | đô thị, camera công cộng | 573,8 camera mỗi dặm vuông | khoảng 220 | comparitech.com |
| Dryad Silvanet | rừng, cảm biến cháy | 1 node mỗi ha; thí điểm 91 node trên 78 ha | 100–120 | dryad.net |
| Ô ForestGEO | rừng, camera bẫy ảnh, ô nghiên cứu | 49–50 camera trên 1 km² | khoảng 50 | LJMU 2024 |
| CitySee (Vô Tích) | đô thị, CO₂ | khoảng 1 200 node trên khoảng 100 km² | khoảng 12 | Mao et al., INFOCOM 2012 |
| Lưới camera bẫy ảnh cảnh quan | rừng | 1 camera mỗi km² (TEAM: 1 mỗi 2 km²; Parks Canada: 1 mỗi 100 km²) | 0,01–1 | Apostle Islands, Parks Canada |
| Yêu cầu mMTC của IMT-2020 | chỉ tiêu dung lượng, không phải triển khai | 10⁶ thiết bị mỗi km² | 1 000 000 | ITU-R M.2410 |

Thêm: một khảo sát triển khai WSN quan trắc môi trường ghi 80 % số triển khai có không quá 50 node; PermaSense mỗi điểm
khoảng 20 node; GreenOrbs tới 330 node trong rừng (không rõ diện tích).

Nhận xét:
- Triển khai dài hạn trên diện rộng ngoài trời nằm trong khoảng 10–600 node/km². Trên 1 000 node/km² chỉ gặp ở ô nhỏ
  vài ha hoặc thử nghiệm quân sự ngắn ngày.
- Mật độ 820 node/km² của bài nằm ở đầu trên: ngang mức trung bình một thành phố thông minh dày (SmartSantander), gấp
  khoảng 8 lần mạng cảm biến rừng thương mại (Dryad), gấp khoảng 4 lần thành phố có nhiều CCTV nhất, và gấp hàng trăm lần
  lưới camera bẫy ảnh trong rừng.
- Ứng với cell R = 100 m: 820 node/km² cho khoảng 21 node một cell, 400 cho khoảng 10, 100 cho khoảng 2–3.
- Đề xuất ba mức để chạy và báo cáo: khoảng 820 (mức ICC), khoảng 400 (kiểu SmartSantander) và khoảng 100 (kiểu Dryad).
  Mức 100 cần quyết thêm chuyện R và băng tần (mục 7).
