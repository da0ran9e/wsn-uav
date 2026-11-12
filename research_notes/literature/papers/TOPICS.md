---
status: current
updated: 2026-11-12
---
# Chủ đề → bài

Sinh tự động bởi `tools/papers/paper_index.py`. Mỗi dòng: bài, mức liên quan, tóm tắt một dòng. Tìm số liệu hay định lý cụ thể: `grep -n "\[SỐ\]\|\[KQ\]" *.md`.


## `dtsp` · Dubins TSP và biến thể

- [leny2012-dtsp](leny2012-dtsp.md) ★★★ · Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP.
- [savla2008-dtsp](savla2008-dtsp.md) ★★★ · Ba kết quả cho DTSP: (1) trường hợp xấu nhất độ dài tour tăng tuyến tính theo n, ALTERNATING ALGORITHM (giữ thứ tự ETSP, bỏ xen kẽ cạnh) xấp xỉ hằng số khi khoảng cách điểm bị chặn dưới, kèm cận điểm–điểm D ≤ E + κπρ; (2) điểm ngẫu nhiên đều: tour cỡ n^{2/3}, RECURSIVE BEAD-TILING đạt hằng số với xác suất 1; (3) DTRP: thời gian hệ thống cỡ λ² (Euclid chỉ cỡ λ).
- [babel2017-obstacles](babel2017-obstacles.md) ★★ · Đặt bài toán CTSPO (DTSP + tránh chướng ngại), dùng mạng "Mikado" (đường thẳng ngẫu nhiên nối bằng clothoid) để tìm đường bay được, tối ưu hướng bay qua bằng đồ thị phụ p hướng/điểm và đường ngắn nhất, dựng tour bằng chèn dần (NEARIN, FARIN, RANDIN, CHEAPIN); kèm câu "DTSP-N NP-khó vì khi vùng co về điểm thì về DTSP".

## `dtspn` · Dubins TSP với lân cận

- [isaacs2011-dtspn](isaacs2011-dtspn.md) ★★★ · Hai thuật toán cho Dubins TSP với lân cận (DTSPN): vùng rời nhau thì lấy một mẫu mỗi vùng cho hệ số xấp xỉ không phụ thuộc số vùng; vùng chồng nhau thì lấy mẫu rồi biến GTSP có nhóm chồng nhau sang ATSP (Noon–Bean), tour ngắn tới gần một nửa so với RCM.
- [babel2017-obstacles](babel2017-obstacles.md) ★★ · Đặt bài toán CTSPO (DTSP + tránh chướng ngại), dùng mạng "Mikado" (đường thẳng ngẫu nhiên nối bằng clothoid) để tìm đường bay được, tối ưu hướng bay qua bằng đồ thị phụ p hướng/điểm và đường ngắn nhất, dựng tour bằng chèn dần (NEARIN, FARIN, RANDIN, CHEAPIN); kèm câu "DTSP-N NP-khó vì khi vùng co về điểm thì về DTSP".

## `np-hard` · kết quả về độ khó

- [leny2012-dtsp](leny2012-dtsp.md) ★★★ · Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP.
- [babel2017-obstacles](babel2017-obstacles.md) ★★ · Đặt bài toán CTSPO (DTSP + tránh chướng ngại), dùng mạng "Mikado" (đường thẳng ngẫu nhiên nối bằng clothoid) để tìm đường bay được, tối ưu hướng bay qua bằng đồ thị phụ p hướng/điểm và đường ngắn nhất, dựng tour bằng chèn dần (NEARIN, FARIN, RANDIN, CHEAPIN); kèm câu "DTSP-N NP-khó vì khi vùng co về điểm thì về DTSP".

## `approx-bound` · hệ số xấp xỉ, cận trên và cận dưới của tour

- [isaacs2011-dtspn](isaacs2011-dtspn.md) ★★★ · Hai thuật toán cho Dubins TSP với lân cận (DTSPN): vùng rời nhau thì lấy một mẫu mỗi vùng cho hệ số xấp xỉ không phụ thuộc số vùng; vùng chồng nhau thì lấy mẫu rồi biến GTSP có nhóm chồng nhau sang ATSP (Noon–Bean), tour ngắn tới gần một nửa so với RCM.
- [leny2012-dtsp](leny2012-dtsp.md) ★★★ · Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP.
- [savla2008-dtsp](savla2008-dtsp.md) ★★★ · Ba kết quả cho DTSP: (1) trường hợp xấu nhất độ dài tour tăng tuyến tính theo n, ALTERNATING ALGORITHM (giữ thứ tự ETSP, bỏ xen kẽ cạnh) xấp xỉ hằng số khi khoảng cách điểm bị chặn dưới, kèm cận điểm–điểm D ≤ E + κπρ; (2) điểm ngẫu nhiên đều: tour cỡ n^{2/3}, RECURSIVE BEAD-TILING đạt hằng số với xác suất 1; (3) DTRP: thời gian hệ thống cỡ λ² (Euclid chỉ cỡ λ).

