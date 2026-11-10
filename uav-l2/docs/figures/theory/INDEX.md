# Hình kiểm chứng lý thuyết (ND1)

Ảnh không chữ (quy tắc mục 63). Log và bảng số: `logs/2026-11-10_1000-nd1-week1/`; bản nháp mô hình: `paper/j1/MODEL-vi.md`.

| Tệp | Mô tả | Lệnh | Tham số | Ngày | Commit |
|---|---|---|---|---|---|
| `nd1-channel-p-of-d-model-vs-ns3.png` | xác suất nhận gói theo khoảng cách ngang 0–1,5 km, bốn màu là bốn mức kênh (open, r500, r200, r100): chấm là đo từ lượt bay ns-3, đường liền là mô hình hai đoạn + Rician K = 2 với một ngưỡng chung S = −101,04 dBm | `uav-l2/tools/theory/channel_check.py` | lượt bay hiệu chỉnh `ENVCAL` (cụm 1, k8), bin 10 m | 2026-11-10 | xem git log |
| `nd1-theorem-a-ratio-vs-r50.png` | tỉ số T_FC/T_River theo R50 (hai trục log, 4 mức kênh), ba màu là ba bản đồ (k8 xanh, k12 cam, k16 lục): chấm là số đo C4, đường liền là chặn dưới của định lý A với xác suất nhận mức cell, đường đứt là bản chỉ tính node CL, đường chấm ngang là tỉ số 1 | `uav-l2/tools/theory/theorem_a.py` (`--cell` cho đường liền) | C4 seed 1–10, nhóm bán kính 300 m | 2026-11-10 | xem git log |
| `nd1-prop-b-activation-vs-deviation.png` | tỉ lệ kích hoạt takeover theo độ lệch ngang e của SPINE cell (0–700 m): chấm xám là xác suất mô hình của từng SPINE cell, đường đỏ là tỉ lệ đo theo khoảng e, đường xanh đứt là tỉ lệ mô hình | `uav-l2/tools/theory/prop_b.py` | lượt bay gió k8-s1 r100, σ 50×3, 100×3, 200×1 seed, 840 SPINE cell | 2026-11-10 | xem git log |
