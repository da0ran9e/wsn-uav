# Nhiệm vụ trọn vẹn với mô hình lớp 1 mới: đề xuất, ablation, baseline

Lời gốc: CLAUDE.md §8 mục 110–114. Mô hình lớp 1 (bản cho System Model): `paper/L1-MODEL-vi.md`.
Mã: `tools/l1_model.py` (mô hình điểm), `tools/l1_rank.py` (cả nhiệm vụ), `tools/l1_compare.py` (bảng, hình), `tools/subch.py` (baseline subCH), `tools/tour_heur.py` (tour khi có nhiều cluster), `tools/l1_anim.py` + `anim/l1-head.html`, `anim/l1-body.html` (hình động), `tools/l1_steps.py` (hình từng bước).
Log: `logs/2026-10-20_1834-l1-mission/`, `logs/2026-10-20_1934-campaign2/`.

__SUMMARY__

## 1. Cách làm: ba vòng

| Vòng | Làm gì | Dữ liệu ns‑3 |
|---|---|---|
| 1 | Cài mô hình lớp 1 vào nhiệm vụ. So P cũ, không hợp tác, thứ tự phát, độ quan trọng, các baseline. | Có sẵn: 39 bản đồ cluster có sẵn (k‑medoids, River đầy đủ D); 3 bản đồ cho mọi cách chia lớp 2. |
| 1b | Thử bốn ý tưởng rút ra từ vòng 1 (mục 2.2), từng cái và tổ hợp. | Như vòng 1. |
| 2 | Chạy ns‑3 mới cho đủ 40 bản đồ: River cửa sổ cho cluster có sẵn, baseline subCH, MEANDER (lớp 2 đề xuất). So mọi phương án với chính sách tốt nhất. | 40 bản đồ × 3 cách chia. |
| 3 | Độ nhạy theo tham số lớp 1, chọn cấu hình cuối, báo cáo từng bước. | Như vòng 2. |

Đơn vị độc lập là **bản đồ**: 10 bản đồ mỗi cỡ (2, 4, 6, 8 cluster). Mỗi bản đồ chạy 100 lượt bốc (kho ảnh, nhiễu đối sánh, pha LoRa), ghép cặp giữa mọi phương án: cùng bản đồ, cùng lượt bốc thì cùng một "thế giới". Khoảng tin cậy 95 % tính trên trung bình của từng bản đồ (phân phối t, 9 bậc tự do). Mười bản đồ mỗi cỡ là dưới quy tắc N ≥ 120, nên mọi số ở đây là số thăm dò. Bằng chứng chính là chiều chênh lệch nhất quán qua các bản đồ (đếm số bản đồ thắng).

## 2. Phương án đề xuất, từng bước

### 2.1 Các bước
1. **Bản đồ và cluster (lớp 2).** Miền có hồ, chia thành cluster ≤ 80 cell. Cluster có sẵn là k‑medoids; MEANDER là cách tái cấu trúc của lớp 2 (luồng cong theo địa hình).
2. **Vai trò.** Mỗi cluster có CH; các critical cell là cell của CH, cộng các cell có CL vượt trội toàn cục hoặc cục bộ (River, Thuật toán 3).
3. **Bộ manh mối (lớp 1).** BS soạn 12 ảnh: 2 mặt (24,9 kB), 4 dáng (49,9 kB), 6 bộ phận (24,9 kB), tổng 4 036 gói 99 B. Mỗi ảnh có độ nhận diện r (gần 1) và độ quan trọng w do BS chấm. Thứ tự phát xen kẽ khía cạnh.
4. **Đường bay và tour đội 1 (lớp 2).** Đường thẳng qua CH theo hướng dài nhất trong cluster. Thứ tự cluster theo **độ trễ có trọng số**: cực tiểu Σ_k n_k · (lúc rời cluster k), n_k là số critical cell. Held–Karp chính xác tới 12 cluster, quá thì heuristic (`tour_heur.py`).
5. **Lượt phát.** UAV phát bản sao bộ manh mối trên cửa sổ 400 kB các gói Axe quanh CH, lặp lại trước và sau cửa sổ. Mỗi critical cell tự giữ những manh mối mà node trong cell nghe đủ (ns‑3 pass).
6. **River cửa sổ (lớp 3).** River chỉ chuyển cửa sổ 400 kB quanh CH tới mọi critical cell (ns‑3, MAC 802.15.4, lưới 7 màu).
7. **Đối sánh và báo cáo hai lần.** Cell tính điểm hai bước (mục 2.4 của `paper/L1-MODEL-vi.md`) và báo hai lần qua CH và LoRa: ngay sau khi gom nội cell (phần tự nghe được), rồi sau River (đủ bộ). Mỗi báo cáo gồm điểm cao nhất và bitmap manh mối.
8. **BS.** Mỗi báo cáo thành một phân phối chuẩn của điểm xác minh; từ đó tính P(cell là c\*) cho mọi cell, kể cả cell chưa báo (tiên nghiệm) và cell đã xác minh.
9. **Đội 2 (pha 2).** Xuất phát ở báo cáo đầu tiên. Chọn cell đã biết có P / (bay + xác minh) lớn nhất, như quy tắc cũ. Chỉ bay đi xác minh khi P của cell đó ≥ P_U, xác suất c\* nằm trong số cell chưa báo; nếu không thì **đón đầu**: bay về tâm có trọng số P của các cell chưa thăm và chờ báo cáo kế tiếp. Thăm hết mọi cell; **pha 2 hoàn thành khi xác minh xong c\***.

### 2.2 Bốn ý tưởng thêm sau vòng 1
- **Điểm hai bước theo khía cạnh** (lớp 1). Gộp một bước làm lệch tỉ trọng khi cell chỉ giữ một phần manh mối.
- **Báo cáo hai lần** (lớp 3 + phản hồi). Không hợp tác thì báo sớm nhưng kém chính xác; River thì chính xác nhưng muộn. Gửi cả hai lấy được cái lợi của cả hai, không tốn thêm khe LoRa: CH vốn phát mỗi khe 40 s, gom mọi kết quả mới.
- **Chờ P_U và đón đầu** (pha 2). Ở vòng 1, đội 2 đi ngay ở báo cáo đầu và xác minh trung bình 1,6–2,3 cell sai trước c\*. Mỗi lần sai tốn khoảng 78 s xác minh cộng thời gian bay.
- **Tour theo độ trễ** (lớp 2). c\* có thể là bất kỳ critical cell nào, nên điều cần cực tiểu là thời điểm *trung bình* các critical cell được bỏ lại, không phải thời điểm cluster cuối (l3first) hay tổng quãng bay (short).

### 2.3 Hình
- `figures/l1-model.png`: mô hình lớp 1 (mô tả trong `paper/L1-MODEL-vi.md` §4).
- `figures/l1-steps-<bản đồ>.png`: một nhiệm vụ qua các bước 1–9 (mục 5).
- `anim/l1-replay.html`: hình động cùng nhiệm vụ (mục 5).

__RESULTS__
