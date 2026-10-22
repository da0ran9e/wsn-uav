# Chốt propose lớp 2: các vòng thử ngày 2026-10-22

Lời gốc: CLAUDE.md §8 mục 133–136. Log: `logs/2026-10-22_1806-propose-iter/` (vòng 1–6 trên k8-s10 và hai bản đồ kiểm tra), `logs/2026-10-22_1947-swath-validate/` (16 bản đồ). Mã: `tools/swath.py`, `tools/swath_mission.py`, `tools/chord_tour.py`, `tools/mission.py --chordTour`, `tools/l2_metrics.py`, `tools/l2_compare_fig.py`.

## 1. Cách đo

- **16 bản đồ**, 4 mỗi cỡ (k2, k4, k6, k8), chọn ngẫu nhiên từ 40 bản đồ của chiến dịch (`random.Random(136)`): k2-s4, s9, s10, s23; k4-s2, s13, s20, s21; k6-s9, s11, s13, s20; k8-s1, s8, s10, s11.
- Mọi cách chia dùng **cùng P\***: báo hai lần, đội 2 cất cánh lúc 0, đón đầu, β = 1/4, đổi hướng giữa đường; River cửa sổ 400 kB theo từng critical cell; một lượt ns-3 mỗi cụm; 100 lượt bốc lớp 1 mỗi bản đồ.
- **Ghép cặp:** cùng bản đồ, cùng lượt bốc thì cùng kho ảnh và cùng nhiễu đối sánh ở mọi cách chia (thư mục làm việc phải mang đúng tên bản đồ, §2.1).
- Tour đội 1 có động học: nối Dubins bán kính 255 m; bay liền khi đường cụm sau nối tiếp đường cụm trước (`skin`). Với k-medoids lấy kiểu tour tốt hơn trong `kin` và `skin` cho từng bản đồ.
- 16 bản đồ vẫn là số thăm dò (dưới quy tắc N ≥ 120), dùng để chọn cấu hình, không đưa vào bài.

## 2. Các điểm chưa hợp lý tìm ra

### 2.1 Lỗi so sánh: không ghép cặp
`l1_rank.py` sinh kho ảnh của từng camera theo tên thư mục bản đồ. Các vòng 1–5 đặt tên thư mục khác nhau giữa các cách chia (`KD-k8-s10`, `SW-k8-s10`), nên hai cách chia nhận hai thế giới ngẫu nhiên khác nhau. Chênh lệch ở các vòng đó (ví dụ "SWATH nhanh hơn 98 s trên k6-s9") phần lớn là nhiễu. Chấm lại có ghép cặp: k4-s2 +34 s, k6-s9 −6 s, k8-s10 −13 s. Từ vòng 6 mọi so sánh đều ghép cặp.

### 2.2 Critical cell bị biên cụm cắt
Phép thử "vượt trội so với vùng quanh nó" chỉ xét cell trong cùng cụm, nên cụm mảnh có thêm critical cell (k8-s10: MEANDER-K 57 so với k-medoids 45). Sửa: xét cả cell của cụm bên cạnh (`--critRing domain`). Sau sửa: 49 so với 44.

### 2.3 Gói phát sát mép cụm không được tính
Axe chỉ gồm gói phát khi UAV ở đúng trên cell của cụm. Gói phát khi UAV ở cell kề (cách node 200–290 m, bán kính phủ A2G khoảng 990 m) bị bỏ. Sửa: gán cho cell gần nhất của cụm trong vòng 1 (`--axeNear`). Với ghép cặp, sửa này gần như không đổi T\* của k-medoids (535/536, 725/730, 810/805 s) nhưng giúp các cách chia có đường bay sát mép cụm.

## 3. Các phương án lớp 2 đã thử

