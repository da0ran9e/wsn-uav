---
status: current
updated: 2026-11-06
---
# Đề cương nghiên cứu SigDrop (bản nháp)

Đưa truy vấn nhận dạng xuống mạng camera IoT bằng UAV: tổ chức mạng theo lưới cell, lập quỹ đạo và phân phối dữ liệu
dưới mặt đất có kế hoạch.

Bản nháp theo khung người dùng đưa ngày 2026-11-06 (`docs/chatlog/2026-11.md`, mục 276–278). Mọi con số ở mục 4 lấy từ
`docs/EXPERIMENTS-INDEX.md`. Chỗ ghi **[cần chốt]** là chỗ người dùng cần quyết định.

---

## 1. Tóm tắt

Sau một sự việc (trẻ lạc, truy vết đối tượng), hàng nghìn camera IoT trong khu vực có thể đã ghi lại mục tiêu, nhưng
không biết phải tìm ai. Tải dữ liệu thô về trạm gốc (BS) thường không khả thi, vì băng thông ít (LoRa, vệ tinh) hoặc vì
vướng pháp lý. SigDrop làm ngược lại: đưa **truy vấn**, tức một bộ ảnh tham chiếu vài trăm KB, xuống các node biên bằng
UAV cánh bằng, để node tự đối sánh với kho của mình và chỉ báo về một điểm số.

Giải pháp có ba pha:
- **Pha 0:** tổ chức mạng một lần theo lưới cell lục giác (CL, cặp gateway, định tuyến, lịch kênh).
- **Pha 1:** UAV bay một lượt qua mỗi cụm theo quỹ đạo lập sẵn (CHORD, LM-Tour). Cơ chế **River** phân phối dữ liệu
  dưới mặt đất theo kế hoạch BS tính trước (SPINE → Bank → Ring → critical cell), nên không cần khám phá nội dung lúc chạy.
- **Pha 2:** đội UAV thứ hai xác minh các cell nghi vấn.

Kết quả bước đầu (bài ICC 2027, ns-3):
- LM-Tour + River nhanh nhất trong các phương án thực tế.
- Ở kênh xấu, River nhanh hơn phương án fountain code không hợp tác 49–72 %.
- So với Deluge/Trickle trên cùng lượt bay, River dùng ít frame hơn 1,9–2,5 lần.

Giai đoạn tiếp theo nhằm:
- chứng minh chặt hơn (mô hình, cận dưới);
- làm giao thức bền vững trong điều kiện thực tế (sai lệch đường bay, node hỏng);
- mở rộng quy mô;
- kiểm chứng trên phần cứng.

## 2. Đặt vấn đề và tính cấp thiết

### 2.1 Bối cảnh
- **Mạng camera IoT đô thị dày đặc nhưng phân mảnh:** camera an ninh, chuông cửa, máy bán hàng, camera hành trình.
  Mỗi thiết bị có năng lực khác nhau và ghi đè dữ liệu cũ sau vài ngày.
- **Ở nơi hoang dã** (rừng, khu bảo tồn), node chỉ có LoRa hoặc vệ tinh, vài trăm byte mỗi giờ.
- **UAV là phương tiện tự nhiên** để mang dữ liệu lớn tới một vùng rộng trong thời gian ngắn.

### 2.2 Vấn đề cụ thể và khó khăn kỹ thuật
Giao một tập Q gói (khoảng 400 KB) tới mọi **critical cell** (CL đủ mạnh để đối sánh), từ một UAV cánh bằng bay một
lượt, trong thời gian ngắn nhất. Các khó khăn:
- **Kênh A2G 802.15.4:**
  - tầm phát hiệu quả chỉ 100–1000 m tuỳ môi trường;
  - fading đổi theo từng gói;
  - node xa đường bay mất nhiều gói.
- **UAV cánh bằng:**
  - không thể hover;
  - bán kính quay tối thiểu khoảng 64 m ở 25 m/s;
  - mỗi cụm chỉ được bay qua một lần.
- **Liên kết G2G yếu hơn A2G nhiều:**
  - NLoS, thông lượng thấp;
  - tranh chấp kênh khi nhiều cell trao đổi cùng lúc.
