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

## 5. Bản nhận định của người dùng (CLAUDE.md §8 mục 90) và góp ý

Bản của người dùng thay đổi một điểm thiết kế so với §1: **signature là 3–5 ảnh crop đã nén (JPEG/WebP, 1–2 KB mỗi ảnh, mỗi ảnh một view)**, không phải embedding. BS chọn khung tốt nhất cho từng view theo điểm chất lượng ảnh rồi mới crop. Node tự tính embedding của các ảnh này bằng mô hình của chính nó.

**Điểm mạnh nên giữ:**
- **Không phụ thuộc mô hình.** Mỗi node tự tính embedding nên vấn đề "khác họ mô hình thì không so được" (§1, [R2] mục B) biến mất. Đây là lý do tốt nhất để chọn ảnh thay cho embedding, nên nói thẳng trong paper.
- **Cỡ 1 KB cho mặt có nguồn trực tiếp.** [1] cho thấy crop mặt 112 px nén WebP/AVIF/HEIF/JPEG XL ở 1 024 B giữ lỗi gần mức ảnh gốc. JPEG thường ổn ở 112 px/1 KB nhưng hỏng ở 512 B hoặc 224 px. JPEG 2000 kém nhất và khuếch đại chênh lệch giữa các nhóm nhân khẩu học.
- **Chọn khung theo chất lượng** khớp với tài liệu về chất lượng ảnh mặt ([R2]: MagFace, SER‑FIQ).

**Chỗ nên chỉnh hoặc nói rõ:**

1. **Rank‑1 là chỉ số tập đóng.** "Trong 10 lần thử, cái đứng đầu danh sách đúng là mục tiêu" giả định mục tiêu chắc chắn có trong kho của camera. Câu hỏi thật của node là tập mở: mục tiêu có trong kho hay không. Rank‑1 không cho biết tỉ lệ trả YES nhầm khi mục tiêu vắng mặt, mà đây mới là thứ quyết định số nghi vấn giả và số lần đội 2 phải bay ([R1], [R2] mục A). Nên thêm một câu: tỉ lệ báo nhầm được kiểm soát riêng bằng ngưỡng hiệu chỉnh theo FMR; bảng chỉ mô tả khả năng tìm thấy khi mục tiêu có mặt.
2. **Rank‑1 phụ thuộc cỡ kho.** Market‑1501 có khoảng 750 danh tính trong tập thử. Camera ghi hàng nghìn tracklet sẽ cho rank‑1 thấp hơn số benchmark. Nên ghi cỡ kho của nguồn bên cạnh mỗi số.
3. **Bước "tra dữ liệu train để cho ra số điểm" là bước hiệu chỉnh.** Nên viết rõ:
   - Hàm ánh xạ cosine → điểm, riêng cho từng họ mô hình và từng lớp đối tượng, neo theo FMR.
   - Cách gộp K ảnh: lấy trung bình điểm.
   - Cách gộp các tracklet: lấy tracklet giống nhất.
   - Ngưỡng 70–90 % đặt trên thang đã hiệu chỉnh đó.
