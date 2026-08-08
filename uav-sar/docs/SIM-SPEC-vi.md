# Đặc tả giả lập thống nhất — v1 (2026-08-08)

Tài liệu **chốt**, rút ra từ `EXPERIMENT-DESIGN-vi.md` Phần 1–5. Khác nhau về vai
trò:

| tài liệu | vai trò |
|---|---|
| `EXPERIMENT-DESIGN-vi.md` | **nhật ký thảo luận** — có cả ý đã bị bác, có lập luận, đọc để hiểu *vì sao* |
| **`SIM-SPEC-vi.md` (đây)** | **đặc tả** — chỉ cái đã chốt, đọc để *cài và chạy* |
| `STATUS.md` | trạng thái đo đạc — số nào tin được |

Quy tắc: **mâu thuẫn giữa hai tài liệu thì tài liệu này thắng.** Mọi mục còn mở
được đánh dấu **[MỞ]** và liệt kê tập trung ở §10 — không được tự suy diễn thành
quyết định.

---

## 1. Thế giới

- Vùng $\mathcal{A}$ hình vuông, lưới $N\times N$ cảm biến tĩnh, BS ở gốc.
- **Một** nạn nhân thật tại vị trí liên tục $v$ (không bắt buộc trùng nút).
- **$M$ nạn nhân giả** tại $c_1..c_M$, độ tương đồng $s_m\in[0,1]$. Chúng giống
  tập tham chiếu **đủ để đánh lừa tầng cue**, không phải nhiễu cảm biến.
- $M=0$ cho **mọi so sánh chính** (D14). $M>0$ chỉ dùng ở phần "khả năng vận
  hành" của bài báo.

## 2. Cảm biến — hai tầng

Chất lượng khớp **thật** của nút $i$ phụ thuộc lượng dữ liệu tham chiếu nó đang
giữ, $C_i\in[0,1]$:

$$q_i(C_i)=\max\Big(g(\lVert p_i-v\rVert),\ \max_m s_m\,(1-C_i)\,g(\lVert p_i-c_m\rVert)\Big)$$

Số **đo được** dùng nhiễu **phụ thuộc tín hiệu** (D3, thay cho nhiễu cộng cũ):

$$\hat q_i=\mathrm{clip}_{[0,1]}\big(q_i+\sigma\,(q_i+q_0)\,\varepsilon_i\big),
\qquad \varepsilon_i\sim\mathcal N(0,1),\quad q_0=0.05$$

Hệ quả bắt buộc phải giữ: **nút không có vật thể nào gần thì không thể xác nhận**
— tính chất này phải đúng *theo cấu trúc*, không nhờ chỉnh ngưỡng.

**Ràng buộc hiệu chuẩn (bắt buộc, không được bỏ qua):** $\sigma$ mới **không cùng
đơn vị** với `senseSigma` cũ (độ lệch hiệu dụng $0.85\sigma$ ở nút nạn nhân,
$0.05\sigma$ ở nút trắng). Trước khi chạy bất kỳ so sánh nào, chọn $\sigma$ sao
cho **xác suất nút gần nạn nhân nhất vượt `kAlertThreshold` bằng đúng giá trị của
mô hình cũ**, và ghi bảng hiệu chuẩn vào repo.

## 3. Đội bay — hai khung máy bay

| | FAST | DATA |
|---|---|---|
| khung | fixed-wing | rotary-wing |
| tốc độ | **25 m/s** (`kFastSpeedMps`) | **15 m/s** (`kDataSpeedMps`) |
| giữ vị trí | không | có |
| việc | quét, rải **cue**, đưa báo cáo về BS | tuần tra rải **full data**, giao hàng khi được triệu tập |

Phân công là **hệ quả vật lý**: quét cần khung không dừng; dwell giao hàng 20–40 s
cần khung giữ vị trí.

## 4. Payload — con số ĐÚNG (sửa lỗi trong nhật ký thảo luận)

`EXPERIMENT-DESIGN-vi.md` §1.7/§1.14 ghi "tập đầy đủ 18 400 B ≈ 184 chunk, 7.7×
so với cue". **Sai.** Đọc `target-profile.h` + `SendFullChunk`:

| | byte | chunk 91 B | |
|---|---:|---:|---|
| L0 cue | 8×150 = 1 200 | 16 | FAST rải |
| L1 mô tả | 2×600 = 1 200 | 14 | FAST rải |
| L2 chi tiết | 4×4 000 = 16 000 | 176 | DATA giao |
| L3 đầy đủ | 1×16 000 = 16 000 | 176 | DATA giao |
| **cue (L0+L1)** | **2 400** | **30** | |
| **full (L0..L3)** | **34 400** | **382** | `m_full = tp.All()` |

