---
status: current
updated: 2026-11-20
---
# J1 · Bối cảnh, thực thể và tham số của bài toán

File mô tả chung cho J1 (chatlog mục 323–338). Đây là bản thử nghiệm, chốt dần qua thảo luận, không sửa đề cương. Phần
phát biểu bài toán tối ưu pha 1 (L1 trong `PLAN-TRACKS-vi.md`) dựa trên file này. Mỗi mục ghi trạng thái: **chốt**
(người dùng đã quyết), **đề xuất** (Claude đề xuất, chờ duyệt), **mở** (còn phải bàn).

## 1. Kịch bản

| Mục | Nội dung | Trạng thái |
|---|---|---|
| Vùng nhiệm vụ | Đô thị hiện đại (mục 338): càng hiện đại thì mạng IoT càng dày, nhưng nhà cao tầng và hạ tầng làm kênh A2G kém đi nhiều. Kênh là phần sẽ làm phức tạp dần. Vì J1 chỉ xét một UAV, vùng thử nghiệm thu lại vừa đủ cho một UAV làm trong một chuyến bay (mục 327) | chốt |
| Vì sao khó | Nhà cao tầng và hạ tầng che khuất kênh từ trên không xuống, nên kênh yếu và biến động; đô thị càng hiện đại thì càng dày node nhưng kênh A2G càng kém (mục 338) | chốt |
| Thiết bị | Chuông cửa, camera tường, camera cột, máy bán hàng; thêm node chuyển tiếp trên cột đèn ở cell cần; 11–22 % chạy pin và không chuyển tiếp; một số node mạnh chạy được AI (mục 15, 20–21) | chốt |
| Sự cố | Mục tiêu điển hình là tìm người (mục 335): truy vấn là bộ ảnh tham chiếu của người cần tìm, AI node đối sánh với ảnh camera đã gửi về; mạng phục vụ nhiều lượt truy vấn trong suốt vòng đời | chốt |
| Phân bố thiết bị | Rải ngẫu nhiên, càng đều càng tốt, phủ cả vùng (mục 325). Mật độ giữ như bản hội nghị (khoảng 816 node/km²) như giả định hướng tới: mạng dày chưa phổ biến nhưng nhiều khả năng sớm có (mục 335); chạy thêm vài mức để xem độ nhạy | chốt |
| Vì sao cần UAV | Hai lý do (mục 343): node rẻ chỉ có radio 802.15.4, không nối Internet; dữ liệu phải ở lại thiết bị vì quyền riêng tư, chỉ điểm số vài byte rời node. Qua LoRa mất ít nhất 1,8 h, qua mạng mặt đất từ trạm gốc xem mục 12. Chi tiết ở mục 15 | chốt (lý do), đề xuất (lập luận) |

## 2. Thực thể

| Thực thể | Mô tả | Trạng thái |
|---|---|---|
| Trạm gốc (BS) | Đội chữa cháy và cứu nạn cứu hộ của khu vực, có LoRa gateway và sân cất hạ cánh (mục 22); lập kế hoạch pha 0, pha 1, nhận kết quả qua LoRa | chốt |
| UAV cánh bằng (đội 1) | J1 xét một UAV phát truy vấn ở pha 1. Nhiều UAV để sau, chỉ khi có cơ chế phối hợp thật (mục 326), xem mục 5 | chốt |
| UAV cánh quay (đội 2) | Đến xác minh các cell nghi vấn ở pha 2. J1 xét cả pha 2: mục tiêu chung là tối thiểu tổng thời gian pha 1 và pha 2 (mục 338). Mô hình pha 2 hiện có: `uav-l2/docs/MISSION-vi.md` (15 m/s, tour qua các nghi vấn, lơ lửng 30 s mỗi điểm) | chốt |
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
maximum coverage (cần tra cứu thêm). **Trạng thái:** chốt (cách hiểu; J1 giải luôn bài này, mục 335), đề xuất (phát biểu ở
mục 13).

## 4. Tham số

Các tham số vô tuyến, kênh và UAV đã có ở `params.yaml` (bảng ở `paper/PARAMS-vi.md`), kèm nguồn và nhãn. File này chỉ
ghi tham số của kịch bản mới và chỗ phải đổi.

| Tham số | Bản hội nghị (ICC) | J1 | Trạng thái |
|---|---|---|---|
| Diện tích vùng | 617 cell ≈ 16 km² (bản đồ k8) | một quận đô thị thật 5–60 km², nằm gọn trong một chuyến bay (mục 18–22); bộ bản đồ đề xuất Nam Từ Liêm, Hoàng Mai, Punggol, Downtown Core | chốt |
| Số cell | 617 | 195–1 552 cell tuỳ quận (R = 100 m, mục 10, 18–20) | chốt |
| Mật độ node | khoảng 21 node một cell (13 086 node) | giữ khoảng 816 node/km² làm mức chính (hướng tới, mục 335); thêm 400 và 280 node/km² để xem độ nhạy (vẫn trong vùng lưới cell liên thông, mục 10) | chốt (mức chính), đề xuất (mức phụ) |
| Số CC | 45 CC trên 8 cụm (k8), cho sẵn theo bản đồ | J1 giải bài chọn CC (mục 335), số CC là một phần lời giải | chốt |
| Kênh A2G, G2G | A2G hai đoạn + suy hao môi trường cố định, Rician K = 2; G2G 3GPP UMi NLoS | làm phức tạp dần theo từng bước (mục 335): LoS phụ thuộc góc ngẩng, che khuất tương quan, fading tương quan, cấu trúc phố hay địa hình cho G2G (mục 9; việc K1) | chốt (hướng), đề xuất (thứ tự bước) |
| UAV cánh bằng | 1 chiếc, 25–50 m/s, H = 100 m, ρ = 63,7 m | 1 chiếc VTOL, giữ động học, bay 100 m so với mặt đất, cất cánh từ đội cứu nạn cứu hộ, sức bền 1–3 h (mục 22) | chốt |
| Số truy vấn trong vòng đời mạng | 1 | vài chục tới khoảng 150 báo cáo mất tích mỗi năm mỗi quận, một phần cần UAV (mục 23) | chốt (ước lượng) |

## 5. Hệ quả của các lựa chọn đã chốt

- (Cũ, đã thay bởi mục 338.) Ý ban đầu về vườn quốc gia mật độ thấp không còn dùng; kịch bản là đô thị hiện đại mật độ cao,
  giới hạn giãn cách node do tầm G2G quyết định (mục 10).
- Dữ liệu nằm ở AI node nên trước truy vấn đã có luồng nền từ node thường về AI node. Bài toán chọn CC (mục 3) có thêm
  ràng buộc phủ: mỗi node thường cách một AI node không quá h hop, và AI node có giới hạn bộ nhớ. Lập luận "bộ nhớ đầy
  thì dữ liệu bị ghi đè" đặt ở AI node.
- Một UAV vẫn là bài toán chính (mục 326): chia vùng cho từng UAV rồi mỗi chiếc bay một tour (Dubins mTSP min-max) là
  cách làm thông thường, không giải quyết điểm khó vốn nằm ở bài một UAV. Khi bàn tới nhiều UAV, mục tiêu vẫn là min-max
  (thời điểm AI node cuối cùng sẵn sàng), và các UAV phải phối hợp với nhau chứ không chia phần việc. Tài liệu chia việc
  trong Drive (Rathinam 2007, Sensors 23:6432, Xu–Liang–Lin 2015) chỉ dùng làm baseline khi đó.

## 6. Câu hỏi mở

- a. Giữ R = 100 m: mục 10 cho thấy giới hạn giãn cách do tầm G2G quyết định, không do R; mật độ chính giữ như bản hội
  nghị (mục 335).
- b. Đã trả lời (mục 327): một chuyến bay, vùng thu lại cho vừa. Còn mở: chọn sức bền bao nhiêu (mục 7 gợi ý 1,5 h).
- c. Đã trả lời (mục 326): một UAV; nhiều UAV để sau, mục tiêu min-max, phối hợp chứ không chia việc.
- d. Đã trả lời (mục 335): tìm người.
- e. Vì sao không phát truy vấn từ trạm gốc qua mạng mặt đất hay qua LoRa: phép tính ở mục 12 (mục 334). Còn mở: cách
  bài đối đáp với kiểu flood đồng bộ (Pando).
- f. Số sự cố trong vòng đời mạng: ước lượng ở mục 23 (mục 359).
- g. Môi trường như bài giả định có thật không, mỗi cụm thường rộng bao nhiêu (mục 327), mật độ node thường gặp (mục 329),
  kích thước vùng đô thị và kênh có hợp với đô thị không (mục 332), pháp lý UAV đô thị và giãn cách node
  tối đa (mục 333). Đối chiếu ở mục 7–11.
- h. Đã trả lời (mục 343): hướng 1 (node chỉ có 802.15.4) và hướng 4 (giữ dữ liệu tại chỗ). Lập luận ở mục 15.
- i. Đã trả lời (mục 364): mạng dùng chung kiểu Sidewalk, thành phố hoặc nhà cung cấp chạy pha 0.
- j. Phần lớn đã trả lời (mục 344): không giới hạn thời gian, tìm tới khi thấy (chỉ bị chặn bởi năng lượng UAV); camera
  trả lời "thấy người trông giống mục tiêu". Cửa sổ mặc định 2 giờ (mục 345).
- k. Đã trả lời (mục 347, 349): V1 và V4; pha 2 của bài kết thúc khi V1 xác nhận đúng lần thấy, V4 là bước sau (mục 17).
- l. (mục 342) Vận hành UAV ở đô thị: điểm cất cánh, độ cao bay khi có nhà cao hơn 100–120 m, vùng cấm bay, sức bền.
- m. Đã trả lời (mục 364): 45 % node trên nhà chạy pin (11–22 % tổng số node), không chuyển tiếp; năng lượng chỉ ràng buộc
  ở node pin.
- n. (mục 349) Trạm gốc ở đâu: trong đô thị (đồn công an, trạm cứu hoả) hay ngoài rìa như bản đồ k8 (cách cell gần nhất
  1 km); quyết định quãng bay của cả hai pha.
- o. Đã trả lời (mục 350–358): bản đồ thật từ OSM, 12 khu, bộ đề xuất bốn khu; quy tắc đặt node, cột đèn theo nhu cầu, node lá
  (mục 18–21, việc K14).
