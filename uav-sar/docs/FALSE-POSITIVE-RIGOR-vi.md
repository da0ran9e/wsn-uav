# Dương tính giả và tính chặt chẽ của bài báo

Tài liệu này **không** so sánh với baseline. Nó xử lý một lỗ hổng về tính hợp lệ:
mọi kết quả đã đo của dự án đều ngầm dựa trên một giả định chưa từng được viết ra,
và giả định đó sai trong thực tế với tần suất lớn.

> **Giả định A (tính duy nhất).** Trong vùng tìm kiếm chỉ có **một** vật thể khớp
> với tập dữ liệu tham chiếu.

Ví dụ của bạn — nhiều người mặc cùng một mẫu trang phục — là một phản ví dụ
thường gặp, không phải trường hợp biên. Trong SAR còn có những phản ví dụ nặng
hơn: nhóm đi cùng nạn nhân, quần áo bỏ lại, và **chính đội cứu hộ mặc đồng phục**.

---

## 1. Hai thứ khác nhau đang bị gọi chung là "dương tính giả"

| | nhiễu bộ phát hiện | nhập nhằng của thế giới |
|---|---|---|
| bản chất | **epistemic** — cảm biến đo sai | **aleatoric** — thế giới thật sự có hai vật giống nhau |
| nút báo cao là | **sai** | **đúng** |
| giảm được bằng | quan sát lâu hơn, lấy trung bình, SNR tốt hơn | **không** giảm được bằng cùng phương thức cảm biến |
| cận dưới lý thuyết | CRLB (liên tục) | **sai số Bayes** $\ge$ hàm của độ tương đồng (rời rạc) |
| trong mã (trước) | `senseSigma` | **không tồn tại** |

Đây là điểm mấu chốt và nó có hệ quả thực tế: nếu mô hình hoá "nhiều người mặc áo
giống nhau" bằng cách **tăng `senseSigma`**, ta ngầm khẳng định rằng một cảm biến
tốt hơn sẽ giải quyết được vấn đề. Sai. Với hai chiếc áo giống hệt, một camera
độ phân giải vô hạn vẫn cho hai kết quả khớp như nhau. **Nhập nhằng phải được mô
hình hoá là nhập nhằng, không phải là nhiễu.**

Nó cũng giải thích vì sao mô hình cũ không thể sinh ra nhiều điểm yêu cầu (đo
được ở `PROBLEM-MULTI-CANDIDATE-vi.md`: $K=1$ trong 94.2 % số run): nhánh dương
tính giả nền bị chặn ở `maxNoiseQuality = 0.18`, dưới ngưỡng báo động 0.75 rất
xa. Mô hình cũ **chỉ có** dương tính giả loại nhiễu, và cố ý làm chúng yếu.

## 2. Mô hình đã cài đặt

`ClutterSource` trong `models/common/clue-field.h`:

```cpp
struct ClutterSource { double x, y; double similarity; };  // similarity in [0,1]
```

Trường bằng chứng tại nút $i$ là **giá trị khớp tốt nhất mà bộ phát hiện tìm
được**, bất kể vật nào tạo ra nó:

$$q_i=\max\Big(g(\|p_i-v\|),\ \max_{m=1..M} s_m\, g(\|p_i-c_m\|)\Big),\qquad
\hat q_i=\mathrm{clip}\big(q_i+\sigma\varepsilon_i\big)$$

Ba quyết định thiết kế, đều có lý do:

1. **Dùng chung nhân $g(\cdot)$** cho nạn nhân và vật gây nhầm. Nếu cho chúng
   hình dạng khác nhau thì tầng gộp bằng chứng có thể phân biệt bằng *hình dạng*,
   tức là ta lén trả lại đúng khả năng phân biệt mà bài toán nói là không có.
2. **Luồng RNG riêng** (`seed ^ 0x9E3779B9`) để đặt vật gây nhầm. Nhờ vậy
   `clutterCount = 0` tái lập **y hệt từng bit** mọi kết quả đã đo — đã kiểm
   chứng: `candidate_stats 16 0.10 120` cho ra đúng các con số cũ. Nếu rút thêm
   số từ luồng chính thì mọi quyết định dương-tính-giả nền sẽ dịch đi và toàn bộ
   kết quả lịch sử âm thầm thay đổi.
3. **`sourceId` chỉ dùng để phân tích.** Không ứng dụng nào được đọc nó — đó là
   một oracle, và audit B1 đã gỡ bỏ oracle cuối cùng của dự án.

