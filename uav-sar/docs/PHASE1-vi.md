# Phase 1 — Quét sàng lọc bằng đội cánh cố định

> **Tình trạng tài liệu.** Đây là **thiết kế bài toán**, không phải kết quả đã đo
> trong ns-3. Mọi con số dưới đây đến từ mô hình **quy hoạch** (`tools/`), chạy
> độc lập với mô phỏng — các kế hoạch bay được chấm bằng **đúng luật dẫn đường**
> của mô phỏng (§5.0), nhưng **không** có vô tuyến, kênh truyền hay mặt đất.
> Chúng nói *nên kỳ vọng gì*, chưa nói *hệ thật cho ra gì*. §7 liệt kê việc phải
> làm để biến chúng thành kết quả.
>
> Kiến trúc hai pha **đã có sẵn trong mã** (đội FAST + đội DATA). Cái đổi ở đây là
> **bài báo đặt vấn đề quanh cái gì và đo cái gì**, không phải đổi hệ thống.

---

## 1. Đặt vấn đề — vì sao tách hai pha

Nhiệm vụ SAR trong rừng có hai việc **khác hẳn nhau về kinh tế**:

| | Phase 1 — sàng lọc | Phase 2 — xác nhận |
|---|---|---|
| đội bay | cánh cố định, 2 chiếc | cánh quay, 2 chiếc |
| phủ | **toàn bộ vùng** | **từng điểm** |
| chi phí mỗi đơn vị | rẻ (bay liên tục, không dừng) | đắt (bay tới, treo, rót dữ liệu) |
| đầu ra | **danh sách ứng viên có xếp hạng** | toạ độ **đã xác nhận** |
| sai lầm đắt nhất | **bỏ sót** nạn nhân (không thể sửa) | **phục vụ nhầm** (chỉ tốn thời gian) |

Đây chính là cấu trúc **bộ phân loại tầng** (cascade): tầng một rẻ và **thiên về
nhạy**, tầng hai đắt và **thiên về đặc hiệu**. Điểm mấu chốt: **Phase 1 không được
phép cố gắng chính xác.** Việc của nó là **không bỏ sót** với chi phí thấp, rồi
chuyển một tập ứng viên **đủ nhỏ** cho Phase 2.

Vì thế câu hỏi trung tâm của Phase 1 **không phải** "phủ hết vùng nhanh nhất bằng
cách nào", mà:

> **Bao lâu thì mặt đất tích được đủ dữ liệu tham chiếu để phân biệt được, và
> đường bay nào của một khung cánh cố định đạt tới đó sớm nhất?**

---

## 2. Vì sao đây KHÔNG phải coverage path planning cổ điển

Nếu Phase 1 chỉ là CPP cho cánh cố định thì không có gì để viết — boustrophedon,
Dubins TSP, spiral đều đã có từ lâu. Ba khác biệt cấu trúc khiến nó **không** phải
CPP:

### 2.1 Cảm biến **không nằm trên UAV**

UAV không phát hiện gì cả. Nó **rót các mảnh dữ liệu nhận dạng (cue) xuống nút mặt
đất**, và **nút mặt đất mới là bộ phát hiện**. "Phủ" ở đây không phải phủ vết cảm
biến — nó là **phủ truyền thông cho một quảng bá gieo mầm cho một bộ phát hiện
phân tán**.

### 2.2 Chất lượng phát hiện **tích luỹ liên tục**, không nhị phân

CPP cổ điển: một ô **đã phủ** hoặc **chưa phủ**. Ở đây, một nút phân biệt được
**tỉ lệ thuận với lượng dữ liệu nó giữ**. Bay qua nhanh hơn ⇒ nút nhận ít chunk
hơn ⇒ **phân biệt kém hơn**. Đây là biến liên tục, và nó gắn thẳng vào tốc độ bay.

### 2.3 Đầu ra là **tập ứng viên**, không phải bản đồ

Phase 1 thành công khi tập ứng viên có **recall cao** (mọi nạn nhân thật đều sinh
ra một ứng viên) và **precision đủ dùng** (Phase 2 không bị ngập). Đây là mục tiêu
**sàng lọc**, đo bằng ROC, không phải mục tiêu phủ.

---

## 3. Mô hình toán

### 3.1 Phơi sáng

UAV bay đường $p(t)$, quảng bá bán kính $R_c$. Nút $i$ ở $s_i$ phơi sáng:

$$\tau_i \;=\; \int_0^T \mathbb{1}\big[\,\|p(t)-s_i\| \le R_c\,\big]\,dt$$

Với một luống thẳng, tốc độ $v$, nút cách trục luống $y$:

$$\tau_i(y) \;=\; \frac{2\sqrt{R_c^2-y^2}}{v}$$

**Nút xấu nhất là nút nằm ngay dưới trục luống** — nó có dây cung dài nhất
($2R_c$) nhưng **không nhận được gì từ hai luống kề** (khoảng cách luống bằng
đúng $R_c$). Đây là ràng buộc quyết định, không phải nút ở rìa.

### 3.2 Tích luỹ và phân biệt

Cue phát ở tốc độ $\rho$ chunk/s, bộ cue có $N$ chunk. Tỉ lệ dữ liệu nút giữ sau
$k$ lượt quét:

$$C_i \;=\; \min\!\Big(1,\; \frac{k\,\tau_i\,\rho}{N}\Big)$$

Nút phân biệt được nạn nhân với vật gây nhầm khi $C_i \ge C^*$. **$C^*$ là núm
thiết kế trung tâm của Phase 1** — nó nối tầng vật lý (bao nhiêu byte) với tầng
quyết định (phân biệt được hay không).

### 3.3 Gộp bằng chứng và tuyên ứng viên