- p. Mạng thay đổi theo thời gian: thử nghiệm và đề xuất ở mục 23 (mục 359).
- q. Đã trả lời (mục 364): nhiều sự cố cùng lúc và node gian lận để ngoài J1, nêu ở phần giới hạn.
- r. Đã trả lời (mục 367, mục 25). Ghi chú gốc: đánh thức: node chạy pin ngủ phần lớn thời gian, sự cố đến bất ngờ; node phải thức đúng lúc UAV bay qua và lúc
  River chạy. Đề cương ND0 đã nêu cơ chế đánh thức theo lịch bay do trạm gốc phát.
- s. Đã trả lời (mục 365, việc K1d, mục 24). Ghi chú gốc: nhiễu 2,4 GHz ở đô thị: WiFi, Bluetooth, chính radio điều khiển của UAV (ghi chú `papers/dargie2021-lqe.md`: PRR theo
  kênh 0,13–1,0). Mô hình hiện không có nhiễu ngoài.
- t. (mục 363) Vị trí node: trạm gốc cần toạ độ node để lập kế hoạch và chọn điểm lơ lửng V1; lấy từ địa chỉ lắp đặt, GPS hay
  định vị trong mạng, và sai số bao nhiêu.
- u. (mục 369) Nội dung và cỡ truy vấn: truy vấn là ảnh (400 KB, Q = 4 041 gói) hay vector đặc trưng (vài chục KB); ảnh cần khi
  thiết bị chạy mô hình khác nhau, vector cần khi mọi AI node dùng chung mô hình. Truy vấn chứa ảnh của người cần tìm, nên có
  cần mã hoá để chỉ AI node đọc được, và cần ký để node biết truy vấn thật do trạm gốc phát.
- v. (mục 369) Giấy phép bay: bay công vụ vẫn phải xin phép; nếu xin theo từng lần thì thời gian chờ có thể lớn hơn cả nhiệm
  vụ. Đề xuất giả định đội cứu nạn có giấy phép thường trực cho vùng của mình.
- w. (mục 369) Thiết bị di động: camera hành trình, điện thoại (đề cương mục 2.1 có nhắc) có thuộc mạng không; đề xuất chỉ xét
  thiết bị cố định.
- x. (mục 369) Ban đêm và thời tiết: camera hồng ngoại ban đêm làm đối sánh kém; mưa và gió ảnh hưởng UAV (đã có thí nghiệm gió
  WND); có cần xét không.
- y. (mục 369) Phương án dữ liệu gửi về AI node (D0–D3, mục 14, PLAN-K9-DATA) chưa chọn.

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

## 9. Nếu đặt kịch bản ở đô thị: kích thước và kênh (2026-11-17, mục 332)

Nguồn ghi ở từng ý: [repo] là tài liệu hoặc log đã có trong repo, [web] là tra mới hôm nay.

**Kích thước.** SmartSantander trải khoảng 35 km², lõi thí điểm 6 km² chia 22 vùng, mỗi vùng một gateway đặt trên cao,
tức khoảng 0,27 km² mỗi vùng; khoảng 2 000 thiết bị 802.15.4, chừng 90 thiết bị mỗi gateway [web]. CitySee trải khoảng
100 km² [web]. Bản đồ k8 (16 km², 8 cụm khoảng 2 km²) vừa cỡ một quận hay một thành phố nhỏ. Cụm đô thị thật nhỏ hơn
cụm của bài khoảng 7 lần về diện tích, còn số node mỗi gateway (90–100) gần với Dryad.

**Độ cao bay.** H = 100 m nằm dưới giới hạn 120 m của EU và Mỹ (kiến thức chung, chưa trích nguồn). Khu cao tầng trên
100 m thì không bay được ở độ cao này. UAV cánh bằng bay BVLOS trên khu đông người là rào cản pháp lý lớn; đô thị thường
dùng cánh quay.

**Kênh A2G.** Mô hình đang dùng: không gian tự do tới 100 m, sau đó số mũ 3, Rician K = 2 bốc lại mỗi gói, cộng suy hao
môi trường cố định η = 0 / 9,03 / 19,77 / 25,74 dB cho R50 = 1016 / 498 / 199 / 99 m [repo: `logs/2026-10-25_0330-env-modes/`].
Mô hình đô thị Al-Hourani 2014 (xác suất LoS theo góc ngẩng) cho R50 ≈ 660 m (ngoại ô), 350–360 m (đô thị), 235–245 m
(đô thị dày), 45 m (cao tầng) [repo: `logs/2026-10-24_1056-a2g-radius/`, tính lại hôm nay ra cùng số]. Vậy về tầm phủ, bốn
chế độ của bài trải đúng dải ngoại ô tới giữa đô thị dày và cao tầng. Lệch nằm ở hình dạng [repo: `04-a2g-channel.md`
mục 1]:
- η cố định không phụ thuộc góc ngẩng. Ở đô thị, gần thiên đỉnh gần như luôn LoS (P_LoS ≈ 0,97 ở cự ly ngang 100 m), xa
  hơn thì chủ yếu NLoS (0,12 ở 500 m), nên đường p(d) thật dốc hơn: mô hình bi quan gần UAV, lạc quan ở xa.
- Trạng thái LoS/NLoS phải nhất quán theo không gian cho từng node dọc lượt bay; hiện fading bốc độc lập mỗi gói.
- Thiếu shadowing log-normal (đo ở A2G đô thị σ ≈ 2,8–5,4 dB). K = 2 bi quan cho LoS (đo 12–29 dB), lạc quan cho NLoS.

**Kênh G2G.** Mô hình đang dùng là 3GPP TR 38.901 UMi NLoS (35,3 log₁₀ d, σ = 7,8 dB cố định mỗi cặp, Rayleigh theo khối
100 ms) [repo: `params.yaml` C7–C10], tức vốn là mô hình phố đô thị, hợp với đô thị hơn hợp với rừng. Không tính shadowing,
xác suất qua một liên kết là 0,93 ở 50 m, 0,75 ở 75 m, 0,45 ở 100 m (tính hôm nay). Số mũ đo ở phố 2,4 GHz nằm trong
khoảng 2–5 tuỳ hình dạng phố [web]. Các chỗ chưa khớp:
- UMi viết cho trạm cao 10 m tới máy 1,5 m; 3GPP dùng lại cho D2D ở 1,5 m nhưng chính các tài liệu D2D ghi rằng kênh đối
  xứng máy–máy không hợp với mô hình bất đối xứng này [web].
- Không có trạng thái LoS: hai node cùng một phố có LoS (UMi LoS khoảng 22 log₁₀ d, tầm xa hơn nhiều), còn hai node cách
  một dãy nhà gần như không nối được. Mô hình hiện coi mọi cặp như nhau cộng nhiễu σ độc lập [repo: C11 che khuất độc lập].
- Liên thông thật đi theo lưới phố. Lưới cell lục giác R = 100 m với cặp gateway giữa mọi cell kề có thể gãy ở chỗ hai
  cell bị khối nhà ngăn.
- SmartSantander đặt repeater và gateway trên cột đèn, đèn tín hiệu [web]; node đặt cao 3–6 m có kênh tốt hơn node sát đất.
- Ghi chú bài báo vừa thêm (session khác, cùng ngày) bổ sung [repo: `papers/sanchez2014-smartsantander.md`,
  `papers/liu2013-greenorbs.md`]: node SmartSantander gắn cột đèn dùng hai module XBee-Pro 2,4 GHz, node dồn dày nhất ở
  vùng trung tâm khoảng 1 km² (tr. 10); ở GreenOrbs dưới 10 % số node gánh 80 % lưu lượng (tr. 8), cùng loại với nút cổ
  chai ở cell Bank mà trace River cho thấy.

## 10. Mật độ node và lưới cell G2G (2026-11-17, mục 333)

Tính Monte Carlo trên đúng kênh G2G của mô phỏng (10 dBm, số mũ 3,5, che khuất 7,8 dB mỗi cặp, Rayleigh; liên kết dùng được
khi q ≥ 0,5, tốt khi q ≥ 0,9), cell R = 100 m, một cell giữa và 6 cell kề, 400 lần bốc. Script
`paper/j1/analysis/g2g_density.py`, log `logs/2026-11-17_1500-g2g-density/`.

| Giãn cách s | node/km² | node/cell | cell rỗng | cell liên thông không cần cầu | cặp cell kề có gateway dùng được / tốt | q gateway tốt nhất (trung vị) |
|---|---|---|---|---|---|---|
| 20 m | 2 500 | 65 | 0 % | 100 % | 100 % / 100 % | 1,000 |
| 35 m (bài) | 816 | 21 | 0 % | 100 % | 100 % / 100 % | 0,998 |
| 50 m | 400 | 10 | 0 % | 98 % | 99,8 % / 93 % | 0,987 |
| 60 m | 278 | 7 | 0 % | 90 % | 98 % / 77 % | 0,967 |
| 70 m | 204 | 5 | 0 % | 84 % | 90 % / 58 % | 0,928 |
| 85 m | 138 | 3,6 | 3,5 % | 74 % | 70 % / 35 % | 0,817 |
| 100 m | 100 | 2,6 | 5,8 % | 72 % | 53 % / 22 % | 0,679 |

Nhận xét:
- Giãn cách tối đa để lưới cell còn nguyên là khoảng 50–60 m (280–400 node/km², 7–10 node một cell). Từ 70 m, 10 % cặp
  cell kề không còn gateway dùng được; từ 85 m lưới vỡ rõ. Bản ROUTING của uav-coop (tầm hình học 50 m) cũng thấy ở
  giãn cách 50 m phải thêm 375 liên kết bắc cầu, 20 cầu dài hơn 100 m [repo: `uav-coop/docs/ROUTING-vi.md`].
- Giới hạn này do tầm G2G quyết định (liên kết dùng được tới khoảng 96 m khi không có che khuất), không do R. Tăng R chỉ
  thêm node vào cell, không làm hai node cách 100 m nối được nhau. Mức kiểu Dryad (100 node/km²) vì vậy không chạy được
  với radio 2,4 GHz 10 dBm hiện tại dù tăng R; phải đổi radio (sub-GHz, công suất cao hơn) hoặc mô hình kênh.
- Khi lưới còn liên thông, chi phí truyền trong cell gần như không đổi theo mật độ: hop trung vị 56–63 m, ETX khoảng 1,9
  mỗi 100 m ở mọi giãn cách. Mật độ cao hơn chỉ thêm lựa chọn cặp gateway (q tốt nhất 0,998 so với 0,93) và độ bền khi
  node hỏng. Mô hình không tính tranh chấp CSMA giữa nhiều node trong cell (mỗi cell một môi trường, một máy phát) và
  không tính che khuất tương quan, vốn làm lợi ích chọn cặp nhỏ đi.
- Mật độ còn quyết định xác suất nhận ở mức cell P_k của pha bay (ít node thì P_k thấp hơn); chưa tính ở đây.