## `tsp-solver` · bộ giải TSP, biến đổi GTSP sang ATSP

- [isaacs2011-dtspn](isaacs2011-dtspn.md) ★★★ · Hai thuật toán cho Dubins TSP với lân cận (DTSPN): vùng rời nhau thì lấy một mẫu mỗi vùng cho hệ số xấp xỉ không phụ thuộc số vùng; vùng chồng nhau thì lấy mẫu rồi biến GTSP có nhóm chồng nhau sang ATSP (Noon–Bean), tour ngắn tới gần một nửa so với RCM.
- [leny2012-dtsp](leny2012-dtsp.md) ★★★ · Chứng minh Dubins TSP (tour và path) NP-khó bằng phép quy từ TSP Euclid có phóng to; chỉ ra heuristic theo thứ tự Euclid kém tối ưu cỡ Ω(n); đề xuất thuật toán rời rạc hoá hướng qua GTSP → ATSP.
- [zeng2018-multicast](zeng2018-multicast.md) ★★★ · UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP.
- [babel2017-obstacles](babel2017-obstacles.md) ★★ · Đặt bài toán CTSPO (DTSP + tránh chướng ngại), dùng mạng "Mikado" (đường thẳng ngẫu nhiên nối bằng clothoid) để tìm đường bay được, tối ưu hướng bay qua bằng đồ thị phụ p hướng/điểm và đường ngắn nhất, dựng tour bằng chèn dần (NEARIN, FARIN, RANDIN, CHEAPIN); kèm câu "DTSP-N NP-khó vì khi vùng co về điểm thì về DTSP".

## `uav-multicast` · UAV phát dữ liệu chung xuống mặt đất

- [zeng2018-multicast](zeng2018-multicast.md) ★★★ · UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP.

## `uav-coverage` · phủ vùng, đặt vị trí UAV làm trạm gốc

- [alhourani2014-lap](alhourani2014-lap.md) ★★★ · Mô hình suy hao không–đất trung bình = FSPL + η theo nhóm LoS/NLoS, xác suất LoS theo góc ngẩng xấp xỉ bằng hàm S P(LoS, θ) = 1/(1 + a·exp(−b(θ − a))) với a, b khớp theo tham số đô thị ITU (α, β, γ); bán kính phủ R(h) có cực đại, góc ngẩng tối ưu θ_OPT không phụ thuộc PL_max.

## `ground-coop` · hợp tác mặt đất sau khi UAV phát (D2D, chuyển tiếp)

- [stojanovic2009-nccoop](stojanovic2009-nccoop.md) ★★★ · Trạm gốc phát tệp K gói cho N máy thu qua kênh on/off độc lập (xác suất mất p_e): round-robin tốn K·log_{1/p_e}N; RLC tốn log_{1/p_e}N khi K cố định nhưng ≈ (1 + 1/log(1/p_e))K khi K ≳ (log N)^r; hợp tác hai giai đoạn với M = (log N)^r nút chuyển tiếp đạt 2K(1 + o(1)) với mọi K.
- [zeng2018-multicast](zeng2018-multicast.md) ★★★ · UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP.

## `dissemination` · phổ biến dữ liệu và mã trong WSN

- [du2017-pando](du2017-pando.md) ★★★ · Pando phát luồng gói LT (fountain) liên tục qua cây pipeline dùng giao thoa xây dựng (Glossy) và đa kênh (PIP), giải mã xen trong khoảng rỗi CPU, dừng bằng phản hồi "im lặng" RSSI; đạt tin cậy 100 % và nhanh hơn Splash 3,5× (Indriya), nhanh hơn Deluge ~32,7×.
- [hui2004-deluge](hui2004-deluge.md) ★★★ · Deluge phổ biến đối tượng dữ liệu lớn (ảnh chương trình) tới mọi nút WSN đa chặng bằng quảng bá kiểu Trickle, chia trang để pipeline, NACK chọn lọc; đạt ~90 B/s (1/9 tốc độ radio) trên 75 nút, gói điều khiển 18 %, và cho mô hình thời gian E[T_obj] = min(dn, d+3(n−1))·(E[T_page]+D).

## `coding` · fountain code, RLNC, network coding

