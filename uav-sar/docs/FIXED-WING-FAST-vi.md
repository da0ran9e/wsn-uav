# Nếu đội FAST là fixed-wing thì mô hình phải đổi những gì?

Câu hỏi: **đổi hướng bay động (dynamic re-routing) có phù hợp với fixed-wing
không?** Trả lời ngắn: **có, và đó là chuyện tiêu chuẩn** — fixed-wing được mô
hình hoá bằng **xe Dubins** (tốc độ không đổi, độ cong bị chặn), tài liệu về
Dubins path và loiter orbit cho fixed-wing rất dày.

Nhưng "bay lại được" không phải là câu hỏi đúng. Câu hỏi đúng là: **ba giả định
đang nằm trong mã nguồn sẽ sai**, và một trong ba có thể phá một cơ chế đang gánh
kết quả.

---

## 1. Ràng buộc thật của fixed-wing

| ràng buộc | hệ quả |
|---|---|
| không hover được, phải bay trên tốc độ thất tốc | "giữ vị trí" trở thành **bay vòng tròn** |
| bán kính lượn nhỏ nhất $R=\dfrac{v^2}{g\tan\varphi}$ | không rẽ tại chỗ; mọi lần bẻ lái tốn thêm quãng đường |
| hiệu quả cao ở tốc độ hành trình | rẻ hơn rotary-wing khi bay, **vô dụng khi cần đứng yên** |

Với thông số hiện tại của dự án ($v=20$ m/s):

| góc nghiêng $\varphi$ | $R_{\min}$ | cự ly xiên tới nút ở tâm vòng (cao độ 20 m) | trong tầm A2G 50 m? |
|---:|---:|---:|:--:|
| 30° | **70.6 m** | 73.4 m | **KHÔNG** |
| 45° | 40.8 m | 45.4 m | có (biên, dư 9 %) |
| 30°, nhưng $v=13$ m/s | 29.8 m | 35.9 m | có |

## 2. Cơ chế bị đe doạ: `kRelayGraceS` (giữ vị trí 30 s làm trạm chuyển tiếp)

Đây là chỗ nghiêm trọng nhất, vì cơ chế này **đang gánh kết quả**: một FAST UAV
bay xong vòng quét phải nán lại 30 s để còn ai đó trên trời chuyển tiếp lệnh
SUMMON. Với rotary-wing, "nán lại" = hover ngay trên đầu → cự ly xiên 20 m, thừa
thãi. Với fixed-wing, "nán lại" = **bay vòng bán kính $R_{\min}$**, và bảng trên
nói:

> Ở 20 m/s với góc nghiêng 30°, một fixed-wing bay vòng **không bao giờ** nằm
> trong tầm A2G 50 m của nút ở tâm. Trạm chuyển tiếp biến mất.

Ba lối thoát, phải chọn và khai báo:

1. **Nghiêng gắt hơn (45°)** — $R=40.8$ m, dư 9 % so với tầm 50 m. Rất mỏng, và
   45° nghĩa là chịu tải 1.41 g liên tục.
2. **Bay chậm hơn khi làm trạm chuyển tiếp** (13–15 m/s) — hợp lý, fixed-wing nhỏ
   thất tốc quanh 12–14 m/s. Nhưng lúc đó tốc độ quét cũng giảm.
3. **Bỏ khái niệm "giữ vị trí"**, thay bằng **liên lạc theo lượt bay qua**
   (intermittent contact): FAST bay vòng lớn và SUMMON được chuyển tiếp mỗi khi
   nó bay ngang. Đúng vật lý hơn cả, nhưng biến bài toán hẹn gặp (P2) từ "có mặt"
   thành "gặp nhau theo chu kỳ" — và bài toán đó khó hơn hẳn.

**Không được lặng lẽ giữ nguyên `kRelayGraceS` rồi gọi đội FAST là fixed-wing.**

## 3. Mô hình năng lượng đang SAI cho fixed-wing

