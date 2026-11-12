---
status: current
updated: 2026-11-12
---
# Ghi chú đọc 32 PDF trong thư mục Drive (2026-11-12)

Mỗi bài có khoá là DOI, kèm tên file trong Drive để mở lại nhanh. Mức liên quan: ★★★ dùng trực tiếp cho J1, ★★ nền hoặc
công cụ, ★ chỉ để biết. Nhãn chỉ chỗ dùng: [L1] bổ đề độ khó, [A] định lý crossover, [FC] baseline fountain code và bay
vòng, [TOUR] CHORD và LM-Tour, [ĐV] định vị đóng góp. Cách đọc: toàn văn được trích bằng `pdftotext`; các bài ★★★ được
đọc kỹ phần phát biểu và chứng minh, các bài khác chủ yếu đọc abstract, mở đầu và kết luận. PDF không được commit (xem
`PDF-LIST-2026-11-12-vi.md`).

## 1. Điều rút ra quan trọng nhất

- **Bổ đề L1 viết được chính xác.** Le Ny–Feron–Frazzoli 2012 (Định lý 2) chứng minh Dubins TSP (bản tour và bản path)
  NP-khó bằng cách lấy phép quy của Papadimitriou từ Exact Cover sang TSP Euclid, rồi phóng to mọi khoảng cách theo hệ số
  2Cn/ε. Bước này dùng cận "tour Dubins tối ưu ≤ tour Euclid tối ưu + Cn" của Savla et al. 2008, trong đó C là hằng số
  phụ thuộc bán kính quay. Phép quy của SigDrop có thể đi đúng theo khuôn này. Babel 2017 viết rõ lập luận "khi diện tích
  vùng tiến về 0, DTSP-N trở về DTSP, nên DTSP-N cũng NP-khó"; có thể trích để nói về bản có lân cận.
- **Zeng–Xu–Zhang 2018 gần như là baseline FC của chúng ta, ở bản một chặng và UAV cánh quay.** Bài dùng RLNC. Mỗi trạm
  mặt đất cần đủ số gói mã; xác suất giải được được chặn dưới (Định lý 1), rồi điều kiện này chuyển thành thời gian kết
  nối tối thiểu với từng trạm, có biên an toàn dạng Gauss (hàm Q ngược). Đây chính là kiểu biên 3√((1+ε)K_j) mà baseline
  FC đang dùng, nên định lý A có thể phát biểu chặn dưới của T_FC theo "thời gian kết nối tối thiểu" và trích Zeng 2018.
  Định lý 2 của bài cho thấy quỹ đạo tối ưu gồm các đoạn thẳng nối nhau, đưa bài toán về chọn waypoint kiểu TSP. Bài không
  có hợp tác mặt đất và cho phép UAV treo tại chỗ, nên vẫn khác SigDrop.
- **Có sẵn quy trình tính tour tham chiếu để đo khoảng cách tối ưu của CHORD và LM-Tour.** Lấy mẫu vị trí và hướng trong
  mỗi vùng, đưa về Generalized TSP, biến đổi Noon–Bean 1993 sang ATSP cùng số nút, rồi giải bằng LKH (Helsgaun 2000).
  Isaacs–Klein–Hespanha 2011 dùng đúng hướng này và cho hệ số xấp xỉ không phụ thuộc số vùng khi các vùng rời nhau. Việc
  này rẻ (Python và LKH, không cần ns-3) và trả lời được câu hỏi phản biện "CHORD cách tối ưu bao xa".
- **Le Ny 2012 (Định lý 3) cảnh báo:** các thuật toán giữ thứ tự của tour Euclid rồi chỉ chọn hướng có thể kém tối ưu tới
  cỡ n lần khi các điểm dày so với bán kính quay. Bán kính cell 100 m so với bán kính quay 63,7 m nằm gần vùng này, nên
  không nên lập luận "tour của CHORD gần tối ưu vì theo thứ tự Euclid".
