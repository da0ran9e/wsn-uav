# 2026-10-20 · MEANDER trong cả nhiệm vụ, ns-3, bản đồ 4/6/8 cluster (CLAUDE.md §8 mục 104)

**Mục đích:** chạy MEANDER (luồng cong bám địa hình, mục 103) qua toàn bộ nhiệm vụ ns-3 trên ba bản đồ nhiệm vụ gốc. So với k‑medoids (đề xuất gốc) và LANE 4,5 (đề xuất lớp 2 cũ, mục 84, chưa từng chạy ns-3).

**Lệnh (chạy từ `uav-l2/`):**
- `geom-k{4,6,8}.cmd/.log`: các giai đoạn hình học của `meander_mission.py --geometry` (bản đồ, deploy, đường cong qua CH). Chạy lại sau hai lần sửa đường cong; log là lần cuối.
- `run.cmd` / `run.log`: MEANDER k4, k6, k8, rồi LANE k4, k6, k8 (`mission.py --partition lane`).
  - Lượt bay + River chuẩn bị, 3 job, 02:28–02:57.
- `ablation.cmd` / `ablation.log`: MEANDER với Bank song song. Copy thư mục MEANDER, xoá plan và kết quả River, dùng lại bitmap lượt bay.
- `compare.cmd` / `compare.log`: `meander_compare.py`, ba cách chia, 100 lần bốc nghi vấn mỗi bản đồ.
- `ablation-compare.cmd` / `.log`: so Bank cục bộ với Bank song song.
- `bendfig.cmd` / `.log`: hình uốn đường qua CH.

**Đầu vào:**
- Bản đồ `restructure.domain(K, seed)`, seed 2/4/4, giống `mission.py`.
- k‑medoids: thư mục dựng lại bằng regeom trong scratchpad `W/k{4,6,8}`. Kết quả ns-3 ngày 13/10, cùng các binary.
- Binary: `deploy-bin`, `pass-bin`, `river-bin` trong `/home/user/ns3-dev/build` (không dựng lại).

**Đầu ra:**
- `uav-l2/docs/data/meander/ns3-{summary,cells,draws}.csv`
- `uav-l2/docs/data/meander/works/{meander,lane,meanderParallel}/k*/`: map, cluster, tour, deploy, đường cong, kết quả River; không có plan và bitmap.
- Hình: `uav-l2/docs/figures/meander-ns3-maps.png`, `meander-ns3-results.png`, `meander-bend-ch.png`
- Báo cáo: `uav-l2/docs/CURVE-vi.md` Phần 3
- Dữ liệu thô (scratchpad, không commit, khoảng 83 MB mỗi bộ): `MM/k*`, `ML/k*`, `MMp/k*`, gồm bitmap lượt bay, plan và log ns-3 từng cluster.

**Kết quả chính:**
- **Thời điểm kết thúc nhiệm vụ P (giây), k4 / k6 / k8:**
  - k‑medoids: 734 / 866 / 906 — sớm nhất trên cả ba bản đồ.
  - LANE: 764 / 1078 / 1044.
  - MEANDER: 867 / 999 / 1106.
- **Nguyên nhân:**
  1. Đội 1 bay thêm 155–255 s, vì luồng phủ kín miền.
  2. River chậm ở cluster có Axe dài. Thời gian tương quan Spearman 0,73 với chiều dài Axe và 0,84 với D. 36 % cluster MEANDER có Axe ≥ 20 cell.
- **Bank cục bộ và Bank song song cho kết quả như nhau.**
- **Sửa mã đi kèm:**
  - `river_plan` có thêm `reentry` (đường cong đi qua một cell hai lần).
  - Kẹp chỉ số trong nhánh `banks="local"`.
  - Uốn đường MEANDER qua CH: 28/28 khả thi, 1 cluster cần nới σ ×3.

**Dang dở:**
- Số thăm dò: 3 bản đồ, mỗi cluster 1 lượt, N < 120.
- Hướng sửa (Phần 3.4) chờ bàn với người dùng:
  1. Giới hạn chiều dài Axe.
  2. Chỉ giao cho cluster phần dữ liệu mà lớp 1 cần.
  3. k‑medoids với đường cong.