4. **Tiền xử lý ở node cũng là một nguồn chênh giữa thiết bị.** Ví dụ căn chỉnh mặt theo điểm mốc, hay cách resize. Nên quy định ảnh mặt gửi đi đã căn chỉnh sẵn ở 112×112, như giao thức của [1].
5. **Ảnh thân người, xe, động vật ở 1–2 KB chưa có nguồn đo trực tiếp.** Bản của người dùng đã nói đúng điều này. Crop thân người chuẩn là 256×128, lớn gấp khoảng 2,6 lần diện tích crop mặt 112×112. Ở cùng 1–2 KB, crop thân người bị nén mạnh hơn nhiều. Đây là khoảng trống thật, nên nêu như một giới hạn hoặc một thí nghiệm của paper.
6. **IEC 62676‑4.** Mức 250 px/m (40 px ngang mặt) là mức *Identification* của bản 2014. Bản 2025 đã đổi tên các mức (Outline, Discern, Perceive, Characterize, Validate, Scrutinize), và tôi chưa xác minh được giá trị px/m mới. Nên trích "IEC 62676‑4:2014" hoặc kiểm lại bản 2025. Con số "người cao ≥ 128 px" là quy ước đầu vào của mô hình re‑ID, không phải tiêu chuẩn, nên ghi là giả định.
7. **Hàng động vật:** cận dưới "2/10" thấp hơn số thấp nhất đã thấy (HappyWhale 34,3 % trong MegaDescriptor [R2]), tức khoảng 3/10. Nếu không có nguồn khác thì nên sửa thành "khoảng 3/10 tới gần 10/10".
8. **Hàng mặt ngoài thực địa "khoảng 6/10":** khớp TinyFace (rank‑1 68–76 %), nhưng QMUL‑SurvFace chỉ 29,9 % [R2]. Nên ghi khoảng "3–7/10" hoặc nói rõ đang dựa trên kiểu dữ liệu nào.
9. **Cột "điều kiện thuận lợi"** cần định nghĩa cả hai phía: ảnh gửi đi rõ, *và* camera ghi được mục tiêu đủ rõ (đúng ngưỡng điểm ảnh ở mục 1).

**Kiểm tra trích dẫn:** cả 6 tài liệu đều tồn tại. Thông tin để bổ sung cho danh mục tài liệu:

| # | Thông tin đầy đủ | Ghi chú |
|---|---|---|
| [1] | P. Hurtik, J. Sochor (Innovatrics), "Toward Sub‑1 kB Identity‑Preserving Face Compression: A Benchmark of Codecs, a Custom Learned Codec, and Studies of Resolution, Demographic Fairness, Recompression, and Adversarial Robustness", arXiv:2608.22866, 2026 | Dữ liệu: Color FERET (ảnh studio) và một tập ngoài thực địa; matcher ArcFace, LVFace, TopoFR, EdgeFace. EER 0,09 % nên ghi rõ là trên Color FERET |
| [2] | Y. Zhang, Z. Zheng, B. He, L. Sun, "Learning Posterior and Prior for Uncertainty Modeling in Person Re‑Identification", arXiv:2007.08785, 2020 | Thử trên Market‑1501, DukeMTMC, MARS |
| [3] | H. Li, G. Wu, W.‑S. Zheng, "Combined Depth Space Based Architecture Search for Person Re‑Identification", CVPR 2021, tr. 6729–6738 | CDNet khoảng 1,8 M tham số |
| [4] | G. Zhang, Y. Ge, Z. Dong, H. Wang, Y. Zheng, S. Chen, "Deep High‑Resolution Representation Learning for Cross‑Resolution Person Re‑Identification", arXiv:2105.11722, 2021 | Tập MLR‑Market‑1501, MLR‑CUHK03, MLR‑VIPeR, MLR‑DukeMTMC‑reID, CAVIAR |
| [5] | T. Mamedov, D. Kuplyakov, A. Konushin, "Approaches to Improve the Quality of Person Re‑Identification for Practical Use", Sensors 23(17):7382, 2023 | |
| [6] | L. S. Luevano, Ü. Öztürk, H. Otroshi Shahreza, A. George, S. Marcel, "Improving Low‑Resolution Face Recognition under Limited Data: How Synthetic Data Generation Can Close the Domain Gap", IJCB 2026, arXiv:2608.06580 | |

Các con số cụ thể bên trong từng bài (78–83 %, 54–60 %, bảng 4 của [5], phụ lục B của [2]) **chưa được đối chiếu** trong phiên này. Nên mở bản gốc kiểm lại trước khi nộp.

## 6. Bản cập nhật bài toán (CLAUDE.md §8 mục 92) và kiểm tra

