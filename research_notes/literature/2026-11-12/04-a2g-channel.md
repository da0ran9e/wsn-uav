---
status: reference
updated: 2026-11-12
---
# 04 — Kênh không–đất (A2G) cho 802.15.4 2.4 GHz từ UAV: kiểm tra mô hình SigDrop và giả định A1

Ngày: 2026-11-12. Phạm vi: 25 lượt tìm kiếm web. **Hạn chế lớn:** WebFetch bị chặn (arxiv.org, pmc.ncbi.nlm.nih.gov
không phân giải được trong session này), nên **không đọc được toàn văn bài nào**. Mọi số liệu dưới đây lấy từ tóm tắt
hoặc đoạn trích trong kết quả tìm kiếm. Quy ước trạng thái:
- **đã xác minh (TT)**: thấy tiêu đề, venue/DOI và nội dung cụ thể trong tóm tắt/đoạn trích; chưa đọc toàn văn.
- **chỉ thấy tiêu đề**: chỉ thấy tiêu đề/metadata/link.
- **(TN)**: giá trị theo trí nhớ, KHÔNG thấy trong kết quả tìm kiếm; phải đối chiếu bản gốc trước khi đưa vào paper.
- **(TÍNH)**: chúng tôi tự tính từ công thức hoặc hình học, không phải số đo.

## 1. Tóm tắt

1. **A1 theo gói, phần fading nhỏ (diffuse):** λ = 12,5 cm; gói cách nhau 10 ms ứng với UAV dịch 0,25–0,5 m = 2–4 λ;
   Doppler cực đại 200–400 Hz. Với tán xạ đẳng hướng (Clarke), hệ số tương quan công suất |J0(2π f_D τ)|² ≈ 0,025
   (25 m/s) và 0,013 (50 m/s) (TÍNH), nên vẽ lại fading mỗi gói là hợp lý **chỉ trong trường hợp đẳng hướng**. Trong
   A2G, vật tán xạ tập trung quanh node mặt đất nên **trải góc nhìn từ UAV hẹp** (Δ ≈ R_s/d, ví dụ 10 m/300 m ≈ 0,03 rad).
   Khoảng cách tương quan phía UAV vì vậy cỡ λ/Δ ≈ 4–12 m, tức **khoảng 7–50 gói liên tiếp tương quan** (TÍNH, chưa có
   số đo A2G 2.4 GHz trực tiếp; không tìm được bài đo coherence time A2G ở 2.4 GHz).
2. **A1 theo gói, phần xác định và che khuất:** tia LoS và tia phản xạ đất đổi chậm. Với node cao 1 m, vân giao thoa hai
   tia dài 18 m (r = 100 m) đến 165 m (r = 500 m) đường bay (TÍNH). Che khuất (shadowing) do tán cây, nhà, đổ nát giữ
   gần như không đổi qua hàng chục đến hàng trăm mét: Sun (luận án của nhóm Matolak) ước lượng khoảng dừng (stationarity
   distance) ≈ 15 m. **Kết luận: A1 theo gói không đứng vững như một giả định vật lý.** Phân phối biên mỗi gói có thể
   đúng, nhưng mất gói đến theo cụm. Mô hình hiện tại vì vậy **lạc quan** với các chỉ số kiểu "nhận ≥ 1 gói trong một
   lượt bay" và với phương sai số gói nhận được.
3. **A1 theo node:** fading nhỏ độc lập giữa các node cách nhau > λ/2 là hợp lý, vì phía mặt đất có trải góc rộng. Ngược
   lại, shadowing tương quan theo mô hình Gudmundson ρ = exp(−Δ/d_c), với d_c từ vài chục đến trên 100 m (số 3GPP là TN).
   Ngoài ra có các yếu tố chung phía UAV tác động lên mọi node cùng lúc: búp sóng anten khi máy bay nghiêng cánh, che
   khuất bởi thân máy bay (NASA/Matolak đo độ sâu và thời lượng), nhiễu Wi-Fi (Wen & Dargie: PRR phụ thuộc cả nhiễu
   nền). **A1 theo node đứng được cho fading nhỏ, không đứng được cho shadowing và các hiệu ứng chung.**
