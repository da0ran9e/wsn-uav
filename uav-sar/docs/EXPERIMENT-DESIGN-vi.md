# Thiết kế thực nghiệm — ghi chép thảo luận

Tài liệu sống, cập nhật trong lúc thảo luận. Mỗi phần ghi: **hiểu biết hiện tại**,
**câu hỏi mở**, và **quyết định đã chốt** (kèm ngày). Chưa chốt thì để nguyên là
câu hỏi — không suy diễn thành kết luận.

Lộ trình: (1) mục tiêu & chỉ số → (2) nhánh so sánh → (3) điểm vận hành →
(4) thiết kế thống kê → (5) bố cục bài báo.

---

## Phần 1 — Mục tiêu và chỉ số

### 1.1 Ba kết cục đang bị gộp làm một

Hệ thống có **ba** kết cục khác nhau, và số liệu hôm nay chứng minh chúng có thể
đi **ngược chiều nhau**:

| # | kết cục | cột trong `metrics.csv` | ý nghĩa vận hành |
|---|---|---|---|
| (a) | **nạn nhân được phục vụ** | `timeToCompleteData_s` | nút gần nạn nhân đã tái tạo đủ tập tham chiếu |
| (b) | **vị trí báo về đúng** | `fixOnVictim`, `reportErr_m`, `timeToFixAtBS_s` | đội cứu hộ biết phải đi đâu, và chỗ đó đúng |
| (c) | **nhiệm vụ kết thúc** | `timeToReportAtBS_s` | mọi UAV đã về và báo cáo (`--allHome`) |

Bằng chứng chúng độc lập nhau — quét `kConfirmThreshold`, 24×24, N=40:

| ngưỡng | (a) cứu được | (b) báo **đúng** chỗ | (c) **không** kết thúc |
|---:|---:|---:|---:|
| 0.30 | 52.5 % | 55.0 % | 1/40 |
| 0.45 | 52.5 % | 57.5 % | 8/40 |
| 0.55 | 53.3 % | **66.7 %** | **12/30** |

(a) phẳng, (b) tăng, (c) xấu đi nhanh. Ba đường cong khác nhau từ **một** tham số.

### 1.2 Ý kiến của tôi (chưa phải quyết định)

**(b) mới là kết cục của bài báo, không phải (a).**

Lý do: về mặt vận hành, thứ đội cứu hộ nhận được là **toạ độ**. (a) là *phương
tiện* — nút của nạn nhân giữ đủ dữ liệu để **tự xác nhận danh tính**, và giá trị
của việc đó nằm ở chỗ nó làm (b) đáng tin. (c) là **quy ước mô phỏng**
(`--allHome`), không phải mục tiêu cứu nạn.

Nguy hiểm cụ thể nếu lấy (a) làm chỉ số chính: đã **đo được** trường hợp *cứu
được nạn nhân nhưng chỉ đường cho đội cứu hộ tới chỗ khác* — 52.5 % phục vụ được
đi kèm sai số báo về median 90 m. Một bài báo tối ưu theo (a) sẽ trông tốt lên
trong khi hệ thống tệ đi.

### 1.3 Hệ quả: dữ liệu bị **kiểm duyệt**, nên không có trung bình

Ở ngưỡng 0.55, **40 %** số run không bao giờ kết thúc trong chân trời 1200 s.
Với những run đó $T=\infty$, nên $\mathbb{E}[T]$ **không xác định** và mọi
"median thời gian nhiệm vụ" hiện đang tính trên **tập sống sót** — đúng loại
survivorship bias mà `STATUS.md` §5 đã cảnh báo ở chỗ khác.

Cách trình bày đúng, theo thứ tự ưu tiên:

1. **Đường cong** $\Pr[\text{fix đúng tới BS trước } t]$ — xử lý kiểm duyệt tự
   nhiên, và cho thấy toàn bộ hình dạng thay vì một con số.
2. $\Pr[T\le T_d]$ tại một **hạn chót khai báo** $T_d$ (kiểu "giờ vàng").
3. Trung bình có kiểm duyệt, với chân trời ghi rõ — chỉ khi cần một con số.

