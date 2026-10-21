# 2026-10-21 · Thử điều chỉnh MEANDER và thêm động học đội 1 (CLAUDE.md §8 mục 116–117)

**Mục đích:** trước khi thiết kế lại lớp 2, thử vài cách điều chỉnh MEANDER hiện tại (mục 116). Sau đó thêm động học cho đội 1: bán kính quay tối thiểu ở các quãng nối (mục 117). Báo cáo: `uav-l2/docs/L2-DIAG-vi.md` §6 (§7 là phần công bằng, mục 118).

**Lệnh (chạy từ `uav-l2/`, log `.md` ghi bằng `tools/runlog.py`):**
- `screen.md`: `tools/l2_lanes.py`, chỉ hình học, quét luồng 4,5 / 6 / 7,5 / 9 cell × gộp mảnh 0,25 / 0,5 (sàng lọc nhanh).
- `seam.sh` → `seam.md`: tour `seam`, bay nối liền hai cluster thẳng hàng. Dùng lại các lần chạy ns‑3 cũ (KW, MW), 40 bản đồ × 100 lượt bốc.
- `geo.sh`, `geo-one.sh` → `geo.md`, `geo-L6f0.5.md`: `meander_mission.py --geometry` (bản đồ, deploy, đường cong thật, không ns‑3) cho 8 cấu hình.
  - `geo.md` thoát 125. Tôi đã dừng nhầm xargs (`pkill`), nên phải chạy lại hai cấu hình bằng tay.
  - `geo-L7.5f0.5.txt` và `geo-L9f0.5.txt` là log in ra trực tiếp, không qua runlog.
  - L4.5f0.5 bỏ dở ở 27/40 bản đồ và không dùng.
- `geo-diag1.md`, `geo-diag2.md`, `geo-diag3.md`: `tools/l2_diag.py --geometry` trên các cấu hình đó.
- `kin.sh` → `kin.md`: tour `kin` (quãng nối Dubins, bán kính 255 m) cho KW, MW, SW trên các lần chạy ns‑3 cũ.
- `ns3.sh` → `ns3/<bản đồ>.md`, `ns3/done.txt`: ns‑3 đầy đủ (pass, River, cửa sổ 400 kB) cho luồng 7,5 cell, gộp < 1/2, trên 40 bản đồ. Bản đồ nào cũng thoát 0, xong lúc 05:53.
- `eval.sh` → `eval.md`: `l1_rank.py` (P\*, B4, P\* đổi hướng, B7, P\* và B4 với tour `kin`) và `l1_compare.py`, ghép cặp với E1 và E2.
  - Lần đầu, eval được treo chờ ns‑3 xong. Tiến trình chờ đó hết giới hạn thời gian đúng lúc ns‑3 xong, nên eval chưa chạy.
  - Eval được chạy lại bằng tay.

**Đầu vào:** các thư mục trong scratchpad của phiên:
- KW, MW, SW: chiến dịch `logs/2026-10-20_1846-campaign2/`.
- `MG/L*f*`: hình học, khoảng 100 MB mỗi cấu hình.
- `MG/L7.5f0.5`: có ns‑3, 833 MB. Không commit.

**Đầu ra:** `uav-l2/docs/data/l2diag/{screen,seam-*,geo1,geo2,geo3,kin-*,adj-*}.csv`. Mã mới: `tools/dubins.py`, `mission_policy.seams`, `mission_policy.kin_links`, `meander.partition_meander(frag_share)`, `meander_mission.py --frag`.

**Kết quả chính (T\* của P\*, s, k2 / k4 / k6 / k8, 10 bản đồ mỗi cỡ, mang tính thăm dò):**
- Bay nối liền: không có lợi (MEANDER k8: 919 → 916 s).
- Luồng 7,5 cell, gộp < 1/2, nối thẳng: 464 / 608 / 722 / 860. So với MEANDER gốc 470 / 642 / 792 / 919 và k‑medoids 408 / 566 / 675 / 769.
- Nối Dubins:
  - k‑medoids 420 / 586 / 716 / 824;
  - MEANDER gốc 487 / 679 / 845 / 987;
  - MEANDER đã chỉnh 479 / 634 / 770 / 921.
  - Khoảng cách tới k‑medoids giảm còn khoảng một nửa, nhưng k‑medoids vẫn thắng ở mọi cỡ: MEANDER đã chỉnh thắng 0–2 bản đồ trên 10.
- Cận dưới B7 bằng nhau ở hai cách chia. Phần chênh nằm ở tour dài hơn và nhiều critical cell hơn.

**Dang dở:** so sánh chưa công bằng theo mục 118. MEANDER và subCH có nhiều cluster nhỏ hơn và cỡ không đều (`L2-DIAG-vi.md` §7). Đã đề xuất MEANDER‑K và subCH‑K (đúng K cluster, cỡ khoảng số cell/K), đang chờ người dùng duyệt trước khi cài và chạy ns‑3.
