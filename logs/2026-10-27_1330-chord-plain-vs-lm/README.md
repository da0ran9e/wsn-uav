# 2026-10-27 · CHORD thông thường so với LM-Tour bản tốt nhất, chạy ns-3 (CLAUDE.md §8 mục 186)

**Câu hỏi:** khi CHORD chỉ là đường thẳng dài nhất qua CH (không CHORD-T), LM-Tour dựng trên nó có nhanh hơn đáng kể không?

## Thiết lập
- **Bản đồ:** k8-s1 (`--clusters 8 --seed 1`), 8 cụm, 45 critical cell. Bản đồ, cụm, node, CH giống hệt từng byte với bản đồ của bảng chính (`FIX/`).
- **Kênh:** cả bốn (open, r500, r200, r100). Một lượt ns-3 mỗi cụm (mission index 800101–800108, như bảng chính), 100 lượt bốc lớp 1 ghép cặp.
- **Ba phương án**, phần chung giữ nguyên: giao đủ một bản truy vấn mỗi cụm (`--kinPass`), cửa sổ theo critical cell, River `--repair 20`, mã fountain, phản hồi hai lần, pha 2 `-puq-stage-zero-redir` (phương pháp `P+prog-kin-puq-stage-zero-redir-kt-fcd`).

| phương án | lớp 2 | thư mục |
|---|---|---|
| **CHORD** (thông thường) | đường thẳng dài nhất qua CH, chọn riêng từng cụm; không chọn hướng chung với tour (không `--chordTour`) | `runs/CP/<kênh>/k8-s1` |
| **LM-Tour** (bản tốt nhất của `paper/LMTOUR-vi.md` §6, sweep 2) | trên dây cung của CHORD: chèn tham lam theo J_k, uốn vào đĩa B(c, ξ), CH ghim; R = 450 m, ξ auto (draft v5: 255 / 255 / 199 / 99 m), θ = 1, một vòng | `runs/LM/<kênh>/k8-s1` |
| CHORD-T (tham chiếu, P\* của bảng chính) | `--chordTour 0.6,0.8`; chạy lại pass và River từ bản lưu | `runs/REF/<kênh>/k8-s1` |

- Pass và River của LM-Tour chạy thật trên ns-3 (bước D của `LMTOUR-vi.md`, trước đây chưa làm).
- **Môi trường:** máy macOS (M3), ns-3.46 dựng riêng ở `~/Github/ns3-uav-build/ns3` (sao chép nguồn ns-3 sẵn có, module `uav-coop`, `uav-coop2` symlink về repo), Python 3.10 venv `~/Github/ns3-uav-build/.venv`. Thư mục chạy: `~/Github/ns3-uav-build/runs`.
- **Kiểm chứng binary:** sha256 khác `CAMP-BIN4` (macOS), nhưng River của CHORD-T chạy lại cho kết quả giống hệt bản cloud ở 32/32 cụm (`r*-rf-crit.csv`), và T\* tham chiếu trùng bảng chính (647 / 784 / 876 / 872 s).

## Lệnh
`bash run.sh <kênh>` (bốn kênh chạy song song, khoảng 3 giờ), rồi `python3 compare.py > table.md`.

## Kết quả (`table.md`)
T\* trung bình ± nửa khoảng tin cậy 95 % (s). Chênh ghép cặp, âm là phương án đầu nhanh hơn; ngoặc: % lượt bốc phương án đầu nhanh hơn.

| kênh | CHORD-T (tham chiếu) | CHORD | LM-Tour | LM-Tour − CHORD | CHORD-T − CHORD | LM-Tour − CHORD (River dự đoán) | đội 1 CHORD-T / CHORD / LM (s) |
|---|---|---|---|---|---|---|---|
| open | 647 ± 100 | 672 ± 102 | 672 ± 102 | +1 ± 1 (10 %) | −24 ± 22 (72 %) | +1 ± 1 | 782 / 784 / 783 |
| r500 | 784 ± 96 | 802 ± 102 | 802 ± 101 | 0 ± 4 (12 %) | −18 ± 34 (60 %) | −4 ± 5 | 782 / 784 / 792 |
| r200 | 876 ± 97 | 877 ± 105 | 867 ± 105 | −10 ± 18 (50 %) | −1 ± 36 (54 %) | −10 ± 15 | 782 / 784 / 794 |
| r100 | 872 ± 98 | 892 ± 105 | 890 ± 105 | −2 ± 5 (37 %) | −19 ± 37 (55 %) | −4 ± 5 | 782 / 784 / 794 |

Số lần chèn của LM-Tour (tổng 8 cụm): 3 / 4 / 9 / 4. Không critical cell nào kẹt ở cả ba phương án.

## Đọc kết quả
1. **LM-Tour không nhanh hơn CHORD thông thường một cách đáng kể:** 0 tới −10 s (≤ 1,2 %), mọi chênh đều nằm trong nhiễu. ns-3 xác nhận đúng dự đoán của mô hình (cột River dự đoán).
2. **Lý do giống `LMTOUR-vi.md` §7:** uốn đường không đổi được tổng lượng River của cụm; không cell nào tự giải mã thêm (own decode 0 → 0 ở r500–r100); tour đội 1 dài thêm 8–10 s.
3. **Bỏ CHORD-T làm CHORD chậm hơn 1–24 s,** và LM-Tour không lấy lại được phần đó. Phần lợi của CHORD-T đến từ chọn hướng dây cung chung với thứ tự tour, mà LM-Tour (chế độ uốn) không làm.
4. Đây là số thăm dò: một bản đồ, một lượt ns-3 mỗi cụm (quy tắc N ≥ 120, CLAUDE.md §6).