## 11. Pháp lý UAV ở đô thị (2026-11-17, mục 333, tra web)

- Mỹ: luật BVLOS Part 108 gửi OIRA ngày 10/7/2026, tới tháng 11/2026 chưa ban hành; FAA mong ban hành trước cuối 2026,
  áp dụng đầy đủ có thể sau đó khoảng một năm. Hiện bay ngoài tầm nhìn vẫn phải xin miễn trừ từng trường hợp.
- EU: quy định U-space 2021/664 áp dụng từ 26/1/2023, nhưng tới nay mới có rất ít vùng U-space thật (một nguồn công nghiệp
  nói chỉ một vùng hạn chế); Đức dự kiến trình luật chỉ định vùng U-space cuối 2026.
- Trung Quốc: Luật Hàng không dân dụng sửa đổi có chương riêng cho UAV, hiệu lực 1/7/2026; chiến lược "kinh tế tầm thấp"
  (dưới 3 000 m) khoảng 1,5 nghìn tỉ nhân dân tệ năm 2025, 2,7 triệu gói giao bằng UAV năm 2024; đồng thời Bắc Kinh siết
  quy định địa phương.
- Việt Nam: Luật Phòng không nhân dân 2024 (hiệu lực 1/7/2025) buộc đăng ký UAV; Nghị định 288/2025/NĐ-CP (hiệu lực
  5/11/2025) quản lý tàu bay không người lái, theo một nguồn thì cấp phép bay trong khu cấm bay chỉ cho bay công vụ. Số
  hiệu nghị định xử phạt (282 hay 288) lẫn lộn giữa các nguồn, cần đối chiếu văn bản gốc.
- Xu hướng chung là mở đường cho bay thường xuyên ngoài tầm nhìn qua đăng ký, định danh từ xa và quản lý không lưu tầm
  thấp (UTM, U-space), không phải bỏ bớt quản lý. Với bài: nhiệm vụ tìm kiếm cứu nạn hay an ninh là bay công vụ, nhóm dễ
  được cấp phép nhất, kể cả ở đô thị.

## 12. Vì sao cần UAV: gửi truy vấn qua LoRa hay qua mạng mặt đất mất bao lâu (2026-11-18, mục 334)

Truy vấn 400 KB (409 600 B). Mốc so sánh: trên bản đồ k8, r100, critical cell cuối cùng của CHORD + River xong khoảng
746 s (12,4 phút) sau khi cất cánh [repo: `paper/j1/draft-v1/`].

**LoRa từ trạm gốc tới các CH** (thời gian phát theo công thức Semtech, BW 125 kHz, CR 4/5, gói lớn nhất của từng SF; giả
định lạc quan: mọi CH nằm trong tầm, một lần phát tới tất cả, không mất gói):

| SF, cỡ gói | Thời gian phát thuần | Chu kỳ 10 % (băng 869,4–869,65 MHz) | Chu kỳ 1 % (băng 868,0–868,6 MHz) |
|---|---|---|---|
| SF7, 222 B | 10,7 phút | 1,8 h | 17,9 h |
| SF9, 115 B | 36,5 phút | 6,1 h | 61 h |
| SF12, 51 B | 5,5 h | 55 h | 23 ngày |

SF7 có tầm ngắn nhất, nên trường hợp tốt nhất 1,8 h khó giữ được ở địa hình che khuất. Tới CH rồi vẫn còn phải truyền mặt
đất trong cụm như River. LoRa vì vậy chỉ hợp để gửi kết quả vài byte về trạm gốc (đúng vai trò hiện có).

**Mạng mặt đất 802.15.4 từ trạm gốc.** Trên k8, trạm gốc cách cell gần nhất 1,08 km, tức không có đường mặt đất nếu không
thêm trạm chuyển tiếp. Critical cell cách trạm gốc 1,1–6,3 km (trung vị 3,7 km), 18 cell (trung vị) tới 35 cell; với
khoảng 2,7 chặng node mỗi cell (1,7 trong cell cộng 1 qua cặp gateway, số đo trace River) là khoảng 50–95 chặng [mới tính].
Tốc độ phổ biến của các giao thức đã đo, quy ra 400 KB (gấp 12,5 lần tệp 32 KB) [repo: ghi chú bài báo]:

| Giao thức | Số đo gốc | Quy ra 400 KB | Testbed |
|---|---|---|---|
| Pando (flood đồng bộ + fountain) | 32 KB trong 5,7–11,4 s | 1,2–2,4 phút | FlockLab 31 nút, Indriya 99 nút |
| Splash (flood đồng bộ, pipeline cây) | 32 KB trong khoảng 25 s | khoảng 5 phút | Indriya 139 nút, tới 9 chặng |
| Typhoon | 20 KB trong 54–75 s | 18–25 phút | TOSSIM lưới 20 × 20; 22 mote |
| Deluge gốc | 88,4 B/s | khoảng 77 phút | 75 Mica2-dot |
| DelugeT2 (quy đổi trên Indriya) | 32 KB khoảng 373 s | khoảng 78 phút | Indriya |

Nhận xét:
- Mọi số trên đo ở mạng tới khoảng 9 chặng; mạng của bài sâu 50–95 chặng. Tôi chưa thấy số đo của flood đồng bộ (Pando,
  Splash) ở độ sâu đó. Ghi chú GreenOrbs cho thấy tỉ lệ gói tới đích rơi từ 0,72 (1 chặng) xuống 0,12 (8 chặng) ở mạng
  công suất thấp trong rừng, và CitySee ghi tải dồn quanh sink ở mạng 21 chặng [repo].
- Giao thức CSMA thường (Typhoon, Deluge) cần 20 phút tới hơn một giờ, chậm hơn UAV nhiều.
- Flood đồng bộ kiểu Pando là đối thủ thật: nếu nó giữ được tốc độ ở 50–95 chặng thì nhanh ngang hoặc hơn UAV. Lập luận
  của bài khi đó phải dựa vào: không có đường mặt đất từ trạm gốc (phải dựng chuỗi chuyển tiếp), độ bền của flood đồng bộ
  ở độ sâu lớn và qua địa hình che khuất, và năng lượng (flood gửi 400 KB tới mọi node, River chỉ dùng các cell trên
  đường và quanh critical cell). ns-3 lr-wpan không mô phỏng được giao thoa xây dựng của Glossy, nên so trực tiếp phải
  dùng mô hình hoặc số đo của các bài trên.

## 13. Bài chọn critical cell: phát biểu đề xuất (2026-11-18, mục 335)

J1 giải cả bài chọn critical cell (mục 335). Đây là đề xuất để bàn, chưa chốt.

**Bối cảnh tìm người.** Trước sự cố, node thường gửi ảnh camera về AI node phụ trách. Khi có sự cố, trạm gốc phát truy
vấn (ảnh tham chiếu của người cần tìm); mỗi AI node nhận đủ truy vấn rồi đối sánh với ảnh nó giữ, báo điểm về trạm gốc.
Thời gian quan trọng là lúc AI node cuối cùng đối sánh xong, vì người cần tìm có thể ở vùng của bất kỳ AI node nào.

**Biến và dữ liệu.** Tập ứng viên V_s (node mạnh, năng lực c_v, bộ nhớ M_v, tốc độ đối sánh μ_v); node thường V_o, mỗi
node u sinh d_u ảnh trong cửa sổ lưu W; khoảng cách chặng h(u, v) trên đồ thị G2G. Biến y_v ∈ {0, 1} (mở AI node v), x_uv
∈ {0, 1} (giao node u cho v). Cell chứa ít nhất một AI node mở là critical cell.

**Ràng buộc.** Mỗi node thường giao cho đúng một AI node mở, cách không quá H chặng (giới hạn luồng nền); tổng ảnh giao
cho v không vượt M_v; hai AI node mở cách nhau ít nhất D_min (ý "không giành khách nhau" ở mục 3; có thể bỏ nếu ràng
buộc bộ nhớ và chặng đã đủ giữ chúng tách nhau). Mục 338: bỏ D_min, chỉ dùng giới hạn chặng H và bộ nhớ.

**Mục tiêu.** Pha 1 xong ở max_k [T_giao,k(K) + T_đối sánh,k], trong đó T_giao,k là lúc critical cell k nhận đủ truy vấn
(phụ thuộc cả tập K qua tour và River), T_đối sánh,k = (ảnh giao cho k) / μ_k. Mục tiêu chung của bài là tối thiểu tổng
thời gian pha 1 và pha 2 (mục 338): pha 2 bắt đầu khi trạm gốc nhận đủ báo cáo qua LoRa và kết thúc khi UAV cánh quay
xác minh xong người cần tìm, nên tập K còn ảnh hưởng pha 2 qua vị trí các nghi vấn so với trạm gốc.

**Đánh đổi chính.** Ít critical cell thì việc giao truy vấn nhẹ (ít Ring, Λ\* nhỏ, River ngắn) nhưng mỗi AI node giữ nhiều
ảnh hơn nên đối sánh lâu hơn, luồng nền đi xa hơn, cần nhiều bộ nhớ hơn. Nhiều critical cell thì ngược lại. Vì vậy có số
critical cell tối ưu ở giữa; đặt chúng gần đường bay hay gần nhau cũng làm giao nhanh hơn nhưng làm đối sánh lệch tải.

**Cách giải đề xuất.** T_giao,k(K) không có dạng đóng, nên tách hai tầng: (1) pha 0 chọn K bằng một hàm thay thế cho
T_giao (công thức surrogate T̂_River đã khớp từ số đo, hoặc khoảng cách tới đường bay và lượng thiếu dự kiến), cộng
T_đối sánh, giải bằng heuristic kiểu facility location có sức chứa (tìm kiếm cục bộ đổi mở/đóng); (2) pha 1 giữ nguyên
CHORD/LM-Tour + River cho tập K đã chọn, đo T\* bằng ns-3. Bài chọn K chứa facility location có sức chứa nên NP-khó
(trích chuẩn khi viết).

**Cần quyết hoặc cần số liệu:** tốc độ đối sánh μ (chưa có nguồn đo re-ID đầu cuối, mục 338; repo có số thành phần và mô
hình suy ra theo bậc thiết bị ở `research_notes/l1-edge-recognition/edge_devices.md`), lượng ảnh mỗi camera trong cửa sổ
W và chính sách giữ/bỏ (mục 14), giá trị H. Đánh đổi số critical cell làm thành việc kỹ thuật K9 (mục 338).

## 14. Bộ nhớ node và chính sách giữ/bỏ dữ liệu (2026-11-18, mục 338)

