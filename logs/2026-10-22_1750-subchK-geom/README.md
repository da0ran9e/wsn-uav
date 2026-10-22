# 2026-10-22 · subCH-K: kiểm tra hình học trên 40 bản đồ (CLAUDE.md §8 mục 118, 134)

**Mục đích:** baseline subCH với đúng K cụm cỡ đều, để so công bằng với k-medoids.

**Mã:** `uav-l2/tools/mission.py --count K/2` (k-medoids đúng K/2 cụm, trần nâng lên ceil(cell / (K/2))); `--partition subch --pairs` (`uav-l2/tools/subch.py` `split2`: mỗi cụm tách đúng hai nửa liền mạch, cỡ bằng nhau, mọc từ hai critical cell xa nhau nhất); `--geometry` (dừng sau tour).

**Lệnh:** `job.sh` cho từng bản đồ: nguồn `HK/<bản đồ>` (log `<bản đồ>-half.md`), rồi `SKW/<bản đồ>` (log `<bản đồ>.md`). Thư mục làm việc trong scratchpad.

**Kết quả:** 40/40 thoát 0, đúng K cụm.
| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| hệ số biến thiên cỡ cụm, TB (lớn nhất) | 0,017 (0,061) | 0,046 (0,154) | 0,033 (0,067) | 0,034 (0,071) |
| tour đội 1 (s) | 216 | 358 | 495 | 685 |
Tour k-medoids cùng bản đồ: 213 / 369 / 512 / 682 s (`uav-l2/docs/L2-DIAG-vi.md` §2).

**Dang dở:** lượt bay và River (chờ duyệt chiến dịch).
