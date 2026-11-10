# 2026-11-10 · ND1 ngày 5 (thử nghiệm): bổ đề L1, kiểm mệnh đề B (chatlog mục 303)

- **Mục đích:** thử ngày 5 của ND1. Viết phác thảo chứng minh L1 và kiểm mệnh đề B trên dữ liệu gió có sẵn, không chạy
  mô phỏng mới. Kết quả ghi vào sổ thử nghiệm `paper/j1/ND1-TRIAL-vi.md`, không sửa đề cương.
- **Lệnh:** `prop-b.md` (`uav-l2/tools/theory/prop_b.py` trên `WIND` của `logs/2026-11-01_0600-takeover`).
- **Đầu vào:** scratchpad `WIND/s{50,100,200}/R*/k8-s1`: kế hoạch, node, gateway, quỹ đạo dự kiến, track và bit nhận.
- **Đầu ra:** `prop-b-cells.csv` (840 SPINE cell); `uav-l2/docs/figures/theory/nd1-prop-b-activation-vs-deviation.png`.
- **Kết quả chính:**
  - Mô hình kênh dự đoán đúng số lần kích hoạt: 2,0 / 18,2 / 51,7, so với đo 3 / 17 / 48.
  - Không có ngưỡng cứng; kích hoạt mà có cell khác giữ gói chỉ xuất hiện khi e ≥ 100 m.
  - Chặn hop ⌈e/(√3R)⌉ + 1 đúng ở 51/51 SPINE cell, chặt ở 9/51.
  - Ở σ = 200 m có một SPINE cell cần 4 hop.
- **Dở dang:** chặn trên P_a theo e; chứng minh chặn hop; thêm seed σ = 200 m (cần thảo luận trước khi chạy).
