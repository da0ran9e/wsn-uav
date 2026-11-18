# K9: chọn critical cell và đánh đổi số critical cell (2026-11-18, chatlog mục 341)

Kế hoạch: `paper/j1/PLAN-K9-DATA-vi.md` (bước B0–B7). Phiên session_01Anfb7c. Dữ liệu C4 dựng lại trong scratchpad bằng
`logs/2026-10-27_1714-campaign4/child-setup.sh` (CAMP-BIN5 và hình học seed 1 của 12 thư mục C4); không cần build ns-3 cho
B0–B3.

## Giai đoạn 1 (B2): tập critical cell từ file ngoài

- Mã: thư mục nhiệm vụ có `crit.csv` (cột q,r, mọi cụm) thì dùng tập này thay Algorithm 3 ở mọi chỗ đọc critical cell:
  `river_plan.load` và `plan` (kế hoạch River, `river_export.py`), `mission_report.load_map` (LM-Tour, `river_surrogate`),
  `meander_lane.critical` (`mission.py --bendCrit`, làn meander). `mission.py --crit FILE` chép file vào thư mục nhiệm vụ một
  lần; chạy lại với file khác thì dừng.
- Kiểm: `b2-regress.md` (`paper/j1/analysis/crit_regress.py`) trên 12 thư mục C4 (k8, k12, k16 × open, r500, r200, r100):
  đưa đúng tập Algorithm 3 vào thì kế hoạch giống từng byte (và trùng kế hoạch chiến dịch đã bay), tập LM-Tour và tập uốn
  tour không đổi; đưa một tập khác (bỏ một cell mỗi cụm, thêm một cell) thì kế hoạch và báo cáo theo đúng tập đó. Đạt 12/12.
- Lỗi gặp và sửa: thư mục thử dùng symlink `d{k}` nên `d{k}/..` trỏ về thư mục gốc; `load` giờ tìm `crit.csv` theo tên
  (`os.path.normpath`), không qua symlink.

## Giai đoạn 2 (B0): tham số

- Đầu ra: `paper/j1/K9-PARAMS-vi.md` (ρ, cỡ dữ liệu D1–D3, thời gian xử lý theo bậc thiết bị, độ chính xác OSNet theo cỡ, tham
  số mạng). Phần lớn lấy từ repo (`research_notes/l1-edge-recognition/`, `research_notes/l1-signature-matching/`); web cho ρ
  (hai đoạn trích tìm kiếm) và bảng 6 của OSNet (đọc trang ar5iv).
- Còn là ước lượng: cỡ JPEG khung và ảnh cắt, thời gian OSNet x0,25 trên MCU, tỉ lệ node là camera, ρ mức thấp và giữa.
