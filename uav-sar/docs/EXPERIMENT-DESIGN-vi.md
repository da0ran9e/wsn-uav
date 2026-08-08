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

### 1.12 MÔ HÌNH MỚI — phát biểu lại toàn bộ

Tổng hợp mọi thứ đã chốt. Đây là mô hình cần cài, không phải mô hình đang chạy.

#### A. Thế giới

- Vùng $\mathcal A$, lưới $N$ cảm biến, BS tại gốc.
- **Một** nạn nhân thật tại vị trí liên tục $v$.
- **$M$ nạn nhân giả** tại $c_1..c_M$, mỗi cái có độ tương đồng $s_m\in[0,1]$.
  Chúng là vật thể **thật sự giống** tập tham chiếu đủ để đánh lừa **tầng cue**.

#### B. Cảm biến — hai tầng, đây là trục chính của bài

Chất lượng khớp **thật** của nút $i$ phụ thuộc **lượng dữ liệu tham chiếu nó
đang giữ**, ký hiệu $C_i\in[0,1]$:

$$q_i(C_i)=\max\Big(g(\|p_i-v\|),\ \max_m s_m\,(1-C_i)\,g(\|p_i-c_m\|)\Big)$$

- $C_i \to 0$ (chỉ có mảnh cue): nạn nhân giả **trông y như** nạn nhân thật → FP.
- $C_i \to 1$ (đủ tập tham chiếu): số hạng giả **tắt** → nút **tự biết** mình là FP.

Số **đo được** dùng nhiễu **phụ thuộc tín hiệu** (thay cho nhiễu cộng cũ):

$$\hat q_i=\mathrm{clip}_{[0,1]}\Big(q_i+\sigma\,(q_i+q_0)\,\varepsilon_i\Big),
\qquad \varepsilon_i\sim\mathcal N(0,1),\ q_0\approx0.05$$

Hệ quả then chốt: nút **không có vật thể nào gần** thì $\hat q_i\approx0$ và
**không thể xác nhận** — nên *FP không bao giờ báo cáo nạn nhân*, **theo cấu
trúc**, không nhờ chỉnh ngưỡng.

#### C. Đội bay — hai khung máy bay, có cơ sở vật lý

| | FAST | DATA |
|---|---|---|
| khung | **fixed-wing** | **rotary-wing** |
| tốc độ | 25 m/s (90 km/h) | 15 m/s (54 km/h) |
| giữ vị trí | **không** (phải bay vòng) | **có** |
| việc | quét, rải cue, tiếp sức, đưa báo cáo về BS | tuần tra **rải full data**, giao hàng khi được triệu tập |

Phân công này là **hệ quả vật lý**: quét và đưa tin cần khung không bao giờ dừng;
dwell giao hàng 20–40 s cần khung giữ được vị trí.

#### D. Hợp tác mặt đất — HAI mặt phẳng

1. **Mặt phẳng bằng chứng** *(đã có)*: RPT lên cây trong ô, SHARE xuyên ô, bầu
   cử, SUMMON, CONFIRM/REJECT. Chia sẻ *ai thấy gì*.
2. **Mặt phẳng payload** *(mới, D2)*: nút **tiếp sức chunk dữ liệu** cho nút cùng
   ô. Chia sẻ *chính dữ liệu*.

Mặt phẳng 2 là **chỗ khác biệt so với `nocoop`**, và là lập luận chi phí mạnh
nhất mà bài báo có: một lượt UAV bay qua chỉ cần chạm tới **vài nút**, phần còn
lại của ô nhận qua G2G — nên cần **ít lượt bay hơn hẳn** cho cùng số nút hoàn tất.

#### E. Nhiệm vụ — MỘT kết cục

$$T=\min\{t:\ \text{BS nhận báo cáo mang toạ độ ĐÃ XÁC NHẬN}\}$$

- **Thành công**: $T<\infty$ **và** toạ độ ứng với nạn nhân thật.
- **Thất bại**: không có báo cáo, **hoặc** báo cáo mang toạ độ của nạn nhân giả.
- **Thời gian nhiệm vụ**: tính tại $T$ (UAV **đầu tiên** về báo cáo).
- **Chi phí**: năng lượng + gói tin của **toàn đội tới khi hạ cánh**, không dừng
  ở $T$.
