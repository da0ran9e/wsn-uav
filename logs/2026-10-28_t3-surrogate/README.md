# 2026-10-28 · Kiểm tra Bậc 3: bộ dự đoán River học bằng cây có chọn đường bay tốt hơn công thức không

**Câu hỏi:** người dùng yêu cầu thử khoảng 200 lượt River; nếu kết quả không thực sự hơn thì bỏ. Bậc 3 của `SigDrop2_LMTour_Surrogate_guide.pdf` là LightGBM; ở đây dùng HistGradientBoosting của scikit-learn với cùng tham số (400 vòng, lr 0,05) và ràng buộc đơn điệu.

**Đường bay** (`variants.py ENV`):
- Mỗi (kênh, cụm) của k8-s1 có 6 biến thể: v0 là đường DTSP-N của LM-Tour (hướng lấy từ `runs/LMD`) không uốn; v1–v5 uốn về một critical cell ngoài ξ, hết thì uốn về hai cell.
- Mỗi biến thể phải cắt cụm một lần.
- Biến thể j của mọi cụm chung một thư mục `runs/T3v{j}/ENV/k8-s1`. Cụm thiếu biến thể thì bay lại v0; `t3.py` bỏ đường trùng.

**ns-3** (`run.sh ENV`): 24 mission × 8 cụm = 192 lượt pass + River, CAMP-BIN local, `--riverRepair 20`. Mọi critical cell đều xong (0 cell kẹt).

**Phân tích** (`t3.py > table.md`):
- Tập thử: 1 457 kết quả cell; 253 đường bay khác nhau trên 32 nhóm (kênh, cụm), 5–10 đường mỗi nhóm. Gồm cả các đường CP, LM, LMD, DR có sẵn. DR r200 bị bỏ vì `check_plan` không khớp.
- Setting A: học trên k12, k16 (632 cell của `river-surrogate.csv`). Setting B: thêm các đường thử của các cụm k8 khác, bỏ một cụm mỗi lượt.
- Chỉ số: S = Σ doneS của các critical cell trong cụm; Spearman của S trên các đường trong nhóm; regret là S thật của đường mô hình chọn trừ S thật nhỏ nhất.

## Kết quả

| setting | mô hình | MAE doneS (s) | Spearman | regret (s) | chọn đúng |
|---|---|---|---|---|---|
| A | công thức (Bậc 2) | 19,5 | 0,52 | **26,2 ± 30,0** | 34 % |
| A | tuyến tính, 12 đặc trưng | 20,2 | 0,50 | 26,9 ± 30,0 | 34 % |
| A | GBR sâu 2 | 19,7 | 0,42 | 45,9 ± 55,8 | 34 % |
| A | HGB (Bậc 3) | 21,5 | 0,47 | 43,9 ± 46,1 | 28 % |
| B | công thức | 19,4 | 0,39 | 59,4 ± 50,4 | 31 % |
| B | HGB | 20,3 | 0,43 | 46,9 ± 46,1 | 34 % |
| – | chọn ngẫu nhiên | – | 0 | 58,6 | – |

Regret HGB − công thức: A **+17,7 ± 24,7 s** (HGB hơn ở 9, kém ở 12 trong 32 nhóm); B −12,5 ± 37,4 s (10 hơn, 9 kém).

## Đọc
1. **Bậc 3 không hơn Bậc 2.** Với tập học từ bản đồ khác (A, đúng cách dùng thật), HGB chọn đường kém hơn công thức 18 s mỗi cụm, MAE cao hơn 2 s. Khi được học thêm đường của chính bản đồ (B), chênh nằm trong nhiễu. → **Bỏ Bậc 3**, giữ công thức.
2. **Công thức xếp hạng đường trong một cụm ở mức trung bình** (Spearman 0,52, chọn đúng đường tốt nhất 34 %). Regret 26 s so với 59 s của chọn ngẫu nhiên: có giá trị, nhưng còn xa hoàn hảo. Thêm dữ liệu cùng bản đồ (B) không giúp công thức.
3. Không mô hình nào hơn hẳn, kể cả khi cho thêm dữ liệu. Nếu muốn cải thiện việc chọn đường, hướng đáng thử là đặc trưng mới (mô tả cách đường bay đổi tải River của cả cụm), không phải mô hình phức tạp hơn. Chưa đo nhiễu lặp lại của một lượt River (cùng đường, khác seed), nên chưa biết trần của bài toán xếp hạng này.