Trong ô $c$, gộp bằng noisy-OR (đã cài):

$$E_c \;=\; 1-\prod_{i\in c}\,(1-e_i), \qquad
e_i = \text{bằng chứng nút } i \text{ đo được với } C_i \text{ dữ liệu}$$

Ô tuyên một ứng viên khi $E_c \ge \theta$. Tập ứng viên
$\mathcal{C}(\theta)=\{c : E_c\ge\theta\}$ là **thứ duy nhất Phase 1 giao cho
Phase 2**.

### 3.4 Số lượt quét cần thiết

Nút xấu nhất cần:

$$k^*(v) \;=\; \Big\lceil \frac{N\,C^*}{2R_c\,\rho\,/\,v} \Big\rceil
\;=\; \Big\lceil \frac{N\,C^*\,v}{2R_c\,\rho} \Big\rceil$$

Đây là **hàm bậc thang theo $v$**, và cái bậc thang đó là nguồn của toàn bộ kết
quả ở §5.

---

## 4. Bài toán tối ưu — ba phát biểu, xếp theo mức đáng làm

### P1-A. Thứ tự luống như Dubins TSP *(đã giải chính xác — lợi 15 %)*

Phát biểu tự nhiên nhất, và là cái tôi nghĩ tới đầu tiên. Mỗi luống $\ell$ có hai
cấu hình bay (đông→tây, tây→đông). Chọn hoán vị $\pi$ và hướng $d$:

$$\min_{\pi,\,d}\;\; \sum_{\ell} L_\ell \;+\; \sum_{k} \mathrm{Dub}_R\big(q^{\text{out}}_{\pi(k)},\, q^{\text{in}}_{\pi(k+1)}\big)$$

với $\mathrm{Dub}_R$ là khoảng cách Dubins bán kính $R = v^2/(g\tan\phi)$. Đây là
**ATSP bất đối xứng có hai chế độ mỗi thành phố**. Ở quy mô vận hành (11 luống)
nó **giải được CHÍNH XÁC** bằng Held–Karp — $2^{11}\times 22$ trạng thái — nên
báo được **tối ưu thật**, không phải đầu ra của một heuristic.

**Đã giải. Kết quả: rút 14.5 % quãng đường và 14.4 % thời gian một lượt quét**,
ở cùng độ phủ 100 %. Chi tiết ở §5.1. Đây là **đòn bẩy thật, nhưng là đòn bẩy
nhỏ hơn** so với P1-B, và hai cái **cộng được với nhau**.

### P1-B. Chọn tốc độ bay *(đòn bẩy thật)*

Tốc độ chi phối **hai thứ cùng lúc**, và cả hai đều **xấu đi khi bay nhanh**:

$$R(v)=\frac{v^2}{g\tan\phi} \quad (\text{bậc hai}), \qquad
\tau(v)=\frac{2R_c}{v} \quad (\text{nghịch đảo})$$

Bay nhanh ⇒ bán kính lượn phình theo **bình phương** ⇒ chi phí quay đầu tăng;
**đồng thời** phơi sáng giảm ⇒ cần thêm lượt quét. Chỉ có **một** thứ tốt lên là
số mét trên giây.

$$\boxed{\;\min_{v}\;\; T_{\text{screen}}(v) \;=\; k^*(v)\;\cdot\;\frac{L_{\text{plan}}\big(R(v)\big)}{v}\;}$$

Trong chế độ một lượt quét, ngưỡng đóng lại thành dạng đóng:

$$v^* \;=\; \frac{2\,R_c\,\rho}{N\,C^*}$$

Đây là **phát biểu tôi đề nghị làm bài toán chính của Phase 1**. Nó ngắn, nó suy
ra được, nó **đảo ngược một trực giác** ("đội scout thì phải bay nhanh"), và nó
**chỉ tồn tại vì cảm biến nằm dưới mặt đất** — với một scout mang cảm biến trên
mình thì $\tau$ không liên quan gì tới phân biệt, và bài toán biến mất.

### P1-C. Điểm vận hành sàng lọc — giao diện với Phase 2

Ngưỡng $\theta$ trượt trên đường ROC:

$$\max_{\theta}\;\; \Pr\big[\text{mọi nạn nhân sinh ứng viên}\big]
\quad\text{s.t.}\quad \mathbb{E}\big[\,|\mathcal{C}(\theta)|\,\big]\;\le\;K_{\max}$$

$K_{\max}$ **không tự do** — nó do Phase 2 quyết định: với $m$ cánh quay, ngân
sách thời gian $T_2$ và lịch phục vụ tối ưu (bài toán thợ sửa chữa lưu động, §17
của báo cáo tiến độ), $K_{\max}$ là số điểm phục vụ hết được trong $T_2$.

**Đây là chỗ hai pha khớp vào nhau**, và là lý do tách pha có nội dung toán học
chứ không chỉ là cách kể chuyện: Phase 1 tối ưu **có ràng buộc do Phase 2 đặt ra**.

---

## 5. Kết quả

Hình học vận hành: vùng 460 × 460 m, $R_c=50$ m, khoảng cách luống 50 m
(11 luống), $\phi=45°$, cue $N=30$ chunk @ $\rho=5$ chunk/s.

> Cài đặt Dubins **tự kiểm chứng**: mọi độ dài dạng đóng được tích phân ngược lại
> và khẳng định điểm cuối trùng cấu hình yêu cầu. Bản đầu tiên của tệp này **sai
> ở từ LRL** (lệch 208 m) trong khi năm từ kia đúng tuyệt đối — một dạng đóng
> Dubins chép sai dấu vẫn trả về số **trông hợp lý**. Sai số hiện tại: 5.6 × 10⁻¹³ m.