- Thời gian/năng lượng là **chỉ số**, không phải ràng buộc cứng.

#### F. Hệ quả lớn nhất của mô hình mới — và nó đổi cả thiết kế thực nghiệm

Với D1 (tuần tra rải full data) + D2 (tiếp sức payload), mệnh đề của bạn trở
thành **đúng**: chờ đủ lâu thì nạn nhân **chắc chắn** nhận đủ dữ liệu. Nhưng khi
đó — và điều này áp dụng cho **cả các baseline**, vì `nocoop`/`tsp-mc` cũng phủ
toàn vùng — **mọi lược đồ đều thành công nếu chân trời đủ dài**.

Nghĩa là **tỉ lệ cứu được thôi không còn là chỉ số phân biệt.** Bài báo chuyển
trục sang:

$$\text{công bố } \Pr[T\le t] \text{ theo } t,\ \text{và chi phí để đạt được nó}$$

Đây thực ra là **thiết kế sạch hơn** và trùng với cách đánh giá của dòng multicast
(Zeng'18 đo *completion time*). Tỉ lệ thất bại chỉ còn ý nghĩa **tại một chân trời
hữu hạn khai báo trước** (pin thật), và khi đó nó là một điểm trên đường cong chứ
không phải một con số rời.

#### G. Còn phải quyết

- **G1** Quy tắc tiếp sức payload: bitmap "tôi có gì" + chỉ gửi chunk hàng xóm
  thiếu? Hay phát lại tốc độ thấp trong ô? (Bài toán gossip/rateless.)
- **G2** Ưu tiên cue khi tuần tra: tỉ lệ chu kỳ cue:full là bao nhiêu?
- **G3** "Đúng chỗ" định nghĩa thế nào — hiện là *gần nạn nhân hơn gần mọi vật
  gây nhầm*. Có cần thêm bán kính tuyệt đối (ví dụ ≤ 50 m) không?
- **G4** Chân trời khai báo $T_{\max}$ để báo tỉ lệ thất bại: lấy từ đâu?

### 1.14 Ý TƯỞNG ĐỂ CÂN NHẮC SAU (D7) — đội FAST hỗ trợ rải dữ liệu

> **Ý tưởng (2026-08-07):** nếu đội FAST đã rải hết cue mà **chưa tìm thấy mục
> tiêu**, nó có thể chuyển sang **hỗ trợ đội DATA rải dữ liệu ở tốc độ cao**.

**Chưa cài. Ghi lại để cân nhắc.** Dưới đây là phân tích để lần sau khỏi phải làm
lại từ đầu.

#### Vì sao hấp dẫn: nó **cộng hưởng** với D2

Một mình thì gần như vô dụng; đi cùng mặt phẳng payload thì rất mạnh. Lý do nằm
ở cửa sổ tiếp xúc.

| | tốc độ | bán kính ngang (cao độ 20 m, tầm A2G 50 m) | **cửa sổ tiếp xúc một lượt bay qua** |
|---|---:|---:|---:|
| FAST fixed-wing | 25 m/s | 45.8 m | **3.7 s** |
| DATA rotary | 15 m/s | 45.8 m | 6.1 s (và **hover được** → vô hạn) |

Chi phí phát tập đầy đủ: 18 400 B = **184 chunk** × 100 B. Một khung
100 B payload + 13 B MAC + 2 B FCS + 6 B PHY = 968 bit ở 250 kbps = 3.87 ms,
cộng backoff CSMA trung bình + CCA ≈ **5.1 ms/khung**.

$$\text{airtime tối thiểu} = 184 \times 5.1\,\text{ms} = \mathbf{0.94\ s}$$

**Kết luận định lượng:** một lượt FAST bay qua cho **3.7 s** tiếp xúc so với
**0.94 s** airtime tối thiểu — dư khoảng 4×, nhưng đó là trường hợp **bay ngay
trên đầu, kênh sạch, không tranh chấp, không mất gói**. Nút lệch sang bên có cửa
sổ ngắn hơn nhiều, và nhiều nút cùng tranh một cửa sổ.

Nên phát biểu đúng là: **một lượt FAST bay qua đủ để nạp đầy khoảng MỘT nút nằm
gần đúng dưới đường bay.**

- **Không có D2:** gần như vô dụng — nạp một nút lẻ không giúp gì.
- **Có D2:** rất mạnh — FAST chỉ cần **gieo một nút mỗi ô**, phần còn lại của ô
  tự lấp qua G2G. Đội fixed-wing biến thành **máy gieo hạt** cho mặt phẳng
  payload, và đó đúng là việc mà một khung không dừng được nên làm.

#### Xung đột phải giải: FAST đang có việc khác sau khi quét xong

`kRelayGraceS = 30 s` — sau khi quét xong, FAST **giữ vị trí làm trạm chuyển
tiếp** để lệnh SUMMON còn đường lên trời. Cơ chế này **đang gánh kết quả**
(audit A10). Nếu FAST bỏ đi rải dữ liệu thì trạm chuyển tiếp biến mất.

Hai vai xung đột trực tiếp. Với **2 chiếc FAST** thì cách tự nhiên là **chia
vai**: một chiếc giữ vai chuyển tiếp, một chiếc chuyển sang hỗ trợ rải dữ liệu.
Cần đo, vì mất một nửa năng lực chuyển tiếp có thể đắt hơn phần dữ liệu thu được.

Lưu ý thêm: theo `FIXED-WING-FAST-vi.md`, ở 25 m/s với góc nghiêng 30° thì bán
kính lượn là 70.6 m và cự ly xiên 73.4 m — **ngoài tầm A2G 50 m**. Nghĩa là vai
"giữ vị trí làm trạm chuyển tiếp" **vốn đã có vấn đề** với khung fixed-wing. Nếu
vai đó không đứng vững thì xung đột tự biến mất, và D7 trở thành lựa chọn hiển
nhiên cho FAST sau khi quét xong.

#### Điều kiện kích hoạt (cục bộ, không cần oracle)

FAST tự biết: (1) đã bay hết kế hoạch phủ của mình, và (2) chưa nghe SUMMON nào
trong `kRelayGraceS`. Cả hai đều là thông tin cục bộ — không vi phạm nguyên tắc
"không dùng oracle".

#### Phải đo gì khi triển khai

1. Số nút hoàn tất dữ liệu **nhờ FAST gieo** so với nhờ DATA giao — có tách được không.
2. Ảnh hưởng lên $T$ (thời gian tới fix đúng), so cặp, có/không D7.
3. Giá năng lượng: FAST bay thêm ở 25 m/s, mà đường cong công suất đang dùng là
   **rotary** nên số hạng ký sinh $\propto v^3$ **thổi phồng** chi phí này.
4. Có làm hỏng vai chuyển tiếp không — đo qua tỉ lệ SUMMON tới được đội DATA.

---

## Phần 2 — Các nhánh so sánh

### 2.1 Ma trận hai chiều (đã chốt 2026-08-07)

D1 làm UAV DATA tuần tra rải full data trên toàn dải — **đúng việc `nocoop` đang
làm**. Nên `proposed` giờ **chứa `nocoop` bên trong**, và câu hỏi "baseline nào
công bằng" phải trả lời lại. Cách trung thực hơn: phủ mù là **nền**, và mỗi tầng
hợp tác thêm vào mua được gì.

**Chiều A — vòng phản hồi** (mặt đất có bảo bầu trời đi đâu không?)

| mức | cơ chế |
|---|---|
| A0 | không có — phủ mù |
| A1 | có, **không hợp tác** — ECHO một hop (`closed-loop`) |
| A2 | có, **hợp tác** — cây trong ô + SHARE + bầu cử (`proposed`) |

**Chiều B — mặt phẳng PAYLOAD** (nút có tiếp sức **chunk dữ liệu** cho nhau
không?) — *lưu ý: đây là payload, không phải bằng chứng; bằng chứng thuộc chiều A*

| mức | cơ chế |
|---|---|
| B0 | không hợp tác |
| B1 | **hợp tác trong ô** |
| B2 | **hợp tác trong và ngoài ô** — thêm mức này để xem **overhead có đáng đổi lấy thời gian không** |

→ **3 × 3 = 9 nhánh.** `tsp-mc` đứng riêng làm **baseline tài liệu** (Zeng'18),
**không** được cấp relay — giữ đúng như đã công bố, nếu không thì đang so với một
thứ chưa ai từng đề xuất. `pure-uav` **bỏ** — bài này so sánh đa UAV.

### 2.2 Dự đoán: đây là hiệu ứng TƯƠNG TÁC, không phải hai hiệu ứng cộng

B một mình nhiều khả năng **không** tiết kiệm gì: tiếp sức trong ô chỉ giảm chi
phí **nếu UAV biết dừng sớm**, mà một UAV phủ mù cứ rải hết ngân sách dwell bất
kể mặt đất đã tự lo xong. Muốn tiết kiệm airtime thật thì UAV phải **nghe được
rằng đủ rồi** — tức là chiều A.

Nếu đúng: `A0B1 ≈ A0B0` về chi phí, còn `A2B1` mới rẻ. Đó là lập luận mạnh nhất
bài báo có thể có về vì sao cần hợp tác — **không phải vì hợp tác tự nó rẻ, mà vì
hợp tác là thứ cho phép dừng sớm.** Nếu sai, `A0B1` thành baseline mạnh mà
`proposed` phải vượt. Ma trận đo trực tiếp được điều này.

B2 so B1 trả lời câu riêng của bạn: chunk đi xuyên ô thì một lượt bay phủ được xa
hơn, nhưng G2G chỉ ~37 m và flood đi theo link may mắn — **overhead có thể nuốt
hết phần thời gian tiết kiệm được.** Chưa có dự đoán; đo.

### 2.3 CÂU HỎI QUAN TRỌNG NHẤT: một CONFIRM có đủ không?

> *"có nhưng cần xác nhận lại là chỉ có 1 confirm từ nạn nhân thôi sao lại là đủ"*

Tách làm ba mệnh đề, và **chỉ mệnh đề đầu đúng**:

**(1) Một CONFIRM *từ nạn nhân* là đủ về mặt logic.** Nếu nút của nạn nhân giữ đủ
tập tham chiếu **và vẫn khớp**, thì mục tiêu nhận dạng đã đạt. Không cần nút thứ
hai xác nhận hộ.

**(2) Nhưng UAV KHÔNG BIẾT CONFIRM đó đến từ nạn nhân.** Gói CONFIRM hiện tại:

```
kConfirmLen = 5 B:  [type][dst][regionId:u16][nodeId:u8]
```

**Không mang bằng chứng, không mang vị trí.** `nodeId` còn bị cắt xuống 8 bit. Nên
"dừng khi có CONFIRM đầu tiên" thực chất là **"dừng khi có ai đó bất kỳ xác nhận"**
— hai chuyện khác nhau. Đây là lỗ hổng mà câu hỏi của bạn chỉ ra, và tôi chưa thấy.

**(3) Vị trí báo về đang là ĐIỂM NHẮM, không phải vị trí nút xác nhận.** Tức là ta
đang báo về *chỗ lãnh đạo đoán*, trong khi có sẵn một nút **chắc chắn khớp** và
**biết chính xác mình ở đâu**.

#### Đề xuất: CONFIRM mang bằng chứng + vị trí

```
kConfirmLen = 10 B: [type][dst][regionId:u16][nodeId:u8][evQ8:u8][x:i16][y:i16]
```

Ba thứ được cùng lúc:

1. **Dừng sớm có căn cứ** — UAV chỉ dừng khi nghe CONFIRM có `evQ8 ≥` ngưỡng nhận
   dạng, thay vì dừng khi có bất kỳ ai lên tiếng.
2. **Vị trí báo về tốt hơn** — báo **vị trí của nút xác nhận mạnh nhất**, một nút
   *đã cầm đủ dữ liệu và vẫn khớp*, thay vì báo điểm ước lượng từ bằng chứng mức
   cue. Đây là argmax trên tập nút **đã được kiểm chứng**, mạnh hơn hẳn argmax
   hiện tại.
3. **Mệnh đề của bạn thành đúng theo cấu trúc** — cộng với nhiễu phụ thuộc tín
   hiệu (D3), một nút không có tín hiệu **không thể** sinh CONFIRM có evidence
   cao. Nên **một** CONFIRM evidence-cao thật sự là đủ.

Chi phí: 5 B → 10 B, thừa sức trong trần 100 B.

**Chuỗi logic gọn lại:** D3 làm một CONFIRM **đáng tin**; mang evidence làm nó
**kiểm chứng được**; mang vị trí làm nó **chính xác hơn**.

### 2.4 Việc phát sinh từ Phần 2

| # | việc | quy mô |
|---|---|---|
| D8 | CONFIRM mang `evQ8` + vị trí; fix báo về = vị trí nút xác nhận mạnh nhất | nhỏ, giá trị cao |
| D9 | UAV dừng giao hàng sớm khi nghe CONFIRM đủ mạnh | nhỏ, **mở khoá lợi ích của B** |
| D10 | Bỏ `pure-uav` khỏi bộ nhánh | nhỏ |
| D11 | Cài B1 (tiếp sức trong ô) và B2 (thêm xuyên ô) | lớn |

### 2.5 DANH SÁCH QUYẾT ĐỊNH TÍCH LUỸ (D1–D11)

| # | quyết định | trạng thái | quy mô |
|---|---|---|---|
| D1 | Tuần tra DATA rải **full data**, cue ưu tiên cao hơn | chưa cài | vừa |
| D2 | Hợp tác **payload nội ô** | chưa cài | lớn |
| D3 | FP do nạn nhân giả; **nhiễu phụ thuộc tín hiệu** | mô hình clutter đã có; nhiễu **chưa** | nhỏ |
| D4 | Thời gian nhiệm vụ = **UAV đầu tiên** về báo cáo | chưa cài | nhỏ |
| D5 | Chi phí tính tới khi **toàn đội** hạ cánh | đã có | — |
| D6 | Thời gian/năng lượng là **chỉ số**, không phải ràng buộc | đã có | — |
| D7 | FAST hỗ trợ rải dữ liệu sau khi quét xong | **để sau** | vừa |
| D8 | CONFIRM mang `evQ8` + vị trí; fix = vị trí nút xác nhận mạnh nhất | chưa cài | nhỏ, giá trị cao |
| D9 | UAV **dừng giao hàng sớm** khi nghe CONFIRM đủ mạnh | chưa cài | nhỏ, mở khoá lợi ích của B |
| D10 | Bỏ `pure-uav`; `tsp-mc` giữ nguyên, không relay | chưa cài | nhỏ |
| D11 | Cài B1 (trong ô) và B2 (trong + ngoài ô) | chưa cài | lớn |

---

## Phần 3 — Điểm vận hành và tham số quét

### 3.1 Vấn đề: tích Descartes đầy đủ là bất khả thi

Các trục có thể quét: quy mô (4 mức) × nhập nhằng (3 mức) × nhiễu (3 mức) ×
**9 nhánh** × N=120 = **~39 000 run**. Không chạy nổi.

Nên phải chọn: **một điểm vận hành chính** chạy đủ ma trận, cộng các **quét
một-yếu-tố** xuất phát từ điểm đó.

### 3.2 Đề xuất: đổi tham số sang ĐƠN VỊ CÓ NGHĨA VẬN HÀNH

Đây là điểm tôi cho là quan trọng nhất của Phần 3. Hiện ta quét **hằng số nội
bộ**; nên quét **đại lượng mà người phản biện hiểu được**:

| đang quét | nên quét | vì sao |
|---|---|---|
| `senseSigma` | $\Pr[\text{nút của nạn nhân vượt ngưỡng báo động}]$ | "chất lượng bộ phát hiện", đọc được ngay |
| `gridSize` | **diện tích vùng** (m²) và **mật độ nút** (nút/ha) | quy mô thật, so được với tài liệu SAR |
| `clutterCount` | **mật độ vật gây nhầm** (số/km²) | so được với kịch bản thật |
| `numUav` | **số UAV trên km²** | so được giữa các quy mô |

Trục nhập nhằng thứ hai — **độ tương đồng $s$** — giữ nguyên vì nó vốn đã là một
tỉ số không thứ nguyên và đọc được: $s=1$ nghĩa là *không phân biệt được*.

### 3.3 CẢNH BÁO: D3 làm `senseSigma` cũ **mất ý nghĩa**

Nhiễu mới là $\sigma(q+q_0)$, nên độ lệch hiệu dụng tại nút nạn nhân
($q \approx 0.8$) là $0.85\sigma$, còn tại nút trắng là $0.05\sigma$. Cùng một
con số `senseSigma` **không còn mô tả cùng một bộ phát hiện**.

Hệ quả bắt buộc: **phải hiệu chuẩn lại** — chọn $\sigma$ sao cho một đại lượng
vận hành giữ nguyên (ví dụ: xác suất nút gần nạn nhân nhất vượt ngưỡng báo động
bằng đúng giá trị nó có ở mô hình cũ). Nếu không thì mọi so sánh trước/sau D3 là
so hai bộ phát hiện khác nhau, không phải so hai mô hình nhiễu.

### 3.4 Điểm vận hành chính — đề xuất

| tham số | giá trị | lý do |
|---|---|---|
| lưới | **24×24** (460×460 m) | 16×16 quá nhỏ (đa ứng viên hiếm, chỗ đỗ giữa map luôn với tới được); 40×40 quá chậm để chạy N=120 × 9 nhánh |
| đội bay | **6 UAV** (2 FAST + 4 DATA) | đã dùng suốt phần thảo luận; ~28 UAV/km² |
| nhập nhằng | **M = 4**, $s \in [0.85, 0.95]$ | ~19 vật/km² |
| nhiễu | hiệu chuẩn lại theo §3.3 | |
| chân trời | **1200 s** | **cần biện minh — xem §3.5** |

### 3.5 Chân trời $T_{\max}$: hiện chưa có cơ sở

Tỉ lệ thất bại **hoàn toàn** do $T_{\max}$ quyết định, vì theo mô hình mới mọi
lược đồ đều thành công nếu chờ đủ lâu. Nên $T_{\max}$ **không được là một con số
tuỳ tiện**.

Kiểm tra: pin **không** phải ràng buộc trong mô hình hiện tại — các run tốn
70–200 kJ = 19–56 Wh cho cả đội, trong khi một pin multirotor cỡ 300 Wh cho
~1.7 h bay. Vậy 1200 s **không** đến từ giới hạn pin.

Cách xử lý sạch nhất: **công bố $\Pr[T\le t]$ dưới dạng đường cong**, khi đó
$T_{\max}$ chỉ còn là *một điểm đọc trên đường cong*, không phải tham số ẩn quyết
định kết luận. Bảng tóm tắt vẫn cần một $T_d$ để trích số, và **$T_d$ đó phải lấy
từ tài liệu SAR chứ không phải từ số liệu của ta** — lấy từ số liệu của ta là chọn
ngưỡng sau khi nhìn kết quả.

### 3.6 Ngân sách chạy

| thí nghiệm | nhánh | N | run | ghi chú |
|---|---:|---:|---:|---|
| ma trận chính 3×3 @ 24×24 | 9 | 120 | 1 080 | + `tsp-mc` = 1 200 |
| quét quy mô (16/24/32/40) | 3 rút gọn | 120 | 1 440 | A0B0, A2B0, A2B1 |
| quét nhập nhằng ($M$, $s$) | 3 rút gọn | 120 | ~1 080 | |
| quét chất lượng phát hiện | 3 rút gọn | 120 | ~1 080 | |
| **tổng** | | | **~4 800** | |

Ở 24×24 mỗi run ~30–60 s, chạy 3 luồng → **~15–25 giờ máy**. Khả thi nhưng phải
chạy một mạch trên **một binary** — nghĩa là **cài xong toàn bộ D1–D11 rồi mới
chạy**, không vừa chạy vừa sửa.

### 3.7 Câu hỏi cho bạn

- **Q3.1** Đồng ý đổi tham số sang đơn vị vận hành (§3.2) không? Nó làm bảng biểu
  dễ bảo vệ hơn nhưng phải viết lại script phân tích.
- **Q3.2** Điểm vận hành chính 24×24 / 6 UAV / M=4 có hợp lý không, hay bạn muốn
  lấy 40×40 làm chính (đắt hơn nhiều)?
- **Q3.3** $T_d$ để trích số trong bảng tóm tắt lấy từ đâu? Có tài liệu SAR nào
  bạn muốn dựa vào không?
- **Q3.4** Mật độ vật gây nhầm nên là bao nhiêu cho "thực tế"? Hiện M=4 trên
  0.21 km² ≈ 19/km², tôi không có cơ sở nào cho con số này.
- **Q3.5** Có cần quét **số UAV** như một trục riêng không, hay cố định 6 và để
  phần "thêm UAV" vào phụ lục?

### 3.8 Câu hỏi mở còn lại

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