### 1.4 PHẢN BIỆN CỦA BẠN (đã chấp nhận phần lớn) — chỉ có MỘT kết cục

> Chỉ có một kết cục: **tìm thấy nạn nhân và có ít nhất 1 UAV bay về báo cáo**
> (sớm nhất, không cần tất cả). Vì hai đội bay liên tục nên dù cue của đội
> fixed-wing không đủ để kích hoạt summon, đội DATA bay chậm hơn chắc chắn sẽ
> phát đủ dữ liệu (không xét giới hạn thời gian/năng lượng). Và nút tạo ra FP
> **không thể** báo cáo nạn nhân, nên không có trường hợp phục vụ sai.

**Chấp nhận, và nó giải quyết được vấn đề ở §1.3:** nếu nhiệm vụ kết thúc ở bản
báo cáo **đầu tiên**, thì (c) không còn là quy ước riêng nữa mà nhập vào (a)+(b);
và "không kết thúc" trở thành **thất bại thật** chứ không phải dữ liệu bị kiểm
duyệt. Ba đường cong ở §1.1 gộp thành một.

Nhưng **ba chỗ mã nguồn hiện tại không khớp với mô hình này**, hai chỗ đã đo:

**(i) Đội DATA khi tuần tra chỉ phát CUE, không phát tập dữ liệu đầy đủ.**
`SetCues(cues)` với `cues = L0 + L1` = 8×150 + 2×600 = **2 400 B**; tập đầy đủ
là 18 400 B (thêm L2 = 4×4000). Chỉ UAV **đã được triệu tập** mới rải dữ liệu
đầy đủ. Nên mệnh đề "đội DATA chắc chắn sẽ phát đủ dữ liệu" **hiện chưa đúng** —
nó phát đúng thứ mà đội FAST đã phát. Muốn mệnh đề đó đúng thì phải cho tuần tra
rải cả L2, và khi đó phải trả lời: nó khác baseline phủ mù `nocoop` ở chỗ nào?

**(ii) "Nút FP không thể báo cáo" chỉ đúng nếu ngưỡng xác nhận nằm trên sàn
nhiễu.** Với `clutterResolve = 1`, một nút cạnh vật gây nhầm khi giữ đủ dữ liệu
đọc ra ≈ 0 và phát REJECT — đúng như bạn nói. Nhưng ngưỡng xác nhận đang là
`kCoopThreshold = 0.30`, và ở `senseSigma = 0.20` một nút **không có tín hiệu
gì** vẫn vượt ngưỡng do nhiễu với xác suất $Q(0.30/0.20) = 6.7\%$. Đo được:
seed 7 có 2 CONFIRM thật, một cái từ nút 118 tại (300,80) — ngay cạnh vật gây
nhầm. Vậy mệnh đề của bạn đúng **về nguyên tắc** và sai **theo tham số hiện tại**;
sửa bằng ngưỡng, không bằng cơ chế.

**(iii) "Báo cáo đầu tiên kết thúc nhiệm vụ" không được phép dừng đồng hồ năng
lượng.** Đó chính là audit F2: trước đây đề xuất dừng đồng hồ ở courier đầu tiên
trong khi ba UAV còn trên trời, đối đầu với yêu cầu 4/4 của `tsp-mc`. Quy tắc
của bạn hợp lý cho **thời gian**, nhưng năng lượng và gói tin phải tính cho
**toàn đội cho tới khi hạ cánh**, nếu không đề xuất giấu được chi phí của đội bay
còn lại.

**(iv) "Không xét giới hạn thời gian và năng lượng"** — cần tách hai nghĩa. Bỏ
chúng như **ràng buộc cứng** (không có ngưỡng pin cắt ngang) thì hợp lý. Bỏ chúng
như **chỉ số** thì không so sánh được gì nữa, vì khi đó mọi lược đồ đều thành công
nếu chờ đủ lâu — và toàn bộ bài báo là về *nhanh đến đâu, tốn bao nhiêu*.

### 1.5 Kết cục thống nhất (đề xuất chốt)

$$T \;=\; \min\{t : 	ext{BS nhận được báo cáo mang toạ độ ĐÃ ĐƯỢC XÁC NHẬN}\}$$