`params::EnergyPowerW` là đường cong **rotary-wing** (Zeng–Xu–Zhang 2019). Fixed-
wing có dạng hoàn toàn khác ([Zeng & Zhang, *Energy-Efficient UAV Communication
with Trajectory Optimization*, IEEE TWC 2017](https://arxiv.org/pdf/1608.01828)):

$$P(v,a)=c_1v^3+\frac{c_2}{v}\left(1+\frac{a^2}{g^2}\right)$$

Khác biệt căn bản: rotary-wing tốn năng lượng **ngay cả khi đứng yên** (lực nâng
do rotor), fixed-wing lấy lực nâng từ cánh nên **không có số hạng hover**, đổi
lại **không có $v=0$**.

Hệ quả cho bài báo: ở tốc độ hành trình, fixed-wing rẻ hơn rotary-wing đáng kể,
nên **mô hình hiện tại đang ĐÁNH GIÁ THẤP lợi ích của việc dùng fixed-wing cho
FAST**. Điều đó liên quan trực tiếp tới vấn đề mở số 1 (`proposed` thua
`closed-loop` 12 % năng lượng) — nhưng lưu ý `closed-loop` dùng **cùng đội bay**,
nên nó cũng được lợi y hệt; đây **không** phải cách để thắng nhánh đó.

**Việc phải làm nếu đổi:** thêm đường cong fixed-wing riêng và gắn theo vai trò.
Trộn hai loại khung máy bay mà dùng chung một đường cong công suất là đúng loại
lỗi mà audit F1 đã bắt được một lần rồi (khi ấy là tốc độ hai tầng không có gì
trong mô hình thực hiện nó).

## 4. Điều bất ngờ: fixed-wing **biện minh** cho kiến trúc hai đội

Hiện tại việc chia FAST/DATA là một lựa chọn thiết kế **không có cơ sở vật lý** —
audit F1 thậm chí đã phải gỡ bỏ chênh lệch tốc độ hai tầng vì không có gì trong
mô hình thực hiện nó. Nếu FAST là fixed-wing và DATA là rotary-wing thì:

| vai trò | yêu cầu | khung máy bay phù hợp |
|---|---|---|
| FAST: quét rộng, rải cue, **không bao giờ dừng**, đưa báo cáo về BS | bay xa, nhanh, hiệu quả hành trình | **fixed-wing** |
| DATA: đứng trên một điểm 20–40 s để rải hết tập dữ liệu | **giữ vị trí** | **rotary-wing** |

Sự phân công đó trở thành **hệ quả của vật lý chứ không phải sở thích thiết kế**
— một lập luận mạnh hơn nhiều cho phần thiết kế hệ thống của bài báo.

Lưu ý trung thực: DATA **cũng** có thể là fixed-wing bay vòng bán kính 40.8 m
(cự ly xiên 45.4 m < 50 m), nên nói "fixed-wing không giao dữ liệu được" là **quá
mạnh**. Nói đúng: biên rất mỏng, và dwell giao dữ liệu là chỗ rotary-wing thắng
rõ.

## 5. Về việc bàn giao báo cáo cho FAST — **đã cài đặt và đang chạy**

Kiểm chứng từ dữ liệu, không phải từ mã: mọi run đều có `report_pickup = 1`, tức
là một FAST UAV **thật sự** nhận HANDOFF, giành quyền đưa tin bằng CLAIM trên
radio, và mang bản tin (kèm toạ độ) về BS. Cơ chế này có sẵn từ trước.

Nếu FAST là fixed-wing thì vai trò đưa tin **càng hợp** (bay xa, nhanh, không cần
dừng). Chỗ duy nhất cần xem lại là **thời điểm nhận bàn giao**: DATA phát HANDOFF
khi đang ở trên vùng giao dữ liệu, và một fixed-wing chỉ bay ngang qua theo chu
kỳ — nên bàn giao trở thành sự kiện **theo lượt gặp**, cần phát lại cho tới khi
có một lượt bay qua. Hiện `kConfirmRetries = 5` lần cách nhau 0.5 s = **2.5 s**,
gần như chắc chắn quá ngắn so với chu kỳ một vòng lượn ($2\pi R/v \approx 13$ s ở
$R=40.8$ m).

## 6. Tóm tắt: đổi được, nhưng phải đổi 3 thứ

| # | hạng mục | trạng thái |
|---|---|---|
| 1 | Đổi hướng bay động | **phù hợp** — Dubins, chuyện tiêu chuẩn |
| 2 | `kRelayGraceS` "giữ vị trí" | **sẽ hỏng** ở 20 m/s + nghiêng 30°; phải chọn một trong ba lối thoát ở §2 |
| 3 | Đường cong năng lượng | **đang sai**; cần mô hình fixed-wing riêng theo vai trò |
| 4 | Cửa sổ phát lại HANDOFF (2.5 s) | **quá ngắn** so với chu kỳ vòng lượn ~13 s |
| 5 | Biện minh kiến trúc hai đội | **được lợi** — trở thành lập luận vật lý |

Chưa làm gì trong số này. Đây là ghi chép để quyết định, không phải thay đổi đã
thực hiện — vì đổi khung máy bay là thay đổi giả thiết mô hình, và nó phải được
khai báo trong bài chứ không trôi vào mã.
