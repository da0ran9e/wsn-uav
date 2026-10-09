# Lớp 3: định tuyến dữ liệu trên mặt đất sau lượt bay (cơ chế River)

> Phạm vi: Pha 1, bên trong **một cụm**, sau khi UAV fixed-wing bay qua một lần.
> - Lớp 1 (cần bao nhiêu dữ liệu) và Lớp 2 (bay sao cho phủ) là đầu vào đã biết.
> - Lớp 3 là đóng góp chính.
>
> Tài liệu này có bốn phần:
> - §0: lời gốc của người dùng, giữ nguyên văn;
> - §1: phát biểu bài toán;
> - §2: định nghĩa cấu trúc River;
> - §3: mã giả **phần đầu**, gồm việc BS lập kế hoạch và gửi bảng cho CH.
>
> Các phần sau (CH phát bảng xuống cell, Axe bổ sung cho Bank, Circle chuẩn bị và giao dữ
> liệu) sẽ viết tiếp khi được thảo luận.

## 0. Lời gốc (nguyên văn, không chỉnh sửa)

Trích từ CLAUDE.md §8, mục 40–43.

*40. 2026-10-09 · uav-coop2 · trả lời; ý tưởng River / Axe / Banks, critical cells và Circle · kèm ảnh runs-maps*

```text
1. chưa cần biết số file, tuỳ vào cài đặt tham số, nhưng UAV cứ phát liên tục cluster nhận được càng nhiều càng tốt 
2. Tôi có thêm ý tưởng về các node manh, không cần tất cả các cell đều phải nhận dạng, mà sẽ chọn ra một vài CL vượt trội hơn phần trung bình được coi là các điểm xử lý chính bên cạnh CH
3. và các node này mới cần đủ bộ 
4. tạm thời chưa xét đến năng lượng, bộ nhớ hay thời gian


ý tưởng tiếp theo liên quan đến vệt các node nhận được file dọc đường, tôi định sẽ gọi các node có xác xuất cao (tham số) nhận được ít nhất 1 file đầy đủ là River (theo dòng chảy của dữ liệu đổ xuống) các node được UAV chính xác bay ngang qua tạo thành một vệt gọi là Axe các node nằm ở biên tạo thành hai vệt gọi là Banks, dòng sông này mang nhiều dữ liệu nhất và sẽ có trách nhiệm phân phối đến các cell có node quan trọng. 

Các critical cells (quan trọng) này sau khi UAV bay qua sẽ chủ động yêu cầu các gói thiếu thông qua hàng xóm. Vì vậy, các hàng xóm của cell đó cần sẵn sàng phục vụ và tạo thành một vòng service bao quanh critical cell gọi là circle. Để ổn định lưu lượng mỗi hàng xóm sẽ đảm nhận một phần dữ liệu còn thiếu, tuỳ vào lượng dữ liệu mà nó thiếu Circle có thể điều chỉnh kích thước và vị trí, ví dụ circle 6 hàng xóm hoặc circle 12 ...
```

*41. 2026-10-09 · uav-coop2 · đính chính: River/Axe/Banks theo cell, tính trước tại BS, River theo ngưỡng PER, Circle theo phân công của Axe; đường bay đẹp*

```text
bạn gần hiểu đúng rồi, để tôi đính chính lại:
River, Axe và Banks đều tính theo đơn vị cell nhé 

1. tất cả yếu tố này đều có thể được tính toán trước bởi BS thậm chí là cell nào sẽ nhận được phần dữ liệu nào, CH sẽ nắm được thông tin này ngay trước giờ bay và gửi một danh sách hoặc bảng tra cho các cell thuộc Axe để chủ động phân phối thông tin
2. ta thay đổi cách lấy độ rộng của river theo ngưỡng PER của node nhé, như vậy nó cũng có thể tính toán trước 
3. bạn hiểu ý 3 gần giống ý tôi rồi, Circle chuẩn bị sẵn dữ liệu nhưng khi Critical cell yêu cầu thì đưa, 
4. vì Axe đã có phân công từng phần dữ liệu, circle cũng dựa vào đây để phân chia (có thể là theo hướng thuận tiện nhất đến với một cell axe)
5. Ch luôn là một crit cell, các crit cell khác tuỳ vào phân bố của cluster mà chọn ra vài cell vượt trội hẳn so với phần còn lại hoặc so với khu vực quanh nó 


thử mô tả lại bằng hình với PER ở Banks khoảng 80% và đường bay tương đối thẳng nhé, từ giờ ta sẽ xét đến các đường bay tương đối đẹp trước
```