Cờ dòng lệnh: `--clutterCount=M --clutterSimMin=a --clutterSimMax=b`.

## 3. Trần khả phân biệt

Đo tỉ lệ chọn đúng của **quy tắc đỉnh** — tin nút mạnh nhất, đúng thứ
`--aimArgmax` đang làm (`tools/candidate_stats.cc`, 16×16, $\sigma=0.10$,
$N=120$):

| tương đồng $s$ | $M=1$ | $M=2$ | $M=4$ | lý thuyết tại $s=1$ |
|---:|---:|---:|---:|---:|
| 0.70 | 99.2 % | 98.3 % | 94.9 % | — |
| 0.85 | 84.0 % | 83.2 % | 60.8 % | — |
| **1.00** | **41.7 %** | **33.3 %** | **20.8 %** | $1/(M+1)$ = 50 / 33.3 / 20 % |

Tại $s=1$ số đo khớp $1/(M+1)$ (điểm $M=1$ thấp hơn kỳ vọng $\approx1.8\sigma$,
trong khoảng tin cậy). Cần đọc bảng này cho thật đúng, vì có **hai** phát biểu ở
đây và chỉ một trong hai là cận:

- **Tại $s=1$, $1/(M+1)$ là cận thông tin thật sự.** Hàm hợp lý đối xứng hoàn
  toàn giữa các vật thể, nên **không** bộ ước lượng nào — dù thông minh đến đâu,
  dù gộp bao nhiêu nút — vượt qua được. Ở đó **41.7 % không phải là điểm kém của
  bộ điều khiển; một hệ thống đạt 41.7 % là tối ưu.**
- **Tại $s<1$ các con số trên KHÔNG phải cận.** Chúng là hiệu năng của một quy
  tắc cụ thể (quy tắc đỉnh). Vật thể thật có biên độ cao hơn, nên một bộ ước
  lượng **gộp bằng chứng trong cụm** sẽ giảm phương sai biên độ và làm tốt hơn.
  Khoảng cách đó chính là chỗ tầng hợp tác có giá trị.

Thử ngay quy tắc thứ hai — chọn cụm có **tổng** bằng chứng lớn nhất (so sánh theo
cặp trên cùng bộ hạt giống, kiểm định McNemar chính xác):

| | $s=0.70$ | $s=0.85$ | $s=1.00$ |
|---|---|---|---|
| $M=1$ | +0.8 pp (p=0.25) | +3.4 pp (p=0.42) | +0.8 pp (p=1.00) |
| $M=2$ | +0.9 pp (p=0.25) | +0.8 pp (p=1.00) | −4.2 pp (p=0.51) |
| $M=4$ | +2.6 pp (p=0.25) | **+9.2 pp (p=0.061)** | −2.5 pp (p=0.69) |

Kết luận trung thực: **không ô nào đạt ý nghĩa thống kê ở mức 0.05.** Hai điều
đọc được:

1. **Tại $s=1.00$ chênh lệch bằng 0 trong sai số lấy mẫu** (cặp bất đồng
   $b\approx c$: 16/17, 21/16, 14/11) — **đúng như lý thuyết bắt buộc**. Đây là
   một phép kiểm tra tính nhất quán đã vượt qua, không phải kết quả rỗng.
2. **Điểm $M=4,\ s=0.85$ là manh mối duy nhất** (+9.2 pp, $p=0.061$). Nó nằm đúng
   chỗ lý thuyết dự đoán: vùng nhập nhằng **trung gian**, nơi vẫn còn thứ để phân
   biệt nhưng một nút đơn lẻ thì không đủ. Chưa đủ để phát biểu; đủ để theo đuổi
   bằng $N$ lớn hơn và lưới $s$ mịn hơn.

Cần nói rõ vì sao điều này quan trọng: nếu manh mối trên đứng vững, nó là **cơ chế
cụ thể trả lời vấn đề mở số 1 trong `STATUS.md`** (hợp tác trả giá ở đâu?). Câu
trả lời sẽ là *ở vùng nhập nhằng trung gian*, và nó có dạng chữ U ngược — bằng 0 ở
cả hai đầu (dễ quá thì không cần, bất khả thì không thể).

## 4. Chỉ số hiện tại **vỡ** dưới nhập nhằng — đây là rủi ro phản biện lớn nhất

