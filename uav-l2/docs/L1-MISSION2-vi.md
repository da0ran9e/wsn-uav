# Nhiệm vụ trọn vẹn với mô hình lớp 1 mới: đề xuất, ablation, baseline

Lời gốc: CLAUDE.md §8 mục 110–114. Mô hình lớp 1 (bản cho System Model): `paper/L1-MODEL-vi.md`.
Mã: `tools/l1_model.py` (mô hình điểm), `tools/l1_rank.py` (cả nhiệm vụ), `tools/l1_compare.py` (bảng, hình), `tools/subch.py` (baseline subCH), `tools/tour_heur.py` (tour khi có nhiều cluster), `tools/l1_anim.py` + `anim/l1-head.html`, `anim/l1-body.html` (hình động), `tools/l1_steps.py` (hình từng bước), `tools/l1_state.py` (trạng thái đội 2).
Log: `logs/2026-10-20_1834-l1-mission/`, `logs/2026-10-20_1846-campaign2/`.

## Tóm tắt

**Cấu hình cuối (P\*):**
- Cluster có sẵn (k‑medoids ≤ 80 cell), đường thẳng qua CH; tour đội 1 theo độ trễ có trọng số.
- Bộ 12 manh mối phát xen kẽ; River cửa sổ 400 kB.
- Mỗi critical cell báo hai lần qua CH và LoRa.
- Đội 2 cất cánh cùng đội 1, đón đầu, và đi xác minh khi P ≥ P_U/4.

**Kết quả** (40 bản đồ × 100 lượt, ghép cặp; số thăm dò vì chỉ có 10 bản đồ mỗi cỡ, dưới quy tắc N ≥ 120):

| Phương án | T\* k2 / k4 / k6 / k8 (s) | So với P\* |
|---|---|---|
| **P\*** | **408 / 566 / 675 / 769** | |
| không hợp tác (B4) | 434 / 622 / 734 / 838 | chậm hơn trên 39/40 bản đồ |
| P của vòng trước | 513 / 678 / 783 / 867 | chậm hơn trên 40/40 |
| cánh quay tốt nhất (B3‑500) | 783 / 1 267 / 1 795 / 2 123 | gấp 1,9–2,8 lần |
| không pha 1 (B1) | 897 / 1 699 / 2 498 / 3 083 | gấp 2,2–4,0 lần |
| cận dưới, biết trước c\* (B7) | 245 / 287 / 314 / 347 | |
| subCH (baseline lớp 2) | 423 / 617 / 717 / 830 | chậm hơn trên 32/40 |
| MEANDER (lớp 2 đề xuất) | 470 / 642 / 792 / 919 | chậm hơn trên 40/40 |

1. **Hợp tác (River) rút T\* 26–68 s nhờ xếp hạng đúng hơn, không phải nhờ báo sớm hơn.** Lợi lớn hơn khi đối sánh nhiễu: 92 s khi D = 64, 34 s khi D = 256.
2. **Đòn bẩy lớn nhất là pha 2:** đón đầu, cất cánh lúc 0, ngưỡng β = 1/4. 55–64 % T\* nằm sau lúc báo cáo của c\* về BS.
3. **Lớp 2:** cả hai cách tái cấu trúc (MEANDER, subCH) đều chậm hơn cluster có sẵn. Thêm cluster làm tour đội 1 dài hơn và tăng số critical cell. Cluster có sẵn hiện là lựa chọn tốt nhất.
4. **Hai ý tưởng thử sau vòng 2:**
   - Cận trên "đủ 12 manh mối" chỉ nhanh hơn 0–7 s, nên không đáng sửa Axe ngắn ở k‑medoids.
   - Đổi hướng giữa đường nhanh hơn 5–15 s, trên 36/40 bản đồ.
5. **Hướng tiếp (chưa cài):**
   - Xác minh hai bước.
   - Cell báo thêm độ tự tin.
   - Lớp 2 nhắm vào tour: ít cluster, Axe ≥ 2 km, đường bay liên tục.

## 1. Cách làm: ba vòng

| Vòng | Làm gì | Dữ liệu ns‑3 |
|---|---|---|
| 1 | Cài mô hình lớp 1 vào nhiệm vụ. So P cũ, không hợp tác, thứ tự phát, độ quan trọng, các baseline. | Có sẵn: 39 bản đồ cluster có sẵn (k‑medoids, River đầy đủ D); 3 bản đồ cho mọi cách chia lớp 2. |
| 1b | Thử bốn ý tưởng rút ra từ vòng 1 (mục 2.2), từng cái và tổ hợp. | Như vòng 1. |
| 2 | Chạy ns‑3 mới cho đủ 40 bản đồ: River cửa sổ cho cluster có sẵn, baseline subCH, MEANDER (lớp 2 đề xuất). Chọn ngưỡng chờ của đội 2, so mọi phương án với chính sách tốt nhất, thử thêm hai ý tưởng (mục 5.3–5.4). | 40 bản đồ × 3 cách chia. |
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
9. **Đội 2 (pha 2).** **Cất cánh cùng đội 1** (t = 0) và bay về tâm các critical cell trong lúc chưa có báo cáo nào. Khi đã có báo cáo, chọn cell đã biết có P / (bay + xác minh) lớn nhất, như quy tắc cũ. Chỉ bay đi xác minh khi P của cell đó ≥ β · P_U, với P_U là xác suất c\* nằm trong số cell chưa báo và **β = 1/4** (chọn ở mục 5.1). Nếu không thì **đón đầu**: bay về tâm có trọng số P của các cell chưa thăm và chờ báo cáo kế tiếp. Thăm hết mọi cell; **pha 2 hoàn thành khi xác minh xong c\***.

