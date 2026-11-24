---
status: current
updated: 2026-11-24
---
# J1 · Ba bài toán cốt lõi (chatlog mục 399)

Phát biểu (P0), (P1), (P2) ở dạng toán gọn, bỏ chi tiết cài đặt, để mỗi bài nhận ra được là một lớp bài đã biết. Quyết định đầu
vào ở [L1-VARIABLES](L1-VARIABLES-vi.md) mục 6–8. Bài thay mục V của [dàn ý](OUTLINE-vi.md). Công thức viết theo ký hiệu của bản
thảo (`draft-v1/tex/sec-model.tex`) khi đã có.

## 0. Ký hiệu chung

| Ký hiệu | Nghĩa |
|---|---|
| $G=(\mathcal C,\mathcal E)$ | đồ thị cell lục giác; $\mathcal E$ là các cặp cell kề |
| $\mathcal M$ | tập môi trường: mỗi cell và mỗi cặp gateway; trong một khe $\tau_f$ mỗi môi trường chỉ có một máy phát |
| $V$, $V_p\subseteq V$ | mọi node; node cắm điện đủ mạnh để làm AI node |
| $Q$, $T_p$ | số gói của truy vấn, thời gian phát một gói |
| $c^\star$ | cell của người cần tìm, theo tiên nghiệm đều trên node |
| $\omega$ | phần ngẫu nhiên: kênh, MAC, lần thấy và điểm số của camera |
| $T^\star$ | thời gian từ cất cánh tới lúc V1 xác nhận đúng người |

Mục tiêu chung của cả bài:

$$\min\ \mathcal J(T^\star)=Q_{0.9}\bigl[T^\star\bigr],\qquad \text{báo kèm } \mathbb E[T^\star].$$

Còn một câu chờ chốt: phân vị lấy qua $(\omega,c^\star)$ (cách B, khớp tiên nghiệm đều), hay lấy $\max_{c^\star}Q_{0.9,\omega}$
(cách A, trường hợp xấu nhất). Ba bài dưới đây viết được cho cả hai cách. Lưu ý là phân vị của một tổng không bằng tổng các phân vị,
nên khi tách theo pha, mỗi bài dùng mục tiêu riêng thay cho $\mathcal J$.

## 1. (P0) Chọn AI cell: facility location có sức chứa với ràng buộc nghẽn

**Tham số.**
- $\lambda_u$: tốc độ byte luồng nền của node $u$ ($\rho\cdot f_{\mathrm{cam}}\cdot$ cỡ bản ghi, phương án lai lấy cỡ trung bình).
- $a_m(u,v)$: số khung trên môi trường $m$ cho mỗi byte đi theo đường cell ngắn nhất từ $u$ tới $v$ (mô hình tải 1,5 / 1,7 / 1
  khung).
- $h(u,v)$: số chặng cell từ $u$ tới $v$; $H=5$.
- $\beta_u$: dung lượng kho mà node $u$ chiếm ở AI node; $B_v$: bộ nhớ của $v$.
- $\bar u$: ngân sách thời gian kênh cho luồng nền (10 % hoặc 20 %).

**Biến.** $y_v\in\{0,1\}$ với $v\in V_p$ (node $v$ làm AI node); $x_{uv}\in\{0,1\}$ (node $u$ giao cho $v$). Tập critical cell là
$K(y)=\{\mathrm{cell}(v):y_v=1\}$.

$$
\begin{aligned}
\textbf{(P0)}\quad \min_{x,y}\ & \hat{\mathcal J}_0\bigl(K(y),x\bigr)\\
\text{s.t.}\ & \textstyle\sum_{v} x_{uv}=1 && \forall u\in V &&\text{(mỗi node một AI node)}\\
& x_{uv}\le y_v && \forall u,v\\
& h(u,v)\,x_{uv}\le H && \forall u,v &&\text{(giới hạn chặng)}\\
& \textstyle\sum_{u}\beta_u x_{uv}\le B_v\,y_v && \forall v &&\text{(bộ nhớ)}\\
& \textstyle\sum_{u,v}\lambda_u\,a_m(u,v)\,x_{uv}\,\tau_f\le\bar u && \forall m\in\mathcal M &&\text{(nghẽn trên môi trường)}
\end{aligned}
$$

**Mục tiêu.** Pha 0 giải trước sự cố và giải riêng, nên $\hat{\mathcal J}_0$ là ước lượng phân vị 0,9 của $T^\star$ theo tập
$K$. Ước lượng gồm hai phần:
- Phần pha 1 lấy từ surrogate River:
  $\hat T_1(K)=\max_k\bigl(\mathrm{leave}_k+\max_{h\in K_k}(a+b\,\mathrm{hops}_h+c\,\mathrm{lack}_h)+d\sum_{h\in K_k}\mathrm{lack}_h\bigr)$.
- Phần pha 2 tăng theo $|K|$, vì nhiều AI cell thì nhiều cell báo nhầm (K9 B5).

**Lớp bài.**
- Bỏ ràng buộc nghẽn và lấy mục tiêu $\sum_v y_v$ thì bài là facility location có sức chứa, một nguồn (SSCFLP). Bài này NP-khó vì
  chứa bài phủ tập.