- **Thành công** nếu $T < \infty$ **và** toạ độ đó ứng với nạn nhân (`fixOnVictim = 1`).
- **Thất bại** nếu không có báo cáo nào, hoặc báo cáo mang toạ độ sai người.
- **Chi phí** đo trên **toàn đội đến khi hạ cánh**, không dừng ở $T$.

Chỉ số chính công bố: $\Pr[T \le t]$ theo $t$ (một đường cong), kèm tỉ lệ thất bại
theo hai loại tách riêng.

### 1.6 QUYẾT ĐỊNH ĐÃ CHỐT (thảo luận 2026-08-07)

| # | quyết định | trạng thái mã nguồn |
|---|---|---|
| D1 | Đội DATA khi tuần tra rải **dữ liệu đầy đủ**, cue vẫn ưu tiên cao hơn | **chưa có** — hiện chỉ rải cue |
| D2 | Node được **hợp tác nội ô bằng data packet** — đây là chỗ khác `nocoop` | **chưa có** — mặt phẳng hợp tác hiện chỉ chia sẻ BẰNG CHỨNG, chưa bao giờ chia sẻ PAYLOAD |
| D3 | FP do **nạn nhân giả** đánh lừa cue; đủ dữ liệu thì nút tự nhận ra | **đã có** = `ClutterSource` + `clutterResolve=1` |
| D4 | **Thời gian nhiệm vụ** = UAV **đầu tiên** về báo cáo | **chưa có** — `timeToReportAtBS_s` hiện là lúc **mọi** UAV đã báo |
| D5 | **Năng lượng/gói tin** tính tới khi **toàn đội** hạ cánh | đã có (`--allHome`) |
| D6 | Thời gian & năng lượng là **chỉ số**, không phải ràng buộc cứng | đã có |

Kiểm chứng cho D2 và D4 (đọc mã, không suy đoán):

- `sar-ground-app.cc`: nút chỉ **nhận** chunk CUE/FULL (dòng 613); mọi lệnh
  `m_dev->Send` của nút đều là ECHO/RPT/SHARE/RCLAIM/CONFIRM/REJECT — **không
  nút nào từng phát lại một chunk dữ liệu**.
- `sar-bs-app.cc`: `MarkReportAtBS` chỉ được gọi khi
  `m_reporters.size() >= m_expected`, tức **toàn đội**, chứ không phải chiếc đầu.

### 1.7 Nhận xét của tôi về từng quyết định

**D1 + D2 — đồng ý, và D2 là chỗ mạnh nhất trong toàn bộ thiết kế.**
Hiện tại mặt phẳng hợp tác chỉ chia sẻ *bằng chứng*; nó không hề giảm được lượng
airtime cần để giao *payload*. Cho phép chia sẻ payload nội ô tạo ra một lợi thế
chi phí **có cấu trúc** so với `nocoop`: một UAV bay qua chỉ cần phủ tới **vài
nút**, các nút đó tiếp sức cho cả ô qua G2G, nên UAV cần ít lượt bay hơn hẳn cho
cùng số nút hoàn tất. Đó là lập luận "vì sao hợp tác rẻ hơn" mạnh hơn nhiều so
với mọi lập luận đã có trong bài.

**Ba rủi ro phải đo, không được giả định:**

1. **Tập đầy đủ = 18 400 B ≈ 184 chunk 100 B.** Tiếp sức từng ấy chunk qua LR-WPAN
   250 kbps có tranh chấp, tầm 37 m, có thể **chậm hơn** là chờ UAV bay qua lần
   nữa. Hợp tác payload chưa chắc đã lãi.
2. **Phát lại mù sẽ nổ mạng.** Cần quy tắc: nút chỉ tiếp sức chunk mà hàng xóm
   còn thiếu (bitmap "tôi có gì" + yêu cầu), hoặc phát lại ở tốc độ thấp trong ô.
   Đây thực chất là bài toán **gossip / mã rateless**, không phải một dòng lệnh.
3. **Rải full data khi tuần tra sẽ nhân chi phí gói tin lên nhiều lần** (7.7× so
   với cue). Ở 24×24 hiện đã 12–15k gói; cần kiểm nó không nuốt mất chính lợi thế
   mà D2 tạo ra.

