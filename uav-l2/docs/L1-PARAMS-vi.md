# Lớp 1: câu hỏi nghiên cứu và tham số đang dùng trong giả lập

Lời gốc: CLAUDE.md §8 mục 83, 85, 86.

**Nguồn:**
- Số đề xuất lấy từ báo cáo `reports/Nhận dạng tại node biên lớp 1.md` và phép tính `L1-HOOKS-vi.md` §2.
- Nhãn [nguồn], [nguồn·trích], [chưa kiểm], [mô hình] giữ nguyên nghĩa như trong báo cáo.

**Cột "Trạng thái":**
- **tạm**: số đặt tạm, chưa có cơ sở lớp 1.
- **khớp**: số đang dùng nằm trong khoảng lớp 1 đề xuất.
- **thiếu**: giả lập chưa có tham số cho câu hỏi này.

## 1. Câu hỏi anh/chị đặt (mục 83)

| Mã | Câu hỏi nghiên cứu | Tham số trong giả lập (file) | Đang dùng | Lớp 1 đề xuất | Trạng thái |
|---|---|---|---|---|---|
| Q1 | Node trả lời câu nào, nhận dạng đối tượng gì | Không có. Nghi vấn sinh ngẫu nhiên: 1 thật + 2–3 giả mỗi bản đồ (`mission_policy.py`, `draws`) | Không mô hình | Truy hồi mở theo tracklet, chính là body re‑ID, có cổng người/trẻ em và thuộc tính. Mặt chỉ là kênh phụ ở cửa ra vào [nguồn] | thiếu |
| Q4 | Đơn vị phát và số bit mỗi signature | `PAYLOAD = 99` B/khung (`mission_baselines.py`). Giả lập phát chuỗi D gói, không phân biệt loại dữ liệu | 99 B/khung; signature không định nghĩa | Mã 64 B (PQ‑64 / 512 bit) = 1 khung; template fp16 512‑d = 11 khung; int8 = 6 khung; crop JPEG 5–15 kB = 50–150 khung [nguồn + mô hình] | thiếu |
| Q5 | Mỗi mục tiêu cần mấy signature (file) | Không có. River đòi critical cell gom **toàn bộ D**: 3 268–5 542 khung, trung bình 4 200 | D | **3–4 view đa dạng** mỗi mục tiêu, gộp thành template (lợi ích bão hòa ở khoảng 3) [nguồn + mô hình] | tạm (cao gấp 2–100 lần) |
| Q9 | Tập có phân lớp thô → tinh được không | Không có | Không | L0 thuộc tính (≤ 16 B), L1 mã 64 B, L2 template khoảng 11 khung, L3 prototype theo điều kiện. Embedding phải được huấn luyện để cắt được (MRL) [nguồn, số trên ImageNet] | thiếu |
| Q10 | Recall/precision theo tỉ lệ tập nhận được | Ngưỡng B4: cell thật phát hiện nếu giữ ≥ θ của D, θ ∈ {0,85; 0,9; 0,95} (`THETAS`) | Bậc thang theo tỉ lệ gói | recall(f) ≈ recall₁₀₀ · (1 − 0,15…0,2 · e^(−fK/2,5)); nhận 20 % của 15 view vẫn giữ khoảng 95 % recall [mô hình]. Phụ thuộc **số file nguyên vẹn**, không phụ thuộc tỉ lệ gói | tạm |
| Q15 | Số bit tối thiểu để báo nhầm vừa ngân sách phản hồi | Số nghi vấn giả cố định 2–3 mỗi bản đồ. Kênh LoRa: `AIR = 0,4` s, `DUTY = 1 %`, một khe mỗi `GAP = 40` s cho mỗi CH | 2–3 giả trên 2–8 cluster | E[FA] ≤ 1 mỗi cluster ⇒ FMR 10⁻⁸–10⁻¹⁰; khoảng 111–360 bit hiệu dụng; 256 bit nếu khớp theo tracklet [mô hình] | khớp (số nghi vấn giả) / thiếu (bit) |
| Q16 | Ngưỡng cố định hay node tự chỉnh | Điểm nghi vấn: thật ~ U(0,5; 1), giả ~ U(0,2; 0,8) (`S_TRUE`, `S_FALSE`). Đội 2 chọn theo điểm / thời gian | Điểm ngẫu nhiên, không ngưỡng | Node chuẩn hóa điểm (S‑norm) và gửi LLR; ngưỡng cổng tại node tăng theo k·G; BS quyết định bằng Benjamini–Hochberg [nguồn + mô hình] | tạm |

## 2. Câu hỏi phát sinh từ giả lập (mục 85)

