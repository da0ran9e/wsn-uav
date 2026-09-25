# Hệ Phase 1 (PA1) — cài đặt, kiểm chứng, kết quả

> Tài liệu của `models/p1/`. Hệ cũ (`models/common/`, `models/application/`)
> không bị đụng tới.
>
> Trạng thái: cài **PHA 0 (P0.0–P0.6) → T0 → T1** rồi dừng. `22 096` CHECK,
> sạch trên 9 tổ hợp lưới/bán kính/hạt giống.

## 0. Thay đổi cấu trúc của PA1

Đường bay không còn là "thăm tâm ô". Nó là **bay dọc đường hàng + lượn bám**:

```
Ω thô → lồi hoá (P0.0) → chọn ψ (P0.1) → lát lưới XOAY theo ψ (P0.2)
      → mỗi nút tự tính hàng và độ lệch δ_ν (P0.4)
      → bầu CH CÓ Ý THỨC ĐƯỜNG BAY (P0.5)
      → nhu cầu k_n rồi θ_n (P0.6)
      → T0 chi phí phục vụ c_n     ← TÍNH MỘT LẦN, KHÔNG LẶP
      → T1 chia HÀNG cho các UAV   ══ ĐÃ CÀI ĐẾN ĐÂY ══
```

**Vòng phụ thuộc đã biến mất.** Trước đây `c_n` phụ thuộc độ lệch, độ lệch phụ
thuộc tuyến, tuyến lại cần `c_n` — nên T4 phải lặp, và nó **dao động chu kỳ 2**,
phải thêm phép kiểm tự nhất quán và bước rút chia đôi. Nay đường bay là **đường
hàng đã cố định ở Pha 0**, `δ_n` là thuộc tính của CH chứ không của kế hoạch.
Harness kiểm điều này: chạy `ServiceCost` hai lần phải ra **cùng một số**.

## 1. Kiểm toán PA1 trước khi cài

**Hai công thức P0.5/T0.4 ra từ MỘT mô hình** — lượn hình sin biên độ δ, bước
sóng 2a:

| | |
|---|---|
| độ dài thêm trên một bước ô | `a·δ²k²/4 = π²δ²/(4a)` với `k = π/a` ✓ |
| bán kính cong nhỏ nhất | `1/(δk²) = a²/(π²δ)` ⇒ `δ_max = a²/(π²ρ)` ✓ |

Chúng **không độc lập** — không thể sửa một cái mà quên cái kia. Tốt.

**F1 khớp số:** đo `E|δ| = 0.389 R_c` (PA1 nói 0.385); tỉ lệ vi phạm `46 %` với
`n_c=1`, `2.07 %` với `n_c=5`, `0.04 %` với `n_c=10` (PA1: 45 %, ~2 %, ~0 %).

> ⚠️ **`δ_max ≈ 0.4 R_c` CHỈ đúng tại điểm thiết kế.** `δ_max/R_c = 3R_c/(π²ρ)`
> **tăng tuyến tính** theo `R_c`: bằng `4/π² = 0.405` chính xác tại `R_c = 4ρ/3`,
> nhưng `0.29 R_c` ở `0.94ρ` và `1.05 R_c` ở `3.45ρ` — chỗ đó ràng buộc **không
> còn cắn**. Bảng F1 chỉ áp dụng **ở lân cận điểm thiết kế**; cần ghi rõ.

**Lập luận P0.1 đúng:** chi phí mỗi lần rẽ không phụ thuộc ψ (`h` từ lưới, `ρ`
từ khí động), tổng độ dài hàng ≈ `A/h` cũng không — nên min chi phí rẽ ⟺ min số
hàng ⟺ min bề rộng ⊥ ψ. Harness kiểm calipers với quét thô 0.1°.

## 2. P0.5 — hai số hạng cùng đơn vị giây

```
n* = argmin  c(θ(I_ν)) + π²δ_ν²/(4a·v_cruise)   s.t.  δ_ν ≤ δ_max
```

