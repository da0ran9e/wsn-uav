---
status: current
updated: 2026-11-27
---
# J1 · Bản nháp phần đặt vấn đề, theo từng ý (v2, rừng)

Bản nháp cùng làm theo chatlog mục 415, gồm ba mục của bài: mô tả hệ thống (III), mô hình (IV), phát biểu bài toán (V). Viết thành
từng ý để bạn đọc, sửa, rồi viết lại thành văn tiếng Anh. Quyết định đầu vào: bối cảnh [CONTEXT-vi.md](CONTEXT-vi.md), ba bài toán
[PROBLEMS-vi.md](PROBLEMS-vi.md) (các đề xuất được tạm đồng ý ở mục 415), dàn ý [OUTLINE-vi.md](OUTLINE-vi.md). Mẫu viết:
Zhan 2018 và Zeng 2018 ([FORMULATION-EXAMPLES-vi.md](FORMULATION-EXAMPLES-vi.md)).

Nhãn ở cuối ý: **có** (số và lập luận đã có nguồn trong repo), **đề xuất** (tôi đặt, chờ bạn duyệt), **mở** (chưa quyết hoặc chưa có
số). Ký hiệu chưa chốt, đổi được.

## III. Mô tả hệ thống (kể bằng lời, chưa dùng ký hiệu)

### III.1 Vùng và thiết bị

1. Vùng là một khu rừng đất thấp, địa hình phẳng hoặc thoải, như cửa sổ 10 × 10 km ở Cát Tiên (chênh cao trong một cell trung vị 14 m).
   **có**
2. Lõi rừng không có sóng di động; đường liên lạc với bên ngoài chỉ có LoRa và UAV. **có** [chung, cần một nguồn về vùng phủ sóng]
3. Ban quản lý rừng sở hữu một mạng thiết bị chạy pin:
   - camera bẫy ảnh, chụp khi có chuyển động;
   - cảm biến âm thanh, cảm biến cháy;
   - một số AI node: camera thông minh hoặc hộp xử lý biên đặt ở chỗ trống, có tấm pin mặt trời đủ nuôi bộ tăng tốc mạng nơ-ron.

   **đề xuất**
4. Mọi thiết bị dùng chung một mạng mesh 802.15.4 ở 2,4 GHz. Mỗi cụm có một trưởng cụm có thêm radio LoRa để báo về trạm. **có**
   (chốt ở CONTEXT dòng g)
5. Trạm gốc đặt ở trạm kiểm lâm hoặc trụ sở vườn ở bìa rừng, có LoRa gateway và chỗ cất hạ cánh cho hai UAV:
   - đội 1: UAV cánh bằng cất hạ cánh thẳng đứng (VTOL), phát truy vấn;
   - đội 2: UAV cánh quay có camera, xác minh.

   **đề xuất**

### III.2 Pha 0, trước mọi sự cố

6. Trạm gốc dựng tổ chức mạng một lần:
   - chia vùng thành cell lục giác;
   - mỗi cell bầu một cell leader (CL), hai cell kề có đúng một cặp gateway;
   - gom cell thành cụm.

   **có**
7. Trạm gốc chọn các cell đặt AI node (critical cell) và giao mỗi cell thường cho một AI node. Thiết bị trong cell thường gửi bản ghi
   người nó phát hiện (ảnh cắt hoặc vector) về AI node đó. **có**
8. Vì không có thông tin vị trí, vùng nhiệm vụ luôn là cả vùng mạng phủ. Trạm gốc tính sẵn một kế hoạch pha 1 cho cả vùng: đường bay
   của đội 1 và kế hoạch vận chuyển mặt đất đi kèm. Phần kế hoạch của từng cell được phát xuống mạng và lưu tại cell. **đề xuất**
   (tạm chốt mục 415)
9. Kế hoạch tính lại khi thiết bị hỏng, thêm hay bớt. **đề xuất**

### III.3 Khi có sự cố

10. Có người báo mất tích. Thông tin duy nhất là bộ ảnh do người thân cung cấp; không có điểm thấy cuối. **có** (chốt mục 414)
11. Trạm gốc dựng truy vấn từ bộ ảnh, rồi phát qua LoRa một bản tin đánh thức vài byte gồm mã nhiệm vụ và giờ cất cánh. **có**
12. Từ bản tin và kế hoạch đã lưu, mỗi thiết bị tự tính lúc phải thức. **đề xuất**