- **Thư mục không có bài nào về phát dữ liệu xuống mạng có hợp tác nhiều chặng.** Gần nhất là Zeng 2018 (không hợp tác)
  và Joint Rate and Coverage 2020 (UAV làm trạm gốc, D2D một chặng mở rộng vùng phủ). Rủi ro trùng lặp với Wang 2020
  (IoT-J) vẫn phải kiểm khi có PDF.
- **Nhóm bài orienteering cho UAV cánh bằng** (Pěnička 2017, Faigl 2017, Váňa 2017, Autonomous Robots 2019) giải bài toán
  thu dữ liệu có giới hạn quãng bay, với vùng nhận là đĩa quanh mỗi node. Chúng hữu ích nếu SigDrop có ràng buộc pin của
  UAV, và cho thấy cách mô hình "vùng nghe" bằng đĩa là chuẩn trong tài liệu.

## 2. Dubins TSP: nền tảng và độ khó

| DOI | File | Bài | Ghi chú | Dùng cho |
|---|---|---|---|---|
| 10.2307/2372560 | dubins1957 | Dubins, On curves of minimal length with a constraint on average curvature…, Amer. J. Math. 1957 | Đường ngắn nhất giữa hai cấu hình có hướng, với độ cong bị chặn, thuộc tập 6 loại cung tròn và đoạn thẳng (LSL, RSR, LSR, RSL, RLR, LRL). | ★★ [TOUR], trích khi định nghĩa mô hình Dubins |
| 10.1016/S0921-8890(00)00127-5 | shkel2001 | Shkel, Lumelsky, Classification of the Dubins set, RAS 2001 | Chọn trực tiếp đường ngắn nhất trong tập Dubins mà không tính cả 6 đường; nhanh cho lập kế hoạch thời gian thực. | ★ công cụ |
| 10.1109/CDC.2007.4434503 | leny2007 | Le Ny, Frazzoli, Feron, The curvature-constrained TSP for high point densities, CDC 2007 | Bản hội nghị trước của Le Ny 2012: phác thảo chứng minh DTSP NP-khó (DTSP ít nhất khó như TSP Euclid) và thuật toán cho mật độ điểm cao. | ★★ [L1], trích kèm bản 2012 |
| 10.1109/TAC.2011.2166311 | leny2012 | Le Ny, Feron, Frazzoli, On the Dubins traveling salesman problem, IEEE TAC 57(1):265–270, 2012 | Định lý 2: tour-DTSP và path-DTSP NP-khó; phép quy là phép quy của Papadimitriou cho TSP Euclid, phóng to theo 2Cn/ε, dùng cận DTSP ≤ ETSP + Cn. Định lý 3: có những instance mà các heuristic theo thứ tự Euclid kém tối ưu cỡ n lần. Bài cũng đề xuất thuật toán rời rạc hoá hướng. Bài **không** xét bản có lân cận. | ★★★ [L1], [TOUR] |
| 10.1109/TAC.2008.925814 | savla2008 | Savla, Frazzoli, Bullo, Traveling salesperson problems for the Dubins vehicle, IEEE TAC 53(6), 2008 | Thuật toán ALTERNATING (giữ thứ tự tour Euclid, gán hướng xen kẽ) đạt trong hằng số lần tối ưu với một lớp tập điểm; cận trên độ dài đường Dubins điểm-tới-điểm (Định lý 3.4), là nguồn của cận DTSP ≤ ETSP + Cn; bản ngẫu nhiên: điểm phân bố đều cho tour kỳ vọng cỡ ít nhất n^(2/3). | ★★★ [L1] (cận dùng trong phép quy), [TOUR] |
| 10.1109/CDC.2006.376928 | ma2006 | Ma, Castañón, Receding horizon planning for Dubins TSP, CDC 2006 | Lập kế hoạch cuộn theo ba điểm liên tiếp, có kết quả tối ưu cho bài toán Dubins ba điểm. | ★ [TOUR] |
| 10.1109/TASE.2006.872110 | rathinam2007 | Rathinam, Sengupta, Darbha, A resource allocation algorithm for multivehicle systems with nonholonomic constraints, IEEE TASE 2007 | Chia tour cho nhiều xe có ràng buộc góc quay, hướng tại điểm không cho trước; thuật toán xấp xỉ. | ★★ nếu dùng nhiều UAV (đội 1, đội 2) |
| 10.1007/s10732-020-09440-2 | s10732-020-09440-2 | New heuristic algorithms for the Dubins TSP, J. Heuristics 26:503–530, 2020 | Các heuristic DTSP chuyển từ TSP, dựa trên tối ưu hướng của một chuỗi điểm có thứ tự cho trước bằng mạng phụ rời rạc hoá hướng. | ★★ [TOUR], đối chứng |
| 10.1016/j.ejor.2017.03.067 | babel2017 | Curvature-constrained traveling salesman tours for aerial surveillance, EJOR 2017 | DTSP có chướng ngại cho giám sát trên không. Phần tổng quan có câu: khi diện tích vùng tiến về 0, DTSP-N trở về DTSP, nên DTSP-N NP-khó. | ★★★ [L1] (trích cho bản có lân cận) |

