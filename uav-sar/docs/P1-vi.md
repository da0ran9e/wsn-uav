# Hệ Phase 1 mới — cài đặt, kiểm chứng, kết quả

> Tài liệu của **hệ mới** trong `models/p1/`. Hệ cũ (`models/common/`,
> `models/application/`) không bị đụng tới và các số đo trong `STATUS.md`
> vẫn còn hiệu lực.
>
> Trạng thái: cài **đến hết T1 (chia vùng)** rồi dừng theo yêu cầu.
> `54 017` CHECK ở cấu hình mặc định, sạch trên 8 tổ hợp lưới/bán kính/hạt giống.

## 0. Thứ tự — và một lần sửa sai thứ tự

```
tập nút KHÔNG ĐỒNG NHẤT
   → chia cluster (ô lục giác) + bầu CH theo NĂNG LỰC
   → TẬP CH LÀM ĐẠI DIỆN để lập lịch bay
   → T0 nhu cầu θ  ·  T1 hai kiểu lập lịch          ══ ĐÃ CÀI ĐẾN ĐÂY ══
   → tập ĐƯỜNG BAY THÔ (T2)
   → TINH CHỈNH (T3 tốc độ, T4 vòng lặp)
   → UAV BAY & PHÁT dữ liệu tham chiếu
   → RỒI MỚI CÓ tập vị trí nghi vấn   ← đầu ra Pha 1, đầu vào Pha 2
```

**Bản cài đầu tiên đặt phát hiện SAI CHỖ.** Nó chạy Tầng 1 *trước* khi bay, lấy
tập nghi vấn `𝒟` và tiên nghiệm `ω_n` rồi phân tầng `θ` theo đó
(`n ∈ 𝒟 → θ_full`, `n ∉ 𝒟 → θ_hedge`). Tức là **lập kế hoạch bằng thông tin mà
chính chuyến bay mới sinh ra được**: lúc lập lịch chưa nút nào cầm tham chiếu,
nên chưa nút nào nói được ở đó có gì.

Đã sửa. Nay `BuildDemands()` **không nhận** kết quả cảm biến, `kThetaHedgeFrac`
bị xoá, và `θ` chỉ còn phụ thuộc **năng lực**:

$$\theta_n \;=\; \theta_{\text{full}} \,/\, I_n$$

Đây vẫn là một trọng số **suy ra từ triển khai** chứ không phải cho sẵn — vẫn là
thứ tách bài này khỏi min–max mTSP có trọng số thông thường — nhưng **hẹp hơn**
lời tuyên bố cũ ("tiên nghiệm đo được từ chính mạng"), và phải viết đúng như thế.

**Giá của việc sửa** (θ×0.60, 780 m, 3 máy bay, 5 hạt giống):

| | biết `𝒟` trước (SAI) | không biết (ĐÚNG) |
|---|---|---|
| tìm được kế hoạch | 4/5 hạt | 2/5 hạt |
| makespan | ~90 s | ~118 s |
| số ô phải thăm | 12–17 | 21 (tất cả lớp A) |

Biết trước tập nghi vấn **đáng giá thật** — nhưng nó là thông tin **chưa tồn tại**
ở thời điểm lập lịch, nên không được dùng. Con số trên là **giá của tính trung
thực**, và nếu sau này có kênh phụ thu báo cáo trước chuyến bay thì đó là một
**mở rộng có thể đo được**, không phải mặc định.

## 1. Phạm vi hiện tại

Cài **đến hết T1 (chia vùng)** và dừng. T2/T3/T4 đã bị **gỡ khỏi build** —
chúng được dựng trên các giả định mà Bản 2 đã đổi, và giữ lại là lặp lại đúng
lỗi "ý tưởng cũ chồng lên ý tưởng mới". Chúng còn nguyên trong git tại thẻ
`p1-full-pipeline-before-rebuild`.

```
models/p1/
  p1-hex.h          bản sao ĐÃ KIỂM của toán hex (18 769 điểm)
  p1-types.h        SERVED / BARREN
  p1-params.h/.cc   mọi tham số, có nhãn TODO(param)
  p1-sensing.h/.cc  Node: camera (bộ lọc cứng), obs, cpu, rxBps
  p1-cells.h/.cc    Pha 0: phân ô → bầu CH → gán lớp → cây nội ô
  p1-demand.h/.cc   T0: G(b), θ_n, c_n
  p1-dubins.h/.cc   hình học Dubins — chỉ dùng để ĐO T1, không lái T1
  p1-partition.h/.cc T1: credit + split, hai biến thể
```

## 2. Ba nguyên lý, và chỗ chúng cắn vào code

| | nội dung | cài ở đâu |
|---|---|---|
| **N1** | không nghi vấn nào tồn tại trước chuyến bay | `BuildDemands()` **không nhận** kết quả cảm biến |
| **N2** | phải phục vụ **mọi** cụm; không đồng nhất nằm ở **lượng** θ | mọi ô `SERVED` đều có θ > 0 |
| **N3** | **CH là chủ thể đối sánh**, không có dữ liệu di chuyển trong cụm | camera là **bộ lọc cứng** khi bầu; **đã xoá** `T_local` |

`T_local` bị xoá hẳn: nó đo thời gian tham chiếu lan tới mọi thành viên đủ năng
lực (49.5 s trung bình) — một cơ chế mà **N3 nói là không tồn tại**.

## 3. §0.2.1 — bầu theo năng lực đáng giá bao nhiêu