- **Miền không lồi:** có hồ, khu cấm bay; cụm có hình dạng bất kỳ.

### 2.3 Khoảng trống của các cách hiện có (chi tiết ở mục 3)
- **Phổ tán trong WSN (Deluge, Trickle):** tìm dữ liệu thiếu lúc chạy bằng quảng bá và yêu cầu. Cách này tốn frame và
  buộc radio luôn nghe; nó cũng không biết node nào quan trọng.
- **Fountain code không hợp tác:** UAV phải bay vòng hoặc giảm tốc ở từng critical cell, nên tour rất dài khi kênh xấu.
- **Các nghiên cứu UAV–WSN:** phần lớn xét chiều thu dữ liệu từ node lên UAV, hoặc giả định UAV hover. Hiếm có nghiên
  cứu phân phối xuống bằng cánh bằng có lập kế hoạch phối hợp với mạng mặt đất.

### 2.4 Nhận xét then chốt
- **Gói nào rơi xuống đâu là đoán trước được.** Đường bay và chỉ số gói đã biết trước, nên BS tính được trước khi cất
  cánh. Pha 0 tổ chức sẵn lưới cell, gateway và lịch kênh, nên BS giao được cho từng cell một vai trò và một đoạn dữ liệu.
  Phân phối dưới mặt đất trở thành **thực thi kế hoạch** thay vì khám phá.
- **Quỹ đạo và phân phối dưới mặt đất phải thiết kế cùng nhau.** Lượt bay quyết định SPINE ở đâu và River dài bao
  nhiêu; River quyết định critical cell nào cần UAV bay gần.

### 2.5 Vì sao cấp thiết
- **Bằng chứng bị ghi đè sau vài ngày,** nên thời gian hoàn thành nhiệm vụ T\* là chỉ số chính.
- **Pháp lý và quyền riêng tư:** chỉ có điểm số rời khỏi node, dữ liệu thô không ra ngoài.
- **Phương án cứu hộ ở nơi không có hạ tầng.**

## 3. Tổng quan nghiên cứu

| Mục | Nội dung | Tài liệu tiêu biểu (cần kiểm tra lại trích dẫn) |
|---|---|---|
| 3.1 Phổ tán dữ liệu trong WSN | phát lại mã, cập nhật firmware, advertise–request | Deluge (Hui & Culler 2004), Trickle (Levis 2004; RFC 6206), MNP |
| 3.2 Mã hoá | fountain (LT, Raptor), network coding cho phổ tán | Luby 2002, Shokrollahi 2006, Rateless Deluge |
| 3.3 UAV multicast và phân phối dữ liệu bằng UAV | UAV làm trạm phát, chiều ngược lại là thu dữ liệu; data ferrying, DTN | Zeng–Zhang (UAV comm.), message ferrying (Zhao 2004) |
| 3.4 Lập quỹ đạo UAV | Dubins TSP với vùng lân cận (DTSP-N), quỹ đạo cánh bằng có ràng buộc độ cong | Dubins 1957, các thuật toán DTSPN |
| 3.5 Kênh A2G | mô hình xác suất LoS, suy hao hai đoạn, fading Rician/Nakagami | Al-Hourani 2014, Qiu 2017 |
| 3.6 Tổ chức mạng và lập lịch | phân cụm, lưới địa lý, lập lịch kênh và khe | LEACH, HEED, GAF; TSCH, 6TiSCH (RFC 9030); PECEE |
| 3.7 Tìm kiếm tại biên (lớp 1, ngắn) | re-ID mở, đối sánh embedding trên thiết bị biên | Market-1501 open-world (arXiv 1807.10482), `research_notes/l1-*` |
| 3.8 Học máy cho lập quỹ đạo | surrogate dự đoán chi phí, tối ưu có mô hình | cần khảo sát |

Cuối mục có **bảng định vị**: các nhóm phương pháp × các tiêu chí sau:
- biết trước nội dung;
- đơn vị lập kế hoạch là cell;
- UAV cánh bằng bay một lượt;
- hợp tác mặt đất có lịch;
- kiểm chứng packet-level.

