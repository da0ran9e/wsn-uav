# Báo cáo tiến độ — các thuật toán và cơ chế đã cài đặt

**Giai đoạn:** 2026-08-08 → 2026-08-11 · **Nhánh:** `claude/document-review-xslwgg`

Tài liệu này mô tả **cái gì đã được cài, tại sao, và công thức của nó**. Viết cho
người đọc lần đầu: mỗi mục có một đoạn giải thích bằng lời, rồi một đoạn công thức
khi có thể viết được thành công thức.

Số liệu trích trong tài liệu đều đo ở điểm vận hành **24×24 nút (460×460 m), 4 UAV
(2 FAST + 2 DATA), 2 nạn nhân thật + 4 vật gây nhầm, chân trời 500 s, 8 hạt giống**,
mỗi bảng so sánh chạy trên **một bản dựng duy nhất**.

> **Cảnh báo về mức tin cậy.** N = 8 hạt giống chỉ đủ để nói **hướng** và để kiểm
> chứng cơ chế. Quy tắc của dự án (`STATUS.md` §5) vẫn là **N ≥ 120** cho bất kỳ
> con số nào đưa vào bài báo. Không con số nào ở đây được coi là kết quả cuối.

---

## Phần I — Mô hình

### 1. Bài toán

Một vùng rừng $\mathcal{A}$ có lưới cảm biến tĩnh. Trong vùng có $V$ **nạn nhân
thật** và $M$ **vật gây nhầm** — những vật thể *thật sự giống* dữ liệu tham chiếu
(người khác mặc cùng mẫu áo, chính đội cứu hộ, một chiếc áo bị vứt lại). Đội UAV
phải tìm ra nạn nhân và đưa **toạ độ đã xác nhận** về trạm gốc.

Điểm mấu chốt: vật gây nhầm **không phải nhiễu cảm biến**. Nút báo cao ở cạnh nó
đang báo **đúng** — thế giới mơ hồ, không phải cảm biến hỏng. Sự khác biệt này
quan trọng vì nhiễu giảm được bằng cách quan sát lâu hơn, còn mơ hồ thì không.

### 2. Cảm biến hai tầng — trục chính của thiết kế

Chất lượng khớp của nút $i$ **phụ thuộc lượng dữ liệu tham chiếu nó đang giữ**.
Với mảnh gợi ý (cue) nhỏ, một chiếc áo cùng màu là khớp; với đủ bộ tham chiếu,
nút tự phân biệt được.

Gọi $C_i \in [0,1]$ là **tỉ lệ dữ liệu tham chiếu** nút $i$ đã nhận, $g(d)$ là đáp
ứng không gian của bộ phát hiện theo khoảng cách, $s_m$ là độ tương đồng của vật
gây nhầm thứ $m$:

$$q_i(C_i) \;=\; \max\Big(\max_{v \in \mathcal{V}} g(\lVert p_i - v \rVert),\;\;
\max_{m} s_m\,(1 - C_i)\,g(\lVert p_i - c_m \rVert)\Big)$$

Số hạng nạn nhân **không** bị $C_i$ làm suy giảm; số hạng vật gây nhầm thì có. Đó
là toàn bộ khác biệt hình thức giữa "nạn nhân" và "vật gây nhầm", và nó sinh ra
hai nghĩa vụ khác nhau: **vật gây nhầm phải bị LOẠI, nạn nhân phải được PHỤC VỤ**.

Số đo được mang nhiễu **phụ thuộc tín hiệu** (nút không có tín hiệu thì đọc gần 0,
không thể xác nhận nhầm — đúng theo cấu trúc, không nhờ chỉnh ngưỡng):

$$\hat q_i = \mathrm{clip}_{[0,1]}\big(q_i + \sigma (q_i + q_0)\,\varepsilon_i\big),
\qquad \varepsilon_i \sim \mathcal{N}(0,1),\; q_0 = 0.05$$

**Bài học đắt nhất của giai đoạn này.** Trọng số trộn $C_i$ ban đầu được cài bằng
`TargetProfile::Confidence` — xác suất hợp $1 - \prod(1-p_j)$ trên các mảnh đang
giữ. Mảnh cue là **7 % số byte** nhưng cho **0.926** trên thước đo đó, nên nút vừa
nhận cue đã được coi là biết 92.6 %. Hệ quả: trục mơ hồ **vô hiệu hoàn toàn** —
$M=0$ và $M=4$ cho kết quả **giống hệt nhau đến từng byte ở 11/12 hạt giống**. Sửa
lại thành tỉ lệ byte thật:

$$C_i = \frac{\sum_{f} \min\!\big(1, |\text{chunk nhận được}_f| / n_f\big)\, b_f}{\sum_f b_f}$$

với $b_f$ là kích thước mảnh $f$ và $n_f$ số chunk của nó. Sau khi sửa, $M=0$
không đổi một cột nào (đúng: không có vật gây nhầm thì trọng số không thể có tác
dụng) còn $M=4$ đổi hoàn toàn.

---

## Phần II — Hạ tầng hợp tác mặt đất

### 3. Lưới ô lục giác và cây trong ô

Nút được gom thành ô lục giác bán kính 80 m. **Lãnh đạo ô** là nút gần trọng tâm
ô nhất; trong ô dựng cây BFS trên các liên kết thật.

Tầm liên kết mặt đất **không đặt tay** mà suy từ link budget, để hạ tầng không giả
định những liên kết mà tầng vật lý không kham nổi:

$$d_{\text{G2G}} = 10^{(P_{tx} - S - L_0)/(10 n)} \approx 37.2 \text{ m}$$

### 4. Tổng hợp bằng chứng trong ô — noisy-OR

Nút vượt ngưỡng hợp tác gửi **RPT** lên cây tới lãnh đạo, kèm **toạ độ GPS của
chính nó**. Lãnh đạo gộp bằng công thức hợp xác suất:

$$E_{\text{cell}} = 1 - \prod_{i \in \text{cell}} (1 - e_i),
\qquad e_i = C_i \cdot \hat q_i$$

Dùng noisy-OR chứ không dùng trung bình vì các nút quan sát **cùng một** vật thể
từ các vị trí khác nhau: hai nút yếu cùng chỉ về một chỗ phải mạnh hơn một nút
yếu đơn lẻ.

### 5. Chia sẻ xuyên ô

Lãnh đạo phát **SHARE** flood qua biên ô, mang **hai** con số: tổng hợp của ô
(để so sức mạnh giữa các ô) và **đỉnh đơn lẻ** — nút mạnh nhất cùng vị trí của nó.

Phải mang cả hai vì chúng không so sánh được với nhau: tổng hợp là hợp xác suất
nên **luôn ≥** mọi thành viên, nếu đem so với một nút đơn lẻ của mình thì lần nào
ô hàng xóm cũng thắng. Chỉ **đỉnh** mới so được với thành viên của mình.

### 6. Bầu cử phân tán — backoff theo bằng chứng

Ô vượt ngưỡng báo động lên lịch phát **SUMMON** sau một khoảng chờ **tỉ lệ nghịch
với bằng chứng**, nên ô mạnh nhất nói trước; ai nghe thấy tuyên bố của ô khác thì
đứng xuống. Không có bộ não trung tâm, chỉ có thứ nghe được trên radio.

$$T_{\text{fire}} = \max\big(t_{\text{quiet}},\, t_{\min}\big)
+ \underbrace{\beta\,(1 - E_{\text{cell}})}_{\text{backoff}} + \mathcal{U}(0,\delta)$$

với $\beta = 0.6$ s. Cửa sổ quan sát là **thích nghi**: $t_{\text{quiet}}$ là thời
điểm bằng chứng của ô **ngừng tăng** trong 8 s — điều kiện mà cửa sổ đồng hồ cố
định chỉ là một xấp xỉ. Lưới lớn thì bằng chứng về lâu hơn nên quyết định tự động
hoãn lâu hơn, mà không nút nào biết lưới lớn cỡ nào.

### 7. Hai ràng buộc không gian

**Tầm nhắm** — lãnh đạo chỉ được nhắm trong bán kính $R_{\text{aim}} = 160$ m
quanh tâm ô của mình (ô mình + vành kề). Không có ràng buộc này thì mọi lãnh đạo
đều nhận đỉnh bằng chứng toàn cục và mọi ứng viên sập về một điểm.

**Phạm vi đứng xuống** — chỉ đứng xuống trước tuyên bố **về cùng một chỗ**:

$$\text{đứng xuống} \iff \exists\, a \in \mathcal{A}_{\text{claimed}} :\;
\lVert a - \hat a_{\text{mine}} \rVert \le R_{\text{elect}} = 150 \text{ m}$$

**Lỗi tinh vi đã sửa:** trước đây quyết định này được **chốt ngay khi nhận** tuyên
bố. Nhưng flood RCLAIM lan khắp vùng trong vài mili-giây, tức **trước khi** hầu
hết các ô có bằng chứng gì, và một ô chưa có điểm nhắm thì đứng xuống **vô điều
kiện và vĩnh viễn**. Đo được: **10 ô trải khắp 300 m cùng đứng xuống trong 30 ms**.
Nghĩa là ràng buộc `electScope` trên thực tế **không ràng buộc gì**. Sửa: lưu tập
điểm đã bị chiếm $\mathcal{A}_{\text{claimed}}$, và **hoãn quyết định tới lúc bầu
cử**, khi đã có $\hat a_{\text{mine}}$ để so.

### 8. SUMMON là một hop — nên flood phải gánh việc thông báo

SUMMON là quảng bá **một hop** (~37 m). Lãnh đạo các ô cách nhau 63–156 m, nên nửa
"đứng xuống" của cuộc bầu cử **không thể tới nơi về mặt vật lý** — đó là lý do có
flood **RCLAIM**.

Vấn đề tương tự với bầu trời: một ứng viên chỉ tới được đội DATA nếu tình cờ có
FAST trong ~50 m đúng lúc lãnh đạo phát. Với đường bay cánh cố định các luống cách
nhau hàng trăm mét, chuyện đó hiếm. Đo được: **3 vùng triệu tập, bảng công việc
của DATA chỉ có 2**.

**Giải pháp:** dùng chính flood RCLAIM làm **tin tuyển việc**. Nó vốn được phát để
các ô khác đứng xuống, mang sẵn id vùng và toạ độ nhắm, và nó flood toàn vùng —
nên ở đâu có UAV thì ở đó có một nút đang chuyển tiếp nó. Đây là mặt phẳng hợp tác
mặt đất làm đúng việc nó sinh ra để làm: **bù cho một bầu trời không thể có mặt
khắp nơi**.

### 9. Đóng vòng: CONFIRM và REJECT

