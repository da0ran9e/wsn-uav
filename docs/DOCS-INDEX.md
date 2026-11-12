# Chỉ mục tài liệu

Sinh bằng `python3 tools/build_index.py` từ phần đầu (front matter) của mỗi tài liệu; không sửa tay.
Thí nghiệm: `docs/EXPERIMENTS-INDEX.md`. Log: `logs/INDEX.md`. Chat log: `docs/chatlog/INDEX.md`.
Module `uav-sar/`, `uav-coop/`, `uav-coop2/` có README và tài liệu riêng (xem bản đồ trong `CLAUDE.md`).

## Hiện hành (13): nguồn số liệu và mô tả đang dùng

| Tệp | Tiêu đề | Cập nhật | Thay bằng |
|---|---|---|---|
| [`docs/progress/HANDOFF.md`](progress/HANDOFF.md) | Handoff · 2026-10-22 (cập nhật 2026-10-29) | 2026-10-28 |  |
| [`paper/EXPERIMENTS-vi.md`](../paper/EXPERIMENTS-vi.md) | Thực nghiệm, baseline và kết quả | 2026-10-29 |  |
| [`paper/LMTOUR-vi.md`](../paper/LMTOUR-vi.md) | LM-Tour: ý tưởng, thuật toán, bộ dự đoán và kết quả | 2026-10-29 |  |
| [`paper/PARAMS-vi.md`](../paper/PARAMS-vi.md) | Bảng tham số toàn bộ giả lập, để kiểm tra nguồn (CLAUDE.md §8 mục 152) | 2026-10-24 |  |
| [`paper/SIM-REPORT-2026-10-31-vi.md`](../paper/SIM-REPORT-2026-10-31-vi.md) | Báo cáo giả lập 30–31/10/2026: vận chuyển mặt đất trên pass CHORD cố định và sai số quỹ đạo | 2026-10-31 |  |
| [`paper/SIM-REPORT-2026-11-01-takeover-vi.md`](../paper/SIM-REPORT-2026-11-01-takeover-vi.md) | Báo cáo mô phỏng 2026-11-01: cơ chế takeover (dấu ranh giới) cho River khi đường bay lệch | 2026-11-01 |  |
| [`paper/TECHREPORT-vi.md`](../paper/TECHREPORT-vi.md) | Technical report: SigDrop, chiến dịch 4 (CHORD, LM-Tour, DTSP-N + River, FC + DTSP-N) | 2026-10-29 |  |
| [`paper/j1/MODEL-vi.md`](../paper/j1/MODEL-vi.md) | J1 · Mô hình hệ thống (bản nháp, ND1 tuần 1) | 2026-11-10 |  |
| [`paper/j1/ND1-TRIAL-vi.md`](../paper/j1/ND1-TRIAL-vi.md) | ND1 · Sổ thử nghiệm | 2026-11-10 |  |
| [`research_notes/proposal/SIGDROP-PROPOSAL-vi.md`](../research_notes/proposal/SIGDROP-PROPOSAL-vi.md) | Đề cương nghiên cứu SigDrop (bản nháp) | 2026-11-06 |  |
| [`uav-l2/docs/ENERGY-vi.md`](../uav-l2/docs/ENERGY-vi.md) | Mô hình năng lượng cho bảng "Ground transport on fixed CHORD passes" (CLAUDE.md §8 mục 227, phần 3) | 2026-10-30 |  |
| [`uav-l2/docs/PIPELINE-vi.md`](../uav-l2/docs/PIPELINE-vi.md) | Luồng thực thi của mô phỏng ns-3 (một nhiệm vụ pha 1) | 2026-11-09 |  |
| [`uav-l2/docs/RESULTS-vi.md`](../uav-l2/docs/RESULTS-vi.md) | Kết quả CHORD và các baseline, kèm seed để chạy lại (CLAUDE.md §8 mục 166–169, 182) | 2026-10-28 |  |

## Tham khảo (19): còn đúng, dùng để tra cứu nền

