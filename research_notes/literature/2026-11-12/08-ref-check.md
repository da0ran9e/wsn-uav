---
status: reference
updated: 2026-11-12
---
# 08 · Kiểm tra danh mục tài liệu tham khảo của đề cương SigDrop

Tệp được kiểm: `research_notes/proposal/SIGDROP-PROPOSAL-vi.md`, mục "## Tài liệu tham khảo" (dòng 928–959), 28 mục.
Chỗ trích dẫn trong thân bài: chỉ có ở mục 3 "Tổng quan nghiên cứu" (dòng 147–180).
Ngày kiểm: 2026-11-12. Cách kiểm: tìm web (31 lượt). Trong phiên này WebFetch không mở được dblp.org, arxiv.org
hay api.crossref.org (bị chặn mạng), nên mọi thông tin dưới đây đến từ kết quả tìm kiếm (trang IEEE Xplore, ACM, USENIX,
RFC Editor, kho tài liệu của trường, bản tóm tắt). Mục nào không thấy DOI thì ghi rõ "chưa thấy DOI".

## 1. Tóm tắt

- **Đúng: 22 mục** (1, 3–18, 20, 21, 24, 25, 28). Tác giả, tiêu đề, venue và năm khớp với nguồn. Bỏ được nhãn
  [cần kiểm tra] ở các mục 14, 16, 20, 21, 28. Nên bổ sung tập, số, trang và DOI (có trong bảng).
- **Cần sửa: 5 mục.**
  - [2]: tiêu đề bị cắt, thiếu phần sau dấu hai chấm.
  - [19]: sai chữ đệm tên tác giả. Đúng là "W. R. Heinzelman" (Wendi Rabiner Heinzelman), không phải "W. B.".
  - [22]: đề cương đang dùng tiêu đề của bản draft; tiêu đề của RFC 9030 đã xuất bản khác.
  - [26]: thiếu tiêu đề đầy đủ, tác giả, tập và trang.
  - [27]: chưa có trích dẫn. Đã tìm ra bài, nhưng nội dung đề cương gán cho nó không khớp hẳn với abstract.
- **Không xác minh được: 1 mục.** [23] IEEE Std 802.15.4-2020 chưa được tra vì hết lượt tìm. Cách ghi trong đề
  cương đúng dạng chuẩn, nhưng chưa có DOI.
- **Vấn đề nội dung (xem cột ghi chú):**
  - [3] có trong danh mục nhưng thân bài không trích chỗ nào (tham chiếu mồ côi).
  - [27]: abstract không nhắc Nakagami. Cũng chưa thấy chỗ nào xác nhận "suy hao hai đoạn" hay dải α = 2,6–3,35.
  - [16]: abstract đã thấy không nói DTSP-N là NP-khó, nên câu "một bài toán NP-khó" cần nguồn riêng.
  - Thân bài còn một chỗ "[cần bổ sung trích dẫn]" cho PECEE (dòng 177), chưa có mục nào trong danh mục.
- Chưa thấy DOI (thông tin còn lại đã khớp): [5], [16], [18], [26]. Cần tra IEEE Xplore để lấy DOI.

## 2. Bảng đối chiếu