**D3 — đồng ý hoàn toàn, và nó chính là mô hình đã cài.** Nhưng câu hỏi ngưỡng
vẫn còn, và tôi cho rằng **mô hình nhiễu mới là chỗ sai, không phải ngưỡng**:
cộng $N(0,\sigma)$ vào một chất lượng trong $[0,1]$ rồi cắt biên khiến một nút
**không có tín hiệu gì** vẫn đọc ra $\ge 0.30$ với xác suất 6.7 %. Bộ phát hiện
thật không hành xử như vậy — điểm khớp của một quan sát hoàn toàn không khớp thì
tập trung gần 0 với đuôi phải mỏng, không đối xứng quanh 0. **Đề xuất: nhiễu phụ
thuộc tín hiệu** (hoặc nhiễu trong không gian logit) để nút trắng ở lại gần 0.
Khi đó mệnh đề "FP không thể báo cáo" của bạn đúng **theo cấu trúc**, không cần
đẩy ngưỡng lên cao và không phải trả giá bằng 40 % nhiệm vụ không kết thúc.

**D4 — đồng ý, và nó cần một cột mới** chứ không sửa cột cũ: giữ
`timeToReportAtBS_s` (toàn đội, để đối chiếu lịch sử) và thêm
`timeToFirstReport_s`. Bài báo dùng cột mới cho thời gian, cột cũ chỉ để kiểm tra
chi phí đã tính đủ.

### 1.8 Việc phải làm (từ Phần 1)

1. `timeToFirstReport_s` — cột mới, thời gian nhiệm vụ theo D4. *(nhỏ)*
2. Mô hình nhiễu phụ thuộc tín hiệu trong `clue-field`. *(nhỏ, thay đổi mọi kết quả)*
3. Tuần tra rải full data với ưu tiên cue. *(vừa)*
4. **Hợp tác payload nội ô** — bitmap + tiếp sức chunk còn thiếu. *(lớn, và là
   thứ đáng giá nhất)*

### 1.9 Quét ngưỡng xác nhận — đầy đủ, và nó XÁC NHẬN chẩn đoán ở §1.7

24×24, 4 vật gây nhầm (s = 0.85–0.95), 6 UAV, N = 40 mỗi mức, một binary:

| ngưỡng | cứu được | có báo fix | **báo ĐÚNG** | sai số\|đúng | confirm/run | reject/run |
|---:|---:|---:|---:|---:|---:|---:|
| 0.30 | 52.5 % | 100 % | 55.0 % | 25.9 m | 10.6 | 20.4 |
| 0.45 | 52.5 % | 92.5 % | 57.5 % | 25.7 m | 6.4 | 32.4 |
| 0.55 | 52.5 % | 75.0 % | 62.5 % | 25.3 m | 4.7 | 47.3 |
| 0.70 | 52.5 % | 65.0 % | **62.5 %** | 25.7 m | 2.4 | 56.6 |

Bốn điều đọc được, và cả bốn đều nói ngưỡng **không phải** chỗ sửa:

1. **Tỉ lệ cứu được tuyệt đối không đổi: 52.5 % ở cả bốn mức.** Ngưỡng xác nhận
   không hề ảnh hưởng tới việc dữ liệu có tới được nạn nhân hay không — đúng như
   phải thế, vì nó chỉ chi phối *lời tuyên bố*, không chi phối *việc giao hàng*.
2. **Sai số khi báo đúng cũng không đổi (25.3–25.9 m).** Nên phần cải thiện hoàn
   toàn đến từ việc **bỏ bớt báo cáo sai**, không phải ước lượng tốt hơn.
3. **"Báo đúng" bão hoà ở 62.5 %** từ 0.55 trở lên, trong khi **"có báo fix" tiếp
   tục rơi** 75 % → 65 %. Tức là từ mức đó trở đi, nâng ngưỡng chỉ còn **giết
   những báo cáo ĐÚNG**. Đây là điểm gãy của đường cong.
4. **Confirm/run rơi 10.6 → 2.4 còn reject/run tăng 20.4 → 56.6.** Ở 0.70 hệ
   thống chủ yếu đang **từ chối chính nó**.

