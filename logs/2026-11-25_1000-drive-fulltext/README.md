# Trích toàn văn các bài trong thư mục Drive (chatlog mục 401)

Mục đích: người dùng cần một thư mục chứa toàn bộ nội dung gốc (chữ và hình) của các bài đã có PDF, để tra mà không mở PDF.

Lệnh:
- `fetch.md`: `python3 tools/papers/drive_fetch.py <thư mục Drive của dự án> <scratchpad>/drive-pdf`, tải 50 PDF (88 MB).
- Khớp từng PDF với khoá ghi chú qua trường `file:` trong `research_notes/literature/papers/*.md`; bỏ `leny2012 (1).pdf`
  (trùng từng byte với `leny2012.pdf`); `main.pdf` là dargie2021-lqe; Typhoon có hai file.
- `extract.md`: `tools/papers/pdf_extract.py` cho từng bài, 49/49 thành công. Thêm hai bài người dùng tải lên ngày 2026-11-23
  (nguyen2021-hole, nguyen2023-gambac) từ lần trích trước.

Đầu ra (không commit, theo `research_notes/literature/METHOD-vi.md` mục 9): thư mục `sigdrop-fulltext/` trong scratchpad, 51 bài,
47 MB, có `INDEX.md`; gửi cho người dùng dạng `sigdrop-fulltext-2026-11-25.zip`.

Lưu ý: file Typhoon bản Springer chỉ có 2 trang, toàn văn ở bản EWSN; `meta.txt` tra Crossref tự động có chỗ sai (gudmundson1991),
INDEX lấy tên bài từ ghi chú repo.
