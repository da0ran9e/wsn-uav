# 2026-10-20 · Chiến dịch ns‑3 vòng 2: 40 bản đồ × ba cách chia (CLAUDE.md §8 mục 114)

**Mục đích:** dữ liệu ns‑3 (lượt bay và River) cho vòng 2 của `logs/2026-10-20_1834-l1-mission/`, trên cùng 40 bản đồ (10 mỗi cỡ 2, 4, 6, 8 cluster):
- **KW:** cluster có sẵn (k‑medoids) với River cửa sổ 400 kB.
- **SW:** baseline subCH. Cluster có sẵn được cắt quanh các critical cell cách nhau ≥ 6 cell, mảnh dưới 20 cell được gộp lại, mỗi cluster con bay qua CH của nó.
- **MW:** MEANDER (lớp 2 đề xuất), cửa sổ 400 kB.

**Lệnh (chạy từ `uav-l2/`):**
- `campaign.sh`: hai job (bộ, bản đồ) song song, mỗi job hai tiến trình ns‑3. Mỗi job gọi `job.sh`, ghi log `<bộ>/<bản đồ>.md` qua `tools/runlog.py` và một dòng vào `done.txt`.
- **KF:** chỉ chạy mới k2‑s3; bản lưu cũ không có bitmap lượt bay.
- **KW:** chép thư mục KF, xoá kế hoạch và kết quả River, chạy lại với `--windowKB 400`; bitmap lượt bay dùng lại.
- **SW:** `mission.py --partition subch --src KF/<bản đồ>`.
- **MW:** `meander_mission.py --windowKB 400`.
- **LW (LANE):** bỏ lúc 19:12 để tiết kiệm khoảng 2,5 giờ máy, vì ở vòng 1 LANE thua cả k‑medoids lẫn MEANDER. Ba bản đồ LANE của vòng 1 vẫn còn qua liên kết.
- Ba bản đồ k4‑s2, k6‑s4, k8‑s4 của KW, SW và MW là liên kết tới các lần chạy cửa sổ trước đó (`MKw`, `MMw`), không chạy lại.

**Sự cố:**
- Lúc 19:12 tôi sửa `job.sh` (thêm dòng bỏ LW) khi hai job KW k4‑s12 và k4‑s13 đang chạy. Bash đọc script theo từng đoạn, nên hai job đó không ghi được dòng vào `done.txt`. Cả hai vẫn chạy xong với mã thoát 0 (log `KW/k4-s12.md`, `KW/k4-s13.md`), và kết quả đầy đủ (`l1_rank.complete`).
- Thư mục tên lúc đầu là `…_1934-…`, nhưng chiến dịch bắt đầu lúc 18:46 (KF k2‑s3). Đã đổi tên ở cuối và sửa đường dẫn trong `campaign.sh`, `job.sh`.

**Đầu vào:** bản đồ và cluster trong scratchpad `KF` (40 bản đồ); binary `scratchpad/BIN/river-bin` (bản dựng hiện hành, không dựng lại giữa chừng).

**Đầu ra:** scratchpad `KW`, `SW`, `MW`, mỗi bản đồ một thư mục (map, cluster, đường bay, bitmap lượt bay, kết quả River), khoảng 80–120 MB mỗi bộ, không commit. Log từng job: `KW/`, `SW/`, `MW/`.

**Kết quả chính:** chạy 18:46–23:45, toàn bộ mã thoát 0.

| Bộ | Job | Lượt River | Lượt còn critical cell chưa đủ | Thời gian mô phỏng River, TB / lớn nhất | Tổng thời gian job |
|---|---|---|---|---|---|
| KW | 37 | 182 | 0 | 33,1 / 172,2 s | 10 479 s |
| SW | 40 | 289 | 0 | 17,0 / 139,8 s | 13 264 s |
| MW | 37 | 278 | 0 | 28,8 / 128,1 s | 11 158 s |

Cộng với ba bản đồ liên kết, mỗi bộ đủ 40 bản đồ. Phân tích cấp nhiệm vụ: `uav-l2/docs/L1-MISSION2-vi.md` mục 5.

**Dang dở:** 10 bản đồ mỗi cỡ là dưới quy tắc N ≥ 120.
