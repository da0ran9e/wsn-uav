---
status: current
updated: 2026-11-20
---
# Kế hoạch kỹ thuật: node thường gửi gì về AI node, và số critical cell tối ưu

Kế hoạch chi tiết cho K9, K12, K13 trong [PLAN-TRACKS](PLAN-TRACKS-vi.md) (chatlog mục 338, 339). Bối cảnh ở
[CONTEXT](archive/urban-v1/CONTEXT-vi.md) mục 13–14. Chưa chạy gì; các bước có ns-3 cần người dùng duyệt chi phí trước (mục 35).

## 1. Câu hỏi

1. Với mỗi cách gửi dữ liệu về AI node, số critical cell tối ưu là bao nhiêu, và tổng thời gian pha 1 + pha 2 bằng bao
   nhiêu?
2. Cách nào khả thi về luồng nền G2G, năng lượng và bộ nhớ ở mật độ 816 node/km²?
3. Kết luận đổi thế nào theo tốc độ đối sánh (bậc thiết bị), lưu lượng người qua camera, kênh A2G (đô thị dày, cao
   tầng) và mật độ?

## 2. Bốn phương án dữ liệu

| Mã | Node thường gửi về AI node | Cỡ mỗi người | Việc ở node thường | Việc ở AI node khi có truy vấn |
|---|---|---|---|---|
| D0 | không gửi gì; AI node chỉ tìm trong camera của chính nó (giả định của bản ICC và `paper/L1-MODEL-vi.md`) | 0 | không | đối sánh chỉ mục của mình |
| D1 | ảnh khung hình (khung có người, nén) | 30–50 KB mỗi khung (ước lượng) | phát hiện chuyển động | phát hiện người, trích đặc trưng, tìm |
| D2 | ảnh cắt người tốt nhất | 10–20 KB (ước lượng) | phát hiện người, chọn ảnh cắt | trích đặc trưng, tìm |
| D3 | vector đặc trưng + thời điểm, vị trí | 0,5–4 KB (512 chiều INT8 tới 2048 chiều fp16) | phát hiện + trích đặc trưng | chỉ tìm (tích vô hướng) |

Video liên tục (1–2 Mbit/s mỗi camera) vượt dung lượng 802.15.4 (250 kbit/s cả môi trường) nên không đưa vào.

**Ước lượng thô để xếp thứ tự** (sẽ thay bằng bước B1): một môi trường cell chuyển khoảng 15 KB/s (99 B mỗi khung,
khoảng 6,5 ms mỗi khung đo ở trace River), qua 1,5–1,7 khung mỗi gói trong cell nên vào CL của AI node khoảng 9–10 KB/s.
Nếu luồng nền chỉ được dùng 10–20 % thời gian (để chừa chỗ và tiết kiệm pin) thì mỗi AI node nhận khoảng 1–2 KB/s. Với
100 camera giao cho một AI node, mỗi camera 60 người/h: D3 (0,6 KB) cần 1 KB/s, vừa sát giới hạn; D2 (15 KB) cần 25 KB/s,
vượt cả dung lượng môi trường. Như vậy giới hạn thật là luồng nền G2G, còn bộ nhớ thẻ SD gần như không bao giờ chật (D2 ở
mức trên vẫn giữ được khoảng 59 ngày trên 128 GB). Lưu lượng người qua camera ρ quyết định gần hết, nên phải khảo sát
trước (B0).

## 3. Mô hình dùng chung

- Bản đồ: k8 của chiến dịch C4 (`scratchpad/C4/CP/<kênh>/R1/k8-s1`, 617 cell, 13 086 node, 8 cụm). Thêm k12 khi kết quả
  k8 ổn.
- Ứng viên AI node: node mạnh theo thuộc tính có sẵn trong bản đồ (`cpu`, `comm`, `score` của `uav-coop-deploy`); lấy
  các node có `cpu` trên ngưỡng (ví dụ 20 % node mạnh nhất), mỗi ứng viên có bộ nhớ M_v và bậc thiết bị.
- Giao node: node thường u giao cho AI node mở gần nhất theo chặng, không quá H chặng, tổng luồng vào mỗi AI node không vượt
  C_v (luồng nền cho phép, KB/s) và tổng dữ liệu trong cửa sổ W không vượt M_v.