Sai số định vị trở thành **hỗn hợp hai chế độ**. Đo ở mức trường manh mối
(khoảng cách từ đỉnh cụm được chọn tới nạn nhân, $N=120$, mọi $M$ và $s$):

| | chọn đúng người | chọn nhầm người |
|---|---:|---:|
| sai số median | 8–10 m | **185–237 m** |

Chênh nhau **hơn 20 lần**. Vì thế:

- **`reportErr_m` mất ý nghĩa khi lấy median/p90 trên hỗn hợp.** Nếu tỉ lệ chọn
  nhầm vượt 10 %, **p90 nhảy bậc** từ ~30 m sang ~200 m. Đó không phải suy giảm
  trơn — đó là một điểm gián đoạn, và một bài báo báo cáo p90 mà không tách chế độ
  sẽ trình bày một con số vô nghĩa.
- Con số **"hợp tác giảm 29 % p90 sai số"** trong `STATUS.md` **chỉ đúng dưới giả
  định A**. Phải ghi rõ như vậy.

Một run thật minh hoạ (seed 3, $M=2$, $s=0.9$):

```
victim (204.2, 115.8)   reported (32.4, 107.0)
reportErr_m           = 171.99      <- schema cũ ghi nhận là "sai số ước lượng"
fixOnVictim           = 0           <- thực chất: đóng vòng vào NHẦM NGƯỜI
fixToNearestClutter_m = 36.95       <- và cách vật gây nhầm chỉ 37 m
```

Nghĩa là hệ thống **hoạt động đúng**: nó định vị chính xác một vật thể khớp với
dữ liệu tham chiếu, cách 37 m. Nó chỉ khớp nhầm vật. Schema cũ ghi lại chuyện đó
thành "sai số 172 m" — trộn lẫn hai sự kiện có ý nghĩa hoàn toàn khác nhau.

**Đã sửa:** `metrics.csv` thêm `clutterCount, fixOnVictim, fixToNearestClutter_m`;
`config.txt` thêm dòng `clutter=M,simMin,simMax` và `campaign_common.assert_one_clutter`
**từ chối** tổng hợp các run khác chế độ nhập nhằng (cùng lý do với
`assert_one_build`: trộn vào vài run là đủ kéo lệch đuôi mà nhìn không ra).

### 4.1. Số liệu hệ thống — $M=2$, 16×16, $N=120$ mỗi mức

Chạy thật qua ns-3 (`proposed`, `senseSigma=0.10`, `gpsSigma=5`, `victimOnNode=0`):

| $s$ | nạn nhân được phục vụ | `fixOnVictim` | **trần** $1/(M{+}1)$ | sai số median (gộp) | p90 (gộp) | sai số median **có điều kiện đúng** | p90 có điều kiện | thời gian | năng lượng |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| — ($M=0$) | 92.5 % | — | — | 14.6 m | 29.9 m | 14.6 m | 29.9 m | 103.9 s | 68.3 kJ |
| 0.70 | 55.8 % | 61.7 % | — | 25.2 m | **253.9 m** | 14.5 m | 33.3 m | 103.6 s | 64.4 kJ |
| 0.85 | 40.0 % | 44.5 % | — | **162.4 m** | **257.9 m** | 13.9 m | 31.6 m | 103.6 s | 64.4 kJ |
| 1.00 | **34.2 %** | 39.2 % | **33.3 %** | 165.0 m | 259.2 m | 14.2 m | 24.8 m | 103.6 s | 64.4 kJ |

Năm điều đọc được, tất cả đều quan trọng:

1. **Tại $s=1.00$ hệ thống nằm ĐÚNG TRÊN TRẦN**: 34.2 % so với $1/3$. Không có gì
   để sửa ở đó — đó là giới hạn thông tin, không phải khuyết điểm kỹ thuật.
2. **Sai số có điều kiện chọn đúng KHÔNG đổi** (13.9–14.5 m, y hệt 14.6 m của
   $M=0$) ở mọi mức $s$. Bộ ước lượng hoàn toàn không suy giảm — **chỉ khâu chọn
   ứng viên hỏng**. Đây là bằng chứng trực tiếp cho luận điểm hai chế độ ở §4.
3. **Phân vị gộp vô nghĩa đúng như dự đoán.** p90 nhảy lên ~254 m ngay ở $s=0.70$
   (vì 38 % chọn sai > 10 %), và **median lật** giữa 0.70 và 0.85 khi tỉ lệ chọn
   đúng đi qua 50 % (25.2 m → 162.4 m). Không phải suy giảm trơn — là điểm gián
   đoạn của một hàm phân vị trên hỗn hợp.