4. **Suy hao môi trường cố định là lệch hình dạng:** ở độ cao 100 m, các điểm R50 = 100/200/500/1000 m ứng với góc ngẩng
   45°/27°/11°/6°. Đây đúng là vùng mà xác suất LoS (đường sigmoid của Al-Hourani) và đường đi qua tán cây (∝ 1/sin θ)
   thay đổi mạnh nhất. Mô hình hiện tại **bi quan gần thiên đỉnh, lạc quan ở góc thấp**, nên đường nhận gói thật dốc hơn.
5. **Số mũ suy hao n = 3:** so với số đo A2G có LoS (PLE ≈ 2,1–2,2; 3GPP TR 36.777 coi LoS gần không gian tự do), n = 3
   là **bi quan** cho môi trường mở. Tuy vậy, các thí nghiệm 802.15.4 thật từ drone cho tầm ngắn hơn danh định nhiều:
   Bacco et al. còn khoảng 1/3; Wen & Dargie không lần nào vượt 50 % gói; Nekrasov et al. thấy hướng anten quan trọng.
   n = 3 vì vậy bảo vệ được như một tham số thực nghiệm gộp, với điều kiện phải dẫn các bài này.
6. **K = 2 (≈ 3 dB):** **bi quan** cho LoS mở. Số đo cho K ≈ 12–14 dB ở băng L và 27–29 dB ở băng C (Matolak & Sun,
   trạm đất đặt cao), K tăng theo góc ngẩng, và K(h) = 5,414 ln h − 6,639 dB cho ≈ 18 dB ở 100 m (TÍNH từ công thức
   trích). Ngược lại, K = 2 **lạc quan** khi bị che nặng (20/26 dB): NLoS gần Rayleigh (K = 0), và ở góc ngẩng thấp phản
   xạ đất làm K giảm khoảng 10 dB (Badi et al.).
7. **Thiếu hẳn shadowing log-normal:** σ đo được cho A2G đô thị là 2,8–5,4 dB (FR1/FR3, 2026). Với n = 3, mỗi σ dB làm R50
   của từng node lệch hệ số 10^(σ/30): σ = 6 dB cho ×/÷ 1,58 (TÍNH). Đây có lẽ là độ lệch lớn nhất mà lý thuyết chưa tính.
8. **Tán lá (Weissberger, 2.4 GHz):** 0,58 dB/m cho d ≤ 14 m, sau đó 1,705·d^0,588 dB (TÍNH). Các mức 9/20/26 dB tương
   đương 17/66/103 m đường đi ngang qua cây. Với tán dày 10 m nhìn xiên: 8 dB ở 45°, 17 dB ở 11°, 26 dB ở 6° (TÍNH), nên
   R50 ≈ 350 m. Đã có **dữ liệu thật công khai** để hiệu chỉnh ND2: bộ dữ liệu 802.15.4 2.4 GHz từ UAV của Nekrasov et al.
   trên Dryad.

## 2. Bảng tài liệu

