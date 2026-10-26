# 2026-10-26 · Khung Evaluation cho draft v5 (CLAUDE.md §8 mục 184)
**Mục đích:** cập nhật Thuật toán 3 (ξ), bảng và hình mục Evaluation; không chạy thực nghiệm mới.
**Lệnh:** `estimate.md` (`paper/icc-v5/estimate.py`), `fig6.md` (`paper/icc-v5/fig_mission.py`).
**Đầu vào:** `uav-l2/docs/data/results/baselines.csv`, số River và tự giải mã của mục 182.
**Đầu ra:** `paper/icc-v5/` (xem README ở đó). Số LM-Tour là ước lượng (G = 0,5), chưa chạy.
**Dang dở:** chạy LM-Tour với `--xi auto` và quét ξ ∈ {100, 175, 250}, rồi ns-3 trên pass mới.