**Đã có trong repo** [`research_notes/l1-edge-recognition/edge_devices.md`, ngày 2026-10-15]:
- Lưu trữ: luồng 2 Mbit/s ≈ 21,6 GB/ngày, thẻ 128 GB giữ khoảng 5,5 ngày ghi liên tục; nhà sản xuất khác ghi 128 GB ≈ 16
  ngày ở 1080p; quy tắc chung 1–2 tuần trước khi ghi đè. Thẻ 32–256 GB giữ khoảng 1,5–20 ngày ở 1–2 Mbit/s.
- Đối sánh (mô hình suy ra, chưa đo đầu cuối): lấy mẫu 1 khung/s, khoảng 2 người mỗi khung. Bậc MCU (ESP32-S3) xử lý
  khoảng 1–2 giờ video mỗi giờ tính; chip camera 1–2 TOPS khoảng 6–12; máy nhỏ kèm bộ tăng tốc (Pi 5 + Hailo-8L, RK3588)
  khoảng 30–60; Jetson Orin Nano khoảng 50–150. Ví dụ quét 132 h video mất 11–22 h ở bậc chip camera, 2–4 h ở bậc
  Hailo, 66–130 h ở ESP32-S3. Chưa có số đo re-ID người (OSNet) trên thiết bị nào.
- Bộ nhớ truy vấn: 1 MB là nhỏ với mọi bậc từ chip camera trở lên; node SmartSantander chỉ có 8 KB SRAM nhưng có thẻ SD
  2 GB [`papers/sanchez2014-smartsantander.md`].

**Bốn loại dữ liệu trên một node** (đề xuất, để bàn):

| Dữ liệu | Ở đâu | Cỡ | Đề xuất giữ/bỏ |
|---|---|---|---|
| Ghi hình của chính camera | mọi node camera | phần lớn bộ nhớ (GB) | ghi vòng, bỏ cái cũ nhất (cách camera đang làm) |
| Dữ liệu node phụ thuộc gửi về | AI node | tổng luồng của các node giao cho nó trong cửa sổ W | theo thời gian, giữ W giờ gần nhất; ưu tiên khung có người |
| Truy vấn (400 KB) | critical cell và cell River (SPINE, Bank, Ring) | 400 KB, hoặc một đoạn | ghim, không bị ghi đè cho tới khi nhiệm vụ xong; cell trung chuyển xoá khi River xong |
| Bộ đệm chuyển tiếp | node trên đường | vài gói | hàng đợi MAC như hiện tại |

Nhận xét:
- Truy vấn 400 KB nhỏ so với thẻ nhớ vài GB, nên chỗ chật là RAM của node yếu (vài KB) và cửa sổ W ở AI node, không phải
  chỗ chứa truy vấn.
- Với tìm người, ảnh mới nhất có giá trị nhất, nên giữ theo thời gian (FIFO) là tự nhiên; giữ theo nội dung (khung có
  người, ảnh cắt người) cho W dài hơn nhiều với cùng bộ nhớ.
- Lựa chọn ảnh hưởng lớn nhất: node thường gửi về AI node cái gì. Ảnh gốc làm luồng nền G2G nặng và đối sánh chậm. Ảnh cắt
  người nhẹ hơn nhiều. Vector đặc trưng (512 chiều INT8 = 512 B mỗi người) thì đối sánh chỉ là tính cosine, gần như tức
  thì, nhưng node thường phải tự chạy phát hiện và trích đặc trưng. Lựa chọn này đổi hẳn μ và đánh đổi số critical cell.
- Cần khảo sát thêm (việc K12): lượng ảnh, khung có người mỗi giờ của camera đô thị; chính sách lưu của hệ thống phân tích
  video tại biên; dung lượng nhớ của node camera rẻ.

## 15. Lý do cần UAV ở đô thị hiện đại (2026-11-18, mục 343)

Người dùng chọn hai lý do: node rẻ chỉ có 802.15.4, không nối Internet (hướng 1), và dữ liệu ở lại thiết bị vì quyền
riêng tư (hướng 4). Kịch bản là khu đô thị nhiều chuông cửa, camera quan sát, máy bán hàng tự động.

**Tiền lệ thật** [web, trừ chỗ ghi repo]:
- 802.15.4 đã có sẵn trong nhà thông minh: Thread chạy trên IEEE 802.15.4 ở 2,4 GHz, là tầng mạng của các thiết bị Matter
  công suất thấp; nhiều loa thông minh làm border router.
- Nhưng mạng Thread hiện là mạng riêng của từng nhà: tối đa 32 router mỗi mạng, thiết bị ngủ (chạy pin) không chuyển tiếp
  cho ai. Mạng của bài (13 086 node, mọi node chuyển tiếp) vì vậy không phải Thread nguyên bản mà là một mạng dùng chung cấp
  khu phố.
- Mạng dùng chung giữa thiết bị của nhiều chủ đã có: Amazon Sidewalk dùng chuông cửa, loa của người dân làm cầu nối, công
  bố phủ khoảng 90 % dân số Mỹ năm 2023; nó cũng bị phê phán vì bật mặc định (opt-out) và vì chuyện chính quyền xin truy cập
  camera chuông cửa. Đây là tiền lệ cho câu i (sở hữu, tham gia) và cho mặt pháp lý của hướng 4.
- Cách phân phối tệp hiện nay trên Thread/LwM2M là unicast CoAP từng thiết bị [repo: `02-code-dissemination.md`], tức
  chưa có cơ chế đẩy một tệp lớn tới nhiều thiết bị như bài đặt ra.

**Hệ quả cho mô hình:**
- Chỉ node cắm điện chuyển tiếp; node chạy pin (một phần chuông cửa) chỉ nhận. Mật độ node chuyển tiếp vì vậy thấp hơn mật
  độ thiết bị. Ví dụ 30 % chạy pin thì còn khoảng 570 node chuyển tiếp/km², vẫn trên mức 400 mà lưới cell còn liên thông
  (mục 10). Đề xuất thêm tỉ lệ node chạy pin làm tham số.
- Hướng 4 cho phép trạm gốc chỉ nhận điểm số. Pha 2 (xác minh) là lúc duy nhất ảnh của người nghi vấn rời thiết bị, nên cần
  nói rõ căn cứ (tình huống khẩn cấp, chủ thiết bị đồng ý khi tham gia).
- Câu i có hướng trả lời: chủ thiết bị tham gia một mạng dùng chung kiểu Sidewalk, một bên vận hành (thành phố hay nhà cung
  cấp) chạy pha 0.

## 16. Cửa sổ truy vấn, kiểu trả lời của camera, giới hạn thời gian (2026-11-18, mục 344)

**Đã chốt:** nhiệm vụ không giới hạn thời gian, tìm tới khi thấy, chỉ bị chặn bởi năng lượng (sức bền) của UAV. Camera trả
lời "tôi thấy người (hay vật) trông giống mục tiêu", tức một điểm giống, đúng như mô hình lớp 1 hiện có (`paper/L1-MODEL-vi.md`:
node báo điểm cao nhất của nó).

**Cửa sổ 1–2 giờ so với 1 ngày.** Tính trên mô hình có sẵn trong repo (`uav-l2/tools/l1_mission.py`: điểm người lạ ~ N(0, 1),
điểm mục tiêu ~ N(4,43; 1,30) khớp từ Market-1501, vector ResNet-50 2048 chiều fp16, `match_time`). Ví dụ một AI node
phụ trách 100 camera, mỗi camera 60 người/h (giả định minh hoạ, chờ khảo sát ở K12):

| Cửa sổ | Số người trong kho M | Thời gian tìm khi đã có vector | Chỉ mục | Trích vector khi truy vấn tới (Hailo / Pi 5 CPU) | Ngưỡng để 10 % AI node báo nhầm | Xác suất bắt được mục tiêu: 1 ảnh / 3 ảnh |
|---|---|---|---|---|---|---|
| 1 h | 6 000 | 3 ms | 25 MB | 0,4 phút / 0,13 h | 4,15 | 0,59 / 0,93 |
| 2 h | 12 000 | 6 ms | 49 MB | 0,8 phút / 0,26 h | 4,31 | 0,54 / 0,90 |
| 6 h | 36 000 | 18 ms | 147 MB | 2,3 phút / 0,79 h | 4,54 | 0,47 / 0,85 |
| 24 h | 144 000 | 74 ms | 590 MB | 9,3 phút / 3,2 h | 4,83 | 0,38 / 0,76 |

Nhận xét:
- Nếu vector được tính ngay khi ảnh tới (ở camera hay ở AI node), thời gian tìm chỉ vài chục ms và chỉ mục vài trăm MB, nên
  cửa sổ dài không làm chậm. Nếu chỉ trích vector khi truy vấn tới thì cửa sổ 1 ngày tốn 9 phút trên Hailo, hơn 3 giờ trên
  CPU. Vì vậy D1/D2 nên trích vector dần khi ảnh tới.
- Cái mất thật khi cửa sổ dài là độ phân biệt: kho càng nhiều người lạ thì người lạ giống nhất càng giống, phải nâng ngưỡng
  để giữ cùng tỉ lệ báo nhầm, nên xác suất bắt được mục tiêu từ một ảnh giảm từ 0,59 (1 h) xuống 0,38 (24 h). Có nhiều ảnh
  của mục tiêu thì đỡ hơn (0,93 xuống 0,76 với 3 ảnh).
- Cửa sổ dài thấy được nhiều chỗ người đó từng qua, nhưng lần thấy cũ ít giúp tìm người ở hiện tại. Đề xuất: báo cáo kèm
  thời điểm thấy (thêm vài byte), trạm gốc xếp hạng nghi vấn theo cả độ giống lẫn độ mới; pha 2 xác minh lần thấy mới nhất
  trước.
- Số liệu mô hình khớp từ bộ dữ liệu phòng thí nghiệm, nên độ phân biệt ngoài thực tế có thể kém hơn; xu hướng (dài hơn thì
  phân biệt kém hơn) vẫn đúng.

**Hệ quả cho mục tiêu.** Không giới hạn thời gian thì mục tiêu là tối thiểu thời gian tới khi xác minh đúng người (T1 + T2
như mục 13), với ràng buộc sức bền của hai UAV; nếu một chuyến không đủ thì cần mô hình hạ cánh thay pin. Cửa sổ truy vấn
mặc định 2 giờ, quét 1–24 giờ ở K12/K9 (chốt, mục 345).

## 17. Pha 2 ở đô thị cao tầng: xác minh nghĩa là gì (2026-11-18, mục 345, đề xuất để bàn)