| # | Tác giả, năm | Venue | Link/DOI | Tham số / nội dung dùng được | Trạng thái |
|---|---|---|---|---|---|
| 1 | A. Al-Hourani, S. Kandeepan, S. Lardner, 2014 | IEEE Wireless Commun. Lett. 3(6):569–572 | 10.1109/LWC.2014.2342736 | P_LoS(θ) dạng đóng; độ cao tối ưu theo suy hao cho phép và tham số đô thị "theo ITU" (tức ITU-R P.1410). Tham số sigmoid (a, b) và η_LoS/η_NLoS: ngoại ô (4,88; 0,43; 0,1/21 dB), đô thị (9,61; 0,16; 1/20), đô thị dày (12,08; 0,11; 1,6/23) **(TN, các giá trị này có thể nằm ở bài Globecom 2014 cùng nhóm tác giả)** | đã xác minh (TT); tham số là TN |
| 2 | W. Khawaja, I. Güvenç, D. W. Matolak, U.-C. Fiebig, N. Schneckenburger, 2019 | IEEE COMST 21(3):2361–2391 | 10.1109/COMST.2019.2915069; arXiv 1801.01656 | Tổng quan các chiến dịch đo A2G, fading lớn/nhỏ; ghi nhận K tăng theo góc ngẩng | đã xác minh (TT) |
| 3 | D. W. Matolak, R. Sun, 2017 (Phần III) | IEEE TVT | 10.1109/TVT.2017.2659651; scholarcommons.sc.edu/elct_facpub/317 | K = 12 / 14 dB (băng L) và 27,4 / 28,5 dB (băng C), đô thị gần / ngoại ô; PL dạng log-distance hoặc hai tia; TDL gồm LoS + phản xạ đất + tối đa 7 MPC gián đoạn | đã xác minh (TT) |
| 4 | Matolak & Sun, Phần I (mặt nước) và Phần II (đồi núi) | IEEE TVT 66(1):26–44; 66(3):1913–1925 | scholarcommons.sc.edu/elct_facpub/320 | Phần II: K = 12,8 dB (L), 29,4 dB (C) | đã xác minh (TT) |
| 5 | R. Sun, 2015 (luận án, ĐH South Carolina) | Dissertation | scholarcommons.sc.edu/etd/3655 | Stationarity distance ≈ 15 m; K ≈ 13,1 dB (L), 28,7 dB (C); kênh L và C gần như không tương quan | đã xác minh (TT) |
| 6 | 3GPP TR 36.777 (Rel-15), qua tổng quan X. Lin et al. | arXiv 1805.00826 | arxiv.org/abs/1805.00826 | P_LoS bằng 100 % trên 100 m (UMa-AV) và 40 m (RMa-AV); dưới 22,5 m (UMa/UMi-AV) hoặc 10 m (RMa-AV) dùng mô hình mặt đất; PL ở Bảng B-2, σ shadowing ở Bảng B-3 (chưa đọc). Công thức σ_RMa-AV,LoS = 4,2·exp(−0,0046 h) dB chỉ thấy trong một đoạn trích, chưa đối chiếu | đã xác minh (TT) qua bài tổng quan; bảng số chưa đọc |
| 7 | (nhóm tác giả chưa ghi), 2026 | arXiv 2607.00541 | arxiv.org/abs/2607.00541 | A2G đô thị thấp ở 2,85 / 4,6 / 7,25 GHz: PLE LoS 2,19 / 2,14 / 2,16; σ_SF LoS 4,54 / 3,61 / 2,82 dB, NLoS 5,43 / 4,78 / 2,84 dB; TR 36.777 UMa-AV đánh giá PL thấp hơn số đo | đã xác minh (TT) |
| 8 | M. Gudmundson, 1991 | Electronics Letters 27(23):2145–2146 | 10.1049/el:19911328 | ρ(Δd) = exp(−Δd/d_c). Giá trị khớp trong bài gốc chưa thấy (TN: khoảng vài trăm m cho macro 900 MHz, khoảng 10 m cho microcell) | đã xác minh (TT) về dạng; số là TN |
| 9 | 3GPP TR 38.901 | Spec, bản Rel-19 | 3gpp.org/ftp/specs/PDF/2026-09/Rel-19/38_series/38901-j50.pdf | Khoảng tương quan shadowing (TN): UMa 37/50 m (LoS/NLoS), RMa 37/120 m, UMi 10/13 m | chỉ thấy tiêu đề; số là TN |
| 10 | M. Simunek, F. Pérez Fontán, P. Pechač, 2013 | IEEE Trans. Antennas Propag. 61(7):3850–3858 | 10.1109/TAP.2013.2256098 | UAV góc ngẩng thấp, đô thị: mô hình Loo (Rice + log-normal) có chỉnh sửa, kèm bộ sinh chuỗi thời gian. Đây là khuôn đúng cho ND2 (có tương quan theo thời gian) | đã xác minh (TT); chưa thấy số khoảng tương quan |
| 11 | M. M. Azari, F. Rosas, (…), S. Pollin, 2017 | arXiv 1705.02877 | arxiv.org/abs/1705.02877 | K(θ) không giảm, PLE không tăng theo góc ngẩng | đã xác minh (TT); dạng hàm và tham số chưa đọc |
| 12 | (tác giả chưa thấy), 2019, "3D Trajectory Optimization in Rician Fading for UAV-Enabled Data Harvesting" | arXiv 1901.04106 | arxiv.org/abs/1901.04106 | K = A1·exp(A2·θ), θ = arcsin(z/d), dựa trên số đo của tài liệu [32] trong bài; K nằm trong [A1, A1·e^(A2π/2)]; giá trị A1, A2 chưa đọc | đã xác minh (TT) về dạng |
| 13 | (chưa thấy), 2025, "Trajectory-Aware A2G Channel Characterization for Low-Altitude UAVs Using MaMIMO Measurements" | arXiv 2510.23465 | arxiv.org/abs/2510.23465 | Ngoại ô: K(h) = 5,414·ln h − 6,639 dB, K tăng theo góc ngẩng rồi bão hòa (trạm gốc đặt cao) | đã xác minh (TT) |
| 14 | Aoki & Honda, 2025 | Drones 9(2):86 | mdpi.com/2504-446X/9/2/86 | K ở 2,5 GHz, UAV bay thấp: cao ở môi trường thoáng, giảm mạnh khi có nhà bao quanh (đa phản xạ, nhiễu xạ) | đã xác minh (TT); chưa có số |
| 15 | Badi et al., 2020 | IEEE TVT 69(12) | s2.smu.edu/~camp/pubs/badi_tvt2020.pdf | Phản xạ đất có thể làm K giảm khoảng 10 dB ở góc ngẩng thấp | đã xác minh (TT) qua đoạn trích; tiêu đề chưa thấy |
| 16 | A. Nekrasov, (Allen), E. Belding, 2019 | Sensors 19(16):3479 | 10.3390/s19163479 | XBee3 2.4 GHz, 4 node phát mặt đất, bay đến 122 m, cách ngang ≥ 250 m; tốt nhất ở ≈ 45 m với anten nằm ngang; RSSI dự báo PRR kém | đã xác minh (TT) |
| 17 | (Nekrasov et al.) | Dryad dataset | doi:10.25349/D9KS3W | "Aerial Measurements from Outdoor 2.4GHz 802.15.4 Network": dữ liệu thô để đo PRR và độ cụm | chỉ thấy tiêu đề |
| 18 | J. Wen, W. Dargie, 2020, "Evaluation of the Quality of Aerial Links in Low-Power Wireless Sensor Networks" | IEEE Sensors J. | rn.inf.tu-dresden.de/uploads/Publikationen/impact.pdf | 11 transceiver 802.15.4; RSSI và PRR giảm theo khoảng cách ngang; liên kết đất→không kém khi UAV gần đất; PRR phụ thuộc cả RSSI lẫn nhiễu nền. Bài IoT4Emergency 2020 cùng nhóm: không lần nào vượt 50 % gói | đã xác minh (TT) |
| 19 | M. Bacco, A. Berton, A. Gotta, L. Caviglione, 2018, "IEEE 802.15.4 Air-Ground UAV Communications in Smart Farming Scenarios" | (IEEE Commun. Lett.? venue chưa xác nhận) | openportal.isti.cnr.it/data/2018/389223/2018_389223.postprint.pdf | Di động trên không làm tầm 802.15.4 thực còn khoảng 1/3 danh định | đã xác minh (TT); venue chưa xác nhận |
| 20 | (chưa thấy), MobiQuitous 2014 | EUDL | 10.4108/icst.mobiquitous.2014.257896 | ZigBee CC253x, UAV cao khoảng 3 m, kiểm mô hình hai tia | chỉ thấy tiêu đề |
| 21 | (chưa thấy), URSI AT-AP-RASC 2022 | Proceedings | ursi.org/proceedings/procAT22/ATAPRASC2022-papers/MDG0A59MQB.pdf | LoRa từ UAV qua rừng ngoại ô (độ cao 3/10/30 m): PDR 91 %, mất hết sau ≈ 590 m cho đến bìa rừng ở ≈ 720 m | đã xác minh (TT) |
| 22 | K. Srinivasan et al., 2008, "The β-factor: measuring wireless link burstiness" | ACM SenSys | 10.1145/1460412.1460416 | Phần lớn liên kết 802.15.4 chất lượng trung bình là liên kết cụm; dùng β làm thước đo độ cụm cho ND2 | đã xác minh (TT) |
| 23 | E. J. Weissberger, 1982 | Báo cáo DTIC ADA118343 | apps.dtic.mil/sti/pdfs/ADA118343.pdf | L = 0,45 f^0,284 d (0 < d ≤ 14 m); 1,33 f^0,284 d^0,588 (14 < d ≤ 400 m); f tính bằng GHz, áp dụng 230 MHz–95 GHz; cây nằm trên đường truyền ngang | đã xác minh (TT) về công thức |
| 24 | ITU-R P.833-10 (2021-09) | Khuyến nghị ITU-R | itu.int/dms_pubrec/itu-r/rec/p/R-REC-P.833-10-202109-I!!PDF-E.pdf | A_ev = A_m[1 − exp(−dγ/A_m)]; bảng γ từ 0,04 đến 0,34 dB/m theo tần số và loại đường truyền (không có đúng 2,4 GHz). A_m = 0,18·f^0,752 (f tính bằng MHz), cho ≈ 63 dB ở 2,4 GHz (TN) | đã xác minh (TT); A_m là TN |
| 25 | (chưa thấy), 2024, "Measurement-based fading characterization of multi-link UAV to mobile vehicle channel" | Physical Communication | aminer.org/pub/656dd497939a5f4082002ad1 | Băng hẹp 2,4 và 5,9 GHz: PL, shadowing, K, tương quan chéo giữa các liên kết. Ứng viên tốt nhất cho số K và tương quan ở 2.4 GHz | chỉ thấy tiêu đề |
| 26 | (chưa thấy), 2024, "Mitigating the Impact of UAV Fluctuations on A2G Wireless Communications in the Presence of Channel Aging" | JCIS (SBrT) | jcis.sbrt.org.br/jcis/article/view/886 | Rung lắc UAV làm thay đổi hàm tự tương quan và coherence time, ảnh hưởng mạnh ở tần số cao | đã xác minh (TT) |

