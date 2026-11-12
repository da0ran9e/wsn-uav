---
status: reference
updated: 2026-11-12
---
# 05 — Lệch quỹ đạo do gió của UAV cánh cố định, và các cơ chế giống takeover

Ngày: 2026-11-12. Phạm vi: 25 lượt tìm kiếm web.

**Lưu ý về cách xác minh.** WebFetch bị chặn trong session này: `arxiv.org` và `typeset.io` không phân giải được
(nằm ngoài các domain mạng được phép). Vì vậy mọi số liệu dưới đây lấy từ **trích đoạn và tóm tắt của kết quả tìm
kiếm** (thường là abstract), chưa đọc toàn văn.
- "đã xác minh" nghĩa là URL/DOI và con số đã hiện trong kết quả tìm kiếm.
- "chỉ thấy tiêu đề" nghĩa là chỉ thấy tiêu đề/URL, chưa thấy nội dung hay số liệu.

Trước khi đưa vào paper cần đọc toàn văn.

## 1. Tóm tắt

1. **Bay thẳng, có bù gió: sai số nhỏ hơn σ = 50 m một bậc.** Thử nghiệm bay với guidance phi tuyến (gốc của L1
   trong ArduPilot) đạt 1,6 m RMS khi bay theo đường tròn [Park 2004/2007]. Vector field đạt sai số trung bình
   dưới 1 sải cánh trên đường thẳng và quỹ đạo tròn, dưới 3 sải cánh khi đổi hướng liên tục [Nelson 2007]. Nếu
   bỏ qua gió thì sai số ngang ở trạng thái ổn định là 6,5 m [Beard et al., BYU]. GPS SPS: ≤ 8 m (95%, trung bình
   toàn cầu) theo tiêu chuẩn; đo thực tế ≤ 2,2 m (95%).
2. **Vì vậy σ = 50 m là cận trên thận trọng cho bay thường có bù gió.** Kết quả "σ ≤ 50 m không có gì hỏng"
   đứng vững và nên trình bày là kết quả chính.
3. **Sai số lớn tập trung ở các khúc cua, không rải đều.** Trong khung mặt đất, khúc cua bank tối đa là đường
   trochoid [Techy & Woolsey 2009], không phải cung tròn. Bán kính phía xuôi gió là (Va+W)²/(g·tan φ). Tính lại
   cho SigDrop (tự tính, không trích):
   - Va = 25 m/s, W = 10 m/s: 125 m so với 63,7 m, tức rộng thêm 61 m. Với W = 15 m/s: thêm 99 m.
   - Va = 50 m/s, W = 10 m/s: thêm 112 m. Với W = 15 m/s: thêm 176 m.

   Nếu tour được lập bằng Dubins trong không khí lặng, máy bay sẽ vượt quỹ đạo ở cua cỡ 30–180 m. Đây là cơ sở
   vật lý để giữ kịch bản 100 m.
4. **σ = 200 m (độ lệch kéo dài, không chỉ đỉnh) không có số liệu bay nào ủng hộ** cho bay có bù gió với
   W ≤ 15 m/s. Nên gọi đó là kịch bản stress/cực đoan, ứng với mất ước lượng gió, cua sai mô hình, hoặc
   W/Va tiến gần 1. Với Va ≥ 25 m/s, W/Va ≤ 0,6, nên hiện tượng "run-away" [Stastny 2019] không xảy ra.
5. **Kiểm tra nhanh mô hình hiện tại** (giả sử "kernel 10 s" là độ lệch chuẩn s của Gaussian, nên độ dài tương
   quan là ℓ = √2·s ≈ 14 s). Các con số dưới đây cho vận tốc ngang và gia tốc ngang (RMS):

   | σ | vận tốc ngang | gia tốc ngang | so với Va = 25 m/s |
   |---|---|---|---|
   | 50 m | 3,5 m/s | 0,43 m/s² | — |
   | 100 m | 7,1 m/s | 0,87 m/s² | — |
   | 200 m | 14 m/s | 1,7 m/s² | lệch hướng RMS ≈ 34° |

   Gia tốc ngang vẫn trong giới hạn g·tan 45° = 9,8 m/s². Nhưng với σ = 200 m, lệch hướng RMS ≈ 34° kéo dài
   suốt tour là không hợp lý với một autopilot bám đường.