Mô hình pha 2 hiện có [repo: `uav-l2/tools/mission_baselines.py`, `l1_rank.py`]: UAV cánh quay 15 m/s, lơ lửng ở 100 m trên
cell nghi vấn, chờ ổn định 5 s, gửi bộ tham chiếu đầy đủ R (khoảng 20 ảnh, 1 MB) bằng unicast 802.15.4 tới CL (10 592 khung,
khoảng 73 s), cell đối sánh lại với R; tổng khoảng 78 s mỗi lần xác minh. Pha 2 xong khi xác minh tới cell thật.

Bốn cách xác minh:

| Mã | Cách | Ảnh có rời thiết bị không | Thời gian mỗi nghi vấn (tính trên mô hình repo) | Cần UAV đội 2 |
|---|---|---|---|---|
| V1 | UAV mang R (1 MB) tới node, node đối sánh lại, chỉ báo điểm mới (mô hình hiện tại) | không | bay + khoảng 78 s | có, phải tới gần |
| V2 | Node gửi ảnh cắt nghi vấn (5–15 KB) về trạm gốc qua LoRa của CH, người vận hành xác nhận | có, chỉ ảnh nghi vấn | 1,3–3,9 phút ở chu kỳ 10 %, 13–39 phút ở 1 %; chờ hàng đợi LoRa | không |
| V3 | UAV bay ngang thu ảnh cắt nghi vấn (0,4–1 s qua 802.15.4), gửi về trạm gốc qua đường truyền của UAV | có, chỉ ảnh nghi vấn | bay + khoảng 1 s, không cần lơ lửng lâu | có, chỉ cần đi ngang |
| V4 | UAV tới vị trí lần thấy mới nhất, nhìn bằng camera của chính nó | không (ảnh của UAV) | bay + thời gian quan sát | có |

Nhận xét:
- (Sửa ngày 2026-11-19, mục 347.) Tầm R50 khoảng 45 m ở khu cao tầng là cự ly ngang của một UAV bay qua. Lơ lửng ngay trên
  node thì góc ngẩng gần 90°, xác suất LoS theo Al-Hourani (cao tầng) là 0,85; gói qua được 0,87 nếu lệch 0 m, 0,73 nếu lệch
  20 m, 0,49 nếu lệch 45 m. V1 vì vậy vẫn làm được nếu UAV lơ lửng gần đúng trên node (toạ độ node có từ pha 0), thời gian gửi
  R tăng khoảng 1/0,8 lần; nếu node bị che (NLoS) từ điểm lơ lửng thì gói qua chỉ khoảng 0,13 và UAV phải đổi chỗ. Nhà cao hơn
  độ cao bay thì không lơ lửng trên được.
- V2 bỏ hẳn đội 2 nếu chu kỳ LoRa cho phép, nhưng chậm khi nhiều nghi vấn cùng chờ một CH, và chỉ giữ được hướng 4 một phần.
- V3 nhanh nhất về thời gian ở mỗi điểm và hợp với UAV khó tới sát node, đổi lại ảnh nghi vấn rời thiết bị.
- V4 chỉ có ích khi lần thấy rất mới; người đã đi khỏi thì vô ích, và đây là việc của đội cứu hộ hơn là của mạng.
- Hướng 4 (giữ dữ liệu tại chỗ) chọn V1; nếu chấp nhận ảnh nghi vấn rời thiết bị trong tình huống khẩn cấp thì V3 hoặc V2.
  So sánh V1, V2, V3 trên tổng thời gian hai pha là một thí nghiệm rẻ (mô hình, không cần ns-3).

**Quyết định (mục 347).** Bỏ V3: UAV phải thu mọi ảnh nghi vấn nên thời gian pha 2 như nhau ở mọi baseline, không làm rõ lợi
thế của pha 1. Chọn V1 và V4. V1 giữ dữ liệu tại chỗ và để thứ tự thăm (theo xác suất từ pha 1) quyết định thời gian pha
2, nên chất lượng pha 1 hiện ra trong tổng thời gian. V4 cần thêm mô hình người di chuyển kể từ lúc được thấy (vùng tìm nở
ra theo thời gian) và xác suất UAV nhìn thấy người.

Chốt (mục 349): pha 2 của bài kết thúc khi V1 xác nhận đúng lần thấy (mức dữ liệu); V4 (tìm thấy người ngoài thực địa) là
bước tiếp theo, chỉ làm khi lần thấy đã xác nhận còn đủ mới.

## 18. Bản đồ đô thị mẫu từ OpenStreetMap (2026-11-19, mục 350)

Người dùng chọn dùng bản đồ thật của một khu đô thị làm mẫu. Thăm dò một ô khoảng 0,4 km² ở mỗi khu ứng viên qua API của
OpenStreetMap (log `logs/2026-11-19_0730-osm-probe/`; Overpass và Geofabrik bị chặn trong container này):

| Khu | Toà nhà trong ô | Có chiều cao hoặc số tầng | Cao nhất | Đường |
|---|---|---|---|---|
| Hà Nội, Cầu Giấy | 193 | 12 % | 87 m | 360 |
| Hà Nội, Vinhomes Ocean Park | 47 | 70 % | 90 m | 248 |
| Hà Nội, Royal City | 86 | 10 % | 135 m | 236 |
| TP.HCM, Quận 1 | 164 | 16 % | 193 m | 346 |
| Singapore, khu trung tâm | 287 | 92 % | 245 m | 507 |
| New York, Midtown | 232 | 79 % | 366 m | 598 |

Nhận xét:
- Các khu cũ của Hà Nội và TP.HCM thiếu chiều cao (10–16 %), và số toà nhà có vẻ thiếu so với thực tế; phải đoán chiều cao
  cho phần lớn nhà nên mô hình kênh kém tin cậy.
- Vinhomes Ocean Park là khu đô thị mới đúng kiểu "hiện đại", dữ liệu chiều cao khá (70 %), nhà cao nhất khoảng 90 m, sát
  độ cao bay 100 m.
- Singapore có dữ liệu tốt nhất (92 %) và nhiều nhà cao hơn 120 m, hợp để thử trường hợp khó: nhà thành vật cản, UAV phải
  bay vòng.

**Dùng bản đồ thật thế nào (đề xuất):**
- Toà nhà (đường viền + chiều cao, thiếu thì đoán theo diện tích và loại nhà) và đường phố lấy từ OSM, tải theo ô nhỏ.
- Node đặt theo nhà và phố, không rải đều: chuông cửa ở lối vào nhà, camera trên cột dọc phố, máy bán hàng ở vỉa hè;
  tổng mật độ giữ khoảng 816 node/km².
- Kênh A2G xác định LoS bằng hình học thật: tia từ UAV tới node có cắt khối nhà nào không, thay cho xác suất Al-Hourani.
  Kênh G2G có LoS khi đoạn nối hai node không cắt nhà (K1c).
- Nhà cao hơn độ cao bay thành vùng cấm bay cho tour (K5); điểm lơ lửng của V1 chọn chỗ có LoS tới node.

**Chín khu ứng viên, ô 4 × 4 km bằng cỡ bản đồ k8** (mục 351; log `logs/2026-11-19_0800-osm-areas/`, hình
`paper/j1/figures/osm-*.png`):

| Khu | Nhà (diện tích) | Nước | Đất trống có thẻ | Số nhà | Có chiều cao | Nhà > 100 m / > 120 m | Cao nhất | Cell nước | Cell không chỗ đặt node |
|---|---|---|---|---|---|---|---|---|---|
| Hà Nội, Ocean Park | 6 % | 5 % | 20 % | 4 266 | 5 % | 8 / 7 | 226 m | 2 % | 6 % |
| Hà Nội, Ecopark | 2 % | 7 % | 8 % | 1 776 | 2 % | 8 / 0 | 120 m | 1 % | 10 % |
| Hà Nội, Mỹ Đình | 14 % | 3 % | 14 % | 9 607 | 50 % | 49 / 32 | 336 m | 2 % | 0 % |
| Hà Nội, Linh Đàm | 5 % | 9 % | 8 % | 1 838 | 8 % | 22 / 20 | 174 m | 7 % | 2 % |
| Hà Nội, Starlake (Tây Hồ Tây) | 9 % | 16 % | 10 % | 7 469 | 9 % | 9 / 2 | 135 m | 14 % | 1 % |
| TP.HCM, Thủ Thiêm | 7 % | 19 % | 22 % | 3 911 | 15 % | 45 / 38 | 461 m | 17 % | 9 % |
| TP.HCM, Phú Mỹ Hưng | 6 % | 7 % | 9 % | 3 322 | 8 % | 11 / 0 | 111 m | 4 % | 14 % |
| Singapore, trung tâm và Marina | 17 % | 1 % (thiếu biển) | 21 % | 5 148 | 85 % | 340 / 282 | 305 m | 0 % | 11 % |
| Singapore, Punggol | 15 % | 5 % | 22 % | 2 598 | 77 % | 0 / 0 | 78 m | 4 % | 9 % |

"Cell không chỗ đặt node": cell R = 100 m không có nhà và có dưới 50 m đường. Biển không được tính là nước (OSM vẽ biển bằng
đường bờ), và 34–69 % diện tích chưa gắn thẻ, nên số đất trống chỉ là cận dưới.

Nhận xét:
- Đủ cả hồ hoặc sông, đất trống và nhà cao: Thủ Thiêm (sông Sài Gòn 19 %, nhiều lô đất trống, 38 nhà trên 120 m, có Landmark
  81) và Starlake (một phần Hồ Tây, 16 % nước, khu mới còn nhiều lô trống). Cả hai thiếu chiều cao (9–15 %).
- Linh Đàm có nhiều hồ nhỏ xen chung cư cao tầng (20 nhà trên 120 m), dữ liệu chiều cao kém (8 %).
- Mỹ Đình có dữ liệu chiều cao tốt nhất ở Việt Nam (50 %) và dày nhà cao, nhưng ít nước và gần như không có cell trống.
- Punggol (Singapore) là khu đô thị mới sạch nhất: 77 % có chiều cao, kênh và công viên, nhà đều dưới 100 m nên UAV bay qua
  được; Marina có dữ liệu chiều cao tốt nhất (85 %), nhiều nhà trên 120 m.

**Bản đồ một quận: Hoàng Mai** (mục 352; log `logs/2026-11-19_0900-district-map/`, dữ liệu `paper/j1/maps/hoangmai/`, hình
`paper/j1/figures/map-hoangmai-labelled.png`). Chọn Hoàng Mai vì có nhiều hồ xen chung cư cao tầng. Ranh giới là quận cũ
(OSM giữ dưới dạng boundary=historic sau cải cách 2025). 40,2 km²; nước 17,9 % (50 hồ từ 2 ha và một đoạn sông Hồng);
2 921 toà nhà, 13 % có chiều cao, 81 toà từ 60 m, 23 toà từ 120 m, cao nhất 174 m; vùng cao tầng (nhà từ 60 m nới 100 m)
5,2 % diện tích; 1 552 cell R = 100 m, trong đó 16 % chủ yếu là nước và 5 % nằm trong vùng cao tầng. Địa hình phẳng (trung vị
9 m), nên "vùng cao" ở đây là vùng nhà cao tầng; lớp độ cao 30 m nhiễu (đánh dấu cả mặt hồ) nên không vẽ. OSM thiếu nhiều
nhà thấp tầng và chiều cao, nên vùng cao tầng chỉ gồm các toà đã có dữ liệu.