*42. 2026-10-09 · uav-coop2 · đính chính: River rộng 3–4 cell (ngưỡng PER theo tham số); Circle lấy từ Bank; mỗi Axe chọn cặp Bank và cell path; Circle cũng theo cell path*

```text
tôi sẽ đính chính lại, 

ngưỡng PER cho river sẽ điều chỉnh theo tham số sao cho độ rộng của sông cỡ 3-4 cell chiều ngang để đảm bảo cơ chế lan truyền tôi sắp nói sau đây.

circle sẽ lấy data từ node Bank chứ không phải trực tiếp từ Axe, và Axe sẽ bảm bảo bank có đủ dữ liệu vì ngay từ đầu bank chỉ còn thiếu một chút thôi. 
Mỗi cell Axe chọn it nhất 1 cặp Banks và đường đi (cell paths) tương ứng để phục vụ (hoặc có thể được BS sắp xếp từ trước)
circle cell cũng cần được phục vụ theo cell path chứ không được gửi lung tung
```

*43. 2026-10-09 · uav-coop2 · phát biểu bài toán lớp 3 và mã giả; phần đầu: BS lập đường bay, bảng mảnh dữ liệu theo d_track gửi CH*

```text
giờ chúng ta vừa thử phát biểu lại bài toán tầng 3 này và vừa thử viết pseudo nhé, nếu được hãy 
trước tiên là phần đầu, BS thiết lập đường bay, tính toán lộ trình và gửi cho CH bảng thông tin về các mảnh dữ liệu sẽ được phát theo toạ độ đường bay (d_track) để xác định axe và phân công nhiệm vụ
```

## 1. Phát biểu bài toán

### 1.1 Mạng

- Cụm gồm tập cell lục giác $\mathcal{C}$ (bán kính góc $R$, bề rộng $w=\sqrt3R$) và tập
  node $V$. Node $v$ có vị trí $x_v$, thuộc cell $\mathrm{cell}(v)$, và có điểm năng lực
  $s(v)$.
- $\mathrm{CL}(c)$ là node mạnh nhất của cell $c$. CH nằm trong cell $c_{\mathrm{CH}}$.
- Hai node nối được với nhau khi $\lVert x_u-x_v\rVert\le r_{\mathrm{link}}$ (50 m).
- Tuyến đã được BS tính sẵn ([ROUTING-vi.md](../../uav-coop/docs/ROUTING-vi.md)): mỗi cặp
  cell kề nhau $(a,b)$ có **đúng một** liên kết gateway $\mathrm{gw}(a,b)$, và mọi dữ liệu đi
  giữa hai cell chỉ được đi qua liên kết đó. Không node nào bị cô lập.
- $N(c)$ là các cell kề $c$ nằm trong cụm. $N^2(c)$ là các cell cách $c$ không quá 2 bước.
  $\mathrm{hd}(a,b)$ là khoảng cách lục giác (số bước cell).

### 1.2 Đường bay và luồng phát: toạ độ $d_{\mathrm{track}}$

- Đường bay $\gamma:[0,L]\to\mathbb{R}^2$ do BS lập, tham số hoá theo **độ dài cung**
  $d$ (gọi là $d_{\mathrm{track}}$). UAV bay ở độ cao $H$ với tốc độ $v$ không đổi.
- UAV phát liên tục mỗi $\tau$ giây, bắt đầu tại $d_0$. **Gói thứ $s$ được phát tại**

  $$d_s=d_0+s\,v\tau,\qquad s=0,\dots,N-1,\qquad N=\left\lfloor\frac{L-d_0}{v\tau}\right\rfloor+1 .$$

  Với $v=50$ m/s và $\tau=10$ ms, cứ 0,5 m đường bay có một gói.
- Luồng gói là chuỗi file $F_1,\dots,F_M$ (kích thước $K_1,\dots,K_M$), phát nối tiếp và
  **một lần**. Gói $s$ thuộc file $f(s)$ với chỉ số $s-\sum_{i<f(s)}K_i$.