- Thời gian pha 1: T1 = max_k [T_giao,k + T_đối sánh,k]. T_giao,k lấy từ surrogate T̂_River (model-level) hoặc ns-3
  (kiểm). T_đối sánh,k = `match_time(thiết bị, L, M_k)` của `uav-l2/tools/l1_mission.py` (ResNet-50: 257 ảnh/s trên Pi 5 +
  Hailo-8L, 12,6 ảnh/s trên Pi 5 CPU, có nguồn), với M_k = số người trong cửa sổ W của mọi camera giao cho k; D1, D2 cộng
  thêm thời gian phát hiện và trích đặc trưng cho từng ảnh.
- Thời gian pha 2: mô hình đội 2 hiện có (`uav-l2/tools/l1_rank.py`, `mission_policy.py`): báo cáo qua LoRa, UAV cánh quay
  15 m/s thăm theo xác suất, xác minh tại chỗ. Mục tiêu: T1 + T2 (lúc xác minh xong cell thật).
- Kênh: r200 và r100 (R50 khoảng 200 và 100 m, ứng với đô thị dày và cao tầng theo Al-Hourani, CONTEXT mục 9). Khi K1a xong
  thì thay bằng kênh có LoS theo góc ngẩng.

## 4. Các bước

| Bước | Việc | Công cụ | Chi phí | Đầu ra |
|---|---|---|---|---|
| B0 | Khảo sát tham số (K12): lưu lượng người qua camera đô thị ρ (người/h), cỡ khung và ảnh cắt, số chiều vector của mô hình re-ID nhẹ, thời gian phát hiện + trích đặc trưng trên node thường, dung lượng nhớ node camera rẻ. Tra repo trước (`edge_devices.md`, `06-deployment.md`, `L1-MODEL-vi.md`) | đọc, tìm | khoảng 50–80 nghìn token | bảng tham số kèm nguồn, dải thấp/giữa/cao |
| B1 | Máy tính luồng nền: với mỗi phương án, mỗi H và mỗi tập AI node, tính luồng vào từng môi trường cell và cặp gateway trên cây giao node (dùng mô hình tải 1,5–1,7 khung mỗi gói đã khớp ở `river_lb.py`), cửa sổ W theo bộ nhớ, và năng lượng phát của node thường mỗi giờ | `paper/j1/analysis/bg_load.py` (mới) | Python, vài phút | vùng khả thi (ρ, H, số AI node) cho D1–D3 |
| B2 | Nối ống: `river_plan.py` và `mission.py` nhận tập critical cell từ file (`--crit FILE`); kiểm hồi quy: đưa đúng tập của Algorithm 3 vào thì kế hoạch giống hệt từng byte | sửa `uav-coop2/tools/river_plan.py`, `uav-l2/tools/mission.py` | Python, nhanh | cờ `--crit`, log hồi quy |
| B3 | Bộ chọn critical cell: facility location có sức chứa (luồng nền C_v, bộ nhớ M_v, H chặng), mục tiêu T1 + T2 với T_giao từ surrogate; tìm kiếm cục bộ mở/đóng/đổi, khởi đầu từ Algorithm 3. Quét số critical cell từ ít tới nhiều để vẽ đường đánh đổi, cho từng phương án và từng bậc thiết bị | `uav-l2/tools/cc_select.py` (mới) | Python, dưới 1 giờ cho k8 | `assign.csv`, các tập critical cell, đường đánh đổi mức mô hình |
| B4 | Kiểm bằng ns-3 các điểm chọn trên đường đánh đổi: 4 cỡ tập (ít, tối ưu mô hình, Algorithm 3, nhiều) × 2 kênh × 2 seed, pha 1 đủ (pass + River, có `--tree` và kế hoạch cân tải nếu K11 xác nhận) | `mission.py` + binary hiện có | khoảng 16 cấu hình × 15–20 phút ≈ 4–5 giờ trên 4 nhân | T_giao đo được, so với surrogate |
| B5 | Tổng thời gian hai pha: ghép T_giao đo được với T_đối sánh của từng phương án và mô hình đội 2, rút thăm ghép cặp | `l1_rank.py` / `l1_mission.py` thêm phương án dữ liệu và tập critical cell ngoài (K13) | Python, vài phút | bảng và hình T1, T2, T1 + T2 theo phương án và cỡ tập |
| B6 | Độ nhạy: ρ (thấp/giữa/cao), bậc thiết bị (MCU, Pi 5 CPU, Pi 5 + Hailo), mật độ 400 và 280 node/km² (K10) ở mức mô hình; chỉ đưa lên ns-3 các điểm làm đổi kết luận | B1, B3, B5 | Python; ns-3 nếu cần thì bàn lại | hình độ nhạy |
| B7 | Viết: mục thí nghiệm trong `paper/j1/draft-v1/`, log và README theo mục 94, ảnh theo mục 131 | — | — | đoạn bài, bảng, hình |

