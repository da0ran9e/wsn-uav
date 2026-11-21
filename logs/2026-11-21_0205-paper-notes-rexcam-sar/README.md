# Ghi chú ba bài: ReXCam, Ge 2024 (SAR nhiều UAV), SAREnv

Mục đích: ghi chú bài báo theo `research_notes/literature/METHOD-vi.md` cho khoảng trống 1 và 2 ở `paper/j1/CONTEXT-vi.md` mục 31
(tương quan giữa các camera; bản đồ xác suất vị trí người cần tìm). Session phụ, mở từ session đang làm K9.

Lệnh đã chạy:
- tải PDF bằng curl về scratchpad, mỗi file một thư mục: arxiv.org/pdf/1811.01268v4, arxiv.org/pdf/2411.10148v1 (được);
  mdpi.com/2504-446X/9/9/628/pdf trả về "Access Denied" (Akamai), bài không có bản arXiv;
- `pip install pymupdf` (container chưa có);
- `extract-jain2019-rexcam.md`, `extract-ge2024-sarprob.md`: `pdf_extract.py` (chạy `python3 -I`);
- cắt lại bằng PIL ba hình của ReXCam (Fig. 4, 7, 13) vì bản cắt tự động dính cột bên cạnh;
- `index.md`: `paper_index.py`, `build_index.py`, `check.py`.

Đầu vào: hai PDF arXiv (scratchpad, không commit). Đầu ra: `research_notes/literature/papers/jain2019-rexcam.md`,
`ge2024-sarprob.md`, 8 hình trong `papers/figures/`, hai mã chủ đề mới `camera-analytics`, `search-prob` ở METHOD §6, dòng 52–54 ở
`WORKLIST-2026-11-12-vi.md`.

Kết quả: 56 ghi chú, 22 chủ đề; `check.py` không thêm lỗi mới (so trước và sau thay đổi).

Còn dang dở: bài SAREnv (Grøntved et al., Drones 2025, 9, 628) chờ người dùng gửi PDF trong session này. CONTEXT mục 31 ghi
ReXCam giảm "4,6–38 lần" theo bản v2; bản v4 ghi 3,4 / 8,3 / 23–38 lần, cần sửa ở session chính.
