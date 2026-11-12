---
status: current
updated: 2026-11-12
---
# Tổng hợp tìm tài liệu cho kế hoạch tiếp theo (2026-11-12)

Tài liệu này gom kết quả của 8 phiên tìm tài liệu chạy song song (chatlog mục 305). Đây là tài liệu tham khảo cho thảo
luận và chưa sửa đề cương; người dùng quyết định phần nào đưa vào. Chi tiết, bảng tài liệu và link nằm trong
`2026-11-12/01…08-*.md`.

**Giới hạn chung.** Mạng của session chặn việc tải toàn văn từ arxiv.org, NCBI/PMC, dblp, Crossref và nhiều trang khác.
Vì vậy mọi số liệu đều lấy từ abstract hoặc đoạn trích trong kết quả tìm kiếm. Nhãn "đã xác minh" trong các file chỉ có
nghĩa là đã thấy abstract hoặc bản ghi thư mục, chưa đọc bài. Trước khi trích một con số vào bài, phải đọc bản gốc. Một
số tham số trong file 04 được đánh dấu (TN) vì lấy từ trí nhớ của phiên tìm, chưa có nguồn.

## 1. Định vị đóng góp: rủi ro trùng lặp và phần còn mới

Rủi ro trùng lặp lớn nhất là Wang et al. (IEEE IoT-J 2020, DOI 10.1109/JIOT.2020.2994549). Trong bài này, UAV treo tại chỗ
và multicast bằng NOMA, sau đó người dùng mặt đất chia sẻ khối dữ liệu với nhau qua D2D một chặng để rút ngắn thời gian
nhiệm vụ. Ý tưởng "mặt đất hợp tác sau khi UAV phát" vì vậy đã có. Dòng multicast từ UAV (Zeng–Xu–Zhang, TWC 2018, có
RLNC) gần như trùng baseline FC của chúng ta, nên phải trích. Về phía WSN, Typhoon (EWSN 2008: unicast, nghe ké, đổi
kênh) và MNP (ICDCS 2005: node ngủ khi hàng xóm gửi đoạn không cần) cho thấy unicast và ngủ theo lịch không còn là ý mới.
LWB (SenSys 2012) có lịch do trạm gốc lập, là công trình gần River nhất về mặt "lập kế hoạch tập trung".

Phần SigDrop còn giữ được tính mới, theo những gì tìm thấy:
- chuyển tiếp nhiều chặng theo một kế hoạch toàn cục tính sẵn, gắn với quỹ đạo của một lượt bay duy nhất;
- UAV cánh bằng không treo tại chỗ, và mục tiêu là tập critical cell chứ không phải mọi node;
- takeover: chưa có tiền lệ trực tiếp, chỉ có các cơ chế tương tự (GHT, packet salvaging trong DSR, ExOR, Directed
  Diffusion);
- định lý crossover giữa hợp tác mặt đất và bay vòng khi có bài toán quỹ đạo (bản một chặng không có quỹ đạo đã có:
  Stojanovic et al., TWC 2009);
- trong các bài TMC và IoT-J gần đây, chưa thấy bài nào về UAV cánh bằng gửi truy vấn xuống mạng 802.15.4. Phần lớn là
  UAV cánh quay thu dữ liệu lên. Tìm kiếm này chưa đầy đủ.

Câu hỏi "River thắng Deluge nhờ đâu" (chatlog mục 304) khớp với tài liệu. Các bản cải tiến Deluge trên CSMA (Rateless
Deluge, AdapCode, Typhoon) cũng thu lợi chủ yếu từ việc cắt dữ liệu dư. Cần nói thêm rằng kéo trực tiếp có kế hoạch đã
ngang River, nên đóng góp nằm ở việc lập kế hoạch tập trung.

## 2. Baseline cho J1

Deluge (2004) là baseline cũ. Splash (NSDI 2013) nhanh hơn DelugeT2 khoảng 21 lần, Pando (ToN 2017) còn nhanh hơn nữa;
cả hai dùng truyền đồng bộ (constructive interference), thứ ns-3 không mô phỏng được. Phiên 02 đề xuất:

| Baseline | Vai trò | Làm trên |
|---|---|---|
| Deluge công bằng: cùng tập cell đích, có chế độ LPL/ContikiMAC, quét Imin và cỡ page, tuỳ chọn fountain code | bắt buộc, trả lời phản biện "baseline yếu" | ns-3 hiện có |
| Kiểu Typhoon (unicast + nghe ké + đổi kênh) | baseline CSMA mạnh nhất gần River | ns-3 lr-wpan |
| Splash/Pando dạng mô hình lý tưởng theo slot | cận trên, chỉ để thảo luận | Python |
| CoAP block-wise unicast theo từng cell | cách Thread/LwM2M làm thật, rẻ | ns-3 |

## 3. Lý thuyết

- **L1:** trích Le Ny, Feron, Frazzoli, IEEE TAC 57(1):265–270, 2012, DOI 10.1109/TAC.2011.2166311. Bài này chứng minh
  Dubins TSP qua các điểm là NP-khó, chưa phải bản có lân cận. Phép quy trong sổ thử nghiệm (cho r → 0) đi đúng hướng
  này, nhưng câu chữ phải nói đúng điều đã được chứng minh. L1 chỉ đáng là một bổ đề. Có thuật toán DTSP-N (Váňa–Faigl
  2015, Isaacs–Hespanha 2013) và cận dưới (Manyam–Rathinam) để báo khoảng cách tối ưu của CHORD và LM-Tour.
- **A:** có thể làm chặn dưới chặt hơn bằng cực đại của các biến nhị thức âm, thêm số hạng cỡ √(Q ln m), khớp với
  scaling log của Ghaderi 2008 và Swapna 2013. Việc này bổ sung cho hướng đã ghi trong sổ thử nghiệm (biên an toàn theo
  file, gói nhận khi bay ngang).
- **D:** chặn min-cut là kiến thức chuẩn (Ahlswede 2000; Lun–Médard–Koetter–Effros 2008). Khung gần nhất là coded
  cooperative data exchange đa chặng (Courtade–Wesel, IEEE TIT 2014): node đã có sẵn một phần gói, giống cell sau lượt
  bay, và điều kiện cắt có đúng dạng missing_k(S)/c(S). Phần có thể mới là chứng minh River chỉ kém tối ưu một hằng số
  khi có tranh chấp kênh, theo mẫu Gandhi et al. 2003 và Haeupler 2011.
- **C:** Gallager 1976 (DOI 10.1109/TIT.1976.1055588) là tiền lệ trực tiếp. Không nên khẳng định Ω(H(X)) cho mọi giao
  thức có khám phá; chặn dưới đúng có dạng H(f(X)) hoặc theo lát cắt. Góc mới là đo chi phí thu thập side information,
  thứ các bài CDE và index coding giả định là miễn phí. Phía đạt được có thể dùng set reconciliation (Minsky et al. 2003).

## 4. Mô hình kênh và giả định A1

- **A1 giữa các gói không đứng được như một giả định vật lý.** Nếu tán xạ đẳng hướng, hai gói cách nhau 2–4 bước sóng
  gần như độc lập. Nhưng ở A2G, vật tán xạ dồn quanh node mặt đất, nên phiên 04 ước lượng khoảng 7–50 gói liên tiếp còn
  tương quan, và tia LoS cùng che khuất gần như không đổi trên hàng chục tới hàng trăm mét bay. Đây là ước lượng hình
  học, chưa có số đo ở 2,4 GHz. Hệ quả: mô hình hiện tại lạc quan với chỉ số "nhận ít nhất 1 gói" và với phương sai số
  gói nhận.
- **Giữa các node,** A1 đúng cho fading nhanh nhưng sai cho che khuất. Khoảng tương quan của che khuất (Gudmundson) là
  vài chục tới hơn 100 m, cỡ một cell.
