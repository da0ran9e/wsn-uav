# Ghi chú ExScal, SmartSantander, CitySee (2026-11-17)

- Mục đích: ghi chú ba bài người dùng gửi qua chat (chatlog mục 331), là nguồn của các dòng ExScal, SmartSantander, CitySee
  trong bảng mật độ `paper/j1/CONTEXT-vi.md` mục 8.
- Đầu vào: ba PDF người dùng tải lên, chép vào scratchpad thành `exscal.pdf`, `comnet.pdf`, `liu2013b.pdf` (không commit).
- Lệnh: `extract-exscal.md`, `extract-comnet.md`, `extract-liu2013b.md` (`tools/papers/pdf_extract.py`, khoá tạm `tmp-*`).
  Hình topo ExScal cắt lại tay bằng PyMuPDF (vùng 312,128–560,382 pt trang 3, 200 dpi) vì bản tự cắt dính hình bên cạnh.
  Hai số yield 85,27 % và 73 % của ExScal là ảnh công thức, đọc bằng ảnh render trang 7.
- Metadata Crossref tự lấy sai cho SmartSantander và CitySee; DOI trong front matter ghi theo bản xuất bản, chưa đối chiếu.
- Đầu ra: `research_notes/literature/papers/{arora2005-exscal,sanchez2014-smartsantander,liu2013-citysee}.md`, 6 hình,
  dòng 49–51 của `research_notes/literature/WORKLIST-2026-11-12-vi.md`.
- Kết quả chính: ExScal khoảng 2 700 XSM/km² (983 node trên 1 260 m × 288 m, hai tuần); SmartSantander công bố khoảng
  1 130 node cố định và 23 gateway, dồn dày ở 1 km² trung tâm, không có các số 10 000 hay 15 000–20 000 node; bài CitySee
  không ghi diện tích.
- Còn dở: chưa có Mao et al. INFOCOM 2012 (nguồn diện tích CitySee); CONTEXT mục 8 chưa sửa theo các ghi chú này.