- Ràng buộc chặng là bán kính phủ, giống bài p-center.
- Ràng buộc nghẽn làm tải phụ thuộc đường đi chung. Đây là phần khác với facility location thường: hai node xa nhau vẫn tranh nhau
  cùng một môi trường trên đường về.
- Mục tiêu dạng max theo cụm là mục tiêu cổ chai.

**Lời giải hiện có.** `paper/j1/analysis/cc_select.py`: tìm số AI cell ít nhất còn khả thi bằng nhân đôi rồi chia đôi, sau đó tìm
kiếm cục bộ. Bản cài đặt cố định $x$ theo AI cell gần nhất, còn bài cốt lõi để $x$ tự do. Mục tiêu đang là $\hat T_1$ trung bình,
chưa phải phân vị.

## 2. (P1) Pha 1 với K cố định: Dubins TSP với lân cận ghép với luồng nhiều hàng theo thời gian

**Biến.**
- Quỹ đạo $q:[0,T_f]\to\mathbb R^2$ với $q(0)=q(T_f)=\mathrm{BS}$, $\lVert\dot q\rVert\in[v_{\min},v_{\max}]$, độ cong
  $\le1/r_{\min}$, $q(t)\in F$ (độ cao 100 m, ngoài vùng cấm). Thứ tự cụm $\pi$ nằm sẵn trong $q$.
- Lịch phát $s$: gói $j$ phát lúc $t_j$, mỗi gói chiếm $T_p$; một gói được phát lại nhiều lần.
- Kế hoạch mặt đất $f^{j}_{a\to b,\tau}\in\{0,1\}$: cell $a$ gửi gói $j$ cho cell $b$ (kề $a$, hoặc chính $a$ khi gom trong cell)
  ở khe $\tau$, trên môi trường $m(a,b)$.

**Trạng thái.**
- Nhận từ UAV: $h^j_{c,0}=\mathbf 1[j\in R_c(\omega)]$, với $\Pr\{j\in R_c\}=P_c(q(t_j))$ theo phương trình `eq:pcell` của bản thảo.
- Giữ gói: $h^j_{b,\tau+1}=h^j_{b,\tau}\lor\bigvee_a f^j_{a\to b,\tau}\,\xi^j_{a\to b,\tau}(\omega)$, với $\xi$ là chuyển thành công.

$$
\begin{aligned}
\textbf{(P1)}\quad \min_{q,s,f}\ & Q_{0.9}\Bigl[\max_{k\in K} C_k\Bigr],\qquad C_k=\min\Bigl\{\tau:\textstyle\sum_{j\in D_k}h^j_{k,\tau}\ge Q_k\Bigr\}\\
\text{s.t.}\ & q \text{ khả thi Dubins, } q(t)\in F,\ T_f\le T_{\mathrm{end}} &&\text{(bay)}\\
& f^j_{a\to b,\tau}\le h^j_{a,\tau} && \forall j,a,b,\tau &&\text{(chỉ gửi gói đang giữ)}\\
& \textstyle\sum_{j}\sum_{(a,b):\,m(a,b)=m} f^j_{a\to b,\tau}\le 1 && \forall m,\tau &&\text{(một máy phát mỗi môi trường)}
\end{aligned}
$$

$D_k$ là cửa sổ truy vấn của critical cell $k$ (bản sao phát gần $k$ nhất), $Q_k$ là số gói cần (có mã thì $Q(1+\epsilon)$).

**Thông tin khi lập kế hoạch.** Tập nhận $R_c(\omega)$ chỉ biết sau lượt bay, nhưng kế hoạch lập trước khi cất cánh. Vì vậy (P1) là
bài hai giai đoạn:
- Giai đoạn một: chọn $(q,s,\bar f)$ trên bản đồ nhận dự báo $\hat R_c=\{j:P_c(q(t_j))\ge\theta\}$.
- Giai đoạn hai: sửa theo thực tế. Gồm gom và sửa trong cell, takeover và cơ chế vá (K15).

River là một chính sách giai đoạn một như vậy.

**Lớp bài.**
- Phần $q$ là Dubins TSP với lân cận. Định lý 1 của bản thảo cho thấy bài NP-khó, kể cả khi bỏ hẳn phần mặt đất.
- Với $q$ và $R$ cố định, phần $f$ là bài lập lịch phát đa điểm thời gian nhỏ nhất trên đồ thị, mỗi môi trường sức chứa một (cùng họ
  với minimum broadcast time và gossiping). Bài này NP-khó ngay cả khi chỉ có một nguồn.
- Bỏ điều kiện nguyên và bỏ chiều thời gian thì được LP tải lớn nhất:
  $\min L$ s.t. $\sum_{\text{luồng qua }m}\text{khung}\le L\ \forall m$, bảo toàn luồng từ Bank tới thành viên Ring.
  Từ đó $\max_k C_k\ge\tau_f L^\star_{\mathrm{LP}}$. Đây là chặn `river_lb.py --lp` đang tính.
- Chặn một radio (Mệnh đề 2) là trường hợp riêng: chỉ xét môi trường của critical cell.