### III.4 Pha 1, phát truy vấn

13. Đội 1 cất cánh, bay đúng đường đã tính ở độ cao cố định, phát các gói truy vấn theo thứ tự cố định và lặp lại dọc đường. **có**
14. Cell nằm dưới đường bay giữ những gói thiết bị của nó nghe được. **có**
15. Cell giữ đoạn mà kế hoạch giao cho nó chuyển thì gửi đoạn đó về phía các critical cell theo đường cell của kế hoạch. **có**
16. Một bước sửa bù chỗ hổng do mất gói hoặc do UAV bay lệch đường (gió). Bước sửa gồm:
    - gom và sửa trong cell;
    - takeover;
    - vá cell còn thiếu sau hạn.

    **có** (vá: mở, việc K15)
17. AI node nhận đủ truy vấn thì đối sánh với các bản ghi nó giữ, rồi gửi một điểm số vài byte qua trưởng cụm về trạm bằng LoRa. **có**

### III.5 Pha 2, xác minh

18. Trạm gốc tính xác suất hậu nghiệm cho từng cell từ các điểm số. **có**
19. Đội 2 cất cánh khi có báo cáo đầu tiên, bay tới cell có tỉ số giữa xác suất và thời gian bay tốt nhất, xác minh bằng camera của
    nó, rồi chọn cell tiếp theo. Thứ tự thăm tính lại mỗi khi có báo cáo mới. **có** (chính sách hiện tại; tối ưu pha 2: mở)
20. Nhiệm vụ kết thúc khi đội 2 xác nhận đúng người; toạ độ chuyển cho đội cứu nạn mặt đất. **có**

### III.6 Phạm vi

21. Pha 1 dùng một UAV; nhiều UAV cần cơ chế phối hợp, để sau. **có**
22. Chỉ xét rừng phẳng hoặc thoải; vườn núi cần bay bám địa hình và mô hình che khuất, để phần mở rộng. **có** (chốt mục 411)
23. Chỉ xét những nhiệm vụ có ít nhất một thiết bị thấy người. Tỉ lệ nhiệm vụ không thiết bị nào thấy người là một độ đo của mạng,
    báo riêng. **đề xuất** (tạm chốt mục 415)

## IV. Mô hình

### IV.1 Cell, cụm, môi trường

24. Lưới lục giác bán kính $R_{\mathrm c}=100$ m; đồ thị cell $G=(\mathcal C,\mathcal E)$, cạnh là cặp gateway. **có**
25. Cụm tối đa 80 cell, mỗi cụm một trưởng cụm (CH) có LoRa. **có**
26. Môi trường $m\in\mathcal M$ là mỗi cell và mỗi cặp gateway. Trong mỗi môi trường, mỗi lúc chỉ một radio phát:
    - kênh của cell theo bảng tái dùng 7 màu;
    - mỗi cặp gateway có radio và kênh riêng.

    **có**
27. Cell không có thiết bị (sông, đầm) là lỗ của $G$. **có**

### IV.2 Thiết bị và mật độ

28. Tập thiết bị $V$. Tập thiết bị làm được AI node $V_{\mathrm p}\subseteq V$ chỉ gồm thiết bị ở chỗ trống. **đề xuất**; cách sinh
    $V_{\mathrm p}$ còn **mở** (cần bản đồ lớp phủ)
29. Mật độ 816 thiết bị/km² là giả định hướng tới tương lai. Triển khai thật hiện chỉ 0,003–2 thiết bị/km² trên toàn vườn; mức trên 100
    chỉ có ở ô thí điểm nhỏ (CONTEXT mục 5). Bài nói thẳng điều này và có phần độ nhạy theo mật độ. **có** (lập luận), **mở** (ngưỡng
    lưới liền khi có suy hao tán)

### IV.3 Năng lượng và đánh thức

30. Thiết bị $u$ có ngân sách năng lượng $E_u$ cho một nhiệm vụ. Thiết bị tốn $e_{\mathrm{rx}}$ mỗi giây thức nghe và
    $e_{\mathrm{tx}}$ mỗi khung phát. **đề xuất**; số $E_u$, $e_{\mathrm{rx}}$, $e_{\mathrm{tx}}$ còn **mở**