Bản này thay §5. Node trả lời "người này đã xuất hiện trước camera chưa", ưu tiên không bỏ sót; BS lọc báo nhầm.

### 6.1 Đối chiếu điểm vận hành với [7] (đã mở bản gốc, ar5iv)

| Ý trong bản cập nhật | Bài gốc nói gì | Kết luận |
|---|---|---|
| Market‑1501, 758 người lạ, 14 573 ảnh thử | Tập thử non‑target: 758 ID, 14 573 ảnh; non‑target huấn luyện 728 ID; danh sách theo dõi 15 người (§4.2) | **Đúng** |
| ResNet‑50, YES đúng 99,38 % ở YES nhầm 10 % | Bảng 1, **Individual Verification**, Market‑1501, hàng ResNet‑50 [12], cột FTR 10 %: 99,38 | **Đúng**, và đúng giao thức: một mục tiêu, so với tập ảnh của chính mục tiêu đó |
| YES nhầm tính trên từng ảnh người lạ | FTR = #FNTQ / #NTQ, đếm trên ảnh truy vấn non‑target | **Đúng** |
| Cách quyết định | Khoảng cách tới tập = khoảng cách nhỏ nhất tới một ảnh mục tiêu trong gallery, so với ngưỡng r | Khớp bước 3 (lấy max cosine trên L ảnh) |
| "quay ngoài phố" | Market‑1501: 6 camera trước một siêu thị trong khuôn viên Đại học Thanh Hoa | Nên viết "khuôn viên, ngoài trời" |

Các điểm cùng hàng để chọn ngưỡng (Individual Verification, ResNet‑50): FTR 0,1 % → 82,26 %; 1 % → 95,86 %; 5 % → 98,54 %; 10 % → 99,38 %. Mô hình đề xuất của bài (APN): 99,58 % ở 10 %.

### 6.2 Ba điểm làm số 99,38 % lạc quan hơn kịch bản của ta

1. **Mục tiêu có mặt trong tập huấn luyện.** Bài chia đôi ảnh của mỗi người mục tiêu: một nửa để huấn luyện, một nửa để thử (§4.2). Ở kịch bản của ta, mô hình trên node chưa từng thấy mục tiêu. Đây là sai khác lớn nhất; cần nói rõ trong paper, hoặc tìm số ở giao thức mục tiêu không có trong huấn luyện.
2. **Cùng miền camera, cùng tập.** Gallery và truy vấn cùng 6 camera Market‑1501. Ảnh signature của BS (ảnh rõ, có thể từ nguồn khác) so với crop camera giám sát là bài toán đổi miền; [5] cho thấy mức giảm khi đổi miền.
3. **Footnote của bài:** tác giả sửa lỗi mã và chạy lại tinh chỉnh bằng PyTorch cho mọi phương pháp. Cần trích đúng phiên bản arXiv (số trong bảng phụ thuộc phiên bản).

### 6.3 Hệ quả cho hệ thống

**a) 10 % YES nhầm trên mỗi ảnh nghĩa là gần như mọi camera đều trả YES.** Xác suất một camera có ít nhất một crop người lạ vượt ngưỡng là 1 − (1 − f)^M:

| M (crop) | f = 10 % | f = 1 % | f = 0,1 % |
|---|---|---|---|
| 20 | 0,88 | 0,18 | 0,02 |
| 100 | ≈ 1 | 0,63 | 0,10 |
| 500 | ≈ 1 | ≈ 1 | 0,39 |

Vì vậy, báo cáo không thể chỉ là YES/NO; nếu không, BS không phân biệt được camera nào. Đề xuất: node gửi điểm cao nhất và số crop vượt ngưỡng (vài byte, vừa LoRa, S6), BS xếp hạng. Ngưỡng thấp vẫn đúng tinh thần "không bỏ sót", nhưng phải phát biểu ở mức camera chứ không ở mức ảnh. Ngược lại, nếu mục tiêu để lại k crop trong M, xác suất bỏ sót ở mức camera còn nhỏ hơn 0,6 % (nếu xem như độc lập: 0,006^k).