| Tệp | Tiêu đề | Cập nhật | Thay bằng |
|---|---|---|---|
| [`paper/L1-MODEL-vi.md`](../paper/L1-MODEL-vi.md) | Lớp 1: đối sánh truy vấn tại nút xử lý — mô hình hệ thống | 2026-10-21 |  |
| [`paper/L1-STATEMENT-vi.md`](../paper/L1-STATEMENT-vi.md) | Lớp 1: phát biểu chi tiết, khớp với các công bố | 2026-10-20 |  |
| [`paper/L3-TECHREPORT-vi.md`](../paper/L3-TECHREPORT-vi.md) | River: hợp tác mặt đất có lập kế hoạch sau một lượt bay UAV | 2026-10-22 |  |
| [`paper/RIVER-L3-vi.md`](../paper/RIVER-L3-vi.md) | River: cơ chế lớp 3 | 2026-10-22 |  |
| [`paper/icc-v5/README.md`](../paper/icc-v5/README.md) | Draft v5: Algorithm 3 and Evaluation (CLAUDE.md §8 item 184) | 2026-10-26 |  |
| [`reports/l1-edge-recognition.md`](../reports/l1-edge-recognition.md) | Lớp 1: tính đúng số false alarm trước khi tính bit | 2026-10-15 |  |
| [`reports/l1-signature-matching.md`](../reports/l1-signature-matching.md) | Ống kính, không phải con chip, làm lệch điểm khớp | 2026-10-18 |  |
| [`research_notes/l1-edge-recognition/edge_devices.md`](../research_notes/l1-edge-recognition/edge_devices.md) | Edge camera device compute capabilities and feasible recognition pipelines (Layer 1 node tiers) | 2026-10-15 |  |
| [`research_notes/l1-edge-recognition/partial_set_thresholds.md`](../research_notes/l1-edge-recognition/partial_set_thresholds.md) | Recall/precision with a partial reference set, and how to set match thresholds at the edge node | 2026-10-15 |  |
| [`research_notes/l1-edge-recognition/representation_bits.md`](../research_notes/l1-edge-recognition/representation_bits.md) | Transmitted unit and size of a recognition signature, and the bits needed to keep false alarms low | 2026-10-15 |  |
| [`research_notes/l1-edge-recognition/signatures_coarse_fine.md`](../research_notes/l1-edge-recognition/signatures_coarse_fine.md) | Signatures per target and coarse-to-fine query organisation (Q5 and Q9) | 2026-10-15 |  |
| [`research_notes/l1-edge-recognition/task_and_modality.md`](../research_notes/l1-edge-recognition/task_and_modality.md) | Recognition task and target modality for an edge camera node receiving a compact query (Layer 1) | 2026-10-15 |  |
| [`research_notes/l1-signature-matching/coarse_to_full.md`](../research_notes/l1-signature-matching/coarse_to_full.md) | Two-stage search: light signature (coarse filter) → full reference data (confirmation) — how accurate is each stage | 2026-10-18 |  |
| [`research_notes/l1-signature-matching/cross_device_scores.md`](../research_notes/l1-signature-matching/cross_device_scores.md) | Cross-device match-score variation: same recognition model, same reference signatures, different edge devices | 2026-10-18 |  |
| [`research_notes/l1-signature-matching/partial_signatures.md`](../research_notes/l1-signature-matching/partial_signatures.md) | Partial signature sets: how accuracy drops when a node holds 4/5 or 3/5 reference files | 2026-10-18 |  |
| [`research_notes/l1-signature-matching/score_threshold.md`](../research_notes/l1-signature-matching/score_threshold.md) | What a "70–90 % match score" means, and how a fixed YES/NO threshold behaves (persons, vehicles, animals) | 2026-10-18 |  |
| [`uav-l2/docs/ANIM-vi.md`](../uav-l2/docs/ANIM-vi.md) | Các animation (không chữ trên bản đồ) | 2026-10-25 |  |
| [`uav-l2/docs/FLIGHTLINE-vi.md`](../uav-l2/docs/FLIGHTLINE-vi.md) | Chọn đường bay qua mỗi cluster (FlightLine) | 2026-10-15 |  |
| [`uav-l2/docs/SAT-vi.md`](../uav-l2/docs/SAT-vi.md) | Ngưỡng bão hoà và điểm tối ưu theo hình dạng cụm | 2026-10-21 |  |

## Bị thay thế (13): đã có bản mới hơn (cột cuối)

