# 2026-10-30 · Deluge-lite trên LM-Tour, phương án dự phòng SigDrop 2 (chat log mục 233–241)

**Mục đích:** so River với Deluge-lite trên cùng tour LM-Tour của chiến dịch 4.
- Deluge-lite: Trickle trên mọi cell của cụm, k = 1, mỗi trang 64 gói, trang ngắt ở đầu mỗi ảnh và đầu mỗi Seg.
- Cấu hình: bản đồ k12-s1 (12 cụm, 66 critical cell), kênh open và r200, 8 seed ns-3.

**Tệp:**
- `CHILD.md`: hướng dẫn cho các phiên cloud phụ;
- `setup.sh`: dựng `CAMP-BIN9` = `CAMP-BIN5` + `river-bin9.xz` (thêm `--tScope=all` và lớp frame quảng bá);
- `dl-run.sh REG R [TAG]`: một (kênh, seed);
- `dl-session.sh`: chạy theo phiên;
- `dl_export.py`: xuất kết quả;
- `results/<kênh>-R<seed>-<tag>-{runs,cells}.csv`, `-check.txt`.

**Tinh chỉnh** (`tuning.md`, `tune-dla.md`, `tune-dlb.md`; open, seed 1):

| | Imin / Imax | Readiness trung bình | Frame tổng |
|---|---|---|---|
| River | – | 473,0 s | 930 900 |
| dla | 0,5 / 8 s | 482,8 s | 6 779 134 |
| dlb | 2 / 60 s | 482,3 s | 6 027 140 |

Chọn `dlb` (`dl-config.txt`).

**Đã chạy:**
- River (`rf`): open seed 1–8, r200 seed 1–8.
- Deluge-lite `dlb`: open seed 1 và 4.
- `dla`: open seed 1, chỉ để tinh chỉnh.

**Còn dở:** Deluge-lite cho các seed còn lại và cho r200. Tạm dừng ở mục 241. Paper v5.3 dùng thí nghiệm Deluge trên pass CHORD (`2026-10-30_1545-deluge-r100`), không dùng thí nghiệm này.

**Trạng thái:** dở.