### 2.2 Bốn ý tưởng thêm sau vòng 1
- **Điểm hai bước theo khía cạnh** (lớp 1). Gộp một bước làm lệch tỉ trọng khi cell chỉ giữ một phần manh mối.
- **Báo cáo hai lần** (lớp 3 + phản hồi). Không hợp tác thì báo sớm nhưng kém chính xác; River thì chính xác nhưng muộn. Gửi cả hai lấy được cái lợi của cả hai, không tốn thêm khe LoRa: CH vốn phát mỗi khe 40 s, gom mọi kết quả mới.
- **Chờ P_U và đón đầu** (pha 2). Ở vòng 1, đội 2 đi ngay ở báo cáo đầu và xác minh trung bình 1,6–2,3 cell sai trước c\*. Mỗi lần sai tốn khoảng 78 s xác minh cộng thời gian bay.
- **Tour theo độ trễ** (lớp 2). c\* có thể là bất kỳ critical cell nào, nên điều cần cực tiểu là thời điểm *trung bình* các critical cell được bỏ lại, không phải thời điểm cluster cuối (l3first) hay tổng quãng bay (short).

### 2.3 Hình
- `figures/l1-model.png`: mô hình lớp 1 (mô tả trong `paper/L1-MODEL-vi.md` §4).
- `figures/l1-e1-abl-tstar.png`, `l1-e1-base-tstar.png`, `l1-e1-breakdown.png`: E1 (mục 5.2).
- `figures/l1-e2-tstar.png`, `l1-e2-breakdown.png`: E2, ba cách chia (mục 5.5).
- `figures/l1-sens.png`: độ nhạy (mục 6).
- `figures/l1-steps-k4-s2.png`, `l1-steps-mw-k4-s2.png`, `l1-steps-sw-k4-s2.png`: một nhiệm vụ qua các bước 1–9 (mục 7).
- `anim/l1-replay.html`: hình động của nhiệm vụ k‑medoids (mục 7).

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

## 5. Vòng 2: chiến dịch 40 bản đồ

Chiến dịch ns‑3 mới (`logs/2026-10-20_1846-campaign2/`): River cửa sổ 400 kB cho cluster có sẵn (KW, 40 bản đồ), baseline subCH (SW, 40) và MEANDER (MW, 40). LANE bỏ khỏi chiến dịch để tiết kiệm khoảng 2,5 giờ máy, vì ở vòng 1 nó thua cả k‑medoids lẫn MEANDER.

### 5.1 Ngưỡng chờ của đội 2 (`data/l1rank/rule-*.csv`)

Trên ba bản đồ chung, quy tắc chờ P ≥ P_U (β = 1) làm MEANDER và LANE (nhiều cluster) chậm hơn cả đi ngay. Lý do: P_U là xác suất c\* nằm trong *toàn bộ* các cell chưa báo, mà khi còn nhiều cluster chưa bay thì P_U lớn, nên đội 2 đứng chờ quá lâu. Vì vậy tôi thử ngưỡng P ≥ β · P_U với β = 1, 1/2, 1/4, 0 (β = 0: đi ngay, vẫn đón đầu), và một quy tắc không tham số theo thời gian: P_U chỉ tính các cell sẽ báo về trong lúc đội 2 bận bay và xác minh cell này (BS biết lịch báo của từng cluster từ kế hoạch bay).

Chọn trên cả 40 bản đồ cluster có sẵn (River đầy đủ D, 50 lượt), không chọn trên 3 bản đồ, để tránh khớp quá. T\* trung bình (s):

| Quy tắc | k2 / k4 / k6 / k8 | Cả 40 | Chênh so với β = 1 | Bản đồ tốt hơn β = 1 |
|---|---|---|---|---|
| β = 1 (P ≥ P_U) | 422 / 583 / 748 / 826 | 645 | | |
| β = 1/2 | 415 / 568 / 720 / 789 | 623 | −22 | 38/40 |
| **β = 1/4** | **418 / 560 / 695 / 754** | **607** | **−38** | **35/40** |
| theo thời gian | 420 / 575 / 723 / 774 | 623 | −22 | 30/40 |
| β = 0 (đi ngay, đón đầu) | 424 / 598 / 727 / 789 | 634 | −11 | 21/40 |
| không hợp tác, β = 1/4 | 444 / 609 / 752 / 814 | 655 | +10 | 14/40 |