| Tệp | Tiêu đề | Cập nhật | Thay bằng |
|---|---|---|---|
| [`paper/OVERVIEW-vi.md`](../paper/OVERVIEW-vi.md) | Tổng quan nghiên cứu River | 2026-10-21 | paper/TECHREPORT-vi.md |
| [`paper/SUMMARY-vi.md`](../paper/SUMMARY-vi.md) | Tổng hợp nghiên cứu: giao truy vấn tìm kiếm bằng một lượt bay UAV cánh bằng và hợp tác mặt đất có lập kế hoạch | 2026-10-26 | paper/TECHREPORT-vi.md |
| [`paper/archive/BASELINES-vi.md`](../paper/archive/BASELINES-vi.md) | Baseline và ablation — keyword | 2026-10-23 | paper/EXPERIMENTS-vi.md |
| [`paper/archive/INTRO-vi.md`](../paper/archive/INTRO-vi.md) | Introduction — keyword | 2026-10-20 | bản nộp ICC v5.3 |
| [`paper/archive/L1-VECTOR-vi.md`](../paper/archive/L1-VECTOR-vi.md) | Lớp 1 bằng điểm cosine của từng ảnh (CLAUDE.md §8 mục 110) | 2026-10-20 | paper/L1-MODEL-vi.md |
| [`paper/archive/L2-PARTITION-vi.md`](../paper/archive/L2-PARTITION-vi.md) | Lớp 2: phân vùng MEANDER | 2026-10-22 | paper/LMTOUR-vi.md |
| [`paper/archive/MEMO-2026-10-19-L1-vi.md`](../paper/archive/MEMO-2026-10-19-L1-vi.md) | Mốc ghi nhớ 2026-10-19: lớp 1 chốt và rà soát nguồn tham số | 2026-10-19 | paper/L1-MODEL-vi.md |
| [`paper/archive/OUTLINE-vi.md`](../paper/archive/OUTLINE-vi.md) | Khung paper (bản 1) — đại ý từng phần | 2026-10-20 | bản nộp ICC v5.3 |
| [`paper/archive/RELATED-vi.md`](../paper/archive/RELATED-vi.md) | Related Work — keyword | 2026-10-15 | bản nộp ICC v5.3 |
| [`paper/archive/REST-vi.md`](../paper/archive/REST-vi.md) | Các phần còn lại — keyword | 2026-10-20 | bản nộp ICC v5.3 |
| [`paper/archive/RIVER-vi.md`](../paper/archive/RIVER-vi.md) | River — keyword | 2026-10-15 | paper/RIVER-L3-vi.md |
| [`paper/archive/SYSTEM-vi.md`](../paper/archive/SYSTEM-vi.md) | System Model — keyword | 2026-10-20 | bản nộp ICC v5.3 |
| [`uav-l2/docs/PARAM-SOURCES-vi.md`](../uav-l2/docs/PARAM-SOURCES-vi.md) | Rà soát nguồn gốc tham số giả lập (CLAUDE.md §8 mục 102) | 2026-10-19 | paper/PARAMS-vi.md |

## Lịch sử (13): thử nghiệm hoặc hướng đã đóng, giữ để tra lại

| Tệp | Tiêu đề | Cập nhật | Thay bằng |
|---|---|---|---|
| [`uav-l2/docs/CLUSTER-C3-vi.md`](../uav-l2/docs/CLUSTER-C3-vi.md) | C3 (cluster vàng) — River từng bước, lượt 1 | 2026-10-13 |  |
| [`uav-l2/docs/CLUSTER-RIVER-vi.md`](../uav-l2/docs/CLUSTER-RIVER-vi.md) | River trên các cluster của miền có hồ — lượt 1 | 2026-10-13 |  |
| [`uav-l2/docs/CURVE-vi.md`](../uav-l2/docs/CURVE-vi.md) | Axe cong: Bank theo pháp tuyến cục bộ, và MEANDER (cluster bám địa hình, bay đường cong) | 2026-10-20 |  |
| [`uav-l2/docs/L1-HOOKS-vi.md`](../uav-l2/docs/L1-HOOKS-vi.md) | Lớp 1 chạm vào giả lập ở đâu | 2026-10-16 |  |
| [`uav-l2/docs/L1-MISSION-vi.md`](../uav-l2/docs/L1-MISSION-vi.md) | Nhiệm vụ P với mô hình đối sánh lớp 1 (tham số M, L, F, f, k) | 2026-10-19 |  |
| [`uav-l2/docs/L1-MISSION2-vi.md`](../uav-l2/docs/L1-MISSION2-vi.md) | Nhiệm vụ trọn vẹn với mô hình lớp 1 mới: đề xuất, ablation, baseline | 2026-10-20 |  |
| [`uav-l2/docs/L1-PARAMS-vi.md`](../uav-l2/docs/L1-PARAMS-vi.md) | Lớp 1: câu hỏi nghiên cứu và tham số đang dùng trong giả lập | 2026-10-17 |  |
| [`uav-l2/docs/L2-DIAG-vi.md`](../uav-l2/docs/L2-DIAG-vi.md) | Vì sao lớp 2 đề xuất (MEANDER) chưa thắng cluster có sẵn | 2026-10-21 |  |
| [`uav-l2/docs/MAP-vi.md`](../uav-l2/docs/MAP-vi.md) | Tầng 2 — bước 1: miền bay | 2026-10-13 |  |
| [`uav-l2/docs/MISSION-vi.md`](../uav-l2/docs/MISSION-vi.md) | Giả lập trọn nhiệm vụ Pha 1 — từ bản đồ tới khi đội 2 về BS | 2026-10-14 |  |
| [`uav-l2/docs/PROPOSE-ITER-vi.md`](../uav-l2/docs/PROPOSE-ITER-vi.md) | Chốt propose lớp 2: các vòng thử ngày 2026-10-22 | 2026-10-22 |  |
| [`uav-l2/docs/RESTRUCTURE-vi.md`](../uav-l2/docs/RESTRUCTURE-vi.md) | Tái cấu trúc cluster trước nhiệm vụ: chia theo luồng (LANE) | 2026-10-17 |  |
| [`uav-l2/docs/SWATH-vi.md`](../uav-l2/docs/SWATH-vi.md) | SWATH-K: lớp 2 bằng một đường luống liền | 2026-10-22 |  |
