---
status: reference
updated: 2026-11-12
---
# 03 — Cơ sở lý thuyết cho phần theory của SigDrop (L1, A, B, C, D)

Ngày: 2026-11-12. Phạm vi: 24 lượt tìm/tải. **Giới hạn quan trọng:** WebFetch bị chặn (arxiv.org, manuscript.isc.ac
không resolve trong session này), nên **không đọc được toàn văn bài nào**. Mọi mô tả nội dung dưới đây lấy từ abstract,
bản ghi thư mục hoặc đoạn trích mà công cụ tìm kiếm trả về.

Quy ước trạng thái:
- **đã xác minh**: đã thấy bản ghi thư mục (DOI hoặc trang IEEE/ACM/arXiv/kho trường), và abstract khớp với mô tả. Chưa đọc toàn văn.
- **chỉ thấy tiêu đề**: chỉ thấy tên bài, link hoặc đoạn trích. Venue, trang hay nội dung chưa kiểm.

## 1. Tóm tắt

1. **C có tiền lệ trực tiếp:** Gallager (1976) chặn dưới lượng "protocol information" cho mỗi thông điệp bằng lý thuyết
   thông tin. Nhóm Abouzeid (2003–2008) mở rộng sang overhead định tuyến MANET (entropy rate của topology,
   rate-distortion). Set reconciliation (Minsky–Trachtenberg–Zippel 2003) cho chi phí bit để hai bên biết "ai có gói nào".
   Kết quả C mới thật sự chỉ khi nó định lượng được **giá trị của plan như side information** (khoảng cách
   $H(X)-H(\cdot\mid\text{plan})$), chứ không nhắc lại Gallager.
2. **D là một cut-set bound đã biết.** Nền là Ahlswede et al. (2000) cho multicast, và Lun–Médard–Koetter–Effros (2008)
   cho mạng gói có mất mát và cung broadcast. Khung gần nhất là **coded cooperative data exchange đa chặng**
   (Courtade–Wesel 2014): mỗi node đã có sẵn một phần gói, đúng như cell sau khi UAV bay qua. Điều kiện cắt của họ có
   dạng y hệt $missing_k(S)/c(S)$.
3. **Phần "trong một hằng số" của D có mẫu để theo.** Gandhi–Parthasarathy–Mishra (2003) chứng minh broadcast độ trễ
   tối thiểu là NP-hard nhưng có thuật toán xấp xỉ O(1) khi tầm phát bị chặn. Fragouli–Widmer–Le Boudec (2008) cho thấy
   network coding chỉ lợi hằng số trong mạng cố định. Hai kết quả này là lý do để nói River (không mã hoá) có thể nằm
   trong một hằng số của tối ưu.
4. **Số hạng "khối lượng + độ trễ" của D có tương tự trong gossip:** Haeupler (2011) cho thời gian dừng O(k+T), với k là số
   thông điệp và T là thời gian lan một thông điệp. Deb–Médard–Choute (2006) cho thời gian ≈ ck. Chặn
   $missing/c + h_{min}\,t_{hop}$ là bản tất định, có chặn cắt, của cùng cấu trúc đó.
5. **A (crossover) đã có tiền lệ một chặng:** Stojanovic–Wu–Sharif–Starobinski (TWC 2009) so sánh network coding với
   cooperation khi phát một tệp K gói tới N máy thu và tìm ra ngưỡng theo xác suất lỗi gói (đoạn trích nói 0.36). Cần định
   vị A là bản **đa chặng, có UAV di động và chi phí loiter**, và trích họ.
6. **Chặn dưới của A lỏng vì dùng kỳ vọng thay cho maximum.** Theo Ghaderi–Towsley–Kurose (2008) và Swapna–Eryilmaz–Shroff
   (2013), thời gian hoàn tất khi broadcast có mất mát tới nhiều máy thu tăng theo log của số máy thu. Thêm số hạng
   $\sqrt{Q\ln m}$ (maximum của các biến nhị thức âm) sẽ làm chặn chặt hơn.
7. **L1 bằng cách thu hẹp từ Dubins TSP** (Le Ny–Feron–Frazzoli 2012) là đúng nhưng tầm thường. Zeng–Xu–Zhang (TWC 2018)
   đã có bài toán quỹ đạo UAV multicast cực tiểu thời gian hoàn tất, có RLNC. Đây là công trình gần FC baseline nhất và
   bắt buộc phải trích.
