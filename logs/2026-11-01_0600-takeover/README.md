# 2026-11-01 · River + takeover trên bảng sai số đường bay (CLAUDE.md §8 mục 259 và yêu cầu chạy lại bảng)

- **Mục đích:** thử cơ chế takeover (dấu ranh giới) bổ trợ River khi đường bay lệch do gió. Chạy lại bảng gió
  (σ 50 × 3 seed, 100 × 3, 200 × 1), dùng lại pass gió của `logs/2026-10-31_0000-wind`.
- **Binary:** `CAMP-BINT` = CAMP-BINW + river-bin có `--takeover` (commit 70ef55e). Tag `rfT` trong `mission.py`.
- **Lệnh:** `batch.sh` (mission `--schemes rfT` cho từng σ và seed, log `s*-R*-rfT.md`), `score.sh S R` (l1_rank 100
  lượt trên bản sao thư mục, file rfT đổi tên thành rf), `compare.py` → `compare.md`/`.csv`.
- **Kết quả** (chi tiết `paper/SIM-REPORT-2026-11-01-takeover-vi.md`):
  - mọi critical cell xong ở mọi ô, so với trước: σ100 106/135, σ200 3/45;
  - T\* sau − danh nghĩa (trung bình theo seed): σ100 +0,2 ± 121 s (trước +294 s); sẵn sàng (trung bình 8 cụm) 112–118 s; σ200 chỉ 1 seed, khám phá người giữ là oracle;
  - σ = 50 m: takeover không kích hoạt.
- **Chặn trên vòng báo cáo** (`report_bound.py` → `report-bound.md`, không chạy mô phỏng mới): σ100 có 2–10 cặp, ≤ 3 hop cell, ≤ 25 hop radio; trễ khoảng 0,1–0,34 s một chiều, ≤ 4,9 s nếu tuần tự hoá ×4; người giữ tự báo thì khoảng 540 báo cáo mỗi seed, kể cả σ = 50 m, nên phải để SPINE cell khởi xướng.
- **Takeover tuần tự** (`--takeoverSeq`, tag `rfS`; `batch2.sh`, `score2.sh`, `compare_seq.py` → `compare-seq.md`): hỏi sau khi sửa từ cell kề xong, câu hỏi lan 3 hop bằng frame thật; sẵn sàng 112–118 s, 135/135 cell xong, T\* −22 ± 184 s so với danh nghĩa (trong phạm vi nhiễu).
- **Dở dang:** σ = 200 m mới 1 seed; bản tin TAKEOVER chưa mô phỏng thành frame riêng; năng lượng rfT chưa tính.