Nút nhận **đủ** bộ tham chiếu sẽ tự đối chiếu lần cuối:

$$\text{nút } i \text{ phát } \begin{cases}
\text{CONFIRM} & \hat q_i(C_i{=}1) \ge \theta_{\text{conf}} = 0.55 \\
\text{REJECT} & \text{ngược lại}
\end{cases}$$

REJECT là **nửa âm của việc đóng vòng**, và nó là thứ chỉ nút cầm đủ dữ liệu mới
nói được: mảnh cue mà một dương tính giả đã khớp thì không loại nó được, bộ đầy đủ
thì có. Nhờ đó UAV rời một vùng sai **bằng bằng chứng**, không phải bằng timeout.

Nút chỉ được **đóng dấu vùng** cho CONFIRM/REJECT của mình nếu nó **thật sự ở
trong** vùng đó ($\le 100$ m). Không có ràng buộc này, một nút cách hàng trăm mét
nhận vơ vùng vừa công bố và **đóng oan** một ứng viên chưa ai phục vụ.

---

## Phần III — Điều phối trên không

### 10. Phân chia công việc qua A2A — heuristic gán nhiệm vụ phân tán

Mỗi UAV DATA dựng **bảng công việc** chỉ từ thứ nghe được trên radio:

| nguồn | cho biết |
|---|---|
| A2A / RCLAIM | **có việc ở đâu** — $(\text{rid}, x, y)$ |
| CLAIM của đồng đội (role 0) | **ai đã nhận** |
| CLAIM role 2 | **việc nào đã xong** |
| CONFIRM / REJECT | **việc nào đã ngã ngũ** |

Luật chọn: **gần nhất trong số chưa ai nhận và chưa xong**, và khoảng chờ trước
khi tuyên bố **tỉ lệ với khoảng cách** — nên chiếc gần nhất nói trước, các chiếc
khác nghe thấy rồi chọn việc khác. Toàn bộ giao thức là **một loại thông điệp và
một luật**.

$$k^\star = \arg\min_{k \,\in\, \mathcal{K}_{\text{free}}} \lVert p_{\text{uav}} - a_k \rVert,
\qquad
T_{\text{claim}} = \tau \cdot \min\!\Big(1, \tfrac{\lVert p_{\text{uav}} - a_{k^\star}\rVert}{800}\Big)
+ \mathcal{U}(0,\delta)$$

Ba lớp bảo vệ, mỗi lớp sinh ra từ một lỗi đo được:

1. **Chống trùng theo KHÔNG GIAN.** Hai lãnh đạo ô kề nhau có thể triệu tập *cùng
   một chỗ* dưới hai id khác nhau. Một việc coi là đã nhận nếu đồng đội đã nhận
   **bất kỳ việc nào trong 150 m**. (Đo được trước khi sửa: hai UAV giao cách nhau
   **1 m**.)
2. **Phá hoà tất định.** Hai chiếc tuyên bố trong cùng mili-giây thì **id nhỏ hơn
   thắng** — và chiếc thua **không** được ghi đè quyền sở hữu của chính mình, nếu
   không cả hai cùng tưởng chiếc kia đang giữ và **không ai phục vụ cả**.
3. **Kiểm tra lúc tới nơi.** Đồng đội có thể chiếm chỗ trong hàng chục giây mình
   đang bay tới, nên phải kiểm lại ngay trước khi bắt đầu giao.

**Hiệu quả đo được:** thời gian giao hàng chồng lấn **4 454 s → 32 s → 0 s**.

### 11. Không phục vụ lặp — và một bài học về thước đo

Một chỗ đã nhận **trọn một lượt dwell** là **xong** cho toàn đội; chiếc vừa giao
phát `CLAIM role=2` để đồng đội đánh dấu theo. Ngoài ra, lãnh đạo nhắm lại chỉ
**dịch điểm hover**, không khởi động lại lượt giao 382 chunk.

$$\text{luot giao} / \text{diem}: \quad 2.40 \;\longrightarrow\; 1.08$$

**Bài học:** trong 13 lượt "lặp" còn lại sau lần sửa đầu, **12 lượt là nhãn sai
của phép đo** — UAV chỉ dịch điểm hover trong cùng vùng, không hề phục vụ lại.
Đây là **lần thứ ba** trong giai đoạn này thước đo mô tả sai hành vi (hai lần
trước: "số điểm khác nhau được phục vụ" và "chồng lấn"). Đã tách sự kiện
`deliver_move` khỏi `deliver_start`.

### 12. Quy hoạch đường bay cánh cố định

Bản đầu dùng **greedy maximum coverage**: mỗi bước chọn waypoint "lời" nhất kế
tiếp. Multirotor bay được; cánh cố định thì **không** — đo trên chính quỹ đạo đã
bay: **20.3 %** số mẫu đòi khúc gấp quá khả năng, bán kính nhỏ nhất **1–8 m** trong
khi cần 110 m.

Thay bằng **quét luống (boustrophedon)**: luống dọc cạnh dài của dải, khoảng cách
luống bằng bán kính phủ cue.

Bán kính lượn của một vòng nghiêng đều:

$$R = \frac{v^2}{g \tan\varphi}
\qquad\Rightarrow\qquad
\omega_{\max} = \frac{g \tan\varphi}{v}$$

