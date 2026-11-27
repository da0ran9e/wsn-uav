---
status: current
updated: 2026-11-27
---
# J1 · Bản nháp phần đặt vấn đề, theo từng ý (v2, rừng)

Bản nháp cùng làm theo chatlog mục 415, sửa theo mục 416:
- bộ ký hiệu soạn lại từ đầu;
- ký hiệu đưa vào ngay phần mô tả hệ thống;
- người đi qua nhiều cell, $c^\star$ là vị trí hiện tại;
- mỗi bài toán phát biểu thành câu văn.

Gồm ba mục của bài: mô tả hệ thống (III), mô hình (IV), phát biểu bài toán (V). Quyết định đầu vào lấy từ
[CONTEXT-vi.md](CONTEXT-vi.md), [PROBLEMS-vi.md](PROBLEMS-vi.md) và [OUTLINE-vi.md](OUTLINE-vi.md). Bản ngày 2026-11-27 sáng (84 ý,
ký hiệu cũ) xem trong lịch sử git.

Nhãn cuối ý:
- **có**: số và lập luận đã có nguồn trong repo;
- **đề xuất**: tôi đặt, chờ bạn duyệt;
- **mở**: chưa quyết hoặc chưa có số.

Câu lớn chưa chốt ảnh hưởng cả bản này: truy vấn là ảnh hay vector khi mạng chung chủ (CONTEXT mục 8). Bản này giữ truy vấn ảnh.

## 0. Bộ ký hiệu

Nguyên tắc chọn ký hiệu:
- đối tượng cơ bản trước, theo thứ tự xuất hiện trong bài;
- chữ cái gợi tên tiếng Anh của đối tượng;
- tập viết hoa chữ thư pháp, phần tử viết thường cùng chữ;
- mọi thứ gắn với người cần tìm mang dấu $\star$;
- không dùng một chữ cho hai nghĩa.