4. **Thời gian và năng lượng KHÔNG đổi** (103.6 s / 64.4 kJ ở cả ba mức). Đây là
   chữ ký của kiến trúc "cam kết một ứng viên": hệ thống không trả thêm chi phí
   nào và cũng không thu được gì — nó **chỉ đơn giản là thất bại trong im lặng**.
   Một hệ thống có xử lý nhập nhằng sẽ phải thấy chi phí tăng theo $M$ (đi thăm
   nhiều ứng viên) và độ tin cậy được mua lại bằng chi phí đó.
5. **`fix%` xấp xỉ 100 % ở mọi mức.** Hệ thống **luôn** báo về một vị trí, với
   cùng mức tự tin, kể cả khi nó sai 2/3 số lần. Đây là bài toán hiệu chuẩn ở dạng
   trần trụi nhất: **hệ chưa bao giờ nói "tôi không chắc"**.

### 4.2. Một khoảng cách chưa giải thích được — và một confound tôi tự tạo ra

Ở $s=0.70$, quy tắc đỉnh trên trường manh mối chọn đúng **98.3 %** (§3), nhưng hệ
thống chỉ đạt **61.7 %**. Chênh lệch ~37 pp này **không** phải giới hạn thông tin
— nó là kiến trúc. Giả thuyết: `--electSuppress` chọn cụm **bầu xong trước**, chứ
không phải cụm **mạnh nhất toàn cục**, vì SHARE chỉ lan `kShareTtl = 4` hop.

Nhưng **tôi không được kết luận điều đó từ thí nghiệm này**, vì tôi đã tự tạo ra
một confound: `clutterMinSepM = 150 m` mặc định, trong khi tầm lan của SHARE là
$4 \times R_g \approx 4 \times 37 = 148$ m. Hai cụm nằm **đúng ngay biên** của bán
kính gộp bằng chứng. Vì thế số liệu trên **không tách được** hai giả thuyết:

- (a) bầu cử quyết định theo *thời điểm* chứ không theo *cường độ*, hay
- (b) hai cụm đơn giản là nằm ngoài tầm so sánh của nhau.

**Thí nghiệm để tách:** quét `clutterMinSepM` qua ngưỡng 148 m (ví dụ 80 / 120 /
150 / 250 m). Nếu là (b), tỉ lệ chọn đúng phải **nhảy** khi khoảng cách xuống dưới
tầm SHARE. Nếu là (a), nó phẳng. Chưa chạy — ghi lại làm việc kế tiếp, và **không
được trích khoảng cách 37 pp như một kết luận về bầu cử** cho tới khi chạy xong.

**Bộ chỉ số nên dùng khi $M>0$:**

| chỉ số | vì sao |
|---|---|
| $\Pr[\text{fixOnVictim}]$ | tách chế độ; so với trần ở §3 |
| sai số **có điều kiện** chọn đúng | mới là chỉ số ước lượng thật sự |
| **recall@$b$**: nạn nhân có nằm trong $b$ điểm được phục vụ đầu tiên không | dưới nhập nhằng, đây là chỉ số vận hành đúng đắn |
| công phí phục vụ nhầm (J, gói tin) | chi phí chỉ tồn tại khi $M>0$ |
| hiệu chuẩn xác suất (ECE / reliability diagram) | hệ nói "0.9" thì phải đúng 90 % số lần |

## 5. Bốn chỗ trong kiến trúc **đang giả định tính duy nhất**

Không phải khuyết điểm ẩn — chúng là hệ quả thiết kế hợp lý dưới A, và cần được
nêu tên trong bài báo:

| # | cơ chế | hỏng thế nào khi $M>0$ |
|---|---|---|
| 1 | `--electSuppress`: một SUMMON mỗi run | vứt $M$ ứng viên **trước** mọi quyết định |
| 2 | SUMMON chở **một** điểm (8 B) | không có kênh nào để chở danh sách ứng viên |
| 3 | `--aimArgmax`: một điểm ngắm | biến bài toán *chọn giả thuyết* thành *ước lượng điểm* |
| 4 | Đóng vòng khi **CONFIRM đầu tiên** | vốn đã sai (vấn đề mở số 2); dưới nhập nhằng thì hỏng nặng hơn — vòng lặp đóng lại trên người ngoài cuộc và **không ai biết** |