- **Chọn β = 1/4 cho P\*.** Nó tốt nhất ở mọi cỡ trừ k2, và lợi tăng theo cỡ bản đồ (k8: −72 s so với β = 1).
- Đường cong theo β có đáy: β = 0 làm đội 2 xác minh nhiều cell sai (c\* được xác minh đầu tiên chỉ ở 10–35 % lượt, so với 39–44 % ở β = 1/4); β = 1 làm đội 2 chờ quá lâu.
- Quy tắc theo thời gian không cần tham số và tốt hơn β = 1, nhưng thua β = 1/4 (623 so với 607 s). Tôi chưa tách được lý do.
- Phân rã T\* của P\*: báo cáo đầu tiên của c\* về BS lúc 147 / 223 / 280 / 345 s; phần còn lại, 271 / 337 / 416 / 410 s, là đội 2 bay và xác minh (gồm 1–1,5 cell sai trước c\*). **Phần sau báo cáo chiếm 54–65 % T\***, nên pha 2 vẫn là chỗ có nhiều dư địa nhất.

### 5.2 E1: cluster có sẵn, River cửa sổ (`data/l1rank/e1-*.csv`)

40 bản đồ × 100 lượt, ghép cặp. Cột cuối: số bản đồ (trên 40) mà biến thể nhanh hơn P\*.

| Phương án | T\* k2 / k4 / k6 / k8 (s) | Chênh so với P\* (s) | Bản đồ nhanh hơn P\* |
|---|---|---|---|
| **P\*** | **408 / 566 / 675 / 769** | | |
| *Pha 2* | | | |
| đi ở báo cáo đầu (không cất cánh lúc 0) | 482 / 624 / 716 / 796 | +74 / +58 / +41 / +27 | 0 |
| không đón đầu (chờ tại chỗ) | 503 / 680 / 802 / 905 | +95 / +114 / +127 / +136 | 0 |
| β = 0 (đi ngay) | 420 / 600 / 708 / 813 | +12 / +34 / +33 / +43 | 4 |
| β = 1/2 | 409 / 576 / 699 / 801 | +1 / +11 / +24 / +32 | 8 |
| β = 1 | 416 / 591 / 731 / 839 | +8 / +26 / +56 / +70 | 3 |
| ngưỡng theo thời gian | 414 / 583 / 702 / 788 | +6 / +17 / +27 / +19 | 4 |
| đội 2 cũ (đi ở báo cáo đầu, tham lam, không đón đầu) | 499 / 660 / 748 / 837 | +91 / +94 / +74 / +68 | 0 |
| *Phản hồi và hợp tác* | | | |
| chỉ báo sau River | 416 / 576 / 681 / 776 | +8 / +10 / +6 / +6 | 6 |
| **không hợp tác (B4)** | 434 / 622 / 734 / 838 | **+26 / +56 / +59 / +68** | **1** |
| *Tour đội 1 (lớp 2)* | | | |
| l3first | 408 / 568 / 695 / 796 | +0 / +2 / +20 / +27 | 5 |
| ngắn nhất | 430 / 588 / 701 / 794 | +22 / +22 / +26 / +24 | 4 |
| *Lớp 1* | | | |
| xếp nhóm thay xen kẽ | 410 / 570 / 675 / 766 | +2 / +4 / −0 / −4 | 20 |
| không hợp tác, xếp nhóm | 492 / 776 / 1 027 / 1 155 | +83 / +211 / +352 / +385 | 0 |
| trọng số đều | 730 / 1 239 / 1 837 / 2 358 | +322 / +674 / +1 162 / +1 588 | 0 |
| *Vòng trước* | | | |
| P cũ (River, báo một lần, l3first, đội 2 cũ) | 513 / 678 / 783 / 867 | +105 / +112 / +108 / +98 | 0 |
| P cũ, chờ đủ báo cáo | 578 / 814 / 993 / 1 189 | +170 / +248 / +318 / +420 | 0 |
| *Baseline* | | *Gấp P\** | |
| B1 (không pha 1, TSP, tệp lớn) | 897 / 1 699 / 2 498 / 3 083 | 2,2 / 3,0 / 3,7 / 4,0 | 0 |
| B2‑300 (không pha 1, multicast) | 1 064 / 2 008 / 2 922 / 3 518 | 2,6 / 3,5 / 4,3 / 4,6 | 0 |
| B2‑500 | 826 / 1 446 / 2 135 / 2 563 | 2,0 / 2,6 / 3,2 / 3,3 | 0 |
| B3‑300 (cánh quay multicast bộ manh mối) | 913 / 1 577 / 2 252 / 2 628 | 2,2 / 2,8 / 3,3 / 3,4 | 0 |
| B3‑500 | 783 / 1 267 / 1 795 / 2 123 | 1,9 / 2,2 / 2,7 / 2,8 | 0 |
| B6 (cánh quay unicast bộ manh mối) | 855 / 1 457 / 2 094 / 2 488 | 2,1 / 2,6 / 3,1 / 3,2 | 0 |
| B7 (cận dưới: biết trước c\*) | 245 / 287 / 314 / 347 | 0,6 / 0,5 / 0,5 / 0,5 | 40 |

