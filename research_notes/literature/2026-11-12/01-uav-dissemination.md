---
status: reference
updated: 2026-11-12
---
# 01 — Phát tán dữ liệu từ UAV xuống mạng mặt đất, multicast UAV, phát tán mã, DTSP-N

Phiên tìm kiếm 2026-11-12, khoảng 22 lần tìm và 4 lần fetch. **Lưu ý về mức xác minh:** WebFetch bị chặn với
mọi host đã thử (par.nsf.gov, unpaywall.org, manuscript.isc.ac, bohrium.dp.tech không nằm trong danh sách mạng
cho phép), nên **không đọc được toàn văn bài nào**. Ở đây "đã xác minh" nghĩa là thấy tóm tắt hoặc trích đoạn
abstract (tiêu đề, venue, năm, DOI khớp nhau) trong kết quả tìm kiếm. "chỉ thấy tiêu đề" nghĩa là chỉ thấy tiêu đề
hoặc một câu mô tả. Trước khi trích trong paper, cần mở DOI để kiểm tra lại.

## 1. Tóm tắt các ý quan trọng nhất cho SigDrop

1. **Trích dẫn NP-hard đúng như sau:** J. Le Ny, E. Feron, E. Frazzoli, "On the Dubins Traveling Salesman Problem",
   *IEEE Trans. Automatic Control*, vol. 57, no. 1, pp. 265–270, tháng 1/2012, DOI 10.1109/TAC.2011.2166311. Theo
   abstract: bài chứng minh **DTSP (mục tiêu là các điểm)** là NP-hard, đưa ra cận dưới cho tỉ số xấp xỉ của một số
   heuristic đã có, và đề xuất thuật toán rời rạc hoá hướng (heading discretization). Abstract **không nói về
   neighbourhood**. Kết luận "DTSP-N là NP-hard" chỉ là suy ra, vì DTSP là trường hợp riêng khi bán kính neighbourhood
   bằng 0. Bài toán của SigDrop có vùng phủ R50 ≥ 100 m cố định, nên phép quy dẫn cần viết cẩn thận, ví dụ co giãn
   khoảng cách giữa các cụm sao cho R50 không đáng kể, hoặc tắt hợp tác mặt đất để thu về DTSP-N. Chưa đọc được chi
   tiết chứng minh, nên chưa biết đó là NP-hard thường hay NP-hard mạnh; không được tự viết "strongly NP-hard".
2. **Dòng multicast UAV kinh điển (Zeng–Xu–Zhang, TWC 2018) không có hợp tác mặt đất.** Bài này tối thiểu thời
   gian hoàn thành cho một file chung, dùng RLNC. Quỹ đạo tối ưu gồm các đoạn thẳng nối waypoint, mô hình UAV cánh
   quay đổi được tốc độ và hover được. Đây là nền lý thuyết đúng nhất cho baseline (a) "UAV tự phủ, không hợp tác".
   Một kết quả tìm kiếm mở rộng nói bài này có pha D2D, nhưng kết quả trước đó nói không có. Cần mở toàn văn kiểm tra.
