# Phát biểu các bài toán tối ưu

Bản tiếng Việt của `PROBLEM-FORMULATION.md`, liệt kê tách bạch **các bài toán tối
ưu** có thể phát biểu từ hệ thống này. Mỗi bài toán nêu: phát biểu toán học, biến
quyết định, độ khó, và **thành phần nào trong mã nguồn đang giải nó**.

Các phát biểu được viết *sau* thực nghiệm, có chủ đích: hai đặc điểm mà số liệu
buộc phải đưa vào mô hình — **tính nội sinh của thông tin** (§1.3) và **ràng buộc
hẹn gặp (R)** (§4) — không nằm trong khuôn mẫu "informative path planning" thông
thường, và chính là chỗ bài toán này khác các bài toán lân cận.

---

## 1. Ký hiệu và mô hình

| ký hiệu | ý nghĩa |
|---|---|
| $\mathcal{A}\subset\mathbb{R}^2$ | vùng tìm kiếm |
| $\mathcal{N}=\{1..n\}$, $p_i$ | cảm biến mặt đất, vị trí đã biết |
| $v\in\mathcal{A}$ | vị trí nạn nhân, **chưa biết**, tiên nghiệm $\pi_0$ |
| $\mathcal{M}=\{1..m\}$ | đội UAV |
| $q_u:[0,T]\to\mathbb{R}^3$ | quỹ đạo UAV $u$; $\|\dot q_u\|\le V$; $q_u(0)=q_u(T)=b$ |
| $\mathcal{D}$ | tập dữ liệu tham chiếu (chia thành chunk) |
| $F_i(t)\subseteq\mathcal{D}$ | phần dữ liệu nút $i$ đang giữ tại thời điểm $t$ |
| $\mathcal{G}=(\mathcal{N},\mathcal{E})$ | đồ thị liên thông mặt đất, cạnh khi $\|p_i-p_j\|\le R_g$ |

**Năng lượng:** $E=\sum_u\int_0^T P(\|\dot q_u\|)dt$, $P$ là đường cong công suất
cánh quay (Zeng–Zhang).

**Kênh truyền:** xác suất thành công $\rho(q,p)$ suy từ mô hình A2G (xác suất LoS
theo góc ngẩng, suy hao tán lá ITU-R P.833, pha-đinh Nakagami, shadowing). Thực
đo: $R_g\approx 37$ m $\ll R_a\approx 60\text{–}80$ m — **bất đối xứng này là mấu
chốt** (§4).

### 1.3. Thông tin là **nội sinh** — điểm khác biệt cốt lõi

$$e_i(t)=C\big(F_i(t)\big)\cdot\kappa_i,\qquad C(F)=1-\prod_{d\in F}(1-w_d)$$

với $\kappa_i=g(\|p_i-v\|)+\varepsilon_i$ là đáp ứng bộ phát hiện tại nút $i$.

Nút **không thể tự chấm điểm** dữ liệu của mình khi chưa giữ đủ dữ liệu tham
chiếu. Mà $F_i(t)$ chỉ tăng khi có UAV bay đủ gần:

$$\Pr[d\in F_i(t+dt)\mid d\notin F_i(t)]=\rho(q_u(t),p_i)\cdot x_{u,d}(t)\,dt$$

Do đó $e_i(t)$ là **phiếm hàm của quỹ đạo và lịch phát**. Bộ điều khiển phải *tiêu
tốn thời gian bay để tạo ra chính thông tin mà nó sẽ thu hoạch*. Đây **không** là
informative path planning kinh điển (nơi trường thông tin có sẵn, bay chỉ để lấy
mẫu). Hệ quả: **thăm dò và khai thác không tách rời được** theo cách thông thường.

---

## 2. (P0) Bài toán tổng quát — điều khiển tối ưu ngẫu nhiên

$$\min_{\{q_u,x_u\},\ \tau,\ z}\ \mathbb{E}[T]$$

với ràng buộc:

