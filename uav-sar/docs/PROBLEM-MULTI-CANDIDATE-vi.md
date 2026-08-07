# Nhiều điểm yêu cầu: các bài toán tối ưu khi bộ phát hiện phán đoán sai

Tiếp nối `PROBLEM-FORMULATION-vi.md` (P0–P8). Tài liệu này xét yếu tố **tỉ lệ
phán đoán sai của nút**: khi nút nhận dữ liệu tham chiếu và tự chấm điểm, nó có
thể báo động nhầm, nên nói chung tồn tại **$K>1$ điểm yêu cầu** chứ không phải
một điểm duy nhất. Từ đó nảy sinh một họ bài toán mới: **xếp thứ tự ưu tiên,
đường bay ngắn nhất, phân vùng hợp tác** giữa các UAV.

Trước khi phát biểu, phải nói rõ một điều đã **đo được**, vì nó quyết định toàn
bộ phần còn lại:

> **Trực giác của bạn đúng về mặt vật lý, nhưng mô hình hiện tại không sinh ra
> được chế độ đó.** Ở điểm vận hành đang dùng ($\sigma=0.10$), $K=1$ trong
> **94.2 %** số run ở 16×16 và **98.3 %** ở 40×40; **0 %** số run có mồi nhử ở xa.
> Lý do là cấu trúc, không phải ngẫu nhiên (§2). Muốn nghiên cứu các bài toán ở
> §4–§9 thì **phải sửa mô hình trường manh mối trước** (§3) — nếu không, mọi
> thuật toán định tuyến đa ứng viên sẽ được đo trên các thể hiện mà $K=1$, và
> chúng sẽ "hoà nhau" một cách vô nghĩa.

---

## 1. Đo trước, phát biểu sau

Công cụ: `tools/candidate_stats.cc` — dùng chính `BuildClueField` và
`BuildCellGrid` của dự án, sinh vị trí nạn nhân bằng đúng chuỗi RNG của
`SarScenario::Build`, nên số liệu là số liệu mà bộ mô phỏng nhìn thấy.

```
g++ -O2 -std=c++17 -o candidate_stats tools/candidate_stats.cc \
    models/common/clue-field.cc models/common/cell-grid.cc
./candidate_stats <grid> <senseSigma> <seeds> [maxNoiseQuality]
```

Định nghĩa **ứng viên**: một thành phần liên thông (single-linkage ở tầm liên kết
mặt đất $R_g\approx37$ m) của tập nút vượt ngưỡng $\tau_a=$ `kAlertThreshold`
$=0.75$. Đây đúng là mức mà một lãnh đạo ô có thể được bầu và phát SUMMON.
**Mồi nhử** = ứng viên cách nạn nhân thật $>60$ m.

$N=120$ hạt giống, 16×16, `victimOnNode=0`:

| $\sigma$ | nút ALERT (tb) | $K$ (tb) | $K\ge2$ | $K\ge3$ | $K=0$ | run có mồi nhử |
|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 1.52 | 1.00 | 0.0 % | 0.0 % | 0.0 % | 0.0 % |
| 0.05 | 1.56 | 0.96 | 0.0 % | 0.0 % | 4.2 % | 0.0 % |
| **0.10** | **2.07** | **1.02** | **5.8 %** | **0.0 %** | **3.3 %** | **0.0 %** |
| 0.15 | 2.67 | 1.12 | 15.8 % | 0.0 % | 3.3 % | 0.0 % |
| 0.20 | 3.35 | 1.37 | 32.5 % | 5.8 % | 1.7 % | 6.8 % |

40×40 ($n=1600$ nút, gấp 6.25 lần): $\sigma=0.10 \Rightarrow K\ge2$ chỉ **1.7 %**;
$\sigma=0.20 \Rightarrow K\ge2$ 32.5 %, mồi nhử 15.8 %, khoảng cách mồi nhử gần
nhất **median 246 m**.

Hai điều đáng chú ý:

1. Ở $\sigma=0.10$, $K\ge2$ **giảm** khi lưới lớn hơn (5.8 % → 1.7 %). Điều đó
   phản trực giác nếu ta nghĩ "nhiều nút hơn ⇒ nhiều báo động nhầm hơn"; nó là
   dấu hiệu cho thấy các ứng viên phụ hiện nay **không phải** do nhiễu nền sinh
   ra, mà chỉ là **cụm quanh nạn nhân bị tách đôi** bởi ngưỡng liên thông.
2. Nút vượt ngưỡng COOP ($0.30$) thì tăng mạnh và đúng theo $n$: 18.9 (16×16) →
   135.5 (40×40) ở $\sigma=0.20$. Tức là **dương tính giả có tồn tại**, nhưng
   chúng bị chặn ở tầng dưới, không bao giờ leo tới tầng ALERT.

