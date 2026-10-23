# Hình CHORD-T, CLUE 80 % (CLAUDE.md §8 mục 138)

**Mục đích:** người dùng chốt CLUE 80 % và muốn xem hình trước khi chạy tiếp. Không chạy ns-3 mới; dùng lại các thư mục ghép cặp `VB/kmedoids/<map>`, `VB/chordT1/<map>` trong scratchpad (log `2026-10-22_1947-swath-validate/`).

**Lệnh:** `tours-<map>.md` (đường bay, `iter_fig.py`), `vs-kmedoids.md` (`l2_compare_fig.py`), `coop-gain.md` (`coop_gain_fig.py`, mới).

**Sửa mã:**
- `dubins.py`: thêm `path()`, vẽ đúng đường ngắn nhất trong cả sáu từ Dubins. `path_csc` chỉ có bốn từ CSC: trên các bản đồ này nó vẽ hai đoạn nối dài hơn thật 470–890 m (từ CCC). Đã kiểm trên 5000 ca: điểm cuối lệch dưới 1e-9 m, chiều dài trùng `length()`.
- `iter_fig.py`: với tour `kin` / `skin`, vẽ các đoạn nối bằng `path()` (từ BS và về BS: hướng tự do tốt nhất trong 72 hướng); các panel chung một tỉ lệ.

**Đầu ra:** `uav-l2/docs/figures/chordT80-*.png` (6 hình, ghi trong `INDEX.md`).

**Số đọc từ hình (16 bản đồ, CHORD-T 80 % trừ k-medoids):**

| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| ΔT\* | −12 s | −24 s | −36 s | −43 s |
| Δ lúc TB critical cell có cửa sổ | −12 s | −29 s | −46 s | −54 s |
| Δ tour đội 1 | −38 s | −48 s | −88 s | −80 s |
| lợi hợp tác, k-medoids → CHORD-T | 12 → 21 s | 20 → 74 s | 13 → 66 s | 31 → 39 s |

**Ca lạ k8-s10:** hợp tác chậm hơn không hợp tác (CHORD-T −47 ± 27 s, k-medoids −19 ± 20 s), nhưng p90 tốt hơn (1236 so với 1465 s). Lần theo lượt bốc 56 (`scratchpad/diag/draw_trace.py`): c\* có U = 0,511; báo cáo trực tiếp (63 % trọng số manh mối) xếp nó thứ 1–3. Báo cáo River đủ 12 manh mối cho điểm thấp hơn, nên P(c\*) tụt còn 0,002–0,018 và nó bị thăm thứ 14. Đây là nhiễu đối sánh của lớp 1 trên vài lượt bốc, không phải lỗi cơ chế; 15/16 bản đồ còn lại hợp tác có lợi.
