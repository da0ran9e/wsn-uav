# Bản nháp J1 v2, kịch bản rừng, mục I–V (chatlog mục 412)

Mục đích: soạn lại bản nháp paper theo kịch bản rừng đất thấp, từ đầu bài tới phát biểu bài toán, kèm hình minh hoạ.

Lệnh:
- `01-figures.md`: `python3 paper/j1/analysis/fig_draft_v2.py paper/j1/figures`, sinh 4 hình (mỗi hình bản không chữ, bản có nhãn
  PNG và PDF).
- `02-build.md`: `sh paper/j1/draft-v2/tex/build.sh` (pdflatex hai lượt). TeX Live cài bằng apt trong container này
  (texlive-latex-extra, texlive-publishers), không commit.

Đầu vào: `paper/j1/maps-forest/cattien/{trails,streams}.geojson`; số liệu mật độ ở `paper/j1/CONTEXT-vi.md` mục 5; hình cũ dùng lại từ
`paper/j1/draft-v1/figs/` (bound-nc, concept-river, nd1-channel).

Đầu ra: `paper/j1/draft-v2/tex/main.pdf` (8 trang), hình `paper/j1/figures/draft2-*`.

Kết quả: PDF dựng sạch, không còn tham chiếu hỏng; còn một dòng tràn lề 1,7 pt ở công thức (2). Weissberger với tán 10 m cho 8,1 dB ở
45°, 17,5 dB ở 11°, 24,9 dB ở 6° (repo ghi 26 dB ở 6°, chênh do làm tròn góc).

Còn dở: mục VI–X chưa viết lại; các chỗ [TODO] và [OPEN] trong PDF.
