---
status: current
updated: 2026-11-19
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
| Thiết bị | Nhiều thiết bị IoT có sẵn: camera, cảm biến; phần lớn là node yếu, một số node mạnh chạy được AI | chốt |
| Sự cố | Mục tiêu điển hình là tìm người (mục 335): truy vấn là bộ ảnh tham chiếu của người cần tìm, AI node đối sánh với ảnh camera đã gửi về; mạng phục vụ nhiều lượt truy vấn trong suốt vòng đời | chốt |
| Phân bố thiết bị | Rải ngẫu nhiên, càng đều càng tốt, phủ cả vùng (mục 325). Mật độ giữ như bản hội nghị (khoảng 816 node/km²) như giả định hướng tới: mạng dày chưa phổ biến nhưng nhiều khả năng sớm có (mục 335); chạy thêm vài mức để xem độ nhạy | chốt |
| Vì sao cần UAV | Hai lý do (mục 343): node rẻ chỉ có radio 802.15.4, không nối Internet; dữ liệu phải ở lại thiết bị vì quyền riêng tư, chỉ điểm số vài byte rời node. Qua LoRa mất ít nhất 1,8 h, qua mạng mặt đất từ trạm gốc xem mục 12. Chi tiết ở mục 15 | chốt (lý do), đề xuất (lập luận) |

## 2. Thực thể

| Thực thể | Mô tả | Trạng thái |
|---|---|---|
| Trạm gốc (BS) | Lập kế hoạch pha 0, pha 1 (tour và kế hoạch River), nhận kết quả qua LoRa | chốt |
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
| Diện tích vùng | 617 cell ≈ 16 km² (bản đồ k8) | vừa một chuyến bay của một UAV; ước lượng thô khoảng 100 km², cỡ 50 cụm (mục 7) | chốt (nguyên tắc), mở (con số) |
| Số cell | 617 | khoảng 4 000 nếu 100 km² và giữ R = 100 m | mở (giữ R hay tăng R) |
| Mật độ node | khoảng 21 node một cell (13 086 node) | giữ khoảng 816 node/km² làm mức chính (hướng tới, mục 335); thêm 400 và 280 node/km² để xem độ nhạy (vẫn trong vùng lưới cell liên thông, mục 10) | chốt (mức chính), đề xuất (mức phụ) |
| Số CC | 45 CC trên 8 cụm (k8), cho sẵn theo bản đồ | J1 giải bài chọn CC (mục 335), số CC là một phần lời giải | chốt |
| Kênh A2G, G2G | A2G hai đoạn + suy hao môi trường cố định, Rician K = 2; G2G 3GPP UMi NLoS | làm phức tạp dần theo từng bước (mục 335): LoS phụ thuộc góc ngẩng, che khuất tương quan, fading tương quan, cấu trúc phố hay địa hình cho G2G (mục 9; việc K1) | chốt (hướng), đề xuất (thứ tự bước) |
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

- a. Giữ R = 100 m: mục 10 cho thấy giới hạn giãn cách do tầm G2G quyết định, không do R; mật độ chính giữ như bản hội
  nghị (mục 335).
- b. Đã trả lời (mục 327): một chuyến bay, vùng thu lại cho vừa. Còn mở: chọn sức bền bao nhiêu (mục 7 gợi ý 1,5 h).
- c. Đã trả lời (mục 326): một UAV; nhiều UAV để sau, mục tiêu min-max, phối hợp chứ không chia việc.
- d. Đã trả lời (mục 335): tìm người.
- e. Vì sao không phát truy vấn từ trạm gốc qua mạng mặt đất hay qua LoRa: phép tính ở mục 12 (mục 334). Còn mở: cách
  bài đối đáp với kiểu flood đồng bộ (Pando).
- f. Số sự cố trong vòng đời mạng (để chia chi phí pha 0).
- g. Môi trường như bài giả định có thật không, mỗi cụm thường rộng bao nhiêu (mục 327), mật độ node thường gặp (mục 329),
  kích thước vùng đô thị và kênh có hợp với đô thị không (mục 332), pháp lý UAV đô thị và giãn cách node
  tối đa (mục 333). Đối chiếu ở mục 7–11.
- h. Đã trả lời (mục 343): hướng 1 (node chỉ có 802.15.4) và hướng 4 (giữ dữ liệu tại chỗ). Lập luận ở mục 15.
- i. (mục 342) Ai sở hữu và vận hành mạng, ai chạy pha 0, thiết bị của chủ khác nhau có tham gia không.
- j. Phần lớn đã trả lời (mục 344): không giới hạn thời gian, tìm tới khi thấy (chỉ bị chặn bởi năng lượng UAV); camera
  trả lời "thấy người trông giống mục tiêu". Cửa sổ mặc định 2 giờ (mục 345).
- k. (mục 342) Pha 2 ở đô thị cao tầng: UAV cánh quay bay thấp giữa nhà, xác minh nghĩa là gì (tới chỗ camera, nhận ảnh
  cắt qua UAV, hay báo người đến hiện trường).
- l. (mục 342) Vận hành UAV ở đô thị: điểm cất cánh, độ cao bay khi có nhà cao hơn 100–120 m, vùng cấm bay, sức bền.
- m. (mục 342) Nguồn điện của node: cắm điện lưới hay pin; quyết định năng lượng có phải ràng buộc không.

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

Còn mở: pha 2 kết thúc ở đâu. Đề xuất: V1 xác nhận đúng lần thấy (mức dữ liệu) là kết thúc pha 2 của bài; V4 (tìm thấy người
ngoài thực địa) là bước tiếp theo, chỉ làm khi lần thấy đã xác nhận còn đủ mới.