$$
\begin{aligned}
&\text{(giao dữ liệu)} && F_{j(v)}(T_{\text{srv}})=\mathcal{D},\quad j(v)=\arg\min_i\|p_i-v\|\\
&\text{(báo cáo)} && \text{gói REPORT mang } z \text{ tới được trạm } b \text{ trước } T\\
&\text{(độ chính xác)} && \varrho\big(\|z-v\|\big)\le\epsilon\\
&\text{(năng lượng)} && E\le E_{\max}\\
&\text{(động học)} && \|\dot q_u\|\le V,\ q_u(0)=q_u(T)=b\\
&\text{(nhân quả)} && \tau \text{ là thời điểm dừng theo } \{\mathcal{I}(t)\},\ \ z\in\sigma(\mathcal{I}(\tau))
\end{aligned}
$$

Ba lựa chọn mô hình cần bảo vệ:

1. **$T$ là makespan *tới trạm gốc*, không phải thời gian phát hiện.** Nhiệm vụ
   cứu hộ chưa kết thúc khi một UAV *biết*; nó kết thúc khi trạm chỉ huy biết.
2. **$\varrho$ nên là độ đo rủi ro, không phải kỳ vọng** — xem §7.
3. **Ràng buộc nhân quả** biến đây thành bài toán *điều khiển*, không phải bài
   toán *lập lịch*: $\tau$ và $z$ phải đo được theo thông tin đã thực sự tới nơi.

**Độ khó:** POMDP với không gian trạng thái liên tục ⇒ không giải chính xác được.
Giá trị nằm ở các thu hẹp có nguyên tắc dưới đây.

---

## 3. (P1) Bài toán phủ + hành trình — *cái mà baseline đang giải*

Bỏ toàn bộ thành phần thông tin, yêu cầu phục vụ **mọi** nút:

$$\min_{\{q_u\}}\ T\qquad \text{s.t.}\quad F_i(T)=\mathcal{D}\ \ \forall i\in\mathcal{N}$$

- Đặt trạm ảo: **phủ đĩa tối thiểu** (geometric set cover) — NP-khó.
- Nối các trạm ảo: **TSP with neighborhoods** — NP-khó.
- Thời gian treo tại mỗi trạm: đủ để mọi nút trong đĩa khôi phục được file.

`tsp-mc` (Zeng–Xu–Zhang) và `nocoop` giải đúng bài toán này. **Chúng không bao
giờ sinh ra $z$**, nên ràng buộc độ chính xác là *bất khả thi theo cấu trúc* với
chúng — đó là điểm yếu duy nhất mà chúng không thể khắc phục bằng tham số.

---

## 4. (P2) Bài toán hẹn gặp (rendezvous) — **ràng buộc đang bị vi phạm**

Để một lệnh triệu tập phát tại $\tau$ từ nút $\ell$ **được thi hành**, điểm đích
phải tới được một UAV. Với hạn ngạch $B$ gói, chu kỳ $\Delta$:

$$\textbf{(R)}\qquad \exists\,u\in\mathcal{M},\ \exists\,t\in[\tau,\ \tau+B\Delta]:\quad \|q_u(t)-p_\ell\|\le R_a$$

**Đây là ràng buộc hẹn gặp theo cả không gian lẫn thời gian, và nó chính là ràng
buộc chặt.** Tại 40×40 (780×780 m) sơ đồ hợp tác đã tính đúng điểm đích — sai
9 m, tại $\tau=66$ s — nhưng (R) bị vi phạm: UAV gần nhất chỉ bay qua trong bán
kính $R_a$ vào khoảng $250$ s $\gg \tau+B\Delta$. Kết quả: **0/5** lần phục vụ
được nạn nhân dù ước lượng hoàn hảo.

Hai cách thoả (R):

- **Theo cấu trúc (`closed-loop`):** chỉ phát khi có UAV trong tầm. Nút "vọng
  lại" vì vừa nhận được cue, nên $\rho>0$ đúng lúc phát. Giá phải trả: tập thông
  tin $\mathcal{I}$ bị thu hẹp còn *những gì một UAV nghe được*, nên đuôi sai số
  nặng.
- **Theo điều kiện (cách đã áp dụng):** giữ nguyên mặt phẳng thông tin đa chặng,
  nhưng cho **thời điểm phát** phụ thuộc vào việc quan sát thấy UAV: trưởng cụm
  phát lại lệnh mỗi khi nhận được một gói CUE — vì gói đó là *bằng chứng*
  $\rho(q_u(t),p_\ell)>0$ ngay lúc này. Không thu hẹp $\mathcal{I}$.
  Kết quả: **0/5 → 5/5**.