### 5.0 Cách chấm điểm — và hai lần chấm sai trước đó

Hai bản trước của mục này chấm điểm bằng **mô hình hình học**, và **sai theo hai
hướng ngược nhau**, cả hai đều cho ra số trông hợp lý:

| cách chấm | sai ở đâu | kết luận sai nó tạo ra |
|---|---|---|
| quay đầu ≈ chạy thẳng ra + sang ngang + chạy vào | **bỏ qua độ cong** của cú đảo chiều | Dubins chỉ lợi 2.6 % |
| Dubins qua waypoint quay đầu, **có áp hướng** | máy bay **không bị buộc** tới waypoint theo một hướng cho trước | Dubins lợi 47 % |

Cách chấm hiện tại: **bay cả hai kế hoạch qua đúng luật dẫn đường của mô phỏng**
(`ControlTick` + `FlightController::Step`) — lái liên tục về waypoint, giới hạn
tốc độ lượn $g\tan\phi/v$, nhận waypoint khi tới gần **hoặc** khi đã ngang qua.
Hai kế hoạch vì thế **chỉ khác nhau ở danh sách waypoint**, đúng thứ đang so.

Kèm hai khẳng định chặn: **mọi waypoint phải tới nơi**, và **độ phủ phải > 99 %**
— một kế hoạch ngắn hơn mà bỏ sót nút thì **chưa sàng lọc** những nút đó.

### 5.1 P1-A — thứ tự luống: lợi 14.5 %

| kế hoạch (v = 25 m/s) | độ dài | một lượt | trong vùng | phủ |
|---|---:|---:|---:|---:|
| tuần tự + quay đầu ngoài vùng (đang chạy) | 8.85 km | 354 s | 47.4 % | 100 % |
| **Dubins tối ưu chính xác** (Held–Karp) | **7.56 km** | **303 s** | **52.6 %** | 100 % |

Lời giải tối ưu chọn thứ tự **nhảy luống** (1, 4, 8, 5, 2, 0, 3, 7, 10, 6, 9) để
mỗi cú đảo chiều có sẵn chỗ, nên **không cần waypoint quay đầu ngoài vùng nào cả**
— và vẫn phủ đủ 100 %.

### 5.2 P1-B — tốc độ: đòn bẩy thật

| kế hoạch | $v$ | $R$ | độ dài | một lượt | trong vùng | lượt | $T_{\text{screen}}$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| boustrophedon *(đang chạy)* | 25 | 64 m | 8.85 km | 354 s | 47.4 % | 2 | **708 s** |
| Dubins | 25 | 64 m | 7.56 km | 303 s | 52.6 % | 2 | 605 s |
| boustrophedon | 16 | 26 m | 6.74 km | 422 s | 68.2 % | 1 | 422 s |
| **Dubins** | **16** | **26 m** | **6.16 km** | **385 s** | **71.8 %** | **1** | **385 s** |

**Hai đòn bẩy cộng được với nhau: 708 s → 385 s, nhanh hơn 46 %** — trong đó thứ
tự luống đóng góp ~15 % và tốc độ đóng góp phần còn lại.

Cơ chế của phần tốc độ: ở 16 m/s, $R = 26$ m **nhỏ hơn khoảng cách luống 50 m**,
nên đảo chiều nằm gọn trong vùng (phần bay trong vùng 47.4 % → 68.2 %); **đồng
thời** nút xấu nhất nhận đủ 30 chunk trong **một** lượt thay vì hai.

**Bay nhanh còn hỏng cả độ phủ.** Ở $v \ge 28$ m/s bán kính lượn vượt quá thứ hình
học luống hấp thụ được, máy bay bắt đầu cắt góc và **bỏ sót nút**: boustrophedon
phủ 99.1 % ở 28 m/s và **98.6 % ở 32 m/s**. Nên "bay nhanh để quét nhanh" thua ở
**cả ba** mặt: chi phí quay đầu, phơi sáng, và độ phủ.

### 5.3 Kết quả có phụ thuộc giả định $C^*=1$ không?

Không. Quét $C^*$:

| $C^*$ | $v^*$ | $T$ tại $v^*$ | $T$ tại 25 m/s | lợi |
|---:|---:|---:|---:|---:|
| 0.50 | 33.0 m/s | 297 s | 324 s | 8.3 % |
| 0.60 | 27.5 m/s | 312 s | 324 s | 3.7 % |
| 0.70 | 23.5 m/s | 333 s | 648 s | **48.6 %** |
| 0.80 | 20.5 m/s | 358 s | 648 s | **44.7 %** |
| 0.90 | 18.5 m/s | 382 s | 648 s | **41.1 %** |
| 1.00 | 16.5 m/s | 412 s | 648 s | **36.4 %** |

Với $C^* \ge 0.7$ lợi ích nằm ở **36–49 %** và $v^*$ bám sát dạng đóng
$v^*=2R_c\rho/(NC^*)$. Chỉ khi $C^*\le 0.6$ — tức nút phân biệt được với **dưới
60 %** bộ dữ liệu — thì điểm vận hành hiện tại mới gần tối ưu.

**Nên $C^*$ là đại lượng phải ĐO, không phải giả định.** Nó quyết định điểm vận
hành của cả Phase 1.

---

## 6. Đóng góp phát biểu thế nào — và KHÔNG được phát biểu thế nào

**Không được viết:**

- *"Chúng tôi đề xuất quy hoạch đường bay Dubins cho UAV cánh cố định."* Đã có từ
  Savla–Frazzoli–Bullo, Isaacs–Hespanha. Ở đây nó là **công cụ** cho 15 % — phần
  còn lại, và phần mới, đến từ ràng buộc phơi sáng.