Chưa tra trong ngân sách: ITU-R P.1410 và P.1411 (chỉ biết gián tiếp qua bài #1), bài Goddemeier & Wietfeld (Globecom
Workshops 2015, mô hình Rice riêng cho UAV, chỉ thấy bản ghi dblp), và mô hình suy hao xuyên đổ nát hay công trình.

## 3. Bảng tham số đề xuất cho ND2 ("kênh thật lệch mô hình")

Nguyên tắc: giữ nguyên ngưỡng −101 dBm và công suất phát 10 dBm, mỗi lần thay một yếu tố, rồi báo độ lệch của R50, của
xác suất nhận ≥ 1 gói mỗi lượt bay, và của phương sai số gói nhận.

| Yếu tố | Hiện tại | Giá trị quét đề xuất | Cơ sở |
|---|---|---|---|
| PLE sau 100 m | 3 | 2,2 / 2,5 / 3 / 3,5 | #6, #7 (LoS ≈ 2,1–2,2); #18, #19 (tầm thực ngắn) |
| Suy hao môi trường theo góc ngẩng | hằng 0/9/20/26 dB | (a) η_LoS·P_LoS(θ) + η_NLoS·(1 − P_LoS(θ)) với tham số sigmoid của #1 (TN); (b) tán lá xiên: Weissberger(h_c / sin θ), h_c = 5 / 10 / 20 m, chặn trên bằng A_m của P.833 | #1, #23, #24 |
| K-factor | 2 (3 dB) cố định | K(θ) = A1·exp(A2·θ), quét K(0°) = 0 dB và K(90°) = 10 / 15 dB; K = 0 (Rayleigh) cho môi trường 20 và 26 dB | #3–#5, #12, #13, #15 |
| Shadowing log-normal (mỗi node, mỗi lượt bay) | không có | σ = 0 / 3 / 6 / 8 dB | #7 (2,8–5,4 dB); thêm cho tán lá và đổ nát (giả định) |
| Tương quan shadowing giữa các node | độc lập | ρ = exp(−Δ/d_c), d_c = 10 / 37 / 120 m | #8, #9 (TN) |
| Tương quan shadowing theo đường bay | không có | AR(1) theo quãng bay, d_c,bay = 15 / 50 / 200 m | #5 (15 m); hình học (TÍNH) |
| Tương quan fading nhỏ giữa các gói | ρ = 0 | Gauss–Markov ρ_gói = J0(2π·(v/λ)·Δ·τ) với Δ = 1 (Clarke) / 0,1 / 0,03 rad, tương đương ρ_gói ≈ 0 / 0,6 / 0,96 ở 25 m/s (TÍNH) | lập luận ở mục 1.1; #10 (khuôn chuỗi thời gian) |
| Phản xạ đất xác định | không có | thêm tia hai tia với độ cao node 0,3 / 1 m | #3 (TDL có phản xạ đất), #20 |
| Hiệu ứng chung phía UAV (búp anten, nghiêng cánh, nhiễu) | không có | Gilbert–Elliott chung cho mọi node, trạng thái xấu kéo dài 20–200 ms, chiếm 5–20 % thời gian (giả định, cần đo) | #16, #18, #22 |
| Hiệu chỉnh bằng dữ liệu thật | — | khớp PRR theo khoảng cách và β từ bộ dữ liệu Dryad | #17 |

