# 2026-11-06 · Tái tổ chức repo, bước 4–8 (`docs/REORG-GUIDE-vi.md`, chat log mục 273)

**Mục đích:** phân loại tài liệu, lưu trữ phần cũ, gom tham số về một nguồn, thêm công cụ kiểm tra. Không chạy mô phỏng.

**Lệnh:** `check.md` (`tools/check.py`), `params.md` (`tools/params.py check`), `build-index.md` (`tools/build_index.py`).

**Kết quả:**
- 54 tài liệu có nhãn trạng thái: hiện hành 9, tham khảo 19, bị thay thế 13, lịch sử 13 → `docs/DOCS-INDEX.md`.
- Mã và tài liệu wsn-uav cũ → `archive/wsn-uav-legacy/`; 10 bản nháp paper → `paper/archive/`; thư mục có dấu cách đổi tên.
- `params.yaml` (9 mục, 95 tham số); `tools/params.py render` tái tạo bảng `paper/PARAMS-vi.md` giống từng byte.
- `tools/check.py`:
  - 5 liên kết hỏng, đều có từ trước: 4 tệp đã xoá từ commit đầu ở README wsn-uav cũ, 1 đoạn mã bị nhận nhầm;
  - 77 ảnh cũ chưa có dòng INDEX (quy tắc mục 131 chỉ áp cho ảnh mới);
  - 3 tệp trên 5 MB.

**Còn dở:** bước 6 chưa giảm được `.git`, xem `docs/REORG-GUIDE-vi.md`. Mã chưa đọc `params.yaml`.