| [n] | Trích dẫn hiện tại (rút gọn) | Trạng thái | Trích dẫn đầy đủ đã kiểm (tác giả, tiêu đề, venue, năm, DOI/URL) | Ghi chú về chỗ dùng trong bài |
|---|---|---|---|---|
| 1 | Zeng, Zhang, Lim, Commun. Mag. 2016 | đúng | Y. Zeng, R. Zhang, T. J. Lim, "Wireless communications with unmanned aerial vehicles: Opportunities and challenges," *IEEE Commun. Mag.*, vol. 54, no. 5, pp. 36–42, May 2016. DOI 10.1109/MCOM.2016.7470933 | Dòng 157: "UAV làm trạm phát/chuyển tiếp đã được nghiên cứu rộng". Hợp lý. |
| 2 | Mozaffari et al., "A tutorial on UAVs for wireless networks," COMST 2019 | sửa (tiêu đề cắt) | M. Mozaffari, W. Saad, M. Bennis, Y.-H. Nam, M. Debbah, "A tutorial on UAVs for wireless networks: Applications, challenges, and open problems," *IEEE Commun. Surveys Tuts.*, vol. 21, no. 3, pp. 2334–2360, 3rd Quart. 2019. DOI 10.1109/COMST.2019.2902862 | Dòng 157, cùng ý với [1]. Hợp lý. |
| 3 | Zeng, Zhang, "Energy-efficient UAV communication with trajectory optimization," TWC 2017 | đúng | Y. Zeng, R. Zhang, "Energy-efficient UAV communication with trajectory optimization," *IEEE Trans. Wireless Commun.*, vol. 16, no. 6, pp. 3747–3760, Jun. 2017. DOI 10.1109/TWC.2017.2688328 | **Thân bài không trích chỗ nào.** Hoặc bỏ khỏi danh mục, hoặc trích ở đoạn "Lập quỹ đạo UAV" (bài có mô hình năng lượng đẩy của UAV cánh bằng và quỹ đạo tròn). |
| 4 | Zeng, Xu, Zhang, multicasting, TWC 2018 | đúng | Y. Zeng, X. Xu, R. Zhang, "Trajectory design for completion time minimization in UAV-enabled multicasting," *IEEE Trans. Wireless Commun.*, vol. 17, no. 4, pp. 2233–2246, Apr. 2018. DOI 10.1109/TWC.2018.2790401 | Dòng 158: "thời gian hoàn thành multicast". Khớp. Bản arXiv 1708.06478 có tiêu đề khác ("Trajectory optimization for…"), nên trích theo tiêu đề bản tạp chí. |
| 5 | Zhan, Zeng, Zhang, WCL 2018 | đúng (chưa thấy DOI) | C. Zhan, Y. Zeng, R. Zhang, "Energy-efficient data collection in UAV enabled wireless sensor network," *IEEE Wireless Commun. Lett.*, 2018. Preprint arXiv:1708.00221. Chưa xác nhận được tập/số/trang và DOI. | Dòng 158: "UAV thu dữ liệu từ WSN". Khớp: bài tối ưu lịch thức của node và quỹ đạo UAV để giảm năng lượng lớn nhất của các node. |
| 6 | Wu, Zeng, Zhang, multi-UAV, TWC 2018 | đúng | Q. Wu, Y. Zeng, R. Zhang, "Joint trajectory and communication design for multi-UAV enabled wireless networks," *IEEE Trans. Wireless Commun.*, vol. 17, no. 3, pp. 2109–2121, Mar. 2018. DOI 10.1109/TWC.2017.2789293 | Dòng 158: "tối ưu công suất và quỹ đạo cho thông lượng". Khớp: bài tối đa thông lượng nhỏ nhất bằng cách tối ưu chung lịch, gán người dùng, quỹ đạo và công suất. |
| 7 | Hui, Culler, SenSys 2004 | đúng | J. W. Hui, D. Culler, "The dynamic behavior of a data dissemination protocol for network programming at scale," in *Proc. ACM SenSys*, Baltimore, MD, USA, Nov. 2004, pp. 81–94. DOI 10.1145/1031495.1031506 | Dòng 147: Deluge, "phát … dữ liệu lớn bằng quảng bá". Khớp: abstract nói Deluge phổ tán đối tượng dữ liệu lớn qua mạng nhiều chặng. Chữ "phát lại" nên đổi thành "phổ tán". |
| 8 | Levis et al., Trickle, NSDI 2004 | đúng | P. Levis, N. Patel, D. Culler, S. Shenker, "Trickle: A self-regulating algorithm for code propagation and maintenance in wireless sensor networks," in *Proc. USENIX NSDI*, San Francisco, CA, USA, Mar. 2004, pp. 15–28. URL https://www.usenix.org/conference/nsdi-04/trickle-self-regulating-algorithm-code-propagation-and-maintenance-wireless | Dòng 148: "điều tiết tần suất quảng bá để tiết kiệm năng lượng". Khớp: Trickle dùng cơ chế nén bớt (suppression) và cửa sổ thích nghi, chỉ gửi vài bản tin mỗi giờ khi không có thay đổi. |
| 9 | Levis et al., RFC 6206, 2011 | đúng | P. Levis, T. Clausen, J. Hui, O. Gnawali, J. Ko, "The Trickle algorithm," IETF RFC 6206, Mar. 2011. URL https://www.rfc-editor.org/info/rfc6206 (URL dựng theo mẫu của RFC Editor, chưa mở trực tiếp; kết quả tìm cho thấy tiêu đề, tháng 3/2011, Standards Track, và hai tác giả Levis, Clausen) | Dòng 148, cùng ý với [8]. Hợp lý. |
| 10 | Luby, "LT codes," FOCS 2002 | đúng | M. Luby, "LT codes," in *Proc. 43rd Annu. IEEE Symp. Found. Comput. Sci. (FOCS)*, Vancouver, Canada, Nov. 2002, pp. 271–280. DOI 10.1109/SFCS.2002.1181950 | Dòng 152. Khớp: đây là mã xoá không tỷ lệ (rateless) đầu tiên. |
| 11 | Shokrollahi, "Raptor codes," TIT 2006 | đúng | A. Shokrollahi, "Raptor codes," *IEEE Trans. Inf. Theory*, vol. 52, no. 6, pp. 2551–2567, Jun. 2006. DOI 10.1109/TIT.2006.874390 | Dòng 152. Khớp. |
| 12 | Luby et al., RFC 6330, 2011 | đúng | M. Luby, A. Shokrollahi, M. Watson, T. Stockhammer, L. Minder, "RaptorQ forward error correction scheme for object delivery," IETF RFC 6330, Aug. 2011. URL https://www.rfc-editor.org/info/rfc6330 | Dòng 152. Khớp: RaptorQ là fountain code. |
| 13 | Ho et al., RLNC multicast, TIT 2006 | đúng | T. Ho, M. Médard, R. Koetter, D. R. Karger, M. Effros, J. Shi, B. Leong, "A random linear network coding approach to multicast," *IEEE Trans. Inf. Theory*, vol. 52, no. 10, pp. 4413–4430, Oct. 2006. DOI 10.1109/TIT.2006.881746 | Dòng 153: "network coding được dùng để tăng hiệu quả phổ tán". Chấp nhận được, nhưng bài này về multicast nói chung (đạt dung lượng, phân tán, bền khi mạng thay đổi), không riêng về phổ tán trong WSN. Nếu muốn nói đúng ý "phổ tán trong WSN" thì cần thêm một nguồn chuyên về WSN. |
| 14 | Zhao, Ammar, Zegura, message ferrying, MobiHoc 2004 [cần kiểm tra] | đúng (bỏ nhãn) | W. Zhao, M. Ammar, E. Zegura, "A message ferrying approach for data delivery in sparse mobile ad hoc networks," in *Proc. ACM MobiHoc*, Tokyo, Japan, May 2004, pp. 187–198. DOI 10.1145/989459.989483 | Dòng 159: "dùng phương tiện di động mang dữ liệu giữa các vùng mất kết nối". Khớp: ferry mang bản tin giữa các phần mạng bị chia cắt. |
| 15 | Dubins, Amer. J. Math. 1957 | đúng | L. E. Dubins, "On curves of minimal length with a constraint on average curvature, and with prescribed initial and terminal positions and tangents," *Amer. J. Math.*, vol. 79, no. 3, pp. 497–516, Jul. 1957. DOI 10.2307/2372560 | Dòng 164: được trích cho "DTSP-N". Bài Dubins là nguồn cho ràng buộc độ cong (đường Dubins), không phải cho DTSP-N. Trích như hiện tại vẫn được, nhưng nên viết "ràng buộc Dubins [15]; DTSP-N [16]". |
| 16 | Isaacs, Klein, Hespanha, ACC 2011 [cần kiểm tra] | đúng (bỏ nhãn; chưa thấy DOI) | J. T. Isaacs, D. J. Klein, J. P. Hespanha, "Algorithms for the traveling salesman problem with neighborhoods involving a Dubins vehicle," in *Proc. American Control Conf. (ACC)*, San Francisco, CA, USA, Jun.–Jul. 2011, pp. 1704–1709. Bản PDF: https://skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1252.pdf | Dòng 164. Khớp: bài định nghĩa DTSPN và đưa hai thuật toán đưa bài toán vô hạn về chọn điểm hữu hạn. **Abstract đã thấy không nói "NP-khó"**: cần dẫn nguồn riêng cho tính NP-khó hoặc kiểm trong toàn văn. File `paper/icc-v5/tail.tex` dòng 107 cũng còn "[TODO: verify]" cho mục này. |
| 17 | Al-Hourani, Kandeepan, Lardner, WCL 2014 | đúng | A. Al-Hourani, S. Kandeepan, S. Lardner, "Optimal LAP altitude for maximum coverage," *IEEE Wireless Commun. Lett.*, vol. 3, no. 6, pp. 569–572, Dec. 2014. DOI 10.1109/LWC.2014.2342736 | Dòng 170: "xác suất LoS theo góc ngẩng". Khớp: bài có công thức dạng đóng cho xác suất LoS giữa LAP và máy thu mặt đất. |
| 18 | Khawaja et al., A2G survey, COMST 2019 | đúng (chưa thấy DOI) | W. Khawaja, I. Guvenc, D. W. Matolak, U.-C. Fiebig, N. Schneckenburger, "A survey of air-to-ground propagation channel modeling for unmanned aerial vehicles," *IEEE Commun. Surveys Tuts.*, vol. 21, no. 3, pp. 2361–(trang cuối chưa xác nhận), 3rd Quart. 2019. Preprint arXiv:1801.01656 | Dòng 170: "tổng quan kênh A2G". Khớp. |
| 19 | W. B. Heinzelman, Chandrakasan, Balakrishnan, HICSS 2000 [cần kiểm tra] | sửa (chữ đệm tác giả) | W. R. Heinzelman, A. Chandrakasan, H. Balakrishnan, "Energy-efficient communication protocol for wireless microsensor networks," in *Proc. 33rd Hawaii Int. Conf. Syst. Sci. (HICSS)*, Maui, HI, USA, Jan. 2000. DOI 10.1109/HICSS.2000.926982 | Dòng 175: LEACH là phân cụm phân cấp. Khớp: LEACH luân phiên cluster-head ngẫu nhiên. |
| 20 | Younis, Fahmy, HEED, TMC 2004 [cần kiểm tra] | đúng (bỏ nhãn) | O. Younis, S. Fahmy, "HEED: A hybrid, energy-efficient, distributed clustering approach for ad hoc sensor networks," *IEEE Trans. Mobile Comput.*, vol. 3, no. 4, pp. 366–379, Oct.–Dec. 2004. DOI 10.1109/TMC.2004.41 | Dòng 175. Khớp. Không nhầm với bản INFOCOM 2004 (tiêu đề khác, DOI 10.1109/INFCOM.2004.1354534). |
| 21 | Xu, Heidemann, Estrin, GAF, MobiCom 2001 [cần kiểm tra] | đúng (bỏ nhãn) | Y. Xu, J. Heidemann, D. Estrin, "Geography-informed energy conservation for ad hoc routing," in *Proc. ACM MobiCom*, Rome, Italy, Jul. 2001, pp. 70–84. DOI 10.1145/381677.381685 | Dòng 175: "lưới địa lý (GAF)". Khớp: GAF (geographical adaptive fidelity) giảm 40–60 % năng lượng so với giao thức định tuyến không sửa đổi. |
| 22 | Thubert (Ed.), "An architecture for IPv6 over the TSCH mode of IEEE 802.15.4," RFC 9030 [cần kiểm tra] | sửa (tiêu đề) | P. Thubert, Ed., "An architecture for IPv6 over the Time-Slotted Channel Hopping mode of IEEE 802.15.4 (6TiSCH)," IETF RFC 9030 (Informational), May 2021. URL https://www.rfc-editor.org/info/rfc9030 | Dòng 176: 6TiSCH. Khớp. Tiêu đề trong đề cương là tiêu đề của draft-ietf-6tisch-architecture. |
| 23 | IEEE Std 802.15.4-2020 | không xác minh được | (chưa tra trong phiên này). Giữ: *IEEE Standard for Low-Rate Wireless Networks*, IEEE Std 802.15.4-2020, 2020. Cần bổ sung DOI từ IEEE Xplore. | Dòng 176: TSCH trong IEEE 802.15.4. Ý hợp lý (TSCH là chế độ MAC của 802.15.4). |
| 24 | Li, Wu, Zheng, open-world re-ID, ECCV 2018 | đúng | X. Li, A. Wu, W.-S. Zheng, "Adversarial open-world person re-identification," in *Proc. ECCV*, 2018, pp. 280–296. DOI 10.1007/978-3-030-01216-8_18 | Dòng 180: "điểm vận hành để đánh đổi bỏ sót / báo nhầm". Hợp lý: bài xét kẻ giả danh (imposter) trong re-ID mở. Toàn văn chưa đọc để xác nhận đường cong đánh đổi. |
| 25 | Ye et al., re-ID survey, TPAMI 2022 | đúng | M. Ye, J. Shen, G. Lin, T. Xiang, L. Shao, S. C. H. Hoi, "Deep learning for person re-identification: A survey and outlook," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 44, no. 6, pp. 2872–2893, Jun. 2022. DOI 10.1109/TPAMI.2021.3054775 | Dòng 180: tổng quan. Khớp: bài chia re-ID thành closed-world và open-world. |
| 26 | K.-V. Nguyen et al., "Efficient multi-UAV assisted data gathering schemes …," TII 2023 [cần kiểm tra] | sửa (bổ sung đầy đủ; chưa thấy DOI) | K.-V. Nguyen, C.-H. Nguyen, T. V. Do, C. Rotter, "Efficient multi-UAV assisted data gathering schemes for maximizing the operation time of wireless sensor networks in precision farming," *IEEE Trans. Ind. Informat.*, vol. 19, no. 12, pp. 11664–11674, 2023. (Tập/số/trang lấy từ bản ghi dblp `journals/tii/NguyenNDR23` qua kết quả tìm; trang AMiner: https://www.aminer.cn/pub/648cf13ed68f896efa901765) | Dòng 158: "UAV thu dữ liệu từ WSN". Khớp: phân cụm chung với thu dữ liệu nhiều UAV (thuật toán GAMBAC), kéo dài tuổi thọ mạng. `paper/icc-v5/tail.tex` dòng 121 cũng còn "[TODO: volume/pages]". |
| 27 | Qiu et al., đo kênh không–đất ở độ cao thấp, 2017 [chưa có thông tin] | sửa (bổ sung trích dẫn; nội dung cần kiểm) | Z. Qiu, X. Chu, C. Calvo-Ramirez, C. Briso, X. Yin, "Low altitude UAV air-to-ground channel measurement and modeling in semiurban environments," *Wireless Commun. Mobile Comput.*, vol. 2017, Art. no. 1587412, 11 pp., Nov. 2017. DOI 10.1155/2017/1587412 | Dòng 171. **Có chỗ lệch:** abstract nói bài đưa ra số mũ suy hao đo ở các độ cao khác nhau, một mô hình hệ số Rician phụ thuộc độ cao, và "hai vùng truyền sóng có đặc tính rất khác nhau". Abstract **không nhắc Nakagami**. Cũng chưa rõ "hai vùng" có phải là "suy hao hai đoạn theo khoảng cách" (không gian tự do tới 100 m rồi (d/100)^−α) như mô phỏng đang dùng hay không. Dải α = 2,6–3,35 (`paper/PARAMS-vi.md` C2, `paper/OVERVIEW-vi.md`) chưa kiểm được vì không mở được toàn văn. Bài là open access (Hindawi/Wiley), cần đọc toàn văn để đối số. |
| 28 | Kulkarni, Wang, MNP, ICDCS 2005 [cần kiểm tra] | đúng (bỏ nhãn) | S. S. Kulkarni, L. Wang, "MNP: Multihop network reprogramming service for sensor networks," in *Proc. 25th IEEE Int. Conf. Distrib. Comput. Syst. (ICDCS)*, Columbus, OH, USA, Jun. 2005, pp. 7–16. DOI 10.1109/ICDCS.2005.50 | Dòng 147, cùng câu với Deluge. Hợp lý. MNP cũng phổ tán chương trình qua nhiều chặng; chữ "page" là thuật ngữ của Deluge, MNP chia theo "segment". |

## 3. Danh mục đề xuất, sẵn để dán vào đề cương

Định dạng giữ như danh mục hiện có. Đã bỏ nhãn [cần kiểm tra] ở các mục đã xác minh. Những chỗ còn thiếu ghi
**[cần kiểm tra: …]**.

```markdown
1. Y. Zeng, R. Zhang, T. J. Lim, "Wireless communications with unmanned aerial vehicles: Opportunities and challenges," *IEEE Commun. Mag.*, vol. 54, no. 5, pp. 36–42, 2016, doi: 10.1109/MCOM.2016.7470933.
2. M. Mozaffari, W. Saad, M. Bennis, Y.-H. Nam, M. Debbah, "A tutorial on UAVs for wireless networks: Applications, challenges, and open problems," *IEEE Commun. Surveys Tuts.*, vol. 21, no. 3, pp. 2334–2360, 2019, doi: 10.1109/COMST.2019.2902862.
3. Y. Zeng, R. Zhang, "Energy-efficient UAV communication with trajectory optimization," *IEEE Trans. Wireless Commun.*, vol. 16, no. 6, pp. 3747–3760, 2017, doi: 10.1109/TWC.2017.2688328.
4. Y. Zeng, X. Xu, R. Zhang, "Trajectory design for completion time minimization in UAV-enabled multicasting," *IEEE Trans. Wireless Commun.*, vol. 17, no. 4, pp. 2233–2246, 2018, doi: 10.1109/TWC.2018.2790401.
5. C. Zhan, Y. Zeng, R. Zhang, "Energy-efficient data collection in UAV enabled wireless sensor network," *IEEE Wireless Commun. Lett.*, 2018. **[cần kiểm tra: tập, số, trang, DOI]**
6. Q. Wu, Y. Zeng, R. Zhang, "Joint trajectory and communication design for multi-UAV enabled wireless networks," *IEEE Trans. Wireless Commun.*, vol. 17, no. 3, pp. 2109–2121, 2018, doi: 10.1109/TWC.2017.2789293.
7. J. W. Hui, D. Culler, "The dynamic behavior of a data dissemination protocol for network programming at scale," in *Proc. ACM SenSys*, 2004, pp. 81–94, doi: 10.1145/1031495.1031506.
8. P. Levis, N. Patel, D. Culler, S. Shenker, "Trickle: A self-regulating algorithm for code propagation and maintenance in wireless sensor networks," in *Proc. USENIX NSDI*, 2004, pp. 15–28.
9. P. Levis, T. Clausen, J. Hui, O. Gnawali, J. Ko, "The Trickle algorithm," IETF RFC 6206, 2011.
10. M. Luby, "LT codes," in *Proc. IEEE FOCS*, 2002, pp. 271–280, doi: 10.1109/SFCS.2002.1181950.
11. A. Shokrollahi, "Raptor codes," *IEEE Trans. Inf. Theory*, vol. 52, no. 6, pp. 2551–2567, 2006, doi: 10.1109/TIT.2006.874390.
12. M. Luby, A. Shokrollahi, M. Watson, T. Stockhammer, L. Minder, "RaptorQ forward error correction scheme for object delivery," IETF RFC 6330, 2011.
13. T. Ho, M. Médard, R. Koetter, D. R. Karger, M. Effros, J. Shi, B. Leong, "A random linear network coding approach to multicast," *IEEE Trans. Inf. Theory*, vol. 52, no. 10, pp. 4413–4430, 2006, doi: 10.1109/TIT.2006.881746.
14. W. Zhao, M. Ammar, E. Zegura, "A message ferrying approach for data delivery in sparse mobile ad hoc networks," in *Proc. ACM MobiHoc*, 2004, pp. 187–198, doi: 10.1145/989459.989483.
15. L. E. Dubins, "On curves of minimal length with a constraint on average curvature, and with prescribed initial and terminal positions and tangents," *Amer. J. Math.*, vol. 79, no. 3, pp. 497–516, 1957, doi: 10.2307/2372560.
16. J. T. Isaacs, D. J. Klein, J. P. Hespanha, "Algorithms for the traveling salesman problem with neighborhoods involving a Dubins vehicle," in *Proc. American Control Conf. (ACC)*, 2011, pp. 1704–1709. **[cần kiểm tra: DOI]**
17. A. Al-Hourani, S. Kandeepan, S. Lardner, "Optimal LAP altitude for maximum coverage," *IEEE Wireless Commun. Lett.*, vol. 3, no. 6, pp. 569–572, 2014, doi: 10.1109/LWC.2014.2342736.
18. W. Khawaja, I. Guvenc, D. W. Matolak, U.-C. Fiebig, N. Schneckenburger, "A survey of air-to-ground propagation channel modeling for unmanned aerial vehicles," *IEEE Commun. Surveys Tuts.*, vol. 21, no. 3, pp. 2361–, 2019. **[cần kiểm tra: trang cuối, DOI]**
19. W. R. Heinzelman, A. Chandrakasan, H. Balakrishnan, "Energy-efficient communication protocol for wireless microsensor networks," in *Proc. 33rd Hawaii Int. Conf. Syst. Sci. (HICSS)*, 2000, doi: 10.1109/HICSS.2000.926982.
20. O. Younis, S. Fahmy, "HEED: A hybrid, energy-efficient, distributed clustering approach for ad hoc sensor networks," *IEEE Trans. Mobile Comput.*, vol. 3, no. 4, pp. 366–379, 2004, doi: 10.1109/TMC.2004.41.
21. Y. Xu, J. Heidemann, D. Estrin, "Geography-informed energy conservation for ad hoc routing," in *Proc. ACM MobiCom*, 2001, pp. 70–84, doi: 10.1145/381677.381685.
22. P. Thubert (Ed.), "An architecture for IPv6 over the Time-Slotted Channel Hopping mode of IEEE 802.15.4 (6TiSCH)," IETF RFC 9030, 2021.
23. *IEEE Standard for Low-Rate Wireless Networks*, IEEE Std 802.15.4-2020, 2020. **[cần kiểm tra: DOI]**
24. X. Li, A. Wu, W.-S. Zheng, "Adversarial open-world person re-identification," in *Proc. ECCV*, 2018, pp. 280–296, doi: 10.1007/978-3-030-01216-8_18.
25. M. Ye, J. Shen, G. Lin, T. Xiang, L. Shao, S. C. H. Hoi, "Deep learning for person re-identification: A survey and outlook," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 44, no. 6, pp. 2872–2893, 2022, doi: 10.1109/TPAMI.2021.3054775.
26. K.-V. Nguyen, C.-H. Nguyen, T. V. Do, C. Rotter, "Efficient multi-UAV assisted data gathering schemes for maximizing the operation time of wireless sensor networks in precision farming," *IEEE Trans. Ind. Informat.*, vol. 19, no. 12, pp. 11664–11674, 2023. **[cần kiểm tra: DOI]**
27. Z. Qiu, X. Chu, C. Calvo-Ramirez, C. Briso, X. Yin, "Low altitude UAV air-to-ground channel measurement and modeling in semiurban environments," *Wireless Commun. Mobile Comput.*, vol. 2017, Art. no. 1587412, 2017, doi: 10.1155/2017/1587412.
28. S. S. Kulkarni, L. Wang, "MNP: Multihop network reprogramming service for sensor networks," in *Proc. IEEE ICDCS*, 2005, pp. 7–16, doi: 10.1109/ICDCS.2005.50.
```

### Đề xuất sửa câu trong thân bài (mục 3), để người dùng quyết định

- Dòng 147: "Deluge [7] và MNP [28] **phát lại** mã hoặc dữ liệu lớn …" → "**phổ tán** mã hoặc dữ liệu lớn …". "Yêu cầu theo
  page" là cơ chế của Deluge, còn MNP chia theo segment.
- Dòng 164: "… ràng buộc Dubins là DTSP-N [15], [16], một bài toán NP-khó" → tách nguồn: "ràng buộc Dubins [15] …
  DTSP-N [16]". Câu "NP-khó" cần nguồn riêng, hoặc phải kiểm trong toàn văn [16].
- Dòng 171: "Suy hao hai đoạn và fading Rician/Nakagami theo đo đạc ở độ cao thấp [27]". Abstract của [27] chỉ ủng hộ
  số mũ suy hao theo độ cao và hệ số Rician phụ thuộc độ cao. Cần bỏ "Nakagami" hoặc thêm nguồn khác cho Nakagami.
  Cũng cần đọc toàn văn [27] để xác nhận mô hình hai đoạn và dải α 2,6–3,35 trước khi giữ câu này.
- [3] không được trích trong thân bài: hoặc bỏ khỏi danh mục, hoặc trích ở đoạn "Lập quỹ đạo UAV".
- PECEE (dòng 177) vẫn "[cần bổ sung trích dẫn]", chưa có trong danh mục.

### Nguồn đã thấy (chọn lọc)

- IEEE Xplore 7470933 (ref 1), arXiv 1602.03602; pure.ul.ie (ref 2); unpaywall 10.1109/TWC.2018.2790401 (ref 4)
- usenix.org/conference/nsdi-04/… (ref 8); rfc-editor.org/info/rfc6330 (ref 12); rfc-editor.org/info/rfc9030 (ref 22)
- researchr.org/publication/ZhaoAZ04 (ref 14); skoge.folk.ntnu.no/prost/proceedings/acc11/data/papers/1252.pdf (ref 16)
- ieeexplore.ieee.org/document/926982 (ref 19); cs.purdue.edu/homes/fahmy/papers/tmc04.pdf (ref 20); ant.isi.edu/~johnh/PAPERS/Xu01a.html (ref 21)
- link.springer.com/doi/10.1007/978-3-030-01216-8_18 (ref 24); arxiv 2001.04193 (ref 25)
- aminer.cn/pub/648cf13ed68f896efa901765 (ref 26); next.sciencegate.app/document/10.1155/2017/1587412 (ref 27)
- websrv.cecs.uci.edu/~papers/icdcs05/02_kulkarnis_mnp.pdf (ref 28); en.wikipedia.org/wiki/Dubins_path (ref 15)