- **Mô hình lệch theo cả hai chiều.** Suy hao môi trường đang cố định theo khoảng cách, trong khi thực tế phụ thuộc góc
  ngẩng (Al-Hourani P_LoS(θ), tán lá tỉ lệ 1/sin θ). Mô hình vì vậy bi quan gần thiên đỉnh và lạc quan ở góc thấp. K = 2
  bi quan khi LoS mở (số đo 12–29 dB) nhưng lạc quan khi bị che nặng. Mô hình còn thiếu che khuất log-normal (σ đo được
  2,8–5,4 dB).
- **Thực địa:** khi UAV đang bay, tầm 802.15.4 dùng được chỉ còn khoảng 1/3 danh định (Bacco 2018). Tay điều khiển
  2,4 GHz của drone gây nhiễu 802.15.4 (Wen & Dargie 2020).
- **Có dữ liệu thật để hiệu chỉnh:** bộ đo 802.15.4 2,4 GHz từ UAV trên Dryad, doi:10.25349/D9KS3W. File 04 có bảng
  tham số đề xuất cho ND2: hệ số suy hao, K(θ), σ che khuất, khoảng tương quan, tán lá Weissberger, mô hình
  Gilbert–Elliott.

## 5. Độ lệch quỹ đạo do gió

- Thử bay thực tế cho sai số bám đường khoảng 1,6–6,5 m (Park et al.; Nelson et al.; Beard et al.), sai số GPS dưới 8 m.
  σ = 50 m vì vậy đã là cận trên an toàn, và kết luận "σ ≤ 50 m không gãy gì" đứng vững.
- σ = 100 m có cơ sở vật lý nhưng chỉ ở các khúc quay: quay trong gió tạo đường trochoid (Techy & Woolsey 2009). Theo
  tính toán của phiên 05, tour lập trong điều kiện lặng gió quay vượt 61–176 m khi gió 10–15 m/s.
- Không có nguồn nào cho σ = 200 m kéo dài suốt tour (với nhân 10 s, mức này tương đương sai số hướng khoảng 34° RMS).
  Nên trình bày σ = 200 m như trường hợp thử ngưỡng gãy.
- Mô hình đề xuất cho J1: sinh quỹ đạo từ mô hình bay (góc nghiêng ≤ 45°, dẫn đường L1, gió đều 0–15 m/s cộng nhiễu loạn
  Dryden ở mức nhẹ và vừa). Cần thêm sai số dọc đường bay: nếu gán gói cho cell theo thời điểm phát thì lệch dọc có thể
  tới hàng trăm mét. Phương án chủ động để so với takeover là mở rộng vùng phủ theo thống kê độ lệch (Lahmeri et al.,
  OJ-COMS 2024).

## 6. Triển khai (J2, ND0)

- Nhận dạng người trên vi điều khiển tốn khoảng 0,2–1,6 mJ mỗi lần suy luận. Chưa thấy bài nào làm person re-ID trên
  MCU; đây là khoảng trống cho J2, nhưng chi phí nạp và đối sánh truy vấn 400 KB phải tự đo.
- Không testbed 802.15.4 công cộng nào có drone bay trên các node (FIT IoT-LAB, FlockLab 2, D-Cube, Indriya2). AERPAW có
  drone nhưng dùng SDR, LTE, LoRa.
- Đề xuất: chạy pha 0 (cell, tô màu kênh, TSCH) ở quy mô lớn trên FIT IoT-LAB, cộng 20–50 node ngoài trời tự dựng và một
  drone nhiều cánh quạt. Phần cứng gợi ý mỗi node: nRF52840 dongle (khoảng 10–16 USD) và Grove Vision AI V2
  (15,99 USD, khoảng 0,35 W, 33 ms mỗi lần suy luận); gateway hai radio, cluster head có thêm LoRa.
- Độ cao tốt nhất cho 802.15.4 từ drone khoảng 45 m, với anten thu song song mặt đất (Nekrasov, Sensors 2019).

## 7. Nơi nộp và lịch