`ElectScore()` **đã bị xoá khỏi `Node`**: mục tiêu P0.5 cần hình học ô, mà một
nút không có. Dựng nó trong `p1-cells.cc` chính là thứ **khử trọng số chọn tay**
mà mọi biến thể LEACH/HEED phải chọn giữa hai đại lượng không cùng đơn vị.

Harness kiểm **I2** (CH luôn trong `δ_max`) và kiểm luôn **độ cong của đường
lượn ≥ ρ** — tức đường bay P0.5 hứa hẹn là bay được thật.

## 3. Kết quả — `R_c = 84 m` (≈ đúng điểm thiết kế `4ρ/3 = 84.9 m`)

```
=== PHASE 0   40x40 nút, R_c=84m, rho=63.7m (1.32 rho)
cells=32 trên 5 hàng   served=32 barren=0   (F1 hỏng: 0)
a=145.5m  h=126.0m  delta_max=33.7m = 0.401 R_c
F1 theo số ứng viên:  n_c=6: 0/1   n_c=7: 0/1   n_c=12: 0/30

=== P0.6/T0   Pe*=0.050  J=3  sàn Fano=0.250  K=24 tệp × 4096 B
  F2 thoả: 0.050 < 1/(J+1) = 0.250
  I=1.00 -> k=9 tệp,  θ=87 743 B      I=0.10 -> k=86 tệp, θ=723 824 B
  32 CH: 32 phải lượn vòng, 0 hỏng F3;  phục vụ 837 s, trong đó lượn bám 8 s (1%)
  MỘT lượt bay giao 60 849 B ở hành trình, 84 513 B ở tốc độ tối thiểu

=== T1  (R_c=94)  5 hàng, 24 CH
method                  M   makespan   spread     turns     depot
credit (free)           2       462s    12.5%       37s       39s
credit (contiguous)     2       462s    12.5%       37s       39s
split                   2       463s    15.1%       26s       39s
credit (free)           3       404s    44.7%       34s       73s
credit (contiguous)     3       393s    43.1%       23s       73s
split                   3       393s    46.0%       17s       68s
```

**Chi phí lượn bám chỉ chiếm 1 % chi phí phục vụ.** Toàn bộ phần còn lại là liều
— và cả 32 CH đều phải lượn vòng, vì `θ` (88–724 kB) vượt xa trần một lượt bay
(84.5 kB). Đây vẫn là vấn đề tham số cũ, nay có dạng rõ hơn: **`k_n` và cỡ tệp
quyết định tất cả**.

**Lệch tải tăng mạnh theo số UAV** (12.5 % ở M=2 → 44.7 % ở M=3) vì chỉ có **5
hàng** — hàng là đơn vị không chia được, nên `M` gần số hàng thì lệch là tất yếu.
Đây là hệ quả trực tiếp của việc PA1 đổi đơn vị phân hoạch từ ô sang hàng.

## 4. Ba lỗi tìm ra khi cài

1. **Mặc định `Election` là `CAPABILITY` chứ không phải `FLIGHT_AWARE`** — P0.5
   không chạy. Harness bắt qua bất biến "CH phải là nút tốt nhất theo P0.5".
2. **`pick < 0` làm sentinel trong khi chỉ số hàng CÓ THỂ ÂM** (lưới đặt trong
   hệ hàng, toạ độ axial chạy hai phía gốc). Hàng `-2` bị coi là "không tìm
   thấy", rơi vào nhánh dự phòng, chọn lại `-2`, rồi **thoát vòng lặp** — chỉ 3
   trong 5 hàng được giao. Cùng loại lỗi với `best = -1.0` đã sửa ở lần trước.
3. **Số UAV nhiều hơn số hàng** ⇒ mầm trùng ⇒ một hàng bay **hai lần**. Nay chỉ
   gieo `min(M, |hàng|)` mầm, số UAV dư để không — hàng không chia được.