Tỉ số thật: **14.3× về byte, 12.7× về gói tin** — không phải 7.7×. Điều này làm
**nặng thêm** cả ba rủi ro của D1/D2: rải full data khi tuần tra tốn hơn ~1.7 lần
so với đã đánh giá, và tiếp sức nội ô phải chuyển **382 chunk**, không phải 184.

**Hệ quả cho thiết kế:** D1 (tuần tra rải full data) và D11 (tiếp sức) **phải đo
chi phí gói tin trước khi coi là mặc định**. Nếu 24×24 hiện đã 12–15k gói thì D1
có thể đẩy lên trên 100k.

## 5. Hợp tác mặt đất — HAI mặt phẳng trực giao

1. **Mặt phẳng bằng chứng** *(đã có)* — RPT lên cây trong ô, SHARE xuyên ô, bầu
   cử, SUMMON, CONFIRM/REJECT. Chia sẻ *ai thấy gì*. → **chiều A**.
2. **Mặt phẳng payload** *(chưa có, D2/D11)* — nút tiếp sức **chunk dữ liệu** cho
   nút khác. Chia sẻ *chính dữ liệu*. → **chiều B**.

Hai mặt phẳng **độc lập**: một nhánh có thể có B mà không có A.

## 6. Nhiệm vụ — MỘT kết cục

$$T=\min\{t:\ \text{BS nhận báo cáo mang toạ độ ĐÃ XÁC NHẬN}\}$$

| | |
|---|---|
| **thành công** | $T<T_{\max}$ **và** toạ độ ứng với nạn nhân thật |
| **thất bại loại 1** | không có báo cáo trước $T_{\max}$ → **kiểm duyệt phải** |
| **thất bại loại 2** | có báo cáo nhưng **sai người** → **thất bại thật**, tệ hơn loại 1 |
| **thời gian nhiệm vụ** | tại $T$ — **UAV đầu tiên** về báo cáo (`timeToFirstReport_s`, D4) |
| **chi phí** | năng lượng + gói tin của **toàn đội tới khi hạ cánh**, không dừng ở $T$ (D5) |

Thời gian và năng lượng là **chỉ số**, không phải ràng buộc cứng (D6).

## 7. Ma trận nhánh — 3×3 + 1

**Chiều A — vòng phản hồi**

| mức | cơ chế | `--scheme` |
|---|---|---|
| A0 | phủ mù, không phản hồi | `nocoop` |
| A1 | phản hồi, **không** hợp tác (ECHO một hop) | `closed-loop` |
| A2 | phản hồi, **có** hợp tác (cây ô + SHARE + bầu cử) | `proposed` |

**Chiều B — mặt phẳng payload** *(cờ mới `--relay`)*

| mức | cơ chế |
|---|---|
| B0 | không tiếp sức |
| B1 | tiếp sức **trong ô** |
| B2 | tiếp sức **trong + ngoài ô** |