## 4. Kết quả bước đầu

### 4.1 Bài ICC 2027
Bản nộp v5.3, LaTeX ở `paper/icc-v5/`. Đóng góp chính: River, CHORD/LM-Tour, đánh giá ns-3 3.46 lr-wpan đầy đủ (MAC
802.15.4, CSMA/ACK, lịch kênh 7 màu).

### 4.2 Kết quả chính
| Mã | Kết quả |
|---|---|
| C4 | 3 bản đồ (8/12/15 cụm) × 4 kênh × tới 10 seed. LM-Tour + River nhanh nhất trong các phương án thực tế: nhanh hơn CHORD + River 1–11 %, DTSP-N + River 10–26 %, FC + DTSP-N 10–72 %. Ở r200/r100, các phương án có River nhanh hơn FC + DTSP-N 49–72 % |
| LMT, T3S | Bộ dự đoán thời gian River dùng cho LM-Tour (812 critical cell); dạng cây có sai số 26,2 s so với 45,9 s của công thức tuyến tính |
| DLG | Cùng lượt CHORD, r100, 5 seed: so với Deluge, River sẵn sàng sớm hơn (117 so với 149–156 s), ít frame hơn 1,9–2,5 lần, ít năng lượng radio hơn 6,5–8,8 lần khi ngủ theo lịch; T\* nhanh hơn 36–43 s, thắng 5/5 seed |
| WND, TKO | Gió σ = 100 m (lệch ngang tới 346 m): River không sửa lỗi chỉ xong 106/135 critical cell, T\* +294 s. Có takeover tuần tự: 135/135 cell, sẵn sàng 112–118 s, T\* bằng danh nghĩa trong phạm vi nhiễu (−22 ± 184 s) |

### 4.3 Giới hạn còn lại
- C4 dừng ở 290/360 job. Mỗi ô có 6–10 seed; có một lỗi segfault tất định (`lmd 4 r500 16`).
- Takeover: khám phá cell giữ gói còn dựa vào bit nhận thật. Đường REPORT theo tọa độ trong header chưa được mô phỏng.
- Gió σ = 200 m mới có 1 seed; đường bay có lúc vượt 1 g.
- Deluge-lite trên LM-Tour (k12) đang tạm dừng.
- Năng lượng UAV chưa đối chiếu hệ số c₁, c₂ của Zeng–Zhang.
- Pha 0 được tính sẵn, chưa mô phỏng bằng frame; lớp 1 chỉ là mô hình điểm khớp.

## 5. Mục tiêu và câu hỏi nghiên cứu

### 5.1 Mục tiêu tổng quát
Xây dựng và kiểm chứng một kiến trúc phân phối truy vấn bằng UAV cho mạng camera IoT. Kiến trúc này phải đạt thời gian
hoàn thành gần cận dưới, bền vững với sai lệch thực tế và chạy được trên phần cứng 802.15.4.

### 5.2 Mục tiêu cụ thể
- MT1: mô hình hoá bài toán, chứng minh độ khó và tìm cận dưới của T\*.
- MT2: hoàn thiện River và takeover thành giao thức chạy được, không dựa vào oracle.
- MT3: thiết kế quỹ đạo dùng bộ dự đoán học từ mô phỏng, có đánh giá tổng quát hoá.
- MT4: đánh giá ở quy mô lớn, nhiều bản đồ và nhiều kịch bản lỗi.
- MT5: kiểm chứng trên testbed hoặc thực địa, nếu có điều kiện.

### 5.3 Câu hỏi nghiên cứu
- **RQ0** (ND0): chi phí dựng và duy trì lưới cell (frame, thời gian, năng lượng) là bao nhiêu, và nó thay đổi thế nào
  theo mật độ node?
- **RQ1** (ND1): cận dưới của T\* là bao nhiêu, và River cùng LM-Tour cách cận đó bao xa?
- **RQ2** (ND2): lập kế hoạch trước có lợi hơn khám phá lúc chạy đến mức nào, và trong điều kiện kênh, mật độ nào?
- **RQ3** (ND2, ND4): River chịu được sai lệch đường bay, node hỏng và kênh xấu tới mức nào?
- **RQ4** (ND3): bộ dự đoán giúp quỹ đạo tốt hơn bao nhiêu so với CHORD, và có tổng quát hoá sang bản đồ mới không?
- **RQ5** (ND5): kết quả mô phỏng còn giữ được bao nhiêu trên phần cứng thật?