- File không thay thế được cho nhau. Node được trao đổi gói với nhau để ghép file.
- Tập cần giao $\mathcal{D}=\{0,\dots,N-1\}$ là mọi gói đã phát. "Đủ lượng" do BS quyết
  định (Lớp 1–2).

### 1.3 Kênh: PER biết trước

- Node $v$ nhận gói $s$ với xác suất $1-p(\rho)$, trong đó
  $\rho=\lVert x_v-\gamma(d_s)\rVert$ là khoảng cách ngang tới vị trí UAV lúc phát.
  Sự kiện nhận ở các gói và các node là độc lập.
- $p(\cdot)$ là đường PER theo khoảng cách. Đường này đo từ chính mô phỏng ns-3, ở độ cao
  100 m và $\alpha=3$ ([data/per-distance.csv](data/per-distance.csv)):

  | $\rho$ | 300 m | 550 m | 750 m | 1 000 m | 1 250 m |
  |---|---|---|---|---|---|
  | $p$ | 1 % | 5 % | 20 % | 50 % | 80 % |

- Vì vậy mọi đại lượng trong §2 **đều tính được tại BS trước giờ bay**. Chỉ tập gói
  $h_v$ mà mỗi node thực sự nhận được mới phải chờ sau lượt bay mới biết.

### 1.4 Mục tiêu và ràng buộc

- **Critical cells** $\mathcal{K}\subseteq\mathcal{C}$ (định nghĩa ở §2); node đích là
  $T=\{\mathrm{CL}(k):k\in\mathcal{K}\}$.
- **Mục tiêu:** mọi $u\in T$ giữ đủ $\mathcal{D}$, với **thời gian hoàn tất** nhỏ nhất. Mốc
  $t=0$ là lúc UAV rời cụm. Mục tiêu phụ: ít lần phát.
- Tạm bỏ qua năng lượng, bộ nhớ, ràng buộc sở hữu và vật cản.
- **Ràng buộc:**
  1. Mỗi node có một radio bán song công: tại một thời điểm chỉ phát hoặc chỉ nhận.
  2. Liên kết G2G có mất gói (n = 3,5, che khuất tĩnh, Rayleigh), nên phải xác nhận và gửi lại.
  3. Giữa hai cell chỉ được đi qua gateway $\mathrm{gw}(a,b)$. Mỗi cặp gateway có kênh riêng.
  4. Dữ liệu chỉ đi theo **cell path** đã định trước, không phát tràn.

### 1.5 Biết trước và biết sau

| BS biết trước giờ bay | Chỉ biết sau lượt bay |
|---|---|
| $\gamma$, $d_s$, $p(\cdot)$, River, Axe, Banks, đoạn của từng Axe, cặp Bank, cell path, $\mathcal{K}$, Circle | $h_v$: các gói mỗi node thực sự nhận; gói nào Bank còn thiếu |

## 2. Cấu trúc River (đơn vị: cell)

Hình minh hoạ: [concept-river](figures/concept-river.png),
[axe](figures/concept-axe.png), [banks](figures/concept-banks.png),
[axe-banks](figures/concept-axe-banks.png), [critical](figures/concept-critical.png),
[circle](figures/concept-circle.png). Hình vẽ cho đường bay thẳng, $W=3{,}5$.