**Lời giải hiện có.**
- Phần $q$: LM-Tour và CHORD.
- Phần $\bar f$: River gốc, cây dùng chung, lập kế hoạch cân tải.
- Giai đoạn hai: takeover.

## 3. (P2) Pha 2: độ trễ nhỏ nhất có trọng số trực tuyến, hoặc TSP có hạn mức xác suất

**Dữ liệu.**
- Cell nghi vấn $c\in A$, báo YES lúc $r_c$; $r_c$ do (P1) quyết định.
- Hậu nghiệm $p_c(t)$, cập nhật mỗi khi có báo cáo.
- Thời gian bay $d(i,j)$ của đội 2 (15 m/s); thời gian xác minh V1 $\sigma=78$ s; V1 coi là đúng khi thăm $c^\star$.

**Biến.** Lúc cất cánh $t_2$ và chính sách thăm $\mu$: ở mỗi lần xác minh xong hoặc có báo cáo mới, $\mu$ chọn cell kế tiếp từ
thông tin đang có. Nếu biết trước mọi báo cáo thì $\mu$ chỉ là một dãy $(c_1,c_2,\dots)$.

Thời gian xác nhận khi $c^\star=c_{i^\star}$:

$$T^\star=t_2+\sum_{i\le i^\star}\bigl(w_i+d(c_{i-1},c_i)+\sigma\bigr),\qquad c_0=\mathrm{BS},$$

với $w_i\ge0$ là thời gian chờ nếu tới $c_i$ trước $r_{c_i}$.

$$
\textbf{(P2)}\quad \min_{t_2,\ \mu}\ Q_{0.9}\bigl[T^\star\bigr]\quad\bigl(\text{hoặc }\mathbb E[T^\star]\bigr),\qquad t_2\ge\min_c r_c .
$$

**Lớp bài.**
- Bản tĩnh với mục tiêu kỳ vọng: biết hết báo cáo, $t_2$ cố định, tối thiểu $\sum_c p_c L_c(\pi)$ với $L_c$ là lúc xác minh xong
  $c$. Đây là bài độ trễ nhỏ nhất có trọng số (traveling repairman), NP-khó. Đây cũng là dạng thời gian trung bình của bài đường đi
  tìm kiếm tối ưu (Trummel và Weisinger 1986).
- Bản tĩnh với mục tiêu phân vị 0,9: tìm $\tau$ nhỏ nhất sao cho có đường từ trạm gốc, trong thời gian $\tau$, thăm đủ các cell có
  tổng xác suất $\ge0{,}9$. Đây là TSP có hạn mức (quota TSP, dạng đường đi) với hạn mức là khối xác suất. Bài đối ngẫu, tối đa xác
  suất trong thời gian $\tau$, là orienteering.
- Có thời điểm báo cáo $r_c$: thành bài có ngày phát hành (release dates). Báo cáo tới dần thì thành bài trực tuyến: giải lại khi có
  tin mới, hoặc phân tích tỉ số cạnh tranh.
- Khi $d\equiv0$, thăm theo $p_c$ giảm dần là tối ưu cho kỳ vọng (quy tắc Smith). Chính sách tham lam hiện tại ($p_c$ chia thời
  gian bay) là phiên bản có quãng bay của quy tắc này, nên khoảng cách tới tối ưu chỉ đến từ quãng bay.

**Lời giải hiện có.** Chính sách tham lam, cất cánh ở báo cáo đầu tiên (`uav-l2/tools/l1_rank.py`, `mission_policy.py`). Chưa có
nghiệm đúng để so; khi có tới khoảng 15 cell nghi vấn thì quy hoạch động trên tập con giải đúng được.

## 4. Ba bài nối nhau ra sao

| Từ | Sang | Qua đại lượng |
|---|---|---|
| (P0) | (P1) | tập critical cell $K$, cửa sổ $D_k$, tải nền làm giảm sức chứa môi trường còn lại cho River |
| (P0) | (P2) | số AI cell, từ đó số cell báo nhầm và cỡ $A$ |
| (P1) | (P2) | thời điểm báo cáo $r_c=C_c+$ thời gian đối sánh và LoRa; độ chính xác của hậu nghiệm |

Nếu chọn thứ tự cụm của (P1) cùng với (P2) (câu còn mở ở L1-VARIABLES mục 8), thì mục tiêu của (P1) thay bằng $\mathcal J$, và
(P1) phải tính tới việc đưa cụm có xác suất cao lên trước.

## 5. Kết quả độ khó cần viết

| Bài | Đã có | Cần viết |
|---|---|---|
| (P0) | không | NP-khó: quy từ phủ tập hoặc SSCFLP; nhận xét ràng buộc nghẽn |
| (P1) | Định lý 1 (NP-khó, quy từ Exact Cover); chặn phủ (Định lý 2); chặn một radio (Mệnh đề 2) | phát biểu chặn LP tải lớn nhất thành mệnh đề; độ khó của phần $f$ khi $q$ cố định |
| (P2) | không | NP-khó theo traveling repairman hoặc quota TSP; nhận xét quy tắc Smith khi không có quãng bay |