## 5. Còn treo

- **T0.4 tính hai lần một cách bảo thủ:** nó tính tiền lượn bám `π²δ²/(4a)` để
  **tới** CH, **và** lấy liều ở `G(δ_n)` là độ lệch của một lượt bay **thẳng**.
  Hai thứ đó là hai chuyến bay khác nhau. Nếu lượn tới CH thì liều gần `G(0)`;
  nếu bay thẳng thì không có độ dài thêm. Cài **đúng như spec**, và đánh dấu
  `DoseAtHead()` là chỗ duy nhất cần sửa nếu cách đọc kia mới đúng.
- **§K vẫn viết "khi và chỉ khi"** với `R_c ≥ 4ρ/3`. Harness đo lại mỗi lần
  chạy: công thức được trích **thổi** chi phí rẽ chật tới **15.5 %** so với
  Dubins thật (tối ưu thật là CCC), và ngưỡng thật là `1.218 ρ` / `1.156 ρ`.
- **`rxBps` chưa vào mục tiêu P0.5** — chưa rõ nó có cắn không khi cỡ tệp đã cố
  định. `TODO(param)`.

## 6. Lịch sử — cái gì đã bị bỏ, và vì sao

Tài liệu spec đã đi qua ba bản. Ghi lại đây để không ai đi tìm những khái niệm
đã chết trong code:

| Khái niệm | Xuất hiện ở | Trạng thái |
|---|---|---|
| **Lớp ô A / B / C** theo *phương thức cảm biến* | Bản 1, Bước 0.3 | **BỎ.** Bản 2 §0.2.2 thay bằng giả định phạm vi *"mọi ô có ≥1 nút camera"*; không còn khái niệm phương thức. Code chỉ còn `SERVED` / `BARREN`. |
| **Tầng 1 chạy TRƯỚC chuyến bay** → tập nghi vấn `𝒟`, tiên nghiệm `ω_n`, `θ` phân tầng | Bản 1 | **BỎ.** Bản 2 N1: không nghi vấn nào tồn tại trước chuyến bay. `θ` chỉ còn theo năng lực. |
| **`T_local`** — thời gian phát tán tham chiếu trong cụm | Bản 1 Bước 0.4 | **BỎ.** Bản 2 N3: CH đối sánh dữ liệu *của chính nó*, không có dữ liệu di chuyển trong cụm. |
| **T2 = GTSP** với `h` cấu hình hướng mũi mỗi nút | Bản 1, Bản 2 | **THAY.** PA1 T2: bài hoán vị với chi phí `L(|Δr|·h, ρ)` chỉ phụ thuộc hiệu chỉ số hàng. Nhỏ hơn nhiều bậc. |
| **T4 bắt buộc lặp** (vì `c_n` ↔ `b` vòng tròn) | Bản 1, Bản 2 | **THÀNH TUỲ CHỌN.** PA1 T0.2: `δ_n` cố định từ P0.5, `c_n` tính một lần. |
| **Đơn vị phân hoạch là Ô** | Bản 1, Bản 2 | **THAY.** PA1 T1: đơn vị là **HÀNG** — UAV vào hàng nào thì bay hết hàng đó. |

Toàn bộ code của các bản trước còn trong git tại thẻ
`p1-full-pipeline-before-rebuild`.


## 6b. Hai thí nghiệm về `R_c` — bay qua CL vs lan gói trong ô

Hai tác động ngược chiều của `R_c`, đo trên **6 hạt giống**, vùng 780×484 m,
1600 nút @20 m, tầm mặt đất 40 m, ρ=63.7 m.