8. **B được hỗ trợ yếu:** chỉ có các phân tích phủ sóng kiểu chuyển pha của cooperative broadcast (Sirkeci-Mergen–Scaglione).
   Không tìm thấy lý thuyết sẵn cho ngưỡng lệch quỹ đạo.

## 2. Bảng tài liệu

| # | Tác giả, năm | Tiêu đề / venue | Link / DOI | Hỗ trợ | Trạng thái |
|---|---|---|---|---|---|
| 1 | R. G. Gallager, 1976 | Basic limits on protocol information in data communication networks, IEEE Trans. IT 22(4):385–398 | DOI 10.1109/TIT.1976.1055588 | C | đã xác minh |
| 2 | C. E. Rohrs, 1978 | A Lower Bound to Protocol Information in Data Networks (luận văn ThS MIT, ESL-TH-825) | https://apps.dtic.mil/sti/pdfs/ADA056345.pdf | C | chỉ thấy tiêu đề |
| 3 | Zhou & Abouzeid, 2003 | Information-theoretic bounds for mobile ad-hoc networks routing protocols (đoạn trích ghi ISIT 2003; file preprint mang tên ICOIN 2003) | https://sites.ecse.rpi.edu/~abouzeid/preprints/2003icoin-b.pdf | C | chỉ thấy tiêu đề (venue chưa chắc) |
| 4 | Bisnik & Abouzeid, 2007 | On the Capacity Deficit of Mobile Wireless Ad Hoc Networks: A Rate Distortion Formulation | arXiv cs/0703050, https://arxiv.org/abs/cs/0703050 | C | chỉ thấy tiêu đề |
| 5 | Wang & Abouzeid, 2008 | (INFOCOM 2008) overhead tối thiểu của link-state routing bằng rate-distortion; chưa thấy tiêu đề chính xác | https://sites.ecse.rpi.edu/~abouzeid/preprints/2008infocom.pdf | C | chỉ thấy tiêu đề |
| 6 | Minsky, Trachtenberg, Zippel, 2003 | Set Reconciliation with Nearly Optimal Communication Complexity, IEEE Trans. IT 49(9):2213–2218 | DOI 10.1109/TIT.2003.815784 | C | đã xác minh |
| 7 | Ahlswede, Cai, Li, Yeung, 2000 | Network Information Flow, IEEE Trans. IT 46(4):1204–1216 | DOI 10.1109/18.850663 | D | đã xác minh |
| 8 | Lun, Médard, Koetter, Effros, 2008 | On coding for reliable communication over packet networks, Physical Communication 1(1):3–20 | arXiv cs/0510070, https://arxiv.org/abs/cs/0510070 | D, A | đã xác minh |
| 9 | Courtade & Wesel, 2014 | Coded Cooperative Data Exchange in Multihop Networks, IEEE Trans. IT 60(2):1136–1158 | DOI 10.1109/TIT.2013.2290993; arXiv 1203.3445 | D, C | đã xác minh (số trang lấy từ bản ghi mirror) |
| 10 | El Rouayheb, Sprintson, Sadeghi, 2010 | On Coding for Cooperative Data Exchange, ITW 2010 | arXiv 1002.1465; DOI 10.1109/ITWKSPS.2010.5503135 | D, C | đã xác minh (địa điểm ITW mâu thuẫn: Cairo hay Dublin) |
| 11 | Deb, Médard, Choute, 2006 | Algebraic gossip: a network coding approach to optimal multiple rumor mongering, IEEE Trans. IT 52(6):2486–2507 | DOI 10.1109/TIT.2006.874532 | D | đã xác minh |
| 12 | B. Haeupler, 2011 | Analyzing Network Coding Gossip Made Easy, STOC 2011 | DOI 10.1145/1993636.1993676; arXiv 1010.0558 | D | đã xác minh |
| 13 | Fragouli, Widmer, Le Boudec, 2008 | Efficient Broadcasting Using Network Coding, IEEE/ACM ToN 16(2):450–463 | DOI 10.1109/TNET.2007.901080 | D, A | đã xác minh |
| 14 | Gandhi, Parthasarathy, Mishra, 2003 | Minimizing broadcast latency and redundancy in ad hoc networks, MobiHoc 2003, tr. 222–232 (bản tạp chí IEEE/ACM ToN 2008) | https://old.sigmobile.org/mobihoc/2003/papers/p222-gandhi.pdf | L1, D | đã xác minh (bản hội nghị) |
| 15 | M. Luby, 2002 | LT codes, FOCS 2002 | DOI 10.1109/SFCS.2002.1181950 | A | đã xác minh (số trang mâu thuẫn: 271–280 hay 271–282) |
| 16 | A. Shokrollahi, 2006 | Raptor Codes, IEEE Trans. IT 52(6):2551–2567 | DOI 10.1109/TIT.2006.874390 | A | đã xác minh |
| 17 | Karp, Luby, Shokrollahi, 2004 | Finite length analysis of LT codes, ISIT 2004 | DOI 10.1109/ISIT.2004.1365074 | A | đã xác minh (chỉ abstract) |
| 18 | Eryilmaz, Ozdaglar, Médard, Ahmed, 2008 | On the Delay and Throughput Gains of Coding in Unreliable Networks, IEEE Trans. IT 54(12):5511–5524 | DOI 10.1109/TIT.2008.2006454 | A | đã xác minh |
| 19 | Swapna, Eryilmaz, Shroff, 2013 | Throughput-Delay Analysis of Random Linear Network Coding for Wireless Broadcasting, IEEE Trans. IT 59(10):6328–6341 | DOI 10.1109/TIT.2013.2271895; arXiv 1101.3724 | A | đã xác minh |
| 20 | Ghaderi, Towsley, Kurose, 2008 | Reliability Gain of Network Coding in Lossy Wireless Networks, INFOCOM 2008, tr. 2171–2179 | https://ieeexplore.ieee.org/document/4509879 | A | đã xác minh |
| 21 | Stojanovic, Wu, Sharif, Starobinski, 2009 | Data dissemination in wireless broadcast channels: Network coding versus cooperation, IEEE Trans. Wireless Commun. (bản hội nghị CISS 2007) | https://www.bohrium.com/paper-details/data-dissemination-in-wireless-broadcast-channels-network-coding-versus-cooperation/811855354802470912-2455 | A | chỉ thấy tiêu đề (chưa thấy DOI; ngưỡng 0.36 lấy từ đoạn trích) |
| 22 | Sirkeci-Mergen, Scaglione, Gastpar, 2012 | Cooperative Broadcast in Large-Scale Wireless Networks (chương sách IGI Global) | https://www.igi-global.com/chapter/cooperative-broadcast-large-scale-wireless/58807 | A, B | chỉ thấy tiêu đề |
| 23 | (chưa rõ tác giả) | Broadcast Analysis for Large Cooperative Wireless Networks (phê phán mô hình continuum khi mạng cần nhiều chặng) | arXiv 1104.3209, https://arxiv.org/pdf/1104.3209 | A, B | chỉ thấy tiêu đề |
| 24 | Le Ny, Feron, Frazzoli, 2012 | On the Dubins Traveling Salesman Problem, IEEE Trans. Automatic Control 57(1):265–270 | DOI 10.1109/TAC.2011.2166311 | L1 | đã xác minh |
| 25 | Zeng, Xu, Zhang, 2018 | Trajectory Design for Completion Time Minimization in UAV-Enabled Multicasting, IEEE Trans. Wireless Commun. (arXiv ghi "Trajectory Optimization for …") | DOI 10.1109/TWC.2018.2790401; arXiv 1708.06478 | A, L1 (rủi ro) | đã xác minh (metadata) |

