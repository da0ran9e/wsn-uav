# 2026-10-26 · Khung Evaluation cho draft v5 (CLAUDE.md §8 mục 184)
**Mục đích:** cập nhật Thuật toán 3 (ξ), bảng và hình mục Evaluation; không chạy thực nghiệm mới.
**Lệnh:** `estimate.md` (`paper/icc-v5/estimate.py`), `fig6.md` (`paper/icc-v5/fig_mission.py`).
**Đầu vào:** `uav-l2/docs/data/results/baselines.csv`, số River và tự giải mã của mục 182.
**Đầu ra:** `paper/icc-v5/` (xem README ở đó). Số LM-Tour là ước lượng (G = 0,5), chưa chạy.
**Dang dở:** chạy LM-Tour với `--xi auto` và quét ξ ∈ {100, 175, 250}, rồi ns-3 trên pass mới.
**Mục 185:** `build-pdf.md` (`paper/icc-v5/build.sh`): trang 1–4 của v5 giữ nguyên, trang 5–7 dựng lại từ `tail.tex` (chữ xanh = thay đổi, [EST] đỏ = ước lượng). Đầu ra `paper/icc-v5/SigDrop_ICC_draft_v5-merged.pdf`, 7 trang. Fig. 4, 5 cắt từ trang 5 của v5 (`figs/fig4-*.png`, `figs/fig5-*.png`).