Spec đánh dấu "chưa đo". Nay đo, **trên 12 thế giới** chứ không một hạt giống:

```
0.2.1 -- I_n cua CH YEU NHAT, 12 the gioi  (min / median / max)
  capability (thiet ke)  0.336 / 0.425 / 0.466
  centroid   (PECEE)     0.096 / 0.144 / 0.209
  random     (null)      0.105 / 0.146 / 0.166
  capability / centroid: 1.89x .. 4.81x, tot hon o 12/12 the gioi  -> DUOC XAC LAP
  capability / random  : 2.30x .. 3.80x                            -> DUOC XAC LAP
  centroid vs random: 0.144 vs 0.146 -- gan tam KHONG mang thong tin nang luc
```

Đo **CH yếu nhất**, không phải trung bình: ô đó mang `θ` lớn nhất nên đặt ra chi
phí phục vụ khó nhất của cả bài toán.

**Điểm sạch nhất để viết vào bài:** `centroid` ≈ `random`. Không phải "gần tâm là
proxy tồi cho năng lực" — mà là **nó không phải proxy gì cả**. Đó là lý do đổi
quy tắc bầu, phát biểu được bằng một con số.

> Hai lần đầu tôi báo số cho mục này đều **sai** và đã rút lại: lần một đọc từ
> **một hạt giống** (1.91×, không đại diện); lần hai chạy trên một `election`
> **bị lỗi** — sentinel `best = -1.0` trong khi CENTROID chấm bằng khoảng cách
> **âm**, nên mọi ứng viên xa tâm quá 1 m đều bị loại và có cấu hình không bầu
> được ai. Bảng trên là sau khi sửa.

## 4. T1 — thước đo, và giá của việc phân tầng

Bản 2 để T1 chấm bằng **Euclid** (động học là việc của T2, T4 khép vòng). Tôi cài
đúng thế, nhưng **đo luôn** cùng phân vùng đó bằng Dubins:

```
method                  M   makespan   spread  Dubins that      gap
credit (free)           2       799s     5.4%         811s     1.5%
credit (contiguous)     2       828s     5.0%         841s     1.6%
split                   2       814s     5.2%         826s     1.5%
credit (free)           3       585s     9.6%         595s     1.7%
credit (contiguous)     3       556s     9.8%         576s     3.5%
split                   3       568s    15.3%         574s     1.1%
credit (free)           4       451s     7.1%         457s     1.4%
credit (contiguous)     4       453s    16.3%         460s     1.6%
split                   4       449s    10.8%         458s     2.1%
```

**Khoảng cách chỉ 1.1–3.5 %.** Tôi đã cảnh báo rủi ro này (dự án từng trả giá vì
chấm bằng mét đường thẳng), nhưng ở đây **phân tầng của Bản 2 là đúng**: ước
lượng Euclid ở T1 gần như không làm lệch thứ hạng khối. Cả hai biến thể đều chấm
bằng **cùng một thước** nên không bên nào được ưu ái. Chân depot nằm **trong**
phép chia đôi ở cả hai.

## 5. Vì sao phải dựng lại từ đầu

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

## 6. Tham số: một chỗ, có nhãn

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

## 7. Pha 0 — một lượt, đúng thứ tự

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

## 8. Mô hình cảm biến — ĐẦU RA của Pha 1 (đã gỡ khỏi build)

`scoreCue` **không phải đầu vào lập lịch**. Nó là **đường cơ sở** để đo chuyến bay
mua được gì: mạng tự nói được đến đâu, so với nói được đến đâu sau khi có tham
chiếu. So sánh đó là một **kết quả**, và đó là công dụng duy nhất của nó.

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

## 9. Đã gỡ khỏi build

T2 (Dubins-GTSP), T3 (LP hồ sơ tốc độ), T4 (vòng lặp tinh chỉnh) và mô hình
cảm biến sau chuyến bay **đã gỡ**. Chúng chạy được và có kiểm, nhưng dựng trên
các giả định Bản 2 đã đổi (lớp A/B/C theo phương thức, `T_local`, `θ` chỉ theo
`obs`). Giữ lại là lặp lại đúng lỗi đã phải sửa một lần.

Khôi phục: `git show p1-full-pipeline-before-rebuild`.

Những kết quả đã đo của chúng vẫn đúng **với giả định lúc đó**, và ghi lại ở đây
để không phải tìm lại: DP hướng mũi = brute force chính xác; `h=8` chỉ trên
`h=32` 1.5 %; 2-opt/Or-opt ngắn hơn NN 38.2 %; simplex (cân tỉ lệ hàng +
Dantzig/Bland) không thua 240 000 mẫu ngẫu nhiên; T4 dao động chu kỳ 2 và cần
phép kiểm **tự nhất quán** cộng **bước rút chia đôi**.

## 10. Sửa mệnh đề trung tâm — VẪN CHƯA VÀO SPEC

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

## 11. Chạy lại

```bash
python3 tools/check_p1_isolation.py                 # luật cách ly
cd /home/user/ns3-dev && python3 ./ns3 build
./build/src/uav-sar/examples/ns3.46-uav-sar-p1-test-optimized [grid] [R_c] [seed]
```

Harness in ra, theo thứ tự: đối chiếu hex · Pha 0 (ô, CH, lớp, cây) · §0.2.1 so
ba quy tắc bầu trên 12 thế giới · T0 (`G(b)`, `θ`, `c_n`, cửa sổ vận hành) ·
Dubins tự kiểm · T1 ba phương án × ba cỡ đội, kèm khoảng cách Euclid–Dubins.
