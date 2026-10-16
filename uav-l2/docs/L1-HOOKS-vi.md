# Lớp 1 chạm vào giả lập ở đâu

Lời gốc: CLAUDE.md §8 mục 85.

Nguồn số liệu:
- Báo cáo `reports/Nhận dạng tại node biên lớp 1.md`. Các nhãn [nguồn], [nguồn·trích], [chưa kiểm], [mô hình] giữ nguyên như trong báo cáo.
- Phép tính mới trên dữ liệu lượt bay đã có: `uav-l2/tools/l1_files.py` → `data/mission/l1-files.csv`. Phép tính dùng 40 bản đồ, 200 cluster, **1 304 critical cell**, và không chạy ns-3 mới.

## 1. Bảng đối chiếu: số tạm trong giả lập và điều lớp 1 nói

| # | Câu hỏi lớp 1 | Giả lập hiện nay (số tạm) | Lớp 1 nói gì | Hệ quả |
|---|---|---|---|---|
| 1 | Critical cell cần bao nhiêu dữ liệu là "đủ" | **Toàn bộ D** của cluster: 3 268–5 542 khung, trung bình 4 200 (≈ 0,42 MB) | Mỗi mục tiêu cần 3–4 view đa dạng, gộp thành template [mô hình, từ NIST, IJB‑A, MARS]. Một truy vấn gồm 4 file: **44 khung** nếu là mã fp16, **200–600 khung** nếu là crop JPEG 5–15 kB. Với 1–3 mục tiêu: 44–1 800 khung = **1–43 % của D** | Mục tiêu của River ("gom đủ D") có thể cao gấp 2–100 lần nhu cầu thật. Xem §2 |
| 2 | Cần bao nhiêu file phân biệt | Không có khái niệm file: D là một chuỗi gói, River đếm gói | **3–4 file mỗi mục tiêu** (L2 template + L3 prototype theo điều kiện), cộng 1 file L0+L1 dài 1 khung | Đơn vị "đủ" của lớp 3 nên là **"đủ V file phân biệt"**, không phải "đủ D gói" |
| 3 | Gói rời có ghép được không | Lượt bay đã dùng quy tắc "chỉ gói liền nhau mới thành file" (mục 34). River vẫn đếm gói lẻ | Mã 1 khung sống độc lập. File nhiều khung cần đủ mọi khung, trừ khi dùng fountain code [mô hình] | Cỡ file F quyết định mất mát (§2) |
| 4 | Edge nhận đủ thì phán đoán đúng bao nhiêu | Cell thật chắc chắn phát hiện khi đã sẵn sàng. Điểm: thật ~ U(0,5; 1), giả ~ U(0,2; 0,8) | Body re‑ID, gallery đóng: R1 **82–95 %** (MSMT17 / Market) [nguồn]. Đổi quần áo: R1 **40–71 %** [nguồn]. Mặt trong ảnh giám sát thật: R1 **29,9 %**, TPIR ≈ 13 % ở FPIR 10 % [nguồn]. Chế độ mở (open‑set) ở FPIR thấp: chưa có số re‑ID | "Chắc chắn phát hiện" là quá lạc quan. Cần một xác suất phát hiện P_d < 1 cho cell thật, phụ thuộc số view nhận được (#5) |
| 5 | Mỗi file và mỗi bộ file cho bao nhiêu | Không mô hình | **1 view so với nhiều view:** NIST lỗi giảm khoảng 10 lần với khoảng 6 ảnh. IJB‑A tăng 19 % từ 1 lên 64 ảnh, bão hòa ở khoảng 3. MARS: R1 75,0 → 79,8 % khi tăng từ 2 lên 4 khung [nguồn]. Luật xấp xỉ: recall(f) ≈ recall₁₀₀·(1 − 0,15…0,2·e^(−fK/2,5)) [mô hình] | Giả lập có thể lấy **P_d = recall(số file nguyên vẹn đã nhận)**, thay cho ngưỡng "≥ t của D" của B4 |
| 6 | Bao nhiêu nghi vấn giả | 2–3 nghi vấn giả cho mỗi bản đồ | Muốn E[FA] ≤ 1 mỗi cluster thì FMR mỗi phép so sánh phải 10⁻⁸–10⁻¹⁰. Điều đó buộc phải khớp theo tracklet, gộp template, và BS kiểm soát FDR [mô hình] | 2–3 nghi vấn giả trên 2–8 cluster khớp với mục tiêu E[FA] ≤ 1 mỗi cluster. Giữ được, nhưng nên sinh từ mô hình FMR thay vì cố định |
| 7 | Edge xử lý mất bao lâu | **MATCH = 5 s** | Quét **footage thô** của một thẻ 5,5 ngày: chip camera (T1) **11–22 giờ**; Pi + Hailo / RK3588 (T2) **2–4 giờ**; ESP32‑S3 66 giờ trở lên [mô hình, từ số nhà sản xuất đã giảm]. Nếu thiết bị **đã lập chỉ mục embedding sẵn**, tức luôn trích re‑ID cho mọi tracklet, thì chỉ còn tìm 10⁴–10⁶ vector 512 chiều: ≈ 5·10⁷–5·10⁸ phép nhân‑cộng, tức mili‑giây tới giây trên T1 [mô hình] | **5 s chỉ đúng khi node lập chỉ mục sẵn.** Nếu phải quét video thô thì MATCH tính bằng giờ và lấn át mọi thời gian khác của nhiệm vụ. Cần anh/chị chốt giả định |
| 8 | Node nào xử lý | Critical cell = CH + cell vượt trội (μ + 2σ toàn cục, μ + σ cục bộ) theo điểm năng lực ngẫu nhiên | Chỉ từ T1 (≥ 0,5–2 TOPS) mới quét kịp trước khi bị ghi đè [mô hình]. T0 (MCU, chuông cửa rẻ) chỉ làm được phát hiện | Thuộc tính "khả năng tính toán" của node có thể gán theo tầng T0–T3 thay cho phân bố U[0,1) |
| 9 | Báo cáo về BS nặng bao nhiêu | Một bản tin LoRa 0,4 s cho mỗi CH, chở mọi kết quả | Khoảng **6 B mỗi node**: LLR, log₂M, tỉ lệ tham chiếu, chất lượng [mô hình] | Khớp. Một bản tin LoRa chở được vài chục kết quả |
| 10 | Đội 2 cần đưa bao nhiêu để xác minh gần như chắc chắn | Treo 5 s + **1 MB** unicast (≈ 73 s) + đối sánh 5 s ≈ **83 s** mỗi lần thăm | 1 MB ≈ 70–200 crop, vượt xa mức bão hòa 3–6 view. Truy vấn giàu đầy đủ (nhiều view fp32 + template mặt) chỉ khoảng **10–50 kB → 0,7–3,5 s** [mô hình]. Muốn gần như chắc chắn, cách đáng tin hơn là **đảo chiều**: node gửi crop tracklet khớp nhất lên UAV (10–50 kB, khoảng 1–4 s), rồi người hoặc mô hình mạnh ở BS xác nhận | Thời gian thăm có thể giảm từ khoảng 83 s xuống khoảng 15 s, tiết kiệm khoảng 70 s × 1,8 lượt thăm. **Mức "gần như chắc chắn" chưa có số**: nó phụ thuộc người duyệt và chất lượng crop |
| 11 | Ngưỡng B4 (không hợp tác) | Cell thật phát hiện được nếu giữ ≥ 0,85 / 0,9 / 0,95 của D | Phát hiện phụ thuộc **số file nguyên vẹn**, không phụ thuộc tỉ lệ gói (#2, #5) | Kết luận "B4 mất cell thật ở 25–62 % lượt" phụ thuộc hoàn toàn vào số tạm này. Xem §2 |

## 2. Phép tính mới: critical cell giữ được gì ngay sau lượt bay, trước River

Cách tính:
- D được cắt thành các file liền nhau, mỗi file F khung. Một file chỉ tính khi giữ đủ mọi khung.
- "Node" = node tốt nhất của critical cell, bay qua xong không hợp tác gì.
- "Cell" = gộp các node trong cell. Đây là gom nội cell, tức B4, chưa có River.

**a) Tỉ lệ file nguyên vẹn khi phát D một lần, file không lặp:**

| Cỡ file | 1 khung (mã 64 B) | 6 (int8) | 11 (fp16) | 21 (fp32) | 50 (crop ~5 kB) | 150 (crop ~15 kB) |
|---|---|---|---|---|---|---|
| Node: trung bình / p10 | 0,66 / 0,46 | 0,41 / 0,15 | 0,33 / 0,06 | 0,26 / 0,02 | 0,19 / 0,00 | 0,13 / 0,00 |
| Cell: trung bình / p10 | 0,90 / 0,72 | 0,84 / 0,65 | 0,83 / 0,63 | 0,82 / 0,61 | 0,80 / 0,59 | 0,78 / 0,57 |

**b) Một truy vấn gồm V file phân biệt, mỗi file F khung, phát lặp lại suốt D. Tỉ lệ critical cell có đủ cả V file:**