Điểm 4 đáng nhấn: hiện tại **bất kỳ** nút nào tái tạo đủ dữ liệu đều phát CONFIRM.
Với $M>0$, việc đó cho phép nhiệm vụ kết thúc "thành công" trong khi nạn nhân
chưa hề được phục vụ, **và hệ thống không có tín hiệu nào để biết**. Dưới giả
định A, ít nhất người nhận cũng ở gần nạn nhân.

## 6. Ngưỡng phải suy ra từ hàm mất mát bất đối xứng

`kAlertThreshold = 0.75` và `kCoopThreshold = 0.30` hiện là hằng số không có căn
cứ. Dưới nhập nhằng thì không thể để vậy, vì hai loại sai lầm **không đối xứng**:

$$L_{\text{miss}}\ \ggg\ L_{\text{false serve}}$$

Bỏ sót nạn nhân là hỏng nhiệm vụ; phục vụ nhầm một người tốn $2d/V+s\approx45$–70 s
và có thể sửa. Quy tắc quyết định tối ưu Bayes là ngưỡng theo **tỉ số mất mát**:

$$\text{phục vụ } k \iff \pi_k > \frac{L_{\text{false serve}}}{L_{\text{miss}}+L_{\text{false serve}}}$$

Với tỉ số 1:20 thì ngưỡng $\approx 0.048$ — tức là **phục vụ gần như mọi ứng viên
đáng kể**, hoàn toàn ngược với ngưỡng 0.75 hiện tại. Đây là một lập luận thiết kế
mạnh và độc lập với mọi số đo: dưới nhập nhằng, chiến lược đúng nghiêng hẳn về
**phủ tập ứng viên** chứ không phải chọn điểm tốt nhất. Nó cũng cho `deliverDwell`
và bài toán P6 một nền tảng lý thuyết thay vì chỉ là một đường cong đo được.

## 7. Cái gì thật sự phá được nhập nhằng (và cái gì thì không)

**Không** có tác dụng: cảm biến tốt hơn cùng phương thức, quan sát lâu hơn, nhiều
nút hơn, thuật toán gộp thông minh hơn. Tất cả đều bị chặn bởi §3.

**Có** tác dụng:

1. **Phương thức cảm biến khác** — ảnh nhiệt, gọi–đáp có xác nhận, tín hiệu điện
   thoại. Nếu bài báo muốn dùng lập luận này thì phải **khai báo thành giả thiết
   mô hình**, không được lặng lẽ cho đội FAST một siêu năng lực.
2. **Thời gian — dấu hiệu mạnh nhất và đang bị vứt bỏ.** Nạn nhân bị thương thì
   **bất động**; người khoẻ mạnh mặc áo giống thì **di chuyển**. Mô hình hiện tại
   rút nhiễu **một lần cho mỗi nút cho cả run**, nên trường bằng chứng là tĩnh
   theo định nghĩa và tín hiệu này không tồn tại. Cho vật gây nhầm một vận tốc
   nhỏ ($\sim1$ m/s) là thay đổi nhỏ, và nó tạo ra một bộ phân biệt **thật sự**:
   độ ổn định không gian của cụm theo thời gian. Theo tôi đây là hướng có giá trị
   khoa học cao nhất trong toàn bộ tài liệu này.
3. **Tiên nghiệm ngữ cảnh** — điểm xuất phát, đường mòn, thời gian mất tích. Biến
   $\pi_k$ từ đồng đều thành có cấu trúc, tức là kéo trần ở §3 lên.
4. **Cấu trúc cụm** — một nhóm người đi cùng nhau tạo cụm bằng chứng **rộng hơn**
   một người nằm một chỗ. Có thể khai thác được, nhưng chỉ khi nhân $g$ khác nhau
   giữa hai loại — và như §2 đã nói, cho khác nhau là tự tặng mình khả năng phân
   biệt. Phải cẩn thận, chỗ này rất dễ tự lừa mình.

## 8. Hạn chế phải ghi trong bài (đừng để phản biện tìm ra trước)

- **Vật gây nhầm được đặt đều và đứng yên.** Thực tế chúng **tương quan**: nhóm đi
  cùng nạn nhân thì ở *gần* nạn nhân (mô hình đều sẽ bỏ sót chế độ này, và đó là
  chế độ **dễ** hơn); còn **đội cứu hộ mặc đồng phục thì di chuyển cùng UAV** —
  chế độ này khó hơn nhiều và mô hình hiện tại hoàn toàn không có.