| Thứ tự | Ký hiệu | Nghĩa | Gợi nhớ |
|---|---|---|---|
| 1 | $\mathcal C$, $c$ | tập cell, một cell | **C**ell |
| 2 | $R$ | bán kính cell (100 m) | **R**adius |
| 3 | $\mathcal N$, $n$; $\mathcal N_c$ | tập thiết bị, một thiết bị; thiết bị của cell $c$ | **N**ode |
| 4 | $\mathcal E$, $e=(c,c')$ | cặp cell kề, nối bằng một cặp gateway | **E**dge |
| 5 | $G=(\mathcal C,\mathcal E)$ | đồ thị cell | **G**raph |
| 6 | $\mathcal M=\mathcal C\cup\mathcal E$, $m$ | môi trường: mỗi cell, mỗi cặp gateway; mỗi lúc một máy phát | **M**edium |
| 7 | $\mathcal K$, $k$; $\mathcal C_k$ | tập cụm, một cụm; cell của cụm $k$ | clusters, chỉ số $k$ như k-means |
| 8 | $o$ | trạm gốc | **o**rigin |
| 9 | $\mathcal N^{\mathrm{AI}}\subseteq\mathcal N$ | thiết bị làm được AI node (ở chỗ trống) | AI |
| 10 | $\mathcal A\subseteq\mathcal C$, $a$ | tập AI cell (critical cell), một AI cell | **A**I |
| 11 | $y_n$, $x_{ca}$ | mở AI node $n$; giao cell $c$ cho AI cell $a$ | biến nhị phân, $y$ mở, $x$ giao |
| 12 | $\lambda_c$, $b_c$ | tốc độ luồng nền của cell $c$ (B/s); dung lượng bản ghi của $c$ | $\lambda$ tốc độ đến; **b**yte |
| 13 | $H$, $B_a$, $\phi$ | số chặng tối đa; bộ nhớ của AI cell $a$; phần thời gian kênh cho luồng nền | **H**op, **B**uffer |
| 14 | $L$, $Q$, $j$ | số ảnh, số gói của truy vấn, chỉ số gói | **Q**uery |
| 15 | $\mathbf q(t)$, $T_{\mathrm f}$ | đường bay của đội 1, thời gian bay | **q**uỹ đạo; **f**light |
| 16 | $h$, $v$, $\rho$ | độ cao, tốc độ, bán kính quay của đội 1 | **h**eight, **v**elocity |
| 17 | $T_{\mathrm p}$, $t_j$ | chu kỳ phát gói; lúc phát gói $j$ | **p**acket |
| 18 | $\mu(\cdot)$, $P_c(\mathbf q)$, $R_{50}$, $\kappa$ | xác suất một thiết bị nhận gói theo khoảng cách; xác suất cell nhận; khoảng cách nhận 50 %; ngưỡng tin cậy khi lập kế hoạch | **P** probability |
| 19 | $\mathcal R_c$ | tập gói cell $c$ nhận từ UAV | **R**eceived |
| 20 | $\tau$, $f^j_{c\to c'}(\tau)$, $s^j_c(\tau)$ | khe mặt đất (một chặng có xác nhận); kế hoạch gửi gói $j$ từ $c$ sang $c'$; cell $c$ đang giữ gói $j$ | **f**orward, **s**tored |
| 21 | $\mathcal S_a$, $Q_a$ | đoạn gói AI cell $a$ dùng; số gói $a$ cần | **S**egment |
| 22 | $C_a$, $r_a$ | lúc AI cell $a$ nhận đủ truy vấn; lúc báo cáo của $a$ tới trạm | **C**ompletion, **r**eport |
| 23 | $E_n$, $e_{\mathrm{tx}}$, $e_{\mathrm{rx}}$, $W_c$ | ngân sách năng lượng; năng lượng mỗi khung phát, mỗi giây thức; cửa sổ thức của cell $c$ | **E**nergy, **W**ake |
| 24 | $\mathbf x^\star(t)$, $c^\star$ | vị trí người lúc $t$; cell người đang ở lúc xác minh | $\star$ = người cần tìm |
| 25 | $\delta_c$, $t^{\mathrm d}_c$ | cell $c$ ghi được người hay không; lúc ghi | **d**etection |
| 26 | $\gamma_c$ | điểm sàng lọc của cell $c$ do AI cell trả về | điểm số |
| 27 | $\pi_c(t)$ | xác suất người đang ở cell $c$, theo thông tin tới lúc $t$; $\pi_c(0)=1/\lvert\mathcal C\rvert$ | $\pi$ phân bố |
| 28 | $v_2$, $\sigma$, $d(c,c')$ | tốc độ đội 2; thời gian xác minh một cell; thời gian bay của đội 2 giữa hai cell | $\sigma$ dừng |
| 29 | $w_a$ | trọng số của AI cell $a$ trong mục tiêu | **w**eight |
| 30 | $\omega$ | mọi phần ngẫu nhiên: kênh, MAC, quỹ đạo người, phát hiện, điểm số | |
| 31 | $T^\star$, $T^\star_{90}$ | thời gian từ cất cánh tới khi xác nhận người; phân vị 90 % của nó | $\star$ = người cần tìm |

Đổi so với bản đô thị:
- $V\to\mathcal N$ (node);
- $K\to\mathcal A$ (AI cell);
- $h^j_{c,\tau}\to s^j_c(\tau)$, vì $h$ dành cho độ cao;
- $D_k\to\mathcal S_a$;
- $p(d)\to\mu(\cdot)$, vì $p$ dễ lẫn với xác suất vị trí;
- $Q_{0.9}[\cdot]\to T^\star_{90}$, vì $Q$ dành cho số gói;
- thời gian chờ ở (P2) đổi chữ để khỏi trùng $w_a$;
- cụm dùng $\mathcal K$, $k$.

## III. Mô tả hệ thống (lời văn có ký hiệu)

### III.1 Vùng, mạng, thiết bị

1. Vùng là một khu rừng đất thấp, phẳng hoặc thoải, ví dụ cửa sổ 10 × 10 km ở Cát Tiên (chênh cao trong một cell trung vị 14 m). Vùng
   được chia thành các cell lục giác $c\in\mathcal C$ bán kính $R=100$ m. **có**
2. Trong vùng có tập thiết bị $\mathcal N$ chạy pin của ban quản lý rừng và các đối tác: camera bẫy ảnh, cảm biến âm thanh, cảm biến
   cháy. Thiết bị của cell $c$ là $\mathcal N_c$. Lõi rừng không có sóng di động. **đề xuất** (chủ sở hữu phụ thuộc CONTEXT mục 8)
3. Hai cell kề $e=(c,c')\in\mathcal E$ nối với nhau bằng đúng một cặp gateway; $G=(\mathcal C,\mathcal E)$ là đồ thị cell. Cell
   không có thiết bị (sông, đầm) là lỗ của $G$. **có**
4. Mỗi cell và mỗi cặp gateway là một môi trường $m\in\mathcal M$: trong một môi trường, mỗi lúc chỉ một radio phát. **có**
5. Cell gom thành cụm $k\in\mathcal K$; mỗi cụm có một trưởng cụm có thêm radio LoRa nói chuyện được với trạm gốc $o$. Nguyên lý chia
   cụm (CONTEXT mục 9): đường kính một cụm khoảng bằng quãng UAV bay khi phát một bản truy vấn, tức $Q T_{\mathrm p} v\approx2$ km, ứng
   với trần 80 cell. **có** (thuật toán), **đề xuất** (cách lý giải)
6. Một số thiết bị $\mathcal N^{\mathrm{AI}}\subseteq\mathcal N$ ở chỗ trống, có tấm pin mặt trời và bộ tăng tốc, làm được AI node.
   Cell có AI node đang mở là AI cell $a\in\mathcal A$. **đề xuất**
7. Trạm gốc $o$ đặt ở trạm kiểm lâm bìa rừng, có LoRa gateway và hai UAV:
   - đội 1: UAV cánh bằng VTOL, phát truy vấn;
   - đội 2: UAV cánh quay có camera, xác minh.

   **đề xuất**

### III.2 Pha 0, trước mọi sự cố

8. Trạm gốc dựng tổ chức mạng một lần: CL của mỗi cell, cặp gateway của mỗi $e\in\mathcal E$, cụm $\mathcal K$. **có**
9. Trạm gốc chọn tập AI cell $\mathcal A$ và giao mỗi cell $c$ cho một AI cell $a$ ($x_{ca}=1$). Thiết bị của $c$ gửi bản ghi những
   người chúng phát hiện về $a$ với tốc độ $\lambda_c$. **có** (giao theo cell: **đề xuất**)
10. Không có thông tin vị trí nên vùng nhiệm vụ luôn là cả $\mathcal C$. Trạm gốc tính sẵn một kế hoạch pha 1 gồm:
    - đường bay $\mathbf q(t)$, $t\in[0,T_{\mathrm f}]$;
    - kế hoạch mặt đất $f$.

    Phần kế hoạch của mỗi cell được lưu tại cell đó. **đề xuất** (tạm chốt mục 415)
11. Kế hoạch tính lại khi thiết bị hỏng, thêm hay bớt. **đề xuất**

### III.3 Người cần tìm

12. Người đi lạc trong rừng một thời gian trước khi được báo mất tích. Quỹ đạo $\mathbf x^\star(t)$ đi qua nhiều cell. **có** (mục 416)
13. Không phải thiết bị nào người đi qua cũng chụp được: cell $c$ ghi được người với một xác suất nào đó ($\delta_c=1$, lúc
    $t^{\mathrm d}_c$). Các cell ghi được tạo thành một vết thưa dọc quỹ đạo. **có** (mục 416)
14. $c^\star$ là cell người đang ở vào lúc đội 2 tới xác minh. Nhiệm vụ chỉ thành công khi đội 2 xác minh đúng $c^\star$; các cell cũ
    trên vết cũng cho điểm sàng lọc cao nhưng người đã rời đi. **có** (mục 416)

### III.4 Khi có sự cố

15. Có người báo mất tích. Thông tin duy nhất là $L=12$ ảnh do người thân cung cấp; không có điểm thấy cuối. **có**
16. Trạm gốc dựng truy vấn $Q=4041$ gói từ bộ ảnh, rồi phát qua LoRa một bản tin đánh thức vài byte (mã nhiệm vụ, giờ cất cánh). **có**
17. Từ bản tin và kế hoạch đã lưu, mỗi cell $c$ tự tính cửa sổ thức $W_c$. **đề xuất**

### III.5 Pha 1, phát truy vấn

18. Đội 1 cất cánh từ $o$, bay theo $\mathbf q(t)$ ở độ cao $h$, phát gói $j$ lúc $t_j$, mỗi gói cách nhau $T_{\mathrm p}$, lặp lại
    truy vấn dọc đường. **có**
19. Cell $c$ dưới đường bay giữ tập gói $\mathcal R_c$ mà thiết bị của nó nghe được. **có**
20. Theo kế hoạch $f$, cell gửi gói từng khe $\tau$ sang cell kề, dọc đường cell về các AI cell. **có**
21. Bước sửa bù chỗ hổng do mất gói hoặc bay lệch gồm:
    - gom và sửa trong cell;
    - takeover;
    - vá cell còn thiếu.

    **có** (vá: **mở**)
22. AI cell $a$ nhận đủ truy vấn lúc $C_a$. Nó đối sánh truy vấn với bản ghi của các cell giao cho nó, rồi gửi qua trưởng cụm về trạm
    lúc $r_a$ hai thứ cho mỗi cell $c$ của mình:
    - điểm sàng lọc $\gamma_c$;
    - lúc ghi $t^{\mathrm d}_c$ của bản ghi khớp nhất.

    **đề xuất** (thêm lúc ghi vào báo cáo, vài byte)

### III.6 Pha 2, xác minh

23. Trạm gốc cập nhật $\pi_c(t)$, xác suất người đang ở cell $c$, từ điểm số và lúc ghi. **đề xuất** (mô hình ở IV.9)
24. Đội 2 cất cánh, chọn cell kế tiếp theo $\pi_c(t)$ và thời gian bay $d(\cdot,\cdot)$, xác minh mất $\sigma$, rồi chọn tiếp; tính
    lại khi có báo cáo mới. **có**
25. Nhiệm vụ kết thúc khi đội 2 xác nhận người ở $c^\star$, lúc $T^\star$ tính từ khi đội 1 cất cánh. **có**

### III.7 Phạm vi

26. Phạm vi của bài:
    - một UAV ở pha 1;
    - rừng phẳng hoặc thoải;
    - chỉ xét nhiệm vụ có ít nhất một cell ghi được người ($\sum_c\delta_c\ge1$).

    **có** (tạm chốt mục 411, 415)

## IV. Mô hình

### IV.1 Đội 1 và cách phát

27. Đội 1: $h=100$ m, $v\in[25,50]$ m/s, góc nghiêng ≤ 45°, $\rho(v)=v^2/g$ (255 m ở 50 m/s). $\mathbf q$ đi từ $o$ và về $o$.
    **có**
28. Gói 99 B, $T_{\mathrm p}=10$ ms; một bản truy vấn trải dài $Q T_{\mathrm p}v\approx2$ km bay. **có**

### IV.2 Kênh A2G qua tán

29. Suy hao hai đoạn cộng suy hao tán $L_{\mathrm{obs}}$; Rician $K=2$; ngưỡng hiệu dụng $S=-101{,}04$ dBm. Từ đó có $\mu(\cdot)$,
    xác suất một thiết bị nhận gói theo khoảng cách ngang. **có**
30. Bốn chế độ $L_{\mathrm{obs}}=0/9/19{,}8/25{,}7$ dB, ứng với $R_{50}=1016/498/199/99$ m. Ba chế độ có tán ứng với 17/66/103 m đường
    qua cây theo Weissberger. Áp cho đường xiên là ngoại suy. **có**
31. Xác suất cell nhận một gói phát khi UAV ở $\mathbf q$: $P_c(\mathbf q)=1-\prod_{n\in\mathcal N_c}(1-\mu(\lVert\mathbf q-\mathbf
    n\rVert))$, với giả định các thiết bị nhận độc lập. **có**

### IV.3 Kênh G2G và môi trường

32. Kênh G2G: log-distance (số mũ 3,5), shadowing 7,8 dB, Rayleigh khối 100 ms, cộng suy hao tán. **mở** (cần mô hình đo trong rừng)
33. Một chặng có xác nhận chiếm môi trường $\tau\approx5$–7 ms (tối thiểu 4,8 ms). **có**

### IV.4 Truy vấn và hoàn tất

34. Có mã không tỉ lệ thì AI cell $a$ cần $Q_a=\lceil(1+\epsilon)Q\rceil$ gói khác nhau trong đoạn $\mathcal S_a$ ($\epsilon=0{,}05$).
    **có**
35. $C_a$ là lúc CL của $a$ giữ đủ $Q_a$ gói. **có**

### IV.5 Luồng nền

36. Cell $c$ gửi bản ghi về AI cell của nó với tốc độ $\lambda_c$; luồng nền chiếm tối đa $\phi$ (10 hoặc 20 %) thời gian kênh của mỗi
    môi trường. **có**
37. Rừng ít người nên $\lambda_c$ nhỏ. **mở** (số ảnh có người của camera bẫy ảnh)

### IV.6 Năng lượng

38. Thiết bị $n$ có ngân sách $E_n$ cho một nhiệm vụ, tốn $e_{\mathrm{tx}}$ mỗi khung phát và $e_{\mathrm{rx}}$ mỗi giây thức.
    Ngân sách cell $E_c$ là tổng ngân sách các thiết bị chuyển tiếp của cell. **đề xuất**; số liệu **mở**
39. Cửa sổ thức $W_c$ suy ra từ kế hoạch: từ lúc UAV tới gần $c$ hoặc gói đầu tiên cần qua $c$, tới lúc $c$ chuyển xong. **đề xuất**

### IV.7 Đội 2

40. $v_2=15$ m/s, $\sigma\approx78$ s mỗi lần xác minh; $d(c,c')$ là thời gian bay giữa hai cell. **có**
41. Dưới tán dày, camera của đội 2 có thể không thấy người. **mở** (camera nhiệt, hạ thấp ở chỗ trống, hay coi xác minh luôn đúng)

### IV.8 Người cần tìm và phát hiện

42. Lúc bắt đầu, người ở một cell bất kỳ với xác suất như nhau. **có** (chốt mục 414)
43. Người di chuyển với tốc độ không quá $v^\star$, có thể dừng hẳn sau một lúc. **đề xuất**; mô hình di chuyển còn **mở** (đi ngẫu
    nhiên, hay đi rồi dừng)
44. Khi người ở trong cell $c$, thiết bị của $c$ ghi được người với xác suất $p^{\mathrm d}$ mỗi lần đi qua: $\delta_c=1$, lúc
    $t^{\mathrm d}_c$. **đề xuất**
45. AI cell trả điểm $\gamma_c$ cao cho mọi cell có $\delta_c=1$, kể cả cell cũ trên vết, và điểm thấp (có lúc cao nhầm) cho cell khác.
    Mô hình điểm là binormal như bản ICC. **có**

### IV.9 Hậu nghiệm về vị trí hiện tại

46. Gọi $c_{\mathrm{last}}$ là cell có điểm cao với lúc ghi muộn nhất. Người đang ở trong vùng đi được từ $c_{\mathrm{last}}$ trong thời
    gian $t-t^{\mathrm d}_{c_{\mathrm{last}}}$, bán kính khoảng $v^\star(t-t^{\mathrm d}_{c_{\mathrm{last}}})$. **đề xuất**
47. $\pi_c(t)$ ghép ba nguồn thông tin:
    - tiên nghiệm đều;
    - điểm số và lúc ghi của mọi cell đã báo;
    - mô hình di chuyển.

    Cell chưa báo giữ phần xác suất của mình. Vết càng cũ thì xác suất càng loang rộng. **đề xuất**
48. Hệ quả cho pha 2: cell điểm cao nhất chưa chắc là nơi nên tới; nên tới chỗ ghi muộn nhất, hoặc vùng quanh nó. **đề xuất**

### IV.10 Độ đo

49. $T^\star$ là thời gian từ lúc đội 1 cất cánh tới khi đội 2 xác nhận người ở $c^\star$; ngẫu nhiên theo $\omega$. **có**
50. Độ đo chính là $T^\star_{90}=\min\{\theta:\Pr\{T^\star\le\theta\}\ge0{,}9\}$, xác suất lấy chung qua $\omega$, tức qua cả kênh lẫn
    quỹ đạo người. **có** (tạm chốt mục 415)
51. Độ đo phụ:
    - $\mathbb E[T^\star]$;
    - makespan $\max_aC_a$;
    - tỉ lệ nhiệm vụ thành công trong sức bền UAV;
    - năng lượng mỗi thiết bị.

    **đề xuất**

## V. Phát biểu bài toán

### V.1 Vì sao tách ba bài

52. Bài lý tưởng là chọn chung AI cell, đường bay, kế hoạch mặt đất và chính sách đội 2 để $T^\star_{90}$ nhỏ nhất. Bài tách thành ba,
    vì hai lý do:
    - phân vị của một tổng không bằng tổng các phân vị;
    - (P2) chạy theo báo cáo, còn (P0) và (P1) chạy trước sự cố.

    **có**
53. (P0) và (P1) phát biểu tách, còn thuật toán thì giải lặp giữa hai bài. **đề xuất** (tạm chốt mục 415)
54. Trọng số $w_a$ nối ba bài. Báo cáo quyết định là báo cáo về lần ghi muộn nhất; với tiên nghiệm đều và người đi không xa, xác suất
    báo cáo đó đến từ AI cell $a$ xấp xỉ phần vùng giao cho $a$: $w_a\approx\frac1{\lvert\mathcal C\rvert}\sum_cx_{ca}$. **đề xuất**
    (xấp xỉ, cần kiểm khi người đi xa)

### V.2 (P0) Chọn AI cell

55. **Phát biểu.** Cho:
    - đồ thị cell $G$ và tập môi trường $\mathcal M$;
    - tập thiết bị làm được AI node $\mathcal N^{\mathrm{AI}}$;
    - tốc độ luồng nền $\lambda_c$ và dung lượng bản ghi $b_c$ của mỗi cell.

    Chọn những thiết bị làm AI node và giao mỗi cell cho một AI cell sao cho ước lượng phân vị 90 % của thời gian tìm người là nhỏ
    nhất. Điều kiện:
    - mỗi cell giao cho đúng một AI cell đang mở;
    - cell cách AI cell của nó không quá $H$ chặng;
    - tổng bản ghi giao cho một AI cell không vượt bộ nhớ $B_a$ của nó;
    - luồng nền đi qua mỗi môi trường chiếm không quá phần $\phi$ thời gian kênh.

    **đề xuất**
56. **Dạng toán.**
    $$\min_{x,y}\ \hat T^\star_{90}(\mathcal A(y))\quad\text{s.t.}\quad \sum_ax_{ca}=1;\ \ x_{ca}\le\sum_{n\in\mathcal N_a}y_n;\ \
    h(c,a)\,x_{ca}\le H;\ \ \sum_cb_cx_{ca}\le B_a;\ \ \sum_{c,a}\lambda_c\,\alpha_m(c,a)\,x_{ca}\,\tau\le\phi\ \ \forall m.$$
    Ở đây $\alpha_m(c,a)$ là số khung trên môi trường $m$ cho mỗi byte đi từ $c$ tới $a$, và $h(c,a)$ là số chặng cell. **đề xuất**
57. **Mục tiêu.** $\hat T^\star_{90}$ là ước lượng cho một nhiệm vụ trên cả vùng, gồm hai phần:
    - phần pha 1 từ surrogate River, tính theo trọng số $w_a$;
    - phần pha 2 tăng theo $\lvert\mathcal A\rvert$, vì nhiều AI cell thì nhiều báo nhầm.

    **mở** (dạng chính xác)
58. **Lớp bài.** Bỏ ràng buộc nghẽn và lấy mục tiêu số AI node thì được SSCFLP với chi phí mở bằng nhau (Bakker 2025); ràng buộc
    chặng là bán kính phủ. Ràng buộc nghẽn là chỗ khác: tải phụ thuộc đường đi chung. **có**
59. **Vì sao khó.**
    - Biến nhị phân.
    - Mục tiêu không có dạng đóng: nó phụ thuộc lời giải của (P1), vốn là bài NP-khó.

    **đề xuất**

### V.3 (P1) Pha 1 với tập AI cell cố định

60. **Phát biểu.** Cho:
    - tập AI cell $\mathcal A$ và trọng số $w_a$;
    - mô hình nhận gói $P_c$;
    - ngân sách năng lượng của các cell.

    Chọn đường bay của đội 1, thứ tự phát gói và kế hoạch chuyển gói trên mặt đất sao cho thời điểm mà, với xác suất 0,9, AI cell giữ
    báo cáo quyết định đã nhận đủ truy vấn là sớm nhất. Điều kiện:
    - đường bay khả thi với UAV cánh bằng (tốc độ, bán kính quay), nằm trong vùng cho phép và trong sức bền;
    - cell chỉ gửi gói nó đang giữ;
    - mỗi môi trường mỗi khe chỉ một máy phát;
    - năng lượng mỗi cell tiêu trong nhiệm vụ không vượt ngân sách.

    **đề xuất**
61. **Trạng thái.**
    - Nhận từ UAV: $s^j_c(0)=\mathbf 1[j\in\mathcal R_c]$, với $\Pr\{j\in\mathcal R_c\}=P_c(\mathbf q(t_j))$.
    - Chuyển: $s^j_{c'}(\tau+1)=s^j_{c'}(\tau)\lor\bigvee_cf^j_{c\to c'}(\tau)\,\xi^j_{c\to c'}(\tau)$, với $\xi$ là chuyển thành công.
    - Hoàn tất: $C_a=\min\{\tau:\sum_{j\in\mathcal S_a}s^j_a(\tau)\ge Q_a\}$.

    **có**
62. **Dạng toán.**
    $$\min_{\mathbf q,(t_j),f}\ C_{90}=\min\Bigl\{\theta:\sum_aw_a\Pr\{C_a\le\theta\}\ge0{,}9\Bigr\}$$
    $$\text{s.t.}\quad \mathbf q\ \text{Dubins},\ \mathbf q(t)\in F,\ T_{\mathrm f}\le T_{\mathrm{end}};\ \ f^j_{c\to c'}(\tau)\le
    s^j_c(\tau);\ \ \sum_j\sum_{(c,c')\in m}f^j_{c\to c'}(\tau)\le1\ \forall m,\tau;\ \ e_{\mathrm{tx}}F_c+e_{\mathrm{rx}}\lvert
    W_c\rvert\le E_c.$$
    Ở đây $F_c=\sum_{j,c',\tau}f^j_{c\to c'}(\tau)$ là số khung cell $c$ gửi. **có** (ba ràng buộc đầu), **đề xuất** (mục tiêu
    $C_{90}$, ràng buộc năng lượng)
63. **Hai giai đoạn.** Giai đoạn một lập kế hoạch trên bản đồ nhận dự báo $\hat{\mathcal R}_c=\{j:P_c(\mathbf q(t_j))\ge\kappa\}$, với $\kappa$ là ngưỡng tin cậy.
    Giai đoạn hai sửa theo thực tế. River là một chính sách cho giai đoạn một. **có**
64. **Lớp bài.**
    - Phần đường bay là Dubins TSP với lân cận, NP-khó kể cả khi bỏ mặt đất (Định lý 1).
    - Với đường bay cố định, phần mặt đất là lập lịch phát đa điểm thời gian nhỏ nhất trên môi trường sức chứa một, cùng họ MLBS.

    **có**
65. **Vì sao khó.**
    - Đường bay liên tục, có ràng buộc độ cong.
    - Kế hoạch mặt đất nhị phân theo thời gian, gắn với đường bay qua $\mathcal R_c$.
    - Mục tiêu phân vị không có dạng đóng.

    **đề xuất**
66. **Chặn dưới.** LP tải lớn nhất cho chặn của makespan. Với $C_{90}$ chỉ phải phục vụ tập AI cell có tổng trọng số ≥ 0,9, nên chặn
    thành bài chọn tập rồi LP. **mở**

### V.4 (P2) Pha 2

67. **Phát biểu.** Cho:
    - các báo cáo tới dần: với mỗi cell có điểm sàng lọc và lúc ghi;
    - xác suất hiện tại $\pi_c(t)$;
    - thời gian bay $d(\cdot,\cdot)$ và thời gian xác minh $\sigma$.

    Chọn lúc đội 2 cất cánh và quy tắc chọn cell kế tiếp sao cho phân vị 90 % của thời điểm xác nhận được người ở vị trí hiện tại là
    sớm nhất. Điều kiện:
    - đội 2 chỉ cất cánh khi đã có ít nhất một báo cáo;
    - đội 2 trong sức bền.

    **đề xuất**
68. **Dạng toán.** Nếu biết trước mọi báo cáo và người đứng yên, chính sách là một dãy $(c_1,c_2,\dots)$, và với $c^\star=c_{i^\star}$:
    $$T^\star=t_2+\sum_{i\le i^\star}\bigl(\vartheta_i+d(c_{i-1},c_i)+\sigma\bigr),\qquad c_0=o,$$
    với $\vartheta_i\ge0$ là thời gian chờ báo cáo. Bài: $\min_{t_2,\text{chính sách}}T^\star_{90}$, với $t_2\ge\min_ar_a$. **có** (đổi
    ký hiệu chờ)
69. **Người di chuyển** làm bài khác bản đô thị. Xác suất của mỗi cell đổi theo thời gian ngay cả khi không có báo cáo mới, vì vết cũ
    loang ra. Bài thành tìm mục tiêu di động có thông tin trễ. **đề xuất**; cần tra lý thuyết tìm kiếm mục tiêu di động
70. **Lớp bài.**
    - Bản tĩnh, người đứng yên, mục tiêu kỳ vọng: bài độ trễ nhỏ nhất có trọng số, NP-khó (Sitters 2002); dạng tất định của bài đường đi
      tìm kiếm tối ưu (Trummel và Weisinger 1986).
    - Mục tiêu phân vị: quota TSP với hạn mức là khối xác suất.
    - Báo cáo tới dần: bài trực tuyến.
    - Người di chuyển: bài tìm mục tiêu di động.

    **có** cho ba ý đầu, **mở** cho ý cuối

### V.5 Kết quả độ khó sẽ nêu

71. Định lý 1: (P1) là NP-khó. **có**
72. Mệnh đề: (P0) là NP-khó, quy từ SSCFLP. **mở**
73. Mệnh đề: bản tĩnh của (P2) là NP-khó, quy từ bài độ trễ nhỏ nhất có trọng số. **mở**

## Còn mở

- Truy vấn ảnh hay vector (CONTEXT mục 8); câu này kéo theo cỡ cụm (CONTEXT mục 9).
- Mô hình di chuyển của người (ý 43) và xác minh dưới tán (ý 41).
- Số năng lượng (ý 38), mô hình G2G (ý 32), luồng nền (ý 37).
- Dạng chính xác của $\hat T^\star_{90}$ (ý 57), xấp xỉ $w_a$ (ý 54), chặn cho $C_{90}$ (ý 66).