### 5.4 Đóng góp dự kiến
1. Kiến trúc ba pha, với phân phối dưới mặt đất được lập kế hoạch trước.
2. Giao thức River kèm takeover tự thích ứng với sai lệch đường bay.
3. Lập quỹ đạo có bộ dự đoán (LM-Tour).
4. Mô hình và cận dưới.
5. Bộ mô phỏng ns-3 và dữ liệu công khai.

## 6. Đối tượng và phạm vi

### 6.1 Đối tượng nghiên cứu
Mạng camera IoT 802.15.4 không đồng nhất, tổ chức theo lưới cell. UAV cánh bằng (pha 1) và UAV cánh quay (pha 2).
Truy vấn là một bộ ảnh tham chiếu khoảng 400 KB.

### 6.2 Trong phạm vi / ngoài phạm vi
| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Pha 0 (lưới cell), pha 1 (lớp 2 quỹ đạo, lớp 3 River), pha 2 ở mức mô hình thời gian | Thuật toán nhận dạng ảnh (lớp 1): chỉ dùng mô hình điểm khớp đã chốt, trích từ các công bố |
| Kênh A2G và G2G, MAC 802.15.4, năng lượng radio và UAV | Bảo mật, quyền sở hữu thiết bị: chỉ nêu ở phần hướng mở |
| Miền không lồi có vật cản mềm | Vật cản cứng và khu cấm bay: **[cần chốt]** đưa vào ND4 hay để sau |

### 6.3 Giả định chính
- Pha 0 hoàn tất trước nhiệm vụ. Lưới, CL, cặp gateway, định tuyến và lịch kênh giữ nguyên suốt nhiệm vụ, và BS biết
  toàn bộ.
- Node đứng yên. UAV biết vị trí của mình (GPS) và có thể ghi tọa độ vào header gói.
- Ảnh không thay thế cho nhau: critical cell cần đủ Q gói.
- Kênh phản hồi về BS là LoRa hoặc vệ tinh, độ trễ có giới hạn chu kỳ phát.

### 6.4 Chỉ số đánh giá
- **T\*:** thời gian hoàn thành nhiệm vụ, trung bình 100 lượt lớp 1 ghép cặp mỗi seed.
- **Thời điểm sẵn sàng:** với mỗi cụm, lúc critical cell cuối cùng xong, tính từ khi UAV rời cụm; sau đó lấy trung bình
  qua các cụm.
- **Tỉ lệ critical cell xong.**
- **Số frame mặt đất.**
- **Năng lượng radio** (tổng và node nóng nhất; CC2420 và EFR32), **năng lượng UAV** (mô hình có gia tốc).

## 7. Nội dung và phương pháp nghiên cứu

### 7.0 Phương pháp chung
- **Công cụ:** ns-3.46 lr-wpan và các binary đóng băng (sha256 trong log). Python cho lập quỹ đạo và lớp 1. Tham số
  tập trung ở `params.yaml`.
- **Thống kê:**
  - CI 95 % theo seed;
  - so sánh ghép cặp trên cùng lượt bay và cùng kênh;
  - tối thiểu 5 seed cho kết luận chính;
  - không kết luận từ một seed;
  - báo cáo cả số seed thắng.
- **Baseline:** Deluge/Trickle (phạm vi cell River và phạm vi đường), kéo trực tiếp, FC + DTSP-N, DTSP-N + River, CHORD.
- **Tái lập:** mỗi lần chạy có thư mục `logs/` kèm README và mã thí nghiệm trong `docs/EXPERIMENTS-INDEX.md`.