## 3. DTSP-N, lấy mẫu và công cụ giải

| DOI | File | Bài | Ghi chú | Dùng cho |
|---|---|---|---|---|
| 10.1080/03155986.1993.11732212 | noon1993 | Noon, Bean, An efficient transformation of the generalized TSP, INFOR 1993 | Biến GTSP (chọn đúng một nút mỗi nhóm) thành ATSP chuẩn với cùng số nút (Định lý 2). | ★★ [TOUR], bước then chốt của quy trình lấy mẫu |
| 10.1016/S0377-2217(99)00284-2 | helsgaun2000 | Helsgaun, An effective implementation of the Lin–Kernighan TSP heuristic (LKH), EJOR 2000 | Bộ giải TSP mạnh nhất phổ biến; tìm được lời giải tối ưu cho mọi instance đã biết lúc đó, kể cả 13 509 thành phố. | ★★ [TOUR], bộ giải để tính tour tham chiếu |
| 10.1109/ACC.2011.5991501 | isaacs2011 | Isaacs, Klein, Hespanha, Algorithms for the TSP with neighborhoods involving a Dubins vehicle, ACC 2011 | Hai thuật toán DTSP-N. Thuật toán 1 cho vùng rời nhau: mỗi vùng lấy mẫu một lần, hệ số xấp xỉ không phụ thuộc số vùng (phụ thuộc đường kính vùng, khoảng cách tối thiểu giữa vùng và bán kính quay; Định lý 3.1). Thuật toán 2 cho vùng chồng nhau, qua GTSP → ATSP. | ★★★ [TOUR], [L1] |
| 10.2514/6.2009-5888 | obermeyer2009 | Obermeyer, Path planning for a UAV performing reconnaissance of static ground targets in terrain, AIAA GNC 2009 | Quy bài toán trinh sát về DTSP thăm đa giác (PVDTSP), giải bằng thuật toán di truyền; tour ngắn khoảng một nửa so với tìm ngẫu nhiên với 5–20 mục tiêu. | ★★ [TOUR] |

## 4. Thu dữ liệu bằng UAV cánh bằng (orienteering)