## 19. Vùng cấm bay (2026-11-19, mục 353)

**Quy định** [web]: Bộ Quốc phòng công bố cổng tra cứu khu vực cấm bay, hạn chế bay tại cambay.mod.gov.vn từ 15/6/2025, theo
Quyết định 18/2020/QĐ-TTg; dữ liệu bản đồ này được quản lý theo luật bảo vệ bí mật nhà nước, nên không tải về làm dữ liệu
được (cổng cũng không vào được từ container). Nghị định 288/2025/NĐ-CP (hiệu lực 5/11/2025): trong khu vực cấm bay chỉ cấp
phép cho nhiệm vụ công vụ (quốc phòng, an ninh, an toàn bay, trật tự xã hội), và nộp hồ sơ không đồng nghĩa được cấp.
TP.HCM công bố 63 phường, xã, đặc khu thuộc phạm vi cấm bay drone; Hải Phòng 30, với lưu ý danh sách chỉ nói địa bàn có
vùng cấm, không phải cả địa bàn bị cấm. Chưa tìm thấy danh sách của Hà Nội.

**Hệ quả cho bài:**
- Nhiệm vụ tìm người là bay công vụ, nhóm duy nhất được xét cấp phép trong vùng cấm (đã chọn ở mục 11). Vùng cấm theo quy
  định vì vậy là điều kiện xin phép, không chặn hẳn nhiệm vụ.
- Vùng phải tránh thật sự là vùng an toàn: quanh sân bay (đường tiếp cận), đất quân sự, và vật cản vật lý là nhà cao hơn độ
  cao bay. Bài mô hình hoá ba loại này bằng dữ liệu OSM (aeroway=aerodrome, landuse=military, nhà từ 100 m nới 50 m), nối
  với việc K5 (tour né vùng cấm) và Hệ quả 2 (vùng cấm làm chặn dưới không hợp tác vô hạn).
- Đây là ước lượng: vùng cấm thật có thể rộng hơn (ví dụ quanh cơ quan nhà nước), nên kết quả cần ghi là trên vùng cấm ước
  theo OSM.

**Sáu quận đã cắt** (mục 353; dữ liệu `paper/j1/maps/<quận>/`, hình `paper/j1/figures/map-<quận>[-labelled].png`, log
`logs/2026-11-19_0900-district-map/`). Cấm bay ước theo OSM gồm sân bay và đất quân sự; vật cản là nhà từ 100 m nới 50 m.

| Quận | km² | Nước | Hồ ≥ 2 ha | Nhà có chiều cao | Nhà ≥ 120 m | Cao nhất | Vùng cao tầng | Cấm bay ước theo OSM | Vật cản (toà) |
|---|---|---|---|---|---|---|---|---|---|
| Hoàng Mai | 40.2 | 17.9 % | 50 | 13 % | 23 | 174 m | 5.2 % | 0.3 % | 31 |
| Cầu Giấy | 12.5 | 2.7 % | 3 | 3 % | 10 | 165 m | 17.0 % | 1.8 % | 16 |
| Tây Hồ | 24.7 | 23.5 % | 8 | 11 % | 0 | 110 m | 2.6 % | 0.1 % | 4 |
| Nam Từ Liêm | 32.2 | 4.5 % | 12 | 78 % | 12 | 186 m | 10.8 % | 2.5 % | 74 |
| Long Biên | 60.2 | 9.6 % | 37 | 3 % | 0 | 81 m | 0.9 % | 2.7 % | 0 |
| Quận 7 (TP.HCM) | 35.8 | 12.8 % | 16 | 7 % | 0 | 111 m | 3.0 % | 0.1 % | 11 |

Nhận xét: Nam Từ Liêm có dữ liệu chiều cao tốt nhất (78 %) và nhiều nhà cao, nhiều đất quân sự (2,5 %); Hoàng Mai và Tây Hồ
nhiều nước nhất (18 %, 24 %); Cầu Giấy dày nhà, vùng cao tầng lớn nhất (17 %); Long Biên có sân bay Gia Lâm và nhiều đất quân
sự (2,7 %) nhưng không có nhà trên 100 m; Quận 7 nhiều kênh rạch. Vùng cấm bay ước theo OSM chỉ chiếm 0,1–2,7 % diện tích
mỗi quận; vùng cấm chính thức (không tải được) chắc chắn rộng hơn.

**Sáu khu đô thị hiện đại ở nước ngoài** (mục 355; cùng script, cùng tham số; nước gồm cả biển dựng từ đường bờ, vì OSM chỉ vẽ
biển bằng đường bờ; cột cuối là cao độ mặt đất trung vị – cao nhất theo ô Terrarium, gồm cả nhà và cây nên chỉ để tham khảo):

| Khu | km² | Nước | Nhà có chiều cao | Nhà ≥ 120 m | Cao nhất | Vùng cao tầng | Cấm bay ước theo OSM | Vật cản (toà) | Vật cản (diện tích) | Cao độ đất |
|---|---|---|---|---|---|---|---|---|---|---|
| Singapore, Downtown Core | 5.1 | 2.0 % | 79 % | 38 | 245 m | 27.0 % | 0.0 % | 42 | 10.9 % | 13–127 m |
| Singapore, Punggol | 9.5 | 8.7 % | 73 % | 0 | 78 m | 5.6 % | 0.0 % | 0 | 0.0 % | 9–51 m |
| Hồng Kông, Yau Tsim Mong | 11.5 | 39.3 % | 50 % | 87 | 484 m | 36.0 % | 0.8 % | 127 | 8.6 % | 5–81 m |
| Dubai Marina | 1.9 | 0.1 % | 48 % | 44 | 395 m | 74.7 % | 0.0 % | 58 | 36.2 % | 1–25 m |
| Tokyo, Minato | 23.9 | 14.1 % | 10 % | 89 | 325 m | 28.6 % | 0.1 % | 123 | 8.7 % | 20–86 m |
| Seoul, Gangnam | 40.4 | 1.1 % | 19 % | 27 | 264 m | 22.7 % | 0.0 % | 70 | 2.4 % | 33–296 m |

Nhận xét: dữ liệu chiều cao tốt nhất ở Singapore (73–79 %), Hồng Kông và Dubai (48–50 %). Dubai Marina là trường hợp cực
đoan: vật cản chiếm 36 % diện tích, gần như không bay được ở 100 m. Downtown Core và Yau Tsim Mong có vật cản 9–11 % và vùng cao
tầng 27–36 %; Yau Tsim Mong có 39 % là biển. Punggol sạch nhất: nhà đều dưới 100 m, có kênh và hồ. Gangnam là nơi duy nhất có
địa hình cao thật (đồi tới gần 300 m ở phía nam), nên độ cao bay phải tính từ mặt đất chứ không từ trạm gốc.

## 20. Đặt node trên bản đồ thật: lưới cell liên thông và hổng ra sao (2026-11-19, mục 356)

Script `paper/j1/analysis/urban_nodes.py`, log `logs/2026-11-19_1000-urban-nodes/`, hình `paper/j1/figures/cells-*.png`.
Node đặt theo viền nhà mỗi 40 m (chuông cửa, camera tường; 45 % chạy pin và không chuyển tiếp) và dọc phố mỗi 30 m (camera
cột, máy bán hàng; cắm điện), không đặt trên nước, lấy mẫu về 816 node/km² đất. Kênh G2G của mô phỏng (liên kết dùng được khi
q ≥ 0,5); biến thể "tường" trừ thêm 15 dB cho mỗi toà nhà mà đoạn nối cắt qua (tối đa 3), bước đầu của K1c.

| Bản đồ | Kênh | Node | Chạy pin | Cell đất | Cell nước | Cell rỗng | Cell đứt bên trong | Cặp kề không có gateway | Thành phần | Cell trong thành phần lớn nhất | Node pin không với tới node điện |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Punggol | như hiện tại | 7 058 | 22 % | 328 | 32 | 3 % | 2 % | 2 % | 1 | 100 % | 0 % |
| Punggol | có tường | 7 058 | 22 % | 328 | 32 | 3 % | 28 % | 4 % | 1 | 100 % | 5 % |
| Downtown Core | như hiện tại | 4 094 | 18 % | 192 | 3 | 6 % | 1 % | 1 % | 1 | 100 % | 0 % |
| Downtown Core | có tường | 4 094 | 18 % | 192 | 3 | 6 % | 38 % | 5 % | 1 | 100 % | 6 % |
| Nam Từ Liêm | như hiện tại | 25 081 | 17 % | 1 199 | 39 | 5 % | 1 % | 2 % | 2 | 99,9 % | 0 % |
| Nam Từ Liêm | có tường | 25 081 | 17 % | 1 199 | 39 | 5 % | 9 % | 3 % | 2 | 99,9 % | 3 % |
| Hoàng Mai | như hiện tại | 26 929 | 11 % | 1 285 | 267 | 2 % | 1 % | 2 % | 1 | 100 % | 0 % |
| Hoàng Mai | có tường | 26 929 | 11 % | 1 285 | 267 | 2 % | 4 % | 2 % | 1 | 100 % | 1 % |

Nhận xét:
- Lưới cell vẫn là một khối liền ở cả bốn bản đồ (99,9–100 % cell nằm trong thành phần lớn nhất). Lỗ hổng gồm cell nước
  (1–17 % số cell, hồ Hoàng Mai nhiều nhất) và cell đất không có node cắm điện (2–6 %: công viên, nút giao lớn, đất trống, chỗ
  OSM thiếu dữ liệu). Các lỗ nằm rải rác nên không cắt lưới; sông có cầu và node dọc đường nên vẫn nối được.
- Với kênh hiện tại gần như mọi cell liên thông bên trong (1–2 % bị đứt) và 1–2 % cặp cell kề thiếu gateway.
- Khi tính xuyên tường, khu nhà dày đặc vỡ nhiều: 28–38 % cell ở Singapore bị đứt bên trong (các node trong cell không còn
  đường tới nhau mà không ra khỏi cell), 4–5 % cặp kề mất gateway, 5–6 % node pin không với tới node điện. Ở Hà Nội chỉ 4–9 %,
  một phần vì OSM thiếu nhà thấp tầng nên ít tường hơn thực tế.