**b) Kích thước signature xung đột với lượng dữ liệu một cluster nhận được.**
- Một lượt bay trao cho mỗi cluster trung bình khoảng 415 KB (324–549 KB; mục 91).
- L ảnh × 50–200 KB: với L = 3–6 là 0,15–1,2 MB, tức ngang hoặc vượt D.
- Mỗi ảnh là một file 500–2 000 khung liền nhau; theo quy tắc mục 34, mất một khung là mất cả ảnh. Theo `l1_files.py`, khi truy vấn ≈ D chỉ khoảng 15 % critical cell có đủ mọi file.
- Mô hình body re‑ID nhận ảnh khoảng 256×128. Ảnh 50–200 KB bị thu nhỏ về cỡ đó trước khi embed, nên phần dung lượng vượt quá không giúp so khớp toàn thân. Một crop 256×128 JPEG chất lượng cao khoảng 10–20 KB.
- Đề xuất: (i) gửi ảnh ở đúng độ phân giải đầu vào của mô hình (khoảng 10–20 KB/ảnh, L = 3–6 ⇒ 30–120 KB, cỡ 7–30 % của D); hoặc (ii) giữ 50–200 KB nhưng chấp nhận River là bắt buộc, cần đường bay dài hơn trong cluster (LANE) hoặc nhiều lượt.

**c) Ảnh mặt chưa được dùng.** Bước 3 chỉ so toàn thân. Nếu giữ ảnh mặt trong signature, cần một bước so mặt riêng (chỉ hữu ích khi crop camera đủ lớn, xem §5), hoặc bỏ ảnh mặt để giảm dung lượng.

**d) Thiếu ảnh.** Nếu node chỉ ghép đủ một phần L ảnh (ví dụ thiếu ảnh nhìn sau), độ nhạy giảm theo view bị thiếu (−1 đến −25 điểm, báo cáo thứ hai). Báo cáo nên kèm bitmask các view node có.

**e) Người mặc cùng màu.** Đây chính là nguồn YES nhầm trong 6.3a. Ngưỡng thấp sẽ giữ họ lại; BS hoặc đội 2 loại họ ở bước xác minh.

### 6.4 Tham chiếu bổ sung

| | Tài liệu | Ghi chú |
|---|---|---|
| [7] | X. Li, A. Wu, W.-S. Zheng, "Adversarial Open‑World Person Re‑Identification", ECCV 2018, arXiv:1807.10482 | Đã đối chiếu Bảng 1 và §4.1–4.2 |

## 7. Mức đánh đổi và cỡ L, M (CLAUDE.md §8 mục 93)

### 7.1 Các mức đánh đổi, từ [7] Bảng 1 (Market‑1501, Individual Verification, ResNet‑50)

f là tỉ lệ YES nhầm trên mỗi ảnh người lạ, TTR là tỉ lệ YES đúng trên mỗi ảnh mục tiêu. Hai cột cuối là phép tính của ta (§6.3a), không có trong bài.

| f | TTR | Bỏ sót mỗi ảnh | Crop nhầm kỳ vọng, M = 100 / 1 000 | Bỏ sót mức camera nếu có k = 3 crop mục tiêu độc lập |
|---|---|---|---|---|
| 0,1 % | 82,26 % | 17,7 % | 0,1 / 1 | 0,56 % |
| 1 % | 95,86 % | 4,1 % | 1 / 10 | 0,007 % |
| 5 % | 98,54 % | 1,5 % | 5 / 50 | ≈ 0 |
| 10 % | 99,38 % | 0,6 % | 10 / 100 | ≈ 0 |
| 20 % | 99,58 % | 0,4 % | 20 / 200 | ≈ 0 |