| Mã | Câu hỏi nghiên cứu | Tham số trong giả lập (file) | Đang dùng | Lớp 1 đề xuất | Trạng thái |
|---|---|---|---|---|---|
| S1 | Truy vấn lớn cỡ nào so với D, có phát lặp không | River gom toàn bộ D, phát một lần | Q ≈ D, không lặp | Q = 44–1 800 khung (1–43 % của D) cho 1–3 mục tiêu. Nếu phát lặp, gom nội cell đã đủ mọi file cho **97–99,5 %** critical cell; với Q ≈ D chỉ **15 %** [tính trên bit ns‑3] | **quyết định giá trị của River** |
| S2 | Cỡ file F (số khung) và quy tắc "đủ mới dùng" | Lượt bay: chuỗi gói liền nhau (mục 34). River đếm gói lẻ | Gói lẻ | F = 1 / 6 / 11 / 50 / 150 khung tùy biểu diễn. Sau lượt bay, cell giữ 78–90 % file nguyên vẹn, node đơn lẻ chỉ 13–66 % (`l1_files.py`) | thiếu |
| S3 | Edge nhận đủ thì phát hiện đúng bao nhiêu (P_d) | Cell thật chắc chắn phát hiện khi đủ dữ liệu | P_d = 1 | Body re‑ID R1 82–95 % (sạch), 40–71 % (đổi quần áo); mặt trong ảnh giám sát R1 29,9 % [nguồn]. Open‑set ở FPIR thấp chưa có số | tạm (quá lạc quan) |
| S4 | Đối sánh mất bao lâu | `MATCH = 5` s (`mission_policy.py`, `mission_baselines.py`, `mission_report.py`) | 5 s | Có chỉ mục embedding sẵn: mili‑giây tới giây. Quét video thô một thẻ 5,5 ngày: T1 11–22 giờ, T2 2–4 giờ, T0 trên 66 giờ [mô hình] | khớp nếu có chỉ mục / sai lệch hàng giờ nếu quét thô |
| S5 | Node nào đủ sức làm điểm xử lý | Critical cell = cell CH + ngoại lệ toàn cục (μ + 2σ) + ngoại lệ cục bộ (μ + σ, tốt nhất trong 2 vòng) theo điểm obs·cpu·comm, mỗi thuộc tính ~ U[0,1) (`river_plan.py kg=2, kl=1, r=2`; `deploy.h`) | Điểm ngẫu nhiên | Chỉ T1 trở lên (≥ 0,5–2 TOPS) quét kịp trước khi bị ghi đè; T0 chỉ làm phát hiện. Gán cpu theo tầng T0–T3 [mô hình] | tạm |
| S6 | Báo cáo về BS cần bao nhiêu byte | Mỗi bản tin LoRa chở mọi kết quả đã tới CH; `HOP = 0,1` s mỗi cell để chuyển kết quả về CH | Không giới hạn byte | Khoảng **6 B mỗi node** (LLR, log₂M, tỉ lệ tham chiếu, chất lượng); một bản tin LoRa chở được vài chục kết quả [mô hình] | khớp |
| S7 | Đội 2 cần đưa bao nhiêu để xác minh gần như chắc chắn | `BIG = 1 MiB` unicast, `SETTLE = 5` s, `MATCH = 5` s ⇒ khoảng 83 s mỗi lần thăm (`mission_baselines.py`); `HOVER = 30` s trong `mission_policy.py` | 1 MiB / 30–83 s | Truy vấn giàu 10–50 kB (0,7–3,5 s), hoặc **đảo chiều**: node gửi crop khớp nhất (10–50 kB, 1–4 s) lên UAV để người hoặc mô hình mạnh ở BS xác nhận; khoảng 15 s mỗi lần thăm [mô hình] | tạm |
| S8 | Mức "gần như chắc chắn" khi xác minh là bao nhiêu | Cell thật được xác nhận chắc chắn khi đội 2 tới | P = 1 | Chưa có số: phụ thuộc người duyệt, chất lượng crop, và việc kết hợp mặt + thân + thời gian | thiếu |
| S9 | Tệp nhẹ của baseline B3/B6 | Tệp nhẹ = \|D\| trung bình của bản đồ ≈ 0,41–0,45 MB | 0,41–0,45 MB | Bằng Q của S1: 4–180 kB [mô hình] | tạm |
| S10 | Số mục tiêu tìm cùng lúc | 1 mục tiêu (1 cell thật) | 1 | 1–3 mục tiêu, nhân Q và số so sánh theo số mục tiêu [mô hình] | thiếu |

## 3. Tham số nào đổi thì kết luận nào thay đổi

| Tham số | Kết luận đang phụ thuộc vào nó |
|---|---|
| S1 (Q/D, phát lặp) | Giá trị của River so với gom nội cell; B4 "mất cell thật ở 25–62 % lượt" |
| Q10 / S3 (P_d) | Tỉ lệ thành công của mọi phương án; số lượt thăm của đội 2 |
| S4 (MATCH) | Thời điểm kết thúc nhiệm vụ; lợi thế của đội 2 xuất phát sớm |
| S7 (xác minh) | Khoảng cách P so với B1/B2 (cả hai đều trả thời gian xác minh ở mỗi critical cell) |
| Q16 (điểm nghi vấn) | Lợi thế của thứ tự thăm theo điểm so với TSP |