- Hệ quả: giả định "mọi node của cell tới được CL bên trong cell" không còn giữ ở khu dày đặc khi tính tường. Hướng xử lý:
  cho phép đường trong cell mượn cell kề, giảm R, hoặc thêm node chuyển tiếp ở cột đèn dọc phố. Mô hình 15 dB mỗi toà là thô,
  cần hiệu chỉnh ở K1c.

## 21. Thêm node chuyển tiếp trên cột đèn (2026-11-19, mục 357)

Thêm node cắm điện trên cột đèn mỗi 35 m dọc phố, cách mép đường 3 m, chồng lên các thiết bị đã có; hai cách đặt: chỉ ở các
cell cần (rỗng, đứt bên trong, hoặc thiếu gateway với cell kề, xét ở kênh có tường) và trên mọi phố. Che khuất cố định theo
từng cặp node để so cặp; số không cột đèn vì vậy lệch nhẹ so với mục 20 (cùng mô hình, khác lần bốc). Log
`logs/2026-11-19_1000-urban-nodes/<bản đồ>-poles.md`, hình `paper/j1/figures/cells-*-walls-poles-*.png`.

| Bản đồ | Kênh có tường | Cột đèn thêm | Cell đứt bên trong | Cặp kề không có gateway | Node pin không với tới node điện | Node điện lạc khỏi nhóm chính của cell (phần trên nhà) |
|---|---|---|---|---|---|---|
| Punggol | không cột đèn | 0 | 31 % | 5 % | 5 % | 5,7 % (73 %) |
| Punggol | cột ở cell cần | +1 876 (+27 %) | 15 % | 1 % | 4 % | 2,3 % (68 %) |
| Punggol | cột mọi phố | +4 995 (+71 %) | 18 % | 1 % | 3 % | 1,8 % (68 %) |
| Downtown Core | không cột đèn | 0 | 45 % | 4 % | 7 % | 8,8 % (62 %) |
| Downtown Core | cột ở cell cần | +1 476 (+36 %) | 29 % | 2 % | 4 % | 3,3 % (53 %) |
| Downtown Core | cột mọi phố | +3 488 (+85 %) | 29 % | 2 % | 4 % | 2,6 % (49 %) |
| Nam Từ Liêm | không cột đèn | 0 | 11 % | 3 % | 3 % | 2,0 % (77 %) |
| Nam Từ Liêm | cột ở cell cần | +2 319 (+9 %) | 7 % | 1 % | 2 % | 1,1 % (80 %) |
| Nam Từ Liêm | cột mọi phố | +15 348 (+61 %) | 6 % | 1 % | 2 % | 0,7 % (80 %) |
| Hoàng Mai | không cột đèn | 0 | 4 % | 2 % | 1 % | 0,3 % (57 %) |
| Hoàng Mai | cột ở cell cần | +1 062 (+4 %) | 1 % | 1 % | 1 % | 0,1 % (55 %) |
| Hoàng Mai | cột mọi phố | +18 639 (+69 %) | 2 % | 1 % | 1 % | 0,1 % (70 %) |

Nhận xét:
- Đặt cột đèn chỉ ở cell cần cho kết quả gần bằng đặt mọi phố, với số node thêm ít hơn nhiều (4–36 % thay vì 61–85 %).
- Cột đèn sửa được phần khung: cặp cell kề thiếu gateway giảm từ 2–5 % xuống 1–2 %, node điện bị lạc giảm 2–3 lần.
- Phần còn đứt chủ yếu là vài node gắn trên nhà, nằm sau toà nhà so với phố (49–80 % số node lạc là node trên nhà); trung bình
  khoảng 3 node lạc mỗi cell đứt. Các node này nên coi là node lá (chỉ nhận, không cần chuyển tiếp) hoặc nối qua cell kề; cell
  "đứt" theo định nghĩa chặt (một node lạc cũng tính) vì vậy là cách đếm bi quan.
- Đặt cột ở mọi phố đôi khi làm tăng số cell đứt (Punggol 15 % lên 18 %): cột trên lối đi bộ trong khu nhà cũng có thể bị lạc.
- Chốt (mục 358), đưa vào K14: thêm lớp node chuyển tiếp trên cột đèn, đặt theo nhu cầu ở pha 0; node trên nhà không với tới nhóm chính
  của cell thì làm node lá.

## 22. Trạm gốc, điểm cất cánh, độ cao bay (2026-11-19, mục 358; chốt ở mục 359)

**Trạm gốc đặt ở đâu.** Trên bốn bản đồ đề xuất, OSM có sẵn đồn công an và trạm cứu hoả trong ranh giới: Nam Từ Liêm 9 đồn công
an, 1 đội chữa cháy và cứu nạn cứu hộ (khu vực 16), 1 bãi đỗ trực thăng; Hoàng Mai 27 đồn công an, 1 đội chữa cháy và cứu nạn
cứu hộ (khu vực 12); Punggol 3 đồn công an, 1 trạm cứu hoả; Downtown Core 1 đồn công an, 2 trạm cứu hoả. Đề xuất: trạm gốc là
đội chữa cháy và cứu nạn cứu hộ của khu vực, vì đây là lực lượng làm tìm kiếm cứu nạn và có sân để UAV cất hạ cánh; LoRa
gateway đặt ở đó. Khác bản đồ k8: trạm gốc nằm trong khu vực, không cách cell gần nhất 1 km.

**Cất cánh.** Đô thị không có đường băng, nên UAV cánh bằng là loại VTOL (cất hạ cánh thẳng đứng), như các mẫu ở mục 7. Tốc độ
và bán kính quay giữ như bản hiện tại.

**Độ cao bay.** Giữ 100 m so với mặt đất. Nhà từ 100 m (nới 50 m) là vùng cấm cho tour (K5): Downtown Core 10,9 % diện tích,
Yau Tsim Mong 8,6 %, Minato 8,7 %, Nam Từ Liêm 3,3 %. Gangnam có đồi gần 300 m, nên độ cao bay tính theo mặt đất bên dưới.

**Sức bền.** Các quận 5–60 km² nằm gọn trong một chuyến bay của loại VTOL 1–3 h (tour bản đồ k8 16 km² hết khoảng 13 phút).

## 23. Mạng thay đổi theo thời gian và số sự cố trong vòng đời (2026-11-20, mục 359)

**Số sự cố** [web; sửa và ghi nguồn ở mục 362]: Singapore nhận khoảng 1 300 báo cáo người mất tích mỗi năm trong 2021–2025
(tổng khoảng 6 500, khoảng 20 % chưa giải quyết), theo trả lời chất vấn Quốc hội của Bộ Nội vụ Singapore (MHA); số theo năm
1 211 (2022), 1 095 (2023), 1 355 (2024) theo Straits Times. Chia cho tổng dân số khoảng 6 triệu được khoảng 22 báo cáo mỗi
100 000 dân mỗi năm (khoảng 31 nếu chỉ tính 4,2 triệu cư dân); đây là phép chia của tôi. Anh và xứ Wales: khoảng 5,5 sự việc
mất tích mỗi 1 000 dân mỗi năm theo số của UK Missing Persons Unit (NCA) mà một tài liệu của cảnh sát Greater Manchester trích
lại; đếm cả lần báo lặp lại nên không so thẳng được. Dân số: Hoàng Mai 506 347 (điều tra 2019, qua Wikipedia và CityPopulation,
nguồn gốc là Tổng cục Thống kê), Punggol 204 490 cư dân năm 2026 (SingStat, Population Trends 2026, qua Mothership), Nam Từ
Liêm chưa tìm được số 2019. Áp tỉ lệ Singapore: Hoàng Mai khoảng 110–160 báo cáo mỗi năm, Punggol khoảng 45–65, tức một tới ba
lần mỗi tuần; chỉ một phần (trẻ em, người già sa sút trí tuệ, người có nguy cơ) cần tới nhiệm vụ UAV. Pha 0 vì vậy được chia
cho hàng chục truy vấn mỗi năm.

Nguồn trích dẫn được (cần mở bản gốc trước khi đưa vào bài; trang MHA không vào được từ container):
- MHA, "Written Reply to Parliamentary Question on Missing Persons in Singapore", https://www.mha.gov.sg/media-room/newsroom/written-reply-to-pq-on-missing-persons-in-singapore/
- MHA, "Breakdown of unresolved missing persons reports by age group and disability status", https://www.mha.gov.sg/media-room/newsroom/breakdown-of-unresolved-missing-persons-reports-by-age-group-and-disability-status/
- National Crime Agency, UK Missing Persons Unit, Annual Data Report 2022–23 (bản lưu): https://tnaqa.mirrorweb.com/ukgwa/20260803081315mp_/https://www.nationalcrimeagency.gov.uk/images/mpu/downloads/UKMPU%20Annual%20Data%20Report%202022-23.pdf
- SingStat, Population Trends 2026: https://www.singstat.gov.sg/publication-resources/population-trends-2026
- Tổng cục Thống kê, Kết quả Tổng điều tra dân số và nhà ở 2019 (cần tìm bản gốc cho số theo quận).
Nguồn thứ cấp chỉ dùng để tra, không trích: The Online Citizen, Straits Times (qua Magzter), Mothership, Wikipedia, CityPopulation.

**Mạng thay đổi.** Không tìm thấy số đo tỉ lệ thiết bị IoT gia đình ngoại tuyến, nên tỉ lệ vắng là giả định và được quét. Các
nghiên cứu đo lưu lượng nhà thông minh (Mazhar và Shafiq, IoTDI 2020, hơn 200 nhà, 1 237 thiết bị, arXiv 2001.08288; Kumar và
cộng sự, USENIX Security 2019) không báo độ sẵn sàng, nên không trích làm nguồn cho tỉ lệ vắng. Thử trên bản đồ thật (kênh có tường, có cột đèn ở cell cần; tắt ngẫu nhiên một
phần thiết bị, cột đèn giữ nguyên; log `logs/2026-11-19_1000-urban-nodes/*-absent.md`):

| Bản đồ | Thiết bị vắng | Cell đứt bên trong | Cặp kề thiếu gateway | Thành phần | Node điện lạc |
|---|---|---|---|---|---|
| Punggol | 0 % | 15 % | 1 % | 1 | 2,3 % |
| Punggol | 10 % | 20 % | 2 % | 1 | 2,8 % |
| Punggol | 20 % | 26 % | 3 % | 1 | 3,4 % |
| Punggol | 30 % | 32 % | 4 % | 1 | 4,8 % |
| Nam Từ Liêm | 0 % | 7 % | 1 % | 2 | 1,1 % |
| Nam Từ Liêm | 10 % | 8 % | 2 % | 2 | 1,6 % |
| Nam Từ Liêm | 20 % | 10 % | 2 % | 1 | 2,2 % |
| Nam Từ Liêm | 30 % | 13 % | 3 % | 1 | 2,9 % |

