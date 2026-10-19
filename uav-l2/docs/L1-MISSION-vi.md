# Nhiệm vụ P với mô hình đối sánh lớp 1 (tham số M, L, F, f, k)

Lời gốc: CLAUDE.md §8 mục 92–94. Phát biểu lớp 1: `paper/L1-STATEMENT-vi.md` §6–7. Mã: `tools/l1_mission.py`; dựng lại hình học từ dữ liệu đã lưu: `tools/regeom.py`. Log: `logs/2026-10-19_1500-l1-propose/`.

## 1. Thay đổi so với P cũ

P = tour l3first, đội 2 đi sớm, thăm theo điểm. Lớp 3 giữ nguyên: thời điểm critical cell có đủ D lấy từ kết quả ns‑3 River đã có (40 bản đồ, 1 304 critical cell). **Không chạy ns‑3 mới.**

| | P cũ | P với lớp 1 |
|---|---|---|
| Nghi vấn | 1 thật + 2–3 giả, rút ngẫu nhiên | mọi critical cell trả YES |
| Cell thật | luôn phát hiện | phát hiện nếu crop tốt nhất ≥ ngưỡng; có thể bỏ sót ⇒ nhiệm vụ thất bại |
| Điểm báo về | thật U(0,5; 1), giả U(0,2; 0,8) | xác suất hậu nghiệm từ điểm crop tốt nhất (BS tính) |

## 2. Mô hình lớp 1

- **Điểm số:** ROC hai phân phối chuẩn khớp vào [7] Bảng 4 (Market‑1501, Individual Verification, ResNet‑50 multi‑shot). Người lạ ~ N(0, 1), mục tiêu ~ N(4,43; 1,30). Khớp lại: 84,9 / 94,7 / 98,4 / 99,2 / 99,7 % ở f = 0,1 / 1 / 5 / 10 / 20 %, so với bài 82,3 / 95,9 / 98,5 / 99,4 / 99,6 %.
- **View:** crop mục tiêu có view trước / sau / nghiêng, đều nhau. L ảnh signature theo thứ tự trước, sau, nghiêng, trước, … Crop có view không nằm trong các ảnh cell giữ được thì điểm ~ N(3,04; 1,30), tức mất 25 điểm TTR ở f = 1 % [mô hình, theo đầu "thiếu view duy nhất khớp" trong báo cáo lớp 1]. Ảnh thứ hai của cùng view không cộng thêm: [7] Bảng 4 cho 1 → 2 ảnh gallery chỉ +0,8 đến +2,3 điểm.
- **Số ảnh cell giữ được:** min(L, ⌊D / khung mỗi file⌋), khung mỗi file = ⌈F·1000 / 99⌉.
- **Node:** ngưỡng t ứng với f; YES nếu crop tốt nhất ≥ t; báo điểm đó.
- **Cell thật:** có k crop mục tiêu trong M crop.
- **BS:** hậu nghiệm = tiên nghiệm 1 / (số critical cell) × tỉ số hợp lý "1 mục tiêu trong M" so với "M người lạ". Đội 2 thăm theo hậu nghiệm / thời gian như P.
- **Ghép cặp:** cell thật, pha LoRa, phân vị người lạ của từng cell và k crop mục tiêu giống nhau giữa mọi cấu hình.

**Lưới:** f ∈ {0,1; 1; 5; 10} %, M ∈ {100; 1 000; 10 000}, k ∈ {1; 3}, L ∈ {1; 2; 3; 4; 8}, F ∈ {15; 50} KB. 30 lượt rút × 40 bản đồ = **1 200 nhiệm vụ mỗi cấu hình**, 240 cấu hình. Dữ liệu: `data/mission/l1m-summary.csv`, `l1m-draws.csv.gz`.

## 3. Kết quả (L = 3, F = 15 KB; trung bình 32,6 critical cell mỗi bản đồ)