3. **Bài gần SigDrop nhất tìm được là Wang et al., IEEE IoT-J 2020** ("Graph-Based File Dispatching Protocol With
   D2D-Enhanced UAV-NOMA Communications in Large-Scale Networks"). UAV multicast các block file bằng NOMA tại các
   điểm dừng (MBSP), rồi người dùng đã có block chia sẻ cho nhau qua D2D để giảm thời gian nhiệm vụ của UAV. Ý tưởng
   "mặt đất hợp tác sau khi UAV phát" **đã có trước**. Khác biệt của SigDrop: UAV cánh bằng không hover, chuyển tiếp
   nhiều chặng theo kế hoạch do trạm gốc tính sẵn (SPINE/Bank/Ring, đường cell cố định), mục tiêu là các critical cell,
   có sửa lỗi takeover khi gió làm lệch quỹ đạo, và mạng 802.15.4 cỡ 13 000 node.
4. **Văn liệu multicast/dissemination từ UAV gần như toàn bộ là UAV cánh quay, ít node đích (vài đến vài chục), tối
   ưu liên tục (SCA, convex) trên mô hình thông lượng Shannon.** Các bài đã thấy: Zeng 2018, Wu et al. (capacity), Gu
   et al. IoT-J 2020, Wu–Liu–Zhang 2019. Không bài nào có ràng buộc Dubins hay mô phỏng ở mức gói 802.15.4. Một bài
   arXiv 2025 (2507.04421) nói thẳng rằng multicast UAV trước đó hầu hết chỉ một chặng.
5. **Phát tán mã/firmware nhờ UAV có tồn tại nhưng theo hướng khác:** Liang et al. (TII 2022) và Sharma–Villányi
   (OJCOMS 2024) dùng UAV để kiểm chứng độ tin cậy của xe hoặc "code mule", không phát quảng bá cả file. Phía WSN thì
   có Deluge/Trickle (2004), MOAP (2003), và MobileDeluge (MASS 2014) với trạm gốc di động chỉ gieo cho node trong một
   chặng. Không thấy bài nào dùng UAV cánh bằng gieo một object lớn rồi để mạng mặt đất chuyển tiếp theo kế hoạch.
6. **DTSP-N có thuật toán và cận dưới dùng được ngay cho CHORD/LM-Tour:** Váňa–Faigl (IROS 2015, giải được hàng trăm
   vùng), Isaacs–Klein–Hespanha (ACC 2011), Isaacs–Hespanha (*Algorithms* 2013, lấy mẫu rồi GTSP→ATSP), và cận dưới
   DTSP của Manyam–Rathinam (arXiv 1506.08752, G* ở RSS 2023). Nên dùng chúng để báo optimality gap của tour.
7. **Cho định lý crossover:** Wu–Liu–Zhang (IEEE Wireless Commun. 2019) chính thức hoá đánh đổi thông lượng, độ trễ
   và năng lượng đẩy theo quỹ đạo, nhưng không so "hợp tác mặt đất" với "UAV lượn chờ". Định lý crossover của SigDrop
   có vẻ chưa có tiền lệ trực tiếp. Đây chỉ là nhận định từ khoảng 22 lần tìm, chưa phải khảo sát đầy đủ.

## 2. Bảng tài liệu chính

| # | Tác giả, năm | Tiêu đề / venue | Link/DOI | Liên quan với SigDrop | Trạng thái |
|---|---|---|---|---|---|
| 1 | J. Le Ny, E. Feron, E. Frazzoli, 2012 | "On the Dubins Traveling Salesman Problem", IEEE TAC 57(1):265–270 | DOI 10.1109/TAC.2011.2166311 | Nguồn chứng minh DTSP là NP-hard; DTSP-N suy ra như trường hợp tổng quát | đã xác minh (abstract) |
| 2 | K. Savla, E. Frazzoli, F. Bullo, 2008 | "Traveling salesperson problems for the Dubins vehicle", IEEE TAC | https://www.ccdc.ucsb.edu/node/12348 | Nền tảng DTSP (cận, thuật toán) mà bài 1 dựa vào | chỉ thấy tiêu đề |
| 3 | Y. Zeng, X. Xu, R. Zhang, 2018 | "Trajectory Design for Completion Time Minimization in UAV-Enabled Multicasting", IEEE TWC 17(4):2233–2246 | DOI 10.1109/TWC.2018.2790401; arXiv https://arxiv.org/pdf/1708.06478 | Multicast file chung bằng RLNC, tối thiểu thời gian hoàn thành; khung lý thuyết cho baseline (a) | đã xác minh (abstract) |
| 4 | Wu, Xu, Qiu, Zhang (theo trích đoạn), 2017 | "Capacity of UAV-Enabled Multicast Channel: Joint Trajectory Design and Power Allocation" | https://arxiv.org/pdf/1711.04387 | Dung lượng kênh multicast UAV, chỉ một chặng | đã xác minh (abstract, venue chưa rõ) |
| 5 | Q. Wu, L. Liu, R. Zhang, 2019 | "Fundamental Trade-offs in Communication and Trajectory Design for UAV-Enabled Wireless Network", IEEE Wireless Commun. | DOI 10.1109/MWC.2018.1800221; https://arxiv.org/pdf/1805.07038 | Đánh đổi thông lượng, trễ, năng lượng; khung để đặt định lý crossover | đã xác minh (abstract) |
| 6 | B. Wang, R. Zhang, C. Chen et al., 2020 | "Graph-Based File Dispatching Protocol With D2D-Enhanced UAV-NOMA Communications in Large-Scale Networks", IEEE IoT-J 7(9):8615–8630 | DOI 10.1109/JIOT.2020.2994549; https://researchportal.hkust.edu.hk/en/publications/graph-based-file-dispatching-protocol-with-d2d-enhanced-uav-noma-/ | **Gần nhất:** UAV multicast rồi D2D chia sẻ block; khác ở chỗ chỉ một chặng, UAV hover, mạng tế bào | đã xác minh (tóm tắt) |
| 7 | (cùng nhóm), WCNC 2020 | "...With D2D-Aided UAV-NOMA Communications in Large-Scale Networks" | https://par.nsf.gov/biblio/10193326 | Bản hội nghị của #6 | chỉ thấy tiêu đề |
| 8 | J. Gu, H. Wang, G. Ding, Y. Xu, Z. Xue, H. Zhou, 2020 | "Energy-Constrained Completion Time Minimization in UAV-Enabled Internet of Things", IEEE IoT-J | DOI 10.1109/JIOT.2020.2981092; https://ieeexplore.ieee.org/abstract/document/9037366/ | UAV cánh quay phát dữ liệu cho thiết bị IoT, giới hạn năng lượng, SCA; không có hợp tác mặt đất | đã xác minh (tóm tắt ngắn) |
| 9 | J. Liang, W. Liu, N. N. Xiong, A. Liu, S. Zhang, 2022 | "An Intelligent and Trust UAV-Assisted Code Dissemination 5G System for Industrial Internet-of-Things", IEEE TII 18(4):2877–2889 | DOI 10.1109/TII.2021.3110734 | Phát tán mã có UAV, nhưng UAV thu bằng chứng tin cậy; xe mới là bên phát mã | đã xác minh (abstract) |
| 10 | Sharma, Villányi, 2024 | Khung phát tán mã dùng chữ ký số, có UAV hỗ trợ, cho IIoT 5G, IEEE OJCOMS | DOI 10.1109/OJCOMS.2024.3368275 | Tiếp nối #9 (code mule đáng tin); không trùng | chỉ thấy tiêu đề (tóm tắt một câu) |
| 11 | J. W. Hui, D. E. Culler, 2004 | "The dynamic behavior of a data dissemination protocol for network programming at scale" (Deluge), SenSys 2004, pp. 81–94 | DOI 10.1145/1031495.1031506 | Baseline (b); số liệu khoảng 90 B/s, điều khiển 18% số lần truyền | đã xác minh (abstract) |
| 12 | P. Levis, N. Patel, D. Culler, S. Shenker, 2004 | "Trickle: A Self-Regulating Algorithm for Code Propagation and Maintenance in WSNs", NSDI 2004 | https://static.usenix.org/events/nsdi04/tech/levisTrickle/levisTrickle.pdf | Baseline (b), cơ chế quảng bá của Deluge | đã xác minh (abstract) |
| 13 | T. Stathopoulos, J. Heidemann, D. Estrin, 2003 | "A Remote Code Update Mechanism for Wireless Sensor Networks" (MOAP) | https://ant.isi.edu/~johnh/PAPERS/Stathopoulos03b.html | Phát tán mã nhiều chặng kinh điển | đã xác minh (tóm tắt) |
| 14 | (tác giả chưa thấy), 2014 | MobileDeluge, IEEE MASS 2014 | https://xiaozhon.github.io/pubs/MASS_2014.pdf | Trạm gốc di động cầm tay gieo Deluge cho node trong một chặng; gần với ý "mobile seeder" | chỉ thấy tiêu đề (tóm tắt một câu) |
| 15 | P. Váňa, J. Faigl, 2015 | "On the Dubins Traveling Salesman Problem with Neighborhoods", IROS 2015 | https://comrob.fel.cvut.cz/papers/iros15dtspn.pdf | Thuật toán DTSP-N lặp, giải được hàng trăm vùng; dùng làm đối chứng cho CHORD/LM-Tour | đã xác minh (abstract) |
| 16 | P. Váňa, J. Faigl, 2015 | "On Sampling Based Methods for the Dubins Traveling Salesman Problem with Neighborhoods", Acta Polytechnica CTU Proc. | DOI 10.14311/app.2015.1.0057 | Như #15 | chỉ thấy tiêu đề |
| 17 | D. G. Isaacs, D. J. Klein, J. P. Hespanha, 2011 | "Algorithms for the Traveling Salesman Problem with Neighborhoods Involving a Dubins Vehicle", ACC 2011 | https://skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1252.pdf | Thuật toán DTSP-N | đã xác minh (tóm tắt) |
| 18 | J. T. Isaacs, J. P. Hespanha, 2013 | "Dubins Traveling Salesman Problem with Neighborhoods: A Graph-Based Approach", *Algorithms* | https://www.icb.ucsb.edu/publications/2038 | Lấy mẫu rồi GTSP→ATSP; cách chuẩn để có lời giải tham chiếu | đã xác minh (abstract) |
| 19 | S. G. Manyam, S. Rathinam, 2015 | "On Tightly Bounding the Dubins Traveling Salesman's Optimum" | https://ar5iv.labs.arxiv.org/html/1506.08752 | Cận dưới DTSP qua bài toán khoảng hướng; dùng cho optimality gap | đã xác minh (abstract) |
| 20 | S. G. Manyam, A. Nayak, S. Rathinam, 2023 | G* cho cận dưới qua Dubins gate, RSS 2023 | https://www.roboticsproceedings.org/rss19/p059.pdf | Cận dưới chặt hơn cho đường Dubins qua vùng | chỉ thấy tiêu đề (tóm tắt một câu) |
| 21 | P. Váňa, J. Faigl, 2018 | Generalized Dubins Interval Problem, RSS 2018 | https://m.roboticsproceedings.org/rss14/p35.html | Bài toán con của DTSP-N | chỉ thấy tiêu đề |
| 22 | (tác giả chưa thấy), 2017 | "Ultra Reliable UAV Communication Using Altitude and Cooperation Diversity" | https://arxiv.org/pdf/1705.02877 | Relay mặt đất DF hai pha sau khi UAV phát, nhưng là unicast | đã xác minh (tóm tắt) |
| 23 | (tác giả chưa thấy), 2025 | "Resource-Efficient Seamless Transitions For High-Performance Multi-hop UAV Multicasting" | https://arxiv.org/pdf/2507.04421 | Nói rõ multicast UAV trước đây chủ yếu một chặng; ở đây nhiều chặng trên không | đã xác minh (tóm tắt) |
| 24 | (tác giả chưa thấy), 2020 | FUOTA trên LoRaWAN, có trình mô phỏng FUOTASim | https://arxiv.org/pdf/2002.08735 | Phân mảnh và multicast firmware cho IoT; không có UAV | chỉ thấy tiêu đề (tóm tắt) |
| 25 | K. Sistu et al., 2024 | "Time-Constrained Erasure Correction for Data Recovery in UAV-Aided IoT" | https://arxiv.org/html/2403.09782v4 | Fountain code cho chiều cảm biến→UAV (uplink); có thể trích cho phần fountain của baseline (a) | đã xác minh (tóm tắt) |
| 26 | (tác giả chưa thấy), 2011 | R-Code: broadcast tin cậy bằng network coding trong mesh, Ad Hoc Networks | https://www.cnsr.ictas.vt.edu/publication/AHN11_Yang_RNCBRBWMN.pdf | Chia trách nhiệm chuyển tiếp theo quan hệ guardian–ward; tiền lệ của "kế hoạch chuyển tiếp" trên mặt đất | chỉ thấy tiêu đề (tóm tắt) |
| 27 | (nhóm T. He), TPDS | COABroadcast: broadcast tất định trên backbone kèm XOR coding | https://www-users.cse.umn.edu/~tianhe/Research/Publications/Keyword/Papers/COABroadcast_TPDS.pdf | Tiền lệ của đường chuyển tiếp cố định trên backbone | chỉ thấy tiêu đề (tóm tắt) |

## 3. Khoảng trống và cơ hội

- **UAV cánh bằng (Dubins) phát một object lớn cho mạng 802.15.4 nhiều chặng:** không tìm thấy bài nào. Văn liệu
  multicast UAV dùng UAV cánh quay hover được, một chặng, vài chục node đích. SigDrop có thể định vị mình là bài đầu
  tiên ghép ràng buộc Dubins với chuyển tiếp mặt đất nhiều chặng theo kế hoạch.
- **Kế hoạch tính trước theo quỹ đạo:** Wang 2020 chia sẻ D2D bằng phân bổ tài nguyên dựa trên đồ thị nhưng chỉ
  một chặng. Không thấy bài nào gán "mỗi cell dưới đường bay giữ một đoạn gói" rồi định tuyến cố định đến tập đích
  con (critical cells). Cận dưới min-cut cho thời gian sẵn sàng của mặt đất và định nghĩa "giá trị thông tin của kế
  hoạch" (chi phí điều khiển so với Deluge, nơi điều khiển chiếm 18% số lần truyền) có vẻ mới.
- **Định lý crossover (hợp tác mặt đất hay UAV lượn chờ):** Zeng 2018 và Wu–Liu–Zhang 2019 cho phép tối ưu tốc độ và
  hover nhưng không có lựa chọn "để mặt đất mang dữ liệu đi". Đây là chỗ đóng góp lý thuyết rõ nhất.
- **Độ bền với lệch quỹ đạo do gió (takeover):** không thấy bài multicast UAV nào xét lệch quỹ đạo khi thực thi.
- **Đối chứng tour:** dùng Isaacs–Hespanha (GTSP→ATSP) hoặc Váňa–Faigl làm lời giải tham chiếu và Manyam–Rathinam
  làm cận dưới, để báo gap của CHORD/LM-Tour thay vì chỉ so tương đối giữa các baseline.
- **Baseline (a) nên dựng theo Zeng 2018** (RLNC/fountain, tối thiểu thời gian hoàn thành) kết hợp DTSP-N, và trích
  bài này làm đại diện cho hướng "UAV tự phủ".

## 4. Rủi ro trùng lặp với đóng góp của SigDrop

- **Cao: Wang et al., IoT-J 2020 (#6).** Đã có "UAV multicast, sau đó người dùng mặt đất chia sẻ block qua D2D để rút
  ngắn nhiệm vụ UAV", và đó là bài IoT-J, đúng venue mục tiêu. Reviewer có thể nói "ground cooperation after UAV
  multicast is known". Cần trích bài này và tách biệt rõ: nhiều chặng so với một chặng D2D; kế hoạch tất định theo
  quỹ đạo; UAV cánh bằng không hover; tập đích con cần cả query; sửa lỗi takeover; cận min-cut; quy mô 13 000 node,
  802.15.4. Nên đọc toàn văn trước khi viết related work (bị chặn trong phiên này).
- **Trung bình: UAV gieo rồi Deluge, MobileDeluge (#14).** Ý "mobile seeder + giao thức phát tán phân tán" đã có (cầm
  tay, một chặng). Baseline (b) của SigDrop cần được trình bày đúng là phiên bản UAV của ý này, để phần mới nằm ở kế
  hoạch, không nằm ở việc gieo.
- **Trung bình: broadcast tất định trên backbone (#26, #27).** Đường cell cố định và cấu trúc Bank/Ring giống
  backbone broadcast. Phần mới phải là sự kết hợp với điểm vào theo không gian do quỹ đạo UAV tạo ra (SPINE) và với
  việc phân đoạn object, không phải bản thân định tuyến cố định.
- **Thấp, nhưng về hình thức: NP-hardness.** Quy dẫn từ DTSP/DTSP-N gần như hiển nhiên, nên reviewer TMC có thể
  coi là đóng góp nhỏ. Nên trình bày như bổ đề nền và để định lý crossover, ngưỡng takeover, cận min-cut làm đóng góp
  chính. Phải trích đúng Le Ny et al. 2012 (DTSP với mục tiêu là điểm) và không nói bài đó chứng minh DTSP-N.
- **Chưa loại trừ được:** chưa quét IEEE Xplore cho 2023–2026 với "UAV multicast + multi-hop relay + WSN", và
  WebFetch bị chặn. Cần một lượt kiểm tra trên Google Scholar với các cụm "UAV-assisted dissemination" + "multi-hop"
  + "sensor network" và "fixed-wing UAV broadcast" trước khi khẳng định "first".