- Điểm gãy nằm ở khoảng f = 1 %. Từ 0,1 % lên 1 % được thêm 13,6 điểm TTR; từ 1 % lên 10 % chỉ được thêm 3,5 điểm nhưng số crop nhầm tăng 10 lần.
- APN (mô hình của bài) cùng các mức: 84,00 / 96,72 / 98,69 / 99,58 / 99,58 %.
- Set Verification (danh sách 15 người) thấp hơn hẳn: ResNet‑50 80,00 % ở 1 %, 96,92 % ở 10 %.
- Cột k = 3 giả sử ba crop của mục tiêu độc lập (ba lần đi qua, ba thời điểm). Crop trong cùng một tracklet tương quan mạnh nên thực tế bỏ sót cao hơn.
- Mọi số ở đây đều lạc quan vì mục tiêu có trong tập huấn luyện của bài (§6.2).

**Đề xuất:** đặt ngưỡng ở f ≈ 1 % mỗi ảnh; node báo điểm cao nhất và số crop vượt ngưỡng; BS xếp hạng camera theo điểm.

### 7.2 Cỡ L theo D ≈ 400 KB mỗi cluster

D là tổng dữ liệu một cluster nhận dọc Axe (khoảng 4 100 khung × 99 B), không phải lượng một node nhận. Số dưới đây lấy từ `data/mission/l1-files.csv` (200 cluster, 1 304 critical cell, trước River):

| Truy vấn (phát lặp dọc D) | Tổng | Cell có đủ mọi file | Node tốt nhất có đủ mọi file |
|---|---|---|---|
| 4 ảnh × 15 KB | 60 KB (15 % D) | 99 % | 48 % |
| 12 ảnh × 15 KB | 180 KB (43 % D) | 97 % | 0 % |
| 40 file × 10 KB | ≈ D | 15 % | 0 % |

- Ranh giới: tổng truy vấn khoảng ≤ 45 % D, tức khoảng ≤ 180 KB, để phát được ít nhất 2 bản. Khi đó gom nội cell đã gần đủ, River chỉ phải bù phần nhỏ.
- **Ảnh 15–20 KB (đúng cỡ đầu vào body re‑ID): L = 6–10.** Ví dụ trước, nghiêng trái, nghiêng phải, sau, 1–2 ảnh trong điều kiện sáng khác, cộng 1–2 crop mặt khoảng 5 KB.
- **Ảnh 50 KB: L ≤ 3.** **Ảnh 200 KB: L = 1–2**, và đã vượt D nếu L ≥ 3.
- Chưa đo: file 500–2 000 khung (50–200 KB). Bản đo hiện có chỉ tới 150 khung. Tỉ lệ file nguyên vẹn ở mức cell gần như không đổi từ 50 lên 150 khung (80 % → 78 %), vì mất gói ở cell theo cụm, nên file lớn hơn có lẽ giảm chậm, nhưng phải đo mới nói được. Dữ liệu bit thô của lượt bay không còn trên máy này; muốn đo phải chạy lại pass ns‑3.

### 7.3 M

M không bị D ràng buộc; nó là tham số kịch bản của camera (lưu lượng người qua × thời gian lưu).
- Nên đếm M theo **tracklet** (một người đi qua một lần), không theo khung hình; một tracklet cho một điểm, khớp với cách [7] đếm trên ảnh.
- Gợi ý quét M ∈ {100; 1 000; 10 000}: chuông cửa hoặc ngõ nhỏ vài trăm mỗi ngày, mặt tiền cửa hàng vài nghìn.
- M chỉ quyết định số crop nhầm f·M và vì vậy độ tin của việc xếp hạng ở BS; với f = 1 %, M = 1 000 cho khoảng 10 crop nhầm mỗi camera, nên báo cáo phải là điểm, không phải YES/NO.