| DOI | File | Bài | Ghi chú | Dùng cho |
|---|---|---|---|---|
| 10.1109/ICUAS.2017.7991350 | penicka2017 | Pěnička, Faigl, Váňa, Saska, Dubins orienteering problem with neighborhoods, ICUAS 2017 | Chọn tập mục tiêu và thứ tự để tối đa phần thưởng trong giới hạn quãng bay; nhận được dữ liệu trong đĩa bán kính δ quanh mục tiêu. | ★★ mô hình vùng nghe dạng đĩa |
| 10.1109/IROS.2017.8206453 | faigl2017 | Faigl, Pěnička, On close enough orienteering problem with Dubins vehicle, IROS 2017 | Bản "đủ gần" của orienteering cho xe Dubins, giải bằng học không giám sát. | ★ |
| 10.1109/ECMR.2017.8098715 | vana2017 | Váňa, Faigl, Sláma, Pěnička, Data collection planning with Dubins airplane model and limited travel budget, ECMR 2017 | Mở rộng sang 3D với mô hình Dubins airplane cho UAV cánh bằng thu dữ liệu. | ★ |
| 10.1007/s10514-019-09844-5 | 10.1007@s10514-019-09844-5 | Data collection planning with non-zero sensing distance for a budget and curvature constrained UAV, Autonomous Robots 2019 | Bản tạp chí của hướng DOPN, có thử nghiệm bay thật với máy tính trên UAV và bộ điều khiển MPC. | ★★ [TOUR], dẫn chứng thực nghiệm |

## 5. UAV phát dữ liệu, hợp tác, nhiều xe

| DOI | File | Bài | Ghi chú | Dùng cho |
|---|---|---|---|---|
| 10.1109/TWC.2018.2790401 | 1708.06478v1 | Zeng, Xu, Zhang, Trajectory design for completion time minimization in UAV-enabled multicasting, IEEE TWC 17(4):2233–2246, 2018 (bản arXiv v1 có tên "Trajectory optimization for…") | Xem mục 1. RLNC; xác suất giải được chặn dưới qua số gói nhận (Định lý 1, dùng Bổ đề 1 về tổng Bernoulli); điều kiện thành thời gian kết nối tối thiểu có biên Gauss; quỹ đạo tối ưu gồm các đoạn thẳng nối nhau (Định lý 2); đưa về TSP qua waypoint. UAV cánh quay, một chặng, không hợp tác. | ★★★ [FC], [A], [ĐV] |
| 10.1109/ICCC51575.2020.9345214 | Joint_Rate_and_Coverage… | Joint rate and coverage design for UAV-enabled wireless networks with underlaid D2D communications, ICCC 2020 | UAV làm trạm gốc khẩn cấp; D2D dùng lại phổ để mở rộng vùng phủ cho người dùng ngoài tầm UAV. Hợp tác một chặng, mạng di động. | ★★ [ĐV] |
| 10.1109/TC.2013.2295609 | XLL15 | Xu, Liang, Lin, Approximation algorithms for min-max cycle cover problems, IEEE TC 64(3), 2015 | Thuật toán xấp xỉ phủ đồ thị bằng k chu trình sao cho chu trình dài nhất nhỏ nhất; áp dụng cho thu dữ liệu và sạc không dây trong WSN. | ★★ nếu chia cụm cho nhiều UAV |
| 10.3390/s23146432 | sensors-23-06432 | Heuristics and learning models for Dubins MinMax TSP, Sensors 2023 | Bản nhiều xe, mỗi nhóm chọn một mục tiêu (one-in-a-set), cực tiểu tour dài nhất: MILP, VNS, mạng nơ-ron đồ thị. | ★ nhiều UAV |
| 10.3390/s23052560 | sensors-23-02560-v2 | Exact and heuristic multi-robot Dubins coverage path planning for known environments, Sensors 2023 | Phủ vùng bằng nhiều robot Dubins: thuật toán chính xác (MILP) và heuristic. | ★ |

## 6. Phủ vùng, UAV làm trạm gốc, thu dữ liệu (ít liên quan)

