# 2026-10-20 · Ba hướng sửa cho nhiệm vụ MEANDER (CLAUDE.md §8 mục 106)

**Mục đích:** chạy ns-3 ba hướng sửa của `uav-l2/docs/CURVE-vi.md` §3.4 trên ba bản đồ nhiệm vụ k4-s2, k6-s4, k8-s4.
1. Giới hạn chiều dài Axe.
2. Chỉ giao phần dữ liệu lớp 1 cần.
3. k-medoids với đường bay cong.

**Lệnh (chạy từ `uav-l2/`, log ghi bằng `tools/runlog.py`):**
- `geom-test-k4.md`: thử phần hình học của MEANDER span 12 và k-medoids + đường cong trên k4.
- `campaign.sh`: toàn bộ đợt chạy, 04:05–04:59.
  - `full-k{4,6,8}.md`: đầy đủ D.
    - k-medoids đường thẳng chạy lại (`mission.py`), trùng từng số với kết quả cũ.
    - k-medoids + đường cong (`meander_mission.py --partition kmedoids`).
    - MEANDER span 12 (`--span 12`).
  - `window-k{4,6,8}.md`: cửa sổ Q = 400 kB (`--windowKB 400`) cho cả năm cách chia, trên bản sao thư mục, dùng lại bitmap lượt bay.
- `compare.md`: `meander_compare.py`, 10 bộ × 3 bản đồ, 100 lần bốc nghi vấn.
- Tổng cộng 199 lượt River, 0 lỗi.

**Đầu vào:** scratchpad `MK, KC, ML, MM, MC` và các bản `…w` (`/tmp/claude-0/.../scratchpad/`, khoảng 85 MB mỗi bộ, không commit). Binary trong `/home/user/ns3-dev/build`, không dựng lại.

**Đầu ra:**
- `uav-l2/docs/data/meander/fixes-{summary,cells,draws}.csv`
- `uav-l2/docs/data/meander/works/<bộ>/k*/`: map, cluster, tour, deploy, đường cong, kết quả River.
- Hình: `uav-l2/docs/figures/fixes-{results,maps}.png`
- Báo cáo: `uav-l2/docs/CURVE-vi.md` Phần 4

**Kết quả chính:** thời điểm kết thúc nhiệm vụ P, k4 / k6 / k8.

| Cách chia | Kết thúc (s) |
|---|---|
| k-medoids (P gốc) | 734 / 866 / 906 |
| k-medoids + cửa sổ (tốt nhất) | 725 / 867 / 899 |
| k-medoids + đường cong | 772 / 929 / 965 (cửa sổ 740 / 915 / 955) |
| MEANDER | 867 / 999 / 1106 (cửa sổ 831 / 986 / 1062) |
| MEANDER span 12 | 788 / 969 / 1096 (cửa sổ 788 / 968 / 1079) |
| LANE | 764 / 1078 / 1044 (cửa sổ 760 / 1072 / 1034) |

- **Cửa sổ:** River nhanh hơn ở mọi cách chia, nhưng nhiệm vụ chỉ sớm hơn 0–44 s (khe LoRa và đội 2).
- **Span:** River nhanh, nhưng thêm cluster và phần lớn cluster nhận dưới 400 kB.
- **Đường cong cho k-medoids:** tour dài hơn, nên chậm hơn.
- **Thiếu dữ liệu:** với Q = 400 kB, ngay cả k-medoids có 1/4, 2/6, 4/8 cluster nhận dưới Q (cần khoảng 2 km Axe).

**Dang dở:**
- Số thăm dò: 3 bản đồ, N < 120.
- Span nên đo trên đường tâm luồng thay vì theo s.
- Q cần chốt cùng mô hình lớp 1.