- *"Chúng tôi tìm kiếm nhiều mục tiêu bằng nhiều UAV."* §19e của báo cáo tiến độ
  đã ghi: đây **không** phải khoảng trống.
- *"Bay nhanh hơn thì quét nhanh hơn."* Số liệu nói ngược lại.

**Được viết:**

> Khi việc phát hiện được **uỷ nhiệm xuống mạng cảm biến mặt đất**, tốc độ bay của
> UAV scout không còn là biến thông lượng thuần tuý: nó **đồng thời** đặt bán kính
> lượn (bậc hai) và lượng dữ liệu tham chiếu mỗi nút tích được (nghịch đảo). Hệ quả
> là thời gian sàng lọc có **cực tiểu bên trong**, ở tốc độ **thấp hơn hẳn** tốc độ
> khung máy bay cho phép — và cực tiểu này **không tồn tại** trong quy hoạch phủ cổ
> điển, nơi vết cảm biến là nhị phân và độc lập với tốc độ.

Đây là phát biểu **kiểm chứng được**, **suy ra được dạng đóng**, và **gắn chặt
với kiến trúc** — nó biến mất nếu cảm biến đặt trên UAV.

---

## 7. Việc phải làm — biến mô hình thành kết quả

Mọi số ở §5 là **mô hình quy hoạch**. Để đưa vào bài báo:

| # | việc | cổng kiểm chứng |
|---|---|---|
| 1 | **Đo $C^*$ thật** trong ns-3: quét ngưỡng, tìm tỉ lệ dữ liệu tối thiểu để nút phân biệt nạn nhân/vật gây nhầm | đường cong phân biệt vs $C_i$, $N \ge 120$ |
| 2 | **Quét `--fastSpeed`** {14, 16, 18, 20, 25, 30} và đo $T_{\text{screen}}$ thật | cực tiểu bên trong có xuất hiện? ở đâu? |
| 3 | Cột mới `candidatesFound` / `candidatesResolved` / `timeToScreen_s` | thay script đo ngoài (đã sai 2 lần) |
| 4 | Đo **recall / precision của Phase 1** riêng khỏi kết cục Phase 2 | ROC theo $\theta$ |
| 5 | Nối $K_{\max}$ với năng lực Phase 2 | đường cong đánh đổi $\theta$ ↔ tải Phase 2 |
| 6 | Kiểm chứng $R(v)$ thật trong mô phỏng khớp $v^2/(g\tan\phi)$ | khúc gấp quá khả năng ≈ 0 ở mọi $v$ |

**Cảnh báo phương pháp:** quét tốc độ đổi **cả kinematics lẫn phơi sáng cùng lúc**
— đúng loại nhầm lẫn mà `SIM-SPEC` §8 đã cảnh báo với `gridSpacing` (đổi bốn thứ
một lúc). Muốn **quy** hiệu ứng cho từng nguyên nhân thì phải có ablation tách
đôi: giữ $R$ cố định mà đổi $v$ (không thực tế về vật lý nhưng hợp lệ như một
ablation), và giữ $v$ cố định mà đổi $\rho$.

---

## 8. Quan hệ với phần còn lại của dự án

- **Không đụng chiều B** (tiếp sức payload). Chiều B thuộc Phase 2 — nó nói về
  phân phát *bộ dữ liệu đầy đủ*, còn Phase 1 chỉ rải *cue*.
- **P10 (thợ sửa chữa lưu động)** vẫn là bài toán của Phase 2, và nay có vai trò
  rõ hơn: nó **định nghĩa $K_{\max}$** cho P1-C.
- **`closed-loop` vẫn là comparator hỏng** (mới đo: 1 điểm nhắm duy nhất, 0
  CONFIRM). Với khung Phase 1, nó lại càng phải sửa: nếu bài báo nói về **sàng
  lọc**, thì baseline phải **sàng lọc được**.
- **Baseline ngoài cho Phase 1** nên là quy hoạch phủ cánh cố định kinh điển
  (boustrophedon + Dubins TSP ở tốc độ tối đa) — tức **chính P1-A ở $v$ lớn nhất**.
  Đó là điều một kỹ sư sẽ làm nếu không biết về ràng buộc phơi sáng, và khoảng
  cách giữa nó với $v^*$ **chính là đóng góp**, đo bằng cùng một thước.

---

## 9. Tái lập

```bash
python3 uav-sar/tools/dubins_lanes.py                              # Dubins + phơi sáng
python3 uav-sar/tools/phase1_plans.py docs/visualize/phase1-plans.html   # bảng + hình
```

| tệp | vai trò |
|---|---|
| `tools/dubins_lanes.py` | hình học Dubins + Held–Karp, **tự kiểm chứng bằng tích phân ngược** |
| `tools/fly_sim.py` | luật dẫn đường của mô phỏng, dùng để **chấm điểm** mọi kế hoạch |
| `tools/phase1_plans.py` | so sánh + sinh `docs/visualize/phase1-plans.html` |

Không phụ thuộc gì ngoài thư viện chuẩn. Dạng đóng Dubins được kiểm trước khi in
bất kỳ số nào; nếu sai, script **dừng** chứ không in số sai. Mọi kế hoạch bị chặn
bởi hai khẳng định: tới đủ waypoint, và phủ > 99 %.

---

## 10. Đã cài vào ns-3 (2026-08-30) — chia luống, và cổng pha

§5 là mô hình quy hoạch. Mục này là **kết quả ns-3 thật**, 8 hạt giống mỗi nhánh,
`--gridSize=24 --numUav=4 --victimCount=2 --clutterCount=4`.

### 10.1 Vấn đề đo được trước khi sửa