```
  R_c |     bay qua moi CL (s)    |   lan 1 goi trong o (s)   | ty le
      |   min    TB    max        |   min    TB    max        | bay/lan
   40 |   456   456   456         |   0.6   0.6   0.7         |   702x
   80 |   245   246   247         |   3.1   3.2   3.4         |    76x
  140 |   152   155   159         |   6.5   6.7   7.0         |    23x
  200 |   186   189   191         |   6.3   7.2   7.7         |    26x
  250 |   123   126   130         |   9.2  10.3  11.4         |    12x
  280 |   139   141   146         |   8.7  10.2  13.4         |    14x

tuong quan: bay vs R_c = -0.756   lan vs R_c = +0.933   bay vs lan = -0.887
```

**Ba kết luận.**

**(1) Hai đại lượng nghịch chiều đúng như spec nói** — `bay` giảm (`−0.756`),
`lan` tăng (`+0.933`), tương quan giữa chúng `−0.887`. Nguồn rõ ràng: số hàng
`9 → 2` kéo thời gian bay xuống; độ sâu cây `1.8 → 8.7` và số nút phải phát
`3.3 → 154` kéo thời gian lan lên.

**(2) Nhưng chúng KHÔNG cùng bậc độ lớn — lan gói tin không bao giờ là nút thắt.**
Tỉ lệ đi từ **702×** xuống **12×**, và **không bao giờ chạm 1**. Ở mọi `R_c`
trong dải, thời gian bay lớn hơn thời gian lan ít nhất **một bậc**. Nghĩa là
`T_local` **không phải** một trong các tác động đáng kể lên `R_c` — đúng như
nghi vấn ❓ mà Bản 2 §0.4 tự đặt ra sau khi chốt N3.

**(3) Khe MAC quyết định tất cả, kích thước gói không quyết định gì.**
100 B ở 250 kbps là **3.2 ms** airtime, so với khe **200 ms** đã đo — chênh
**62×**. Mọi kết luận về `R_c` mà phụ thuộc độ dài gói là kết luận về sai biến.

### N3 đáng giá bao nhiêu — bằng giây

Bản 1 để cụm trưởng **phát tán tập tham chiếu** trong ô (`T_local`). N3 bỏ điều
đó. Dùng đúng mô hình lan trên, một tập tham chiếu là `87 743 B = 878 gói`:

| `R_c` | bay cả vùng | lan **1 gói** | lan **cả tập tham chiếu** |
|---:|---:|---:|---:|
| 40 m | 456 s | 0.7 s | 576 s (**1×** chuyến bay) |
| 80 m | 246 s | 3.3 s | 2 895 s (**12×**) |
| 160 m | 164 s | 7.1 s | 6 248 s (**38×**) |
| 280 m | 139 s | 9.7 s | 8 546 s (**61×**) |

**Phát tán tham chiếu trong một ô tốn gấp hàng chục lần bay hết cả vùng.**
N3 không phải một phép đơn giản hoá — nó là **phiên bản duy nhất khép được**.

### Mô hình lan, và giới hạn của nó

Ba mô hình, vì sự thật bị kẹp chứ không biết chính xác:

| | |
|---|---|
| `depth` | tái dùng không gian hoàn hảo — cùng độ sâu phát cùng lúc. **Cận dưới.** |
| `forwarders` | không tái dùng — mỗi lần phát một khe. **Cận trên.** |
| `slots` | **tô màu khe tham lam**: nút phát ở khe sớm nhất sau cha nó mà không có ai trong `2×` tầm mặt đất đang phát. **Số nên trích.** |

Tái dùng không gian mua được nhiều ở ô lớn: `R_c=250` có **158 nút phải phát**
nén vào **53 khe** — gấp **3.0×**.

⚠️ Khe 200 ms là số đo cho **`Send()` liên tiếp từ MỘT nút**. Ở đây tôi tính
một khe đầy cho **mỗi lần phát của mỗi nút** — bi quan — nhưng lại cho nhiều nút
phát **cùng khe** khi đủ xa — lạc quan. Hai cái bù nhau, và `TODO(param)`: cần
đo tranh chấp CSMA giữa các nút khác nhau để chốt.

