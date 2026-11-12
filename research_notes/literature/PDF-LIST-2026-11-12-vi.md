---
status: current
updated: 2026-11-12
---
# Danh sách PDF cần đọc (từ đợt tìm tài liệu 2026-11-12)

Các phiên tìm tài liệu không đọc được toàn văn vì công cụ WebFetch bị chặn. Riêng `curl` qua proxy lại tải được arXiv và
một số trang tác giả, nên nhóm A Claude tự lấy. Nhóm B là bài sau paywall hoặc host không tới được, cần người dùng lấy
giúp. **Không commit PDF vào repo** (repo đang public, xem mục cuối). Đánh dấu [x] khi đã có PDF.

## A. Claude tự lấy được (arXiv hoặc bản của tác giả)

| | Bài | Nguồn mở | Dùng cho |
|---|---|---|---|
| [ ] | Zeng, Xu, Zhang, Trajectory design for completion time minimization in UAV-enabled multicasting, IEEE TWC 2018 | arXiv 1708.06478 | baseline FC, định lý A |
| [ ] | Courtade, Wesel, Coded cooperative data exchange in multihop networks, IEEE TIT 2014 | arXiv 1203.3445 | định lý D, C |
| [ ] | Swapna, Eryilmaz, Shroff, Throughput-delay analysis of RLNC for wireless broadcasting, IEEE TIT 2013 | arXiv 1101.3724 | định lý A |
| [ ] | Haeupler, Analyzing network coding gossip made easy, STOC 2011 | arXiv 1010.0558 | định lý D |
| [ ] | Lun, Médard, Koetter, Effros, On coding for reliable communication over packet networks, 2008 | arXiv cs/0510070 | định lý D |
| [ ] | Khawaja et al., A survey of air-to-ground propagation channel modeling for UAVs, IEEE COMST 2019 | arXiv 1801.01656 | kênh, A1 |
| [ ] | Manyam, Rathinam, On tightly bounding the Dubins traveling salesman's optimum, 2015 | arXiv 1506.08752 | khoảng cách tối ưu CHORD |
| [ ] | Lahmeri et al., robust trajectory optimisation under UAV deviation (OJ-COMS 2024) | arXiv 2404.01195 (cần đối chiếu bản tạp chí) | gió, takeover |
| [ ] | Bacco et al., UAV–802.15.4 testbed, 2018 | postprint ISTI-CNR | kênh thực địa |
| [ ] | Váňa, Faigl, On the Dubins TSP with neighborhoods, IROS 2015 | comrob.fel.cvut.cz | L1, CHORD |
| [ ] | Gandhi, Parthasarathy, Mishra, Minimizing broadcast latency and redundancy in ad hoc networks, MobiHoc 2003 | sigmobile.org | định lý D |
| [ ] | Isaacs, Klein, Hespanha, Algorithms for the TSP with neighborhoods involving a Dubins vehicle, ACC 2011 | ntnu.no | L1, CHORD |
| [ ] | Wang, Abouzeid, overhead tối thiểu của link-state routing, INFOCOM 2008 | ecse.rpi.edu | định lý C |
| [ ] | MobileDeluge, IEEE MASS 2014 | xiaozhon.github.io | định vị đóng góp |

## B. Cần người dùng lấy giúp

**Ưu tiên 1 (ảnh hưởng trực tiếp tới J1):**

| | Bài | DOI / nguồn | Vì sao |
|---|---|---|---|
| [ ] | Wang, Zhang, Chen et al., Graph-based file dispatching protocol with D2D-enhanced UAV-NOMA communications in large-scale networks, IEEE IoT-J 7(9):8615–8630, 2020 | 10.1109/JIOT.2020.2994549 | rủi ro trùng lặp lớn nhất |
| [ ] | Le Ny, Feron, Frazzoli, On the Dubins traveling salesman problem, IEEE TAC 57(1):265–270, 2012 | 10.1109/TAC.2011.2166311 | bổ đề L1: điều gì đã được chứng minh |
| [ ] | Stojanovic, Wu, Sharif, Starobinski, Data dissemination in wireless broadcast channels: network coding versus cooperation, IEEE TWC 2009 | chưa có DOI | crossover một chặng, tiền lệ của định lý A |
| [ ] | Gallager, Basic limits on protocol information in data communication networks, IEEE TIT 1976 | 10.1109/TIT.1976.1055588 | định lý C |
| [ ] | Ferrari, Zimmerling, Mottola, Thiele, Low-power wireless bus (LWB), ACM SenSys 2012 | chưa có DOI | lịch tập trung, gần River nhất |
| [ ] | Al-Hourani, Kandeepan, Lardner, Optimal LAP altitude for maximum coverage, IEEE WCL 2014 | 10.1109/LWC.2014.2342736 | P_LoS theo góc ngẩng |
| [ ] | Techy, Woolsey, minimum-time paths in steady wind (trochoid), AIAA JGCD 32(6), 2009 | 10.2514/1.44580 | gió, σ = 100 m ở khúc quay |