Mỗi UAV FAST được cấp **một nửa danh sách nút**, rồi **tự dựng lưới luống** trên
hộp bao của nửa đó. Không ai sở hữu luống nào, nên hai UAV đặt luống cách nhau
dưới một bán kính quảng bá ở hai bên đường ranh:

| | giá trị |
|---|---:|
| nút được **cả hai** UAV phủ | **143/576 = 24.8 %** |
| lệch tải giữa hai UAV | 69.4 % ↔ 55.2 % (**lệch 14.2 điểm**) |

Rải cue cho một nút đã giữ đúng những chunk đó **không mua được gì** — nó là
airtime và giờ bay tiêu vào việc đã làm rồi.

### 10.2 Sửa: một bộ luống cho cả vùng, mỗi luống một chủ

`models/common/lane-plan.{h,cc}`. Ba phần:

1. **Một bộ luống toàn vùng** (`BuildFieldLanes`) — giống hệt thứ `BuildMission()`
   sinh ra cho cả vùng, nên hành vi phủ **của từng luống** không đổi.
2. **Sở hữu độc quyền** (`LanesFor`) — khối luống **liền kề**, không xen kẽ. Xen kẽ
   cho mỗi UAV khoảng cách luống rộng hơn (lượn rẻ hơn) nhưng đặt **mọi** luống
   cạnh luống của bạn — đúng thứ trùng lặp đang muốn bỏ. Liền kề chỉ để lại **một**
   đường ranh.
3. **Thứ tự Dubins chính xác** (`OrderLanes`) — Held–Karp trên (luống × hướng).
   Ở 5–6 luống mỗi UAV nó rẻ, nên là **tối ưu thật**, không phải heuristic.

**Kiểm chứng cài đặt.** Hàm Dubins C++ được so với bản Python đã tự kiểm chứng ở
§5 trên 400 cặp cấu hình ngẫu nhiên: lệch tối đa **1.0 × 10⁻⁷ m**. Và chạy với
`--lanePlan=0 --phaseGate=0` tái lập lô cũ **trùng từng ô, 0/442 ô sai** — mã mới
là no-op thật khi tắt.

### 10.3 Kết quả — nhánh B

| chỉ số | A (cũ) | **B (chia luống)** |
|---|---:|---:|
| nút phủ hai lần | 24.8 % | **17.0 %** |
| lệch tải | 14.2 % | **3.8 %** |
| quãng đường FAST | 11.1 km | **9.5 km (−14.4 %)** |
| phủ nút (FAST) | 99.8 % | 99.3 % |
| phủ nút (mọi UAV) | 100.0 % | 100.0 % |
| nạn nhân định vị | 15/16 | **16/16** |
| toạ độ sai người | 0 | 0 |
| ứng viên được phục vụ | 67/70 | **73/73 = 100 %** |
| thời gian tới toạ độ | 251 s | **211 s** |
| năng lượng | 236 kJ | 237 kJ |

**−14.4 % quãng đường FAST khớp gần như chính xác con số −14.5 % mà mô hình quy
hoạch §5.1 dự đoán** — mô hình và ns-3 nói cùng một thứ, đo bằng hai đường độc lập.

17 % còn lại là **nội tại**: khoảng cách luống bằng bán kính quảng bá, nên hai
luống hai bên đường ranh **buộc** phải phủ chồng một dải rộng đúng một khoảng
luống. Với chia liền kề thì một đường ranh là ít nhất có thể.

### 10.4 Cổng pha — tách được, nhưng đắt

`--phaseGate=1`: đội cánh quay **không nhận việc** cho tới khi nghe đủ thông báo
"đã quét xong" từ mọi UAV FAST (CLAIM role 3), có **dự phòng bằng bầu trời im
lặng** và một hạn chót fail-open.

Ba lỗi phải sửa trước khi nó thật sự là một cổng:

1. **Cổng đặt sai chỗ.** Chặn tuần tra và chặn rải cue **không** tách được pha: UAV
   đang chờ vẫn nghe RCLAIM, vẫn nhận việc, vẫn bay đi giao. Đo được: giao hàng ở
   t = 41–128 s trong khi cổng mở ở t = 189 s. **Nhận việc mới là "bắt đầu"**, nên
   cổng phải nằm ở `ConsiderTasks()`.
2. **Cổng fail-closed.** Chỉ dựa vào một quảng bá CLAIM(3) không lặp: 1 hạt giống
   trong 5 **không mở cổng nào**, một hạt khác chỉ mở 1 trong 2. Sửa: FAST lặp lại
   thông báo, và **bầu trời im lặng cũng mở cổng** — từ chỗ chờ, "trời im" chính
   là âm thanh của "đội quét đã xong".
3. **Guard `module=` không bắt được bản dựng cũ** khi `.so` bị thay **trong lúc**
   tiến trình đang chạy: tiến trình cũ stat lại tệp mới và đóng dấu nhãn mới. Ba
   run rác đã lọt qua đúng đường này. Đây là một lỗ mới của guard, chưa vá.

| chỉ số | B | **C (+cổng pha)** |
|---|---:|---:|
| chỉ số FAST | — | **y hệt B** (cổng không đụng đội FAST) |
| nạn nhân định vị | 16/16 | **14/16** |
| năng lượng | 237 kJ | **321 kJ (+36 %)** |
| thời gian tới toạ độ | 211 s | **285 s (+35 %)** |

### 10.5 Chờ dưới đất — **hỏng hẳn**, và nó chỉ ra một ràng buộc thật

Phương án hiển nhiên để bỏ +36 % năng lượng: chờ **dưới đất**, không tốn công
treo. Đo được (`--phaseGateGround=1`), 4/4 hạt giống:

> **0 lần giao hàng, 0/8 nạn nhân định vị được.**