31. Ngân sách của cell là $E_a=\sum_{u\in U_a^{\mathrm{fwd}}}E_u$, tổng ngân sách các thiết bị chuyển tiếp của cell $a$. **đề xuất**
32. Cửa sổ thức $W_a=[t^{\mathrm{on}}_a,t^{\mathrm{off}}_a]$ của cell $a$ suy ra từ kế hoạch. Nó bắt đầu khi UAV tới gần $a$ hoặc khi
    gói đầu tiên cần chuyển qua $a$, và kết thúc khi $a$ chuyển xong phần của mình. **đề xuất** (tạm chốt: hệ quả, không là biến)

### IV.4 UAV và cách phát

33. Đội 1 bay ở độ cao $h=100$ m, tốc độ 25–50 m/s, góc nghiêng tối đa 45°. Bán kính quay $\rho(v)=v^2/g$ là 255 m ở 50 m/s và
    63,7 m ở 25 m/s. **có**
34. Đội 1 phát một gói 99 B mỗi $T_{\mathrm p}=10$ ms. Đường bay là $q:[0,T_{\mathrm f}]\to\mathbb R^2$, đi từ trạm gốc và về trạm
    gốc. Gói $j$ phát tại $q(t_j)$. **có**
35. Đội 2 bay 15 m/s, xác minh mỗi cell khoảng $\sigma=78$ s. **có**

### IV.5 Kênh A2G qua tán

36. Suy hao gồm hai đoạn cộng suy hao môi trường $L_{\mathrm{obs}}$ (công thức (1) của bản thảo). Pha đinh Rician $K=2$, ngưỡng hiệu
    dụng $S=-101{,}04$ dBm. **có**
37. Bốn chế độ kênh: $L_{\mathrm{obs}}=0/9/19{,}8/25{,}7$ dB, ứng với $R_{50}=1016/498/199/99$ m. **có**
38. Đối chiếu với Weissberger, ba chế độ có tán ứng với 17/66/103 m đường đi qua cây. Tán dày 10 m nhìn xiên cho 8 dB ở 45° và
    17,5 dB ở 11°. Áp mô hình cho đường xiên là ngoại suy; suy hao theo góc ngẩng để ở phần độ nhạy. **có**
39. Xác suất cell nhận được một gói: $P_c(x)=1-\prod_{u\in U_c}(1-p(\lVert x-u\rVert))$, với giả định các thiết bị nhận độc lập. Các
    chặn chỉ cần $P_c$, không cần giả định này. **có**

### IV.6 Kênh G2G dưới tán

40. Giữ khuôn log-distance (số mũ 3,5), shadowing 7,8 dB theo cặp thiết bị, Rayleigh khối 100 ms, cộng suy hao tán $L_{\mathrm f}(d)$
    (Weissberger: 12,6 dB ở 30 m, 17 dB ở 50 m, 25,6 dB ở 100 m). **mở**: số mũ và shadowing lấy từ mô hình phố đô thị nên có thể tính
    trùng; cần mô hình đo cho node đặt sát đất trong rừng
41. Một chặng có xác nhận của khung 127 B chiếm môi trường ít nhất 4,8 ms; thực tế $\tau_f\approx5$–7 ms. **có**

### IV.7 Truy vấn và hoàn tất

42. Truy vấn gồm $L=12$ ảnh, $Q=4041$ gói. **có**
43. Có mã không tỉ lệ thì cell giải được khi giữ $\lceil(1+\epsilon)Q\rceil$ gói khác nhau, với $\epsilon=0{,}05$. **có**
44. Thời điểm hoàn tất $C_k$ của critical cell $k$ là lúc CL của nó giữ đủ gói để giải truy vấn. **có**

### IV.8 Luồng nền

45. Thiết bị $u$ gửi bản ghi người nó phát hiện về AI node với tốc độ $\lambda_u$ byte/s: vector nếu có bộ tăng tốc, ảnh cắt nếu
    không. **có**
46. Luồng nền chiếm tối đa $\bar u$ (10 hoặc 20 %) thời gian kênh của mỗi môi trường. **có**
47. Trong rừng ít người qua lại nên $\lambda_u$ nhỏ hơn đô thị nhiều. **mở**: cần tần suất ảnh có người của camera bẫy ảnh. Kissling
    2024 có số tổng là khoảng 40 ảnh mỗi camera mỗi ngày.

### IV.9 Vị trí người, báo cáo, xác minh

