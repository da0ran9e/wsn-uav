---
status: current
updated: 2026-11-26
---
# J1 · Ba bài toán cốt lõi, phiên bản rừng (v2, đang bàn)

Bàn theo chatlog mục 414: bàn ba bài toán trước khi viết tiếp. Điểm xuất phát là ba bài của bản đô thị
([archive/urban-v1/PROBLEMS-vi.md](archive/urban-v1/PROBLEMS-vi.md)). File này ghi những gì đổi khi chuyển sang rừng và đổi sang
tiên nghiệm đều không có điểm thấy cuối. Mỗi ý ghi **chốt**, **đề xuất** hoặc **mở**.

## 0. Tiền đề mới

1. **Không có thông tin vị trí** (chốt, mục 414). Ngoài bộ ảnh truy vấn không biết gì, nên người cần tìm ở cell $c^\star$ có phân bố
   đều trên vùng mạng phủ: $\Pr\{c^\star=c\}=1/|\mathcal C|$.
2. **Vùng nhiệm vụ là cả vùng mạng phủ** (đề xuất). Không có điểm thấy cuối thì không khoanh được vùng nhỏ hơn. Vùng mạng của một
   chuyến bay khoảng 50 cụm, cỡ cửa sổ 10 × 10 km; vườn lớn hơn thì chia thành nhiều vùng, mỗi vùng một chuyến.
3. **Kế hoạch pha 1 cố định, tính xong từ pha 0** (đề xuất, hệ quả của 1 và 2). Vùng nhiệm vụ không đổi theo sự cố, nên đường bay
   và kế hoạch mặt đất chỉ phụ thuộc mạng. Khi có sự cố, trạm gốc chỉ cần phát truy vấn và bản tin đánh thức. Bản đô thị phải tính
   kế hoạch theo từng vùng sự cố.
4. **Người được thấy ở đâu.** Người ở cell $c^\star$ bị các thiết bị của $c^\star$ chụp (với xác suất phát hiện nằm trong $\omega$);
   bản ghi của thiết bị $u$ nằm ở AI node $v(u)$. Báo cáo đúng vì vậy đến từ critical cell giữ bản ghi của $c^\star$. Gọi $w_k$ là tỉ
   lệ cell có bản ghi về critical cell $k$; với tiên nghiệm đều, $\Pr\{\text{báo cáo đúng đến từ }k\}=w_k$.

## 1. Mục tiêu chung và hệ quả của tiên nghiệm đều

Mục tiêu vẫn là $\min Q_{0.9}[T^\star]$, báo kèm $\mathbb E[T^\star]$. Với $k^\star$ là critical cell giữ bản ghi đúng,

$$T^\star\approx C_{k^\star}+\delta_{\mathrm{match}}+\delta_{\mathrm{LoRa}}+T_2,$$

trong đó $T_2$ là thời gian từ lúc báo cáo đúng tới khi UAV cánh quay xác nhận.

Câu "phân vị lấy qua những gì" (còn mở từ bản đô thị) giờ quyết định thẳng mục tiêu của (P1):
- **Cách B, phân vị chung qua $(\omega,c^\star)$.** Bỏ qua $T_2$ thì $Q_{0.9}[C_{k^\star}]$ là $\theta$ nhỏ nhất sao cho
  $\sum_k w_k\Pr\{C_k\le\theta\}\ge0{,}9$. Mục tiêu của (P1) thành phân vị 0,9 có trọng số của các thời điểm hoàn tất, không phải
  thời điểm critical cell cuối cùng xong. Kế hoạch được phép để chậm những critical cell giữ tổng cộng dưới 10 % vùng.
- **Cách A, trường hợp xấu nhất theo $c^\star$.** $\max_{c^\star}Q_{0.9,\omega}$ cho mục tiêu makespan $\max_kC_k$ như bản đô thị.

Cách B khớp đúng với tiên nghiệm đều và cho bài toán mới hơn. Cách A dễ bảo vệ hơn ("không bỏ ai") và giữ được các kết quả makespan
đã có (Định lý 1, chặn LP tải lớn nhất). Đề xuất: lấy cách B làm mục tiêu chính, báo makespan như một độ đo phụ. **mở**

## 2. (P0) Chọn AI cell

Giữ dạng facility location có sức chứa, một nguồn (urban-v1 mục 1):
- biến $y_v$ (thiết bị $v$ làm AI node), $x_{uv}$ (thiết bị $u$ giao cho $v$);
- ràng buộc: mỗi thiết bị một AI node, chỉ giao cho AI node đang mở, không quá $H$ chặng, bộ nhớ, luồng nền mỗi môi trường
  $\le\bar u$.

