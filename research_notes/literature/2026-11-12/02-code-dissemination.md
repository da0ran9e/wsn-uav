---
status: reference
updated: 2026-11-12
---
# 02 — Phát tán dữ liệu lớn / mã trong WSN-IoT: state of the art và baseline công bằng cho River

Ngày: 2026-11-12. Phạm vi: Deluge và họ của nó, mã hoá (fountain/RLNC), truyền đồng bộ (CT), MAC low-power listening,
OTA hiện đại, phát tán có lập lịch tập trung, UAV.

**Lưu ý về xác minh:** trong phiên này WebFetch bị chặn (arxiv.org, comp.nus.edu.sg không thuộc mạng được phép), nên
không mở được PDF nào. "đã xác minh" nghĩa là tôi thấy tóm tắt hoặc metadata (tác giả, venue, DOI, số liệu) trong kết quả
tìm kiếm trỏ tới đúng URL đó, không phải đã đọc toàn văn. Số liệu nên được kiểm lại trong PDF trước khi đưa vào paper.
Nếu cần đọc toàn văn, phải cho phép `arxiv.org` và `www.comp.nus.edu.sg` trong network settings của session.

## 1. Tóm tắt

1. **Deluge (2004) đã bị vượt xa từ lâu về tốc độ.** Splash (NSDI 2013) phát 32 KB tới 139 node (tới 9 hop) trong khoảng
   25 s, nhanh hơn DelugeT2 trung bình 21× (tốt nhất 57,8×). Pando (ToN 2017) nhanh hơn state of the art thêm 3,5×. Chính
   phần mở đầu của Splash viết rằng Deluge có thể mất tới một giờ để nạp mã cho mạng 100 node. Phản biện TMC/IoT-J biết
   những con số này.
2. **Họ CSMA "sửa Deluge" chủ yếu giảm dữ liệu thừa, không phải control.** Rateless Deluge (IPSN 2008) tiết kiệm
   15–30 % ở mặt phẳng dữ liệu nhưng 50–80 % ở mặt phẳng điều khiển. AdapCode dùng ít hơn tới 40 % gói so với Deluge.
   Typhoon (unicast + nghe lén + đa kênh) giảm tới 3× cả thời gian lẫn năng lượng. Kết quả này **khớp với phân tích của
   ta**: control chỉ khoảng 5 %, phần lớn lợi thế nằm ở dữ liệu dư. Có thể trích để củng cố lập luận.
3. **Typhoon là "họ hàng" gần nhất của River trong thế giới CSMA:** dữ liệu gửi unicast, node khác nghe lén, đổi kênh để
   tăng tái sử dụng không gian, và có lập luận năng lượng dựa trên idle listening. Cần định vị River so với Typhoon (River
   có kế hoạch toàn cục từ trạm gốc, Typhoon thì cục bộ).
4. **LWB (SenSys 2012) là tiền lệ "lập lịch tập trung" quan trọng nhất:** trạm gốc lập lịch, mỗi slot là một lần Glossy
   flood. River khác ở chỗ lập kế hoạch theo đường cell và theo phạm vi cụm, chứ không flood toàn mạng. Mixer (SenSys
   2018, RLNC + CT) nhanh hơn tới 65 % và giảm radio-on tới 50 % so với state of the art.
5. **MNP (ICDCS 2005) đã có cơ chế ngủ khi hàng xóm gửi segment không cần thiết** và chọn một người gửi mỗi vùng. Phản
   biện có thể nói "ngủ" không phải điểm mới, nên phải nhấn vào chỗ ngủ **theo lịch dự tính trước**.
6. **MAC duty-cycling làm Trickle chậm đi đáng kể:** CSMA/CA kết hợp ContikiMAC có thể khiến node bị "đói" bản tin
   Trickle, gây độ trễ lan truyền lớn (Stolikj et al., EWSN 2015). Nếu thêm LPL cho Deluge để so năng lượng công bằng, thời
   gian của Deluge sẽ còn tệ hơn. Đây là lợi thế cho ta, nhưng phải mô hình hoá thì mới nói được.
