# Hệ Phase 1 mới — cài đặt, kiểm chứng, kết quả

> Tài liệu của **hệ mới** trong `models/p1/`. Hệ cũ (`models/common/`,
> `models/application/`) không bị đụng tới và các số đo trong `STATUS.md`
> vẫn còn hiệu lực.
>
> Trạng thái: **toàn tuyến T0→T4 đã cài và kiểm**. `64 431` CHECK ở cấu hình
> mặc định, sạch trên 8 tổ hợp lưới/bán kính/hạt giống.

---

## 1. Vì sao phải dựng lại từ đầu

Lần cài đầu **chồng ý tưởng mới lên ý tưởng cũ**. Bảy chỗ chồng lấn cụ thể,
trong đó hai chỗ do chính lần cài đó tạo ra:

| # | Chồng lấn |
|---|---|
| C1 | Hai mô hình "có gì ở đây": `clue-field` (`clueQuality`) và `tier1-detect` (`a_n`) |
| C2 | Hai `kAlertThreshold` — **0.75** và **0.45**, khác đại lượng, khác thang, **cùng biên dịch** |
| C3 | Ba mô hình dữ liệu tham chiếu: 4 tầng ngữ nghĩa / `θ` bytes / "k tệp" |
| C4 | Hai cụm trưởng: `cell-grid` bầu theo **gần tâm** và dựng cây từ đó; lớp mới bầu theo **năng lực** nhưng **không dựng lại cây** |
| C5 | `node-capability` viết cho các chặng cũ `EVIDENCE/IDENTITY/SEEDING`, `Modality` bắt vít lên trên |
| C6 | Hai mô hình phủ: `lane-plan` + `gmc` phủ **vùng/nút** vs T1/T2 phục vụ **ô lớp A có trọng số** |
| C7 | `kCpuConfirmMin` — tham số hệ mới — nằm trong file hệ cũ |

**Kỷ luật không chặn được chồng lấn, nên nó thành phép kiểm.**
`tools/check_p1_isolation.py`: `models/p1/` chỉ được include header của chính nó
và thư viện chuẩn. Mọi thứ khác là FAIL.

Chỗ nào hệ mới cần thứ hệ cũ có → **bản sao riêng + phép kiểm hai bản khớp nhau**.
Bản sao **đã kiểm** thì an toàn; ký hiệu dùng chung mang **hai nghĩa** thì không.
Chỉ có một bản sao như thế — toán hex — đối chiếu với `cell-grid` trên **18 769 điểm**.

---

## 2. Tham số: một chỗ, có nhãn

`models/p1/p1-params.h`. Nhãn:

- `TODO(param)` — **bắt buộc** thay bằng số đo/quyết định trước khi báo cáo kết quả nào dựa vào nó
- `[derived]` — suy ra, không đặt tay
- `[design]` — quyết định, không phải số đo

**Ràng buộc thứ tự ngưỡng**, ghi thành ràng buộc chứ không phải nút chỉnh:

```
sàn nhiễu  <  kAlertScore  <  kConfirmScore  <  R_victim
   0.300       0.35            0.50             0.563
```

`R_victim` = điểm mà nút **gần nạn nhân nhất** đọc được khi đã cầm tham chiếu —
giá trị true-positive tốt nhất mà deployment có thể sinh ra. Harness tính nó từ
deployment thật và fail nếu chuỗi đứt.

---

## 3. Pha 0 — một lượt, đúng thứ tự

```
phân ô hex  →  bầu theo NĂNG LỰC (modality là bộ lọc CỨNG)  →  gán A/B/C
            →  dựng cây nội ô TỪ cụm trưởng đã bầu
```

Đây là chỗ sửa C4. Bầu vì một lý do rồi định tuyến từ cụm trưởng chọn vì lý do
khác thì mọi số đếm chặng sau đó **sai một lượng không ai đo**.

| lớp | điều kiện | hệ quả |
|---|---|---|
| **A** | có nút **đúng phương thức** và **đủ tính toán** chạy đối sánh | **tốn thời gian bay** |
| **B** | có nút chụp ảnh nhưng không phân biệt được | **không gửi tham chiếu** — mua gì cũng vô ích |
| **C** | chỉ cảm biến vô hướng | không đóng góp |