48. Người ở cell $c^\star$, phân bố đều trên vùng mạng phủ: $\pi_c=1/|\mathcal C|$. **có** (chốt mục 414)
49. Người ở $c^\star$ có thể bị thiết bị của $c^\star$ chụp lại; xác suất phát hiện nằm trong phần ngẫu nhiên $\omega$. **đề xuất**
50. **Giao theo cell** (đề xuất mới). Mọi thiết bị của một cell giao cho cùng một AI node, biến $x_{ck}$ thay cho $x_{uv}$. Lý do:
    - mạng vốn làm việc theo cell (CL gom dữ liệu trong cell);
    - báo cáo đúng khi đó đến từ đúng một critical cell;
    - trọng số có dạng gọn: $w_k=\frac1{|\mathcal C|}\sum_c x_{ck}$ là xác suất báo cáo đúng đến từ $k$.

    **mở**: giao theo thiết bị thì một người có thể bị nhiều AI node báo.
51. AI node $k$ báo điểm số lúc $r_k=C_k+\delta_{\mathrm{match}}+\delta_{\mathrm{LoRa}}$; LoRa một tin mỗi 40 s do giới hạn chu kỳ
    phát. **có**
52. Hậu nghiệm $p_c(t)\propto\ell(s_{k(c)})$ cho cell đã có báo cáo, với $\ell$ là tỉ số hợp lý của điểm số theo mô hình binormal. Cell
    chưa có báo cáo giữ nguyên tiên nghiệm. Vì tiên nghiệm đều, hậu nghiệm chỉ do điểm số quyết định. **có**
53. Đội 2 thăm mỗi lần một cell và nhận ra người nếu thăm đúng $c^\star$. **có**

### IV.10 Độ đo

54. $T^\star$ là thời gian từ lúc đội 1 cất cánh tới lúc đội 2 xác nhận người; ngẫu nhiên theo $\omega$ và $c^\star$. **có**
55. Độ đo chính là $Q_{0.9}[T^\star]=\min\{\theta:\Pr\{T^\star\le\theta\}\ge0{,}9\}$, xác suất lấy chung qua $(\omega,c^\star)$.
    **có** (tạm chốt mục 415, cách B)
56. Độ đo phụ:
    - $\mathbb E[T^\star]$;
    - makespan $\max_kC_k$;
    - tỉ lệ nhiệm vụ xác nhận được người trong sức bền UAV;
    - năng lượng mỗi thiết bị cho một nhiệm vụ.

    **đề xuất**

## V. Phát biểu bài toán

### V.1 Vì sao tách ba bài

57. Bài lý tưởng là chọn chung tất cả để tối thiểu $Q_{0.9}[T^\star]$:
    - AI cell;
    - đường bay và kế hoạch mặt đất;
    - chính sách của đội 2.

    **có**
58. Tách thành ba bài, mỗi bài một mục tiêu riêng, vì hai lý do. **có**
    - Phân vị của một tổng không bằng tổng các phân vị, nên $Q_{0.9}[T^\star]$ không tách cộng được theo pha.
    - (P2) chạy trực tuyến theo báo cáo, còn (P0) và (P1) chạy trước sự cố.
59. (P0) và (P1) đều chạy trước sự cố, nên về nguyên tắc giải chung được. Bài vẫn phát biểu tách để mỗi bài nhận ra được là một lớp
    bài đã biết. Thuật toán thì lặp: chọn $K$, lập kế hoạch pha 1, đưa thời điểm hoàn tất về để sửa $K$. **đề xuất** (tạm chốt mục 415)
60. Ba bài nối nhau qua các đại lượng sau (bảng ở PROBLEMS mục 5):
    - $K$ và $w_k$ từ (P0) sang (P1), (P2);
    - $r_k$ từ (P1) sang (P2).

    **có**

### V.2 (P0) Chọn AI cell

61. Biến: $y_v\in\{0,1\}$ với $v\in V_{\mathrm p}$ (mở AI node $v$); $x_{ck}\in\{0,1\}$ (giao cell $c$ cho AI node ở cell $k$).
    **đề xuất** (giao theo cell, ý 50)