Ghi chú: thời lượng gói tối đa 4,26 ms. Với Clarke ở 400 Hz, coherence time ≈ 1 ms nên fading thay đổi ngay trong một
gói. Giả định "fading khối mỗi gói" chỉ đúng khi trải góc nhìn từ UAV hẹp, tức đúng trường hợp làm A1 theo gói yếu đi.

## 4. Rủi ro

- **Chưa đọc toàn văn:** mọi số lấy từ tóm tắt hoặc đoạn trích. Các số đánh dấu TN (tham số Al-Hourani, khoảng tương quan
  của 3GPP và Gudmundson, A_m của P.833) phải kiểm trước khi trích. Cần mở lại arxiv.org/PMC hoặc tải PDF thủ công.
- **Lệch hình học:** phần lớn số đo A2G (Matolak, 3GPP, MaMIMO) dùng trạm đất đặt cao hoặc trạm gốc ở băng L/C hay
  di động tế bào. Node camera ở độ cao 0,3–1 m dưới tán lá hay đổ nát sẽ có K thấp hơn và PLE cao hơn, nên áp số đo
  thẳng vào sẽ lạc quan.
- **Lỗ hổng tài liệu:** không tìm được số đo trực tiếp coherence time hay tương quan gói A2G ở 2.4 GHz cho UAV 25–50 m/s.
  Lập luận "trải góc hẹp" là của chúng tôi; phản biện có thể đòi số đo, nên ND2 nên đo chính độ cụm này (β, độ dài cụm mất).
- **Weissberger** xây dựng cho đường truyền ngang qua rừng, việc áp cho đường xiên qua tán là ngoại suy. Gió lay lá gây
  fading thời gian độc lập với chuyển động UAV (chưa tra).
- **Đổ nát và đô thị đổ sập:** chưa có mô hình A2G nào được kiểm. Các mức 20/26 dB hiện chưa có nguồn.
- **Nguy cơ phản biện về A1:** nếu giữ A1 trong phần lý thuyết, cần (i) gọi tên A1 là xấp xỉ cho phần diffuse, (ii) thêm
  một biến ngẫu nhiên shadowing cho mỗi node và mỗi lượt bay (mô hình điều kiện), và (iii) cho kết quả độ nhạy ND2 với
  ρ_gói và d_c.
- Fixed-wing nghiêng cánh khi vòng có thể đưa node vào null của anten. Matolak/NASA có đo che khuất do thân máy bay
  nhưng chưa lấy được số.