> **Diễn giải, có đánh dấu:** spec định nghĩa lớp A **chỉ theo phương thức**. Ở
> đây thêm "và đủ tính toán chạy đối sánh" (`kCpuMatchMin`), vì ô không chạy nổi
> đối sánh thì cũng không bao giờ phân biệt được — đúng lý do spec loại lớp B.
> Đặt `kCpuMatchMin = 0` thì hai định nghĩa trùng nhau.

`T_local` (bước 0.4) đã đo: **trung bình 49.5 s, tối đa 82.3 s** ở `R_c = 94 m`
cho `θ_full = 120 kB` tới **mọi** nút phân biệt được trong ô. Mô hình
store-and-forward nên đây là **cận trên**.

---

## 4. Tầng 1 — điều then chốt

> **Một TẦNG không phải một BỘ PHÁT HIỆN.** Cùng một nút, cùng một lần rút nhiễu,
> cho **hai** giá trị đọc: `scoreCue` (không tham chiếu) và `scoreFull` (đã cầm
> tham chiếu đầy đủ).

Rút nhiễu riêng cho hai tầng biến Tầng 2 thành **cú tung đồng xu thứ hai không
liên quan**, và luận điểm cả kiến trúc dựa vào — *giao dữ liệu là hành vi GỠ
NHẬP NHẰNG, không phải hành vi vận chuyển* — âm thầm hết được mô hình hoá.

Nhiễu rút **một lần mỗi nút mỗi run** — đó là một quan sát footage của chính nút
đó, không phải sự kiện theo gói. Rút theo mỗi lần đọc cho phép nút **bình quân
hoá giới hạn của chính nó**, biến ràng buộc cứng thành ràng buộc mềm.

### 4.1 Trần Fano áp cho VẬT, không phải cho Ô

| đo | kết quả |
|---|---|
| Tầng 1 trên bố trí thật (M=3) | **34.5 %** |
| trần `1/(M+1)` | 25.0 % |
| đối chứng: cảm biến giống hệt, vật đặt trên nút | 33.0 % — **vẫn trên trần** |
| đối chứng + **một vật mỗi ô** | **25.5 %** ✓ |
| Tầng 2, tham chiếu đầy đủ | **88.8 %** |

Giả thuyết đầu của tôi (bất đối xứng do cảm biến không đồng nhất) **sai** — đối
chứng bác bỏ. Nguyên nhân thật: khi hai vật rơi **cùng một ô**, gọi tên ô đó là
đúng nếu **một trong hai** là thật, nên phân hoạch thô ăn điểm cao hơn trần
**mà không cần thêm thông tin nào**.

> **Trích `1/(M+1)` mà đo ở mức ô là thổi phồng Tầng 1 — ở đây 9.5 điểm phần trăm.**

### 4.2 Báo giả: LAN BIÊN, không phải nhiễu

Gán nhãn ground truth theo **bán kính đáp ứng** làm gần như mọi ô đều "có vật"
(15/16). Gán theo **hình học** rồi tách hai loại:

- **lan biên** — vật ở ô kề; báo động **đúng**, chỉ nhãn ô sai. Đây là **giới hạn
  phân giải của lớp ô** và là thứ Pha 2 phải trả tiền để gỡ.
- **nhiễu độc lập** — thứ bộ phát hiện tốt hơn sẽ khử.

Đo được: **toàn lan biên, không nhiễu độc lập**.

---

## 5. T0 → T4