6. **Rủi ro chưa mô hình: lệch dọc tuyến (along-track).** Gió ngược hoặc xuôi đổi tốc độ mặt đất ±W, nên
   ±40% ở Va = 25 m/s. Nếu cell nhận gói được tính theo *thời điểm* phát, sai số dọc tuyến tăng tuyến tính, ví dụ
   10 m/s × 60 s = 600 m. Hướng xử lý: phát theo vị trí (theo độ dài cung), hoặc giữ tốc độ mặt đất bằng
   autothrottle.
7. **Tài liệu truyền thông UAV đã có tiền lệ mô hình hoá bất định.** Gió là ước lượng cộng sai số bị chặn, và
   UAV có jitter [Xu, Sun, Ng, Schober, TCOM 2020]. Lệch quỹ đạo được mô hình thống kê rồi xử lý chủ động bằng cách
   mở rộng footprint cho chồng lấn [Lahmeri et al., OJ-COMS 2024]. Thiết kế quỹ đạo theo gió cho UAV cánh cố định
   thu dữ liệu dùng thống kê gió offline và tinh chỉnh online [Zhang, Lyu, Fu]. Chưa thấy công trình nào sửa lỗi
   *phản ứng* (reactive) như takeover.
8. **Takeover có tiền lệ gần ở từng phần, chưa thấy bản trọn vẹn:**
   - giao quyền giữ dữ liệu theo vị trí, có bản sao trên perimeter thay thế khi node chủ hỏng (GHT);
   - sửa cục bộ tại node đang giữ gói (DSR salvaging);
   - chọn người chuyển tiếp sau khi biết ai thực sự nhận được (ExOR);
   - truy vấn bằng flooding (Directed Diffusion).

## 2. Bảng tài liệu