Trần 62.5 % là chỗ đáng chú ý nhất: cứu được 52.5 % nhưng báo đúng 62.5 % — hai
con số này **không thể** cùng đúng nếu "báo đúng" đòi hỏi đã phục vụ nạn nhân.
Nghĩa là có những run báo đúng vị trí **mà nạn nhân chưa hoàn tất dữ liệu**: một
nút *lân cận* nạn nhân xác nhận thay. Điều đó hợp lý và thậm chí là tốt về mặt
vận hành (đội cứu hộ vẫn được chỉ đúng chỗ), nhưng nó nói rằng **D4 "tìm thấy nạn
nhân" cần định nghĩa lại**: là *nút của nạn nhân hoàn tất*, hay *một nút đủ gần
xác nhận đúng chỗ*? Hai định nghĩa cho hai con số khác nhau.

**Kết luận cho D3:** ngưỡng mua được 7.5 điểm phần trăm độ đúng rồi bão hoà, trong
khi tiếp tục cắt cả báo cáo đúng. Đó là dấu hiệu của việc **bù ngọn**. Sửa mô hình
nhiễu để nút trắng ở lại gần 0 là cách xử lý gốc, và khi đó ngưỡng có thể quay về
thấp mà không mất gì.

### 1.10 "Cứu được" nghĩa là gì, và vì sao nó KHÔNG phải 100 %

**Định nghĩa hiện tại, chính xác theo mã:** `MarkCompleteData` chỉ được gọi khi
`m_isTarget && HasEntireDataset()` — tức **đúng cái nút được chỉ định là gần nạn
nhân nhất** đã tái tạo **đủ mọi mảnh** của tập tham chiếu.

Bạn hỏi rất đúng: nếu cứ chờ đủ lâu thì sao vẫn có tỉ lệ? Ba lý do, và **không lý
do nào là "thiếu thời gian"**:

**(1) UAV tuần tra CHỈ phát cue, không bao giờ phát tập đầy đủ.**
`SendFullChunk` mở đầu bằng `if (m_state != State::DELIVER ...) return;` — chỉ
UAV **đã được triệu tập và đang ở trạng thái giao hàng** mới rải L2. Tuần tra gọi
`PatrolCueTick`, phát `m_cues` (L0+L1). Nên **tuần tra chạy vô hạn cũng không bao
giờ hoàn tất dữ liệu cho nạn nhân.** Đây chính là D1: mệnh đề "đội DATA chắc chắn
sẽ phát đủ dữ liệu" hiện **sai theo cấu trúc**, không phải sai vì hết giờ.

**(2) Mô phỏng dừng, không chạy vô hạn.** `Simulator::Stop` kích hoạt khi BS đủ
báo cáo; UAV về nhà theo `kSkyQuietS` (45 s không nghe cue). Nên "chờ đủ lâu"
không xảy ra trong thiết kế hiện tại.

**(3) Giao hàng ở cự ly, có mất gói.** Ngay cả khi có UAV được triệu tập tới đúng
vùng, nạn nhân thường cách điểm thả 20–44 m và xác suất nhận từng gói giảm theo
cự ly. Đã đo trước đây: 9 trong 12 lần thất bại ở 16×16 đúng là kiểu này — giao
hàng CÓ xảy ra, điểm thả gần nhất cách 19.7–43.6 m.

**Kết luận:** tỉ lệ 52.5 % không phản ánh "chưa đủ thời gian" mà phản ánh (1) và
(3). Và **D1 + D2 chính là thứ làm trực giác của bạn trở thành đúng** — khi tuần
tra rải cả L2 và nút tiếp sức payload trong ô, thì "chờ đủ lâu ⇒ chắc chắn xong"
mới thành mệnh đề thật.

### 1.11 D3 nói rõ hơn: sai ở MÔ HÌNH NHIỄU, không ở ngưỡng

**Mô hình hiện tại** (`clue-field.cc`):

$$\hat q_i \;=\; \mathrm{clip}_{[0,1]}\big(q_i + \sigma\,\varepsilon_i\big),
\qquad \varepsilon_i\sim\mathcal N(0,1)$$

Nhiễu **cộng** và **không phụ thuộc tín hiệu**. Hệ quả cho một nút có
$q_i = 0$ (không có vật thể nào gần):

