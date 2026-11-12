---
status: current
updated: 2026-11-12
---
# Danh mục ghi chú bài báo

Sinh tự động bởi `tools/papers/paper_index.py`; đừng sửa tay. Cách ghi chú: `../METHOD-vi.md`.

| Bài | Năm | Venue | DOI | Mức | Chủ đề | Tóm tắt một dòng |
|---|---|---|---|---|---|---|
| [isaacs2011-dtspn](isaacs2011-dtspn.md) | 2011 | American Control Conference (ACC), pp. 1704–1709 | 10.1109/ACC.2011.5991501 | ★★★ | dtspn, approx-bound, tsp-solver | Hai thuật toán cho Dubins TSP với lân cận (DTSPN): vùng rời nhau thì lấy một mẫu mỗi vùng cho hệ số xấp xỉ không phụ thuộc số vùng; vùng chồng nhau thì lấy mẫu rồi biến GTSP có nhóm chồng nhau sang ATSP (Noon–Bean), tour ngắn tới gần một nửa so với RCM. |
| [leny2012-dtsp](leny2012-dtsp.md) | 2012 | IEEE TAC 57(1):265–270 (technical note) | 10.1109/TAC.2011.2166311 | ★★★ | dtsp, np-hard, approx-bound, tsp-solver | Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP. |
| [zeng2018-multicast](zeng2018-multicast.md) | 2018 | IEEE TWC 17(4):2233–2246 | 10.1109/TWC.2018.2790401 | ★★★ | uav-multicast, coding, a2g-channel, tsp-solver, ground-coop | UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP. |
