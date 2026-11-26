# Trích bảy bài arXiv mở vào repo private và ghi chú bốn bài (chatlog mục 406)

Mục đích: đưa các bản arXiv đã đọc ở mục 400 vào repo private `da0ran9e/sigdrop-fulltext`, và ghi chú bốn bài sát (P1), (P2) nhất.

Lệnh: `extract.md` chạy `tools/papers/pdf_extract.py` cho 7 PDF arXiv (tải ở mục 400) thẳng vào clone của repo private. Tra Crossref
trả sai cho hermans2019, you2013, bakker2025 và thất bại cho zhan2018, nên `meta.txt` của bốn bài sửa tay.

Đầu ra:
- Repo private, commit a7ca0a6: 7 thư mục mới, INDEX.md và README.md cập nhật.
- Ghi chú mới trong repo này: `research_notes/literature/papers/{wu2018-multiuav,zhan2018-wsncollect,hermans2019-expsearch,you2013-mlbs}.md`,
  6 hình trong `papers/figures/` (Fig. 1 của Zhan cắt tay bỏ cột tài liệu tham khảo). Thêm mã chủ đề `search-theory`, `scheduling`.

Còn dở: gong2018, bakker2025, mozaffari2017 chỉ có toàn văn, chưa ghi chú.
