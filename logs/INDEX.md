# Chỉ mục log

Mỗi thư mục trong `logs/` một dòng. Mã là mã thí nghiệm dùng chung với `docs/EXPERIMENTS-INDEX.md`; mục là số trong
`docs/chatlog/INDEX.md`. Trạng thái: **hiện hành** (số đang dùng trong paper v5.3 hoặc mã đang chạy), **tham khảo**,
**bị thay thế**, **lịch sử** (thử nghiệm đã đóng), **tài liệu** (chỉ dựng tài liệu), **vận hành**, **dở**.
Thêm một dòng mỗi khi tạo thư mục log mới.

| Mã | Thư mục | Nội dung | Mục | Trạng thái |
|---|---|---|---|---|
| L1P | [`2026-10-19_1500-l1-propose`](2026-10-19_1500-l1-propose/) | lớp 1 (M, L, F, f, k) trong nhiệm vụ đề xuất | 92–94 | lịch sử |
| L1D | [`2026-10-19_1639-l1-device`](2026-10-19_1639-l1-device/) | thời gian đối sánh trên Pi 5 (+Hailo-8L) | 95 | lịch sử |
| CRV | [`2026-10-19_1838-curve-banks`](2026-10-19_1838-curve-banks/) | Bank theo pháp tuyến cục bộ, MEANDER đầu tiên | 103 | lịch sử |
| MND1 | [`2026-10-20_0222-meander-ns3`](2026-10-20_0222-meander-ns3/) | MEANDER cả nhiệm vụ, ns-3, 4/6/8 cụm | 104 | lịch sử |
| MND1a | [`2026-10-20_0314-meander-anim`](2026-10-20_0314-meander-anim/) | animation MEANDER | 105 | lịch sử |
| MND1b | [`2026-10-20_0331-fixes`](2026-10-20_0331-fixes/) | ba hướng sửa MEANDER (span, window, k-medoids cong) | 106 | lịch sử |
| L1V | [`2026-10-20_1614-l1-vector`](2026-10-20_1614-l1-vector/) | lớp 1 bằng điểm cosine từng ảnh | 110 | lịch sử |
| L1M | [`2026-10-20_1834-l1-mission`](2026-10-20_1834-l1-mission/) | nhiệm vụ trọn vẹn với mô hình lớp 1 mới | 113–114 | lịch sử |
| C2 | [`2026-10-20_1846-campaign2`](2026-10-20_1846-campaign2/) | chiến dịch ns-3 vòng 2: 40 bản đồ × KW/MW/SW | 114 | lịch sử |
| L2D | [`2026-10-21_0010-l2-diag`](2026-10-21_0010-l2-diag/) | chẩn đoán vì sao MEANDER chưa thắng | 115 | lịch sử |
| L2A | [`2026-10-21_0110-l2-adjust`](2026-10-21_0110-l2-adjust/) | chỉnh MEANDER, thêm động học đội 1 | 116–117 | lịch sử |
| SAT | [`2026-10-21_1738-saturation`](2026-10-21_1738-saturation/) | ngưỡng bão hoà theo hình dạng cụm | 120–121 | tham khảo |
| — | [`2026-10-22_0502-river-l3-doc`](2026-10-22_0502-river-l3-doc/) | tài liệu lớp 3 / River | 122 | tài liệu |
| — | [`2026-10-22_0518-l2-doc`](2026-10-22_0518-l2-doc/) | tài liệu nhanh lớp 2 (MEANDER) | 123 | tài liệu |
| — | [`2026-10-22_0549-docs-short`](2026-10-22_0549-docs-short/) | rút gọn hai tài liệu lớp 3, lớp 2 | 124 | tài liệu |
| — | [`2026-10-22_0928-l3-techreport`](2026-10-22_0928-l3-techreport/) | báo cáo kỹ thuật lớp 3 có hình | 125–126 | tài liệu |
| — | [`2026-10-22_1006-l2-techreport`](2026-10-22_1006-l2-techreport/) | báo cáo kỹ thuật lớp 2 kiểu IEEE | 127 | tài liệu |
| ENV | [`2026-10-22_1732-env-setup`](2026-10-22_1732-env-setup/) | dựng lại môi trường ns-3 trên container mới | — | vận hành |
| ENVr | [`2026-10-22_1745-repro`](2026-10-22_1745-repro/) | kiểm chứng môi trường mới bằng bản đồ cũ | — | vận hành |
| MNDK | [`2026-10-22_1746-meanderK-geom`](2026-10-22_1746-meanderK-geom/) | MEANDER-K: hình học trên 40 bản đồ | 118, 134 | lịch sử |
| SCHK | [`2026-10-22_1750-subchK-geom`](2026-10-22_1750-subchK-geom/) | subCH-K: hình học trên 40 bản đồ | 118, 134 | lịch sử |
| PIT | [`2026-10-22_1806-propose-iter`](2026-10-22_1806-propose-iter/) | chốt propose: lặp cải tiến trên k8-s10 | 135 | lịch sử |
| SWV | [`2026-10-22_1947-swath-validate`](2026-10-22_1947-swath-validate/) | kiểm các phương án lớp 2 trên 16 bản đồ | 136 | lịch sử |
| — | [`2026-10-23_0433-clue80-figs`](2026-10-23_0433-clue80-figs/) | hình CHORD-T, CLUE 80 % | 138 | lịch sử |
| BL1 | [`2026-10-23_0706-baselines`](2026-10-23_0706-baselines/) | baseline B5, B8, Trickle; bảng nhanh 16 bản đồ | 134, 139–140 | lịch sử |
| — | [`2026-10-23_1027-algo-maps`](2026-10-23_1027-algo-maps/) | hình các thuật toán trên cùng bản đồ | 141 | lịch sử |
| CMK | [`2026-10-23_1754-chord-meander-kin`](2026-10-23_1754-chord-meander-kin/) | CHORD-T vs MEANDER, động học, giao đủ | 144–145 | lịch sử |
| MNL | [`2026-10-23_1837-meander-lane`](2026-10-23_1837-meander-lane/) | MEANDER kiểu luống vs CHORD-T | 146 | lịch sử |
| MNW | [`2026-10-23_1855-meander-wins`](2026-10-23_1855-meander-wins/) | tìm kịch bản MEANDER thắng | 147 | lịch sử |
| FSW | [`2026-10-23_1920-factor-sweep`](2026-10-23_1920-factor-sweep/) | quét yếu tố MEANDER vs CHORD-T, ns-3 | 148–150 | lịch sử |
| MNS | [`2026-10-24_0403-meander-straight`](2026-10-24_0403-meander-straight/) | MEANDER làm thẳng dần | 151 | lịch sử |
| MNT | [`2026-10-24_0514-meander-trim`](2026-10-24_0514-meander-trim/) | MEANDER thẳng hẳn, giao vừa đủ | 153 | lịch sử |
| CHA | [`2026-10-24_0522-ch-anywhere`](2026-10-24_0522-ch-anywhere/) | CH ngẫu nhiên cho CHORD-T và MEANDER | 154 | lịch sử |
| MGC | [`2026-10-24_0541-meander-given-ch`](2026-10-24_0541-meander-given-ch/) | MEANDER theo CH có sẵn | 155 | lịch sử |
| NGC | [`2026-10-24_0714-ns3-given-ch`](2026-10-24_0714-ns3-given-ch/) | CHORD-T uốn nhẹ, pass ns-3 theo hồ sơ vận tốc | 156–157 | lịch sử |
| A2G | [`2026-10-24_1056-a2g-radius`](2026-10-24_1056-a2g-radius/) | bán kính phát hiệu quả theo môi trường | 158 | tham khảo (paper §III-B) |
| CHF | [`2026-10-24_1857-chord-fit`](2026-10-24_1857-chord-fit/) | CHORD trên cluster có sẵn, vừa đủ, thứ tự theo River | 159 | lịch sử |
| RDY | [`2026-10-25_0205-readiness`](2026-10-25_0205-readiness/) | rà soát trước chiến dịch số liệu | 160 | lịch sử |
| C3a | [`2026-10-25_0237-campaign`](2026-10-25_0237-campaign/) | script chiến dịch CHORD-T 120 bản đồ, chưa chạy | 161 | lịch sử |
| C3b | [`2026-10-25_0300-campaign`](2026-10-25_0300-campaign/) | đóng băng binary CAMP-BIN, chạy thử trên k2-s4, k8-s1 | 161 | lịch sử |
| ENVm | [`2026-10-25_0330-env-modes`](2026-10-25_0330-env-modes/) | ba chế độ kênh R50 ≈ 500/200/100 m | 163 | hiện hành (dùng trong paper) |
| — | [`2026-10-25_0500-chord-anim`](2026-10-25_0500-chord-anim/) | animation CHORD 8/12/16 cụm | 164 | tham khảo |
| FCB | [`2026-10-25_0600-fc-baseline`](2026-10-25_0600-fc-baseline/) | baseline FC và DN vs CHORD | 166–168 | bị thay thế bởi C4 |
| CHW | [`2026-10-25_0800-chord-win`](2026-10-25_0800-chord-win/) | vì sao CHORD thua, sửa cho thắng | 169 | lịch sử |
| LMT | [`2026-10-25_1500-lm-tour`](2026-10-25_1500-lm-tour/) | LM-Tour: bộ dự đoán River (A) và LM-Tour Python (C) | 171–175 | hiện hành (bộ dự đoán) |
| BL2 | [`2026-10-26_0900-baselines`](2026-10-26_0900-baselines/) | bảng chung CHORD + sáu baseline | 181–182 | bị thay thế bởi C4 |
| — | [`2026-10-26_1800-icc-v5`](2026-10-26_1800-icc-v5/) | khung Evaluation draft v5 (ước lượng) | 184 | bị thay thế |
| CVL | [`2026-10-27_1330-chord-plain-vs-lm`](2026-10-27_1330-chord-plain-vs-lm/) | CHORD thường vs LM-Tour, ns-3, k8-s1 | 186 | lịch sử |
| C4 | [`2026-10-27_1714-campaign4`](2026-10-27_1714-campaign4/) | chiến dịch 4: 4 phương án × 10 seed × 3 bản đồ × 4 kênh (dừng 290/360) | 187–210 | hiện hành (Bảng I–II, Hình 4) |
| LMD | [`2026-10-27_1800-lm-dtspn`](2026-10-27_1800-lm-dtspn/) | LM-Tour: DTSP-N qua CH rồi uốn về landmark | 187 | hiện hành (thuật toán LM-Tour) |
| DRC | [`2026-10-28_0240-dtspn-check`](2026-10-28_0240-dtspn-check/) | DTSP-N + River có zigzag không | 192 | hiện hành (paper §VI) |
| DRF | [`2026-10-28_0310-dtspn-fix`](2026-10-28_0310-dtspn-fix/) | sửa DTSP-N + River qua mọi critical cell | 193 | hiện hành |
| P1F | [`2026-10-28_0810-phase1-paths`](2026-10-28_0810-phase1-paths/) | hình đường bay pha 1, độ dài tour | 202, 204 | hiện hành (Hình 5) |
| T3S | [`2026-10-28_t3-surrogate`](2026-10-28_t3-surrogate/) | bộ dự đoán bằng cây so với công thức tuyến tính | — | hiện hành (paper §VI) |
| DLG | [`2026-10-30_1545-deluge-r100`](2026-10-30_1545-deluge-r100/) | River vs kéo trực tiếp vs Deluge trên pass CHORD, r100 | 227–249 | hiện hành (paper §VI) |
| DLL | [`2026-10-30_1730-deluge-lite`](2026-10-30_1730-deluge-lite/) | Deluge-lite trên LM-Tour, k12: River 16 lượt, dlb 2 lượt, tạm dừng | 233, 241 | dở |
| WND | [`2026-10-31_0000-wind`](2026-10-31_0000-wind/) | sai số quỹ đạo do gió, σ 50/100/200 m | 250–256 | hiện hành (paper §VI) |
| TKO | [`2026-11-01_0600-takeover`](2026-11-01_0600-takeover/) | River + takeover trên bảng sai số đường bay | 257–264 | hiện hành (paper §IV, §VI) |
| REORG | [`2026-11-06_0000-reorg`](2026-11-06_0000-reorg/) | tái tổ chức repo bước 4–8: nhãn tài liệu, archive, params.yaml, check.py | 273 | vận hành |
| `2026-11-10_1000-nd1-week1/` | ND1 tuần 1: mô hình, kiểm mô hình kênh và định lý A trên dữ liệu có sẵn |
| `2026-11-10_1400-nd1-day5/` | ND1 ngày 5 (thử nghiệm): bổ đề L1, kiểm mệnh đề B trên dữ liệu gió |
| `2026-11-12_0900-lit-search/` | 8 phiên tìm tài liệu song song cho kế hoạch sau ICC |
| `2026-11-12_1400-paper-notes/` | Ghi chú chi tiết bài báo: công cụ, phương pháp, 3 bài mẫu |
