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