## 3. Gợi ý làm chặt từng phát biểu

**L1 (NP-hard).** Thu hẹp về Dubins TSP [24] bằng cách cho $p=1$ trong một đĩa nhỏ quanh mỗi cell và cho chuyển tiếp mặt
đất miễn phí. Chứng minh như vậy chỉ đáng một bổ đề. Ba cách làm nó có giá trị hơn:
- Chứng minh bài toán **vẫn NP-hard khi quỹ đạo đã cố định**: phần lập kế hoạch mặt đất (chọn segment và đường cell) chứa
  bài toán broadcast độ trễ tối thiểu [14]. Khi đó cả hai thành phần đều khó, và điều này biện minh cho việc tách thành
  tour rồi ground.
- Cho **hệ số xấp xỉ của cách tách** đó: $T_{tách} \le \alpha\cdot OPT$. Có thể dùng chặn dưới D làm đại lượng so sánh.
- Định vị so với [25]: họ tối ưu quỹ đạo multicast nhưng không có hợp tác mặt đất.

**A (crossover).** Bốn việc cần làm:
- Thay $\sum_k \tau[(1+\varepsilon)Q/p_k - n_k]^+$ bằng chặn theo **maximum** trong từng nhóm loiter $G$ có $m_G$ cell.
  Số lượt phát để mọi cell đạt $(1+\varepsilon)Q$ là maximum của $m_G$ biến nhị thức âm, nên
  $E[\max] \approx (1+\varepsilon)Q/p + \sqrt{(1+\varepsilon)Q(1-p)}/p\cdot\sqrt{2\ln m_G}$. Số hạng thứ hai tương ứng với
  scaling $\log K$ trong [20] và $\ln n$ trong [19]. Nhờ đó chặn chặt hơn, và cũng giải thích vì sao "week-1 check" thấy chặn lỏng.