Hai nguyên nhân, cả hai đều là ràng buộc thật của kiến trúc hai pha:

1. **Thông báo không tới nơi.** Từ mặt đất ở góc BS, đội DATA nghe được **0/2**
   thông báo quét-xong phát trên vùng. Phải cho UAV FAST **phát lại khi hạ cánh về
   BS** thì cổng mới mở — nghĩa là *phải bay về mới bàn giao được*.
2. **Danh sách ứng viên hết hạn trước khi Phase 2 bắt đầu.** Ngay cả khi cổng mở
   (t = 245 s), hoạt động cuối cùng của mặt đất đã là t = 191.7 s: các thủ lĩnh đã
   dùng hết `kMaxRetargets` và **ngừng phát SUMMON**. Không còn lời mời nào để trả
   lời.

**Đây là kết quả có giá trị, không phải một thất bại cần giấu.** Nó phát biểu được
thành một ràng buộc thiết kế: *tách pha nghiêm ngặt đòi hỏi danh sách ứng viên phải
được **lưu giữ và quảng bá lại**, hoặc Phase 2 phải chồng lấn Phase 1.* Quảng bá
của mặt đất có **tuổi thọ hữu hạn** ($\text{kMaxRetargets} \times
\text{kRetargetAfterS}$), và tuổi thọ đó là thứ quyết định cổng pha có khả thi hay
không.

### 10.6 Mặc định để lại

| cờ | mặc định | lý do |
|---|---|---|
| `--lanePlan` | **bật** | thắng ở mọi chỉ số, không đánh đổi |
| `--phaseGate` | **tắt** | là **dụng cụ đo** để quy công cho Phase 1, không phải chế độ vận hành tốt hơn |
| `--phaseGateGround` | tắt | hỏng hẳn cho tới khi ứng viên được lưu giữ |

Cổng pha vẫn có giá trị: bật nó lên thì **tập ứng viên chứng minh được là do đội
cánh cố định sinh ra một mình** (đội DATA không rải cue nào). Đó đúng là thứ cần
cho việc quy đóng góp của Phase 1 — chỉ là nó phải được gọi tên là dụng cụ đo, kèm
giá của nó.

---

## 11. Quét theo NĂNG LỰC, không theo nút (2026-08-31)

Cho tới đây "phủ" nghĩa là **mọi nút phải nằm trong bán kính quảng bá của đường
bay**. Điều đó chỉ đúng nếu mọi nút như nhau. Chúng không như nhau, và khi chúng
khác nhau thì "phủ vùng" và "phủ thứ đáng phủ" là **hai câu hỏi khác nhau**.

### 11.1 Ba năng lực, ba cổng khác nhau

`models/common/node-capability.{h,cc}`. Mỗi nút mang ba chỉ số **hỏng độc lập**,
và mỗi cái chặn một **giai đoạn khác nhau** của dây chuyền sàng lọc:

| năng lực | chặn cái gì | mô hình |
|---|---|---|
| **quan sát** | **BẰNG CHỨNG** | **tầm hiệu dụng**, không phải độ lợi |
| **tính toán** | **DANH TÍNH** | dưới `kCpuConfirmMin` thì không chạy được bộ khớp |
| **giao tiếp** | **TỐC ĐỘ GIEO** | **chu kỳ thức**, không phải bitrate |

Cả ba lựa chọn mô hình đều là **kết quả của một lần đo sai trước đó**:

**(a) Quan sát: tầm, không phải độ lợi.** Bản đầu nhân thẳng số đo với `obs`. Kết
quả: **0/2 nạn nhân**, dù việc giao dữ liệu chạy hoàn hảo — vì phép nhân đẩy
*đồng loạt* mọi nút xuống dưới ngưỡng xác nhận. Trường là
$q = Q_{\max} e^{-d/L}$; cho `obs` co **tầm** $L$ rồi khử $d$:

$$q' \;=\; Q_{\max}\left(\frac{q}{Q_{\max}}\right)^{1/\text{obs}}$$

Không cần biết $d$, và `obs = 1` tái lập trường **đúng nguyên văn**. Một camera
tốt ở xa và một camera kém ở gần nay đọc ra cùng một số — đó mới là vật lý.

**(b) Giao tiếp: chu kỳ thức, không phải bitrate.** Cue chỉ chào ~4 kbps trong khi
mọi radio 802.15.4 chạy 250 kbps, nên **bitrate không bao giờ là ràng buộc** — mô
hình dựng trên nó chỉ là đồ trang trí. Thứ thật sự ràng buộc trong WSN là **nút rẻ
thì ngủ**. Nút thức 40 % thời gian mất 60 % của một lượt bay ngang.

**(c) Và nó chỉ chặn CUE.** Bản đầu chặn cả `FULL`, và cũng ra **0/2 nạn nhân**:
nút của chính nạn nhân (duty 0.39) **không bao giờ nhận đủ bộ tham chiếu**, nên
không bao giờ xác nhận được. Lý do đúng: radio ngủ thua một nguồn **không đoán
trước và không xin phát lại được** — đúng là chiếc scout lướt qua ở 25 m/s. Nó
**không** thua chiếc DATA đỗ trên đầu 20 giây, vì đồng bộ với nguồn bền là đúng
việc chu kỳ thức sinh ra để làm. **Năng lực radio thuộc về Phase 1**, và đó cũng
là chỗ người lập đường bay làm được gì đó với nó.

### 11.2 Phủ theo ô: chọn luống theo năng lực biên trên mỗi mét

`--cellCoverTarget`: chọn luống cho tới khi **mọi ô** đạt một tỉ lệ năng lực sàng
lọc **của chính nó**, tham lam theo *năng lực biên trên mỗi mét bay*. Nút không có
camera **không đáng bay qua** — và đó chính là câu mà cách phủ cũ không nói được.