## 2. Vì sao mô hình hiện tại chặn chế độ đa ứng viên

`ClueFieldConfig` (`models/common/clue-field.h`):

```
maxNoiseQuality  = 0.18      // trần chất lượng của một dương tính giả nền
bgFalsePositiveRate = 0.03
kAlertThreshold  = 0.75      // sar-params.h
```

Một nút nằm ngoài `weakRadius` có $q_{\text{true}}\le 0.18$, và **97 %** trong số
đó có $q_{\text{true}}=0$ (chỉ 3 % được rút nhánh dương-tính-giả nền). Để nó phát
SUMMON, nhiễu bộ phát hiện phải một mình đẩy nó qua $0.75$:

$$\Pr[\text{mồi nhử}\mid q_{\text{true}}=0]=Q\!\left(\frac{0.75}{\sigma}\right)
=\begin{cases}Q(7.5)\approx 3\cdot10^{-14}&\sigma=0.10\\ Q(3.75)\approx 8.8\cdot10^{-5}&\sigma=0.20\end{cases}$$
$$\Pr[\text{mồi nhử}\mid q_{\text{true}}\le0.18]\le Q\!\left(\frac{0.57}{\sigma}\right)
=\begin{cases}Q(5.7)\approx 6\cdot10^{-9}&\sigma=0.10\\ Q(2.85)\approx 2.2\cdot10^{-3}&\sigma=0.20\end{cases}$$

Với $n=256$ nút: $\sigma=0.10$ cho kỳ vọng $\sim5\cdot10^{-8}$ mồi nhử mỗi run —
**không bao giờ xảy ra**; $\sigma=0.20$ cho $\approx0.04$/run, cùng bậc độ lớn với
6.8 % đo được. Vậy:

> **Trần nhiễu nền $0.18$ nằm dưới ngưỡng báo động $0.75$ quá xa, nên theo cấu
> trúc mô hình, một dương tính giả không thể trở thành một điểm yêu cầu.**

Còn một cơ chế thứ hai, ở tầng giao thức, cũng triệt tiêu đa ứng viên:
`--electSuppress` làm **đúng một** SUMMON được phát mỗi run (đã đo: 0/20 run có
hai vùng). Kể cả khi trường manh mối sinh ra $K=3$, tầng bầu cử vẫn **vứt bỏ
$K-1$ ứng viên trước khi có bất kỳ quyết định định tuyến nào**. Trong thế giới
một điểm, đó là tối ưu; trong thế giới nhiều điểm, đó là một **lỗi thiết kế**
(§9).

## 3. Sửa mô hình: nguồn gây nhiễu có cấu trúc không gian

Nâng `maxNoiseQuality` là cách rẻ nhất để bật chế độ đa ứng viên, và nó có tác
dụng đúng như dự đoán ($N=120$, 16×16, $\sigma=0.10$):

| `maxNoiseQuality` | $K$ (tb) | $K\ge2$ | $K\ge3$ | run có mồi nhử | k/c mồi nhử gần nhất |
|---:|---:|---:|---:|---:|---:|
| 0.18 (hiện tại) | 1.02 | 5.8 % | 0.0 % | 0.0 % | — |
| 0.40 | 1.02 | 5.8 % | 0.0 % | 0.0 % | — |
| 0.60 | 1.03 | 6.7 % | 0.0 % | 0.9 % | 159 m |
| **0.80** | **1.52** | **38.3 %** | **14.2 %** | **38.7 %** | **195 m** |

40×40, `maxNoiseQuality=0.60`: $K\ge2$ 21.7 %, mồi nhử 20.5 %, khoảng cách median
**456 m**. Ở tốc độ 20 m/s, đi nhầm một mồi nhử như thế tốn $\approx 46$ s bay
khứ hồi **cộng** thời gian rải dữ liệu (`kMinDeliverDwellS` 20–40 s). So với thời
gian nhiệm vụ 16×16 hiện tại (~104 s), **một lần đi nhầm là một sai lầm cỡ 60 %
tổng thời gian nhiệm vụ**. Đây chính là lý do bài toán định tuyến đa ứng viên
đáng nghiên cứu.

Tuy nhiên **nâng trần nhiễu là mô hình sai về mặt vật lý**: nó tạo ra các mồi nhử
là **nút đơn lẻ, độc lập nhau**. Nguồn gây nhiễu thật (một người khác, một con
thú, đống lửa, chiếc áo bỏ lại) là **nguồn có vị trí**, và các nút quanh nó cùng
sáng lên — nghĩa là mồi nhử phải là **một cụm giống hệt cụm nạn nhân**, chỉ khác
ở biên độ đỉnh. Đề xuất cụ thể:

```cpp
struct ClutterSource { double x, y, peak; };   // peak ~ U[0.55, 0.95] * maxQuality
// M ~ Poisson(lambda * |A|), lambda cỡ 1 nguồn / (300 m)^2
// q_true(i) = max( g(||p_i - v||), max_m  peak_m * g(||p_i - c_m||) )
```

Dùng **cùng nhân không gian** $g(\cdot)$ cho nạn nhân và cho nhiễu là điểm mấu
chốt: khi đó **hình dạng cụm không phân biệt được**, và hậu nghiệm $\pi_k$ không
thể suy ra từ một lần quan sát — nó phải đến từ tiên nghiệm, từ ngữ cảnh, hoặc từ
một **quan sát thứ hai**, mà việc đi lấy quan sát thứ hai lại chính là một biến
quyết định (§7). Đó là chỗ bài toán trở nên thú vị thay vì chỉ là "chọn đỉnh cao
nhất".

---

## 4. Ký hiệu bổ sung

Sau giai đoạn gieo cue, tầng mặt đất kết tinh thành tập ứng viên

$$\mathcal{K}=\{1,\dots,K\},\qquad c_k\in\mathcal{A}\ \text{(vị trí)},\quad
\hat e_k\ \text{(bằng chứng gộp)},\quad \pi_k=\Pr[v\in B(c_k,r)\mid \mathcal{F}]$$

với $\sum_k \pi_k \le 1$ (phần thiếu là xác suất nạn nhân **không** nằm trong bất
kỳ ứng viên nào — chính là $K=0$ đo được 3.3 %). Ký hiệu thêm:

| ký hiệu | ý nghĩa |
|---|---|
| $s_k$ | thời gian phục vụ tại $c_k$ (dwell rải dữ liệu, $\approx$ `kMinDeliverDwellS`) |
| $d(a,b)$ | thời gian bay giữa hai điểm $=\|a-b\|/V$ |
| $t_k$ | thời điểm ứng viên $k$ **hoàn tất phục vụ** |
| $\mathcal{M}_D$ | đội UAV DATA, $|\mathcal{M}_D|=m$ |
| $a:\mathcal{K}\to\mathcal{M}_D$ | phân công |
| $\sigma_u$ | thứ tự thăm của UAV $u$ |

**Hàm mục tiêu chủ đạo — kỳ vọng thời gian cứu nạn:**

$$\boxed{\ \min_{a,\ \sigma}\ \mathbb{E}[T_{\text{rescue}}]=\sum_{k\in\mathcal{K}}\pi_k\, t_k\ +\ \Big(1-\sum_k\pi_k\Big)\,T_{\max}\ }$$

Đây **không** phải TSP (không phải min tổng đường bay), cũng **không** phải
orienteering (phần thưởng không cộng dồn — chỉ có **một** ứng viên là thật). Nó là
**bài toán độ trễ nhỏ nhất có trọng số xác suất**, họ hàng của *Minimum Latency
Problem* / *Traveling Repairman*.

---

## 5. (P9) Chọn điểm vận hành ROC — bài toán **thượng nguồn** quyết định mọi thứ

Ngưỡng $\tau_a$ vừa quyết định xác suất bỏ sót nạn nhân, vừa quyết định **kích
thước** của mọi bài toán định tuyến ở hạ nguồn:

$$\min_{\tau_a}\ \mathbb{E}[T_{\text{rescue}}]
\quad\text{với}\quad
K(\tau_a)\ \text{ứng viên},\quad
\Pr[v\notin\textstyle\bigcup_k B(c_k,r)]\le\epsilon$$

Ràng buộc là **phủ xác suất**: hạ $\tau_a$ thì gần như chắc chắn nạn nhân nằm
trong tập ứng viên, nhưng $K$ tăng và $\mathbb{E}[T]$ tăng theo (mỗi ứng viên thừa
tốn $d+s$). Nâng $\tau_a$ thì $K\to1$ nhưng $\epsilon$ tăng — và **hỏng $\epsilon$
là hỏng vĩnh viễn**, còn $K$ lớn chỉ là chậm.

Số liệu §1 chính là hàm $K(\tau_a,\sigma)$ đo thực nghiệm. Đáng chú ý: cột $K=0$
(3.3 % ở $\sigma=0.10$) **là** $\epsilon$, và nó **khác không ngay ở điểm vận hành
hiện tại**. Nghĩa là $\tau_a=0.75$ đang được đặt ở phía "quá cao" của đường cong
mà chưa ai đo. **Đây là thí nghiệm rẻ nhất và có giá trị nhất trong toàn bộ tài
liệu này**: quét $\tau_a\in[0.4,0.9]$, vẽ $(\epsilon,\ \mathbb{E}[T])$.

