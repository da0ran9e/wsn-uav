# 2026-11-12 · Ghi chú chi tiết bài báo: công cụ, phương pháp, 3 bài mẫu (chatlog mục 311)

- **Mục đích:** dựng cách ghi chú bài báo để tra nhanh mà không mở lại PDF, kèm hình tiêu biểu; làm mẫu trên 3 bài ★★★
  và ghi quy trình vào CLAUDE.md để chạy ở session khác.
- **Lệnh:** `extract.md` (`tools/papers/pdf_extract.py` cho leny2012, zeng2018 bản arXiv, isaacs2011);
  `tools/papers/paper_index.py` sinh danh mục.
- **Đầu vào:** PDF trong thư mục Drive của người dùng (tải về scratchpad, không commit).
- **Đầu ra:** `research_notes/literature/METHOD-vi.md`; `research_notes/literature/papers/{leny2012-dtsp,
  zeng2018-multicast,isaacs2011-dtspn}.md`, `INDEX.md`, `TOPICS.md`, `figures/` (7 hình, 524 KB, có INDEX);
  `tools/papers/{drive_fetch,pdf_extract,paper_index}.py`; mục mới trong CLAUDE.md §6.
- **Kết quả chính:**
  - Cắt hình theo chú thích hoạt động tốt với PDF có lớp chữ. Trang ảnh quét không cắt được (Isaacs 2011 tr. 2, 4, 5).
  - Zeng 2018 nêu pha chia sẻ D2D sau multicast là hướng mở (tr. 3).
  - Nhiều tham số kênh của SigDrop trùng Bảng II của Zeng 2018.
- **Dở dang:** 29 bài còn lại trong Drive và các bài người dùng sẽ lấy thêm, chạy theo `METHOD-vi.md` ở session khác.