Đổi cho rừng:
1. **Tập ứng viên nhỏ** (đề xuất). $V_{\mathrm p}$ chỉ gồm thiết bị ở chỗ trống đặt được tấm pin mặt trời. Đây là dữ liệu đầu vào;
   chưa có cách sinh $V_{\mathrm p}$ (OSM không có lớp rừng dùng được, cần bản đồ lớp phủ như ESA WorldCover). **mở**
2. **Luồng nền nhẹ** (đề xuất). Ít người qua lại nên ràng buộc nghẽn ít khi chặt; ràng buộc chặng và bộ nhớ thành chính.
3. **Năng lượng cho luồng nền** (mở). Thiết bị chạy pin nên mỗi lần chuyển tiếp bản ghi cho thiết bị khác đều tốn pin. Có thể thêm
   $\sum_{u,v}\lambda_u\,b_n(u,v)\,x_{uv}\,e_{\mathrm{tx}}\le\bar e_n$ cho mỗi thiết bị $n$, với $b_n(u,v)$ là số khung $n$ phải gửi
   cho mỗi byte đi từ $u$ tới $v$. Ràng buộc này cùng dạng ràng buộc nghẽn, nhưng tính theo thiết bị thay vì theo môi trường.
4. **Mục tiêu** (đề xuất). Vì kế hoạch pha 1 cố định (tiền đề 3), mục tiêu của (P0) là ước lượng $Q_{0.9}[T^\star]$ của đúng một
   nhiệm vụ, không còn phải lấy trung bình qua các vùng sự cố. Ước lượng gồm surrogate River cho phần pha 1 và một số hạng tăng theo
   $|K|$ cho báo nhầm ở pha 2.

**Câu lớn.** Pha 0 và pha 1 đều chạy trước sự cố. Có giải chung (P0) và (P1) thành một bài offline không, hay vẫn tách? Bản đô thị
tách vì kế hoạch pha 1 phụ thuộc vùng sự cố; lý do đó không còn. Giải chung thì đúng mục tiêu hơn nhưng khó hơn nhiều. Đề xuất: vẫn
tách khi phát biểu (dễ nhận lớp bài), còn thuật toán thì lặp: chọn $K$, lập kế hoạch pha 1, đưa thời điểm hoàn tất thật về sửa $K$.
**mở**

## 3. (P1) Pha 1 với K cố định

Giữ dạng urban-v1 mục 2:
- biến: quỹ đạo $q$, lịch phát $s$, kế hoạch mặt đất $f^j_{a\to b,\tau}$;
- ràng buộc: bay Dubins trong vùng cho phép và trong sức bền; chỉ gửi gói đang giữ; mỗi môi trường một máy phát mỗi khe;
- hai giai đoạn: lập kế hoạch trên bản đồ nhận dự báo, rồi sửa theo thực tế (gom trong cell, takeover, vá).

Đổi cho rừng:
1. **Mục tiêu** theo câu ở mục 1: cách B là phân vị 0,9 có trọng số $w_k$ của $C_k$; cách A là makespan. **mở**
2. **Năng lượng** (đề xuất). Thêm $e_{\mathrm{tx}}F_a+e_{\mathrm{rx}}W_a\le E_a$ cho mỗi cell $a$, với $F_a$ là số khung $a$ gửi
   và $W_a$ là độ dài cửa sổ thức. Ràng buộc này phạt các cell nằm trên nhiều đường vận chuyển (SPINE, Bank) và các cell phải thức
   lâu. Cần số năng lượng thật để biết ràng buộc có chặt không; nếu không chặt thì chỉ báo năng lượng ở phần đánh giá. **mở**
3. **Cửa sổ thức là biến hay là hệ quả.** Nếu kế hoạch cố định thì $W_a$ suy ra từ kế hoạch: từ lúc UAV tới gần $a$ (hoặc gói đầu
   tiên cần chuyển qua $a$) tới lúc $a$ chuyển xong. Đề xuất coi $W_a$ là hệ quả, không phải biến riêng. **đề xuất**
4. **Kênh** đổi sang suy hao qua tán (A2G có sẵn bốn chế độ; G2G còn thiếu mô hình). Dạng bài toán không đổi.