| chặng | cách giải | kiểm chứng |
|---|---|---|
| **T0** `G(b)`, `θ` phân tầng, `c_n` giây | Simpson trên `p(d)` | `G(0)` Simpson **380.31 m** vs tổng chữ nhật độc lập **380.31 m** |
| **Dubins** | port từ bản Python đã kiểm; CCC **dựng hình học** | sai số điểm cuối **1.5e-12 m** / 4000 cặp, **cả 6 từ** đều xuất hiện |
| **T1** credit + split | cả hai chấm bằng **cùng** thước Dubins; **chân depot nằm trong** phép chia đôi | mọi ô được phục vụ đúng một lần |
| **T2** hướng mũi | **DP chính xác** cho thứ tự cố định; chỉ THỨ TỰ là heuristic | DP **1273.308 m** = brute force trên `6⁴` tổ hợp |
| **T3** hồ sơ tốc độ | **simplex hai pha, quy tắc Bland** | tối ưu đã biết chính xác; **240 000** mẫu ngẫu nhiên **không lần nào** thắng simplex |
| **T4** vòng lặp | chấp nhận/từ chối + **bước rút nửa** | chỉ kế hoạch **tự nhất quán** được nhận |

### 5.1 Vì sao KHÔNG dùng Noon–Bean

Giá trị của Noon–Bean là cho phép chĩa **bộ giải ATSP chính xác trưởng thành**
vào kết quả — mà môi trường này **không có** (không OR-Tools, không LKH, không
Concorde). Vậy ATSP vẫn phải giải bằng heuristic, Noon–Bean **không mua được gì**
mà vẫn tốn phình `n·h` nút cộng hằng big-M mà heuristic xử lý kém.

Thay vào đó **giữ phần chính xác thật sự chính xác**: với thứ tự ô **cố định**,
hướng mũi tối ưu tìm được bằng **quy hoạch động** trên `h` trạng thái —
chính xác, `O(n h²)`. Chỉ THỨ TỰ là heuristic. Xấp xỉ bị **nhốt vào một chỗ và
gọi tên**, thay vì trải khắp một phép biến đổi đã mất bảo đảm.

> Các cận `(6⅓+ε)` / `(7+ε)` cho rooted min-max cycle cover giả định đồ thị
> **metric**. Chi phí Dubins **không metric**. Thuật toán dùng được; **cận thì không**,
> và không được phát biểu.

### 5.2 Kết quả T1, T2

```
T1 phân vùng (15 ô lớp A)         T2 định tuyến
method            M  makespan     DP hướng mũi = brute force chính xác
credit (free)     2      312s      h sweep:  4→4799m  8→4503m  16→4456m  32→4438m
credit (contig)   2      326s      h=8 chỉ trên h=32 1.5%  →  h=8 là đủ
split             2      352s
credit (free)     3      214s      thứ tự: NN 4503m → 2-opt/Or-opt 2767m
split             3      232s               (ngắn hơn 38.5%)
```

### 5.3 Ràng buộc động học giữa T2 và T3

`ρ = v²/(g tan φ)` **phụ thuộc tốc độ**. T2 chốt hình học ở **một** bán kính, nên
để T3 đổi tốc độ **trên khúc lượn** là làm hỏng đường T2 đã lập. Tốc độ vì thế
**chỉ tự do trên đoạn thẳng**; khúc lượn ghim ở bán kính đã lập. Không có điều
này thì hai chặng **đúng riêng lẻ và sai khi ghép**.

Đo được: **34–47 % số đoạn bị ghim trên khúc lượn**.

### 5.4 Hai lỗi T4 do CHẠY mới thấy

**(a) Trừ liều của HỒ SƠ ĐÃ TỐI ƯU là vòng vo.** Hồ sơ được dựng để thoả đúng
những ô đó, nên **mọi ô trông như đã đủ**, demand bị ghi giảm, và sau vài vòng
planner **tự thuyết phục mình không bay gì cả**. Thứ T4 thật sự tìm là liều một ô
nhận **miễn phí** vì tình cờ nằm gần đường bay **vốn đã phải bay** — đó là tính
chất **hình học** của tuyến, đo ở tốc độ hành trình, và **không thể tự suy về 0**.

**(b) Vòng lặp dao động chu kỳ 2.** Bỏ ô → tuyến ngắn lại → chính ô đó hết được
phủ → quay lại. Đo được: `115 → 0 → 117 → 0 → 117 → 0`. Damping làm chậm dao động
chứ không khử.

Hai sửa:

1. **Phép kiểm hợp lệ.** Kế hoạch **tự nhất quán** khi *mọi ô nó từ chối thăm vẫn
   được tuyến nó thật sự dựng phủ đủ*. Vòng lặp không đạt điều đó **không phải kế
   hoạch tệ hơn — nó không phải kế hoạch**, và không đủ tư cách được trả về.
2. **Bước rút NỬA.** Kích thước tập nghỉ hưu chính là **độ dài bước**: bắt đầu ở
   "tất cả", **chia đôi** mỗi lần kế hoạch sinh ra không tự nhất quán, ưu tiên giữ
   ô thừa liều nhiều nhất.

Kết quả: `0–1 / 6` vòng hợp lệ → **`5 / 6`**.

```
iter  makespan   flight  ô thăm  nghỉ hưu  hợp lệ
0        115s     8873m      22        22   ✓
1          0s        0m       0         0   ✗ (bỏ tất, không phủ được 22 ô)
2        115s     8873m      22        11   ✓   ← bước chia đôi
3         88s     6579m      11        11   ✓   ← tốt nhất
4         89s     7307m      11        12   ✓
```

---

## 6. Hai phát hiện phải chuyển cho khâu duyệt tham số

### 6.1 Bộ tham số hiện tại KHÔNG chạy được

Một lượt bay ở tốc độ tối thiểu giao tối đa

```
λ_tx · G(0) / v_min  =  4000 × 380 / 18  =  84.5 kB     vs   θ_full = 120 kB
```

⇒ **mọi ô đã báo động đều phải lượn vòng**, và **T3 báo INFEASIBLE — đúng**.
Ngưỡng đo được: khả thi từ **θ × 0.50** trở xuống.

Ba cách nới, cần bạn chọn:

| nới | thành | hệ quả |
|---|---|---|
| `λ_tx` 4000 → **≥ 5680 B/s** | θ_max ≥ 120 kB | cần link budget ~45 kbps |
| `θ_full` 120 → **< 84.5 kB** | vừa khít | phải suy từ Chernoff |
| `v_min` giảm | ít tác dụng | giới hạn khí động |

### 6.2 Máy bay giao THỪA gấp bội

Ở kế hoạch cuối, tỉ lệ `liều nhận / θ` cao nhất là **25.6×**. Tổng phát trên toàn
tuyến `λ·L/v` lớn hơn nhu cầu của **bất kỳ ô đơn lẻ nào** nhiều lần, nên phần lớn
ô được phủ **miễn phí** và bài toán định tuyến **suy biến**.

> Bài toán định tuyến Phase 1 **chỉ có nghĩa khi bước hàng `h = 1.5 R_c` lớn so
> với tầm thu**. Nếu không, một lượt bay phục vụ cả vùng lân cận và không còn gì
> để tối ưu.
>
> Đây là **ràng buộc thứ hai trên `R_c`**, từ vật lý khác hẳn ràng buộc `R_c ≥ 4ρ/3`.
> Đo được: tỉ lệ ô nghỉ hưu giảm `12/15 → 16/22 → 7/11 → 4/8` khi `R_c` tăng
> `94 → 140 → 220 → 300 m`.

---

## 7. Sửa mệnh đề trung tâm

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
./build/src/uav-sar/examples/ns3.46-uav-sar-p1-plan-dump-optimized OUT [grid] [R_c] [M] [seed] [θscale]
python3 tools/make_p1_figures.py RUNDIR OUT.png "tiêu đề"
python3 tools/make_p1_viewer.py OUT.html "nhãn=RUNDIR" ...
```

| tệp | nội dung |
|---|---|
| `visualize/figures/p1-plan.png` | 4 bảng: lớp ô · Tầng 1 · đường bay theo tốc độ · vòng lặp T4 |
| `visualize/figures/p1-plan-m5.png` | cùng vùng, 5 máy bay |
| `visualize/figures/p1-plan-wide.png` | `R_c = 220 m` |
| `visualize/p1-replay.html` | **replay có chuyển động**, 5 cấu hình, ô sáng dần theo liều |
