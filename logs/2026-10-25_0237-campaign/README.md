# 2026-10-25 · Script chiến dịch số liệu cuối, bản CHORD-T (chat log mục 160–162)

**Mục đích:** chuẩn bị chiến dịch 120 bản đồ (k2, k4, k6, k8 × seed 1–30) cho hai bộ:
- `P`: P\*, cụm k-medoids, CHORD-T, cửa sổ River 400 kB, kèm kéo trực tiếp và Trickle;
- `K`: ablation lớp 2, đường dài nhất qua CH.

**Tệp:**
- `campaign.sh`: hàng đợi, hai job cùng lúc;
- `job.sh`: một (bộ, bản đồ), binary đóng băng `CAMP-BIN`;
- `score.sh`: chấm 100 lượt bốc lớp 1 bằng `l1_rank.py`.

**Kết quả:** **chưa chạy.**
- Không có `done.txt`. Mục 162 dừng lại ("chưa cần chạy bây giờ").
- Mục 163 chuyển sang các chế độ kênh (`2026-10-25_0330-env-modes`), rồi tới chiến dịch 4 (`2026-10-27_1714-campaign4`), là nơi thay thế script này.
- Lần chạy thử và việc đóng băng binary nằm ở `2026-10-25_0300-campaign`.

**Trạng thái:** lịch sử. Đường dẫn scratchpad trong script là của một phiên cũ, đã mất.
