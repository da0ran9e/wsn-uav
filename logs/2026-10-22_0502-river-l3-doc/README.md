# 2026-10-22 · Tài liệu chi tiết lớp 3 / River (CLAUDE.md §8 mục 122)

**Mục đích:** viết một tài liệu tổng hợp giống bản tổng quan, nhưng chỉ tập trung và đi sâu vào lớp 3 và cơ chế River, có hình từng bước và mã giả cho từng phần.

**Đầu ra:**
- `paper/RIVER-L3-vi.md`: tài liệu, 14 mục, 21 hình. Mỗi thuật toán (1, 2, 2b, 3, 3b, 4, 4b, G, 5, 6, 7, D, S) có mã giả ngắn và mã giả đầy đủ.
- Trang web: https://claude.ai/artifact/WpB2R7G7pVpo4QUwjW4DXB (riêng tư cho tới khi được chia sẻ).
- Ba hình mới, không chữ:
  - `uav-l2/docs/figures/river-window.png`: cửa sổ quanh CH so với cửa sổ theo từng critical cell, trên dải 6 × 4 km;
  - `uav-l2/docs/figures/river-pass-strips.png`: dải gói nhận được của một node và của cả cell, ở 0–800 m từ đường bay;
  - `uav-coop2/docs/figures/ns3-sweeps-plain.png`: bản không chữ của `ns3-sweeps.png`.

**Mã mới hoặc sửa:**
- `uav-l2/tools/window_figure.py`, `uav-l2/tools/pass_strips_figure.py` (mới).
- `uav-coop2/tools/river_sweep_figure.py`: thêm `--plain` (bỏ chữ trên hình).
- `paper/overview-page/build.py`, `template.html`: dựng được nhiều tài liệu (`--doc overview|river-l3`). Bản tổng quan dựng lại giống từng byte (`build-overview-check.md`).

**Lệnh** (mỗi bước một file `.md`):
- `window-figure.md`, `pass-strips-figure.md`: đầu vào là hai dải của chiến dịch bão hoà trong scratchpad (`SAT/w6-l4-s1`, `SAT/w10-l4-s1`; khoảng 1,4 MB và 6 MB, không commit). Tạo lại được bằng `uav-l2/tools/sat_strip.py --width 6 --length 4 --seed 1 --schemes rf,rfc` và `--width 10 --length 4 --seed 1 --schemes rf,rfc`.
- `sweeps-plain.md`: từ `uav-coop2/docs/data/camp54/` (20 lượt), in lại toàn bộ bảng so sánh ghép cặp.
- `build-page.md`, `build-overview-check.md`: dựng trang.

**Số mới trong tài liệu** (từ các lệnh trên):
- Dải 6 × 4 km, 10 critical cell: cửa sổ quanh CH xong trung bình 51,6 s (3–88 s); cửa sổ riêng 7,6 s (3–25 s).
- Dải 10 × 4 km, node ở 0 / 200 / 400 / 600 / 800 m: nhận 3 991 / 3 885 / 3 654 / 3 062 / 2 222 trên 8 000 gói, chuỗi liền dài nhất 460 / 688 / 92 / 42 / 20; cả cell 6 019 / 6 180 / 5 886 / 5 631 / 5 348, chuỗi liền 4 860 / 5 004 / 4 739 / 4 642 / 3 960.

**Dang dở:** không có cho mục này. Vẫn chờ duyệt từ trước: chạy lại nhiệm vụ trên 40 bản đồ với cửa sổ theo critical cell (k‑medoids và MEANDER‑K).
