# Ghi chú hai bài của nhóm Nguyen Khanh-Van (chatlog mục 395)

Mục đích: ghi chú hai bài người dùng tải lên, làm mẫu cách viết đặt vấn đề và phát biểu bài toán cho J1.

Lệnh (log từng bước ở `extract-*.md`):
- `python3 tools/papers/pdf_extract.py <scratchpad>/pdf2/a.pdf nguyen2021-hole <scratchpad>/papers`
- `python3 tools/papers/pdf_extract.py <scratchpad>/pdf2/b.pdf nguyen2023-gambac <scratchpad>/papers`
- `python3 tools/papers/paper_index.py`, `python3 tools/build_index.py`, `python3 tools/check.py`

Đầu vào: hai PDF người dùng tải lên (không commit). Chữ trích và hình gốc nằm ở scratchpad, không commit.

Đầu ra:
- `research_notes/literature/papers/nguyen2021-hole.md`, 4 hình `figures/nguyen2021-hole-fig{2,3,7,16}.png` (Fig. 7 cắt tay bỏ cột
  chữ bên cạnh).
- `research_notes/literature/papers/nguyen2023-gambac.md`, 3 hình `figures/nguyen2023-gambac-fig{1,2,4}.png`.
- Thêm mã chủ đề `geo-routing`, `clustering` vào `research_notes/literature/METHOD-vi.md` mục 6.

Kết quả chính: cả hai bài đọc toàn văn; cả hai không có phát biểu bài toán tối ưu dạng công thức (ghi ở mục hạn chế).
Còn dở: không.
