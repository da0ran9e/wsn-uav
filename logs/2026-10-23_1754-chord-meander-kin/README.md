# 2026-10-23 · CHORD-T và MEANDER tối ưu, động học và điều kiện giao đủ (CLAUDE.md §8 mục 144–145)

**Mục đích:** thử nhanh bằng Python trên k8-s1: MEANDER tự nhiên ở điểm tối ưu của `SAT-vi.md` (luồng 8 cell, cụm 110–190 cell, dài 2–3 km) để lấy số cụm, rồi so với CHORD-T cùng số cụm; thời gian tour đội 1 có hồ sơ tốc độ và điều kiện giao đủ một bản bộ manh mối mỗi cụm.

**Mã:** `uav-l2/tools/kin_time.py` (mới), `meander_mission.py --cap`, `iter_fig.py` (đọc được thư mục `--geometry`).

**Lệnh:** `meander-opt-k8-s1.md` (`--lane 8 --span 14 --cap 190 --geometry`), `kin-k8-s1.md`, `fig-k8-s1.md`.

**Kết quả:** MEANDER tự nhiên chia k8-s1 thành 8 cụm (cỡ 53–109 cell), bằng số cụm k-medoids, nên CHORD-T dùng lại `VB/chordT1/k8-s1`.

| Tour đội 1 (s) | 50 m/s đều | hồ sơ tốc độ, nghiêng 45° | + giao đủ | tổng | nghiêng 30° (tổng) |
|---|---|---|---|---|---|
| CHORD-T 80 % | 734 | 734 | +41 (8/8 cụm giảm tốc) | 776 | 830 |
| MEANDER tối ưu, đường gốc | 850 | 917 | 0 | 917 | 1 053 |
| MEANDER tối ưu, đường làm mịn | 843 | 844 | +6 (2 cụm) | 850 | 925 |
| k-medoids, đường dài nhất | 773 | 773 | +10 (4 cụm) | 783 | 850 |

Hồ sơ tốc độ: v ≤ 50 m/s, v ≤ √(g·tanφ/κ), |a| ≤ 2 m/s², giảm tốc xuống ≥ 25 m/s. Giao đủ: ≥ 40,4 s trên chính cell của cụm (4 041 khung × 10 ms). Đường MEANDER gốc có chỗ gấp (bán kính tới 88 m); làm mịn (1-2-1, đầu mút giữ nguyên) dịch đường ≤ 53 m, CH lệch ≤ 27 m.

**Dang dở:** mới một bản đồ; chưa chạy ns-3 River và T\* cho MEANDER tối ưu; đoạn nối Dubins vẫn dựng ở 255 m (nghiêng 45°).

**Lưu ý (mục 146):** MEANDER trong log này là bản hiểu sai (đường riêng từng cụm, thứ tự theo độ trễ). Bản đúng kiểu luống: `logs/2026-10-23_1837-meander-lane/`.
