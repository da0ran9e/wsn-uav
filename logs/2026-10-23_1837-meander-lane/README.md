# 2026-10-23 · MEANDER kiểu luống, so với CHORD-T cùng số cụm (CLAUDE.md §8 mục 146)

**Mục đích:** sửa MEANDER theo đính chính của người dùng: dựng theo luồng với đường bay kiểu luống, rồi uốn nhẹ để bám critical cell. Thử bằng Python trên k8-s1, so với CHORD-T cùng số cụm.

**Mã:**
- `uav-l2/tools/meander_lane.py` (mới): luồng 8 cell trên toạ độ cong của địa hình; một đường luống liên tục; cụm là các đoạn liên tiếp (≤ 190 cell, ≤ 14 cell dài); CH dưới đường bay; uốn cả luồng một lần (kéo về critical cell ngoài nửa độ rộng River, tối đa 1 cell; rồi qua CH).
- `mission_policy.py`: tour kiểu `route` (giữ thứ tự luống, nối liền khi đoạn này chạy tiếp vào đoạn kia).
- `iter_fig.py`, `kin_time.py`: hỗ trợ `route`; `kin_time.py` bỏ đoạn dẫn ra/dẫn vào tại chỗ nối liền.

**Lệnh:** `geometry-k8-s1.md`, `chordT-k9-geometry.md`, `kin-k8-s1.md`, `fig-k8-s1.md`.

**Kết quả (k8-s1, tour đội 1, giây):**

| | 50 m/s đều | nghiêng 45°, kể cả giao đủ | nghiêng 30°, kể cả giao đủ |
|---|---|---|---|
| CHORD-T 80 %, 9 cụm | 743 | 790 (+47, cả 9 cụm giảm tốc) | 854 |
| MEANDER kiểu luống, 9 cụm | 831 | 881 (+50, 5 cụm giảm tốc) | 930 |

- MEANDER kiểu luống: 4 luồng, 9 cụm (51–94 cell), đường luống 24,8 km; độ cong ≤ 1,12/ρ.
- Critical cell tới đường bay của cụm mình: CHORD-T TB 346 m (11/47 xa hơn 606 m); MEANDER 275 m (4/45).
- Uốn bám critical cell chỉ giúp ít (khoảng cách TB giảm 0–35 % theo cụm; có cụm tăng vì bướu qua CH): luồng rộng 8 cell, critical cell nằm cả hai phía đường bay.

**Dang dở:** chưa chạy ns-3 River và T\*; mới một bản đồ. `cmp-k8-s1-chordT-vs-meanderOpt.png` và bảng trong `logs/2026-10-23_17xx-chord-meander-kin/` là MEANDER cũ (hiểu sai), không dùng.
