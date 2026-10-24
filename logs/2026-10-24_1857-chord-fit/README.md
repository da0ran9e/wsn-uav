# 2026-10-24 · CHORD trên cluster có sẵn: đường vừa đủ, thiếu thì uốn hoặc giảm tốc, thứ tự theo River (CLAUDE.md §8 mục 159)

**Mục đích:** gác MEANDER, quay lại CHORD với cluster có sẵn (k-medoids, giới hạn 80 cell mỗi cụm) và CH chọn như ban đầu (node mạnh nhất cách biên ≥ 300 m, không đủ chỗ thì nới dần). Tối ưu ba điểm:

- đường bay qua CH chỉ dài vừa đủ;
- cụm thiếu thì uốn nhẹ về critical cell gần đó hoặc giảm tốc;
- thứ tự bay ưu tiên cụm có River dự kiến lâu ("cụm to, phức tạp trước").

**Mã:**

- `mission.py --chordFit F` (`fit_path`): mỗi hướng ứng viên được cắt còn đoạn ngắn nhất qua CH mà vẫn bay F bản tập manh mối (F × 2,02 km) trên cell của cụm. Nếu nhiều đoạn dài gần bằng nhau (lệch trong 20 m), lấy đoạn gần critical cell nhất. Phần còn thiếu (giây) được cộng vào thời gian của hướng đó khi chọn tour.
- `--bendShort` (cùng `--bendCrit 5`): chỉ cụm còn thiếu mới uốn về critical cell trong 5 cell.
- `--riverTour λ` (`chord_tour.choose`): mục tiêu chọn tour cộng thêm λ · Σn · max(thời điểm rời cụm + River dự kiến).
  - River dự kiến của một cụm = −12 + 0,101 · số cell + 5,7 · khoảng cách xa nhất (số cell) từ critical cell tới Axe.
  - Công thức khớp trên các lượt ns-3 cũ (`IT/K*`, `NS157/chordB`, `NS3/chord`): R² 0,41; River xong ≈ 10 s nếu critical cell cách Axe tối đa 4 cell, 20–34 s nếu cách 5–7 cell.
- Mọi lượt ns-3 đều dùng `--kinPass` (pass bay theo hồ sơ vận tốc, mục 157).

**Thiết kế so sánh** (k8 seed 1–3, mặc định 8–9 cụm):

- **A:** CHORD-T như trước.
- **B:** `--chordFit 1.0 --bendCrit 5 --bendShort --banks local`.
- **D:** B cộng `--riverTour 0.5`.
- Bản C (F = 1,3) gần như trùng B ở hình học nên không chạy ns-3.

**Lệnh:**

- `geo-*.md`, `geo-ABD.md`: hình học.
- `ns3-{A,B,D}-k8-s*.md`: ns-3.
- `l1rank-*.md` → `l1rank/`: T\*, 100 lần bốc mỗi bản đồ.
- `ns3-cmp-table.md`: bảng so sánh.
- `fig-s1.md` → `uav-l2/docs/figures/chordfit-k8-s1-chordT-fit-fitRiverOrder.png`.

**Kết quả ns-3:**

| bản đồ | thiết kế | tour 45° (s) | cụm phải giảm tốc | rời cụm TB (s) | River xong TB / p90 (s) | sẵn sàng TB (s) | đủ 12 manh mối | T\* TB (s) |
|---|---|---|---|---|---|---|---|---|
| s1 | A | 782 | 7/8 | 328 | 8 / 17 | 336 | 100 % | 762 |
| s1 | B | 712 | 5/8 | 320 | 9 / 25 | 329 | 100 % | 760 |
| s1 | D | 795 | 7/8 | 337 | 8 / 16 | 345 | 100 % | 784 |
| s2 | A | 718 | 7/8 | 330 | 7 / 16 | 337 | 100 % | 744 |
| s2 | B | 708 | 6/8 | 330 | 7 / 16 | 337 | 100 % | 745 |
| s2 | D | 780 | 6/8 | 331 | 8 / 18 | 339 | 100 % | 719 |
| s3 | A | 808 | 9/9 | 354 | 7 / 12 | 360 | 100 % | 770 |
| s3 | B | 823 | 8/9 | 363 | 6 / 14 | 369 | 100 % | 779 |
| s3 | D | 895 | 8/9 | 388 | 8 / 17 | 396 | 100 % | 781 |

T\* gộp 300 lần bốc: A 758, B 761, D 761 s (trung vị 680 / 695 / 660 s). Ba thiết kế gần như không khác nhau.

**Vì sao không cải thiện:**

1. **Không có gì để cắt "vừa đủ".** Cụm có sẵn khoảng 80 cell (đường kính khoảng 1,5 km), dây cung qua CH chỉ có 1,7–1,8 km trên cell của cụm, ngắn hơn mức cần 2,02 km. Gần như mọi cụm đều phải giảm tốc (tối thiểu 35–42 m/s), không cụm nào phải lượn.
2. **River đã rất nhanh** (6–9 s trung bình) vì cụm nhỏ, critical cell nằm gần Axe. Ưu tiên cụm "phức tạp" chỉ tác động vài giây, trong khi làm tour dài thêm 60–90 s (D).
3. **T\* bị chi phối bởi chỗ khác.**
   - Thời điểm rời cụm trung bình khoảng 330 s: một UAV phải ghé lần lượt 8–9 cụm, mỗi cụm tối thiểu 40 s phát.
   - Phần sau khi có báo cáo khoảng 420 s: đội 2 bay và xác minh (mỗi lần xác minh gồm tệp 1 MB và đối sánh).
   - Thay đổi lớp 2 chỉ làm thời điểm rời cụm trung bình dịch ±10 s.

**Ý nghĩa:** với cluster có sẵn kích thước đều nhau, CHORD-T hiện tại đã gần tối ưu theo T\*. B rút ngắn tổng quãng bay (s1 −70 s, s2 −10 s, s3 +15 s) mà T\* không đổi. Ý tưởng "cụm to/phức tạp trước" chỉ có tác dụng khi kích thước cụm chênh nhau nhiều.

**Dang dở:** chưa thử trên cluster có sẵn kích thước không đều; chưa thử đòn bẩy lớn hơn (nhiều UAV đội 1, rút ngắn khâu xác minh của đội 2).
