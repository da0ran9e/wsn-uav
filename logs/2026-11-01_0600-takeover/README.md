# 2026-11-01 · River + takeover trên bảng sai số đường bay (CLAUDE.md §8 mục 259 và yêu cầu chạy lại bảng)

- **Mục đích:** thử cơ chế takeover (dấu ranh giới) bổ trợ River khi đường bay lệch do gió. Chạy lại bảng gió
  (σ 50 × 3 seed, 100 × 3, 200 × 1), dùng lại pass gió của `logs/2026-10-31_0000-wind`.
- **Binary:** `CAMP-BINT` = CAMP-BINW + river-bin có `--takeover` (commit 70ef55e). Tag `rfT` trong `mission.py`.
- **Lệnh:** `batch.sh` (mission `--schemes rfT` cho từng σ và seed, log `s*-R*-rfT.md`), `score.sh S R` (l1_rank 100
  lượt trên bản sao thư mục, file rfT đổi tên thành rf), `compare.py` → `compare.md`/`.csv`.
- **Kết quả** (chi tiết `paper/SIM-REPORT-2026-11-01-takeover-vi.md`):
  - mọi critical cell xong ở mọi ô, so với trước: σ100 106/135, σ200 3/45;
  - T\* sau trừ danh nghĩa: σ100 +0,2 s (trước +294 s), σ200 −19 s (trước +2 684 s);
  - σ = 50 m: takeover không kích hoạt.
- **Dở dang:** σ = 200 m mới 1 seed; bản tin TAKEOVER chưa mô phỏng thành frame riêng; năng lượng rfT chưa tính.