| # | Tác giả, năm | Venue | Link/DOI | Số liệu / nội dung liên quan | Trạng thái |
|---|---|---|---|---|---|
| 1 | S. Park, J. Deyst, J. How, 2004; bản journal 2007 | AIAA GNC 2004; JGCD 30(6):1718–1728 | 10.2514/6.2004-4900; 10.2514/1.28957 | Thử bay 2 UAV nhỏ: ≤ 1,6 m RMS trên đường tròn; ArduPilot dùng guidance phi tuyến dựa trên Park 2004. Trích đoạn không ghi tốc độ gió. | đã xác minh |
| 2 | D. Nelson, D. Barber, T. McLain, R. Beard, 2007 | IEEE T-RO 23(3):519–529 | 10.1109/TRO.2007.898976 | Sai số trung bình < 1 sải cánh (đường thẳng, quỹ đạo tròn), < 3 sải cánh khi đổi hướng nhiều; hội tụ dưới gió không đổi. | đã xác minh |
| 3 | R. Beard, J. Ferrin, J. Humpherys | preprint BYU (chưa thấy venue) | https://www.et.byu.edu/~beard/papers/preprints/BeardFerrinHumpherys__.pdf | "Fixed Wing UAV Path Following in Wind with Input Constraints": sai số ngang ổn định 6,5 m khi giả định gió = 0. Trích đoạn không ghi W. | đã xác minh (trích đoạn) |
| 4 | T. Stastny, R. Siegwart, 2019 | IROS 2019 (theo trích đoạn) | https://arxiv.org/pdf/1908.01381 | Thử bay vùng núi, giật tới 13 m/s; mở rộng L1 khi W ≳ Va; gọi L1 là guidance phổ biến nhất cho UAV cánh cố định nhỏ. Chưa thấy số liệu sai số ngang. | đã xác minh |
| 5 | (chưa xác minh tác giả), 2025 | arXiv | https://arxiv.org/pdf/2512.06610 | Dynamic soaring: thử bám đường nghiêng khi gió yếu, sai số < 3 m (RMSE 2,24 m). | đã xác minh (trích đoạn) |
| 6 | (Robotics 14(1):7), 2025 | MDPI Robotics | https://mdpi.com/2218-6581/14/1/7 | "A Sliding Mode Approach to Vector Field Path Following for a Fixed-Wing UAV": gió vận hành thường bằng 20–50% airspeed với UAV nhỏ; bảng sai số ngang tối đa và RMSE theo W (mô phỏng). | đã xác minh (trích đoạn) |
| 7 | (arXiv 2505.16407), 2025 | arXiv | https://arxiv.org/pdf/2505.16407 | Mô phỏng bám đường với gust Dryden theo MIL-F-8785C, so với VF-Dubins và VF-Line. Cho thấy Dryden là chuẩn thông dụng. | đã xác minh (trích đoạn) |
| 8 | Souanef (Cranfield) | luận văn/bài (chưa rõ) | https://dspace.lib.cranfield.ac.uk/server/api/core/bitstreams/ee08b70b-9267-4188-910d-5411225fa762/content | L1 adaptive path following thử bay với gió tới 10 m/s. Chưa thấy số liệu sai số. | chỉ thấy tiêu đề |
| 9 | P.B. Sujit, S. Saripalli, J.B. Sousa, 2014 | IEEE Control Syst. Mag. 34(1):42–59 | https://bibbase.org/network/publication/sujit-saripalli-borgessousa-unmannedaerialvehiclepathfollowingasurveyandanalysisofalgorithmsforfixedwingunmannedaerialvehicles-2014 | Khảo sát và so sánh các thuật toán bám đường cho cánh cố định khi có gió. | chỉ thấy tiêu đề |
| 10 | (arXiv 2405.02011), 2024 | arXiv | https://arxiv.org/pdf/2405.02011 | Bản đồ hoá vùng núi dốc bằng cánh cố định: sai số bám lớn do độ cong và góc bay đổi đột ngột, nhạy với gió. | đã xác minh (trích đoạn) |
| 11 | GPS.gov / FAA | trang chính thức | https://www.gps.gov/node/200 ; https://webarchive.library.unt.edu/web/20170118223614/http://www.gps.gov/systems/gps/performance/accuracy | SPS: ≤ 8 m (95%, trung bình toàn cầu), ≤ 15 m (vị trí xấu nhất); bản 2017: ≤ 9 m; FAA đo ≤ 2,168 m (95%). | đã xác minh |
| 12 | MathWorks, Aerospace Blockset | tài liệu | https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html | Dryden theo MIL-F-8785C, độ cao thấp: W20 = 15/30/45 kt (≈ 7,7/15,4/23,1 m/s) cho nhiễu động nhẹ/vừa/mạnh; σ_w = 0,1·W20. | đã xác minh |
| 13 | R. Beard, T. McLain, 2012 | Princeton Univ. Press, ISBN 978-0-691-14921-9 | https://www.mathworks.com/academia/books/small-unmanned-aircraft-beard.html | Chương 10 "Straight-line and Orbit Following"; mục 4.4 "Atmospheric Disturbances". | đã xác minh (mục lục) |
| 14 | L. Techy, C. Woolsey, 2009 | JGCD 32(6):1736–1746 | 10.2514/1.44580 | Đường thời gian tối thiểu dưới gió đều: cua tối đa là trochoid trong khung mặt đất. | đã xác minh |
| 15 | D. Xu, Y. Sun, D.W.K. Ng, R. Schober, 2020 | IEEE TCOM 68(5) | https://arxiv.org/pdf/1905.10731 ; https://cris.fau.de/publications/238889444/ | Quỹ đạo bền vững: AoD không hoàn hảo do jitter của UAV, gió = ước lượng + sai số bị chặn, vị trí người dùng bất định. | đã xác minh |
| 16 | M.-A. Lahmeri, W.R. Ghanem, C. Bonfert, R. Schober, 2024 | IEEE OJ-COMS | 10.1109/OJCOMS.2024.3396922 | Mô hình thống kê lệch quỹ đạo UAV; MINLP bền vững; mở rộng footprint để chồng lấn. Chưa thấy độ lớn lệch (m). | đã xác minh |
| 17 | Y. Zhang, J. Lyu, L. Fu | arXiv (venue chưa thấy) | https://arxiv.org/abs/2006.01371 ; https://arxiv.org/pdf/2112.13396 | UAV cánh cố định thu dữ liệu phao biển dưới gió: quỹ đạo chu kỳ hình số 8 tận dụng gió; offline theo thống kê gió + online theo gió thực. | đã xác minh |
| 18 | (arXiv 2005.03091) | arXiv | https://arxiv.org/pdf/2005.03091 | Mô hình sai số vị trí bị chặn (worst-case) cho kết quả quá bảo thủ; đề xuất ràng buộc outage xác suất. | đã xác minh (trích đoạn) |
| 19 | (arXiv 2409.15798), 2024 | arXiv | https://arxiv.org/pdf/2409.15798 | Bù sai số định vị bằng channel knowledge map cho nhiệm vụ UAV-IoT. | chỉ thấy tiêu đề |
| 20 | Cui et al., 2018 | IEEE TVT (theo trích đoạn) | https://arxiv.org/abs/1806.06396 | Quỹ đạo và công suất bền vững khi vị trí kẻ nghe lén không chính xác. | chỉ thấy tiêu đề |
| 21 | D. Johnson, Y. Hu, D. Maltz, 2007 | RFC 4728 (DSR) | https://www.rfc-editor.org/rfc/rfc4728 | "Packet Salvaging" (§3.4.1, §8.3.6): node trung gian giữ gói tìm tuyến khác khi tuyến gãy. | đã xác minh (mục lục) |
| 22 | S. Ratnasamy, B. Karp, S. Shenker et al., 2003 | MONET (bản đầu WSNA 2002) | 10.1023/A:1024591915518 | GHT: lưu dữ liệu ở node gần vị trí băm nhất; nhân bản cục bộ; giao thức nhất quán khi topo đổi (perimeter refresh). | đã xác minh |
| 23 | S. Biswas, R. Morris, 2005 | ACM SIGCOMM | 10.1145/1080091.1080108 | ExOR: chọn hop sau khi phát, theo các node thực sự nhận được. | đã xác minh |
| 24 | C. Intanagonwiwat, R. Govindan, D. Estrin, 2000 | ACM MobiCom | 10.1145/345910.345920 | Directed Diffusion: interest được flooding để tìm dữ liệu. | đã xác minh |
| 25 | B. Karp, H.T. Kung, 2000 | ACM MobiCom | 10.1145/345910.345953 | GPSR: định tuyến địa lý dùng vị trí mang trong gói. | đã xác minh |
| 26 | W. Zhao, M. Ammar, E. Zegura, 2004 | ACM MobiHoc | 10.1145/989459.989483 | Message ferrying: node di động mang dữ liệu theo tuyến đã biết. | đã xác minh |