- [du2017-pando](du2017-pando.md) ★★★ · Pando phát luồng gói LT (fountain) liên tục qua cây pipeline dùng giao thoa xây dựng (Glossy) và đa kênh (PIP), giải mã xen trong khoảng rỗi CPU, dừng bằng phản hồi "im lặng" RSSI; đạt tin cậy 100 % và nhanh hơn Splash 3,5× (Indriya), nhanh hơn Deluge ~32,7×.
- [minsky2003-setrecon](minsky2003-setrecon.md) ★★★ · Biểu diễn tập bằng đa thức đặc trưng, gửi giá trị tại m̄ điểm để nội suy hàm hữu tỉ χ_Δa/χ_Δb và tìm hiệu đối xứng; chi phí (m̄+1)(b+1)−1 bit, gần cận dưới thông tin mb − m lg m; bản không tương tác cho phép một bản tin quảng bá sửa cho nhiều client thiếu các tập khác nhau.
- [stojanovic2009-nccoop](stojanovic2009-nccoop.md) ★★★ · Trạm gốc phát tệp K gói cho N máy thu qua kênh on/off độc lập (xác suất mất p_e): round-robin tốn K·log_{1/p_e}N; RLC tốn log_{1/p_e}N khi K cố định nhưng ≈ (1 + 1/log(1/p_e))K khi K ≳ (log N)^r; hợp tác hai giai đoạn với M = (log N)^r nút chuyển tiếp đạt 2K(1 + o(1)) với mọi K.
- [zeng2018-multicast](zeng2018-multicast.md) ★★★ · UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP.

## `a2g-channel` · kênh không–đất

- [alhourani2014-lap](alhourani2014-lap.md) ★★★ · Mô hình suy hao không–đất trung bình = FSPL + η theo nhóm LoS/NLoS, xác suất LoS theo góc ngẩng xấp xỉ bằng hàm S P(LoS, θ) = 1/(1 + a·exp(−b(θ − a))) với a, b khớp theo tham số đô thị ITU (α, β, γ); bán kính phủ R(h) có cực đại, góc ngẩng tối ưu θ_OPT không phụ thuộc PL_max.
- [zeng2018-multicast](zeng2018-multicast.md) ★★★ · UAV phát một file chung (RLNC) cho K trạm mặt đất; chặn dưới xác suất giải được đưa ràng buộc về "thời gian kết nối tối thiểu trong bán kính D", quỹ đạo tối ưu gồm các đoạn thẳng, waypoint chọn qua đặt trạm ảo (VBS) + TSP + tối ưu lồi, tốc độ qua LP.

## `control-overhead` · chi phí điều khiển, giới hạn thông tin giao thức

- [gallager1976-protocol](gallager1976-protocol.md) ★★★ · Dùng lý thuyết rate–distortion chứng minh mỗi thông điệp cần ít nhất H(M) − log₂(1 − e^{−αd}) bit giao thức (thông tin độ dài + thông tin thời điểm bắt đầu, phụ thuộc chỉ vào tích αd), địa chỉ chỉ là một cách mã hoá thông tin thời điểm; hai chiến lược gom hàng đợi đạt gần cận khi số cặp nguồn–đích lớn.
- [hui2004-deluge](hui2004-deluge.md) ★★★ · Deluge phổ biến đối tượng dữ liệu lớn (ảnh chương trình) tới mọi nút WSN đa chặng bằng quảng bá kiểu Trickle, chia trang để pipeline, NACK chọn lọc; đạt ~90 B/s (1/9 tốc độ radio) trên 75 nút, gói điều khiển 18 %, và cho mô hình thời gian E[T_obj] = min(dn, d+3(n−1))·(E[T_page]+D).
- [minsky2003-setrecon](minsky2003-setrecon.md) ★★★ · Biểu diễn tập bằng đa thức đặc trưng, gửi giá trị tại m̄ điểm để nội suy hàm hữu tỉ χ_Δa/χ_Δb và tìm hiệu đối xứng; chi phí (m̄+1)(b+1)−1 bit, gần cận dưới thông tin mb − m lg m; bản không tương tác cho phép một bản tin quảng bá sửa cho nhiều client thiếu các tập khác nhau.

## `testbed` · thực nghiệm phần cứng, testbed

- [du2017-pando](du2017-pando.md) ★★★ · Pando phát luồng gói LT (fountain) liên tục qua cây pipeline dùng giao thoa xây dựng (Glossy) và đa kênh (PIP), giải mã xen trong khoảng rỗi CPU, dừng bằng phản hồi "im lặng" RSSI; đạt tin cậy 100 % và nhanh hơn Splash 3,5× (Indriya), nhanh hơn Deluge ~32,7×.
- [hui2004-deluge](hui2004-deluge.md) ★★★ · Deluge phổ biến đối tượng dữ liệu lớn (ảnh chương trình) tới mọi nút WSN đa chặng bằng quảng bá kiểu Trickle, chia trang để pipeline, NACK chọn lọc; đạt ~90 B/s (1/9 tốc độ radio) trên 75 nút, gói điều khiển 18 %, và cho mô hình thời gian E[T_obj] = min(dn, d+3(n−1))·(E[T_page]+D).