62. Ràng buộc:
    - (a) mỗi cell giao cho đúng một AI node: $\sum_kx_{ck}=1$;
    - (b) chỉ giao cho AI node đang mở: $x_{ck}\le\sum_{v\in k}y_v$;
    - (c) không quá $H$ chặng cell: $h(c,k)\,x_{ck}\le H$;
    - (d) bộ nhớ: $\sum_c\beta_cx_{ck}\le B_k$;
    - (e) nghẽn trên mỗi môi trường: $\sum_{c,k}\lambda_c\,a_m(c,k)\,x_{ck}\,\tau_f\le\bar u$.

    **có** (đổi sang dạng theo cell)
63. Mục tiêu: $\hat{\mathcal J}_0(K)$ là ước lượng $Q_{0.9}[T^\star]$ của một nhiệm vụ trên cả vùng. Vì kế hoạch pha 1 cố định nên chỉ
    có một nhiệm vụ để ước lượng. Ước lượng gồm hai phần:
    - phần pha 1 lấy từ surrogate River, tính theo phân vị có trọng số $w_k$;
    - phần pha 2 tăng theo $|K|$, vì nhiều AI cell thì nhiều báo nhầm.

    **đề xuất**; dạng chính xác của $\hat{\mathcal J}_0$ còn **mở**
64. Năng lượng cho luồng nền chưa đưa vào (P0). **mở** (tạm chốt mục 415)
65. Lớp bài:
    - bỏ (e) và lấy mục tiêu $\sum y_v$ thì được SSCFLP với chi phí mở bằng nhau (Bakker 2025);
    - (c) là bán kính phủ, như bài p-center;
    - (e) làm tải phụ thuộc đường đi chung: hai cell xa nhau vẫn tranh cùng môi trường trên đường về.

    **có**
66. Vì sao khó, viết theo kiểu Zeng 2018. **đề xuất**
    - Biến nhị phân.
    - Mục tiêu không có dạng đóng: $\hat{\mathcal J}_0$ phụ thuộc kế hoạch pha 1, vốn là lời giải của một bài NP-khó khác.

### V.3 (P1) Pha 1 với $K$ cố định

67. Biến: quỹ đạo $q$ (thứ tự cụm nằm trong $q$), lịch phát $s$, kế hoạch mặt đất $f^j_{a\to b,\tau}\in\{0,1\}$. **có**
68. Trạng thái:
    - nhận từ UAV: $h^j_{c,0}=\mathbf 1[j\in R_c(\omega)]$, với $\Pr\{j\in R_c\}=P_c(q(t_j))$;
    - chuyển trên mặt đất: $h^j_{b,\tau+1}=h^j_{b,\tau}\lor\bigvee_af^j_{a\to b,\tau}\xi^j_{a\to b,\tau}$;
    - hoàn tất: $C_k=\min\{\tau:\sum_{j\in D_k}h^j_{k,\tau}\ge Q_k\}$.

    **có**
69. Mục tiêu (cách B): phân vị 0,9 có trọng số của các thời điểm hoàn tất,
    $$\mathcal J_1(q,s,f)=\min\Bigl\{\theta:\textstyle\sum_{k\in K}w_k\Pr\{C_k\le\theta\}\ge0{,}9\Bigr\}.$$
    Ý nghĩa: với xác suất 0,9 theo cả kênh lẫn vị trí người, critical cell giữ bản ghi đúng đã nhận đủ truy vấn trước $\theta$.
    Makespan $\max_kC_k$ là độ đo phụ. **có** (tạm chốt mục 415)
70. Ràng buộc:
    - (a) bay Dubins, trong vùng cho phép $F$, $T_{\mathrm f}\le T_{\mathrm{end}}$;
    - (b) chỉ gửi gói đang giữ: $f^j_{a\to b,\tau}\le h^j_{a,\tau}$;
    - (c) mỗi môi trường một máy phát mỗi khe: $\sum_j\sum_{m(a,b)=m}f^j_{a\to b,\tau}\le1$;
    - (d) năng lượng mỗi cell: $e_{\mathrm{tx}}F_a+e_{\mathrm{rx}}|W_a|\le E_a$, với $F_a=\sum_{j,b,\tau}f^j_{a\to b,\tau}$.

    **có** cho (a)–(c); **đề xuất** cho (d), tạm chốt mục 415
71. Hai giai đoạn:
    - lập kế hoạch $(q,s,\bar f)$ trên bản đồ nhận dự báo $\hat R_c=\{j:P_c(q(t_j))\ge\vartheta\}$;
    - sửa theo thực tế (gom trong cell, takeover, vá).

    River là một chính sách cho giai đoạn một. **có**