$$\Pr[\hat q_i \ge 0.30] \;=\; Q(0.30/\sigma) \;=\; Q(1.5) \;=\; 6.7\,\%
\quad (\sigma = 0.20)$$

Nói bằng lời: **cứ 15 nút nhìn vào rừng trống thì có 1 nút chấm điểm khớp ≥ 0.30**
so với tập dữ liệu tham chiếu. Bộ phát hiện thật không hành xử như vậy — điểm khớp
của một quan sát *hoàn toàn không khớp* tập trung sát 0 với đuôi phải mỏng, chứ
không phải một Gauss đối xứng quanh 0 rồi bị cắt biên.

Trong hệ thống, hậu quả là những nút đó **giữ đủ dữ liệu và vẫn CONFIRM** — chúng
tự nhận là nạn nhân **từ nhiễu thuần tuý**. Đó là nguồn của các CONFIRM cạnh vật
gây nhầm, và cũng là lý do nâng ngưỡng "có vẻ hiệu quả": ngưỡng đang **bù** cho
một mô hình nhiễu lẽ ra không được đặt khối lượng xác suất ở đó.

**Đề xuất — nhiễu phụ thuộc tín hiệu:**

$$\hat q_i \;=\; \mathrm{clip}_{[0,1]}\Big(q_i + \sigma\,(q_i + q_0)\,\varepsilon_i\Big),
\qquad q_0 \approx 0.05$$

| $q_i$ | độ lệch chuẩn hiệu dụng ($\sigma=0.20$) | $\Pr[\hat q \ge 0.30]$ |
|---:|---:|---:|
| 0.00 (rừng trống) | 0.010 | $\approx 0$ |
| 0.30 (halo xa) | 0.070 | 50 % |
| 0.80 (sát nạn nhân) | 0.170 | ~100 % |

Nút trắng **ở lại trắng**; nút có tín hiệu **vẫn nhiễu đúng như trước**. Đây là
dạng chuẩn cho điểm khớp / bộ phát hiện giới hạn bởi SNR: sai số **tương đối**
chứ không phải tuyệt đối.

**Được gì:** mệnh đề của bạn — *nút FP không thể báo cáo nạn nhân* — trở thành
**đúng theo cấu trúc**. FP khi đó **chỉ** đến từ vật gây nhầm thật (`ClutterSource`)
đánh lừa ở tầng cue, đúng như mô hình bạn mô tả. Và ngưỡng xác nhận có thể quay
về mức thấp, **không phải trả giá 40 % nhiệm vụ không kết thúc**.

**Cảnh báo bắt buộc:** thay đổi này làm hệ thống **đẹp lên trên mọi chỉ số nhập
nhằng**. Vì vậy nó phải được biện minh bằng **lý do vật lý** và khai báo rõ trong
bài như một thay đổi mô hình — không được lặng lẽ áp dụng rồi khoe số. Và **mọi
kết quả có `senseSigma > 0` đều phải chạy lại.**

### 1.12 Câu hỏi mở còn lại

- **Q1.1** Kết cục chính của bài báo là (a), (b), hay một tổ hợp? Nếu (b) thì
  `victim served` xuống vai trò chỉ số phụ / cơ chế.
- **Q1.2** Câu chuyện vận hành là "đội cứu hộ nhận được toạ độ đúng" hay "thiết
  bị của nạn nhân nhận được dữ liệu"? Hai cái dẫn tới hai chỉ số khác nhau.
- **Q1.3** Có chấp nhận công bố **đường cong** thay vì một con số trung bình
  không? Nếu có thì vấn đề kiểm duyệt biến mất.
- **Q1.4** Có hạn chót $T_d$ nào có nghĩa trong SAR để báo $\Pr[T\le T_d]$?
  Nếu có, nó nên đến từ tài liệu SAR chứ không phải từ số liệu của ta.
- **Q1.5** Có tính "báo cáo sai" (fix về BS nhưng sai người) như một **thất bại
  riêng** không? Tôi nghiêng về **có**, vì nó tệ hơn "không báo gì" — nó điều
  động đội cứu hộ đi sai chỗ.
