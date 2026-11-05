# Chỉ mục thí nghiệm

- **Trạng thái:** hiện hành, 2026-11-05.
- **Phạm vi:** các thí nghiệm có số liệu đang dùng trong paper SigDrop (bản nộp ICC v5.3), cùng vài thí nghiệm tham khảo. Mọi thư mục log, kể cả lịch sử, xem `logs/INDEX.md`.
- **Quy ước:** mã thí nghiệm dùng chung cho thư mục log, CSV, tài liệu và hình. Khi tạo thí nghiệm mới, đặt mã và thêm một dòng ở đây.

## Đang dùng trong paper

| Mã | Câu hỏi | Cấu hình | Log | Dữ liệu | Tài liệu | Trong paper |
|---|---|---|---|---|---|---|
| C4 | LM-Tour, CHORD, DTSP-N (+ River hoặc + FC) trên nhiều kênh | 3 bản đồ (k8-s1, k12-s1, k16-s1 = 8/12/15 cụm) × 4 kênh (open, r500, r200, r100) × seed 1–10; dừng ở 290/360 job, mỗi ô ghép cặp 6–10 seed; binary CAMP-BIN5 | `logs/2026-10-27_1714-campaign4/` | `uav-l2/docs/data/results/campaign4.csv`, `logs/.../score/R*/` | `paper/TECHREPORT-vi.md` §3, `uav-l2/docs/RESULTS-vi.md` §7.1 | Bảng I–II, Hình 4, §VI |
| ENVm | Ba mức môi trường theo R50 | L_obs = 0 / 9,0 / 19,8 / 25,7 dB → R50 ≈ 1015 / 498 / 199 / 99 m | `logs/2026-10-25_0330-env-modes/` | trong log | `paper/PARAMS-vi.md` | §III-B |
| A2G | Bán kính phát hiệu quả theo môi trường | giải tích | `logs/2026-10-24_1056-a2g-radius/` | trong log | — | §III-B |
| LMT | Bộ dự đoán thời gian River (bước A) | 812 critical cell của 12 lượt C4 seed 1 | `logs/2026-10-25_1500-lm-tour/` | `uav-l2/docs/data/results/river-surrogate*.{csv,json}` | `paper/LMTOUR-vi.md` | §V, §VI (β, MAE) |
| LMD | LM-Tour: DTSP-N qua CH rồi uốn về landmark | k8-s1 | `logs/2026-10-27_1800-lm-dtspn/` | trong log | `paper/LMTOUR-vi.md` | §V, Thuật toán LM-Tour |
| T3S | Bộ dự đoán dạng cây có tốt hơn công thức tuyến tính không | 192 lượt River trên k8 | `logs/2026-10-28_t3-surrogate/` | trong log | `paper/TECHREPORT-vi.md` §5.7 | §VI (26,2 vs 45,9 s) |
| DRC, DRF | DTSP-N + River: zigzag, rồi sửa cho qua mọi critical cell | seed 1 của C4 | `logs/2026-10-28_0240-dtspn-check/`, `logs/2026-10-28_0310-dtspn-fix/` | trong log | `paper/TECHREPORT-vi.md` §3.4 | §VI (36/92 cell, +44 %) |
| P1F | Đường bay pha 1 và độ dài tour | seed 1, mọi kênh | `logs/2026-10-28_0810-phase1-paths/` | `paths.md` | `uav-l2/docs/figures/c4-phase1/INDEX.md` | Hình 5 |
| DLG | Lập kế hoạch so với khám phá: River vs kéo trực tiếp vs Deluge/Trickle | pass CHORD, k8-s1, r100, seed 1–5 | `logs/2026-10-30_1545-deluge-r100/` | trong log | `paper/SIM-REPORT-2026-10-31-vi.md` | §VI (1,9–2,5× frame) |
| WND | Sai số quỹ đạo do gió | k8-s1, r100, σ 50/100/200 m, seed 1–3 | `logs/2026-10-31_0000-wind/` | trong log | `paper/SIM-REPORT-2026-10-31-vi.md` | §VI |
| TKO | Takeover (dấu ranh giới) bù sai lệch đường bay | lặp lại bảng WND | `logs/2026-11-01_0600-takeover/` | trong log | `paper/SIM-REPORT-2026-11-01-takeover-vi.md` | §IV, §VI (112–118 s) |

## Tham khảo và việc dở

| Mã | Nội dung | Log | Ghi chú |
|---|---|---|---|
| SAT | Ngưỡng bão hoà theo hình dạng cụm | `logs/2026-10-21_1738-saturation/` | điểm tối ưu dùng cho MEANDER (`uav-l2/docs/SAT-vi.md`) |
| FCB, BL2 | FC, DN và sáu baseline trước C4 | `logs/2026-10-25_0600-fc-baseline/`, `logs/2026-10-26_0900-baselines/` | bị C4 thay thế; dữ liệu `uav-l2/docs/data/results/{chord-fc,baselines}.csv` |
| DLL | Deluge-lite trên LM-Tour, k12 | `logs/2026-10-30_1730-deluge-lite/` | tạm dừng (mục 241), chưa có README |
| C4 (phần còn lại) | 70 job chưa xong | `docs/progress/HANDOFF.md` | `lmd 4 r500 16` hỏng tất định (river-bin segfault ở C10) |
