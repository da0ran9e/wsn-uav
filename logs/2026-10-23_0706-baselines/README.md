# 2026-10-23 · Baseline: cài đặt và bảng so sánh nhanh (CLAUDE.md §8 mục 134, 139, 140)

**Mục đích:** cài các baseline còn thiếu (cánh bằng bay vòng B8, quét luống B5, Trickle trên ns-3), chạy cùng các baseline sẵn có và các ablation lớp 2 (subCH-K, MEANDER-K) trên 16 bản đồ ghép cặp, để phán đoán kết quả trước chiến dịch. Số thăm dò (16 bản đồ × 100 lượt bốc), chưa phải số công bố.

**Bản đồ:** 16 bản đồ của `logs/2026-10-22_1947-swath-validate/` (`maps.txt`). P\* = CHORD-T CLUE 80 % (`VB/chordT1`), `P+prog-kin-puq-stage-zero-redir`; mọi phương án có đội 2 dùng cùng chính sách đó.

**Mã mới:**
- `uav-l2/tools/l1_rank.py`: B8-r (cánh bằng bay vòng bán kính 255 m quanh tâm nhóm r của B3, fountain lý tưởng ở PER trung bình trên vòng); B5 (đường luống SWATH phủ cả miền, phát lặp bộ manh mối, thu như pass; luống rộng nhất trong 12…3 cell mà mọi critical cell đủ 12 manh mối với xác suất ≥ 0,9 theo kỳ vọng, rồi mới bốc một lần thu); `Pt`, `Pt+prog` (Trickle); B3/B6 nhận `-redir`.
- `uav-coop2/examples/coop2-river.cc --scheme=trickle` (Deluge kiểu cell, RFC 6206: Imin 1 s, Imax 64 s, k = 1, trang 64 gói; cùng cell, lưới kênh, gateway như River). Binary `BIN2/river-bin`; với `--scheme=river` cho kết quả giống từng dòng binary đóng băng (`regress-river.md`). Thử một cụm: `try-trickle-k2-s4-c1.md`.
- `uav-l2/tools/mission.py`: scheme `t`; mặc định `--schemes` giữ `rf,ad12,d`. `meander_mission.py --axeNear`.
- `uav-l2/tools/baseline_table.py`: bảng so sánh.

**Lệnh:** `job-subch.sh` (subCH-K, `SK/<map>`), `job-meanderK.sh` (MEANDER-K, `MK16/<map>`), `job-trickle.sh` + `run-trickle.sh` (Trickle trên `VA/CT1-<map>`), `build-trickle.md`; chấm điểm `score-base.md`, `score-b5.md` (B5 sau khi sửa cách chọn luống), `score-subch.md`, `score-meanderK.md`, `score-trickle.md`. Mọi lượt chạy thoát 0 (`done-*.txt`). Thư mục làm việc và CSV lượt bốc trong scratchpad (`SK/`, `MK16/`, `VA/`, `BL/`, không commit).

**Kết quả:** `table-all.md` (bảng đầy đủ), `table-no-trickle.md` (bản tạm).

| Phương án | T\* TB | So với P\* (P\* nhanh hơn) | Khung mặt đất / bản đồ |
|---|---|---|---|
| P\* | 585 | – | 252 k |
| kéo thẳng / Trickle | 586 / 586 | +0 (9/16) / +1 (7/16) | 284 k / 1 182 k |
| không hợp tác | 635 | +50 (15/16) | – |
| k-medoids / SWATH-K / MEANDER-K / subCH-K | 614 / 621 / 650 / 600 | +29 / +35 / +64 / +15 (16, 13, 16, 10/16) | 147 / 185 / 92 / 224 k |
| B5 / B8-500 / B3-500 / B1 | 697 / 953 / 1 478 / 1 859 | +112 / +368 / +892 / +1 274 | – |
| B7 (cận dưới) | 299 | −286 | – |

Lớp 3 trên cùng thư mục CHORD-T (lúc critical cell đủ cửa sổ, tính từ khi UAV rời cụm):

| | TB | p90 | cell cuối mỗi bản đồ, TB | khung / bản đồ |
|---|---|---|---|---|
| River | 12,6 s | 24,9 s | 52,1 s | 252 k |
| kéo thẳng | 14,4 s | 32,3 s | 49,4 s | 284 k |
| Trickle | 22,3 s | 44,8 s | 88,2 s | 1 182 k |

**Nhận xét:**
- T\* không phân biệt các cách hợp tác (River, kéo thẳng, Trickle cùng khoảng 585 s): nó do tour đội 1, LoRa và đội 2 quyết định (hàng trăm giây), còn lớp 3 chỉ vài chục giây. Lợi của River nằm ở chi phí mạng (ít hơn Trickle 4,7 lần khung, ít hơn kéo thẳng 11 %) và ở lúc dữ liệu tới critical cell.
- subCH-K là baseline lớp 2 mạnh nhất (+15 s, P\* chỉ nhanh hơn ở 10/16), dù chưa có CHORD-T.
- MEANDER-K ghép cặp, đủ sửa mô hình, vẫn chậm hơn ở 16/16; River gần như không thêm lợi cho nó.
- B3, B6, B8 dùng fountain lý tưởng khi phục vụ nhóm (lạc quan cho chúng).

**Dang dở:** chốt N và chiến dịch; cân nhắc CHORD-T trên cách chia subCH; chọn chỉ số chính cho lớp 3 trong bài (khung, lúc critical cell đủ cửa sổ) bên cạnh T\*.