| DOI | File | Bài | Ghi chú |
|---|---|---|---|
| 10.1016/j.dt.2025.01.008 | 1-s2.0-S2214914725000170-main | Wang, Zhang, Li, Zhang, Multiple fixed-wing UAVs collaborative coverage 3D path planning method for complex areas, Defence Technology 2025 | Phủ vùng 3D nhiều UAV cánh bằng trong môi trường động. ★ |
| 10.1109/JIOT.2025.3528077 | Fixed-Wing-UAV-Coverage-Path-Planning… | Fixed-wing UAV coverage path planning based on turning span selection, IEEE IoT-J 2025 | Phủ ruộng bằng UAV cánh bằng, chọn bề rộng quay để giảm quãng quay. Cho thấy chi phí quay của cánh bằng được IoT-J quan tâm. ★★ [TOUR] |
| 10.1109/ACCESS.2024.3425497 | Deep_Reinforcement_Learning_for_AoI… | DRL for AoI minimization in UAV-aided data collection for WSN and IoT: a survey, IEEE Access 2024 | Tổng quan DRL cho UAV thu dữ liệu (chiều lên). Dùng để nói tài liệu tập trung vào chiều lên. ★ [ĐV] |
| 10.1109/TMC.2021.3089329 | An_Optimized_LTE-Based… | An optimized LTE-based technique for drone base station dynamic 3D placement and resource allocation in delay-sensitive M2M networks, IEEE TMC 2023 | Đặt trạm gốc LTE trên drone để tối đa vùng phủ thiết bị M2M. ★ |
| 10.1109/LWC.2021.3121076 | Coverage_Maximization… | Coverage maximization for heterogeneous aerial networks, IEEE WCL 2022 | Tối ưu quỹ đạo trạm gốc tầm cao và vị trí trạm tầm thấp. ★ |
| 10.1109/JSYST.2025.3532232 | Coverage_Optimization… | Coverage optimization for reliable UAV-assisted 5G/6G communication systems, IEEE Systems J. 2025 | Vị trí UAV tối ưu theo mô hình LoS xác suất, đô thị và ngoại ô. ★ (kênh) |
| 10.1109/CCNC49032.2021.9369472 | Energy_and_Service-Priority… | Energy and service-priority aware trajectory design for UAV-BSs using double Q-learning, CCNC 2021 | Quỹ đạo UAV-BS theo ưu tiên dịch vụ và năng lượng. ★ |
| 10.1109/CCNC51644.2023.10060414 | Multi-UAV_Assisted_Network_Coverage… | Multi-UAV assisted network coverage optimization for rescue operations using RL, CCNC 2023 | Nhiều UAV làm trạm gốc cho cứu hộ sau thảm hoạ. ★ (bối cảnh SAR) |
| 10.1109/WCNC49053.2021.9417264 | UAV-Assisted_Cellular_Communication… | UAV-assisted cellular communication: joint trajectory and coverage optimization, WCNC 2021 | UAV giảm tải cho người dùng biên cell. ★ |
| 10.1145/959060.959072 | tan2003 | Tan, Körpeoğlu, Power efficient data gathering and aggregation in wireless sensor networks, SIGMOD Record 2003 | Gom dữ liệu theo cây khung nhỏ nhất (PEDAP). ★ |

## 7. Việc nên làm từ các ghi chú này

1. Viết lại bổ đề L1 trong sổ thử nghiệm theo khuôn Le Ny 2012 (Định lý 2), trích Savla 2008 cho cận DTSP ≤ ETSP + Cn và
   Babel 2017 cho bản có lân cận.
2. Trong định lý A, trích Zeng 2018 cho chặn dưới kiểu "thời gian kết nối tối thiểu"; nêu rõ khác biệt: UAV cánh bằng,
   có lựa chọn hợp tác mặt đất.
3. Thử đo khoảng cách tối ưu của CHORD và LM-Tour bằng quy trình lấy mẫu, Noon–Bean và LKH trên một bản đồ. Việc này
   không cần ns-3 nhưng vẫn phải bàn chi phí trước khi chạy.
