# 2026-10-25 · Đóng băng binary và chạy thử chiến dịch CHORD-T (chat log mục 161)

**Mục đích:** đóng băng binary ns-3 và chạy thử job của `2026-10-25_0237-campaign` trên hai bản đồ, trước khi chạy cả chiến dịch.

**Lệnh và kết quả** (mỗi bước một `.md` qua `tools/runlog.py`):
- `freeze-bin.md`: chép `BIN2` thành `CAMP-BIN` (27 MB).
  - sha256: `deploy-bin` e38d9e5e…, `pass-bin` 8ca6282c…, `river-bin` ed66896e….
- `try-P-k2-s4.md`, `try-P-k8-s1.md`, `try-Pt-k2-s4.md`, `try-K-k2-s4.md`, `try-K-k8-s1.md`: job thử.
  - k2-s4: 2 cụm, 13 critical cell.
  - k8-s1: 8 cụm (78, 72, 70, 78, 80, 80, 79, 80 cell), 13 086 node.
  - Trickle trên k2-s4: 6/6 critical cell xong, 20,4 s mô phỏng.
- `try-score-P.md`, `try-score-K.md`: chấm điểm trên k2-s4.
  - P\* 389 s, Pd 389 s, Pt 390 s, B4 411 s; K 388 s.

**Kết luận:** job và cách chấm chạy được, nhưng chiến dịch không chạy tiếp (mục 162–163). Binary của chiến dịch 4 là `CAMP-BIN5`, nằm ở `2026-10-27_1714-campaign4`.

**Trạng thái:** lịch sử.