### 7.1 ND0. Tổ chức mạng theo lưới cell (pha 0)
- **Đã có:**
  - lưới lục giác R = 100 m; mỗi cell một CL;
  - mỗi cặp cell kề một cặp gateway;
  - định tuyến PECEE (next hop tới CL và tới từng cell kề);
  - lịch kênh 7 màu;
  - cụm tối đa 80 cell; CH và critical cell do BS chọn.
- **Việc cần làm:**
  - mô phỏng dựng pha 0 bằng frame thật: bầu CL, chọn gateway, phát bảng định tuyến;
  - đo chi phí theo số node và mật độ;
  - bảo trì khi node hỏng hoặc thêm node;
  - quét kích thước cell so với tầm phát và số màu kênh;
  - tái cấu trúc cụm cho quỹ đạo (LANE, MEANDER: đã thử, chưa thắng CHORD).

### 7.2 ND1. Mô hình hoá bài toán và cận dưới
- Phát biểu bài toán tối ưu chung: tour × phân công Seg × lịch River. Chứng minh NP-khó (quy về DTSP-N).
- Cận dưới của T\*:
  - phần bay: tour Dubins tối thiểu qua đĩa các CH;
  - phần mặt đất: dòng cực đại trên đồ thị cell với dung lượng gateway.
- Mô hình giải tích thời điểm sẵn sàng của River, đối chiếu với bộ dự đoán ở LMT.

### 7.3 ND2. Giao thức River và takeover
- **Takeover thực tế:**
  - REPORT dựa trên tọa độ trong header, theo mã giả đã chốt ngày 2026-11-02;
  - so sánh ba cách: theo tọa độ header, SPINE cell tự hỏi lan, và oracle.
- **Các biến thể Ring và Bank;** các câu hỏi phụ đã ghi:
  - độ rộng River tối ưu;
  - ghép Ring khi hai critical cell nằm cạnh nhau;
  - Bank theo pháp tuyến cục bộ khi SPINE cong.
- **Năng lượng có lịch ngủ thật:** mô phỏng node tắt radio, thay cho chặn trên lấy sau khi chạy.
- **So sánh đầy đủ với Deluge-lite** (page không theo thứ tự, NACK bitmap) trên LM-Tour.

### 7.4 ND3. Thiết kế quỹ đạo và surrogate
- Bộ dự đoán thời gian River: thêm đặc trưng, kiểm định chéo theo bản đồ, đo tổng quát hoá sang bản đồ chưa thấy.
- LM-Tour:
  - chọn ξ;
  - điều kiện dừng khi lợi ích bão hoà;
  - ràng buộc gia tốc 1 g;
  - năng lượng UAV trong hàm mục tiêu.
- Nhiều UAV pha 1: chia cụm cho các UAV.

### 7.5 ND4. Đánh giá mô phỏng quy mô lớn
- Hoàn tất C4 và mở rộng lên 10 bản đồ mỗi cỡ, đủ 10 seed.
- **Độ bền vững:** gió σ 50–200 m (đủ seed), node hỏng ngẫu nhiên 5–20 %, sai lệch kênh so với mô hình lập kế hoạch,
  vật cản.
- **Khả năng mở rộng ns-3:** cụm tới khoảng 2 000 node; nếu cần, đánh giá mô phỏng song song (MPI).

### 7.6 ND5. Kiểm chứng thực địa (nếu có điều kiện)
- **Bậc 1:** testbed 802.15.4 thật (FIT IoT-LAB hoặc 20–50 node nRF52840 trong phòng thí nghiệm). Chạy River trên lịch
  thật, UAV thay bằng một node phát di động.
- **Bậc 2:** PX4 SITL ghép ns-3 để kiểm quỹ đạo và động học.
- **Bậc 3:** bay thật trên một cụm nhỏ (khoảng 30 node), nếu có giấy phép bay.

## 8. Kết quả dự kiến và sản phẩm

### 8.1 Bài báo
| Bài | Nội dung | Nơi dự kiến | Thời điểm |
|---|---|---|---|
| B0 | Bài ICC 2027 (đã nộp) | IEEE ICC 2027 | kết quả khoảng 01/2027 |
| B1 | Bản mở rộng: ND1 + ND2 + ND4 | IEEE TWC / IEEE IoT-J **[cần chốt]** | nộp khoảng 06/2027 |
| B2 | Pha 0 và takeover trên testbed (ND0 + ND5) | INFOCOM / SECON / IPSN **[cần chốt]** | khoảng 09/2027 |
| B3 | LM-Tour với bộ dự đoán học được (ND3) | IEEE TMC hoặc hội nghị ML cho mạng | khoảng 12/2027 |