| Truy vấn | Tổng khung (so với D ≈ 4 200) | Node | **Cell** |
|---|---|---|---|
| 4 × 11 (1 mục tiêu, template fp16) | 44 (1 %) | 0,94 | **0,995** |
| 4 × 50 (1 mục tiêu, crop 5 kB) | 200 (5 %) | 0,72 | **0,99** |
| 4 × 150 (1 mục tiêu, crop 15 kB) | 600 (14 %) | 0,48 | **0,99** |
| 12 × 150 (3 mục tiêu, crop 15 kB) | 1 800 (43 %) | 0,00 | **0,97** |
| 40 × 100 (truy vấn dài bằng D, như giả lập hiện nay) | 4 000 (≈ 95 %) | 0,00 | **0,15** |

**Điều này nói gì (phải ghi thẳng):**
- Nếu truy vấn nhỏ so với D (≲ 40 % của D) và UAV **phát lặp lại** nó suốt đoạn bay, gom nội cell đã đưa đủ mọi file tới **97–99,5 %** critical cell. River (hợp tác giữa các cell) khi đó chỉ còn cứu khoảng 0,5–3 % cell nằm xa đường bay.
- River trở nên thiết yếu khi **truy vấn xấp xỉ D**: khi đó chỉ 15 % critical cell tự đủ. Đó là giả định của giả lập hiện nay (gom đủ D) và cũng là tinh thần mục 38–40: nhiều file không thay thế được cho nhau, UAV phát liên tục, cluster nhận càng nhiều càng tốt.
- Vì vậy, **giá trị của River phụ thuộc trực tiếp vào cỡ truy vấn Q/D**, tức vào lớp 1. Paper cần phát biểu rõ chế độ hoạt động: truy vấn lớn, gồm ảnh hoặc video tham chiếu, nhiều mục tiêu, nhiều prototype. Hoặc phải chứng minh lợi ích theo cách khác: thời gian, phần cell xa đường bay, hay cell không có node đủ mạnh.
- Kết luận B4 cũ ("mất cell thật ở 25–62 % lượt") **không còn đứng vững** dưới mô hình file + lặp. Nó chỉ đúng khi truy vấn ≈ D.

