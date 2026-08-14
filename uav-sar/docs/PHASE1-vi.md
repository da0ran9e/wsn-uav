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