| Phương án | Ý tưởng | Kết quả (16 bản đồ, ghép cặp, so với k-medoids) |
|---|---|---|
| MEANDER-K | MEANDER với đúng K cụm cỡ đều | thua trên k8-s10 (vòng 1), không chạy tiếp |
| SWATH-K | một đường luống liền, luồng thẳng 6 cell, K cụm là các đoạn liên tiếp | T\* +6 s (8/16); k2 +57 s, k6 −28 s; khung River +38 k |
| SWATH-K, luồng 7 / 8 | luồng rộng hơn | kém hơn luồng 6 (cụm thiếu bộ manh mối) |
| SWATH-L | SWATH-K, hướng luống chọn để các cell mạnh được bay qua sớm | T\* −4 s (10/16), p90 −47 s; k6 −33 s (4/4), k8 −44 s (4/4), k2 +56 s (0/4); khung River +94 k |
| **CHORD-T1** (60 % / 80 %) | giữ cụm k-medoids và đường thẳng qua CH, nhưng chọn hướng của mọi cụm cùng với thứ tự tour (§3.1) | **T\* −29 s (16/16)**, p90 −37 s; tour −64 s; khung River +105 k |
| CHORD-T2 (70 % / 90 %) | như trên, ràng buộc chặt hơn | T\* −14 s (13/16), p90 −24 s; tour −20 s; khung River +63 k |
| CHORD-T3 (60 % / 70 %) | như trên, ràng buộc lỏng hơn | T\* −38 s (16/16), p90 −50 s; tour −83 s; khung River +128 k |

### 3.1 CHORD-T

Với một UAV cánh bằng, đường thẳng dài nhất qua CH của mỗi cụm chĩa theo hướng tùy ý. Đội 1 vì thế tốn nhiều thời gian quay vòng Dubins giữa các cụm (k8-s10: 327 s nối và 143 s bay về trong tour 899 s). CHORD-T giữ nguyên cụm, CH và critical cell, chỉ đổi hướng đường bay:
1. Mỗi cụm có tối đa 6 hướng ứng viên qua CH (cách nhau ≥ 10°), mỗi hướng có đoạn trong cụm ≥ FRAC đoạn dài nhất và ≥ CLUE một bản bộ manh mối (2,02 km). Mỗi ứng viên được dựng thật bằng `uav-coop-deploy` (đường vào/ra Dubins phải khả thi).
2. BS chọn tổ hợp hướng và thứ tự bay cực tiểu Σ_k n_k · (lúc rời cụm k) (n_k: số critical cell, như tour độ trễ của P\*), nối Dubins, bằng Held–Karp chính xác trên (cụm, hướng, chiều bay) (`tools/chord_tour.py`).
3. Phần còn lại của nhiệm vụ giữ nguyên.

| CHORD-T1 trừ k-medoids | k2 | k4 | k6 | k8 | cả 16 |
|---|---|---|---|---|---|
| ΔT\* (bản đồ tốt hơn) | −12 s (4/4) | −24 s (4/4) | −36 s (4/4) | −43 s (4/4) | −29 s (16/16) |
| ΔT\* p90 | −13 s | −39 s | −68 s | −28 s | −37 s |
| Δ tour đội 1 | −38 s | −48 s | −88 s | −80 s | −64 s |
| Δ lúc TB critical cell có cửa sổ | −12 s | −29 s | −46 s | −54 s | −35 s |
| Δ lúc critical cell cuối có cửa sổ | −14 s | −63 s | −71 s | −97 s | −61 s |
| Δ khung River | +50 k | +177 k | +132 k | +61 k | +105 k |

- **Lợi tăng theo cỡ bản đồ**, vì có nhiều chỗ nối giữa các cụm hơn.
- **Đánh đổi:** đường ngắn hơn nên D giảm (3 850–4 500 gói so với 4 200–7 200). Chỉ 84 % critical cell giữ đủ 12 manh mối sau River, so với 100 % ở k-medoids; trọng số manh mối vẫn đạt 99,5 %. River phải kéo xa hơn: khung tăng, tương quan với D giảm (−0,66) và với critical cell xa đường bay hơn (+0,54).
- **Lớp 2 cần lớp 3.** Lợi của hợp tác (T\* không hợp tác trừ T\* của P\*): k-medoids +19 s, CHORD-T1 **+50 s**, CHORD-T2 +20 s. Không hợp tác thì CHORD-T1 gần như không hơn k-medoids (+2 s). BS được phép chọn đường bay ngắn và nối tour tốt hơn chính vì River lấp phần dữ liệu thiếu.