| Mốc | Nơi | Ghi chú |
|---|---|---|
| 20/1/2027 tóm tắt, 27/1/2027 bài | DCOSS-IoT 2027, Montreal, 21–23/6/2027, CORE B | lấy từ trang chính thức qua đoạn trích, cần mở lại để chốt |
| khoảng 1/2/2027 | VTC2027-Fall, Osaka, 27–30/9/2027 | từ trang tổng hợp, chưa xác minh |
| khoảng 16/4/2027 | LCN 2027, Daytona Beach | từ trang tổng hợp, chưa xác minh |
| đã qua (9/2026) | WCNC 2027, VTC2027-Spring | — |
| chưa công bố | MASS, ISCC, PIMRC, MSWiM, EWSN 2027 | file 07 ước theo năm trước |

- Theo CORE2023, MSWiM là A, ISCC là C, các hội nghị còn lại là B.
- Tạp chí (IF theo trang tổng hợp): TWC 10,7; TMC khoảng 9; IoT-J 8,7; TNSE 7,9; TVT 7,5; Ad Hoc Networks 4,8.
- Không có quy tắc "30 % nội dung mới" chính thức. IEEE yêu cầu nội dung mới đáng kể và trích bài hội nghị. IoT-J yêu
  cầu nộp kèm bài hội nghị có đánh dấu phần mới, và thu 175 USD mỗi trang vượt 8 trang.
- Bài TMC và IoT-J gần đây dài khoảng 15 trang.
- Lịch phiên 07 đề xuất: C1 DCOSS-IoT (1/2027), C2 VTC-Fall (2/2027), C3 PIMRC (khoảng 3/2027), C4 LCN hoặc MASS
  (4–5/2027), C5 MSWiM (khoảng 6/2027, chỉ dùng nội dung J1 không dùng), J1 nộp TMC 6–7/2027, J2 nộp IoT-J cuối 2027.
  Lịch này dày hơn kế hoạch hiện tại của đề cương; cần bàn.

## 8. Tài liệu tham khảo của đề cương

Phiên 08 kiểm 28 mục: 22 mục đúng (bỏ được nhãn "[cần kiểm tra]" ở [14], [16], [20], [21], [28]); 5 mục cần sửa ([2]
tiêu đề bị cắt, [19] tên tác giả là W. R. Heinzelman, [22] phải dùng tiêu đề RFC 9030 đã xuất bản, [26] bổ sung đủ
thông tin IEEE TII 2023, [27] là Z. Qiu et al., WCMC 2017); 1 mục chưa xác minh ([23], IEEE 802.15.4-2020). Có ba chỗ
trích dẫn không khớp: [3] không được trích trong thân bài; abstract của [16] không nói DTSP-N NP-khó; abstract của [27]
không nhắc Nakagami. File 08 có danh mục sửa sẵn để dán. Đề cương chưa được sửa.

## 9. Việc nên cân nhắc cho kế hoạch tiếp theo

Xếp theo mức ảnh hưởng tới J1:
1. **Định vị lại đóng góp** so với Wang 2020, LWB, Typhoon và MNP; đọc toàn văn Wang 2020 trước khi viết phần related work.
2. **Nâng baseline:** Deluge công bằng (LPL, cùng tập đích) và một bản kiểu Typhoon trong ns-3.
3. **Mô hình kênh:** thêm che khuất log-normal có tương quan không gian và fading tương quan theo thời gian, rồi xem kết
   quả River có đổi chiều không. Đây cũng là phép thử độ bền của định lý A khi bỏ A1.
4. **Mô hình gió:** sinh quỹ đạo từ mô hình bay có gió đều và Dryden thay cho nhiễu Gauss; thêm sai số dọc đường bay.
5. **Sửa phát biểu định lý:** L1 (DTSP qua điểm), C (H(f(X)) thay cho H(X)), D (khung CDE của Courtade–Wesel).
6. **Lịch nộp:** quyết định có nộp DCOSS-IoT tháng 1/2027 hay không.

Việc 2–4 cần chạy mô phỏng, nên phải thảo luận chi phí trước khi chạy.