| f | M | k | Thành công | YES nhầm / bản đồ | Lượt thăm | Kết thúc TB, s | p90, s |
|---|---|---|---|---|---|---|---|
| 0,1 % | 100 | 1 | 87,0 % | 3,0 | 1,83 | 765 | 1 124 |
| 0,1 % | 1 000 | 1 | 94,8 % | 19,9 | 4,47 | 946 | 1 622 |
| 0,1 % | 10 000 | 1 | 100 % | 31,6 | 8,51 | 1 261 | 2 722 |
| 1 % | 100 | 1 | 98,3 % | 20,0 | 3,41 | 856 | 1 294 |
| 1 % | 1 000 | 1 | 100 % | 31,6 | 5,75 | 1 054 | 2 037 |
| 0,1 % | 100 | 3 | 99,7 % | 3,0 | 1,77 | 758 | 1 110 |
| 0,1 % | 1 000 | 3 | 99,8 % | 19,9 | 2,54 | 760 | 1 097 |
| 1 % | 1 000 | 3 | 100 % | 31,6 | 2,64 | 763 | 1 108 |
| 1 % | 10 000 | 3 | 100 % | 31,6 | 3,36 | 817 | 1 164 |
| *P cũ (giả lập chỗ giữ)* | | | *100 %* | *2–3* | *1,98* | *782* | *1 123* |

**L và F** (f = 1 %, M = 1 000, k = 3): L = 1 → 4,48 lượt thăm, 899 s; L = 2 → 3,26 lượt, 810 s; L ≥ 3 → 2,64 lượt, 763 s. F = 15 hay 50 KB cho kết quả **giống hệt**, vì ở cả hai cỡ, D của mọi cluster đều chứa đủ ≥ 6 ảnh.

## 4. Đọc kết quả

1. **Mức f = 0,1 % (TTR 82 %) dùng được, nhưng nhờ k chứ không nhờ M.** Với k = 3 crop mục tiêu, tỉ lệ crop mục tiêu vượt ngưỡng ở mức camera là 99,7 % (L ≥ 3). Với k = 1 chỉ 85–87 %.
2. **M lớn làm "thành công" tăng nhưng vì lý do sai.** Ở M = 10 000, gần như mọi critical cell trả YES vì người lạ, kể cả cell thật. Đội 2 vẫn tới cell thật, nhưng phải thăm 8,5 cell (k = 1) thay vì 1,8 và nhiệm vụ dài thêm khoảng 500 s. M không giảm bỏ sót; M làm loãng thứ hạng.
3. **Khi BS xếp hạng theo điểm, ngưỡng tại node gần như không còn là nút vặn chính.** Từ f = 1 % trở lên, mọi cell đều YES, kết quả chỉ còn phụ thuộc vào việc điểm của cell thật có đứng đầu không, tức là k, M và view.
4. **L có giá trị tới 3 (đủ view), sau đó chỉ tốn dữ liệu.** Trong mô hình này, ảnh thứ hai của cùng một view không giúp, khớp với [7] Bảng 4.
5. **So với P cũ:** cấu hình hợp lý (f = 0,1–1 %, M = 100–1 000, k = 3, L = 3) cho kết thúc 745–763 s, gần P cũ (782 s). Chỗ giữ 2–3 nghi vấn giả của P cũ hóa ra không lạc quan hơn mô hình, vì xếp hạng theo điểm đưa cell thật lên đầu.

## 5. Giới hạn

- **L và F chưa chạm tới thời gian lớp 3.** River trong ns‑3 vẫn giao **toàn bộ D** cho critical cell. Nếu truy vấn nhỏ (L·F < D) và UAV phát lặp, nhiều cell đã đủ ngay sau gom nội cell, nên sẵn sàng sớm hơn; số ở đây là cận trên của thời gian. Muốn đo cần bitmap lượt bay, mà bitmap không còn trên máy này (xem §6).
- **Số điểm lạc quan:** mục tiêu nằm trong tập huấn luyện của [7], cùng miền camera (`paper/L1-STATEMENT-vi.md` §6.2).
- **Crop độc lập:** k crop mục tiêu và M crop người lạ rút độc lập. Crop trong cùng một tracklet tương quan mạnh, nên nên hiểu M, k là số tracklet.
- **Mức phạt view (−25 điểm) là giả định**, chưa có nguồn đo trực tiếp.
- Mỗi cấu hình 1 200 nhiệm vụ trên 40 bản đồ: đạt N ≥ 120, nhưng các bản đồ là mẫu ns‑3 độc lập duy nhất.

## 6. Bước tiếp theo đề xuất (chờ duyệt)

**Chạy lại lượt bay ns‑3 để có bitmap** (40 bản đồ, khoảng 200 cluster). Sau đó:
- tính cho từng critical cell thời điểm có đủ L ảnh: ngay sau gom nội cell nếu đủ, nếu không thì dùng thời gian River;
- quét L × F với truy vấn phát lặp.