72. Lớp bài:
    - phần $q$ là Dubins TSP với lân cận, NP-khó kể cả khi bỏ mặt đất (Định lý 1);
    - với $q$ cố định, phần $f$ là lập lịch phát đa điểm thời gian nhỏ nhất trên môi trường sức chứa một, cùng họ MLBS.

    **có**
73. Chặn dưới. Nới lỏng thành LP tải lớn nhất cho chặn của makespan. Với cách B, LP chỉ cần phục vụ các critical cell có tổng trọng số
    ≥ 0,9; tập đó là một biến nhị phân nữa, nên chặn trở thành bài chọn tập rồi LP. **mở** (cần kiểm)
74. Vì sao khó, viết theo kiểu Zeng 2018. **đề xuất**
    - Phần quỹ đạo liên tục, có ràng buộc độ cong, nên không lồi.
    - Phần mặt đất nhị phân theo thời gian, và gắn với quỹ đạo qua bản đồ nhận $R_c$: đường bay quyết định cell nào giữ gói nào.
    - Mục tiêu phân vị không có dạng đóng theo biến.

### V.4 (P2) Pha 2

75. Dữ liệu:
    - cell nghi vấn $A$, với thời điểm báo cáo $r_c$ và hậu nghiệm $p_c(t)$;
    - thời gian bay $d(i,j)$;
    - thời gian xác minh $\sigma$.

    **có**
76. Biến: lúc cất cánh $t_2$ và chính sách $\mu$, chọn cell kế tiếp từ thông tin đang có. **có**
77. Thời gian xác nhận khi biết trước mọi báo cáo:
    $$T^\star=t_2+\sum_{i\le i^\star}\bigl(w_i+d(c_{i-1},c_i)+\sigma\bigr),$$
    với $w_i$ là thời gian chờ báo cáo. **có** (đổi ký hiệu chờ để khỏi trùng với trọng số $w_k$)
78. Bài: $\min_{t_2,\mu}Q_{0.9}[T^\star]$, với $t_2\ge\min_cr_c$ và trong sức bền đội 2. **có**
79. Do vị trí đều nên thứ tự thăm chỉ phụ thuộc điểm số và quãng bay. Cell chưa có báo cáo vẫn giữ xác suất, nên đội 2 phải cân giữa
    thăm cell điểm cao ngay và chờ báo cáo mới. Đây là chỗ (P1) dính với (P2). **có**
80. Lớp bài:
    - bản tĩnh với kỳ vọng là bài độ trễ nhỏ nhất có trọng số (traveling repairman), NP-khó kể cả trên cây có trọng số (Sitters 2002);
      cũng là dạng tất định của bài đường đi tìm kiếm tối ưu (Trummel và Weisinger 1986);
    - bản tĩnh với phân vị là quota TSP với hạn mức là khối xác suất; bài đối ngẫu là orienteering;
    - có thời điểm báo cáo thì thành bài có ngày phát hành, báo cáo tới dần thì thành bài trực tuyến.

    **có**
81. Không có quãng bay thì thăm theo $p_c$ giảm dần là tối ưu cho kỳ vọng (quy tắc Smith). Chính sách tham lam hiện tại là phiên bản có
    quãng bay của quy tắc này. **có**

### V.5 Kết quả độ khó sẽ nêu

82. Định lý 1: (P1) là NP-khó, quy từ Exact Cover theo Le Ny 2012. **có**
83. Mệnh đề: (P0) là NP-khó, quy từ SSCFLP hoặc phủ tập, giữ đúng mục tiêu. **mở** (cần viết chứng minh)
84. Mệnh đề: bản tĩnh của (P2) là NP-khó, quy từ bài độ trễ nhỏ nhất có trọng số. **mở** (cần viết)

## Còn thiếu trước khi viết thành văn

- Số năng lượng: $E_u$, $e_{\mathrm{rx}}$, $e_{\mathrm{tx}}$ của camera bẫy ảnh và node cảm biến (ý 30).
- Mô hình G2G dưới tán (ý 40).
- Tần suất ảnh có người của camera bẫy ảnh (ý 47).
- Giao theo cell hay theo thiết bị (ý 50).
- Dạng chính xác của $\hat{\mathcal J}_0$ (ý 63) và chặn dưới cho cách B (ý 73).
