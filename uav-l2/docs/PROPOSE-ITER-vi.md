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
| CHORD-T | giữ cụm k-medoids và đường thẳng qua CH, nhưng chọn hướng của mọi cụm cùng với thứ tự tour | (đang chạy) |

## 4. Kết luận và đề xuất

(điền sau khi có CHORD-T)
