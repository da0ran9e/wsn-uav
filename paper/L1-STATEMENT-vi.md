# Lớp 1: phát biểu chi tiết, khớp với các công bố

Lời gốc: CLAUDE.md §8 mục 88 (phát biểu) và mục 89 (yêu cầu viết lại).
Nguồn và nhãn: `reports/Đối sánh signature trên thiết bị biên.md` (gọi tắt là [R2]) và `reports/Nhận dạng tại node biên lớp 1.md` ([R1]). Nhãn [nguồn], [nguồn·trích], [NSX], [mô hình] giữ nguyên nghĩa như trong hai báo cáo.

## 1. Phát biểu (bản viết lại)

**Đối tượng và quan sát.**
- Mục tiêu thuộc một trong ba lớp c ∈ {người, xe, động vật}.
- Mỗi camera tham gia (gọi là nút xử lý) đã ghi lại một hoặc vài *tracklet* của các đối tượng trong khung hình. Tracklet là chuỗi crop của cùng một đối tượng trên các khung liên tiếp.
- Ta giả định mục tiêu, nếu đã đi qua, được ghi tương đối rõ. Với người, cỡ người trong khung khoảng ≥ 128 px chiều cao. Với mặt, cần khoảng 250 px/m theo IEC 62676‑4 [R1].
- Nút chạy một bộ phát hiện đối tượng và một mô hình embedding thuộc *họ mô hình* m, ví dụ ArcFace cho mặt, OSNet/ResNet‑IBN cho thân người hay xe, MegaDescriptor cho động vật.
- Kho của nút đã được lập chỉ mục sẵn thành embedding theo tracklet. Đối sánh vì vậy là tìm kiếm vector, không phải quét lại video thô [R1].

**Signature (tầng nhẹ).**
- BS trích từ bộ tham chiếu đầy đủ R (nhiều ảnh rõ hoặc video của mục tiêu) ra K = 3–5 file signature, tổng khoảng 4–5 KB.
- Mỗi file khoảng 1 KB, chứa embedding đã gộp (512 chiều, fp16) của **một view hoặc một điều kiện** khác nhau: chính diện, nghiêng, sau lưng, ban đêm, bộ quần áo khác.
- Mỗi file tự giải mã được. Header mang **mã họ mô hình** và **chỉ số view**.
- BS soạn signature riêng cho từng họ mô hình đang có trong vùng: embedding của hai họ khác nhau không so được với nhau, trừ khi được huấn luyện tương thích kiểu BCT [R2·nguồn].
- Lợi ích theo số view bão hòa ở khoảng 3–4 view đa dạng [R1, R2·nguồn]. Vì vậy K = 3–5 là hợp lý.

**Đối sánh và điểm.**
- Với mỗi tracklet t, nút tính độ tương đồng cosine s_tj với từng file j nó đang giữ.
- Các s_tj được gộp thành **một điểm trung bình theo các file đang giữ**, S_t = mean_j s_tj. Có thể đặt trọng số theo chất lượng ảnh. Theo bảng NAN/AvePool, gộp trung bình cho kết quả tốt hơn lấy max ở FMR thấp [R1·nguồn].
- Điểm của nút là S = max_t S_t, tức tracklet giống mục tiêu nhất.
- "Độ trùng khớp phần trăm" **không phải cosine thô**. Với ArcFace, ngưỡng vận hành chỉ khoảng 0,30–0,45 cosine. Đặt ngưỡng cosine 0,7–0,9 sẽ loại phần lớn cặp thật [R2·nguồn].
- Phần trăm là một thang đã hiệu chỉnh p = g_{m,c}(S), riêng cho từng họ mô hình và từng lớp mục tiêu, khớp bằng hiệu chỉnh beta hoặc logistic trên cặp có nhãn [R2·nguồn FairCal].
- Thang này được neo theo tỉ lệ khớp nhầm (FMR) mỗi phép so sánh: **70 / 80 / 90 % ↔ FMR 10⁻³ / 10⁻⁴ / 10⁻⁵** [R2·mô hình, neo vào AWS 80 %/99 % và Azure 0,5 (NSX)].