**Lớp bài:** như bản đô thị. Phần quỹ đạo là Dubins TSP với lân cận (Định lý 1, NP-khó). Với $q$ cố định, phần mặt đất là lập lịch
phát đa điểm thời gian nhỏ nhất. Chặn LP tải lớn nhất vẫn đúng cho makespan. Với cách B, chặn đổi thành bài LP chọn tập critical cell
có tổng trọng số $\ge0{,}9$ rồi lấy tải lớn nhất trên tập đó; cần kiểm lại.

## 4. (P2) Pha 2: xác minh

Giữ dạng urban-v1 mục 3: chọn lúc cất cánh $t_2$ và chính sách thăm $\mu$; mục tiêu $Q_{0.9}[T^\star]$ hoặc $\mathbb E[T^\star]$.

Đổi do tiên nghiệm đều:
1. **Hậu nghiệm chỉ đến từ điểm số** (chốt, hệ quả của mục 414). Với cell $c$ thuộc AI node $k$:
   $p_c(t)\propto\pi_c\,\ell(s_c)=\ell(s_c)/|\mathcal C|$, với $\ell$ là tỉ số hợp lý của điểm số (mô hình binormal), và cell chưa
   có báo cáo giữ nguyên tiên nghiệm. Vì tiên nghiệm đều, thứ tự thăm chỉ phụ thuộc điểm số và quãng bay.
2. **Cell chưa có báo cáo cũng có xác suất.** Cell mà AI node chưa nhận đủ truy vấn vẫn có thể chứa người. UAV cánh quay phải
   cân giữa thăm một cell điểm cao ngay bây giờ và chờ thêm báo cáo. Đây là chỗ (P1) và (P2) dính nhau: (P1) càng để chậm những cell
   nào thì (P2) càng phải chờ ở đó.
3. **Khi nào dừng hẳn** (mở). Nếu không cell nào vượt ngưỡng (người không đi qua thiết bị nào, hoặc bị phát hiện sót), pha 2 không
   có điểm dừng tự nhiên. Đề xuất: (P2) chỉ xét các nhiệm vụ có ít nhất một thiết bị thấy người; tỉ lệ nhiệm vụ không ai thấy người
   báo riêng như một độ đo của mạng.

**Lớp bài:** như bản đô thị. Bản tĩnh với kỳ vọng là bài độ trễ nhỏ nhất có trọng số (NP-khó, Sitters 2002); bản tĩnh với phân vị là
quota TSP; báo cáo tới dần thì thành bài trực tuyến có thời điểm phát hành.

## 5. Ba bài nối nhau

| Từ | Sang | Qua đại lượng |
|---|---|---|
| (P0) | (P1) | tập critical cell $K$, trọng số $w_k$, cửa sổ truy vấn, tải nền còn lại trên mỗi môi trường |
| (P0) | (P2) | số AI cell, từ đó số báo nhầm |
| (P1) | (P2) | thời điểm báo cáo $r_k$; cell nào báo muộn thì (P2) phải chờ ở đó |

Khác bản đô thị: $w_k$ xuất hiện ở cả ba bài, vì tiên nghiệm đều làm mỗi critical cell quan trọng đúng bằng phần vùng nó giữ bản
ghi.

## 6. Câu cần bạn quyết

**Tạm chốt (chatlog mục 415):** người dùng tạm đồng ý các đề xuất: cách B làm mục tiêu chính (makespan là độ đo phụ); kế hoạch pha 1
tính sẵn từ pha 0; (P0) và (P1) tách khi phát biểu, giải lặp khi làm thuật toán; năng lượng đưa vào (P1), còn (P0) để mở; (P2) chỉ
xét nhiệm vụ có ít nhất một thiết bị thấy người. Bản nháp phần đặt vấn đề theo các quyết định này: [STATEMENT-vi.md](STATEMENT-vi.md).

1. Phân vị lấy theo cách B (chung qua kênh và vị trí người; (P1) thành phân vị có trọng số) hay cách A (trường hợp xấu nhất; (P1) là
   makespan).
2. Kế hoạch pha 1 tính sẵn từ pha 0 cho cả vùng mạng (tiền đề 3): đồng ý không.
3. (P0) và (P1) tách khi phát biểu, giải lặp khi làm thuật toán: đồng ý không.
4. Năng lượng vào bài nào: chỉ (P1), cả (P0), hay chỉ báo ở phần đánh giá.
5. (P2) chỉ xét nhiệm vụ có ít nhất một thiết bị thấy người: đồng ý không.