Thứ tự: B0 và B2 làm song song ngay; B1 sau B0; B3 sau B1, B2; B4 cần duyệt chi phí; B5 sau B4; B6 cuối.

## 5. Tiêu chí đạt

- Hồi quy B2 giống hệt từng byte với Algorithm 3.
- Surrogate T_giao lệch ns-3 không quá khoảng MAE đã biết (22,8 s); lệch hơn thì B3 dùng thêm điểm ns-3 để hiệu chỉnh.
- Mỗi kết luận về phương án tốt nhất đứng vững trên cả hai kênh và hai seed; nếu đổi theo ρ thì báo theo dải ρ.
- Báo cả kết quả âm (ví dụ D2 không khả thi ở mọi ρ thực tế).

## 6. Rủi ro

- ρ đô thị biến thiên rất rộng theo vị trí (phố đông và ngõ vắng chênh nhau hàng chục lần); cần báo theo dải, không lấy
  một con số.
- Chưa có số đo re-ID người trên MCU (`06-deployment.md`); D3 giả định node thường đủ sức trích đặc trưng, nếu không thì
  D3 chỉ đúng cho camera bậc chip camera trở lên.
- Luồng nền chạy liên tục trước sự cố nên không cộng vào thời gian nhiệm vụ, nhưng nếu chiếm phần lớn dung lượng thì làm
  chậm River lúc có sự cố; B1 phải tính cả phần chồng này (luồng nền tạm dừng khi có truy vấn là một lựa chọn).
- Surrogate T̂_River khớp trên tập critical cell của Algorithm 3; tập rất khác (nhiều critical cell sát nhau) có thể nằm
  ngoài vùng khớp.

## 7. Cần người dùng quyết trước khi chạy

1. Giữ cả bốn phương án D0–D3, hay bỏ D1 sau khi B1 xác nhận không khả thi.
2. Tỉ lệ thời gian luồng nền được dùng (đề xuất 10–20 %).
3. Duyệt B4: khoảng 4–5 giờ ns-3 trên 4 nhân của container hiện tại (bản build ns-3 và dữ liệu C4 vẫn còn trong container
   này; container mới thì phải build lại).

## 8. Nhận xét kỹ thuật trước khi chạy (2026-11-18, chatlog mục 340–341)

Đây là các giả thuyết cần thử nghiệm để chốt, chưa phải kết luận (mục 341). Mỗi điểm kèm cách kiểm trong các bước B1–B5.

1. **Đối sánh lúc truy vấn có thể gần bằng 0 cả ở D1, D2.** AI node trích đặc trưng ngay khi ảnh tới (trước sự cố) và giữ
   chỉ mục vector; lúc truy vấn chỉ trích đặc trưng bộ ảnh tham chiếu, so cosine (vài ms với 10⁵ vector) và kiểm lại một
   nhóm ứng viên đầu bảng, không phụ thuộc M_k. Khi đó giá của ít critical cell nằm ở hai ràng buộc nền: AI node theo kịp
   tốc độ ảnh tới (ρ × số camera × thời gian trích ≤ năng lực tính) và luồng nền G2G. Kiểm: B3 mô hình hai chế độ, trích
   trước (mặc định) và trích lúc truy vấn (AI node ngủ để tiết kiệm pin), so đường đánh đổi của hai chế độ.