→ **9 nhánh** + `tsp-mc` (baseline tài liệu Zeng'18, **không** được cấp relay) =
**10 nhánh**. `pure-uav` **bỏ** (D10).

**Dự đoán đăng ký trước:** hiệu ứng là **tương tác**, không cộng —
`A0B1 ≈ A0B0` về chi phí, chỉ `A2B1` mới rẻ, vì tiếp sức chỉ tiết kiệm airtime
**nếu UAV biết dừng sớm**, mà biết dừng cần chiều A.

## 8. Điểm vận hành

| tham số | giá trị | nguồn |
|---|---|---|
| đội bay | **4 UAV** (2 FAST + 2 DATA) | D13 |
| nhập nhằng | **M = 0** | D14 |
| ô lục giác | bán kính 80 m | `kHexCellRadiusM` |
| tầm G2G | **37.2 m cứng**, 26.3 m để còn 8 lân cận | link budget |
| dwell giao hàng | 20 s | `kMinDeliverDwellS` |
| $T_{\max}$ | **[MỞ]** — chưa có cơ sở; pin KHÔNG phải ràng buộc (19–56 Wh dùng / ~300 Wh có) | D15 |

**Trục quy mô — tách làm HAI, không gộp** (§3.16, phương án (b)):

| trục | cách quét | đổi cái gì | giữ nguyên cái gì |
|---|---|---|---|
| **diện tích** | `gridSize` ∈ {20, 24, 40} @ spacing 20 m | diện tích + số nút | mật độ, bậc liên thông |
| **mật độ** | `gridSpacing` ∈ {20, 25, 30, 35} @ `gridSize`=20 | mật độ, bậc liên thông (8→4), số nút/ô | số nút |

Không được quét spacing rồi gọi kết quả là "hiệu ứng của diện tích" — spacing đổi
**bốn thứ cùng lúc**.

### 8.1 Tiêu chí chọn điểm vận hành chính — quan trọng nhất, và nó MỚI

Với D1 (tuần tra rải full data) + D11 (tiếp sức), **mọi lược đồ đều thành công
nếu chờ đủ lâu** — kể cả phủ mù. Nên điểm vận hành phải thoả:

> **Thời gian để tấm phủ mù tự hoàn thành công việc phải LỚN hơn hẳn thời gian
> giao hàng có định hướng.**

Nếu không, mọi nhánh hoà nhau và campaign vô nghĩa. Đây là dạng chặt hơn của lo
lắng "20×20 phủ quá nhanh / 40×40 phủ quá chậm": vùng có ý nghĩa nằm ở giữa, và
**`gridSpacing` là núm chỉnh chính xác vào đó mà không phải trả thêm chi phí máy**
(20×20 @ 35 m cho 0.44 km² ≈ 3/4 của 40×40 với **1/4 số nút**).

**Việc phải làm trước campaign:** đo thời gian phủ-mù-hoàn-thành ở vài điểm
(spacing 20/25/30/35) và chọn điểm chính từ đó. Đây là *hiệu chuẩn*, không phải
kết quả — chạy ở $N$ nhỏ được, và **phải ghi rõ là đã dùng số liệu để chọn điểm
vận hành**.

## 9. Thống kê

| việc | công cụ |
|---|---|
| mô tả một nhánh | **Kaplan–Meier** $\hat S(t)$ |
| so hai nhánh | **log-rank phân tầng theo hạt giống** |
| chênh lệch tại một $t$ khai báo | hiệu hai tỉ lệ, KTC bắt cặp |
| chi phí (năng lượng, gói) | Wilcoxon bắt cặp + Cliff δ (không bị kiểm duyệt) |

- **Mọi hạt giống vào mọi phân tích.** Run thất bại = quan sát bị kiểm duyệt tại
  $T_{\max}$, **không** bị loại (D19). Cấm so thời gian chỉ trên các hạt giống mà
  cả hai nhánh cùng thành công — đó là survivorship bias.
- **Năm so sánh chính** C1–C5, hiệu chỉnh **Holm** trong họ đó; mọi thứ khác gắn
  nhãn **thăm dò** (D20).

| # | so sánh | trả lời |
|---|---|---|
| C1 | hiệu ứng chính của A (gộp B) | phản hồi mua được gì |
| C2 | hiệu ứng chính của B (gộp A) | tiếp sức mua được gì |
| C3 | tương tác A×B | "hợp tác là thứ cho phép dừng sớm"? |
| C4 | A2B1 vs `tsp-mc` | so với tài liệu |
| C5 | B1 vs B2 | overhead xuyên ô có đáng |

- **N = 120** phát hiện được hiệu ứng ≥ ~15 pp. Muốn nói 5–10 pp cần N ≈ 200–800.
  **[MỞ]** N=120 hay 200.
- **Pre-registration** (D21): ghi chỉ số chính, C1–C5, N, chân trời, điểm vận hành
  và quy tắc quyết định vào repo **trước khi có dữ liệu**.

## 10. Còn MỞ — không được tự quyết

| # | câu hỏi | chặn cái gì |
|---|---|---|
| O1 | $T_{\max}$ lấy từ đâu (phải từ tài liệu SAR, không từ số liệu của ta) | tỉ lệ thất bại, bảng tóm tắt |
| O2 | N = 120 hay 200 | ngân sách máy |
| O3 | Quy tắc tiếp sức payload: bitmap "tôi có gì" + gửi chunk còn thiếu, hay phát lại tốc độ thấp trong ô | D11, phần lớn nhất |
| O4 | Tỉ lệ chu kỳ cue:full khi DATA tuần tra | D1 |
| O5 | Điểm vận hành chính cụ thể (sau khi hiệu chuẩn §8.1) | toàn bộ campaign |
| O6 | Tạp chí (12–14 tr.) hay hội nghị (6–8 tr.) | bố cục, số hình |
| O7 | Có làm pre-registration không | D21 |
| O8 | "Đúng chỗ" có cần bán kính tuyệt đối (≤ 50 m) ngoài "gần nạn nhân hơn mọi vật gây nhầm" | định nghĩa thành công |

## 11. Thứ tự cài đặt — và cổng kiểm chứng cho từng bước

Nguyên tắc bất di bất dịch: **campaign chạy một mạch trên MỘT binary.** Cài xong
toàn bộ mới chạy; không vừa chạy vừa sửa. `binary=<mtime>,<size>` phải đồng nhất
trên mọi run của một campaign.

| giai đoạn | việc | cổng kiểm chứng |
|---|---|---|
| **G0** | Gắn thẻ commit hiện tại làm mốc "trước" | `git tag` + ghi binary id |
| **G1a** | D4: cột `timeToFirstReport_s` (giữ nguyên cột cũ) | cột mới ≤ cột cũ trên mọi run |
| **G1b** | D10: bỏ `pure-uav` | build sạch, không còn nhánh trong tool |
| **G1c** | D3: nhiễu phụ thuộc tín hiệu + **bảng hiệu chuẩn** | ở $\sigma$ đã hiệu chuẩn: xác suất một nút **không có tín hiệu** vượt `kAlertThreshold` phải ≈ 0 (mô hình cũ: 6.7 %), và xác suất nút nạn nhân báo động phải **khớp** mô hình cũ |
| **G1d** | D8: CONFIRM 5 B → 10 B (`evQ8` + vị trí); fix = vị trí nút xác nhận mạnh nhất | `Send()` không FAIL; sai số fix giảm hoặc bằng |
| **G1e** | D9: UAV dừng giao hàng khi nghe CONFIRM đủ mạnh | airtime giao hàng giảm; `fixOnVictim` **không** giảm |
| **G2** | D1: tuần tra rải full data, cue ưu tiên cao hơn | **đo gói tin** — nếu tăng > 5× thì dừng lại xem xét lại (§4) |
| **G3a** | D11-B1: tiếp sức **trong ô** (quy tắc từ O3) | số nút hoàn tất tăng với cùng số lượt bay |
| **G3b** | D11-B2: thêm xuyên ô | so B1: thời gian giảm? overhead? |
| **G4** | D12/D18/D19: đơn vị vận hành, KM + log-rank, giữ mọi hạt giống | chạy lại được phân tích cũ, số khớp |
| **G5** | D21: viết pre-registration, **commit trước khi có dữ liệu** | commit hash có trước run đầu tiên |
| **G6** | Hiệu chuẩn §8.1 → chốt điểm vận hành + $T_{\max}$ | ghi vào pre-registration |
| **G7** | Chạy campaign | `assert_one_build` + `assert_one_clutter` xanh |

**Để sau, không nằm trong campaign này:** D7 (FAST hỗ trợ rải dữ liệu sau khi
quét xong), D17 (nhiều mục tiêu thật + nhiều mục tiêu giả).

## 12. Quy tắc phương pháp (từ `STATUS.md` §5, giữ nguyên hiệu lực)

1. **N ≥ 120.** Số đo ở N=20 là **vô hiệu** — đã bỏ sót một chế độ lỗi 3.3 % và
   báo thiếu một sai số 42 %.
2. **Không bao giờ tin một hạt giống.** Đã có **ba lần** một hạt giống nói ngược
   với tập đủ.
3. **Không build lại giữa campaign.** Guard `binary=` tồn tại vì lỗi này đã xảy ra.
4. **Assert trên mọi lần sửa bằng script.**
5. **Không điều kiện hoá trên kết cục.**

## 13. Cái bài báo ĐƯỢC và KHÔNG ĐƯỢC tuyên bố

**Không được:** *"hợp tác ở biên làm SAR nhanh hơn và rẻ hơn"*. `closed-loop`
(A1B0) **thắng** `proposed` (A2B0) về thời gian, năng lượng và gói tin (0/120 về
gói tin) trong bản đo hiện có.

**Được, tách làm hai đóng góp khác nhau:**

| | mua được | trả bằng |
|---|---|---|
| **đóng vòng** (A) | phần lớn lợi thế chi phí so với phủ mù | gần như không |
| **hợp tác biên** (B) | đuôi sai số vị trí (−29 % p90); *dự đoán, chưa đo:* thời gian dưới nhiễu | +12 % năng lượng, +115 % gói tin |

Đóng góp B **chưa từng được đo trong điều kiện nó có lý do tồn tại** — mọi số hiện
có đo ở $M=0$, $\sigma=0$, tức đúng chế độ mà hợp tác không có việc gì để làm. Đó
là lý do tồn tại của ma trận 3×3.