| ký hiệu | định nghĩa |
|---|---|
| $z_c$, $\mathrm{PER}_c$ | tâm cell $c$; $\mathrm{PER}_c=p\big(\min_d\lVert z_c-\gamma(d)\rVert\big)$, tức PER tại điểm đường bay đi gần tâm cell nhất |
| $W$, $\theta$ | **tham số** độ rộng River (số cell theo chiều ngang, 3–4); $\theta=p(Ww/2)$. Với $W=3$, 3,5 và 4 thì $\theta$ lần lượt là 0,7 %, 1,1 % và 1,6 % |
| $\mathcal{R}$ | **River**: $\{c:\mathrm{PER}_c\le\theta\}$ |
| $\mathcal{A}=(a_1,\dots,a_n)$ | **Axe**: các cell mà $\gamma$ cắt qua, xếp theo $d$ lúc vào cell |
| $S_a$ | **đoạn** của cell Axe $a$: các gói $s$ có $\gamma(d_s)$ nằm trong cell $a$. Gói phát ngoài cụm (đoạn đường dẫn) tính cho $a_1$ (trước khi vào) hoặc $a_n$ (sau khi ra). Với đường thẳng, $S_a$ là một khoảng liên tục |
| $\mathcal{B}$ | **Banks**: $\{c\in\mathcal{R}\setminus\mathcal{A}:\exists\,c'\in N(c),\ c'\notin\mathcal{R}\}$ |
| $\sigma(c)\in\{\mathrm{L},\mathrm{R}\}$ | bên của đường bay mà $c$ nằm (dấu tích có hướng với $\gamma'$) |
| $b_\sigma(a)$, $\pi(a\to b)$ | Bank bên $\sigma$ mà Axe $a$ phục vụ, và cell path từ $a$ tới Bank đó (§3, dòng 14–17) |
| $\mathcal{K}$ | **critical cells**: $\{c_{\mathrm{CH}}\}$ ∪ các cell có $s(\mathrm{CL})>\mu+2\sigma_s$ (vượt trội toàn cụm) ∪ các cell có $s(\mathrm{CL})>\mu+\sigma_s$ và mạnh nhất trong $N^2$ (vượt trội khu vực). $\mu,\sigma_s$ là trung bình và độ lệch chuẩn điểm của các CL |
| $\mathcal{O}(k)$ | **Circle** của $k$: $N(k)$ (tối đa 6 cell) |

## 3. Mã giả: phần đầu (tại BS, trước giờ bay)

### Thuật toán P0: toạ độ luồng phát theo đường bay

```text
Algorithm P0  TRACKMAP(γ, L, v, τ, d0, (K_1..K_M))
 1: N ← ⌊(L − d0) / (v·τ)⌋ + 1
 2: for s ← 0 to N−1 do
 3:     d_s ← d0 + s·v·τ                                    ▷ d_track của gói s
 4:     p_s ← γ(d_s)                                        ▷ vị trí UAV khi phát (hình chiếu)
 5:     f(s) ← min{ f : Σ_{i≤f} K_i > s }                   ▷ file chứa gói s
 6: return (d_s, p_s, f(s)) for s = 0..N−1
```

### Thuật toán P1: lập cấu trúc River và phân công

```text
Algorithm P1  BSPLAN(C, γ, {p_s}, p(·), W, scores)
    ▷ — River, Axe, Banks —
 1: θ ← p(W·w/2)
 2: for each c ∈ C do PER_c ← p( min_d ‖z_c − γ(d)‖ );  σ(c) ← SIDE(z_c, γ)
 3: R ← { c ∈ C : PER_c ≤ θ }
 4: A ← cells crossed by γ, in order of first entry           ▷ a_1 .. a_n
 5: for each a ∈ A do S_a ← ∅
 6: for s ← 0 to N−1 do                                        ▷ đoạn của từng cell Axe
 7:     c ← CELLOF(p_s)
 8:     if c ∈ A then S_c ← S_c ∪ {s}
 9:     else if s is before γ enters the cluster then S_{a_1} ← S_{a_1} ∪ {s}
10:     else S_{a_n} ← S_{a_n} ∪ {s}
11: B ← { c ∈ R \ A : ∃ c' ∈ N(c), c' ∉ R }
12: assert ⋃_a S_a = {0..N−1} and the S_a are pairwise disjoint
    ▷ — Axe → cặp Bank, theo cell path trong River —
13: for each a ∈ A, each side σ ∈ {L, R} do
14:     Q ← { b ∈ B : σ(b) = σ, hd(a, b) ≤ ⌈W⌉ }
15:     if Q = ∅ then b_σ(a) ← ⊥; continue                     ▷ River chạm biên cụm ở bên này
16:     b_σ(a) ← argmin_{b∈Q} ( hd(a,b), |d(b) − d(a)| )        ▷ d(·): d_track của điểm gần nhất
17:     π(a → b_σ(a)) ← CELLPATH(a, b_σ(a), R)
    ▷ — critical cells —
18: μ, σ_s ← mean, std of { s(CL(c)) : c ∈ C }
19: K ← {c_CH} ∪ { c : s(CL(c)) > μ + 2σ_s }
20:        ∪ { c : s(CL(c)) > μ + σ_s and s(CL(c)) ≥ max_{c'∈N²(c)} s(CL(c')) }
    ▷ — Circle: mỗi hàng xóm nhận một nhóm Axe liên tiếp, lấy từ Bank theo cell path —
21: for each k ∈ K \ R do
22:     (n_1..n_m) ← N(k) sorted by projection of z_n on the flight direction
23:     split (a_1..a_n) into m consecutive groups G_1..G_m of near-equal size
24:     σk ← σ of the Bank nearest to k
25:     for j ← 1 to m do
26:         D_j ← ⋃_{a ∈ G_j} S_a                               ▷ phần dữ liệu n_j đảm nhận
27:         β_j ← argmin_{b ∈ { b_σk(a) : a ∈ G_j } \ {⊥}} ( hd(b, n_j), ‖z_b − z_{n_j}‖ )
28:         π(β_j → n_j) ← CELLPATH(β_j, n_j, (C \ R \ {k}) ∪ {β_j})
29:     O(k) ← { (n_j, G_j, β_j, π(β_j → n_j)) : j = 1..m }
30: return Θ ← BUILDTABLE(A, {S_a}, B, {b_σ, π}, K, {O(k)})
```

```text
Function CELLPATH(src, dst, allowed)     ▷ đường cell ngắn nhất; nhiều đường bằng nhau thì
 1: BFS from src over the cell graph restricted to allowed;   ▷ chọn đường thẳng nhất
 2:     neighbours expanded in order of ‖z_n − z_dst‖
 3: assert dst reached                                          ▷ BS bảo đảm có đường
 4: return the cell sequence src → … → dst
```

### Thuật toán P2: bảng gửi CH

```text
Algorithm P2  BUILDTABLE and SEND (at the BS, before the flight)
 1: header ← (pathId, d0, v·τ, N, (K_1..K_M), W)
 2: for each a_i ∈ A do
 3:     row_A[i] ← (a_i, intervals of S_{a_i}, (b_L(a_i), π_L), (b_R(a_i), π_R))
 4: for each k ∈ K do
 5:     row_K[k] ← (k, CL(k), [ (n_j, first(G_j), last(G_j), β_j, π(β_j → n_j)) ]_j)
 6: Θ ← header ‖ row_A ‖ row_K, packed into self-contained frames ≤ 100 B
 7: send Θ to CH over the BS link, before take-off
```

**Ước lượng kích thước bảng** (cụm 109 cell, mã cell 1 B; đường thẳng: 15 Axe, 7 critical cell):

| phần | mỗi mục | tổng |
|---|---|---|
| header | ~16 B | 16 B |
| row_A | 1 + 4 (một khoảng) + 2 × (1 + đường ≤ 4) = 15 B | ~225 B |
| row_K | 2 + 6 × (1 + 2 + 1 + đường ≤ 6) = 62 B | ~430 B |
| **tổng** | | **~670 B, khoảng 7 khung** |

Một cell Axe trên đường thẳng giữ khoảng $w/(v\tau)\approx350$ gói. Cell Axe đầu và cuối
giữ thêm phần đường dẫn ngoài cụm, khoảng 510 gói mỗi đầu.

## 4. Điểm chưa chốt

1. **Gói phát ngoài cụm** (đường dẫn vào và ra, mỗi đoạn khoảng 510 gói): tạm tính cho
   cell Axe đầu và cuối (P1 dòng 9–10). Có nên coi chúng là một phần của $\mathcal{D}$ không,
   hay chỉ giao các gói phát trong cụm?
2. **Critical cell nằm trong River** (CH luôn nằm trên Axe): P1 dòng 21 bỏ qua những cell
   này. Chúng nhận thẳng từ Axe hoặc Bank bên cạnh, hay vẫn cần Circle?
3. **Bên không có Bank** (River chạm biên cụm): P1 dòng 15 để trống. Có cần dùng Bank
   bên kia thay thế không?
4. **Đường bay cong:** khi đó $S_a$ có thể gồm nhiều khoảng và Axe có thể đi qua lại một cell.
   Bảng đã cho phép một cell có nhiều khoảng, nhưng hình và ước lượng ở đây mới chỉ tính cho
   đường thẳng.
5. **Bước tiếp theo cần viết:**
   - P3: CH phát bảng $\Theta$ xuống, mỗi cell chỉ nhận phần của mình;
   - P4: Axe bổ sung cho Bank;
   - P5: Circle chuẩn bị dữ liệu và giao khi critical cell yêu cầu.
