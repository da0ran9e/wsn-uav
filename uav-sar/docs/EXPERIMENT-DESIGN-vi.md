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

### 1.6 Câu hỏi mở — cần bạn trả lời

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
