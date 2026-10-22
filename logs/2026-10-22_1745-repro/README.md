# 2026-10-22 · Kiểm chứng môi trường mới bằng một bản đồ cũ

**Mục đích:** chắc rằng binary ns-3 vừa build và mã hiện tại cho đúng kết quả của chiến dịch 2026-10-20 (`logs/2026-10-20_1846-campaign2/`, bộ KW).

**Lệnh:** `kw-k2-s10.md` (mission.py, bản đồ k2-s10, River cửa sổ 400 kB, 88 s), `l1rank-k2-s10.md` (l1_rank.py, 100 lượt bốc).

**Kết quả:** tour đội 1 206 s, 11 critical cell, như cũ. T* trung bình trên 100 lượt khớp từng chữ số với `uav-l2/docs/data/l1rank/e1-draws.csv`: P* 376,8 s, không hợp tác 387,5 s, B1 734,1 s, B7 262,4 s. Môi trường tái tạo đúng.

**Thêm (thử pipeline mới trên k2-s10):** `mission.py --windowAt crit --schemes rf,d` (cửa sổ theo critical cell, River và kéo thẳng) chạy 60 s. `l1_rank.py` với phương án mới `Pd+prog` (River thay bằng kéo thẳng), 100 lượt bốc: P* + đổi hướng 373,3 s, kéo thẳng 373,0 s, không hợp tác 381,5 s. Thư mục thử: scratchpad `test/KC/k2-s10` (không commit).