Thêm (từ `data/l1rank/e1-all-table.csv`, `e1-cells.csv`):

| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| Hạng TB của c\* trong lượt thăm: P\* / không hợp tác | 1,93 / 2,11 | 2,21 / 2,53 | 2,37 / 2,67 | 2,33 / 2,65 |
| c\* được thăm đầu tiên: P\* / không hợp tác | 47 / 44 % | 40 / 39 % | 40 / 38 % | 45 / 42 % |
| T\* phân vị 90: P\* / không hợp tác (s) | 653 / 728 | 923 / 1 117 | 1 088 / 1 322 | 1 243 / 1 470 |
| Báo cáo đầu của c\* về BS (s), như nhau ở cả hai | 147 | 221 | 280 | 344 |

**Rút ra từ E1:**
1. **P\* nhanh hơn P cũ 98–112 s (11–20 %) trên cả 40/40 bản đồ.** Phần lớn đến từ pha 2: đón đầu (95–136 s), cất cánh lúc 0 (27–74 s) và ngưỡng β = 1/4 (8–70 s so với β = 1). Các phần này đo riêng từng cái; chúng không cộng thẳng được.
2. **Hợp tác (River) nhanh hơn không hợp tác 26–68 s, trên 39/40 bản đồ; ở phân vị 90 nhanh hơn 75–234 s.** Cơ chế là xếp hạng đúng hơn, không phải báo sớm hơn: báo cáo đầu của c\* về BS cùng lúc ở cả hai, nhưng với River c\* đứng hạng 1,93–2,37 thay vì 2,11–2,67, nên đội 2 xác minh ít cell sai hơn. Đây là số thăm dò (10 bản đồ mỗi cỡ, dưới N ≥ 120).
3. **Báo hai lần giúp ít: 6–10 s.** Báo cáo đầu về sớm hơn 6–16 s, nhưng phần sau báo cáo gần như không đổi.
4. **Tour theo độ trễ** tốt hơn l3first ở k6/k8 (20–27 s), ngang ở k2/k4, và tốt hơn tour ngắn nhất 22–26 s ở mọi cỡ.
5. **Lớp 1:** có River thì thứ tự phát không còn quan trọng (xếp nhóm ≈ xen kẽ, 20/40). Không hợp tác thì phát xen kẽ rất quan trọng: xếp nhóm làm chậm 58–317 s so với không hợp tác phát xen kẽ. Bỏ độ quan trọng làm thứ hạng hỏng hẳn (gấp 1,8–3,1 lần).
6. **Baseline:** cánh quay tốt nhất (B3‑500) chậm hơn P\* 1,9–2,8 lần, B1 chậm hơn 2,2–4,0 lần. Khoảng cách tăng theo cỡ bản đồ vì UAV cánh quay phải dừng ở từng nhóm critical cell.
7. **Còn cách cận dưới B7 163–423 s.** Phần lớn nằm sau lúc c\* báo về (261–426 s): bay tới c\*, xác minh, và trung bình 0,9–1,4 cell sai trước c\*.
8. **River cửa sổ chưa giao đủ ở mọi cluster.** Critical cell giữ 97 % trọng số manh mối sau River (77 % nếu chỉ tự nghe), nhưng chỉ 56 % giữ đủ cả 12 manh mối. Nguyên nhân: 90/200 cluster (45 %) có Axe ngắn hơn bộ manh mối (4 036 gói, tức khoảng 2 km bay). Trong các cluster đó không critical cell nào đủ 12; trong các cluster còn lại thì 100 % đủ.

Hình (không chữ):
- `figures/l1-e1-abl-tstar.png`: bốn nhóm k2, k4, k6, k8; mỗi chấm là trung bình ± khoảng tin cậy 95 % trên 10 bản đồ. Trái sang phải: P\* (xanh đậm), đi ở báo cáo đầu (xanh nhạt), chỉ báo sau River (xanh vừa), không hợp tác (vàng cam), tour l3first (xanh lá), tour ngắn nhất (xanh lá nhạt), β = 0 (tím), β = 1 (tím nhạt), không đón đầu (hồng), đội 2 cũ (đỏ), P cũ (xám).
- `figures/l1-e1-base-tstar.png`, trục log: P\* (xanh đậm), không hợp tác (vàng cam), B3‑300 (tím), B3‑500 (tím nhạt), B6 (hồng), B2‑300 (xám), B2‑500 (xám nhạt), B1 (đen), B7 (xanh lá).
- `figures/l1-e1-breakdown.png`: mỗi cột là T\*, phần nhạt là lúc báo cáo đầu của c\* về BS, phần đậm là phần còn lại tới khi xác minh xong c\*. Trong mỗi nhóm: P\*, chỉ báo sau River, không hợp tác, đội 2 cũ, P cũ (màu như hình đầu).