## 6c. Nhiều anten trên UAV có đổi được gì không? — **KHÔNG**

Câu hỏi: UAV mang nhiều anten, phát **các gói khác nhau** tới **nhiều nút cùng
lúc**, mỗi nút chỉ nghe được từ một anten. Điều đó có dịch chuyển hai kết quả ở
§6b không?

Trả lời phải **ĐO**, không lý luận, vì nó quy về hai phép đếm.

`examples/p1-antenna-test.cc`, 6 hạt giống, lưới 1600 nút, quét `R_c` 40→280 m.
Đường bay lấy đúng PA1: dọc luống cộng lượn ra CH, dấu của độ lệch theo phía CH
thật. Lấy mẫu **mỗi 2 m**.

### Điều kiện để anten thêm có ích

Phải đồng thời: **(a)** có hơn một nút dưới máy bay cùng lúc, **và (b)** các nút
đó cần **nội dung khác nhau**. Dưới **I4** (quay vòng đều, không báo nhận) (b)
**sai theo thiết kế** — mọi CH nhận cùng một luồng tham chiếu, và chính sự đồng
nhất đó mới làm phép quy xác suất→liều hợp lệ. Vậy **một** anten vô hướng đã
phục vụ **mọi** nút trong `p(d)` cùng lúc rồi.

### A. Một lần quảng bá phục vụ bao nhiêu CH

| `R_c` (m) | số CH | trong tầm cùng lúc (trải 6 hạt) | nhiều nhất | % thời gian có ≥2 |
|---|---|---|---|---|
| 40 | 111 | **21.4** [21.1, 21.6] | 32 | 100 % |
| 94 (điểm thiết kế) | — | **≈4** | 8 | ~95 % |
| 140 | 13 | **1.92** [1.76, 2.19] | 4 | 60 % |
| 200 | 10 | **1.35** [1.28, 1.39] | 3 | 35 % |
| 280 | 6 | **0.76** [0.75, 0.77] | 2 | 15 % |

Ở điểm thiết kế, **một** búp sóng đã phủ ~4 CH cùng lúc. Anten thứ hai phải vượt
con số đó, mà nó không thể: nội dung giống hệt nhau.

### B. Một lượt bay gieo sẵn bao nhiêu

Phải tách hai khái niệm, đừng lẫn:

| | nghĩa | dùng cho |
|---|---|---|
| `pass` | nằm trong tầm ở **một thời điểm nào đó** của lượt bay | **một luồng** gói — đúng cái T0 làm |
| `snap` | nằm trong tầm ở **đúng một thời điểm** | **một gói** duy nhất |

Với `R_c ≤ 180 m`, **`snap` = 100 %**: một gói duy nhất phủ **trọn ô**. Lý do là
tầm không–đất `d50 = 190 m` lớn hơn bán kính ô, nên **vết phủ của UAV nuốt cả ô**.

| `R_c` (m) | `snap` gieo | khe còn lại từ tập `snap` | khe nếu lan từ **một CH** |
|---|---|---|---|
| 94 | 100 % | **0** | ~20 |
| 180 | 99 % | 0.67 | 32.9 |
| 240 | 92 % | 5.81 | 37.9 |
| 280 | 85 % | 15.5 | 51.2 |

**Quảng bá đã xoá gần hết phần việc của mạng mặt đất — miễn phí, không cần anten
nào thêm.** Gieo nhiều gốc không đòi nhiều anten: **một** lần quảng bá đã gieo
mọi nút trong tầm.

### Kết luận

| | nhiều anten đổi được gì |
|---|---|
| §6b thí nghiệm 1 (bay qua CL) | **Không.** Thuần động học: hàng × chiều dài + rẽ + lượn. Vô tuyến không xuất hiện trong bất kỳ số hạng nào. |
| §6b thí nghiệm 2 (lan trong ô) | **Không.** Nguồn là CH, lan trên mạng **mặt đất**; UAV không có mặt. |
| T0 (giao liều UAV→CH) | **Không** — và đây mới là chỗ tưởng có. Quảng bá đã phục vụ mọi CH trong tầm **cùng lúc**; thêm búp sóng chỉ có ích nếu các CH cần nội dung khác nhau, điều I4 cố tình loại bỏ. |