## 8. Bản phát biểu chốt (CLAUDE.md §8 mục 98; khung theo mục 92, tham số theo mục 93–97)

### 1. Mục tiêu
Mỗi camera biên tại một critical cell trả lời: **một người cụ thể đã xuất hiện trước camera này hay chưa?** Yêu cầu ưu tiên là hạn chế tối đa bỏ sót. Báo nhầm được chấp nhận vì BS xếp hạng các báo cáo và đội 2 xác minh tại chỗ.

### 2. Camera ghi được gì
- Camera giữ một tập **M crop người** cắt từ video, đếm theo **tracklet**: một người đi qua một lần cho một crop đại diện.
- Kích thước, góc nhìn, ánh sáng và độ nét của các crop rất khác nhau.
- Không chắc có mục tiêu trong đó. Nếu có, mục tiêu để lại **k** crop, tức đi qua k lần.
- Mỗi crop đều chứa một người. Nhiều người có thể mặc cùng màu với mục tiêu.
- Tham số giả lập: M ∈ {100; 1 000; 10 000}, ứng với ngõ nhỏ hoặc chuông cửa lên tới mặt tiền đông người; k ∈ {1; 3}.

### 3. Tập ảnh signature
- BS gửi **L ảnh toàn thân** của mục tiêu, mỗi ảnh **F = 15–50 KB**, chọn theo góc **trước → sau → nghiêng**, rồi lặp lại nếu L > 3.
- Mỗi ảnh là một file F·1000/99 khung (15 KB → 152 khung, 50 KB → 506 khung). Mất một khung là mất cả ảnh (mục 34).
- **Giới hạn dung lượng:** mỗi cluster nhận trung bình D ≈ 415 KB dọc Axe (324–549 KB). Truy vấn L·F nên ≤ khoảng 180 KB (≈ 45 % D) để UAV phát lặp được ít nhất 2 lần. Khi đó gom nội cell đã cho đủ mọi ảnh ở 97–99 % critical cell.
- **L hợp lý: 3–6.** L = 3 đủ ba góc. Thêm ảnh cùng góc gần như không giúp ([7] Bảng 4: từ 1 lên 2 ảnh mục tiêu chỉ thêm 0,8–2,3 điểm).
- Ảnh mặt chưa dùng trong bước so khớp. Nếu gửi thì cần một bước so mặt riêng.

### 4. Node nhận dạng thế nào
1. **Chuẩn bị sẵn:** M crop đã được embed bằng mô hình của node ngay lúc ghi hình, lưu thành chỉ mục: 2 048 chiều, fp16, 4 KB mỗi crop.
2. **Nhận signature:** node giải mã và embed từng ảnh signature ngay khi ảnh đó đủ, bằng cùng mô hình.
3. **So khớp toàn thân:** mỗi crop lấy điểm cao nhất trên các ảnh signature node đang giữ. Crop vượt ngưỡng t thì tính là YES. Điểm của node là điểm crop cao nhất.
4. **Báo cáo về BS qua CH và LoRa:** vài byte gồm điểm cao nhất, số crop vượt ngưỡng và các góc node đang giữ. BS đổi điểm thành xác suất "đây là camera của mục tiêu" và đội 2 thăm theo thứ tự đó.

### 5. Điểm vận hành
Tham chiếu: [7] Bảng 1/4, Market‑1501, Individual Verification, ResNet‑50 (758 người lạ, 14 573 ảnh thử). f là tỉ lệ YES nhầm trên mỗi crop người lạ.

| f | YES đúng mỗi crop | Bỏ sót mỗi crop |
|---|---|---|
| 0,1 % | 82,3 % | 17,7 % |
| 1 % | 95,9 % | 4,1 % |
| 5 % | 98,5 % | 1,5 % |
| 10 % | 99,4 % | 0,6 % |