7. **OTA công nghiệp (Thread/LwM2M) vẫn là unicast CoAP block-wise từng thiết bị.** LwM2M bắt buộc block-wise khi có
   Firmware Update object. Không thấy chuẩn multicast bulk nào cho TSCH/6TiSCH. Kế hoạch multicast có lập lịch thành thục
   nhất là LoRaWAN FUOTA. Không tìm thấy đánh giá học thuật nào của OTA trên Thread trong 2023–2025 có số liệu về thời
   gian và năng lượng.
8. **Code và mô phỏng:** không tìm thấy module ns-3 nào cho Deluge hay Trickle. Có Deluge trong Contiki (`apps/deluge`),
   Rateless Deluge trong TinyOS (BU NISLab), và Mixer công bố mã (mixer.nes-lab.org, bản TelosB). ns-3 lr-wpan không mô hình
   constructive interference, nên không mô phỏng trung thực được Splash/Pando/Mixer.

## 2. Bảng tài liệu

| # | Tài liệu (tác giả, năm, venue) | Link / DOI | Số liệu chính | Mã nguồn | Xác minh |
|---|---|---|---|---|---|
| 1 | J. W. Hui, D. E. Culler, "The Dynamic Behavior of a Data Dissemination Protocol for Network Programming at Scale", SenSys 2004, pp. 81–94 | https://www.sciweavers.org/node/129419 | Epidemic, theo page, NACK, spatial multiplexing. Tác giả cho rằng "rất khó cải thiện đáng kể" tốc độ của Deluge | Có: Contiki `apps/deluge/deluge.c` (https://git.denkn.at/deac/osd-contiki/src/commit/031c45994b0986963222b957a98cb9a66b6924f8/apps/deluge/deluge.c); DelugeT2 trong TinyOS (theo Splash) | đã xác minh |
| 2 | P. Levis et al., "Trickle: A Self-Regulating Algorithm for Code Propagation and Maintenance in WSNs", NSDI 2004 | https://csl.stanford.edu/~pal/pubs/trickle-nsdi04 | Đánh giá bằng TOSSIM và mica-2 | Thuật toán đơn giản, dễ cài lại | đã xác minh |
| 3 | P. Levis, T. Clausen, J. Hui, O. Gnawali, J. Ko, RFC 6206 "The Trickle Algorithm", 2011 | https://www.rfc-editor.org/rfc/rfc6206 | Chuẩn Proposed Standard; tham số Imin, Imax, k | — | đã xác minh |
| 4 | S. S. Kulkarni, L. Wang, "MNP: Multihop Network Reprogramming Service for Sensor Networks", ICDCS 2005, pp. 7–16 | DOI 10.1109/ICDCS.2005.50; PDF https://websrv.cecs.uci.edu/~papers/icdcs05/02_kulkarnis_mnp.pdf | Chọn tối đa một người gửi mỗi vùng, pipelining, ngủ khi hàng xóm gửi segment không cần; Mica-2/XSM, TOSSIM. Bản TOSN 2009 thêm chế độ ngủ | Không thấy | đã xác minh |
| 5 | T. Stathopoulos et al., "A Remote Code Update Mechanism for WSNs" (MOAP), 2003 | https://ant.isi.edu/~johnh/PAPERS/Stathopoulos03b.html | Giảm 60–90 % số lần truyền so với flooding | Không thấy | đã xác minh |
| 6 | C.-J. M. Liang, R. Musăloiu-E., A. Terzis, "Typhoon: A Reliable Data Dissemination Protocol for WSNs", EWSN 2008, LNCS 4913, pp. 268–285 | DOI 10.1007/978-3-540-77690-1_17; PDF https://www.cs.jhu.edu/~razvanm/ewsn2008typhoon.pdf | Unicast + nghe lén + đa kênh + timer theo không gian; nhanh hơn và tiết kiệm năng lượng tới 3× so với Deluge, rõ nhất ở mạng thưa, nhiều mất gói | Không xác minh | đã xác minh |
| 7 | A. Hagedorn, D. Starobinski, A. Trachtenberg, "Rateless Deluge: OAP of WSNs Using Random Linear Codes", IPSN 2008, pp. 457–466 | DOI 10.1109/IPSN.2008.9; https://sites.bu.edu/nislab/projects/rateless-deluge | Tmote Sky, mất gói 7 %: tiết kiệm 15–30 % dữ liệu, 50–80 % control so với Deluge. Có thêm ACKless Deluge | Có, TinyOS (BU NISLab) | đã xác minh |
| 8 | I.-H. Hou, Y.-E. Tsai, T. Abdelzaher, I. Gupta, "AdapCode: Adaptive Network Coding for Code Updates in WSNs", INFOCOM 2008, pp. 1517–1525 | DOI 10.1109/INFOCOM.2008.211; https://www.ideals.illinois.edu/items/11396 | Ít hơn tới 40 % gói so với Deluge trên mạng lớn | Không thấy | đã xác minh |
| 9 | M. Rossi et al., "SYNAPSE" (SECON 2008) và "SYNAPSE++: Code Dissemination in WSNs Using Fountain Codes" (IEEE TMC 2010) | https://www.dei.unipd.it/~rossi/papers/SYNAPSE-SECON2008.pdf ; https://www.dei.unipd.it/~rossi/papers/TMC_SYNAPSE_2010.pdf | Fountain code trên GF(2). Theo một bài khác (arXiv 1702.02364), giải mã nhanh hơn ít nhất 6,5× so với Rateless Deluge GF(2^8) | Không thấy | đã xác minh (tiêu đề + mô tả ngắn) |
| 10 | M. Doddavenkatappa, M. C. Chan, B. Leong, "Splash: Fast Data Dissemination with Constructive Interference in WSNs", NSDI 2013, pp. 269–282 | https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/doddavenkatappa | Indriya 139 node và Twist 90 node; 32 KB trong khoảng 25 s; trung bình nhanh hơn DelugeT2 21× (tốt nhất 57,8×); goodput 10,1 kbit/s mỗi node, tới 9 hop | Không xác minh | đã xác minh |
| 11 | W. Du, J. C. Liando, H. Zhang, M. Li, "When Pipelines Meet Fountain" (SenSys 2015) và "Pando: Fountain-Enabled Fast Data Dissemination with Constructive Interference" (IEEE/ACM ToN 25(2):820–833, 2017) | DOI 10.1145/2809695.2809721 ; DOI 10.1109/TNET.2016.2614707 | Fountain code + pipeline CT + đổi kênh theo từng gói; phản hồi dựa trên im lặng; độ tin cậy 100 %; nhanh hơn state of the art 3,5×; Contiki/TelosB trên Indriya và Flocklab | Không xác minh | đã xác minh |
| 12 | Yuan, Hollick, "Ripple" (flooding thông lượng cao, Reed-Solomon) | https://manuscript.isc.ac/Inventory/49/722615.htm | Khoảng 3× thông lượng và hiệu quả năng lượng; thông lượng có mã hoá gấp 2–3× Splash; chạy được trên TelosB | Không thấy | đã xác minh (bản ghi tóm tắt; venue chưa thấy) |
| 13 | F. Ferrari, M. Zimmerling, L. Thiele, O. Saukh, "Efficient Network Flooding and Time Synchronization with Glossy", IPSN 2011 | https://www.aminer.org/pub/53e999d2b7602d9702215d8f/efficient-network-flooding-and-time-synchronization-with-glossy | Flood xong trong vài ms; sai số đồng bộ dưới 1 µs | Không xác minh | đã xác minh |
| 14 | F. Ferrari, M. Zimmerling, L. Mottola, L. Thiele, "Low-Power Wireless Bus", SenSys 2012 | https://re.public.polimi.it/handle/11311/691959 ; bản cài Contiki: https://arxiv.org/pdf/1607.06622 | Bộ lập lịch tập trung (sink); mỗi slot một lần Glossy flood; hỗ trợ 1–1, 1–n, n–1, n–n | Có bản cài Contiki/Sky (arXiv 1607.06622) | chỉ thấy tiêu đề và metadata (mô tả từ nguồn thứ cấp); chưa thấy DOI |
| 15 | O. Landsiedel, F. Ferrari, M. Zimmerling, "Chaos: Versatile and Efficient All-to-All Data Sharing and In-Network Processing at Scale", SenSys 2013 | DOI 10.1145/2517351.2517358; https://research.chalmers.se/en/publication/191449 | Hàng trăm node; duty cycle và độ trễ tốt hơn LWB và CTP/Drip vài lần | Không xác minh | đã xác minh |
| 16 | C. Herrmann, F. Mager, M. Zimmerling, "Mixer: Efficient Many-to-All Broadcast in Dynamic Wireless Mesh Networks", SenSys 2018, pp. 145–158 | https://dblp.uni-trier.de/rec/conf/sensys/HerrmannMZ18.html ; PDF https://wwwpub.zih.tu-dresden.de/~mzimmerl/pubs/herrmann18mixer.pdf | RLNC + CT; nhanh hơn tới 65 %, radio-on giảm tới 50 %, tỷ lệ chuyển gói trên 99,9 % (bản trước) | Có theo slide: mixer.nes-lab.org (TelosB; bản ARM "sắp có") — https://www.sambuz.com/doc/mixer-ppt-presentation-861499 | đã xác minh |
| 17 | M. Zimmerling, L. Mottola, S. Santini, "Synchronous Transmissions in Low-Power Wireless: A Survey…", ACM Computing Surveys 53(6), art. 121, 2020/2021 | DOI 10.1145/3410159; https://arxiv.org/abs/2001.08557 | Survey về CT; xếp Pando, Splash, Ripple vào nhóm phát tán 1–n | — | đã xác minh |
| 18 | M. Stolikj, T. Meyfroyt, P. Cuijpers, J. Lukkien, "Improving the Performance of Trickle-Based Data Dissemination in Low-Power Networks", EWSN 2015 | https://arxiv.org/pdf/1509.08654 | CSMA/CA + ContikiMAC làm node "đói" bản tin Trickle, gây trễ lớn; đề xuất "Cleansing"; thử trên IoT-LAB | Contiki 2.7 | đã xác minh |
| 19 | ContikiMAC (Dunkels; RDC mặc định của Contiki 2.5) | Mã nguồn: https://git.denkn.at/deac/osd-contiki/src/commit/a2664054c5c68315f2b33ec43cfc648f3770e426/core/net/mac/contikimac.c | Lúc idle, radio tắt 99,2–99,6 % thời gian (theo mô tả mã nguồn) | Có (Contiki) | chỉ thấy mô tả; URL của báo cáo kỹ thuật chưa xác định |
| 20 | Zheng, Sarikaya, "MDeluge" (Deluge multicast theo cây, 2006) | https://link.springer.com/chapter/10.1007/978-3-642-02085-8_19 (kết quả tìm kiếm, chưa chắc là đúng bài) | Phát tới tập node chỉ định; tốt hơn Deluge trong mô phỏng | Không thấy | chỉ thấy mô tả; URL chưa chắc |
| 21 | Arakadakis et al., "Firmware over-the-air programming techniques for IoT networks – A survey", 2020 (có thể là ACM CSUR) | https://arxiv.org/abs/2009.02260v1 | Survey các giai đoạn FOTA, bảo mật, nền tảng mã nguồn mở | — | đã xác minh (bản arXiv) |
| 22 | Mavromatis et al., "Reliable IoT Firmware Updates: A Large-scale Mesh Network Performance Investigation", 2022 | https://arxiv.org/pdf/2203.04682 | Testbed UMBRELLA (Bristol); thời gian join mesh, thông lượng; bàn về việc CT tăng khả năng mở rộng | Không thấy | đã xác minh |
| 23 | "Reliable Firmware Updates for the …" (ICN, multi-hop), 2021 | https://arxiv.org/pdf/2108.09555v1.pdf | Tới 7 hop, xong trong 10–30 phút | Không thấy | chỉ thấy tiêu đề (một phần) |
| 24 | 6TiSCH++ with Bluetooth 5 and Concurrent Transmissions | https://arxiv.org/pdf/2010.09529 | Flood CT trong slotframe TSCH; mô phỏng | Không thấy | đã xác minh |
| 25 | LwM2M FW Update yêu cầu block-wise (trích spec v1.0) ; LoRaWAN FUOTA (multicast chunk có lập lịch) | https://www.github.com/eclipse-leshan/leshan/wiki/Using-CoAP-Block-Wise-to-transfer-large-file-%3F ; https://www.thethingsindustries.com/docs/concepts/features/lorawan/fuota/ | OTA chuẩn công nghiệp là unicast block-wise từng thiết bị; FUOTA lập lịch downlink multicast rồi kiểm từng chunk | Leshan, TTS | đã xác minh (tài liệu kỹ thuật, không phải bài báo) |
| 26 | Gappa (mở rộng MNP, UAV phát segment mã đa kênh), qua survey GCP | https://arxiv.org/pdf/0707.3717 | Tiền lệ trực tiếp cho "UAV phát mã xuống WSN"; chưa có số liệu | Không thấy | chỉ thấy mô tả thứ cấp |
| 27 | UAV-assisted trusted code dissemination cho IIoT 5G, IEEE OJ-COMS 2024 | https://doaj.org/article/e65c85ae7d1f478d85ff6b1fa8ab5976 | Bài toán về tin cậy và chữ ký, không phải thông lượng | — | đã xác minh (ít liên quan) |