**Ưu tiên 2:**

| | Bài | DOI / nguồn | Vì sao |
|---|---|---|---|
| [ ] | Typhoon, EWSN 2008 | 10.1007/978-3-540-77690-1_17 | baseline kiểu Typhoon |
| [ ] | Pando, IEEE/ACM ToN 2017 | 10.1109/TNET.2016.2614707 | cận trên truyền đồng bộ |
| [ ] | Splash, USENIX NSDI 2013 | trang USENIX (link Claude thử bị 404) | cận trên truyền đồng bộ |
| [ ] | Hui, Culler, Deluge, ACM SenSys 2004 | 10.1145/1031495.1031506 | baseline hiện tại |
| [ ] | Kulkarni, Wang, MNP, IEEE ICDCS 2005 | chưa có DOI | ngủ khi không cần đoạn |
| [ ] | Nelson, Barber, McLain, Beard, vector field path following, IEEE T-RO 2007 | 10.1109/TRO.2007.898976 | sai số bám đường |
| [ ] | Park, Deyst, How, nonlinear path following, AIAA JGCD 2007 | 10.2514/1.28957 | sai số bám đường (ArduPilot) |
| [ ] | Matolak, Sun, A2G channel characterization part III, IEEE TVT 2017 | 10.1109/TVT.2017.2659651 | hệ số K đo được |
| [ ] | Wen, Dargie, UAV và 802.15.4, IEEE Sensors J. 2020 | trang TU Dresden không tới được | nhiễu tay điều khiển |
| [ ] | Nekrasov et al., Sensors 19(16):3479, 2019 (truy cập mở, CC BY) | 10.3390/s19163479 (MDPI trả 403 từ session) | độ cao tối ưu, dữ liệu Dryad |
| [ ] | Minsky, Trachtenberg, Zippel, Set reconciliation, IEEE TIT 2003 | 10.1109/TIT.2003.815784 | định lý C, phía đạt được |
| [ ] | Ghaderi, Towsley, Kurose, Reliability gain of network coding in lossy wireless networks, INFOCOM 2008 | ieeexplore 4509879 | định lý A, số hạng log |
| [ ] | Gudmundson, correlation model for shadow fading, Electronics Letters 1991 | 10.1049/el:19911328 | tương quan che khuất |

## Về việc đưa PDF lên repo

Repo `da0ran9e/wsn-uav` đang **public**. Bài của IEEE, ACM, Springer, AIAA, Elsevier thuộc bản quyền nhà xuất bản, nên
đưa PDF của chúng lên repo public là phân phối lại trái phép. Nhà xuất bản có thể gửi yêu cầu DMCA, và GitHub có thể gỡ
tệp hoặc khoá repo. Bản arXiv mặc định chỉ cấp quyền phân phối cho arXiv, trừ khi tác giả chọn CC BY. Bài truy cập mở
CC BY (MDPI, OJ-COMS) thì được phân phối lại kèm ghi nguồn, nhưng để link là đủ. Ngoài ra, PDF làm phình lịch sử git vĩnh
viễn (xoá sau vẫn còn trong lịch sử), và `tools/check.py` chặn tệp trên 5 MB.

Cách đề xuất:
- Repo chỉ lưu thông tin thư mục (DOI, BibTeX), ghi chú của mình và trích dẫn ngắn có số trang.
- PDF giữ ngoài repo public: gửi qua chat khi cần, hoặc để ở Drive hay một repo private riêng dùng cho cá nhân.
- Container bị xoá khi session dừng, nên ghi chú đọc bài phải đủ dùng mà không cần mở lại PDF.