- **Trong giả lập:** điểm người lạ ~ N(0; 1), điểm mục tiêu ~ N(4,43; 1,30), khớp vào các điểm trên (sai lệch ≤ 2,6 điểm). Crop mục tiêu có góc mà node không giữ ảnh nào ~ N(3,04; 1,30), tức mất 25 điểm ở f = 1 %. Mức phạt này là giả định.
- **Ở mức camera:** bỏ sót = (1 − TTR)^k. Ví dụ f = 0,1 %, k = 3 → khoảng 0,6 %.
- **YES nhầm ở mức camera:** 1 − (1 − f)^M. Ví dụ f = 0,1 %, M = 1 000 → 63 %.
- Vì vậy node không báo YES/NO trần mà báo điểm để BS xếp hạng. **Mức f = 0,1 % (82,3 %) dùng được khi k ≥ 3.** M lớn không giảm bỏ sót, chỉ làm loãng thứ hạng.

### 6. Thiết bị và thời gian xử lý
- Critical cell là thiết bị cỡ **Raspberry Pi 5 chạy ResNet‑50** (25,6 triệu tham số):

  | Cấu hình | Tốc độ embed | Nguồn |
  |---|---|---|
  | Pi 5 + Hailo‑8L | 257,6 ảnh/s | Hailo Community, 2024 |
  | Pi 5 CPU INT8 | 12,6 ảnh/s | arXiv:2609.16085 |

- **Thời gian đối sánh:** T_match = L · 5 ms + L / R + tìm kiếm.
  - L = 3: 0,03 s với Hailo, 0,25 s với CPU.
  - M = 100 000 thêm chưa tới 0,05 s.
- **Ảnh tới nhanh hơn cách nào cũng không được:** một ảnh 15 KB cần ít nhất 0,65 s trên 802.15.4 (1,52 s theo nhịp UAV), nên node luôn xử lý xong trước khi ảnh sau tới.
- **Điều kiện:** chỉ mục phải có sẵn. Nếu phải embed lại M crop thì thêm M / R: 39 s (Hailo) hoặc 13 phút (CPU) với M = 10 000.
- **Ràng buộc thật khi chỉ có CPU:** lập chỉ mục theo kịp camera (khoảng 13 crop/s), nên phải embed theo tracklet chứ không theo từng khung hình.
- **Độ trễ từ lúc UAV rời cluster tới lúc có báo cáo** do lớp 3 và LoRa quyết định, không do đối sánh:
  - River: trung bình 24 s (p90 55 s);
  - chờ khe LoRa: 0–40 s.

### 7. Giới hạn cần ghi trong paper
- [7] huấn luyện trên chính các mục tiêu và thử trên cùng 6 camera, nên số liệu lạc quan so với mục tiêu chưa từng thấy và camera khác miền.
- Crop trong cùng tracklet tương quan mạnh. M và k phải hiểu là số tracklet.
- Các số ước tính chưa đo trên Pi: giải mã 5 ms, băng thông bộ nhớ 8 GB/s, mức phạt góc −25 điểm.

### Bảng tham số giả lập (`uav-l2/tools/l1_mission.py`)

| Ký hiệu | Ý nghĩa | Giá trị |
|---|---|---|
| M | crop (tracklet) mỗi camera | 100; 1 000; 10 000 |
| k | crop mục tiêu tại camera thật | 1; 3 |
| L | ảnh signature | 1; 2; 3; 4; 8 (đề xuất 3–6) |
| F | cỡ mỗi ảnh | 15; 50 KB |
| f | YES nhầm mỗi crop (ngưỡng t) | 0,1; 1; 5; 10 % |
| MU, SIGMA | điểm mục tiêu | 4,43; 1,30 |
| MU_X | điểm mục tiêu khi thiếu góc | 3,04 |
| R | tốc độ embed | 257,6 (Hailo‑8L) / 12,6 (CPU) ảnh/s |
| T_decode, DIM | giải mã; chiều vector | 5 ms; 2 048 (fp16) |
