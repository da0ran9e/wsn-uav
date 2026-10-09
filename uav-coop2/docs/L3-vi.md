# Lớp 3: định tuyến trên mặt đất sau lượt bay (River)

Mô tả gốc của người dùng: CLAUDE.md §8, mục 38–44. Phạm vi: Pha 1, một cụm, đường bay
thẳng, đơn vị là cell.

## 1. Bài toán

UAV bay qua cụm **một lần** theo đường bay $\gamma$ và phát liên tục: gói $s$ được phát tại toạ
độ đường bay $d_s=d_0+s\Delta$, với $\Delta=v\tau$ (0,5 m mỗi gói ở 50 m/s, 10 ms). Mỗi node
nhận gói $s$ với xác suất $1-p(\rho)$, trong đó $\rho$ là khoảng cách ngang tới $\gamma(d_s)$ và
$p(\cdot)$ là đường PER đo từ ns-3. Vì $\gamma$, $d_s$ và $p$ đều biết trước, **BS lập được kế
hoạch trước giờ bay**.

Sau lượt bay, CL của mọi critical cell phải giữ đủ mọi gói được phát trong cụm, với thời gian
hoàn tất nhỏ nhất. Ràng buộc:
- radio bán song công;
- giữa hai cell kề nhau chỉ đi qua một gateway;
- dữ liệu chỉ đi theo cell path đã định.

Gói phát ngoài cụm không được giao cho ai, nhưng cell nào nhận được thì vẫn lưu lại và gửi khi
được hỏi.

| ký hiệu | nghĩa |
|---|---|
| $\mathrm{Cells}$, $z(c)$ | các cell của cụm; tâm của cell $c$ |
| $\mathrm{Crit}$ | critical cells: cell của CH và vài cell có CL vượt trội (so với toàn cụm hoặc với khu vực quanh nó) |
| $\mathrm{Axe}=(a_1,\dots,a_n)$ | các cell mà $\gamma$ cắt qua, theo thứ tự bay |
| $\mathrm{Seg}(a)$ | đoạn dữ liệu của cell Axe $a$: các gói phát khi UAV ở trên $a$ |
| $\omega$ | tham số nửa bề rộng River; chọn để River rộng 3–4 cell, tức $p(\omega)\approx1\,\%$ |
| $\mathrm{Bank}_{\pm}(a)$, $\mathrm{Path}_{\pm}(a)$ | hai Bank mà $a$ phục vụ, và cell path từ $a$ tới mỗi Bank |
| $\mathrm{River}$ | hợp các $\mathrm{Path}$ |

## 2. Thuật toán 1: bảng Axe (tại BS, trước giờ bay)

```text
Algorithm 1  AXETABLE(γ, d0, Δ, N)
1: Axe ← cells crossed by γ, in flight order
2: for each a ∈ Axe do  Seg(a) ← { s < N : γ(d0 + sΔ) ∈ a }
3: send { (a, Seg(a)) : a ∈ Axe } and the Axe direction to CH
4: CH gives every a ∈ Axe its own row
```

Với đường thẳng, $\mathrm{Seg}(a)$ là một khoảng liên tục, khoảng 350 gói mỗi cell. Gói có
$\gamma(d_s)$ nằm ngoài cụm không thuộc $\mathrm{Seg}$ nào.

## 3. Thuật toán 2: thiết lập River (tại mỗi cell Axe)

![thiết lập River](figures/concept-river-setup.png)

Cách đọc hình:
- mũi tên đỏ sẫm: vector tổng của Axe;
- chấm trắng: cell trung tâm;
- đường liền: đường vuông góc qua cell trung tâm, với hai chấm đen nằm cách nó $\omega$;
- hai cell xanh lá đậm và cam đậm: hai Bank của cell trung tâm;
- đường đứt: các đường song song qua những cell Axe khác;
- xanh lá nhạt và vàng: các Bank còn lại;
- xanh nhạt: River.

```text
Algorithm 2  RIVERSETUP(a, u, ω)            ▷ run by Axe cell a; u = unit(z(a_n) − z(a_1))
1: n ← u rotated by 90°                       ▷ the same normal for every Axe cell: parallel lines
2: for σ ∈ {+1, −1} do
3:     Path_σ(a) ← cells crossed by the segment z(a) → z(a) + σ·ω·n, cut at the cluster edge
4:     Bank_σ(a) ← last cell of Path_σ(a)     ▷ River reaching the edge: the edge cell is the Bank
5: River ← ⋃_{a ∈ Axe, σ} Path_σ(a)
```

Trên đường bay thẳng của cụm thử ($W=3{,}5$, $\omega=303$ m, $p(\omega)=1{,}1\,\%$):
- Axe có 15 cell, River 58 cell, Banks 26 cell (12 / 14 hai bên);
- 6 trong 30 Bank là cell biên cụm.

Hình liên quan: [Axe](figures/concept-axe.png), [Banks](figures/concept-banks.png),
[Axe → Banks](figures/concept-axe-banks.png), [River](figures/concept-river.png). Các hình
này do `tools/concept_cells.py` vẽ.