## 3. Mô hình lệch đề xuất và tham số

**Đề xuất cho TMC hoặc IoT-J.** Thay nhiễu trắng làm mượt trừu tượng bằng quỹ đạo sinh từ **mô hình vật lý nhẹ**,
rồi báo cáo phân bố sai số ngang thu được. Reviewer sẽ khó bác hơn vì mỗi tham số đều có nguồn.

1. **Động học:** máy bay đi theo kiểu unicycle với Va không đổi trong khoảng 25–50 m/s, cua phối hợp, |φ| ≤ 45°,
   tốc độ mặt đất = airspeed + gió [Beard & McLain 2012, ch. 10; Xu 2020].
2. **Gió:** gió nền W ∈ {0, 5, 10, 15} m/s với hướng ngẫu nhiên đều. Cộng thêm nhiễu động Dryden theo
   MIL-F-8785C, độ cao thấp, mức nhẹ (W20 = 15 kt) và vừa (W20 = 30 kt) [MathWorks; #7]. Tỉ lệ W/Va = 0,1–0,6
   nằm trong vùng vận hành 20–50% airspeed [#6].
3. **Guidance:** L1 hoặc vector field có bù gió ước lượng [Park; Nelson]. Thêm một biến thể "không bù gió" để
   tạo kịch bản xấu [Beard, 6,5 m].
4. **Kế hoạch:** tour lập bằng Dubins trong không khí lặng (R = 63,7 m). Như vậy phần vượt quỹ đạo ở cua tự xuất
   hiện, đúng bản chất trochoid [Techy & Woolsey].
5. **Định vị trong header:** vị trí GPS cộng nhiễu Gauss, σ ≈ 1–4 m mỗi trục (≈ 2,2–8 m ở mức 95% [GPS.gov]).

**Nếu cần giữ mô hình thống kê** (rẻ hơn khi chạy ns-3), dùng hai thành phần:

- Lệch ngang trên đoạn thẳng là quá trình Gauss–Markov bậc 1 (OU), thời gian tương quan τ ≈ 10–20 s. Tham số này
  nên hiệu chỉnh từ mô phỏng vật lý ở trên, không có nguồn trực tiếp.
- Cộng **độ lệch tất định tại mỗi cua** bằng bán kính trochoid trừ bán kính Dubins, phụ thuộc hướng gió.

| Kịch bản | σ lệch ngang (đoạn thẳng) | Đỉnh lệch tại cua | Căn cứ |
|---|---|---|---|
| Danh nghĩa | 5–20 m | 0–30 m | flight test 1,6–6,5 m + GPS; W ≤ 5 m/s |
| Thận trọng | 50 m | 60–110 m | W = 10 m/s, cua lập trong không khí lặng (tự tính) |
| Stress | 100 m | 100–180 m | W = 15 m/s, Va = 50 m/s, không bù gió |
| Cực đoan (tuỳ chọn) | 200 m | — | không có nguồn trực tiếp; chỉ dùng làm cận phá vỡ |

Cách trình bày gợi ý:
- σ = 50 m là "cận trên thực tế".
- σ = 100 m là "stress có căn cứ vật lý (cua trong gió mạnh)". Takeover nên được chứng minh ở mức này.
- σ = 200 m là "phân tích độ nhạy hoặc điểm gãy".

Bổ sung một trục **lệch dọc tuyến** (±W × thời gian, hoặc OU theo tốc độ mặt đất), hoặc nói rõ là việc phát được
kích hoạt theo vị trí.

## 4. Công trình giống takeover và khác biệt

- **GHT (#22), gần nhất về ý tưởng.** Quyền giữ dữ liệu gắn với một *vị trí*. Khi node chủ hỏng hoặc topo đổi, các
  node trên perimeter có bản sao sẽ thay thế. Khác biệt: GHT chủ động định tuyến dữ liệu tới vị trí băm. Trong
  SigDrop, vị trí phát do gió quyết định; người giữ thực tế được suy ra *sau* từ vị trí UAV trong header, và SPINE
  phải *tìm* họ.
- **DSR packet salvaging (#21).** Sửa cục bộ do node đang giữ gói thực hiện khi kế hoạch (tuyến) gãy. Khác biệt:
  DSR sửa đường đi; takeover sửa *phân công lưu trữ* giữa các cell.
- **ExOR (#23).** Không tin vào phân công trước; quyết định dựa trên ai *thực sự* nhận được. Đây chính là tinh thần
  "người giữ thực tế khác kế hoạch". Khác biệt: ExOR biết người nhận qua batch map và ACK theo thời gian thực;
  SigDrop biết qua vị trí UAV nhúng trong gói và truy vấn trong phạm vi ≤ 3 hop cell.
- **Directed Diffusion (#24).** Flooding interest để tìm nguồn dữ liệu. Truy vấn SPINE là một dạng flooding có
  TTL giới hạn trên lưới cell.
- **GPSR (#25).** Mang vị trí trong gói để ra quyết định địa lý cục bộ. SigDrop dùng vị trí trong gói để *định
  danh người giữ*, không phải để chuyển tiếp.
- **Message ferrying (#26).** Mạng dựa vào tuyến ferry đã biết trước, nên lệch tuyến làm hỏng giả định liên lạc.
  Bài báo nên trích để định vị SigDrop là "ferry phát quảng bá có kế hoạch".
- **Phương án chủ động thay cho takeover:**
  - Lahmeri (#16) mở rộng footprint theo thống kê lệch để luôn có chồng lấn.
  - Xu (#15) và Zhang/Lyu/Fu (#17) đưa gió vào bài toán tối ưu quỹ đạo.

  Nên so sánh takeover (phản ứng, chỉ tốn chi phí khi lệch xảy ra) với một baseline "lề an toàn" (giao gói cho mọi
  cell trong dải ±k·σ quanh quỹ đạo kế hoạch: tốn lưu trữ nhưng không cần truy vấn).

## 5. Rủi ro

1. **Chưa đọc toàn văn.** Mọi số liệu lấy từ trích đoạn tìm kiếm. Riêng #3 (giá trị W cho con số 6,5 m), #5 (tác
   giả) và #8 cần kiểm lại. Muốn đọc toàn văn trong session sau thì phải cho phép `arxiv.org` trong network
   settings.
2. **Không tìm được số liệu bay** cho sai số ngang ở W = 10–15 m/s với UAV 25–50 m/s. Lập luận σ = 100 m dựa trên
   hình học trochoid tự tính, chưa có trích dẫn trực tiếp. Mô phỏng vật lý ở mục 3 sẽ lấp chỗ này.
3. **Nhiễu dừng, trung bình 0, đẳng hướng là sai bản chất.** Lệch thực tế có thiên lệch theo hướng gió và tập trung
   ở cua. Hiệu năng takeover có thể khác, tốt hơn hoặc xấu hơn, khi lệch dồn cục bộ.
4. **Lệch dọc tuyến** có thể lớn hơn mọi lệch ngang nếu ánh xạ gói → cell dựa trên thời gian (mục 1, ý 6).
5. **Nhiễu GPS trong header** (vài mét) có thể làm định danh người giữ sai gần biên cell. Cần so với kích thước cell
   (chưa có trong đề bài).
6. **Reviewer có thể hỏi** vì sao không đưa gió vào lập kế hoạch [Zhang/Lyu/Fu; Techy & Woolsey]. Câu trả lời cần
   có: dự báo gió ở mức tour không chính xác, và takeover là lưới an toàn bổ sung, không thay thế lập kế hoạch có
   gió.