### 8.2 Mã nguồn, dữ liệu
- Bộ mô phỏng ns-3 (`uav-coop/`, `uav-coop2/`) và công cụ lập quỹ đạo (`uav-l2/tools/`), công khai khi bài được nhận.
- Bộ dữ liệu: bản đồ, lượt bay, bit nhận và kết quả chiến dịch (CSV), kèm `params.yaml`.

## 9. Kế hoạch thực hiện

### 9.1 Các giai đoạn (tính từ 12/2026) [cần chốt]
| Giai đoạn | Tháng | Nội dung | Mốc kiểm tra |
|---|---|---|---|
| G1 | 12/2026–02/2027 | ND1 (mô hình, cận dưới); hoàn tất C4; trả lời phản biện ICC | Cận dưới và khoảng cách tới LM-Tour trên 3 bản đồ |
| G2 | 01–04/2027 | ND2 (takeover thực tế, Deluge-lite, năng lượng có lịch ngủ) | Takeover theo tọa độ header không dùng oracle, 5 seed σ = 100 m |
| G3 | 03–06/2027 | ND4 (quy mô lớn, độ bền vững); viết B1 | Bảng độ bền vững đủ 10 seed; nộp B1 |
| G4 | 04–08/2027 | ND0 (pha 0 bằng frame); ND5 bậc 1–2 | Chi phí pha 0 theo mật độ; River chạy trên testbed |
| G5 | 07–12/2027 | ND3 (bộ dự đoán, nhiều UAV); ND5 bậc 3 nếu có điều kiện; viết B2, B3 | Bộ dự đoán tổng quát hoá sang bản đồ mới |

### 9.2 Mốc kiểm tra định lượng
- River nhanh hơn Deluge-lite ≥ 15 % về sẵn sàng ở r100 (≥ 5 seed), hoặc ít frame hơn ≥ 2 lần nếu thời gian ngang nhau.
- Takeover không oracle: 100 % critical cell xong ở σ = 100 m; sẵn sàng chậm hơn danh nghĩa ≤ 10 %.
- LM-Tour cách cận dưới ≤ 30 % **[giá trị cần chốt sau ND1]**.

## 10. Rủi ro và phương án dự phòng

| Rủi ro | Mức | Dự phòng |
|---|---|---|
| ns-3 không chạy nổi cụm lớn hoặc nhiều bản đồ | trung bình | Chia cụm độc lập (đã làm), chạy song song nhiều phiên cloud; giảm chi tiết MAC cho phần không cần |
| Lợi thế so với Deluge-lite nhỏ | trung bình | Đóng khung theo frame và năng lượng ("cùng thời gian, ít frame hơn, không cần khám phá"), như góp ý của reviewer |
| Giả định lớp 1 bị phản biện | trung bình | Phân tích độ nhạy theo tham số điểm khớp; hợp tác với nhóm thị giác máy |
| Không có điều kiện thực địa | cao | Dừng ở testbed (bậc 1–2); vẫn đủ cho bài tạp chí |
| Quota tính toán và thời gian | trung bình | Ưu tiên ô r100 nhiều seed, chạy ghép cặp, chỉ chạy lại các cụm bị ảnh hưởng (như TKO) |
| Mô hình kênh lệch thực tế | trung bình | Quét độ nhạy α, m Nakagami; testbed đo PER thật để hiệu chỉnh |

## Phụ lục
- **Tham số:** sinh bảng từ `params.yaml` (`python3 tools/params.py`).
- **Tài liệu tham khảo:** **[cần lập]** từ mục 3 và danh mục của bài ICC.
- **Nguồn lực:** máy chạy mô phỏng (cloud), thiết bị testbed **[cần chốt]**, UAV và giấy phép bay nếu làm ND5 bậc 3.
