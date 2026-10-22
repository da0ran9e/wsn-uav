# 2026-10-22 · MEANDER-K: kiểm tra hình học trên 40 bản đồ (CLAUDE.md §8 mục 118, 134)

**Mục đích:** so sánh lớp 2 công bằng với k-medoids: đúng K cụm (K = ceil(số cell / 80)), cỡ cụm đều.

**Mã:** `uav-l2/tools/meander.py` (`partition_meander(..., count=K)`: gộp mảnh thừa, chia cụm cho các mảnh theo D'Hondt, rồi `partition.rebalance` với trần 80 cell); `uav-l2/tools/meander_mission.py --meanderK` (thử bề rộng luồng 6, 5,5, 6,5, 5, 7, 4,5, 7,5, 8 cell, dừng ở bề rộng đầu tiên có hệ số biến thiên ≤ 0,11).

**Lệnh:** `mk_geom.py` (chỉ chia cụm, ra `partition.csv`); `job.sh` cho từng bản đồ (`meander_mission.py --meanderK --windowKB 400 --geometry`: chia cụm, deploy, đường cong; chưa chạy lượt bay và River), log `<bản đồ>.md`. Thư mục làm việc: scratchpad `MKW/`.

**Kết quả:** 40/40 thoát 0, đúng K cụm, mọi đường cong khả thi (độ cong ≤ 1/ρ).
| | k2 | k4 | k6 | k8 |
|---|---|---|---|---|
| hệ số biến thiên cỡ cụm, TB | 0,039 | 0,049 | 0,082 | 0,069 |
| bề rộng luồng | 6 (10/10) | 6 (9), 5,5 (1) | 6 (8), 5 (2) | 6 (7), 5,5 (2), 6,5 (1) |
| Axe ngắn nhất (km) | 1,67 | 1,65 | 1,34 | 1,70 |
Chỉ k6-s17 vượt 0,11 (0,125). k-medoids: 0,06–0,11 (`uav-l2/docs/L2-DIAG-vi.md` §7).

**Dang dở:** lượt bay và River (chờ duyệt chiến dịch).