**Quay đầu phải ra NGOÀI vùng.** Thử xen kẽ thứ tự luống để mỗi lần quay đầu có đủ
$2R$ — và số học tự bác bỏ: dải rộng 230 m, đường kính lượn 220 m, thứ tự
$[0,5,1,2,3,4]$ giãn được hai lần đầu (250 m, 200 m) rồi để ba lần cuối ở **50 m**.
Không thứ tự nào cứu được. Máy bay khảo sát thật **không quay đầu trong vùng khảo
sát**: mỗi lần đảo chiều là hai waypoint đặt cách đầu luống $1.2R$ về phía ngoài.

### 13. Mô hình bay có giới hạn tốc độ lượn

Sửa quy hoạch thôi không đủ, vì `FlightController::Turn()` **đặt hướng tức thì** —
không có ràng buộc khí động nào. Thêm giới hạn $\omega_{\max}$ (chỉ cho FAST; DATA
là rotary-wing nên giữ nguyên):

$$\psi_{t+\Delta t} = \psi_t + \mathrm{clip}\big(\psi_{\text{cmd}} - \psi_t,\;
\pm\,\omega_{\max}\Delta t\big)$$

**Riêng giới hạn này làm hỏng hoàn toàn nhiệm vụ**: 0 lượt giao ở cả 8 hạt giống,
và cả 8 có tổng góc đổi hướng **giống hệt 70°**. Lý do: hướng chỉ được ra lệnh
**lúc tới waypoint** — đúng khi quay tức thì, sai hẳn khi có giới hạn, vì cung
lượn ban đầu đẩy máy bay lệch rồi nó bay thẳng mãi. Phải thêm:

- **Dẫn đường liên tục** — ra lệnh hướng mỗi chu kỳ điều khiển, không chỉ lúc tới.
- **Chấp nhận waypoint khi bay ngang qua** — máy bay bán kính $R$ không phải lúc
  nào cũng lọt vào vòng chấp nhận, nó sẽ bay vòng vô hạn.

$$\text{tới nơi} \iff d_t \le r_{\text{acc}} \;\lor\; \big(d_t > d_{t-1} \land d_t < 2R\big)$$

### 14. Chi phí quay đầu — và đòn bẩy duy nhất

Sau khi sửa, **52.7 %** toàn bộ quãng đường FAST vẫn nằm ngoài vùng ở phần quay
đầu. Dời waypoint từ $2R$ về $1.2R$ **gần như không ăn thua** (53.1 % → 52.7 %),
vì chi phí nằm ở **cung lượn** chứ không ở vị trí waypoint:

$$L_{\text{turn}} \ge \pi R = \pi \frac{v^2}{g\tan\varphi}$$

Ở $\varphi = 30°$, $v = 25$ m/s: $R = 110$ m, $\pi R = 345$ m — so với 460 m luống
hữu ích, **năm lần** mỗi lượt quét. Vì $R$ chỉ phụ thuộc $v$ và $\varphi$, **góc
nghiêng là đòn bẩy duy nhất**. Nâng lên $45°$ cho $R = 64$ m, $\pi R = 200$ m.

### 15. Chính sách courier và cổng chờ phủ hết

**Courier.** Mang báo cáo về BS kết thúc lượt quét của chiếc đó. Với đúng 2 chiếc
FAST, mất một chiếc là **mất nửa độ phủ cue** — đo được: chiếc courier bay 2.1 km
và hạ cánh lúc $t=90$ s, chiếc kia bay 5.7 km tới $t=264$ s, độ phủ FAST 73 %. Luật
mới: **chỉ chiếc đã quét xong mới được ứng cử**. Độ phủ lên **100 %**.

**Cổng chờ.** UAV DATA **không được hạ cánh** khi FAST còn đang quét — vùng chưa
quét vẫn có thể sinh ứng viên mới. FAST phát `CLAIM role=3` khi hết kế hoạch; luật
*sky-quiet* (không nghe cue trong 45 s) giữ vai trò chặn trên để không treo.

Hệ quả có dạng rất rõ và không tránh được:

$$T_{\text{fix}} \;\ge\; T_{\text{sweep-complete}}$$

— không thể báo sớm hơn lúc được phép rời đi. Đo được: `tFix` bằng **đúng** thời
điểm quét xong, **giống hệt ở mọi hạt giống**.

### 16. Báo cáo mang nhiều toạ độ

Gói REPORT ban đầu mang **một** cặp toạ độ, và mỗi UAV giữ **một** fix. Đó là
**trần cứng của cả nhiệm vụ**: 2 UAV DATA thì tối đa 2 toạ độ về được mỗi lần
chạy, dù tìm ra bao nhiêu nạn nhân. Vì thế **mọi** thay đổi giữ đội bay ở lại phục
vụ thêm đều đổi thẳng bằng số nạn nhân báo được — 12/16 nạn nhân có UAV tới nơi mà
chỉ 8 fix về tới BS.

Định dạng mới `[type][flags][count] + count × [x:i16][y:i16]` = 19 B, tối đa 4
toạ độ, vẫn thừa sức trong trần 100 B của IEEE 802.15.4. Kết quả: **8/16 → 13/16**,
mọi chỉ số khác không đổi.

### 16a. Toạ độ báo về phải là **chỗ khớp**, không phải **chỗ nhắm**

Ba quy tắc, cùng giải một câu hỏi: *trong tất cả các toạ độ bay lượn trên sóng,
cái nào là câu trả lời?*