Nói chặt: với **K** CH trong tầm và nội dung **như nhau**, quảng bá tốn **1** lần
truyền; unicast với **S** anten tốn **⌈K/S⌉**. Quảng bá **luôn** ≥ tốt bằng, và
tốt hơn hẳn khi `K > S`. Đo được `K ≈ 4` ở điểm thiết kế.

### ⚠️ Kết luận này treo trên hai tham số chưa đo

1. **`p(d)` với `d50 = 190 m` vẫn là `TODO(param)`.** Toàn bộ §6c đứng trên nó.
2. **Độ cao bay `z` chưa phải tham số của p1**, nên `p(d)` đang tính trên khoảng
   cách **ngang**. Độ nhạy, tại `R_c = 94 m`:

   | `z` (m) | 0 | 50 | 100 | 125 | 150 | 175 | 200 |
   |---|---|---|---|---|---|---|---|
   | CH trong tầm | 3.96 | 3.70 | 2.81 | 2.12 | **1.26** | 0.73 | **0.00** |

   Trên **~165 m** con số tụt dưới 1 và lập luận **đổ**. Dưới đó nó vững. Phải
   chốt `z` và đo `p(d)` trước khi trích §6c vào bài.

Hình: `docs/visualize/result/p1-antenna.png`.

## 7. Sửa mệnh đề trung tâm — VẪN CHƯA VÀO SPEC

`R_c ≥ 4ρ/3` suy từ `h = 2ρ`, tức điểm **nửa đường tròn hoàn hảo** — cực tiểu
toàn cục của chi phí rẽ. Nhưng "hàng kề tối ưu" là phép so **với nhảy hàng**, mà
nhảy hàng cũng xấu đi khi `h` nhỏ. **Hai ngưỡng khác nhau.**

| | ngưỡng `R_c` | tại ρ = 70.6 m |
|---|---|---|
| phát biểu (`4ρ/3`) | 1.333 ρ | 94.2 m |
| giao điểm thật, **theo công thức được trích** | **1.218 ρ** | 86.0 m |
| giao điểm thật, **theo Dubins tối ưu** | **1.156 ρ** | 81.6 m |

Thêm nữa, công thức chế độ rẽ chật được trích **không phải đường Dubins ngắn nhất**:
tối ưu thật là **RLR**, rẻ hơn tới **14 %** (`d=75 m`: 484.3 → 419.3 m). Đường RLR
nằm **trọn ngoài luống**, hợp lệ, chỉ đòi **bờ sâu hơn** (~2.3ρ). Bảng phạt vì thế
bị thổi: `2.10× → 1.82×`, `1.31× → 1.15×`.

**⇒ Phát biểu `4ρ/3` là điều kiện ĐỦ (`⟸`), không phải cần và đủ. Bỏ dấu `⟺`.**
Đã ghi vào `p1-params.h` kèm cả ba hằng số.

---

## 8. Chạy lại

```bash
python3 tools/check_p1_isolation.py                 # luật cách ly
cd /home/user/ns3-dev && python3 ./ns3 build
./build/src/uav-sar/examples/ns3.46-uav-sar-p1-test-optimized [grid] [R_c] [seed]
```

Harness in ra, theo thứ tự: đối chiếu hex · Pha 0 (ô, CH, lớp, cây) · §0.2.1 so
ba quy tắc bầu trên 12 thế giới · T0 (`G(b)`, `θ`, `c_n`, cửa sổ vận hành) ·
Dubins tự kiểm · T1 ba phương án × ba cỡ đội, kèm khoảng cách Euclid–Dubins.