**Giới hạn của phép tính:**
- Một lượt bay cho mỗi cluster, dùng chính bit của ns-3 đã có.
- Fading không đổi trong một gói. Theo đặc tả mục 2, giả định này làm kết quả lạc quan khoảng 4 lần với chuỗi gói dài; file 1–11 khung ít bị ảnh hưởng.
- Chưa tính thời gian gom nội cell.
- Cell gom được mọi node, tức giả định không có ràng buộc sở hữu.

## 3. Cần anh/chị chốt

1. **Mô hình truy vấn.** Có ba lựa chọn:
   - (A) Truy vấn nhỏ, phát lặp: thực tế theo lớp 1, nhưng River chỉ cứu ít cell.
   - (B) Truy vấn ≈ D: giữ nguyên giả lập hiện nay.
   - (C) **Quét Q/D** từ 1 % đến 100 % (đề xuất). Điểm giao nằm khoảng 40–95 % của D sẽ là một kết quả của paper.
   
   Phần phân phối tính được ngay trên bit ns-3 đã có. Riêng River cần chạy lại với mục tiêu "đủ V file", và việc này tốn thời gian.
2. **MATCH.** Có hai lựa chọn: node lập chỉ mục embedding sẵn (MATCH vài giây, giữ được 5 s), hoặc quét video thô (MATCH hàng giờ, cần mô hình khác).
3. **Xác minh của đội 2.** Có hai lựa chọn: giữ tệp 1 MB đi xuống, hoặc đổi sang đảo chiều (node gửi crop lên UAV, 10–50 kB).
4. **P_d.** Có nên thay "cell thật chắc chắn phát hiện" bằng P_d = recall(số view nguyên vẹn) theo luật bão hòa ở #5 không?
