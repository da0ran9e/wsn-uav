# 2026-10-27 · LM-Tour xem lại: DTSP-N qua các CH rồi uốn về landmark (CLAUDE.md §8 mục 187)

**Câu hỏi:** LM-Tour dựng đúng dòng 6–14 của Algorithm 3 (DTSP-N qua các đĩa B(CH, ξ), rồi uốn tham lam về các critical cell trọng số cao tới khi J_k thôi giảm) có nhanh hơn CHORD thông thường rõ không?

## Thiết lập
- Bản đồ k8-s1, bốn kênh. Cụm, CH và critical cell giống hệt `logs/2026-10-27_1330-chord-plain-vs-lm/` (thư mục `CP`).
- **Mức mô hình:** T\* dùng River dự đoán (`lm_tour.py score --mode pred`), 100 lượt bốc ghép cặp. Chưa chạy pass và River trên ns-3.
- Các phương án:

| tên | thư mục | đường bay |
|---|---|---|
| CHORD | `runs/CP` | dây cung dài nhất qua CH, chọn riêng từng cụm |
| LM-Tour cũ | `runs/LM` | uốn từ dây cung của CHORD (mục 186) |
| DTSP-N qua CH, không uốn | `runs/LMD0` | `--dtspn --weight cl --wmin 99` |
| **LM-Tour mới** | `runs/LMD` | `--dtspn --weight cl --wmin 1`: DTSP-N rồi uốn về các cell có trọng số ≥ trung bình |

- DTSP-N: mỗi cụm một đường thẳng qua CH, thử 6 hướng (mỗi 30°), không ràng buộc độ dài tối thiểu (đường ngắn thì `pass_speed.fit` cho bay chậm hoặc lượn). Hướng, chiều và thứ tự cụm được chọn cùng lúc bằng Held-Karp (`chord_tour.choose`) để tối thiểu Σ W_k·leave_k.
- Uốn: ứng viên là critical cell cách đường > ξ (ξ auto: 255 / 255 / 199 / 99 m), CH được ghim, đường phải cắt qua cụm đúng một lần.
- Trọng số w_c là điểm CL của cell chia cho trung bình của bản đồ. Lưu ý: trong mô hình lớp 1, c\* không phụ thuộc điểm CL.

## Kết quả (T\* trung bình, s; chênh ghép cặp ± nửa khoảng tin cậy 95 %, ngoặc là % lượt bốc phương án đầu nhanh hơn)

| kênh | CHORD | LM-Tour cũ | DTSP-N không uốn | LM-Tour mới | LM mới − CHORD | DTSP-N − CHORD | phần do uốn | đội 1 CHORD / mới (s) |
|---|---|---|---|---|---|---|---|---|
| open | 672 | 672 | 652 | **633** | −38 ± 31 (76 %) | −19 ± 35 | −19 ± 26 | 784 / 698 |
| r500 | 816 | 812 | 734 | **723** | −93 ± 37 (83 %) | −82 ± 37 | −11 ± 14 | 784 / 699 |
| r200 | 897 | 887 | 830 | **808** | −89 ± 33 (87 %) | −66 ± 34 | −22 ± 8 | 784 / 697 |
| r100 | 917 | 913 | 835 | **827** | −90 ± 34 (87 %) | −83 ± 34 | −7 ± 7 | 784 / 708 |

- Với r200, trọng số đều (`--weight uniform --wmin 0`) cho 827 s.
- Số lần uốn trên 8 cụm: 9 / 10 / 11 / 9.

## Đọc kết quả
1. LM-Tour mới nhanh hơn CHORD thường 38–93 s (6–11 %) ở cả bốn kênh, và khoảng tin cậy không chứa 0.
2. Phần lớn lợi ích đến từ việc thay dây cung dài nhất bằng tour DTSP-N. Mỗi cụm chỉ cần 40,4 s bay trên cell của nó, nên bay chậm qua một đoạn ngắn tốn bằng bay nhanh qua một dây cung dài, nhưng tour giữa các cụm ngắn đi khoảng 43 s. Bước uốn đóng góp thêm 7–22 s. Ở đây uốn gần như không tốn thời gian, vì nó thay việc bay chậm bằng quãng đường bay.
3. Đây là số mức mô hình. Với CHORD, River dự đoán lệch ns-3 khoảng 0–25 s (pred 672 / 816 / 897 / 917 so với ns-3 672 / 802 / 877 / 892). Cần chạy ns-3 (bước D) để xác nhận. Các file mức mô hình nằm trong `model/`.

## ns-3 (bước D): LM-Tour và DTSP-N + River
- `run.sh ENV` dựng plan, chạy pass và River cho LM-Tour. Pass của DTSP-N + River bị `pass-bin` dừng vì đường bay không đi qua CH (coop-pass.cc: `CHECK dPath(CH) < 1 m`; ngoài ra CH không được pass dùng vào việc gì khác).
- `run-dr.sh ENV` xử lý phần đó bằng `prefly.py`: thêm một node chỉ nhận, đánh dấu là CH, đặt ở điểm của đường bay gần CH nhất; bay pass; rồi cắt dòng của node này khỏi bitmap. Sau đó chạy mission và chấm điểm như `run.sh`.
- Thứ tự hai lệnh: `bash run.sh ENV; bash run-dr.sh ENV`, rồi `python3 compare.py > table.md`.
- Mọi critical cell đều xong ở cả hai phương án và cả bốn kênh.

| kênh | CHORD | LM-Tour | DTSP-N + River | LM-Tour − CHORD | LM-Tour − DTSP-N + River | DTSP-N + River − CHORD | đội 1 CHORD / LM / DR (s) |
|---|---|---|---|---|---|---|---|
| open | 672 | **633** | 678 | −38 ± 31 (76 %) | −45 ± 28 (62 %) | +6 ± 21 (54 %) | 784 / 698 / 785 |
| r500 | 802 | **719** | 814 | −83 ± 38 (85 %) | −96 ± 41 (80 %) | +13 ± 36 (46 %) | 784 / 699 / 785 |
| r200 | 877 | **792** | 861 | −84 ± 35 (85 %) | −69 ± 47 (64 %) | −16 ± 50 (49 %) | 784 / 697 / 747 |
| r100 | 892 | **802** | 880 | −90 ± 38 (83 %) | −78 ± 39 (77 %) | −12 ± 40 (54 %) | 784 / 708 / 809 |

Đọc kết quả:
1. ns-3 xác nhận dự đoán: LM-Tour nhanh hơn CHORD thường 38–90 s (6–10 %), và khoảng tin cậy không chứa 0 ở cả bốn kênh.
2. DTSP-N + River hoà CHORD (−16 tới +13 s, nằm trong nhiễu). Đường zigzag qua mọi critical cell làm đội 1 bay lâu ngang CHORD (747–809 s), nên phần lợi River có được nhờ đi sát cell bị phần bay thêm ăn mất.
3. LM-Tour nhanh hơn DTSP-N + River 45–96 s. Hai phương án dùng cùng cách chọn tour; LM-Tour chỉ khác ở chỗ ghim CH và uốn có chọn lọc theo trọng số tới khi lợi ích bão hoà.