### 3.2 Núm điều chỉnh của CHORD-T

Ràng buộc có tác dụng là **CLUE**: đoạn trong cụm tối thiểu, tính theo phần của một bản bộ manh mối (2,02 km). FRAC không đổi gì: 50 % / 80 % cho đúng các hướng và kết quả của 60 % / 80 %.

| CLUE | ΔT\* (bản đồ tốt hơn) | ΔT\* p90 | Δ tour đội 1 | critical cell đủ 12 manh mối | trọng số manh mối | Δ khung River |
|---|---|---|---|---|---|---|
| k-medoids (đường dài nhất) | 0 | 0 | 0 | 100 % | 100 % | 0 |
| 90 % | −14 s (13/16) | −24 s | −20 s | 100 % | 100 % | +63 k |
| 80 % | −29 s (16/16) | −37 s | −64 s | 84 % | 99,5 % | +105 k |
| 70 % | −38 s (16/16) | −50 s | −83 s | 63 % | 97,8 % | +128 k |
| 60 % | −38 s (16/16) | −46 s | −84 s | 59 % | 97,3 % | +117 k |

Hình: `figures/chordT-tradeoff-16maps.png` (đánh đổi theo CLUE), `figures/l2-variants-16maps.png` (mọi phương án theo cỡ bản đồ), `figures/chordT-k6-s9-kmedoids-vs-chordT1.png` (đường bay).

## 4. Kết luận và đề xuất

1. **Lớp 2 đề xuất: CHORD-T.** Giữ cụm k-medoids và đường thẳng qua CH, nhưng BS chọn hướng đường bay của mọi cụm cùng với thứ tự tour. Trên 16 bản đồ ghép cặp nó nhanh hơn bản trước ở mọi bản đồ, và lợi tăng theo cỡ bản đồ. Nó không đổi cụm, nên công bằng về số cụm và cỡ cụm (mục 118) là hiển nhiên.
2. **Núm CLUE:** T\* bão hoà ở 70 % (−38 s); 60 % không nhanh hơn mà thiếu manh mối nhiều hơn. Đề xuất mặc định **CLUE = 80 %** (−29 s, 16/16; giữ 99,5 % trọng số manh mối, 84 % critical cell đủ 12 manh mối). Quy tắc chọn: CLUE nhỏ nhất mà vẫn giữ ≥ 99 % trọng số manh mối. 70 % để làm điểm "nhanh nhất" trong phần độ nhạy. Cần người dùng chốt.
3. **SWATH-K / SWATH-L** (đường luống liền) không hơn trung bình và kém rõ ở bản đồ nhỏ; giữ làm phương án lớp 2 thay thế trong phần thảo luận. MEANDER-K bỏ.
4. **Câu chuyện lớp 2 + lớp 3:** với CHORD-T, hợp tác mặt đất có giá trị gấp khoảng 2,6 lần (+50 s so với +19 s). Không hợp tác thì CHORD-T gần như không hơn k-medoids. Lớp 2 chỉ chọn được đường ngắn và nối tour tốt vì River lấp phần dữ liệu thiếu.
5. **Cái giá:** River tốn thêm khung (+105 k mỗi bản đồ ở CLUE 80 %), vì Axe ngắn hơn và critical cell xa đường bay hơn. Phải báo cáo cùng với T\*.
6. **Sửa mô hình giữ lại cho mọi phương án:** critical cell theo lân cận thật, Axe gồm gói sát mép cụm, cửa sổ theo critical cell, đổi hướng giữa đường.

**Cấu hình P\* đề xuất cho chiến dịch:** `mission.py --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8`; `l1_rank.py` phương án `P+prog-kin-puq-stage-zero-redir`.

**Việc tiếp theo (chờ duyệt):** chốt CLUE; chốt N; rồi chạy chiến dịch với các baseline: B1–B7 sẵn có, kéo thẳng (`Pd+prog`), không hợp tác (B4), k-medoids đường dài nhất (ablation lớp 2), SWATH-K, subCH-K, cánh bằng bay vòng (Python, chưa viết), B5 = SWATH luồng hẹp + không hợp tác, Trickle (ns-3, chưa viết).