**Quyết định tại nút.**
- Nút trả **YES** nếu p ≥ τ + δ, **NO** nếu p ≤ τ − δ, và **UNSURE** khi p nằm giữa. τ ∈ {70, 80, 90 %}, δ tương đương khoảng 0,03 cosine [R2·mô hình].
- Một nút so N tracklet với k file. Xác suất trả YES nhầm ít nhất một lần là 1 − (1 − f)^(N·k), với f là FMR mỗi phép so sánh [R2·mô hình].
  - Ví dụ: N·k = 5 000 cho khoảng 99 % YES nhầm ở mức "70 %" và khoảng 5 % ở mức "90 %".
  - Vì vậy YES/NO tại nút chỉ là **cổng quyết định có gửi báo cáo hay không**. Nút gửi về CH/BS một báo cáo khoảng 6 B: LLR đã hiệu chỉnh, log₂(N·k), **bitmap các file đang giữ**, hạng chất lượng camera.
  - **BS ra quyết định cuối** bằng kiểm soát tỉ lệ phát hiện sai (Benjamini–Hochberg) trên toàn vùng [R1].

**Khác biệt giữa thiết bị.** Cùng một bộ signature cho điểm khác nhau trên các nút. Mô hình điểm cặp thật của nút i:

  S_i = μ_c + Δ_cam(i) + b_dev(i) + ε

- **Δ_cam** (quang học, ISP, độ phân giải, nén, góc đặt) là thành phần lớn nhất. Nó kéo điểm cặp thật xuống khoảng 0,1–0,4 cosine với camera kém [R2·mô hình, chưa kiểm chứng]. Re‑ID khi đổi miền mất 45–55 điểm Rank‑1 [R2·nguồn·trích].
- **b_dev** do lượng tử hóa int8 trên NPU, khoảng ±0,03 cosine, cố định theo loại thiết bị [R2·nguồn·trích: +0,025 trên Hailo]. Trên thang đã hiệu chỉnh, mức này cỡ 2–5 điểm phần trăm, tức đúng cỡ chênh "70 % so với 75 %".
- **ε** là nhiễu từng cặp, nhỏ: fp16 khoảng 0,001–0,005; cùng mô hình fp32 trên phần cứng khác nhau ≪ 0,001 [R2·mô hình].
- Hệ quả:
  - Ngưỡng τ phải được hiệu chỉnh riêng cho từng bản biên dịch của mô hình.
  - Camera kém chủ yếu gây **bỏ sót** (NO nhầm), ít gây báo nhầm.
  - Thiết bị biên dịch hỏng phải được loại khỏi tập nút xử lý qua kiểm thử nghiệm thu, ví dụ `accuracy_analysis` của RKNN [R2·NSX].

**Nhận thiếu file.**
- Nút giữ tập con H ⊆ {1..K}. Recall ở FMR cố định giảm theo **file nào thiếu**, không chỉ theo số file thiếu [R2·mô hình neo vào Sun & Zheng CVPR 2019, Ben Mabrouk 2026]:
  - thiếu một view trùng lặp: khoảng −1 điểm;
  - thiếu view duy nhất khớp góc nhìn của camera: khoảng −2…−6 điểm trong miền huấn luyện, −15…−25 điểm ngoài miền.
- Khi gộp bằng trung bình, ngưỡng phải hiệu chỉnh theo từng tập H. Bitmap trong báo cáo cho BS biết H.

**Hai tầng: khoanh vùng rồi xác nhận.**
- **Tầng 1 (signature nhẹ, pha 1)** dùng để *xếp hạng và khoanh vùng*, không dùng để loại cứng.
  - Thuộc tính thô như màu áo chỉ đúng khoảng 74 % [R2·nguồn Lin et al.].
  - Màu xe đúng khoảng 80–95 % ban ngày [R2·nguồn]. Ban đêm hoặc dưới hồng ngoại, thông tin màu gần như mất hẳn.
  - Lọc cứng làm recall cả hai tầng chỉ còn khoảng 0,7 [R2·mô hình].