2. **Loại dữ liệu đổi cả pha 2.** Vector do node thường trích bằng mô hình nhẹ (D3) kém chính xác hơn vector AI node trích
   từ ảnh cắt (D2), nên nhiều ứng viên sai hơn và đội 2 thăm nhiều cell hơn. Kiểm: B5 thêm độ chính xác theo phương án
   làm đầu vào của `l1_rank.py` (số liệu ở `research_notes/l1-signature-matching/`, `reports/l1-signature-matching.md`).
3. **Surrogate T̂_River tính riêng từng critical cell, không thấy tranh chấp ở cell Bank và cell trung chuyển dùng
   chung.** Bớt critical cell thì tải chung giảm phi tuyến. Kiểm: B3 dùng thêm mô hình tải mức cell của
   `uav-coop2/tools/river_lb.py` (R² 0,89 với trace) làm thành phần thứ hai cho T_giao (tải lớn nhất × thời gian một khung);
   B4 so cả hai với ns-3.
4. **Tập critical cell đi vào cả tour, không chỉ kế hoạch River.** Algorithm 3 có bản sao `critical()` ở
   `uav-l2/tools/meander_lane.py`, gọi ở `mission.py` (uốn chord) và `meander_lane.py`; `lm_tour.py` cũng chấm điểm theo
   critical cell của thư mục CHORD. Kiểm: B2 nối `--crit` vào cả bước dựng tour, hồi quy giống từng byte cả file tour lẫn kế
   hoạch.
5. **D0 không cùng hệ với D1–D3.** Ở D0 camera của node thường không bao giờ được tìm. Kiểm: bảng kết quả thêm cột tỉ lệ camera
   được tìm; D0 là mốc, không xếp hạng chung.
6. **Hạ tầng.** Mục 7.3 đúng cho container của phiên viết kế hoạch; container khác phải build lại ns-3.46 (khoảng 30–45 phút,
   dùng chung cho K11). B4 nên chờ K11 vì K11 quyết định binary và kế hoạch River.

## 9. B8: phương án lai (2026-11-20, chatlog mục 373–375)

Người dùng chốt phương án lai làm phương án chính (CONTEXT mục 28–29): truy vấn vẫn là ảnh (Q = 4 041); ở bước luồng nền, node
có NPU gửi vector của mô hình nhẹ, node yếu gửi ảnh cắt nhỏ; AI node giữ mô hình của từng nhóm node nó phục vụ.

| Tham số | Giá trị quét | Ghi chú |
|---|---|---|
| Tỉ lệ camera có NPU, f_npu | 0,2, 0,5, 0,8 | node có NPU gửi vector, còn lại gửi ảnh cắt |
| Cỡ vector | 0,5 KB (512 chiều INT8 + 20 B) | 4,1 KB (2 048 chiều fp16) làm độ nhạy |
| Cỡ ảnh cắt | 5 KB | 15 KB làm độ nhạy |
| Số mô hình mỗi AI node, K | 1, 3, 5 | chỉ ảnh hưởng thời gian đối sánh (K × L lần trích đặc trưng) và bộ nhớ AI node |
| Luồng nền cho phép | 10 %, 20 % thời gian kênh | như B1 |
| ρ (người/h mỗi camera) | thấp, giữa, cao theo `K9-PARAMS-vi.md` | như B0 |

Các bước:
1. B1 lai: `bg_load.py` tính tải mỗi node theo loại dữ liệu của nó (vector hoặc ảnh cắt) thay vì một loại chung; đầu ra vùng khả
   thi (ρ, f_npu, số AI node).
2. B3 lai: `cc_select.py` dùng tải thực của từng node trong ràng buộc luồng nền; thời gian đối sánh thêm K × L lần trích đặc trưng
   (`match_time`).
3. B5 lai: tổng thời gian hai pha theo f_npu và K, so với D0, D2 (chỉ ảnh cắt), D3 (chỉ vector) đã có.
4. Ghi kết quả vào báo cáo K9 và đoạn VIII-F của bản thảo; ns-3 chỉ chạy lại nếu tập critical cell tối ưu đổi nhiều so với B4
   (bàn chi phí trước, mục 35).