- **Nói rõ nguồn của lợi ích.** FC baseline đã dùng mã fountain, nên lợi ích của River không phải coding gain như [18], [19].
  Nó đến từ (i) tái sử dụng không gian ở mặt đất và (ii) chỉ cần một lượt bay. Viết ngưỡng dưới dạng
  $p^* = \tau(1+\varepsilon)Q\,/\,(T_{ground} + \tau n_k + \ldots)$ và vẽ giản đồ pha trong mặt phẳng $(p, |\text{critical}|)$.
- **Trích [21]** là phiên bản một chặng (coding vs cooperation có ngưỡng). Phát biểu của SigDrop là phiên bản đa chặng có
  chi phí di chuyển UAV. Đây là điểm mới cần nêu rõ.
- **Không để $\varepsilon$ ở dạng tự do.** Với $K\approx 4\,041$, overhead của LT phụ thuộc K [17]. Hãy ghi rõ $\varepsilon(K,\delta)$
  ứng với xác suất giải mã lỗi $\delta$, dẫn [15], [16], [17]. Nếu dùng RaptorQ thì cần thêm nguồn RFC; nguồn này chưa
  xác minh trong đợt tìm này.

**B (ngưỡng lệch quỹ đạo).** Không có lý thuyết trực tiếp. Có thể mô hình hoá xác suất kích hoạt theo độ lệch $e$ thành
**chuyển pha phủ sóng**, theo tinh thần [22]: phủ toàn mạng khi ngưỡng giải mã nhỏ hơn giá trị tới hạn. Khi đó
$h(e)=\lceil e/(\sqrt3 R)\rceil+1$ là bán kính hình học trên lưới lục giác, cần chứng minh chặt (có ví dụ đạt đẳng thức).
[23] cảnh báo rằng xấp xỉ continuum có thể sai khi mạng cần nhiều chặng, nên nếu dùng continuum thì phải kiểm bằng mô phỏng.

**D (sẵn sàng mặt đất).**
- Viết lại chặn dưới đúng dạng **điều kiện cắt của cooperative data exchange đa chặng** [9], [10]. Ở đó side information là
  tập gói mỗi cell nhận từ lượt bay của UAV, và $missing_k(S) = Q - |\bigcup_{i\in S} X_i|$ (tính theo các gói cần cho cell
  critical k). Cách viết này cho phát biểu chuẩn và cho biết ngay rằng phía đạt được (mã hoá tuyến tính) chạm được chặn [8], [9].
- **Định nghĩa $c(S)$ cho mô hình 802.15.4:** half-duplex, một kênh, có xung đột. Dùng siêu cung broadcast [8] kèm ràng buộc
  conflict graph. $c(S)$ không lớn hơn kích thước tập độc lập lớn nhất trong các node kề cắt. Nhờ đó giả thiết "gateway pair
  dùng kênh riêng" thành một điều kiện tường minh.