**(a) Aim thuộc về một vùng, không thuộc về cả bầu trời.** Một UAV FAST chuyển
tiếp `SUMMON` của **mọi** vùng nó bay qua. Nếu chỉ giữ **một** ô "aim đang chờ"
thì bất kỳ `CONFIRM` nào cũng thăng ô đó thành câu trả lời — kể cả `CONFIRM` của
một vùng hoàn toàn khác. Đo được: aim của một **vật gây nhầm** ở (380, 60) về tới
BS như một toạ độ đã xác nhận, chỉ vì vùng của **nạn nhân 2** xác nhận sau đó 3 s.
Aim nay giữ **theo vùng**; `CONFIRM`/`REJECT` của vùng $r$ chỉ động tới aim của
$r$.

**(b) Chỗ khớp tốt hơn chỗ nhắm.** Aim là **phỏng đoán của thủ lĩnh** từ bằng
chứng gộp. Còn một nút gửi `CONFIRM` là nút **giữ đủ bộ tham chiếu và vẫn khớp**,
nên nó chắc chắn nằm trong tầm cảm biến của vật thật. Vì thế `CONFIRM`/`REJECT`
mang thêm **toạ độ của chính nút gửi** (5 → 9 B, cùng sai số GPS như `RPT`), và
đó mới là thứ được báo về.

**(c) Mỗi nút khớp là một mẫu.** Quanh một nạn nhân thường có vài nút cùng khớp.
Lấy nút **đầu tiên nghe được** cho sai số trung vị 24.1 m trên lưới 20 m. Lấy
**trọng tâm** của tất cả — chúng đã có sẵn trên sóng, không tốn thêm gói nào:

$$\hat{p}_r=\frac{1}{|K_r|}\sum_{k\in K_r} p_k,\qquad
K_r=\{\text{nút gửi CONFIRM cho vùng } r\}$$

Kết quả cộng dồn, 8 hạt giống: **`wrongFixes` 7 → 0**, **nạn nhân định vị được
11/16 → 15/16**, sai số trung vị 24.1 → **15.5 m**, p90 28.3 → **24.9 m**.

Ở cấu hình trung thực `--victimOnNode=0` (nạn nhân **không** nằm đúng trên nút):
**16/16**, `wrongFixes` **0**, sai số trung vị **12.4 m**, p90 **18.0 m**. Con số
"0.0 m" của bản cũ là **hiện vật của lưới** — aim trùng đúng nút nạn nhân, tức hệ
thống đọc lại chỉ số nút nó vừa được cho, chứ không định vị gì.

---

## Phần IV — Các bài toán tối ưu đứng sau

### 17. P10 — lập lịch phục vụ đa ứng viên (độ trễ nhỏ nhất có trọng số)

Khi có $K$ điểm nghi vấn với trọng số tin cậy $w_k$, đội bay phải chọn **thứ tự
phục vụ**. Mục tiêu là tổng thời gian chờ có trọng số:

$$\min_{\pi} \; \sum_{k=1}^{K} w_{\pi(k)} \cdot t_{\pi(k)},
\qquad t_{\pi(k)} = \sum_{j \le k} \big(\tfrac{d(a_{\pi(j-1)}, a_{\pi(j)})}{v} + \tau_{\text{dwell}}\big)$$

Với trọng số bằng nhau đây đúng là **bài toán thợ sửa chữa lưu động** (traveling
repairman / minimum latency) — **NP-hard**, và **APX-hard** trên metric tổng quát.

Giai đoạn này bài toán ấy **hiện ra bằng số liệu chứ không còn là phát biểu suông**.
Ở 40×40 với 2 nạn nhân và 4 vật gây nhầm, mặt phẳng hợp tác định vị **cả hai nạn
nhân với sai số 0.0 m trong 72 giây** — nhưng **không có CONFIRM nào**: đội bay
phục vụ theo **thứ tự nghe thấy**, ứng viên đầu tiên là một vật gây nhầm và nó
chiếm mất chiếc DATA rảnh đầu tiên. **Gấp đôi đội bay không sửa được** (8 UAV: 4
divert, vẫn 0 CONFIRM, năng lượng gấp đôi).

Heuristic đang cài là **tham lam gần nhất, phân tán, có phá hoà** (§10).

### 18. Đánh đổi cứu-sớm ↔ quét-sạch

Một UAV đang giữ toạ độ đã xác nhận thì hoặc mang về ngay, hoặc phục vụ tiếp và
để toạ độ ngồi trên khung 15 m/s. Với đội bay nhỏ, **hai mục tiêu loại trừ nhau**:

| | `--fixFirst=1` | `--fixFirst=0` |
|---|---:|---:|
| ứng viên được phục vụ | 66 % | **100 %** |
| nạn nhân định vị được | **14/16** | 8/16 |
| thời gian tới toạ độ | **112 s** | 352 s |
| năng lượng | **218 kJ** | 383 kJ |

Vì thế nó là **một nhánh khai báo**, không phải một lựa chọn giấu trong bộ lập
lịch.

### 19. Trần nhận dạng

Với $M$ vật gây nhầm có độ tương đồng 1.0, **không thuật toán nào** đọc đại lượng
vô hướng này phân biệt được nạn nhân tốt hơn ngẫu nhiên:

$$\Pr[\text{chọn đúng}] \le \frac{1}{M+1}$$

