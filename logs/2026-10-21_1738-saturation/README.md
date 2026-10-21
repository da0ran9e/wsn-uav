# 2026-10-21 · Ngưỡng bão hoà của cơ chế đề xuất theo hình dạng cụm (CLAUDE.md §8 mục 120)

**Mục đích:** tìm kích thước, bề ngang và chiều dài cụm mà ở đó River bắt đầu bão hoà, rồi tìm điểm tối ưu.

**Công cụ (mới):**
- `uav-l2/tools/sat_strip.py`: một cụm dạng dải, rộng W cell, dài L km, bay dọc trục qua CH. Chạy deploy, lượt phát và River qua pipeline của `mission.py`; `--summary` gom mỗi dải một dòng.
- River có thêm tuỳ chọn cửa sổ theo từng critical cell (`uav-coop2/tools/river_export.py --windowAt crit`). Mỗi critical cell chỉ cần bản sao bộ manh mối gần nó nhất dọc đường bay. Bản ghi `NEED` mới trong kế hoạch; `coop2-river.cc` dùng mặt nạ theo từng critical cell.
  - Không có `NEED` thì chương trình cho kết quả y hệt trước. Đã kiểm tra trên dải 6 × 2 km: tệp critical cell và tệp lượt chạy giống từng byte (trừ thời gian chạy thật).
  - Đã biên dịch lại `uav-coop2-river` (30 s).

**Lệnh:**
- `pilot.sh` → `pilot.md`: 4 dải, seed 1, cửa sổ quanh CH (rf).
  - Lần khởi động đầu bay chéo theo hướng dài nhất qua CH. Tôi dừng, xoá, và cho bay dọc trục (`lane.json`, bearing 0).
  - Dải 10 × 4 km: River chạy 25 phút mới mô phỏng được 80 s (7/14 critical cell xong). Tôi dừng bằng tay; log ở `pilot-w10-l4-stopped.md`.
- `w6-l4-crit.md`, `crit-pilot.sh` → `crit-pilot.md`: cửa sổ theo từng critical cell (rfc) trên cùng lượt phát.
- `sweep.sh`: chiến dịch đề xuất, **chưa chạy, chờ người dùng duyệt**.

**Kết quả chạy thử** (seed 1; `uav-l2/docs/data/sat/pilot.csv`, `pilot-crit.csv`):

| Dải | Cell | Critical | Cửa sổ quanh CH: cell cuối xong, khung | Cửa sổ theo critical cell: cell cuối xong, khung |
|---|---|---|---|---|
| 4,5 × 2 km | 60 | 3 | 23,0 s; 30,6 k | 18,8 s; 26,6 k |
| 6 × 2 km | 84 | 5 | 27,8 s; 36,2 k | 26,6 s; 32,9 k |
| 6 × 4 km | 164 | 10 | 88,4 s; 412 k | 24,8 s; 41,4 k |
| 10 × 4 km | 258 | 14 | chưa xong sau 80 s (7/14); > 458 k | 45,4 s; 179 k |

- **Cửa sổ quanh CH bão hoà theo chiều dài**, ở khoảng độ dài cửa sổ (2 km). Critical cell cách CH hơn 1 km dọc đường bay phải kéo dữ liệu từ đoạn Axe quanh CH, nên các luồng dồn về đó.
- **Cửa sổ theo critical cell gỡ được giới hạn chiều dài.**
- **Còn lại giới hạn bề ngang:** critical cell cách đường bay hơn khoảng 900 m (ngoài tầm A2G) phải nhận gần hết qua River.

**Dang dở:** chiến dịch `sweep.sh` (W 3–10 cell × L 1,5–6 km × 3 seed, ước tính 2,5–3 giờ), phân tích điểm tối ưu cấp miền, và kiểm chứng cấp nhiệm vụ.