**Không tìm thấy trong phiên này:** BoX-MAC (Moss & Levis), không thấy URL nào của báo cáo. "MCTP" không ra kết quả nào
phù hợp: có thể là tên khác hoặc nhớ nhầm, cần người dùng cho tiêu đề đầy đủ. Không có bài nào đo năng lượng Deluge trên
BoX-MAC hay LPL.

## 3. Đề xuất baseline công bằng cho J1

**Baseline A (bắt buộc): "Deluge-fair", tức Deluge giữ trong ns-3 nhưng sửa ba điểm mà phản biện sẽ bắt.**
1. *Cùng phạm vi đích:* chỉ các cell trong cụm (cell critical cùng relay cần thiết) tham gia, theo ý tưởng của MDeluge
   (#20). Nếu không, Deluge bị phạt vì phải phủ toàn bộ scope. Nên báo cả hai: scope đầy đủ và scope thu hẹp. Cách này
   tách được phần dư dữ liệu do *thiết kế* (mỗi cell phải đủ mọi page) khỏi phần do *phạm vi*.
2. *Năng lượng công bằng:* thêm mô hình duty cycling kiểu LPL/ContikiMAC cho Deluge (chu kỳ lấy mẫu kênh, preamble hoặc
   strobe) và báo cặp (thời gian, năng lượng) cho cả hai chế độ: radio luôn bật (Deluge nhanh nhất) và LPL (Deluge tiết
   kiệm nhất). #18 cho thấy LPL làm Trickle chậm đi; có số liệu thì ta mới nói được "Deluge không thể vừa nhanh vừa tiết
   kiệm".
3. *Tinh chỉnh tham số:* quét Imin (ví dụ 0,1–1 s), kích thước page, k. Báo cấu hình Deluge tốt nhất chứ không chỉ
   mặc định. Tuỳ chọn: thay truyền page bằng mã fountain/RLNC (ý của Rateless Deluge, SYNAPSE++). #7 và #8 cho thấy
   điều này cắt đúng phần dữ liệu thừa mà ta chỉ ra. Nếu River vẫn thắng "Deluge + FEC" thì lập luận vững hơn nhiều.

*Lý do:* Deluge vẫn là chuẩn de facto được mọi bài sau so sánh, và đã có sẵn trong ns-3 của ta. Ba sửa đổi trên trả lời
trực tiếp câu "baseline yếu, cấu hình bất lợi".

**Baseline B (nên có): một đại diện thế hệ mới, chọn một trong hai.**
- *B1, kiểu Typhoon (CSMA, unicast + nghe lén + đa kênh):* làm được trong ns-3 lr-wpan vì không cần CI. Đây là đối thủ
  CSMA mạnh nhất có kết quả công bố (tới 3× so với Deluge) và gần River nhất về cơ chế, nên so với nó cô lập được giá trị
  của *kế hoạch toàn cục*. Chi phí cài vừa phải.
- *B2, CT pipeline lý tưởng hoá (Splash/Pando):* ns-3 không mô hình CI, nên dùng mô hình ở mức slot: mỗi flood đi một hop
  mỗi slot, pipeline mỗi 3 hop, PRR theo từng link lấy từ cùng mô hình kênh, cộng mã fountain. Đây là *cận trên rộng tay*
  cho baseline. Phản biện từ cộng đồng CT (TU Dresden, ETH, NUS) gần như chắc chắn sẽ hỏi về Splash, Pando hay Mixer.
  Nếu không chạy, ít nhất cần lập luận định lượng: thông lượng mỗi node khoảng 10 kbit/s của Splash áp vào 400 KB và cụm
  80 cell, cùng yêu cầu đồng bộ dưới µs và toàn mạng thức trong lúc flood.

Đề xuất: **A + B1** trong mô phỏng chính, **B2** dưới dạng phân tích hoặc cận trên trong phần thảo luận. Ngoài ra nên có
một baseline rẻ phản ánh thực tiễn công nghiệp, *unicast CoAP block-wise từng cell* (#25), để trả lời các phản biện
IoT-J quan tâm Thread và LwM2M.

**Định vị River (một câu):** River thuộc họ *có lập lịch tập trung* như LWB (#14) và LoRaWAN FUOTA (#25), nhưng lập kế
hoạch theo đường cell và theo phạm vi cụm trên CSMA thông thường, không cần đồng bộ dưới µs như CT. Cơ chế ngủ của nó
dựa trên lịch dự tính trước, khác cách ngủ phản ứng theo hàng xóm của MNP.

## 4. Rủi ro (phản biện có thể nói gì)

1. **"Deluge 2004 lỗi thời; hãy so với Splash, Pando hoặc Mixer."** Cần B2 hoặc lập luận định lượng, kèm lý do ns-3 không
   mô phỏng được CI. Đừng tuyên bố River nhanh hơn state of the art nói chung.
2. **"Radio luôn bật là bất lợi cho Deluge về năng lượng."** Đúng. Thiếu chế độ LPL thì lợi thế năng lượng của ta (vốn
   chỉ đến từ việc ngủ theo lịch) sẽ bị coi là so khập khiễng.
3. **"Ngủ theo lịch không mới (MNP, LWB); unicast + nghe lén không mới (Typhoon)."** Phải nói rõ đóng góp là *kế hoạch
   tối ưu từ trạm gốc cho tập cell critical khi UAV chỉ bay qua một lần*, chứ không phải từng cơ chế riêng lẻ.
4. **"Chi phí lập kế hoạch bị bỏ qua."** River cần topo và chất lượng link ở trạm gốc, còn phải phát kế hoạch xuống mạng
   và chịu rủi ro khi link thay đổi. Deluge không cần gì trong số đó. Phải tính chi phí phát kế hoạch và độ bền khi PRR
   lệch so với lúc lập kế hoạch.
5. **"Không cùng đích":** Deluge phủ mọi cell trong scope, River chỉ phủ cell critical. Phải so trên cùng tập đích (xem
   A.1).
6. **"Chỉ mô phỏng ns-3, không có testbed"** (các bài CT đều chạy Indriya, Flocklab, Twist). Có thể giảm rủi ro bằng cách
   kiểm chéo mô hình Deluge với số liệu đã công bố, hoặc chạy Deluge Contiki trong Cooja với cùng topo nhỏ.
7. **Số liệu trong bảng chưa đọc toàn văn** (xem lưu ý đầu file). Không đưa vào paper trước khi kiểm lại PDF, đặc biệt
   các số của Splash (25 s, 21×), Pando (3,5×), Rateless Deluge (15–30 % / 50–80 %) và Mixer (65 % / 50 %).