Đây là **lỗi Bayes**, không phải cận Cramér–Rao. Ghi rõ vì bản thảo trước có nhắc
tới CRLB ở đúng chỗ này — và đó là một lỗi kỹ thuật thật: CRLB nói về *độ chính
xác của ước lượng*, còn ở đây vấn đề là *không phân biệt được đối tượng*.

---

## Phần IV-B — Khảo sát tài liệu đã thực hiện

Ghi lại vì phần này quyết định **đóng góp của bài được phát biểu thế nào**, và
nó đã ba lần buộc phải hạ giọng một tuyên bố.

> **Phạm vi:** vài lượt tìm kiếm có định hướng (8/2026), **không phải khảo sát hệ
> thống**. Đủ để định vị bài toán và tìm tổ tiên lý thuyết, **không đủ** để viết
> câu "chưa ai làm". Danh sách việc phải làm thêm ở §19d.

### 19a. Tổ tiên lý thuyết: tìm kiếm giữa các tiếp xúc giả

Phát hiện quan trọng nhất: **bài toán này là một bài toán kinh điển của lý thuyết
tìm kiếm**, chỉ là được đặt vào một hệ có mạng.

| công trình | liên quan |
|---|---|
| *Optimal Search Among False Contacts*, SIAM J. Appl. Math. ([doi:10.1137/0152099](https://doi.org/10.1137/0152099)) | mục tiêu nằm giữa các tiếp xúc giả phân phối Poisson; người tìm phải quyết định tại chỗ, và **chỉ phân biệt đúng với một xác suất cho trước** — **đúng cấu trúc** của `ClutterSource` |
| Koopman, *The Theory of Search* I–III, Oper. Res. 1956–57 | nền móng |
| Stone, Royset, Washburn, *Optimal Search for Moving Targets* | "tìm kiếm khi có mục tiêu giả" là **một chương chuẩn**, cùng optimal search-and-stop |

**Hệ quả cho cách viết bài:** không được trình bày yếu tố mơ hồ như một ý tưởng
mới. Cách vừa trung thực vừa mạnh hơn: *"đây là bài toán tìm kiếm giữa các tiếp
xúc giả của Koopman–Stone, lần đầu được đặt vào một hệ có ràng buộc năng lượng
bay và ràng buộc truyền thông mặt đất."*

### 19b. Đúng kịch bản "nhiều vật giống hệt nhau"

- **Identification and Association of Multiple Visually Identical Targets for
  Air–Ground Cooperative Systems**, *Drones* 9(9):612, 2025. Đúng bài toán: UAV
  nhìn xuống nhiều UGV **giống hệt nhau về ngoại hình**. Lời giải của họ **xác
  nhận** lập luận của ta: họ **từ bỏ ngoại hình** và chuyển sang liên kết theo
  hình học/topology (ma trận chiếu, quan hệ góc, hợp nhất Dempster–Shafer) — tức
  là thêm **một kênh thông tin khác**. Họ có chỉ số *False Positive Exclusion
  Rate* nhưng **không đưa ra cận khả phân biệt lý thuyết** — đó là chỗ ta khác họ
  (§19 trong báo cáo này: cận Bayes $1/(M+1)$).
- **Clothes-changing person Re-ID**: cả một dòng nghiên cứu lấy "người khác mặc
  cùng bộ đồ" làm **hard negative kinh điển**, có bộ dữ liệu chuyên dùng người
  mặc-một-bộ làm distractor. Dùng để **biện minh cho tiền đề** — giả định duy
  nhất bị vi phạm thường xuyên là chuyện cộng đồng thị giác đã ghi nhận, không
  phải ta bịa ra.
- **Radar False Alarm Suppression Based on Target Spatial Temporal Stationarity**,
  *Drones* 8(12):699, 2024: dùng khác biệt về **tính dừng không-thời gian** để
  triệt báo động giả. Đây đúng là cơ chế "nạn nhân bị thương thì bất động, người
  khoẻ mặc áo giống thì di chuyển" — **có tiền lệ trong radar**, và theo khảo sát
  này chưa thấy ai dùng cho SAR dựa trên mạng cảm biến mặt đất.

### 19c. Phía UAV-SAR / WSN: dương tính giả có, nhưng ở TẦNG KHÁC

- SAR dùng UAV **có** mô hình hoá FP, nhưng gần như luôn ở mức **bộ phát hiện**
  (tỉ lệ FP của bộ nhận dạng ảnh), không phải ở mức **thế giới có hai vật thật sự
  giống nhau**.
- Tìm kiếm Bayes cho WiSAR (SARBayes; *Multi-UAV SAR in Wilderness*; *SAREnv*)
  mô hình hoá **bỏ sót và báo động giả của cảm biến** trên bản đồ xác suất —
  nhưng mục tiêu vẫn **duy nhất**, không có vật thể thứ hai hợp lệ.
- WSN + UAV thu thập dữ liệu (tổng quan path planning, ACM CSUR 2022) tập trung
  năng lượng, vùng phủ, tuổi thọ mạng — **không xét nhập nhằng danh tính**.
- Định tuyến: **k-traveling repairman / minimum latency** có nền lý thuyết vững,
  nhưng chưa thấy bản kết hợp *trọng số xác suất hậu nghiệm + mục tiêu giả*.

### 19d. Khoảng trống — phát biểu thận trọng, và việc còn phải tra

Ba mảnh đều **đã tồn tại riêng lẻ**:

| mảnh | đã có ở đâu |
|---|---|
| tìm kiếm giữa tiếp xúc giả | lý thuyết tìm kiếm hải quân, 1950–90 |
| nhiều vật thể giống hệt | thị giác máy tính / air–ground, 2025 |
| UAV + WSN + năng lượng | dày đặc, nhưng **giả định mục tiêu duy nhất** |

**Chưa thấy** công trình ghép cả ba: mơ hồ danh tính **ở mức thế giới** trong hệ
UAV + mạng cảm biến hợp tác, kèm **cận khả phân biệt** báo song song với hiệu năng
hệ thống, và kèm **hệ quả lên chỉ số đo** (sai số thành hỗn hợp hai chế độ, phân
vị gộp mất nghĩa).

**Phải làm trước khi viết câu "chưa ai làm":**

1. Tra Scholar/IEEE Xplore: *"search among false contacts"*, *"false targets" +
   "search theory"*, *"data association ambiguity" + "search and rescue"*,
   *"identity ambiguity" + "multi-target search"*.
2. Lần ngược trích dẫn của mục SIAM — nhánh nào đã đưa nó sang robot/UAV?
3. Kiểm riêng mảng **multi-target tracking** (JPDA, MHT, PMBM). Họ xử lý nhập
   nhằng liên kết rất bài bản và phản biện **gần như chắc chắn** sẽ hỏi tại sao
   không dùng khung đó. Câu trả lời chuẩn bị sẵn: ta **không theo vết**, ta **phân
   bổ nỗ lực phục vụ**, và ràng buộc là năng lượng bay + truyền thông.
4. Lấy đủ thông tin thư mục của mục SIAM (trang trả 403, chưa có tác giả/năm).

### 19e. Nhiều mục tiêu THẬT: đây KHÔNG phải khoảng trống

Khi cân nhắc $V>1$ (nhiều nạn nhân thật), khảo sát cho kết quả **ngược với mong
muốn** và cần ghi lại đúng như vậy:

- Lý thuyết tìm kiếm đã có nhánh đa mục tiêu từ lâu (Stone 1975 → Stone–Royset–
  Washburn với ràng buộc di chuyển thực tế).
- **Bầy UAV tìm kiếm đa mục tiêu là một dòng rất đông**: land-coverage aware path
  planning cho bầy UAV SAR; tìm kiếm hợp tác trong môi trường động chưa biết;
  khung RL benchmark cho SAR bằng bầy UAV; bầy UAV cảm biến nhiệt; chuỗi nhiệm vụ
  tìm người bị thương ngoài trời.
- Chỉ số đa mục tiêu đã chuẩn hoá ở mảng theo vết: recall/precision, **false
  alarms per frame**, **MODA**.

**Kết luận trung thực:** "tìm nhiều mục tiêu bằng nhiều UAV" **không** phải khoảng
trống. Nếu dùng $V>1$ thì đóng góp **không** thể là "chúng tôi tìm nhiều mục
tiêu"; nó vẫn phải là **cơ chế nhận dạng dựa trên việc GIAO dữ liệu tham chiếu**
(mặt phẳng payload + REJECT) — thứ mà các công trình trên không có: chúng giả định
bộ phát hiện đặt **trên UAV**, còn ở đây **nút mặt đất tự nhận dạng sau khi được
cấp dữ liệu**. $V>1$ làm bối cảnh giàu hơn và làm P13 có nội dung, nhưng **không
tự nó tạo ra đóng góp**.

### 19f. Tham số lấy từ tài liệu

| tham số | nguồn |
|---|---|
| suy hao A2G, xác suất LoS | Al-Hourani; 3GPP TR 36.777 ($n \approx 2.2$ LoS) |
| suy hao tán lá | ITU-R P.833 |
| mô hình năng lượng rotary-wing | Zeng, Xu, Zhang, IEEE TWC 18(4):2329–2345, 2019 |
| baseline multicast VBS+TSP | Zeng, Xu, Zhang, TWC'18 |
| dải tốc độ khung máy bay | 80–110+ km/h cánh cố định, 40–60 km/h multirotor |

Chi tiết và mức tin cậy từng tham số (`[Lit✓]` / `[Lit dẫn xuất]` / `[Design]`)
ở `PARAMETERS.md`. Ghi chép khảo sát đầy đủ ở `RELATED-WORK-ambiguity.md`.

---

## Phần V — Phương pháp đo

### 20. Các chỉ số đã thêm

| chỉ số | đo cái gì | vì sao cần |
|---|---|---|
| `timeToFixAtBS_s` | lúc BS nhận toạ độ **đã xác nhận** đầu tiên | chỉ số chính $T$ |
| `victimsLocated` | số nạn nhân **khác nhau** được giải quyết | có nhiều nạn nhân thì một con số không đủ |
| `wrongFixes` | số toạ độ chỉ vào vật gây nhầm | "báo sai chỗ" khác hẳn "ước lượng thiếu chính xác" |
| `fixesAtBS` | số toạ độ về tới nơi | lộ ra trần một-fix-mỗi-UAV |
| **chồng lấn** | hai lượt giao ≤150 m **và trùng thời gian** | đây mới là thứ mắt nhìn thấy |
| **độ phủ FAST** | % nút từng nằm trong tầm cue | nút không bị bay qua thì không bao giờ báo được |
| **khúc gấp** | % mẫu đòi bán kính < $R$ | đường bay có bay được không |

Một fix chỉ tính là giải quyết được nạn nhân khi **vừa** trong 50 m **vừa** gần
nạn nhân đó hơn mọi vật gây nhầm — chỉ dùng điều kiện tương đối thì ở $M=0$ nó
luôn đúng và cột đo được số không.

### 21. Guard chống nhầm bản dựng — đã sửa ở đúng tầng

`binary=` chụp mtime+size của **file thực thi**, nhưng mọi app/model/helper nằm
trong **thư viện module** `libns3.46-uav-sar.so`, và hệ thống build **không relink**
file thực thi khi chỉ thư viện đổi. Một bản build đổi hoàn toàn hành vi vẫn để lại
dấu **giống hệt từng byte**.

Bắt được tại trận: hai batch cho kết quả khác hẳn (cùng seed: 2/3 so với 4/4 ứng
viên được phục vụ) mà mang **cùng** `binary=`. Tái hiện có kiểm soát:

```
trước:  binary=1786355023,82512   module=1786411514,829304
sau:    binary=1786355023,82512   module=1786411527,829336
        ↑ KHÔNG đổi                ↑ đổi cả mtime lẫn size
```

Đã thêm `module=` (giải qua `dladdr` từ một symbol trong chính module). Đây mới là
guard mà `STATUS.md` open problem 5 định làm.

### 22. Ba lần thước đo nói sai về hành vi

Ghi lại vì nó là bài học phương pháp, không phải chuyện vặt:

| lần | thước đo sai | nó che mất cái gì |
|---|---|---|
| 1 | "số **điểm khác nhau** được phục vụ" | ba UAV chồng lên một chỗ và một UAV đi ba chỗ đều cho cùng một con số |
| 2 | "số cặp chồng lấn" (không xét thời gian) | hai UAV giao **cùng lúc** cách nhau 1 m |
| 3 | `deliver_start` phát cả khi **tiếp tục** lượt giao | 12/13 "lượt lặp" thực ra không phải lặp |

Cả ba lần, người dùng nhìn replay và thấy đúng còn số liệu thì không.

---

## Phần VI — Trạng thái hiện tại và việc còn lại

### 23. Đo được (8 hạt giống, mỗi lô một `module=`)

| chỉ số | giá trị |
|---|---|
| độ phủ FAST | **99.8 %** |
| **độ phủ DATA** | **99.8 %** (từ 45.7 % — xem §24, lỗi UAV bay lạc) |
| độ phủ ANY | **100.0 %** |
| **UAV bay lạc** | **0/8** hạt giống |
| ứng viên được phục vụ | **67/70 = 95.7 %** |
| lượt giao / điểm | **1.0–1.1** |
| khúc gấp quá khả năng cánh cố định | **0.4 %** |
| quãng đường FAST | 88.5 km (từ 130 km) |
| **nạn nhân định vị được** | **15/16** — và **16/16** với `--victimOnNode=0` |
| **toạ độ sai người (`wrongFixes`)** | **0** (từ 7) |
| **sai số định vị** | trung vị **12.4 m**, p90 **18.0 m** (`--victimOnNode=0`) |
| thời gian tới toạ độ | 248 s |
| **năng lượng** | **236 kJ** (từ 367 kJ) |

> Cả bảng này là **N = 8**. Theo luật `N ≥ 120` của `STATUS.md` đây là **tín
> hiệu**, chưa phải kết quả công bố được.

### 24. Chưa xong — không tuyên bố là đã sửa

- **Ba ứng viên trên 70 vẫn không được phục vụ** (hạt giống 2 và 6). Chưa truy.
- **15/16 chứ không phải 16/16** khi nạn nhân nằm đúng trên nút; ca thiếu là một
  nạn nhân được giao dữ liệu nhưng không sinh CONFIRM đủ mạnh.
- **Chồng lấn giao hàng** đo lần cuối ở 2 cặp / 31 s; chưa đo lại sau §16a.
- **38.8 % vẫn bay ngoài vùng.** Đây là chi phí **nội tại** của cánh cố định trên
  vùng nhỏ: luống 460 m với $R = 64$ m thì mỗi lần đảo chiều vẫn tốn $\pi R = 200$ m.
  Giảm nữa phải đổi **hình học bài toán**, không phải đổi thuật toán — và bản thân
  điều đó là một luận điểm đáng đưa vào bài.
- **Chưa cài:** mặt phẳng tiếp sức payload nội ô (D2/D11) — nút tiếp sức chunk dữ
  liệu cho nhau. Hiện **không nút nào từng phát lại một chunk dữ liệu**; mặt phẳng
  hợp tác mới chỉ chia sẻ *bằng chứng*, chưa chia sẻ *chính dữ liệu*.
- **Chưa chạy campaign chính** ở $N \ge 120$ với pre-registration.

### 25. Hai câu bài báo KHÔNG được viết

1. *"Hợp tác ở biên làm SAR nhanh hơn và rẻ hơn."* Nhánh `closed-loop` (có phản
   hồi, **không** hợp tác) **thắng** `proposed` về thời gian, năng lượng và gói tin
   (0/120 về gói tin). Cái hợp tác mua được là **đuôi sai số vị trí** (−29 % p90),
   ở mức chi phí nêu rõ.
2. *"Mơ hồ danh tính gần như miễn phí."* Con số 5.8 pp đó đo trên cơ chế **chưa
   từng kích hoạt** (§2). Sau khi sửa, mơ hồ là một chế độ **đắt**.