Thời gian máy chưa biết; mình đề xuất đo trước trên 1 cluster rồi ước lượng cho cả chiến dịch.

## 7. Thời gian đối sánh theo thiết bị critical cell (CLAUDE.md §8 mục 95)

Giả định: critical cell là thiết bị cỡ Raspberry Pi 5 chạy ResNet‑50 (25,6 triệu tham số, khoảng 4,1 GMAC mỗi ảnh 224×224). Crop được embed ngay lúc ghi hình, nên khi UAV tới, node chỉ phải:
1. giải mã L ảnh signature;
2. embed L ảnh đó;
3. tìm trong chỉ mục M vector.

### 7.1 Số đo dùng làm tham số

| Thiết bị | ResNet‑50 | Nguồn |
|---|---|---|
| Pi 5 + Hailo‑8L (13 TOPS, PCIe Gen 3 ×1) | **257,6 ảnh/s** (224×224, batch 8) | Hailo Community, "Raspberry Pi 5 with Hailo‑8L Benchmark", 06/2024 |
| Pi 5 CPU (Cortex‑A76), INT8, ONNX Runtime 1.28 | **79,1 ms/ảnh ⇒ 12,6 ảnh/s** (batch 1) | arXiv:2609.16085, Bảng 2 |
| Pi 5 CPU, FP32 | 145,0 ms/ảnh ⇒ 6,9 ảnh/s | như trên |

- "Vài trăm ảnh/s" **chỉ đúng khi Pi 5 có NPU** (Hailo‑8L). CPU của Pi 5 chỉ được khoảng 13 ảnh/s.
- Ảnh re‑ID 256×128 chỉ có 65 % số điểm ảnh của 224×224, nên tốc độ thực có thể cao hơn. Giả lập giữ số đo ở 224×224 cho thận trọng.

### 7.2 Công thức trong giả lập (`l1_mission.py`, `match_time`)

T_match = L · T_decode + L / R + max(M · DIM · 2 B / BW, M · L · DIM / 20 GMAC/s)

- R: tốc độ embed của thiết bị (bảng trên).
- T_decode = 5 ms mỗi JPEG 15–50 KB [ước tính].
- DIM = 2 048: vector pooled của ResNet‑50, lưu fp16.
- BW = 8 GB/s băng thông bộ nhớ hiệu dụng [ước tính].

| T_match, s | M = 100 | 1 000 | 10 000 | 100 000 |
|---|---|---|---|---|
| Hailo‑8L, L = 1 | 0,009 | 0,009 | 0,014 | 0,060 |
| Hailo‑8L, L = 3 | 0,027 | 0,027 | 0,032 | 0,078 |
| Hailo‑8L, L = 8 | 0,071 | 0,072 | 0,079 | 0,153 |
| CPU, L = 3 | 0,252 | 0,253 | 0,257 | 0,303 |
| CPU, L = 8 | 0,673 | 0,674 | 0,681 | 0,755 |

**Nếu chưa có chỉ mục** (phải embed lại M crop khi UAV tới), cộng thêm M / R:

| M | 1 000 | 10 000 | 100 000 |
|---|---|---|---|
| Hailo‑8L | 3,9 s | 39 s | 6,5 phút |
| CPU | 79 s | 13 phút | 2,2 giờ |

Bộ nhớ chỉ mục: 4 KB mỗi crop (fp16), tức 40 MB cho M = 10 000.

### 7.3 Ảnh hưởng tới nhiệm vụ

Chạy lại toàn bộ lưới với Hailo‑8L (`data/mission/l1m-hailo8l-*`; log `logs/2026-10-19_1639-l1-device/`). Kết thúc nhiệm vụ đổi trung bình **−3,8 s** (từ −8,8 đến +2,9 s) so với MATCH = 5 s; tỉ lệ thành công không đổi. Thời gian đối sánh không phải nút cổ chai, miễn là chỉ mục có sẵn. Khe LoRa (40 s) và River lớn hơn nhiều.

Ví dụ (L = 3, F = 15 KB): f = 0,1 %, M = 100, k = 3: kết thúc 758 → 753 s; f = 1 %, M = 1 000, k = 3: 763 → 759 s.
