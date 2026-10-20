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

## 3. Vòng 1: mô hình lớp 1 trong nhiệm vụ cũ (`data/l1rank/r1-*.csv`)

Chạy trên dữ liệu ns‑3 có sẵn, 100 lượt bốc mỗi bản đồ. Ở vòng này điểm còn gộp một bước, và đội 2 theo quy tắc cũ: đi ở báo cáo đầu, chọn theo P / thời gian, tour l3first.

**39 bản đồ cluster có sẵn**, T\* trung bình (s), k2 / k4 / k6 / k8:

| Phương án | T\* | Chênh so với P |
|---|---|---|
| P (River, đi sớm) | 515 / 711 / 792 / 871 | |
| Không hợp tác (B4) | 537 / 752 / 902 / 936 | +22 / +42 / +110 / +64 |
| P, chờ đủ báo cáo | 591 / 825 / 1 003 / 1 196 | +75 / +115 / +210 / +324 |
| P, trọng số đều (bỏ độ quan trọng) | 820 / 1 343 / 1 818 / 2 235 | +304 / +632 / +1 025 / +1 364 |
| P, xếp nhóm thay xen kẽ | 513 / 708 / 787 / 872 | −2 / −3 / −5 / +1 |
| B4, xếp nhóm thay xen kẽ | 626 / 960 / 1 211 / 1 323 | +110 / +249 / +418 / +451 |
| B1 (không pha 1) | 912 / 1 699 / 2 498 / 3 083 | |
| B7 (cận dưới lý tưởng) | 244 / 287 / 314 / 347 | |

**Ba bản đồ chung, mọi cách chia lớp 2** (k4‑s2 / k6‑s4 / k8‑s4, River cửa sổ):

| Cách chia | T\* của P (s) | Tour đội 1 (s) | Critical cell giữ đủ 12 manh mối sau River |
|---|---|---|---|
| k‑medoids (cluster có sẵn) | **653 / 807 / 740** | 327 / 560 / 680 | 60 % |
| k‑medoids + đường cong | 681 / 757 / 792 | 409 / 569 / 692 | 77 % |
| MEANDER | 704 / 923 / 951 | 483 / 770 / 929 | 69 % |
| LANE | 851 / 926 / 888 | 564 / 786 / 934 | 44 % |
| MEANDER, span 12 | 758 / 933 / 1 075 | 549 / 776 / 986 | 38 % |

**Rút ra từ vòng 1:**
- River có ích dưới mô hình mới: không hợp tác chậm hơn ở 33/39 bản đồ. River không làm báo cáo về sớm hơn (ngược lại, muộn hơn), nhưng làm thứ hạng đúng hơn.
- **Xen kẽ chỉ quan trọng khi không hợp tác.** Có River thì cell nhận trọn bộ, thứ tự không đổi gì.
- Bỏ độ quan trọng làm thứ hạng hỏng hẳn. Kết quả này một phần là do cách đặt mô hình: điểm xác minh được định nghĩa bằng chính các độ quan trọng đó.
- Tách thời gian ở k8: báo cáo của c\* về BS lúc trung bình 374 s, nhưng c\* xác minh xong lúc 871 s. Bay thẳng từ BS rồi xác minh chỉ mất 347 s (B7). Phần hở là đội 2 xác minh trung bình 2,3 cell sai trước c\*: đi ngay ở báo cáo đầu thì phải nhận các cell điểm thấp.
- Lớp 2: cluster có sẵn vẫn nhanh nhất trên cả 3 bản đồ, vì tour đội 1 ngắn hơn 150–250 s. MEANDER cho nhiều critical cell giữ đủ manh mối hơn (69 % so với 60 %), nhưng không bù được tour dài.

## 4. Vòng 1b: bốn ý tưởng (`data/l1rank/r1b-*.csv`, 39 bản đồ × 50 lượt, vẫn điểm một bước)

Chênh so với P vòng 1, k2 / k4 / k6 / k8 (số bản đồ tốt hơn P trên 39):

| Thêm vào P | Chênh (s) | Bản đồ tốt hơn |
|---|---|---|
| tour theo độ trễ | 0 / +6 / −22 / −27 | 9 |
| chờ P_U + đón đầu | −23 / −62 / −15 / +7 | 27 |
| báo cáo hai lần | −12 / −33 / −6 / −12 | 31 |
| cả ba | **−29 / −77 / −37 / −12** | **32** |

Ba ý tưởng cộng được với nhau. Ý thứ tư (điểm hai bước) sửa mô hình, nên dùng cho mọi vòng sau.

__ROUND2__

## 6. Độ nhạy theo tham số lớp 1 (`data/l1rank/sens-*.csv`, `figures/l1-sens.png`)

Cluster có sẵn, River đầy đủ D, 40 bản đồ × 50 lượt, mỗi lần đổi một tham số (cỡ bản đồ gộp chung). Chính sách đề xuất ở đây chưa gồm cất cánh từ t = 0.

| Thay đổi | Đề xuất (s) | Chỉ báo sau River (s) | Không hợp tác (s) | Đề xuất − không hợp tác | Bản đồ đề xuất tốt hơn | Hạng TB của c\* (đề xuất) |
|---|---|---|---|---|---|---|
| gốc (D = 128, 2 % mặc giống, M = 223) | 675 | 686 | 729 | −54 | 38/40 | 2,04 |
| D = 64 (đối sánh nhiễu hơn) | 832 | 841 | 935 | −104 | 37/40 | 2,84 |
| D = 256 (đối sánh sạch hơn) | 595 | 605 | 637 | −42 | 35/40 | 1,66 |
| không ai mặc giống | 679 | 689 | 743 | −64 | 38/40 | 2,05 |
| 5 % mặc giống | 662 | 671 | 720 | −58 | 38/40 | 1,98 |
| M = 105 | 658 | 668 | 714 | −56 | 36/40 | 1,90 |
| M = 693 | 682 | 692 | 753 | −70 | 37/40 | 2,08 |

- Kết luận chính (River tốt hơn không hợp tác) đứng vững ở mọi biến thể, 35–38/40 bản đồ.
- Ưu thế của River tăng khi đối sánh nhiễu (D = 64: −104 s): điểm càng kém tin cậy thì thiếu manh mối càng hại.
- **Số chiều hiệu dụng D quyết định mức T\*** (595–832 s). Đây là tham số cần neo vào số đo thật của mô hình embedding.
- Báo cáo hai lần luôn giúp khoảng 10 s.
- Hình `figures/l1-sens.png`: trái là T\* (trung bình ± khoảng tin cậy 95 % trên 40 bản đồ), phải là hạng TB của c\*. Mỗi cụm là một lần chạy, theo thứ tự bảng. Trong cụm: xanh đậm là đề xuất, xanh nhạt là chỉ báo sau River, vàng là không hợp tác.

__STEPS__
