# 2026-10-25 · CHORD trên bản đồ 8, 12, 16 cụm: animation (CLAUDE.md §8 mục 164)

**Mục đích:** chạy P\* (CHORD-T) trên ba bản đồ cỡ khác nhau và dựng trang replay từng bước để xem.

## Cấu hình chung
- P\* như chiến dịch:
  - `mission.py --windowKB 400 --windowAt crit --critRing domain --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env open --schemes rf`;
  - binary `scratchpad/CAMP-BIN3` (pass v3).
- Bản đồ seed 1, sinh như mọi chiến dịch trước:
  - k8: dùng lại `scratchpad/CTRY/P/k8-s1` của lượt thử mục 161;
  - k12 và k16: chạy mới (`P-k12-s1.md`, `P-k16-s1.md`).
  - Bản đồ k16 cho 15 cụm, vì mỗi cụm tối đa 80 cell.
- River chạy lại có `--trace` cho mọi cụm (`trace.sh`, `trace-*.md`). Cùng mission index, cùng kế hoạch và bitmap lượt bay, nên kết quả giống lượt chạy chính từng critical cell (35/35 cụm).
- `l1_anim.py` (đã sửa ở mục này) xuất dữ liệu animation và trang HTML:
  - đội 1 bay đúng quỹ đạo đã bay: nối Dubins và hồ sơ vận tốc theo `kin_time`;
  - thời điểm vào/rời cụm như `l1_rank -kt`;
  - cửa sổ theo từng critical cell;
  - 16 màu cụm.
  - Kiểm tra: T\* của animation ở k8-s1, lượt bốc 2, trùng với `l1_rank` (662 s, thăm thứ 3).
- Mỗi bản đồ chọn lượt bốc có T\* gần trung vị và c\* không phải lần thăm đầu: k8 lượt 2, k12 lượt 77, k16 lượt 52.

## Kết quả (100 lượt bốc lớp 1; `cmp-k*-out.md`, `l1rank/`)

| bản đồ | cụm | critical cell | tour 45° (s) | rời cụm TB (s) | River xong TB / p90 / max (s) | đủ 12 manh mối | T\* TB / trung vị (s) | T\* không hợp tác (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | 8 | 45 | 782 | 328 | 8 / 18 / 35 | 100 % | 762 / 643 | 781 |
| k12-s1 | 12 | 66 | 1 152 | 489 | 8 / 17 / 50 | 100 % | 939 / 864 | 985 |
| k16-s1 | 15 | 92 | 1 415 | 621 | 9 / 18 / 69 | 100 % | 1 127 / 1 084 | 1 214 |

**Bất thường ở k16-s1, cụm C6:**
- River dừng ở giới hạn 900 s: critical cell (21, −8) còn thiếu đúng 1 gói.
- Nguyên nhân không phải kênh: mọi gói cần đều có cell Axe giữ (`seg` 0 / 0).
- Ngoài 6 lượt r100 trước khi sửa (mục 163), đây là lượt River duy nhất không xong trong khoảng 1 230 lượt đã chạy từ 2026-10-22 (0,08 %).
- Cell đó vẫn đủ 12 manh mối nhờ phần tự nghe.
- Cần điều tra lỗi giao thức River ở ca này (khả năng là một gói rơi do MAC bỏ cuộc mà không được hỏi lại).

## Đầu ra
- `uav-l2/docs/anim/chord-k{8,12,16}-s1-replay.html` (0,7 / 1,0 / 1,5 MB) và `chord-k*-s1.json`.
- Khung chụp: `uav-l2/docs/figures/chord-anim-k*-s1-mission-frame.png`.
- Các trang chạy không lỗi trên Chromium headless.

## Dang dở
- Lỗi River ở k16-s1 C6.

## Bổ sung (mục 165): lỗi C6 có lặp lại không
`c6-other-seeds.md`: River của C6 (k16-s1) chạy lại với cùng bitmap lượt bay nhưng mission index khác (bốc G2G và MAC khác).
- Cùng index 1600106: lại kẹt y hệt (5/6, 900 s). ns-3 tất định nên lỗi tái tạo được.
- Index 2–6: xong cả 5 lần (6/6, 28–33 s).
- Kết luận: lỗi là một tổ hợp ngẫu nhiên hiếm, không phải do cấu trúc cụm.

**Phát hiện thêm trong chấm điểm:** `l1_rank.ready` và `mission_report` dùng thẳng `doneS`. Một critical cell không xong River có `doneS = −1`, nên bị coi là đã nhận đủ dữ liệu River lúc rời cụm − 1 s, tức lạc quan. Cần sửa trước chiến dịch.
