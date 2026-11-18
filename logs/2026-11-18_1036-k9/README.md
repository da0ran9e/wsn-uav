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

## Giai đoạn 3 (B1): luồng nền về AI node

- Script `paper/j1/analysis/bg_load.py`; kết quả `data/b1-k8.{md,csv}`, `data/b1-k12.*`, `data/b1-k16.*`; lệnh ở
  `b1-bg-load-*.md`. Kênh r100 (luồng nền không phụ thuộc kênh A2G), mô hình tải của `river_lb.py`.
- Tập AI cell: k-medoids theo số chặng cell trong từng cụm, N = 8…128, cộng tập Algorithm 3. Mỗi cụm giữ mesh riêng.
- Kết quả (k8, ngân sách 10 % thời gian, 30 % node là camera): ρ lớn nhất mà môi trường bận nhất còn chịu được là 0,2–1,9
  người/h với D1, 0,7–7,7 với D2, 13–145 với D3 khi N tăng từ 8 lên 128. Môi trường bận nhất là cell của AI node. k12, k16 cùng
  cỡ. Tập Algorithm 3 (45 cell) chỉ ngang N = 16 medoids, vì các critical cell của nó dồn cục (xa nhất 8 cell, 1 269 node đổ
  về một AI node).
- Hệ quả: D1, D2 không khả thi ở mọi ρ thật trên 802.15.4; D3 chỉ chịu được phố vắng tới phố thường nếu có khoảng 100 AI cell
  trở lên. Ở mức ρ khả thi, năng lực tính của AI node không bị chạm (N = 8: khoảng 2 bản ghi mỗi giây vào AI node bận nhất).

## Giai đoạn 4 (B3): chọn critical cell cho D3 (đang làm)

- Script `paper/j1/analysis/cc_select.py`: River theo surrogate C4 (công thức, mỗi critical cell thêm vào làm cả cụm chậm hơn
  qua cluLack), mạng nền theo `bg_load.py` (ngân sách 10 / 20 %, 30 % node là camera, 528 B mỗi người, giới hạn 5 cell); số
  critical cell ít nhất còn khả thi (nhân đôi rồi chia đôi m), đặt chỗ bằng tìm kiếm cục bộ. Tập chọn ghi ở
  `data/crit-<thư mục>-u<ngân sách>-rho<ρ>.csv` (dùng với `mission.py --crit`).
- Lần chạy đầu (bản tính tải bằng vòng lặp Python) bị dừng ở giới hạn 1 giờ; bản hiện tại tính sẵn tải của mọi cặp (AI cell,
  cell), kiểm trùng với `bg_load.Cluster.load` ngay trong script, nhanh hơn 50–100 lần.
- k8 r100 (`data/cc-r100-R1-k8-s1.md`): ngân sách 10 %, ρ = 20 / 50 / 100 / 200 cần 24 / 34 / 69 / 161 critical cell, T1 mô
  hình 661 / 674 / 728 / 906 s; Algorithm 3 (45 cell) có T1 753 s và vi phạm giới hạn chặng (xa nhất 8 cell). r200 cùng số cell,
  T1 thấp hơn 7–30 s. Đối chiếu với kế hoạch River thật: lệch 0,00 s.
- Còn chạy: k12 và k16 ở r100. Surrogate khớp trên 4–9 critical cell mỗi cụm; tập 20 cell mỗi cụm nằm ngoài vùng khớp, B4 cần
  kiểm bằng ns-3.