Về mặt lý thuyết, đây là phép đổi lịch phát từ **vòng hở** $t\in\{\tau+k\Delta\}$
sang **họ thời điểm dừng hướng sự kiện** $t\in\{s:\text{nhận CUE tại }s\}$, đo
được theo quan sát của chính nút đó.

**Bài toán mở đáng giá:** đặc trưng hoá miền khả thi của (R). Với $m$ UAV bay
hành trình phủ vùng diện tích $|\mathcal{A}|$, tính
$\Pr[\text{(R) thoả}]$ theo $|\mathcal{A}|, m, V, R_a, B\Delta$ — nó **dự đoán**
quy mô mà sơ đồ hợp tác sụp đổ, điều hiện chỉ biết bằng thực nghiệm.

---

## 5. (P3) Bài toán dừng tối ưu — *khi nào thì triệu tập*

Cho quỹ đạo cố định và quá trình bằng chứng $\{e_i(t)\}$:

$$\min_{\tau}\ \mathbb{E}\Big[\alpha\,\tau+\varrho\big(\|z_\tau-v\|\big)\Big]$$

Chờ lâu hơn ⇒ $\mathcal{I}$ giàu hơn ⇒ ước lượng tốt hơn; nhưng chậm giao hàng,
**và** do (R), chờ quá lâu có thể khiến việc thi hành trở nên *bất khả thi*. Miền
khả thi của $\tau$ do đó phụ thuộc quỹ đạo:

$$\tau\in\Big[\underline\tau,\ \sup\{t:\ \text{(R) còn thoả được}\}\Big]$$

**Bằng chứng thực đo:** cửa sổ cố định 45 s là tối ưu ở 16×16 nhưng cho **0** lần
định vị ở 8×8 — vì cận trên ở trên tỉ lệ với kích thước vùng, còn hằng số đồng hồ
thì không. Luật thích nghi hiện dùng (phát khi bằng chứng của trưởng cụm ngừng
tăng) là *xấp xỉ dựa trên dữ liệu* của luật dừng tối ưu thực sự.

---

## 6. (P4) Bài toán ước lượng vị trí — *và cận Cramér–Rao*

Cho tập nút báo cáo $\mathcal{R}$ với quan sát $\kappa_i$ và vị trí tự báo
$\tilde p_i=p_i+\eta_i$:

$$\hat v=\arg\max_{v}\ \sum_{i\in\mathcal{R}}\log f\big(\kappa_i\mid \|\tilde p_i-v\|\big)$$

Hai bộ ước lượng hiện có đều thô:

- `--aimArgmax` (mặc định): $z=\tilde p_{i^\star}$, $i^\star=\arg\max_i e_i$
- `--aimArgmax=0`: trọng tâm trọng số $e_i^2$

Chúng **hoà nhau** trong thực đo — dấu hiệu điển hình của việc **cả hai đều cách
xa cận**. Ma trận thông tin Fisher cho $v$ có dạng đóng; tính **CRLB** là cách
trung thực duy nhất để hoặc biện minh hoặc loại bỏ đóng góp về bộ ước lượng.

---

## 7. (P5) Chọn độ đo rủi ro — *quyết định đóng góp có tồn tại hay không*

Số liệu: hợp tác cải thiện **p90** sai số $-29\%$ nhưng trung vị chỉ
$\delta=-0.159$ (hiệu ứng nhỏ).

$$\varrho=\mathbb{E}[\cdot]\ \Rightarrow\ \text{hợp tác gần như vô giá trị}$$
$$\varrho=\mathrm{CVaR}_{0.9}[\cdot]\ \Rightarrow\ \text{hợp tác có mục đích rõ ràng}$$

**Bài toán:** xác định ngưỡng $\beta^\*$ sao cho với $\varrho=\mathrm{CVaR}_\beta$
và $\beta>\beta^\*$, sơ đồ hợp tác trội hơn `closed-loop`. Đây là đại lượng tính
được, và nó **thuộc về phần phát biểu bài toán, không phải phần thảo luận** — vì
lựa chọn độ đo rủi ro quyết định luôn việc đóng góp có tồn tại hay không.

---

