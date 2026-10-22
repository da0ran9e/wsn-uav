# 2026-10-22 · Chốt phiên bản propose: lặp cải tiến (CLAUDE.md §8 mục 135)

**Mục đích:** tìm điểm chưa hợp lý của propose trên một bản đồ ngẫu nhiên (k8-s10), cải tiến thực tế, lặp lại; chỉ ra ưu điểm của lớp 2 so với bản trước (k-medoids, đường thẳng qua CH). Chưa chạy chiến dịch.

**Chung:** P\* = báo hai lần, đội 2 cất cánh lúc 0, đón đầu, β = 1/4, đổi hướng giữa đường; River cửa sổ 400 kB theo từng critical cell; 100 lượt bốc mỗi bản đồ; một lượt ns-3 mỗi cụm. Thư mục làm việc trong scratchpad `IT/` (không commit).

| Vòng | Thay đổi | Kết quả chính (T\* P\*) | Log |
|---|---|---|---|
| 1 | k-medoids vs MEANDER-K | 812 vs 857 s (nối Dubins); MEANDER-K có 57 critical cell so với 45, bay trong cụm 27,3 km so với 21,4 km | `r1-*.md` |
| 2 | SWATH-K (`tools/swath.py`, `swath_mission.py`): luồng thẳng 6 cell, chuỗi luống cắt đúng K cụm, CH trong dải dưới đường bay (`coop-deploy --chCells`), tour `skin`; critical cell xét lân cận thật (`--critRing domain`) | 789 vs **744 s**; p90 1 263 vs 1 125 s | `r2-*.md` |
| 3 | SWATH-K luồng 7, 8 cell | 751, 859 s: cụm có Axe ngắn hơn bộ manh mối, giữ luồng 6 | `r3-*.md` |
| 4 | kiểm tra chéo k4-s2, k6-s9 | k4: 537 vs 573 s; k6: 755 vs 723 s. Nhiều cụm SWATH có ít hơn 4 041 gói phát ngay trên cell của mình | `r4-*.md`, `check.sh` |
| 5 | Axe gồm cả gói phát sát mép cụm (`--axeNear`: cell gần nhất trong vòng 1), cả hai cách chia | k4: 572 vs **538**; k6: 745 vs **647**; k8: **704** vs 783 s. Mọi critical cell đủ 12 manh mối ở k4, k6 | `r5-*.md`, `near.sh` |

**Kết quả vòng 5 (cấu hình hiện tại), k-medoids / SWATH-K:**
- T\*: k4-s2 572 / 538, k6-s9 745 / 647, k8-s10 704 / 783 s (k-medoids lấy kiểu tour tốt hơn trong `kin`, `skin`).
- Tour đội 1: 452 / 431, 709 / 600, 808–866 / 774 s.
- Khung River: 114k / 143k, 132k / 233k, 159k / 187k.
- Trên một bản đồ, chỉ đổi kiểu nối tour đã làm T\* k-medoids dao động 704–741 s: nhiễu một bản đồ cỡ ±40 s.

**Dang dở:** chưa đủ bản đồ để kết luận lớp 2; chờ người dùng chọn hướng.

## Vòng 6: chấm lại có ghép cặp (quan trọng)

`l1_rank.py` sinh kho ảnh và nhiễu đối sánh của từng camera theo **tên thư mục bản đồ** (`mapname`). Các vòng 1–5 đặt tên `KD-k8-s10`, `SW-k8-s10`… nên hai cách chia nhận hai "thế giới" khác nhau (c\* khác, kho ảnh khác): so sánh **không ghép cặp**. Chấm lại với liên kết `PR/KD/<bản đồ>`, `PR/SW/<bản đồ>` (log `r6-paired.md`):

| Bản đồ | k-medoids | SWATH-K | Chênh |
|---|---|---|---|
| k4-s2 | 535 | 569 | +34 |
| k6-s9 | 725 | 719 | −6 |
| k8-s10 | 810 | 797 | −13 |

Chênh lệch ở vòng 2–5 phần lớn là nhiễu do không ghép cặp; `--axeNear` gần như không đổi T\* của k-medoids (535 so với 536, 725 so với 730, 810 so với 805). Từ đây mọi so sánh dùng tên thư mục là tên bản đồ.

Chỉ số giao dữ liệu (`tools/l2_metrics.py`, k-medoids / SWATH-K): pha 1 xong (critical cell cuối có cửa sổ) 403 / 395, 614 / 514, 728 / 668 s; lúc TB critical cell sẵn sàng 227 / 258, 343 / 311, 360 / 361 s; tour đội 1 452 / 431, 709 / 600, 808 / 774 s.