- **Độ tương đồng là một số vô hướng.** Thực tế bộ phát hiện cho một vector đặc
  trưng; hai vật có thể khớp mạnh ở màu áo nhưng khác ở dáng người. Trừu tượng vô
  hướng chính là thứ tạo ra trần ở §3 — nói rõ như vậy thì trần là một **kết quả
  có điều kiện đã khai báo**, không phải một giới hạn được nguỵ trang thành định
  luật.
- **$\pi_k$ chưa được hiệu chuẩn.** Hệ chưa hề xuất ra một xác suất; nó xuất ra
  một điểm. Mọi phát biểu kiểu Bayes ở §6 hiện là quy tắc thiết kế, chưa phải thứ
  đo được.

## 9. Cách trình bày trong bài báo

Đừng viết "chúng tôi cũng xử lý được dương tính giả". Hãy viết **đường bao vận
hành**:

1. Nêu **giả định A** ở phần mô hình hệ thống, kèm câu rằng SAR thực tế thường vi
   phạm nó.
2. Kết quả chính giữ nguyên **dưới A** ($M=0$), gắn nhãn rõ ràng.
3. Thêm một mục **suy giảm theo $s$ và $M$**, luôn vẽ kèm **trần khả phân biệt**.
   Thông điệp: *hệ thống bám sát trần cho tới $s\approx0.85$; từ đó trở đi mọi bộ
   ước lượng dùng một phương thức đều thất bại, và lối thoát duy nhất là phủ tập
   ứng viên hoặc thêm phương thức cảm biến.*
4. Nêu bốn chỗ giả định duy nhất ở §5 như **công việc tương lai có định hướng**,
   chứ không phải khuyết điểm bị phát hiện.

Cách này biến một điểm yếu thành một **đóng góp**: bài báo là bài duy nhất trong
nhóm nêu tên giả định, đo trần lý thuyết, và chỉ ra chính xác chỗ kiến trúc gãy.
Phản biện gần như chắc chắn sẽ hỏi về nhập nhằng nhận dạng; trả lời trước bằng số
liệu luôn tốt hơn là bị hỏi.

---

## 10. Đã làm / còn lại

**Đã cài đặt và kiểm chứng:**

| tệp | thay đổi |
|---|---|
| `models/common/clue-field.{h,cc}` | `ClutterSource`, `BuildClutter`, nhân $g$ dùng chung, luồng RNG riêng, `sourceId` |
| `models/common/sar-metrics.{h,cc}` | `SetClutter`, cột `clutterCount, fixOnVictim, fixToNearestClutter_m` |
| `helper/sar-config.{h,cc}`, `examples/scenario-sar.cc` | cờ `--clutterCount/--clutterSimMin/--clutterSimMax` |
| `tools/candidate_stats.cc` | trần khả phân biệt + tách hai chế độ sai số |

**Cách dùng như một tham số** (đúng mục đích: giữ so sánh baseline ở chế độ cũ,
và bật lên khi cần kiểm chứng độ thực tế):

```bash
--clutterCount=0                         # mặc định: giả định duy nhất, K=1.
                                         # Tái lập y hệt mọi kết quả cũ.
--clutterCount=2 --clutterSimMin=0.85 --clutterSimMax=0.85   # quét độ thực tế
```

Hàng rào: `config.txt` ghi `clutter=M,min,max`, và `assert_one_clutter` khiến mọi
script tổng hợp **báo lỗi thay vì âm thầm trộn** hai chế độ.

**Còn lại, theo thứ tự giá trị:**

0. Quét `clutterMinSepM` để gỡ confound ở §4.2 — rẻ, và đang chặn một kết luận.
1. Vật gây nhầm **di chuyển** (§7.2) — dấu hiệu phân biệt thật, và không đắt.
2. Cho ứng dụng xuất **$\pi_k$ có hiệu chuẩn**, đo ECE (§4).
3. Ngưỡng suy từ tỉ số mất mát (§6), thay hằng số 0.75.
4. Sửa tiêu chí đóng vòng CONFIRM (§5.4) — vốn đã là vấn đề mở số 2.
5. Chế độ vật gây nhầm **tương quan** (nhóm đi cùng; đội cứu hộ) (§8).