### 5.3 Thử một ý tưởng sau E1: có nên lo Axe ngắn? (`data/l1rank/allclues-*.csv`)

Phát hiện 8 gợi ý một sửa đổi ở ranh giới lớp 1 và lớp 2. Với cluster có Axe ngắn, BS có thể soạn bộ manh mối riêng (bỏ manh mối có giá trị trên mỗi gói thấp nhất cho vừa Axe), hoặc lớp 2 có thể dựng cluster có Axe ≥ 2 km. Trước khi làm, tôi đo cận trên của mọi sửa đổi kiểu này. Giả sử báo cáo sau River của *mọi* critical cell giữ đủ 12 manh mối, còn thời điểm River giữ nguyên. Chạy trên cùng 40 bản đồ × 100 lượt:

| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| P\* (s) | 408 | 566 | 675 | 769 |
| cận trên "đủ 12 manh mối" (s) | 408 | 566 | 671 | 763 |
| bản đồ nhanh hơn | 3/10 | 5/10 | 6/10 | 7/10 |

**Lợi tối đa chỉ 0–7 s.** Axe ngắn nhất vẫn có 3 268 gói (trung vị 3 861), nên manh mối bị cắt chỉ là 1–3 ảnh ở cuối thứ tự phát (dáng và bộ phận, không bao giờ là mặt). Critical cell ở các cluster này vẫn giữ trung bình 93 % trọng số (thấp nhất 83 %), và điểm hai bước chịu được phần thiếu đó. Kết luận: **độ đầy đủ không còn là nút thắt; chỗ đáng làm tiếp là pha 2** (mục 5.1 và điểm 7 của E1). Tôi không cài sửa đổi Axe ngắn.

### 5.4 Đội 2 đang làm gì khi c\* báo về? (`tools/l1_state.py`, `data/l1rank/state.csv`, `redir-*.csv`)

Mục 5.1 cho thấy phần lớn T\* nằm sau lúc báo cáo đầu của c\* về BS. Để biết phần đó đi đâu, tôi ghi lại trạng thái đội 2 ở đúng thời điểm ấy (P\*, 40 bản đồ × 100 lượt):

| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| đang chờ hoặc đón đầu | 67 % | 58 % | 61 % | 65 % |
| đang bay tới cell khác | 13 % | 21 % | 23 % | 22 % |
| đang xác minh cell khác | 20 % | 21 % | 16 % | 13 % |
| từ lúc c\* báo về tới lúc đội 2 hướng về c\* (TB) | 114 s | 166 s | 204 s | 217 s |
| số cell khác được xác minh sau lúc c\* báo về (TB) | 0,72 | 0,91 | 0,99 | 0,97 |

- Khoảng hai phần ba số lượt, khi c\* báo về thì đội 2 đang rảnh và đi ngay. Phần còn lại của những lượt "đang rảnh", và phần lớn độ trễ, là do **xếp hạng chưa chắc**: báo cáo đầu của c\* chưa đủ nổi trội, nên đội 2 xác minh cell khác trước.
- 13–23 % số lượt đội 2 đang bay dở tới cell khác. Trường hợp này đóng góp 22–71 s vào độ trễ trung bình.

Từ đó tôi thử cho UAV cánh quay **đổi hướng giữa đường**: khi có báo cáo mới lúc đang bay, đội 2 quyết định lại từ vị trí hiện tại (có thể giữ hay đổi đích; xác minh đang làm thì không bỏ dở):

| | k2 | k4 | k6 | k8 | Bản đồ nhanh hơn |
|---|---|---|---|---|---|
| P\* (s) | 408 | 566 | 675 | 769 | |
| P\* + đổi hướng (s) | 403 | 554 | 662 | 754 | 36/40 |
| không hợp tác (s) | 434 | 622 | 734 | 838 | |
| không hợp tác + đổi hướng (s) | 431 | 611 | 720 | 825 | |

**Đổi hướng giúp đều nhưng ít: 5–15 s, trên 36/40 bản đồ.** Nó cộng được với hợp tác, và khoảng cách giữa hai bên giữ nguyên (P\* + đổi hướng vẫn nhanh hơn không hợp tác + đổi hướng 28–71 s). Tôi giữ nó là một tùy chọn (`-redir`) và đưa vào E2. Không đổi định nghĩa P\* để E1 và E2 dùng chung một chuẩn.

**Hướng phát triển tiếp (chưa cài):** phần trễ lớn nhất còn lại là xếp hạng chưa chắc, chứ không phải đội 2 đã lỡ cam kết. Hai hướng khả dĩ:
- **Xác minh hai bước.** Đội 2 gửi trước một phần nhỏ của bộ tham chiếu đầy đủ, rồi bỏ dở nếu điểm thấp. Mỗi lần sai hiện tốn đủ 78 s.
- **Cell báo thêm độ tự tin**, ví dụ khoảng cách giữa điểm cao nhất và điểm thứ hai, để BS phân biệt cell nổi trội thật với cell may mắn.



### 5.5 E2: ba cách chia cluster (`data/l1rank/e2-*.csv`)