## 8. (P6) Đánh đổi độ tin cậy – chi phí (tham số `deliverDwell`)

$$\min_{W}\ \Big\{\,T(W)\ :\ \Pr[\text{phục vụ được nạn nhân}]\ \ge\ 1-\delta\,\Big\}$$

với $W$ là thời lượng phát tại điểm giao. Thực đo:

| | 8×8 | 16×16 |
|---|---:|---:|
| $W=20$ s | 87.5 % phục vụ | 90.0 % |
| $W=40$ s | 93.3 % | **96.7 %** |
| tỉ số thời gian so với `tsp-mc×4` | 1.07× → **0.86×** | 1.63× → 1.48× |

**Nghiệm tối ưu phụ thuộc mật độ**: ở 256 nút, $W=40$ mua được độ tin cậy gần
ngang baseline mà vẫn nhanh hơn 1.48×; ở 64 nút, cùng giá trị đó **đảo ngược**
so sánh (ta chậm hơn baseline). Nên phát biểu như một **đường cong điểm vận hành**
(Pareto), không phải một con số.

---

## 9. (P7) Phủ dưới tính khả dụng không dừng — *bài toán con chưa giải*

Quan sát nhưng chưa xử lý được: chia nhiệm vụ phủ cho **cả 4** UAV làm 40×40
nhanh hơn hẳn (396 → 224 s) nhưng phá huỷ 16×16 (phục vụ nạn nhân 90 % → 42.5 %).

Nguyên nhân: một UAV vừa mang vai trò **phủ**, vừa mang vai trò **giao hàng theo
yêu cầu**, nên **tính khả dụng của nó không dừng** — nó có thể bị điều đi bất kỳ
lúc nào, để lại dải phủ dở dang.

$$\min_{\{S_u\}}\ T_{\text{phủ}}\qquad\text{s.t.}\quad \Pr\Big[\bigcup_u \text{phủ}(S_u)=\mathcal{N}\Big]\ge 1-\delta$$

trong đó $S_u$ là dải được giao cho UAV $u$, và xác suất lấy theo **biến cố UAV
$u$ bị điều đi giữa chừng**. Đây là bài toán phủ ngẫu nhiên với tài nguyên có thể
bị rút — sạch sẽ, có ý nghĩa thực tế, và chưa được giải trong công trình này.

---

## 10. (P8) Bài toán đa mục tiêu — mặt Pareto

Bốn tiêu chí xung đột nhau: makespan $T$, năng lượng $E$, số gói tin $\Pi$, sai
số định vị $\varrho(\|z-v\|)$, cùng ràng buộc độ tin cậy.

$$\min_{\text{sơ đồ}}\ \big(T,\ E,\ \Pi,\ \varrho\big)\quad\text{theo nghĩa Pareto}$$

Thực đo tại 16×16, $N=120$: `closed-loop` **trội** `proposed` theo $T$, $E$, $\Pi$
(0/120 lần thắng về số gói); `proposed` trội theo $\varrho$ ở đuôi phân phối. Tức
là **cả hai đều nằm trên mặt Pareto** — không cái nào bị loại. Đây là cách phát
biểu trung thực nhất cho phần so sánh, thay vì cố ép một sơ đồ "thắng".

---

## 11. Tóm tắt: ai đang giải bài toán nào

| bài toán | thành phần trong mã | trạng thái |
|---|---|---|
| (P1) phủ + hành trình | `tsp-mc`, `nocoop`, `BuildGmc`, `BuildVbsTour` | đã giải (heuristic) |
| (P2) hẹn gặp (R) | phát lại lệnh khi nhận CUE | **đã sửa**, chưa đặc trưng hoá lý thuyết |
| (P3) dừng tối ưu | cửa sổ thích nghi | xấp xỉ heuristic |
| (P4) ước lượng + CRLB | `--aimArgmax` | **chưa có CRLB** |
| (P5) độ đo rủi ro | — | **chưa phát biểu chính thức** |
| (P6) đánh đổi tin cậy–chi phí | `--deliverDwell` | đã đo, nên trình bày dạng đường cong |
| (P7) phủ dưới khả dụng không dừng | `--dataPatrol` | **chưa giải** |
| (P8) Pareto đa mục tiêu | toàn bộ so sánh | nên dùng làm khung trình bày |
