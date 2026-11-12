---
status: current
updated: 2026-11-12
---
# Danh mục ghi chú bài báo

Sinh tự động bởi `tools/papers/paper_index.py`; đừng sửa tay. Cách ghi chú: `../METHOD-vi.md`.

| Bài | Năm | Venue | DOI | Mức | Chủ đề | Tóm tắt một dòng |
|---|---|---|---|---|---|---|
| [gallager1976-protocol](gallager1976-protocol.md) | 1976 | IEEE Trans. Information Theory IT-22(4):385–398 | 10.1109/TIT.1976.1055588 | ★★★ | control-overhead | Dùng lý thuyết rate–distortion chứng minh mỗi thông điệp cần ít nhất H(M) − log₂(1 − e^{−αd}) bit giao thức (thông tin độ dài + thông tin thời điểm bắt đầu, phụ thuộc chỉ vào tích αd), địa chỉ chỉ là một cách mã hoá thông tin thời điểm; hai chiến lược gom hàng đợi đạt gần cận khi số cặp nguồn–đích lớn. |
| [minsky2003-setrecon](minsky2003-setrecon.md) | 2003 | IEEE Trans. Information Theory 49(9):2213–2218 (correspondence) | 10.1109/TIT.2003.815784 | ★★★ | control-overhead, coding | Biểu diễn tập bằng đa thức đặc trưng, gửi giá trị tại m̄ điểm để nội suy hàm hữu tỉ χ_Δa/χ_Δb và tìm hiệu đối xứng; chi phí (m̄+1)(b+1)−1 bit, gần cận dưới thông tin mb − m lg m; bản không tương tác cho phép một bản tin quảng bá sửa cho nhiều client thiếu các tập khác nhau. |
| [hui2004-deluge](hui2004-deluge.md) | 2004 | ACM SenSys 2004, tr. 81–94 | 10.1145/1031495.1031506 | ★★★ | dissemination, control-overhead, testbed | Deluge phổ biến đối tượng dữ liệu lớn (ảnh chương trình) tới mọi nút WSN đa chặng bằng quảng bá kiểu Trickle, chia trang để pipeline, NACK chọn lọc; đạt ~90 B/s (1/9 tốc độ radio) trên 75 nút, gói điều khiển 18 %, và cho mô hình thời gian E[T_obj] = min(dn, d+3(n−1))·(E[T_page]+D). |
| [isaacs2011-dtspn](isaacs2011-dtspn.md) | 2011 | American Control Conference (ACC), pp. 1704–1709 | 10.1109/ACC.2011.5991501 | ★★★ | dtspn, approx-bound, tsp-solver | Hai thuật toán cho Dubins TSP với lân cận (DTSPN): vùng rời nhau thì lấy một mẫu mỗi vùng cho hệ số xấp xỉ không phụ thuộc số vùng; vùng chồng nhau thì lấy mẫu rồi biến GTSP có nhóm chồng nhau sang ATSP (Noon–Bean), tour ngắn tới gần một nửa so với RCM. |
| [leny2012-dtsp](leny2012-dtsp.md) | 2012 | IEEE TAC 57(1):265–270 (technical note) | 10.1109/TAC.2011.2166311 | ★★★ | dtsp, np-hard, approx-bound, tsp-solver | Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP. |
| [du2017-pando](du2017-pando.md) | 2017 | IEEE/ACM Trans. Networking 25(2), 2017 (bản accepted, đánh số trang 1–14; bản hội nghị SenSys 2015) | 10.1109/TNET.2016.2614707 | ★★★ | dissemination, coding, testbed | Pando phát luồng gói LT (fountain) liên tục qua cây pipeline dùng giao thoa xây dựng (Glossy) và đa kênh (PIP), giải mã xen trong khoảng rỗi CPU, dừng bằng phản hồi "im lặng" RSSI; đạt tin cậy 100 % và nhanh hơn Splash 3,5× (Indriya), nhanh hơn Deluge ~32,7×. |
| [zeng2018-multicast](zeng2018-multicast.md) | 2018 | IEEE TWC 17(4):2233–2246 | 10.1109/TWC.2018.2790401 | ★★★ | uav-multicast, coding, a2g-channel, tsp-solver, ground-coop | UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP. |