Lưới xuống cấp từ từ, vẫn là một khối liền khi 30 % thiết bị vắng, nhờ lớp cột đèn. Chỗ yếu thật là vai trò gắn với node cụ thể:
nếu đúng node CL hay node gateway vắng thì kế hoạch River tính từ topo cũ sẽ gửi vào chỗ không còn ai.

**Đề xuất chính sách pha 0** (người dùng còn cân nhắc, mục 363):
- Dựng đầy đủ một lần (lưới cell, CL, cặp gateway, cột đèn theo nhu cầu); làm lại khi thay đổi tích luỹ vượt ngưỡng.
- Cập nhật nhẹ định kỳ (ví dụ mỗi đêm): mỗi cell báo node còn sống và chất lượng liên kết lên trạm gốc.
- Trước mỗi nhiệm vụ: điểm danh nhanh trong cell, chọn lại CL và gateway nếu node cũ vắng, rồi trạm gốc phát kế hoạch; mỗi cạnh
  giữ một cặp gateway dự phòng.
- Trong mô phỏng: tỉ lệ thiết bị vắng là tham số (0, 10, 20 %); chi phí điểm danh và phát kế hoạch tính vào thời gian nhiệm vụ.

## 24. Nhiễu 2,4 GHz ở đô thị (2026-11-20, mục 364; chốt ở mục 365, việc K1d)

**Lịch kênh hiện tại trùng WiFi.** Kênh 802.15.4 số k ở 2405 + 5(k − 11) MHz, rộng 2 MHz; WiFi kênh 1, 6, 11 rộng khoảng 22 MHz
quanh 2412, 2437, 2462 MHz, nên chồng lên kênh 802.15.4 số 11–14, 16–19 và 21–24. Chỉ bốn kênh 15, 20, 25, 26 nằm ngoài WiFi
1/6/11; với cách đặt WiFi 1/5/9/13 kiểu châu Âu là 15, 16, 21, 22 [web: ICEST 2019; ghi chú ứng dụng]. Mô phỏng hiện dùng kênh
11 cho lượt bay (`coop-pass.cc`, `kChannel = 11`, chồng WiFi 1), kênh 11–17 cho 7 màu cell và 18–26 cho cặp gateway
(`coop2-river.cc`), tức phần lớn nằm dưới WiFi; mô hình chưa có nhiễu ngoài.

**Số đo đã có** [web, chưa đọc toàn văn; repo ghi ở chỗ có]:
- WiFi chủ yếu làm hỏng phần đầu (header) của khung 802.15.4 nên mất cả khung; thêm header và mã Reed–Solomon (BuzzBuzz) tăng
  tỉ lệ giao 70 % trên testbed (Liang, Priyantha, Liu, Terzis, SenSys 2010).
- Môi trường vô tuyến trong căn hộ đông và biến động hơn văn phòng nhiều (Sha và cộng sự, FIU, đo 16 kênh ở 10 căn hộ, IWQoS
  2011 và IEEE TNSM 2013).
- Đo 24 h ở một văn phòng: kênh 15, 20, 25, 26 giao 96–99,8 % gói, kênh 16–18 còn 80–91 % (blog cá nhân, không trích).
- Radio điều khiển của chính drone gây nhiễu: PRR 0,13–1,0 theo kênh [repo: `papers/dargie2021-lqe.md`]; Nekrasov 2019
  điều khiển drone ở 5,8 GHz để tránh [repo: `papers/nekrasov2019-aerial154.md`].
- Chưa tìm thấy số đo phần trăm thời gian bận của WiFi ngoài phố đô thị; báo cáo Ofcom (ARMMS 2014) và Hà Lan (2017) chỉ nói
  2,4 GHz nghẽn, trung tâm thương mại tệ nhất.

**Đề xuất cho mô hình:**
- Lượt bay chuyển sang kênh sạch (26), vì gói A2G mất là phần River phải bù.
- Ba kênh sạch còn lại dành cho các môi trường bận nhất (cell Bank và cell trung chuyển dọc River, theo trace mục 9 của bản
  thảo); các cell và cặp gateway khác chấp nhận chung kênh với WiFi.
- Thêm mô hình nhiễu: mỗi kênh trùng WiFi có độ bận u (phần thời gian WiFi phát) theo cell; khi bận, CSMA lùi lại và khung đang
  phát hỏng với xác suất u; mất gói theo cụm (hai trạng thái tốt/xấu). Quét u = 0, 0,2, 0,5.
- UAV điều khiển ở băng khác 2,4 GHz (900 MHz hoặc 5,8 GHz).
- Phương án xa hơn: 802.15.4 băng dưới 1 GHz tránh hẳn WiFi, nhưng Thread và thiết bị nhà thông minh hiện ở 2,4 GHz.

## 25. Đánh thức và đồng bộ (2026-11-20, mục 365; chốt ở mục 367)

**Ai phải thức.** Node chuyển tiếp (cột đèn, thiết bị dọc phố, thiết bị trên nhà cắm điện) cắm điện nên luôn bật radio, không cần
đánh thức. Node chạy pin (11–22 %) là node lá: không chuyển tiếp, không bao giờ là AI node, nên không cần truy vấn. Đề xuất: node
pin không tham gia pha 1, chỉ nghe lượt bay nếu tình cờ đang thức; xác suất nhận ở mức cell P_k tính trên node cắm điện. Vấn đề
"đánh thức" vì vậy thu về chuyện chỉnh kênh đúng lúc của node cắm điện.

**Chỉnh kênh đúng lúc.** Lúc rảnh, node cắm điện nghe trên kênh cell của mình; lượt bay phát trên kênh 26 (K1d). Mỗi cell phải
chuyển sang kênh 26 trong cửa sổ UAV bay qua. Cửa sổ ngắn: UAV bay 25–50 m/s, tầm nhận ở đô thị dày khoảng 200 m, nên một cell
gần đường bay nghe được khoảng 10–15 s; cả cụm (khoảng 1,6 km) khoảng 1 phút.

**Đề xuất: kế hoạch tính sẵn, nhiệm vụ chỉ cần một bản tin bắt đầu.**
- Tập critical cell, tour và kế hoạch River chỉ phụ thuộc bản đồ và tập critical cell, không phụ thuộc truy vấn, nên trạm gốc tính
  sẵn ở pha 0 (cập nhật mỗi đêm khi mạng thay đổi, mục 23) và phát xuống mọi cell trước.
- Khi có sự cố, trạm gốc chỉ phát qua LoRa một bản tin vài byte (mã nhiệm vụ, giờ cất cánh, mã kế hoạch); một khung SF7 khoảng
  0,35 s. CH truyền tiếp trong cụm qua 802.15.4, khoảng 30 chặng node, dưới 1 s. Mỗi cell tự tính cửa sổ chuyển kênh từ kế
  hoạch và giờ cất cánh.
- Đồng bộ đồng hồ: thạch anh thường lệch cỡ vài chục ppm, tức vài giây mỗi ngày; đồng bộ lại mỗi đêm cùng lúc cập nhật kế hoạch,
  và bản tin bắt đầu mang giờ của trạm gốc, nên sai số còn cỡ dưới 1 s. Cửa sổ mở rộng thêm vài giây mỗi phía.
- Nếu UAV lệch kế hoạch (gió, đổi đường), UAV phát kèm vị trí trong header gói (đã có trong takeover); cell nghe thấy gói thì
  giữ kênh 26 tới khi hết nghe.

**Hệ quả cho mô hình:** thời gian từ lúc có sự cố tới khi cất cánh gồm một khung LoRa và vài giây phát trong cụm; P_k giảm vì bỏ
node pin (khoảng 78–89 % node còn lại); không cần mô hình ngủ/thức cho node chuyển tiếp.

## 26. Vị trí node (2026-11-20, mục 367, đề xuất để bàn)

**Vị trí dùng vào đâu.** Trạm gốc cần toạ độ node để: gán node vào cell, chọn CL và cặp gateway, lập kế hoạch River và tour, xét LoS
A2G và G2G với nhà (K1a, K1c), và chọn điểm lơ lửng của V1.

**Lấy vị trí từ đâu, sai số bao nhiêu:**
- Cột đèn: thành phố có bản đồ hạ tầng, sai số dưới vài mét (giả định, chưa có nguồn).
- Thiết bị nhà dân: ghi lúc thiết bị tham gia mạng, bằng GPS điện thoại của người cài đặt hoặc địa chỉ lắp đặt. GPS điện thoại
  ngoài trời thoáng sai trong bán kính khoảng 4,9 m (GPS.gov, dẫn ION); gần nhà cao tầng và trong nhà kém hơn nhiều, chưa có số
  đo trích được cho phố đô thị. Địa chỉ chỉ cho tới toà nhà, không cho tầng.
- Định vị trong mạng theo cường độ tín hiệu: sai hàng chục mét, chỉ dùng để kiểm chéo.

**Sai số ảnh hưởng thế nào** (tính mới, Monte Carlo trên lưới lục giác R = 100 m): node bị gán sang cell khác 2,8 % khi sai số
3 m, 4,6 % khi 5 m, 9,0 % khi 10 m, 17,7 % khi 20 m, 26,2 % khi 30 m. Với V1, lệch ngang 20 m làm xác suất gói qua ở khu cao tầng
từ 0,87 xuống 0,73 (mục 17).

**Đề xuất:**
- Gán cell theo kết nối thật ở pha 0 (node thuộc cell của CL mà nó nối được tốt nhất), toạ độ chỉ để khởi tạo; như vậy sai số vị
  trí không làm sai cấu trúc cell.
- Mỗi thiết bị kèm một nhãn vị trí thô: ngoài trời (cột, mặt tiền) hay trong nhà, và tầng nếu có; thiết bị trong nhà bị trừ suy hao
  xuyên tường khoảng 15–20 dB với A2G (như biến thể indoor của `a2g_radius.py`).
- Trong mô phỏng: kế hoạch dùng toạ độ có nhiễu σ = 10 m (cột đèn 2 m), kênh dùng toạ độ thật, để đo độ bền của kế hoạch.
- V1: UAV lơ lửng theo toạ độ ghi sẵn rồi dò quanh theo cường độ tín hiệu nếu gói hỏng nhiều.

Nguồn: GPS.gov, "GPS Accuracy", https://www.gps.gov/systems/gps/performance/accuracy/ (trang ghi không cập nhật từ 2/2025).