Cùng 40 bản đồ, cùng lượt bốc, ghép cặp với E1. Mỗi camera gắn theo cell, nên cell nào là critical cell ở cả hai cách chia thì giữ cùng kho ảnh và cùng điểm xác minh. c\* là critical cell có điểm xác minh cao nhất *của chính cách chia đó*; trung bình mỗi bản đồ có 29,1 critical cell chung giữa k‑medoids và subCH, 3,5 chỉ có ở k‑medoids, 1,3 chỉ có ở subCH.

T\* (s), k2 / k4 / k6 / k8, và số bản đồ (trên 40) mà cách chia đó nhanh hơn k‑medoids với cùng chính sách:

| Cách chia | P\* | Không hợp tác | P\* + đổi hướng | B1 | B7 | Bản đồ P\* nhanh hơn k‑medoids |
|---|---|---|---|---|---|---|
| **k‑medoids (cluster có sẵn, ablation)** | **408 / 566 / 675 / 769** | 434 / 622 / 734 / 838 | 403 / 554 / 662 / 754 | 897 / 1 699 / 2 498 / 3 083 | 245 / 287 / 314 / 347 | |
| subCH (baseline) | 423 / 617 / 717 / 830 | 447 / 659 / 783 / 875 | 411 / 599 / 704 / 813 | 838 / 1 641 / 2 342 / 2 866 | 243 / 289 / 312 / 346 | 8 |
| MEANDER (lớp 2 đề xuất) | 470 / 642 / 792 / 919 | 495 / 679 / 840 / 965 | 464 / 628 / 778 / 902 | 1 049 / 1 839 / 2 876 / 3 500 | 243 / 286 / 316 / 349 | 0 |

| | k‑medoids | subCH | MEANDER |
|---|---|---|---|
| số cluster TB (k2 / k4 / k6 / k8) | 2 / 4 / 6 / 8 | 2,7 / 6,4 / 8,3 / 11,5 | 3,3 / 6,2 / 9,0 / 12,1 |
| số critical cell TB | 13,5 / 26,9 / 39,9 / 50,1 | 12,2 / 25,0 / 37,4 / 46,7 | 16,5 / 30,6 / 47,3 / 59,0 |
| tour đội 1 (s) | 213 / 369 / 512 / 682 | 232 / 480 / 632 / 807 | 285 / 529 / 738 / 950 |
| báo cáo đầu của c\* về BS (s) | 147 / 221 / 280 / 344 | 155 / 240 / 302 / 366 | 178 / 285 / 366 / 459 |
| hạng TB của c\* | 1,93 / 2,21 / 2,37 / 2,33 | 1,98 / 2,46 / 2,48 / 2,55 | 2,19 / 2,43 / 2,55 / 2,58 |
| trọng số manh mối giữ sau River (đủ 12) | 97 % (56 %) | 84 % (20 %) | 91 % (64 %) |

**subCH (baseline mục 114) chậm hơn cluster có sẵn 15–61 s; nó chỉ nhanh hơn trên 8/40 bản đồ.** Hai nguyên nhân, đều thấy trong bảng:
1. **Nhiều cluster hơn:** tour đội 1 dài thêm 19–125 s, và báo cáo của c\* về muộn hơn 8–22 s.
2. **Cluster con có Axe ngắn hơn bộ manh mối:** sau River critical cell chỉ giữ 84 % trọng số (20 % đủ cả 12), so với 97 % (56 %) ở cluster có sẵn. Xếp hạng vì thế kém hơn (hạng của c\* 1,98–2,55 so với 1,93–2,37). Khác với k‑medoids (mục 5.3), ở đây phần bị cắt đủ lớn để gây hại.

Trong subCH, hợp tác vẫn giúp 24–66 s so với không hợp tác. B1 nhanh hơn một chút khi chia subCH, vì có ít critical cell hơn để thăm.

**MEANDER (lớp 2 đề xuất, mục 103–106) chậm hơn cluster có sẵn trên cả 40/40 bản đồ: trung bình 101 s (từ 9 đến 273 s tùy bản đồ; 62 / 76 / 117 / 150 s theo cỡ).** Nó cho nhiều critical cell giữ đủ 12 manh mối hơn (64 % so với 56 %), nhưng:
1. **Tour đội 1 dài hơn nhiều** (thêm 72–268 s). MEANDER chia miền thành nhiều cluster hơn (3,3–12,1), mỗi cluster một đường cong, và đội 1 phải nối các đường đó.
2. **Báo cáo của c\* về muộn hơn** 31–115 s, vì tour dài hơn nên cluster chứa c\* được bay muộn hơn.
3. **Nhiều critical cell hơn** (16,5–59,0 so với 13,5–50,1), nên c\* khó nổi bật hơn: hạng TB 2,19–2,58 so với 1,93–2,37.

Trong MEANDER, hợp tác vẫn giúp 25–48 s so với không hợp tác.