- **Kết quả constant-factor:** chứng minh $T_{River} \le \alpha(\Delta)\cdot\max_S missing/c + \beta\cdot h\,t_{hop}$, với
  $\Delta$ là bậc lớn nhất của conflict graph. Hai mẫu để theo: [14] (O(1)-xấp xỉ cho broadcast độ trễ tối thiểu với tầm phát
  bị chặn) và [13] (coding chỉ lợi hằng số trong mạng cố định). Số hạng cộng $h\,t_{hop}$ tương ứng với T trong O(k+T) của [12].

**C (giá trị thông tin của plan).**
- **Đừng khẳng định $\Omega(H(X))$ cho mọi giao thức discovery.** Một giao thức chỉ cần biết hàm quyết định $f(X)$ (ai gửi gói
  nào), không cần biết toàn bộ X. Chặn dưới đúng phải có dạng $H(f(X))$, hoặc tốt hơn là chặn theo cắt: mỗi cắt S phải truyền
  qua ít nhất $H(\text{tập gói thiếu ở } S)$ bit điều khiển. Cách viết này nối C với D và có dạng Gallager [1] (thông tin giao
  thức tối thiểu).
- **Định lượng cụ thể.** Với X độc lập Bernoulli($p_{ik}$): $H(X)=\sum_{i,k} h_2(p_{ik})$ bit, cỡ $Q\cdot n\cdot h_2(p)$.
  Plan biết trước nghĩa vụ của từng cell (segment), nên chỉ cần mô tả **các nghĩa vụ bị hỏng** D: $H(D)\approx d\log_2(Q/d)$
  với d là số lần hỏng. Phía đạt được là reconciliation $O(d\log Q)$ [6]. Đặt khoảng cách $H(X)-H(D)$ làm "giá trị của plan",
  và so với overhead đo được trong mô phỏng.
- **Định vị:** các bài CDE và index coding [9], [10] **giả định bộ mã hoá biết side information**. C định lượng chính chi phí
  thu thập side information mà các bài đó bỏ qua. Đây là khoảng trống có giá trị nghiên cứu, nhưng còn phải tìm thêm các bài
  về "index coding với side information không biết trước" (chưa tra trong đợt này).

## 4. Rủi ro (kết quả đã có người chứng minh)

- **D:** cut-set bound cho multicast, kể cả khi có mất mát và có side information, là kiến thức chuẩn [7], [8], [9]. Nếu trình
  bày D như một đóng góp mới, reviewer sẽ bác. Phần mới chỉ có thể là ràng buộc kênh và xung đột của 802.15.4, side information
  sinh ra từ quỹ đạo UAV, và constant-factor cho lịch không mã hoá.
- **A:** crossover "coding/broadcast trực tiếp vs cooperation" có ngưỡng đã có trong mô hình một chặng [21]. Scaling theo log
  của số máy thu đã có trong [19], [20]. Lợi ích về độ trễ của coding đã có trong [18]. A phải nhấn vào UAV di động, loiter
  và đa chặng.
- **L1:** Dubins TSP NP-hard [24] và broadcast độ trễ tối thiểu NP-hard [14] đều đã biết. Phép thu hẹp trực tiếp không được tính
  là đóng góp. Quỹ đạo UAV multicast cực tiểu thời gian hoàn tất, có RLNC và chặn dưới xác suất khôi phục, đã có trong [25].
  Đó gần như chính là FC baseline, nên phải trích và so sánh.
- **C:** chặn dưới "protocol information" theo lý thuyết thông tin [1], [2] và overhead định tuyến theo entropy hay
  rate-distortion [3], [4], [5] đã có. Chi phí bit của set reconciliation đã có [6]. Rủi ro lớn nhất là phát biểu quá mức
  ($\Omega(H(X))$ cho mọi giao thức), điều có thể bị phản ví dụ ngay.
- **Còn mở và nên tra tiếp** (chưa có trong bảng): RFC 6330 (RaptorQ) cho $\varepsilon$; Cogill–Shrader–Ephremides (khoảng 2011)
  về chặn kỳ vọng độ trễ khi gửi batch gói tới nhiều máy thu (chỉ thấy được nhắc gián tiếp, chưa có link); index coding với
  side information không biết trước; Dubins TSP with neighborhoods.