### 11.3 Chia việc cân cả NĂNG LỰC lẫn CÔNG BAY

`BalancedSplit`: quy hoạch động **chính xác** trên các điểm cắt liền kề, tối thiểu
hoá **khối tệ nhất** theo tổ hợp có trọng số của lệch công bay và lệch năng lực.
Hai lần sửa, cả hai đều do đo mà ra:

1. **Công bay phải là thứ BAY THẬT, không phải số mét luống.** Chấm bằng độ dài
   luống để lại quãng đường thực **lệch 56 %** trong khi hàm mục tiêu tin là đều —
   khối xa căn cứ ở góc phải trả một đoạn transit mà hàm mục tiêu không nhìn thấy.
   Tính cả transit và chi phí quay đầu: nhánh đồng nhất từ **17.9 % → 1.7 %**.
2. **`SubdivideLanes`.** Chọn theo ô chỉ để lại 4–5 luống (5 luống đã phủ kín vùng
   ở bán kính danh nghĩa), mà một phép chia **không thể mịn hơn số mảnh nó được
   cho**. Cắt dọc luống thành 3 mảnh mỗi UAV.

### 11.4 Kết quả — 8 hạt giống mỗi dòng, **một bản dựng**

| cấu hình | UAV | FAST | năng lực phủ | lệch năng lực | lệch công bay | km FAST | nạn nhân | kJ | t toạ độ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| đồng nhất, phủ nút | 4 | 2 | 99.5 % | 3.4 % | 1.7 % | 9.5 | **13/16** | 239 | 228 s |
| dị biệt, phủ nút | 4 | 2 | 99.4 % | 4.2 % | 5.8 % | 9.5 | 9/16 | 211 | 211 s |
| dị biệt, **phủ ô** | 4 | 2 | 95.2 % | 5.7 % | 9.3 % | **7.0** | 9/16 | 195 | 168 s |
| dị biệt, phủ nút | 6 | 3 | 100.0 % | 41.0 % | 19.2 % | 10.2 | 11/16 | 269 | 158 s |
| **dị biệt, phủ ô** | **6** | **3** | 94.4 % | 27.9 % | 12.3 % | **7.7** | **13/16** | 294 | **123 s** |
| dị biệt, phủ nút | 8 | 4 | 99.9 % | 35.9 % | 18.9 % | 14.2 | 10/16 | 367 | 156 s |
| dị biệt, phủ ô | 8 | 4 | 98.3 % | 37.7 % | 20.7 % | 10.1 | 9/16 | 511 | 122 s |
| dị biệt, phủ nút | 10 | 5 | 99.2 % | 51.1 % | 34.8 % | 15.0 | 10/16 | 706 | 127 s |
| dị biệt, phủ ô | 10 | 5 | 97.6 % | 44.6 % | 30.6 % | 11.5 | 9/16 | 522 | 102 s |

**Ba điều đọc được:**

**(1) Phủ theo ô rẻ hơn và không mất nạn nhân.** Ở 2 UAV: **−26 % quãng đường**
(9.5 → 7.0 km), **−20 % thời gian tới toạ độ** (211 → 168 s), −8 % năng lượng, đổi
lấy **−4.2 điểm** năng lực được phủ — và **cùng 9/16 nạn nhân**. Không bay qua một
nút không camera thì không mất gì cả, đúng như giả thiết.

**(2) Dị biệt hoá đắt, và đó là kết quả chứ không phải lỗi.** Cùng đường bay, chỉ
đổi phần cứng mặt đất: **13/16 → 9/16 nạn nhân (−31 %)**. Đây là con số nói rằng
mọi kết quả trước đây đo trên một mặt đất **lý tưởng hoá**.

**(3) Thêm UAV KHÔNG đơn điệu tốt lên.** Thời gian tới toạ độ giảm 168 → 123 s khi
lên 3 UAV cánh cố định, rồi **đứng yên** (122, 102 s) trong khi năng lượng
**tăng gấp 2.7 lần** (195 → 522 kJ). **Điểm vận hành tốt nhất đo được là 3 UAV
cánh cố định với phủ theo ô**: 13/16 nạn nhân, 123 s, 294 kJ.

### 11.5 Chưa xong — cân bằng vỡ khi đội bay lớn

Lệch năng lực đi từ **5.7 % (2 UAV) lên 44.6 % (5 UAV)**; lệch công bay từ 9.3 %
lên 30.6 %. Đây **không** phải hiện vật đo: quãng đường thực từng chiếc ở 5 UAV là
2.74 / 2.75 / 2.94 / 3.05 / 3.62 km.

Nguyên nhân đã khoanh được: `blockEffort` ước lượng transit bằng **2 × khoảng cách
tới đầu luống GẦN nhất**. Với khối hẹp ở xa, ước lượng đó **hụt** — phải là
$d(\text{BS}, \text{gần nhất}) + d(\text{BS}, \text{xa nhất})$. Chưa sửa: campaign
đang chạy trên một bản dựng và luật §12 của `SIM-SPEC` cấm dựng lại giữa chừng.

**Việc tiếp theo, theo thứ tự:** (1) sửa ước lượng transit và đo lại thang đội bay;
(2) tách **năng lực đã lập kế hoạch** khỏi **năng lực đo được** (transit chung làm
nhiễu phép quy công ở đội bay lớn); (3) `cellCoverTarget` bão hoà ở ≥ 0.5 vì 5
luống đã phủ kín vùng — muốn đường cong đánh đổi thật thì phải quét **bán kính
quảng bá hiệu dụng**, không phải quét chỉ tiêu.

---

