# 2026-10-22 · Báo cáo kỹ thuật lớp 3 có hình từng bước (CLAUDE.md §8 mục 125–126)

**Mục đích:** dựng lại tài liệu lớp 3 thành một báo cáo kỹ thuật, với hình mô tả các bước của từng thuật toán theo kiểu trình phát visualize. Báo cáo dùng các hình người dùng gợi ý cho phần giới thiệu bài toán, lớp 1 và cơ chế River (mục 126), thêm ảnh chụp từ trình phát.

**Đầu vào:**
- Nội dung: `paper/RIVER-L3-vi.md` (bản rút gọn, mục 124).
- Trace ns‑3 của C3 (River chuẩn bị sẵn) và bitmap lượt phát `pass3b-bits-r1.bin`, ở thư mục tạm của phiên trước (`c3trace/`, `l2dep/`). Chúng không được commit. Trace là đầu ra `uav-coop2-river --trace` (s = rf, ro, d), như ghi ở đầu `uav-l2/tools/cluster_steps.py`.
- Trình phát `uav-l2/docs/anim/mission-replay.html`, `meander-replay.html`.

**Lệnh (mỗi bước một tệp .md):**
- `figs-steps.md`: `tools/l3_report_figs.py` vẽ 6 hình từng bước trên C3 → `uav-l2/docs/figures/tr-l3-{alg1,alg2,alg3,alg4,gather,run}.png`. Số in ra là số mà chú thích hình trích dẫn.
- `shots-mission.md`, `shots-meander.md`: `tools/anim_shots.py` chụp khung tĩnh từ hai trình phát → `uav-l2/docs/figures/tr-shot-*.png`. Trình phát giữ trạng thái trong closure, nên công cụ nạp một bản sao có móc tua (không sửa tệp gốc).
- `build-pdf.md`: `paper/techreport/build.py` dựng markdown thành HTML rồi in PDF A4 bằng Chromium. Bản cuối có 26 hình, 9 bảng, 32 trang. Lần dựng đầu (37 trang) buộc mỗi mục sang trang mới và để nhiều khoảng trắng; lần hai chỉ ngắt trang trước phụ lục và thu nhỏ bốn hình cao.

**Đầu ra:**
- `paper/L3-TECHREPORT-vi.md`: nguồn của báo cáo.
- `paper/techreport/L3-TECHREPORT-vi.pdf`: 32 trang, khoảng 6,9 MB.
- `paper/techreport/{build.py, report.css}`: công cụ dựng. Phông Source Serif 4, IBM Plex Sans, JetBrains Mono được tải một lần từ Google Fonts bằng curl vào thư mục cache (không commit).
- `uav-l2/tools/{l3_report_figs.py, anim_shots.py}` và 13 hình `tr-*.png` (khoảng 3,9 MB).

**Ghép hình người dùng gợi ý (mục 126) với tệp trong kho:**

| Ảnh | Tệp | Ghi chú |
|---|---|---|
| 5 | `uav-sar/docs/visualize/result/a2g-strip-node4.png` | |
| 6 | `uav-sar/docs/visualize/result/a2g-sweep-map-K2000.png` | |
| 7 | `uav-sar/docs/visualize/result/g2g-chain-spacetime.png` | |
| 8 | `uav-coop/docs/figures/route-tables.png` | |
| 9 | `uav-coop2/docs/figures/ns3-setup.png` | |
| 10, 11, 12, 16 | `uav-coop2/docs/figures/concept-{river,axe,river-setup,circle}.png` | |
| 13, 15 | `concept-banks.png`, `concept-axe-banks.png` | ảnh người dùng gửi là **bản cũ**, trước khi Bank được dựng bằng đường vuông góc (commit 666c959); báo cáo dùng bản hiện tại trong kho |
| 14 | `uav-coop2/docs/figures/river-plan.png` | |
| 17 | `uav-coop2/docs/figures/ns3-gather.png` | |
| 18, 19 | `uav-l2/docs/figures/c3-step5.png` | hai ảnh trùng nhau |

Các hình 5–9, 14, 17 có chữ trên hình; chúng được giữ nguyên vì người dùng đã chọn chúng.

**Dang dở:** chưa có bản trang web (artifact) của báo cáo này. `paper/overview-page/build.py` chưa hiểu cú pháp hình nhiều ảnh, tham chiếu `{fig:…}` và chú thích bảng của báo cáo.