- **Tầng 2 (bộ dữ liệu đầy đủ, đội 2 mang tới pha 2)** dùng để xác nhận.
  - Độ chính xác "gần như tuyệt đối" **chỉ đạt khi có ảnh mặt chất lượng tốt** (FNMR 0,06–0,2 % ở FMR thấp, theo NIST FRTE 1:1 [R2·nguồn·trích]) **hoặc biển số đọc được**.
  - Các trường hợp khác:
    - người theo dáng toàn thân: khoảng 0,95 nếu cùng quần áo, 0,56–0,74 nếu đổi quần áo;
    - mặt ngoài thực địa: khoảng 0,81 TAR ở FAR 10⁻⁶;
    - xe không có biển: 0,85–0,95;
    - cá thể động vật: 0,35–0,99 tùy loài [R2·nguồn/nguồn·trích; xác suất là mô hình].
  - Sinh đôi và người trông giống nhau không phân giải được bằng ảnh [R2·nguồn NIST IR 8439].

## 2. Đối chiếu với phát biểu gốc (mục 88)

| Phát biểu gốc | Bản viết lại | Lý do (nguồn) |
|---|---|---|
| Camera có video "tương đối rõ" của đối tượng | Tracklet có cỡ đối tượng ≥ ngưỡng điểm ảnh, kho đã lập chỉ mục embedding sẵn | Pixel‑on‑target theo IEC 62676‑4; thời gian quét video thô tính bằng giờ [R1] |
| 3–5 file signature, 4–5 KB | Giữ nguyên. Mỗi file ≈ 1 embedding 512‑d fp16 của một view/điều kiện; header có mã họ mô hình và chỉ số view | Bão hòa ở 3–4 view [R1, R2]; khác họ mô hình thì không so được (BCT) [R2] |
| Chấm điểm trùng khớp, trên 70–90 % thì YES | Điểm cosine được gộp trung bình qua các file, ánh xạ sang thang đã hiệu chỉnh neo theo FMR; trả YES/NO/UNSURE; YES chỉ là cổng gửi báo cáo, BS quyết định | Cosine 0,7–0,9 loại phần lớn cặp thật; nhiều phép so sánh mỗi camera [R2] |
| Thiết bị A 70 %, thiết bị B 75 % thì hai câu trả lời khác nhau | Đúng. Chip lệch 2–5 điểm %, camera lệch lớn hơn một bậc; hiệu chỉnh theo bản biên dịch và vùng UNSURE ±δ hấp thụ phần chênh do chip | [R2] mục (B) |
| Nhận 4/5 file thì tỉ lệ giảm | Giảm theo file nào mất: −1 điểm (view trùng lặp) tới −25 điểm (mất view khớp camera, ngoài miền) | [R2] mục (C) |
| Có bộ dữ liệu đầy đủ thì gần như tuyệt đối | Chỉ đúng với mặt chất lượng tốt và biển số đọc được; các trường hợp khác đặt xác suất theo lớp | [R2] mục (D) |
| Signature nhẹ để khoanh vùng (ví dụ áo vàng) | Giữ ý, nhưng dùng để xếp hạng hoặc giữ top‑k, không loại cứng; tắt bộ lọc màu ban đêm/IR | Màu áo đúng ≈ 74 %; recall nhân qua hai tầng [R2] |

## 3. Dạng ngắn cho mục System Model của paper (tiếng Anh)

> Each processing node holds tracklet embeddings of the objects it has recorded, computed by a model of family m. The UAV delivers K = 3–5 self‑contained signature files (≈1 KB each; one aggregated embedding per view or condition), tagged with the model family and view index. A node averages cosine similarities over the files it holds, takes the best tracklet, and maps the score to a calibrated scale anchored to a per‑comparison false‑match rate (70/80/90 % ↔ 10⁻³/10⁻⁴/10⁻⁵). It answers YES/NO/UNSURE with a margin δ. Because a node compares N·k pairs, YES only gates a 6‑byte report (calibrated LLR, comparison count, bitmap of held files, camera quality class), and the BS decides under false‑discovery control. Scores differ across nodes mainly through camera quality (Δ_cam) and slightly through quantisation (b_dev ≈ ±0.03). Missing a file costs recall according to which view it carried. The light signature ranks candidates; the full reference set, brought in phase 2, is near‑certain only for good face images or readable plates.

## 4. Tham số

Giá trị khởi đầu cho giả lập nằm trong bảng "Tham số đề xuất cho mô hình hệ thống" của [R2]. Các tham số cần thay bằng số đo đầu tiên:
1. Phân bố điểm cặp thật và cặp khác người trên tracklet thật (quyết định τ và δ).
2. Δ_cam theo hạng camera.
3. Đường TAR@FAR theo 1–5 view.
