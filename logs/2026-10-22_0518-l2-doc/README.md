# 2026-10-22 · Tài liệu nhanh lớp 2: phân vùng MEANDER (CLAUDE.md §8 mục 123)

**Mục đích:** một bản giống tài liệu lớp 3 (`paper/RIVER-L3-vi.md`), nhưng cho lớp 2 và ở mức mô tả nhanh: cơ chế phân vùng đề xuất (MEANDER), từng bước với mã giả ngắn và đầy đủ, hình từng bước, kết quả và tình trạng.

**Đầu ra:**
- `paper/L2-PARTITION-vi.md`: 9 mục, 10 hình.
- Trang web: https://claude.ai/artifact/4RMXn44sBxd4YLig4NBhqb (riêng tư cho tới khi được chia sẻ).
- Bốn hình cặp mới, không chữ: `uav-l2/docs/figures/meander-k6-s3-b220-w1-step-{12,34,56,78}.png`. Mỗi hình là hai ô liền nhau của hình 8 bước có sẵn (`…-steps.png`), lưu riêng để đọc được trên trang.

**Mã sửa:**
- `uav-l2/tools/meander.py`:
  - `--split`: lưu thêm các cặp bước;
  - `--frag`: ngưỡng mảnh vụn;
  - tên file có hậu tố `-L…f…` khi L hoặc frag khác mặc định, để không ghi đè hình gốc.
  - Hình 8 bước và hình so sánh dựng lại giống từng byte với bản đã commit.
- `paper/overview-page/build.py`: thêm `--doc l2`. Bản tổng quan và bản lớp 3 dựng lại giống từng byte (`build-overview-check.md`; bản lớp 3 kiểm bằng `cmp` trong lúc làm).

**Lệnh:**
- `meander-steps.md`: `tools/meander.py --clusters 6 --seed 3 --bend 220 --figs docs/figures --split`, chạy trong vài giây, chỉ tính hình học.
- `build-page.md`, `build-overview-check.md`: dựng trang.
- Thử một lần với `--lane 7.5 --frag 0.5` vào scratchpad. Đường bay của cụm luồng rộng trên miền này rối hơn, nên tài liệu minh hoạ bằng tham số gốc 4,5 và ghi rõ tham số đã chỉnh.

**Số trên bản đồ ví dụ** (miền cong 220°, cỡ 6 cluster, luồng 4,5):

| Cách chia | Cluster | Phủ River | Bay trong cluster | Bay chuyển tiếp |
|---|---|---|---|---|
| k‑medoids | 7 | 57,4 % | 14,9 km | 6,9 km |
| LANE | 9 | 79,6 % | 17,9 km | 15,0 km |
| MEANDER | 9 | 88,5 % | 24,5 km | 9,7 km |

Mọi số khác trong tài liệu lấy từ `uav-l2/docs/CURVE-vi.md`, `L2-DIAG-vi.md`, `SAT-vi.md` và `RESTRUCTURE-vi.md`; không chạy ns‑3 mới.

**Dang dở** (chờ duyệt từ trước): MEANDER‑K và chạy lại nhiệm vụ trên 40 bản đồ với cửa sổ theo từng critical cell.