## 12. Đường bay thích nghi thế nào theo tham số (2026-09-01)

Quét hai núm, 4 hạt giống mỗi cấu hình, **một bản dựng**
(`module=1788261584,898456`), 3 UAV cánh cố định, phủ theo ô. Hình ở
`docs/visualize/figures/`.

### 12.1 Spacing: kế hoạch thích nghi mạnh

| spacing | vùng | km FAST | năng lực phủ | lệch | kJ | t toạ độ | nạn nhân |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 m | 460 m | **7.7** | 94.0 % | 11.8 % | 244 | **129 s** | **7/8** |
| 25 m | 575 m | 9.7 | 93.1 % | 23.9 % | 436 | 153 s | 4/8 |
| 30 m | 690 m | 12.9 | 93.6 % | 16.5 % | 488 | 187 s | 5/8 |
| 35 m | 805 m | **14.4** | 91.1 % | 15.4 % | 569 | **221 s** | **2/8** |

Kế hoạch **giữ đúng lời hứa của nó** — năng lực được phủ đứng yên ở 91–94 % qua
toàn dải — nhưng nhiệm vụ **sập**: quãng đường +87 %, thời gian +71 %, nạn nhân
7/8 → 2/8. Vì đội bay không đổi trong khi diện tích tăng gấp 3.

> **Cảnh báo (SIM-SPEC §8):** tăng `gridSpacing` ở cùng `gridSize` làm **diện tích
> tăng VÀ mật độ giảm cùng lúc**. Không được quy hiệu ứng trên cho riêng mật độ.

### 12.2 Trọng số ưu tiên nút: **trơ** ở vùng hiện tại — và lý do đáng ghi

Thêm `--capPriorityExp`: người lập kế hoạch chấm một nút bằng
$(\text{quan sát} \times \text{tính toán})^{E}$. $E=0$ coi mọi nút **có camera**
như nhau; $E=3$ bám các nút mạnh nhất và bỏ vùng yếu. Nút không camera vẫn đáng
**0** ở mọi mức — đó là sự thật về phần cứng, không phải sở thích.

Ở vùng 460 m nó **không đổi được gì**: $E=0$ và $E=3$ cho quỹ đạo **trùng từng
byte**, quãng đường từng chiếc y hệt (2.45 / 2.47 / 2.77 km).

Đây **không phải lỗi cài đặt**. Kiểm bằng bộ chọn chạy độc lập, với **ô lục giác
thật**, quét cả chỉ tiêu 0.2–0.9 và mũ 0–3: **luôn ra 5 luống / 2.3 km**. Số học
nói tại sao:

$$5 \text{ luống} \times 2R_c\,(100\ \text{m}) \;=\; 500\ \text{m} \;\ge\; 460\ \text{m}$$

**Tập luống tối thiểu bị hình học ép cứng.** Khi mọi ô đều phải được gieo, và năm
luống đã phủ kín vùng, thì **không còn tự do nào để ưu tiên**. Núm ưu tiên chỉ có
chỗ hành động khi **vùng đủ lớn so với vệt quét**.

### 12.3 Cùng núm đó, vùng 690 m: có tác dụng

| mũ ưu tiên | km | năng lực phủ | lệch | kJ | nạn nhân |
|---:|---:|---:|---:|---:|---:|
| 0 | 13.2 | 93.4 % | 15.1 % | 498 | 2/8 |
| 1 | 13.1 | 94.1 % | 14.3 % | 506 | 4/8 |
| 3 | **12.9** | 93.4 % | **21.9 %** | **395** | **5/8** |

Ở đây kế hoạch **đổi thật** (thấy rõ trên hình): mũ 3 bay ít hơn, tốn **ít năng
lượng hơn 21 %**, và tìm được nhiều nạn nhân hơn — nhưng **cân bằng xấu đi**
(15.1 % → 21.9 %), vì bám các nút mạnh nghĩa là phải tới những **chỗ cụ thể**
chứ không quét đều.

> **Đây là tín hiệu, chưa phải kết quả.** $n = 4$ hạt giống, và 2/8 → 5/8 nạn nhân
> hoàn toàn có thể là nhiễu. Luật $N \ge 120$ của `STATUS.md` vẫn áp dụng.

### 12.4 Kết luận vận hành

1. **Ở cấu hình đang chạy (460 m), chỉ có spacing/diện tích là núm thật.** Ưu tiên
   năng lực và cả `cellCoverTarget` đều **bão hoà** — vùng quá nhỏ so với bán kính
   quảng bá 50 m.
2. **Muốn nghiên cứu quy hoạch có ý nghĩa thì phải chạy ở vùng ≥ 690 m**, hoặc
   giảm bán kính quảng bá hiệu dụng. Nếu không, mọi thuật toán quy hoạch đều cho
   **cùng một câu trả lời** và bài báo không có gì để so.
3. Ở vùng lớn, ưu tiên năng lực **đổi bay lấy cân bằng**: ít bay hơn, ít năng lượng
   hơn, nhưng tải lệch hơn — một đánh đổi thật, cần $N \ge 120$ để chốt.

### 12.5 Hình và replay

| tệp | nội dung |
|---|---|
| `figures/adapt-spacing.png` | 4 vùng từ 460 → 805 m, đường bay thích nghi |
| `figures/adapt-priority.png` | mũ 0–3 ở 460 m — **bốn hình giống hệt nhau**, đó là kết quả |
| `figures/adapt-priority-bigfield.png` | cùng mũ đó ở 690 m — kế hoạch đổi thật |
| `figures/adapt-curves.png` | đường cong km / năng lực phủ / thời gian theo cả hai núm |
| `visualize/replay-3d-capability.html` | **replay 3D có chuyển động**, 3 cấu hình đội bay |
