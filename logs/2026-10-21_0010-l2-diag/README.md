# 2026-10-21 · Chẩn đoán lớp 2: vì sao MEANDER chưa thắng (CLAUDE.md §8 mục 115)

**Mục đích:** xem lại bốn yếu tố người dùng nêu (số cluster, đường bay, lượng dữ liệu thu được, độ thấm dữ liệu) trên các lần chạy ns‑3 đã có của vòng 2, rồi đề xuất kế hoạch trước khi chạy gì tốn thời gian.

**Lệnh (chạy từ `uav-l2/`, log ghi bằng `tools/runlog.py`):**
- `diag.md`: `tools/l2_diag.py` trên KW (k‑medoids), MW (MEANDER), SW (subCH), 40 bản đồ mỗi bộ, từ thư mục nhiệm vụ đã chạy. Không chạy ns‑3 mới.
- `lanes.md`: `tools/l2_lanes.py`, chỉ hình học. Trên cùng 40 bản đồ, so MEANDER với độ rộng luồng 4,5 / 6 / 7,5 / 9 / 12 cell và k‑medoids (`meander.run`, `meander.summarise`).
- `lanes-fig.md`: vẽ lại `figures/l2-lanes.png` từ `lanes.csv`.

**Đầu vào:** scratchpad `KW`, `MW`, `SW` (chiến dịch `logs/2026-10-20_1846-campaign2/`).

**Đầu ra:** `uav-l2/docs/data/l2diag/{diag-maps,lanes}.csv`; hình `uav-l2/docs/figures/l2-{diag,diag-k6-s4,lanes}.png`; báo cáo `uav-l2/docs/L2-DIAG-vi.md`.

**Kết quả chính:**
- Tour đội 1: k‑medoids 213 / 369 / 512 / 682 s, MEANDER 285 / 529 / 738 / 950 s. Chênh lệch chủ yếu do bay trong cluster (+50 %), vì luồng phủ kín miền. Độ phủ dải River: MEANDER 76–82 %, k‑medoids 54 %.
- MEANDER có nhiều hơn 50–65 % cluster và thêm 3–9 critical cell mỗi bản đồ.
- Ở cùng độ phủ (luồng 12 cell), MEANDER vẫn bay dài hơn (k8: 34,3 so với 27,5 km) vì bay nối và đường vào/ra của nhiều cluster vụn.
- Độ thấm: gói thô thấm gần hết ở mọi cách chia. MEANDER gấp đôi số cell tự giữ đủ 12 manh mối (17–28 % so với 10–14 %), nhưng trọng số manh mối trung bình như nhau (khoảng 77 %).

**Dang dở:** chưa thử phương án luống đúng nghĩa (một đường bay liền qua hồ, cluster là các đoạn trên đường bay). Cần bàn với người dùng trước khi cài và chạy ns‑3.