*Hiện trạng mã nguồn:* `kAlertThreshold` là hằng số biên dịch, chưa có cờ dòng
lệnh. Chưa ai giải bài toán này.

## 6. (P10) Xếp thứ tự ưu tiên một UAV — độ trễ kỳ vọng nhỏ nhất

Một UAV, $K$ ứng viên, xuất phát từ $q_0$. Thứ tự $\sigma=(k_1,\dots,k_K)$ cho

$$t_{k_j}=\sum_{i=1}^{j}\big(d(c_{k_{i-1}},c_{k_i})+s_{k_i}\big),\qquad
\mathbb{E}[T]=\sum_{j}\pi_{k_j}t_{k_j}$$

**Hai trường hợp biên có lời giải chính xác:**

1. **Bỏ qua di chuyển** ($d\equiv0$): bài toán trở thành *weighted completion
   time* $1\|\sum w_jC_j$, và **quy tắc Smith** tối ưu — sắp xếp giảm dần theo
   chỉ số

   $$\rho_k=\frac{\pi_k}{s_k}$$

   Đây là dạng chỉ số kiểu Gittins: **không** sắp theo $\pi_k$, mà theo *xác suất
   trên một đơn vị thời gian tiêu tốn*. Một ứng viên hơi kém tin cậy nhưng phục vụ
   nhanh có thể đáng đi trước.

2. **Chi phí di chuyển đồng nhất** (mọi ứng viên cách đều nhau, $d\equiv\bar d$):
   vẫn là Smith với $s_k\to s_k+\bar d$.

**Trường hợp tổng quát là NP-khó** (chứa Minimum Latency Problem khi $\pi_k$ đều
nhau). Heuristic có bảo đảm và rẻ:

$$k^\star=\arg\max_k\ \frac{\pi_k}{d(q_{\text{cur}},c_k)+s_k}\qquad\text{(tham lam theo chỉ số)}$$

MLP có xấp xỉ hằng số $3.59$ (Chaudhuri–Godfrey–Rao–Talwar); biến thể có trọng số
xác suất giữ được bảo đảm tương tự qua kỹ thuật $k$-MST. Với $K\le4$ (đúng biên đo
được ở §3), **vét cạn $K!\le24$ hoán vị là chuyện vặt** — nghĩa là ở quy mô thực
tế của bài này ta có thể lấy **nghiệm tối ưu chính xác** và dùng nó làm mốc để
đánh giá heuristic phân tán. Đó là một lợi thế trình bày hiếm có: *bài toán NP-khó
nhưng thể hiện đủ nhỏ để biết đáp án đúng*.

*Hiện trạng mã nguồn:* UAV DATA bay tới **một** điểm trong SUMMON. Không có khái
niệm hàng đợi ứng viên. Cơ chế `--retargetAfter=60 s` (§8) là dạng thoái hoá của
bài toán này với $K=2$ và thứ tự cố định.

## 7. (P11) Xác minh hay phục vụ — bài toán thu thập thông tin xen kẽ hành động

Đội FAST bay nhanh, **không** rải dữ liệu, chỉ gieo cue và nghe ECHO/RPT. Vậy có
hai hành động khác nhau tại một ứng viên:

| hành động | ai làm | chi phí | tác dụng |
|---|---|---|---|
| **xác minh** | FAST | $d$ + vài giây | làm sắc $\pi_k$ (quan sát thứ hai) |
| **phục vụ** | DATA | $d + s_k$ ($s\ge20$ s) | kết thúc nếu $k$ là thật |

Bài toán: xen kẽ hai loại hành động sao cho $\mathbb{E}[T_{\text{rescue}}]$ nhỏ
nhất. Đây là **POMDP với hành động thu thập thông tin**, trạng thái tin là vector
hậu nghiệm $\pi\in\Delta^{K}$. Xác minh không bao giờ trực tiếp cứu ai, nên nó chỉ
đáng làm khi **giá trị thông tin vượt chi phí**:

$$\text{VoI}(k)=\mathbb{E}\big[\,\mathbb{E}[T\mid \pi]-\mathbb{E}[T\mid \pi']\,\big]\ >\ d(q_{\text{FAST}},c_k)+\delta$$

**Điểm cần nói thẳng:** nếu mồi nhử dùng **cùng nhân không gian** như nạn nhân
(§3), thì quan sát thứ hai bằng **cùng một cảm biến** hầu như không làm sắc được
$\pi$ (chỉ giảm nhiễu $\sigma$ theo $1/\sqrt2$). Xác minh chỉ có giá trị nếu UAV
mang **phương thức cảm biến khác** (ảnh nhiệt, gọi–đáp) — đó là một giả thiết mô
hình mới, phải khai báo, chứ không được lặng lẽ cho FAST một siêu năng lực. Nếu
không chấp nhận giả thiết đó, **P11 sụp về P10** và ta nên nói vậy thay vì phát
biểu một bài toán không có nội dung.

## 8. (P12) Định tuyến **trực tuyến** — ứng viên xuất hiện dần

Ứng viên không có sẵn tại $t=0$: bằng chứng $e_i(t)$ chỉ lớn lên khi UAV đã rải
dữ liệu tới đó (tính nội sinh của thông tin, §1.3 của tài liệu gốc). Do đó $K$ và
$\pi$ **thay đổi trong lúc UAV đang bay**. Bài toán:

$$\min_{\text{chính sách trực tuyến}}\ \frac{\mathbb{E}[T^{\text{online}}]}{\mathbb{E}[T^{\text{opt-offline}}]}\quad\text{(tỉ số cạnh tranh)}$$

Quyết định cốt lõi: đang trên đường tới $c_1$ thì nghe $c_2$ với $\pi_2>\pi_1$ —
**bẻ lái hay không?** Bẻ lái tối ưu theo tham lam tức thời nhưng có thể dao động
(thrashing) và **không bao giờ hoàn tất phục vụ ai cả**.

Đây **không** phải giả thuyết: dự án đã trả giá cho đúng chuyện này. Bản sửa
`m_regionId` (trước đó mọi lãnh đạo đều đặt `regionId=1`) cho thấy **37 lần bẻ lái
do lệnh triệu tập của vùng khác** so với 9 lần bẻ lái thật. Cơ chế `m_boundRegion`
hiện nay **cấm hoàn toàn** việc bẻ lái sau khi đã nhận nhiệm vụ — tức là dự án
đang chạy chính sách "không bao giờ preempt", là một đầu mút của không gian chính
sách, **chưa từng được so với đầu mút kia**. Chính sách đúng nhiều khả năng nằm ở
giữa: preempt khi và chỉ khi

$$\pi_2\big(t_2^{\text{nếu bẻ lái}}\big)^{-1} > \pi_1\big(t_1^{\text{nếu giữ}}\big)^{-1}\ \text{với biên trễ (hysteresis)}$$

*Hiện trạng mã nguồn:* `kRetargetAfterS=60 s` + `kMaxRetargets=2` là một chính
sách preempt **theo thời gian chờ**, không theo giá trị. Đã đo: trung tính. Điều
đó hợp lý — ở chế độ $K=1$ không có gì để preempt sang.

## 9. (P13) Phân vùng hợp tác — nhiều UAV, phần thưởng **không cộng dồn**

$m$ UAV DATA, $K$ ứng viên. Phân công $a$ và thứ tự $\{\sigma_u\}$:

$$\min_{a,\{\sigma_u\}}\ \sum_{k}\pi_k\,t_k(a,\sigma_{a(k)})$$

**Cấu trúc bài toán:** cho trước phân công $a$, mỗi UAV giải **độc lập** một bài
toán P10 trên tập $a^{-1}(u)$ — vì $t_k$ chỉ phụ thuộc vào lộ trình của UAV được
giao. Toàn bộ độ khó nằm ở phân công. Do đó đây là **set-partitioning** với chi
phí cột là nghiệm P10 của tập con — giải được bằng sinh cột (column generation),
hoặc bằng **đấu giá phân tán**: UAV $u$ đặt giá cho ứng viên $k$ bằng chi phí biên

$$b_u(k)=\mathbb{E}[T\mid a\cup\{k\to u\}]-\mathbb{E}[T\mid a]$$

Cơ chế CLAIM/yield sẵn có trong `sar-data-uav-app` **đã là** một đấu giá phân tán
— chỉ khác là hiện nay nó đấu giá **một** nhiệm vụ theo tiêu chí "ai nhanh tay
nhất" chứ không theo chi phí biên. Nâng nó thành đấu giá nhiều nhiệm vụ là thay
đổi nhỏ về giao thức, lớn về ý nghĩa.

**Điểm khác biệt so với Team Orienteering kinh điển:** phần thưởng ở đó cộng dồn
($\sum$ điểm thu được), ở đây **chỉ một ứng viên là thật**. Hệ quả toán học: giao
việc **trùng** (hai UAV cùng thăm một $c_k$) không bao giờ có lợi, và — quan trọng
hơn — **giá trị biên của UAV thứ $m+1$ giảm rất nhanh**, vì nó chỉ rút ngắn được
đuôi của phân phối. Đây là một dự đoán kiểm chứng được: **quét $m$, kỳ vọng thấy
lợi ích bão hoà ở $m\approx K$**, và $\mathbb{E}[T]$ giảm gần như $1/m$ chỉ khi
$\pi$ gần đều.

## 10. (P14) Rủi ro: giờ vàng, không phải trung bình

Mọi phát biểu trên tối thiểu hoá **kỳ vọng**. SAR quan tâm hạn chót $T_d$:

$$\max_{a,\sigma}\ \Pr[T_{\text{rescue}}\le T_d]
\qquad\text{hoặc}\qquad \min\ \mathrm{CVaR}_\alpha(T_{\text{rescue}})$$

Hai mục tiêu cho **thứ tự khác nhau**. Ví dụ hai ứng viên: $\pi_1=0.6$ ở xa
($t_1=90$ s), $\pi_2=0.4$ ở gần ($t_2=30$ s), $T_d=60$ s.
- Tối thiểu $\mathbb{E}[T]$: đi $c_2$ trước ($\mathbb{E}=0.4\cdot30+0.6\cdot130=90$ s
  so với $0.6\cdot90+0.4\cdot130=106$ s) — **trùng** với Smith.
- Tối đa $\Pr[T\le60]$: đi $c_2$ trước cho $0.4$; đi $c_1$ trước cho $0$. Cũng
  $c_2$.

Nhưng đổi $T_d=100$ s: $\Pr$ khi đi $c_2$ trước vẫn $0.4$, khi đi $c_1$ trước là
$0.6$ — **đảo ngược**. Tức là **thứ tự tối ưu phụ thuộc hạn chót**, và một hệ
thống chỉ tối thiểu hoá kỳ vọng sẽ ra quyết định sai một cách có hệ thống khi hạn
chót rộng. Đây là lập luận mạnh nhất để bài báo **công bố $\Pr[T\le T_d]$ chứ
không chỉ median/p90**.

---

## 10b. ĐO ĐƯỢC: tầng hợp tác là một **cỗ máy đồng thuận**, và chính nó loại trừ đa ứng viên

Sau khi cài `--electScope` (một ô chỉ đứng xuống trước claim **cùng chỗ**, trong
bán kính 150 m) và sửa lỗi so sánh **vị trí** thay vì **điểm nhắm**, quét 40 hạt
giống ở 24×24 với **4 vật gây nhầm** (s = 0.85–0.95), 6 UAV, một binary:

| | |
|---|---:|
| nạn nhân được phục vụ | 22/40 = **55 %** |
| run có **≥ 2 điểm nhắm THẬT SỰ khác nhau** | **2/40 = 5 %** |
| trong số đó, phục vụ được nạn nhân | **0/2** |
| tổng summon 43 → số chỗ khác nhau 42 | chỉ **2 %** là rao lại một chỗ đã có |

Tức là **95 % số run chỉ có đúng một điểm triệu tập**, ngay cả khi trong vùng có
bốn vật thể gần-như-giống nạn nhân.

**Cơ chế, đã kiểm bằng toạ độ chứ không suy diễn:** trong seed 22, bốn lãnh đạo ở
(60,120), (20,20), (280,240), (200,120) **đều nhắm vào (97, 221)** — chiếc xa
nhất cách điểm nhắm của chính nó **260 m**. Trong seed 25, một lãnh đạo ở
(440,360) nhắm vào (317, 83), cách **303 m**.

Nghĩa là: **SHARE lan đỉnh bằng chứng toàn cục ra khắp vùng, nên mọi lãnh đạo độc
lập hội tụ về cùng một điểm nhắm.** Thứ loại trừ đa ứng viên **không phải** cơ chế
triệt tiêu bầu cử — mà là **chính việc gộp bằng chứng**. Tầng hợp tác được thiết
kế để đạt đồng thuận về MỘT chỗ, và nó làm đúng như vậy.

**Hệ quả cho §12:** không thể tạo ra chế độ đa ứng viên bằng cách chọn hạt giống
hay chỉnh ngưỡng. Nó đòi hỏi đúng các hạng mục 3–5: lãnh đạo phát **danh sách xếp
hạng** thay vì một điểm, SUMMON mang được danh sách, và UAV DATA có **hàng đợi ứng
viên**. Trước khi có ba thứ đó, mọi phát biểu về "phân vùng hợp tác giữa nhiều
điểm" (P13) là nói về một chế độ mà hệ thống chưa bao giờ vào.

**Cảnh báo:** `--electScope` **chưa được chứng minh là cải tiến**. Seed 22 được
phục vụ ở 83.6 s khi còn 4 lần rao dư thừa, và **không** được phục vụ khi triệt
tiêu chúng — sự dư thừa đang vô tình giúp, vì càng nhiều lãnh đạo phát beacon thì
UAV DATA càng dễ nghe được. Cần campaign so cặp trước khi giữ hay bỏ.

## 10c. Giới hạn tầm nhắm: MỞ được chế độ đa ứng viên, và làm hỏng hiệu năng

Lãnh đạo chỉ được nhắm trong `kAimScopeM = 2 × bán kính ô = 160 m`. So cặp,
**cùng một binary**, 40 hạt giống, 24×24, 4 vật gây nhầm:

| | `aimScope=0` | `aimScope=160` |
|---|---:|---:|
| **nạn nhân được phục vụ** | **55.0 %** | **37.5 %** |
| | | McNemar **b=7, c=0, p=0.0156** |
| run có ≥2 điểm khác nhau | 2/40 | **16/40** |
| sai số median | 34.7 m | 65.5 m |
| đúng người | 33/40 | 23/40 |
| thời gian nhiệm vụ | 152.0 s | 167.7 s |
| lãnh đạo→điểm nhắm, max | 353 m | **128 m** ✓ |

**Bảy hạt giống mất, không hạt nào được** — hồi quy thật, không phải nhiễu.

Nhưng đọc cho đúng thì đây **không** phải bằng chứng rằng giới hạn sai. Nó là bằng
chứng cho hai điều khác:

1. **55 % cũ được mua bằng một cơ chế phi vật lý.** Một lãnh đạo nhắm vào điểm
   cách 353 m là đang tuyên bố về mảnh đất nó không có bằng chứng trực tiếp nào —
   bằng chứng đó tới qua flood nhiều chặng. Đó là **vấn đề tính hợp lệ của bài
   báo**, không phải sở thích thiết kế. Một phản biện nhìn thấy chi tiết này sẽ
   không chấp nhận.
2. **Chế độ đa ứng viên bị lộ ra là chưa được hỗ trợ.** Trong 16 run đa điểm, chỉ
   **1** phục vụ được nạn nhân. Khi nhiều vùng cùng triệu tập, đội UAV **không có
   cơ chế phân bổ nào**: các summon tranh UAV bằng CLAIM theo kiểu *ai nhanh tay*,
   không theo *ứng viên nào đáng đi trước*. Bốn UAV DATA bị xé ra nhiều hướng và
   không chỗ nào hoàn tất.

Điểm 2 chính là bài toán **P13** trong tài liệu này, và giờ nó có bằng chứng thực
nghiệm: hệ thống **chưa từng có** cơ chế đó. Ba hạng mục ở §12 (SUMMON mang danh
sách xếp hạng, hàng đợi ứng viên trong UAV DATA, đấu giá theo chi phí biên thay
CLAIM ai-nhanh-tay) không còn là đề xuất lý thuyết — chúng là thứ đang chặn.

**Chưa chốt mặc định.** Đây là đánh đổi giữa hiệu năng đo được và tính hợp lệ vật
lý, và cả hai đều chính đáng; xem quyết định trong phiên làm việc.

## 11. Vì sao chế độ đa ứng viên có thể **cứu luận điểm của bài báo**

Đây là hệ quả quan trọng nhất, và nó nối thẳng vào vấn đề mở số 1 trong
`STATUS.md`:

> Hiện tại `closed-loop` (không hợp tác, có phản hồi) **thắng** `proposed` về
> thời gian, năng lượng và gói tin (0/120 lần thắng về gói tin). Hợp tác chỉ mua
> được đuôi p90 của sai số định vị tốt hơn 29 %.

Trong chế độ $K=1$ điều đó **tất yếu**: khi chỉ có một điểm để đi, gộp bằng chứng
xuyên ô không mang lại gì về mặt định tuyến — nó chỉ tinh chỉnh toạ độ. Nhưng
trong chế độ $K>1$:

- **`closed-loop` không có cách nào xếp hạng ứng viên.** Nút nào vượt ngưỡng cũng
  hét lên, UAV nào ở trên cũng đáp — nghĩa là nó sẽ **thăm mọi dương tính giả**,
  và thăm theo thứ tự ngẫu nhiên do hình học sweep quyết định.
- **Hợp tác chính là cơ chế tính $\pi_k$.** Cây trong ô + SHARE xuyên ô là thứ duy
  nhất tổng hợp được "5 nút quanh $c_1$ đều báo 0.8" so với "1 nút lẻ ở $c_2$ báo
  0.78". Chênh lệch đó **không quan sát được** ở một nút đơn lẻ.

Do đó giả thuyết kiểm chứng được — và nên là thí nghiệm tiếp theo của dự án:

> **H:** Lợi ích của hợp tác tăng đơn điệu theo $K$. Ở $K=1$ nó bằng 0 về chi phí
> (đã đo). Tồn tại $K^\*$ mà từ đó `proposed` thắng `closed-loop` cả về thời gian
> **lẫn** năng lượng, vì mỗi mồi nhử tránh được đáng giá $2d/V+s\approx 45\text{–}70$ s
> trong khi chi phí gói tin của mặt phẳng hợp tác là hằng số theo $K$.

Phép thử rẻ: bật nguồn nhiễu có cấu trúc (§3), quét mật độ $\lambda$, vẽ
$\mathbb{E}[T]_{\text{proposed}}-\mathbb{E}[T]_{\text{closed-loop}}$ theo $K$ đo
được. Nếu H sai, ta biết chắc là hợp tác chỉ mua được sai số — cũng là một kết
luận sạch. Nếu H đúng, luận điểm gốc của bài báo được phục hồi **trên đúng điều
kiện mà nó thật sự đúng**, chứ không phải bằng cách nói to hơn.

---

## 12. Thứ tự thực hiện, và cái gì phải sửa trong mã

| # | việc | vì sao trước | quy mô |
|---|---|---|---|
| 1 | Nguồn nhiễu có cấu trúc trong `clue-field` + cờ `--clutterDensity` | không có nó thì $K=1$, mọi thứ dưới đây đo trên tập rỗng | ~40 dòng |
| 2 | Cờ `--alertThreshold`, quét đường cong $(\epsilon,\mathbb{E}[T])$ (P9) | rẻ nhất, và đang có $\epsilon=3.3\%$ chưa ai biện minh | ~5 dòng + campaign |
| 3 | Bỏ `electSuppress` tuyệt đối → **xếp hạng và đưa vào hàng đợi** | tầng bầu cử đang vứt $K-1$ ứng viên trước khi định tuyến | giao thức |
| 4 | SUMMON mang **danh sách** ứng viên | 8 B hiện tại chỉ chở 1 điểm; với trần 100 B chở được 13 mục $\times$ 7 B `[id:u8][x:i16][y:i16][q:u8][π:u8]` | wire format |
| 5 | Hàng đợi ứng viên trong `sar-data-uav-app` + quy tắc chỉ số $\pi_k/(d+s_k)$; $K\le4$ nên **vét cạn được nghiệm tối ưu** để làm mốc | P10 | ứng dụng |
| 6 | Đấu giá theo chi phí biên trong CLAIM (P13) | mở rộng cơ chế đã có | giao thức |
| 7 | Thí nghiệm H ở §11 | đây là cái quyết định bài báo | campaign |

**Cảnh báo phương pháp** (theo `STATUS.md` §5): mọi số ở tài liệu này là số của
**trường manh mối**, sinh ra không cần chạy ns-3. Chúng nói được $K$ bằng bao
nhiêu, **không** nói được hệ thống hành xử thế nào. Đừng trích chúng như kết quả
hệ thống. Và khi chạy campaign thật thì $N\ge120$, không rebuild giữa chừng.

---

## 13. Tóm tắt

| bài toán | dạng chuẩn tắc | độ khó | trạng thái trong dự án |
|---|---|---|---|
| (P9) điểm vận hành ROC | phủ xác suất có ràng buộc | 1 chiều, quét được | **chưa có cờ, $\epsilon=3.3\%$ chưa biện minh** |
| (P10) ưu tiên 1 UAV | min-latency có trọng số xác suất | NP-khó; $K\le4$ vét cạn được | chưa có hàng đợi ứng viên |
| (P11) xác minh vs phục vụ | POMDP có hành động thông tin | PSPACE-khó | **chỉ có nội dung nếu FAST có cảm biến khác** |
| (P12) định tuyến trực tuyến | phân tích tỉ số cạnh tranh | — | đang chạy chính sách "không preempt" |
| (P13) phân vùng hợp tác | set-partitioning / đấu giá | NP-khó | CLAIM là đấu giá 1 nhiệm vụ |
| (P14) rủi ro có hạn chót | tối đa $\Pr[T\le T_d]$ / CVaR | thứ tự khác P10 | chỉ báo cáo median/p90 |

Và một điều kiện tiên quyết, không phải bài toán tối ưu mà là điều kiện để các
bài toán trên tồn tại: **trường manh mối phải sinh được nhiều hơn một ứng viên.**
Hiện tại nó không sinh được.