**Kết luận lớp 2.** Với một UAV cánh bằng bay lần lượt từng cluster, T\* bị chi phối bởi tour đội 1 và số critical cell. Hai cách tái cấu trúc đã thử đều làm xấu hai đại lượng này: MEANDER thêm cluster để bám địa hình, subCH thêm cluster để tách critical cell. Vì thế cluster có sẵn (k‑medoids, đường thẳng qua CH) vẫn nhanh nhất. Kết quả này khớp với vòng 1 trên 3 bản đồ. **Ý tưởng tiếp (chưa cài):** một thiết kế lớp 2 nhắm vào T\* cần ít cluster, mỗi Axe ≥ 2 km (đủ cho bộ manh mối) và một tour ngắn nối các Axe. Ví dụ, chọn một đường bay liên tục cho cả miền trước, rồi mới chia cluster dọc theo nó.

Hình (không chữ):
- `figures/l1-e2-tstar.png`: bốn nhóm k2, k4, k6, k8, mỗi chấm là trung bình ± khoảng tin cậy 95 % trên 10 bản đồ. Chấm tròn là P\*, vuông là không hợp tác, tam giác là B7. Màu: xanh dương là k‑medoids, tím là subCH, xanh lá là MEANDER (nhạt hơn cho không hợp tác).
- `figures/l1-e2-breakdown.png`: như `l1-e1-breakdown.png`. Trong mỗi nhóm, trái sang phải: P\* của k‑medoids, subCH, MEANDER; không hợp tác của ba cách chia (màu nhạt); B7 của ba cách chia.
- `figures/l1-steps-sw-k4-s2.png`: một nhiệm vụ subCH trên bản đồ k4‑s2 (mục 7).

## 6. Độ nhạy theo tham số lớp 1 (`data/l1rank/sens-*.csv`, `figures/l1-sens.png`)

Chạy lại ở cuối với P\* cuối cùng. Cluster có sẵn, River cửa sổ (như E1), 40 bản đồ × 50 lượt, mỗi lần đổi một tham số; cỡ bản đồ gộp chung. Lần chạy đầu lúc 19:16 dùng chính sách cũ hơn; kết luận không đổi.

| Thay đổi | P\* (s) | Chỉ báo sau River (s) | Không hợp tác (s) | P\* − không hợp tác | Bản đồ P\* nhanh hơn | Hạng TB của c\* (P\*) |
|---|---|---|---|---|---|---|
| gốc (D = 128, 2 % mặc giống, M = 223) | 605 | 613 | 654 | −50 | 38/40 | 2,21 |
| D = 64 (đối sánh nhiễu hơn) | 747 | 755 | 840 | −92 | 37/40 | 2,97 |
| D = 256 (đối sánh sạch hơn) | 536 | 546 | 570 | −34 | 34/40 | 1,86 |
| không ai mặc giống | 610 | 617 | 661 | −51 | 38/40 | 2,23 |
| 5 % mặc giống | 591 | 602 | 643 | −52 | 37/40 | 2,16 |
| M = 105 | 589 | 598 | 642 | −53 | 37/40 | 2,08 |
| M = 693 | 615 | 623 | 677 | −62 | 36/40 | 2,29 |

- Kết luận chính (hợp tác nhanh hơn không hợp tác) đứng vững ở mọi biến thể: 34–38/40 bản đồ.
- Ưu thế của hợp tác tăng khi đối sánh nhiễu (D = 64: −92 s) và giảm khi đối sánh sạch (D = 256: −34 s). Điểm càng kém tin cậy thì thiếu manh mối càng hại.
- **Số chiều hiệu dụng D quyết định mức T\*** (536–747 s). Đây là tham số cần neo vào số đo thật của mô hình embedding.
- Báo cáo hai lần luôn giúp 7–10 s.
- Hình `figures/l1-sens.png`: trái là T\* (trung bình ± khoảng tin cậy 95 % trên 40 bản đồ), phải là hạng TB của c\*. Mỗi cụm là một lần chạy, theo thứ tự bảng. Trong cụm: xanh đậm là P\*, xanh nhạt là chỉ báo sau River, vàng cam là không hợp tác.

## 7. Một nhiệm vụ từng bước (bản đồ k4‑s2, P\*)

Hình: `figures/l1-steps-k4-s2.png` (cluster có sẵn), `figures/l1-steps-mw-k4-s2.png` (MEANDER), `figures/l1-steps-sw-k4-s2.png` (subCH), cùng bản đồ. Hình động: `anim/l1-replay.html` (cluster có sẵn, cùng lượt bốc với hình tĩnh). Hình không có chữ. Mỗi hình gồm sáu bản đồ (đọc trái sang phải, trên xuống dưới) và một dòng thời gian:

1. **Cluster và đường bay.** Cluster tô màu nhạt, CH là ngôi sao, critical cell là vòng trắng, đường bay đen, tour đội 1 nét đứt. BS là ô vuông đen; thước dưới góc phải dài 1 km.
2. **Ngay sau lượt bay.** Mỗi cell tô theo phần cửa sổ manh mối của cluster mà node trong cell nghe được (đậm là nhiều). Quanh mỗi critical cell là vòng 12 manh mối theo thứ tự phát: đỏ là mặt, xanh là dáng, vàng là bộ phận; xám là manh mối chưa giữ được.
3. **Sau River.** Vòng manh mối vẽ lại; cell thuộc River tô xanh nhạt.
4. **Lớp 1.** Critical cell tô theo điểm xác minh U (nhạt đến đậm); c\* tô đỏ.
5. **BS biết gì lúc đội 2 cam kết lần đầu.** Đĩa vàng có diện tích theo P(c\*) của cell đã báo; vòng trắng là cell chưa báo.
6. **Pha 2.** Đường đội 2 tới lúc xác minh xong c\*: nét đứt là đón đầu, nét liền là bay đi xác minh. Cell đã xác minh tô xám, c\* tô đỏ.
7. **Dòng thời gian** (vạch lưới 60 s). Hàng trên cùng (xám) là đội 1, từ lúc cất cánh tới lúc về BS. Mỗi hàng tiếp theo là một cluster theo thứ tự tour: lượt bay (xanh đậm), River (xanh lá), báo cáo về BS (chấm mờ là báo phần tự nghe, chấm đậm là báo sau River, chấm đỏ to là c\*). Hàng dưới cùng là đội 2: đón đầu (xám đậm), bay (hồng), xác minh cell sai (đen), xác minh c\* (đỏ). Vạch đỏ đứt là T\*.

**Diễn biến, cluster có sẵn (lượt bốc 0):**
- Đội 1 bay bốn cluster theo tour độ trễ: C2 (rời cluster lúc 76 s), C4 (131 s), C3 (216 s), C1 (289 s), rồi về BS lúc 372 s.
- Sau lượt bay, mỗi critical cell tự giữ được 3–12 trong 12 manh mối. River xong 18–60 s sau khi đội 1 rời cluster. Sau River, mọi critical cell ở C2, C3, C4 giữ đủ 12 manh mối. Ở C1 chỉ giữ 10, vì Axe của C1 chỉ có 3 735 gói, ít hơn 4 036 gói của bộ manh mối, nên hai manh mối cuối không nằm trong cửa sổ.
- Đội 2 cất cánh lúc 0 s và đón đầu về tâm các critical cell. Lúc 96 s, báo cáo đầu tiên (C2) về BS. BS cho cell 237 của C2 xác suất 27 % là c\*; 20 cell chưa báo chia nhau 73 %. Vì 27 % ≥ 73 %/4, đội 2 đi xác minh cell 237.
- Cell 237 chỉ đứng thứ ba theo điểm xác minh. Lượt sai này tốn 104 s bay và 78 s xác minh.
- c\* là cell 336 ở C3. Cả hai báo cáo của nó (tự nghe và sau River) về BS trong cùng một bản tin LoRa lúc 264 s, vì ở cell này River xong chỉ 0,7 s sau lần gom nội cell, trước khe LoRa kế tiếp của CH. Khi đội 2 xác minh xong cell 237 (279 s), BS cho cell 336 xác suất 48 %.
- Đội 2 bay 202 s sang phía tây và xác minh xong c\* lúc **559 s** (lần thăm thứ 2). Bay thẳng từ BS tới c\* rồi xác minh (B7) chỉ mất khoảng 250 s.

**Diễn biến, MEANDER (lượt bốc 5, cùng bản đồ):** sáu cluster cong theo địa hình. Mọi critical cell ở bốn cluster lớn giữ đủ 12 manh mối sau River; hai cluster nhỏ nhất (C5, C6) chỉ giữ 7, vì Axe của chúng ngắn. Đội 2 đón đầu tới 118 s, đi xác minh cell 336 (thứ hai theo điểm, sai), rồi bay 196 s sang phía đông tới c\* (cell 92). T\* = **568 s**, cũng ở lần thăm thứ 2.

**Diễn biến, subCH (lượt bốc 0, cùng bản đồ; `figures/l1-steps-sw-k4-s2.png`):** bốn cluster bị cắt thành sáu cluster con quanh các critical cell xa nhau, nên đội 1 bay sáu đường và về BS lúc 424 s (k‑medoids: 372 s). Axe của mọi cluster con đều ngắn hơn bộ manh mối (D = 1 945–3 886 gói), nên sau River critical cell chỉ giữ 5–11 manh mối, không cell nào đủ 12. Ở lượt bốc này c\* vẫn là cell 336. Báo cáo của nó về BS sớm hơn (238 s so với 264 s), nhưng đội 2 vẫn cam kết đầu tiên vào cell 237 lúc 96 s, nên T\* = **560 s**, gần như bằng k‑medoids. Trên 40 bản đồ thì subCH chậm hơn (mục 5.5).

Cả ba lượt cho thấy cùng một kiểu tốn thời gian: lần cam kết đầu tiên rơi vào một cell điểm cao nhưng sai ở xa c\*. Phần lớn T\* nằm sau lúc báo cáo của c\* về BS (mục 5.1).
