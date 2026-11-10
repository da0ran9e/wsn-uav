# 2026-11-10 · ND1 tuần 1: mô hình, kiểm mô hình kênh, kiểm định lý A (chatlog mục 301–302)

- **Mục đích:** làm tiến độ ngày 1–4 của ND1 (đề cương mục 7.2 và 9): chốt ký hiệu và giả định, kiểm mô hình kênh A2G
  và giả định A1 trên lượt bay ns-3, kiểm công thức của định lý A trên số đo chiến dịch C4. Không chạy ns-3 mới.
- **Lệnh:** `day2-channel.md` (`uav-l2/tools/theory/channel_check.py` trên lượt bay hiệu chỉnh `ENVCAL`),
  `day3-theorem-a.md` (`theorem_a.py`, p_k chỉ node CL), `day4-theorem-a-cell.md` (`theorem_a.py --cell`, p_k mức cell).
- **Đầu vào:** `ENVCAL` (scratchpad, lượt bay cụm 1 k8 ở 4 mức suy hao); `C4/CP` (scratchpad, kế hoạch và node các bản
  đồ C4); `uav-l2/docs/data/results/campaign4.csv`; `logs/2026-10-27_1714-campaign4/score/R*/*/score-ns3.csv`.
- **Đầu ra:** `paper/j1/MODEL-vi.md` (bản nháp mô hình hệ thống, giả định A1–A6, kết quả kiểm chứng);
  `uav-l2/docs/figures/theory/` (2 hình, có INDEX).
- **Kết quả chính:**
  - Một ngưỡng chung S = −101,04 dBm khớp p(d) của cả 4 môi trường, RMSE ≤ 0,003.
  - A1: tương quan nhỏ (chênh khoảng 0,05 giữa xác suất có điều kiện).
  - Định lý A với p_k mức cell là chặn dưới đúng ở 9/9 ô kênh xấu, nhưng còn lỏng (thấp hơn 26–59 %). Bản chỉ tính CL
    vượt số đo ở r100.
- **Dở dang:** đưa biên an toàn theo file và số gói nhận khi bay ngang vào định lý A; bổ đề L1 (ngày 5); mệnh đề B.
