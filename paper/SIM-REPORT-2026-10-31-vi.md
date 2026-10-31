# Báo cáo giả lập 30–31/10/2026: vận chuyển mặt đất trên pass CHORD cố định và sai số quỹ đạo

Tài liệu này gom toàn bộ dữ kiện của hai thí nghiệm bổ sung cho Section VI. Các thí nghiệm này trả lời nhận xét của
reviewer (CLAUDE.md §8 mục 221–241). Log, mã và số thô nằm trong `logs/2026-10-30_1545-deluge-r100/` và
`logs/2026-10-31_0000-wind/`.

**Thuật ngữ trong bài và trong mã:**

| Trong bài | Trong mã / log |
|---|---|
| SPINE | Axe (cell nằm dưới đường bay; `AXE` trong `plan<k>.txt`) |
| Bank | Bank |
| Ring | Circle |
| đoạn SPINE của một cell | Seg(a) |

Mọi câu viết cho bài phải dùng SPINE, không dùng "Axe".

---

## 1. Thiết lập chung

- **Bản đồ:** k8-s1 (8 cụm, 45 critical cell), kênh **r100** (L_obs 25,74 dB, bán kính nhận hiệu quả R50 ≈ 99 m).
- **Tour đội 1:** CHORD của chiến dịch 4. Pass được giữ cố định cho mọi phương án mặt đất (biến kiểm soát).
- **Mô phỏng:** ns-3.46, lr-wpan đầy đủ MAC (CSMA/CA, ACK, phát lại), lưới kênh PECEE 7 màu, gateway kênh riêng.
- **Seed ns-3 (network realisation):** R = 1…5. Seed đổi fading của pass, shadowing và fading G2G, và các bốc ngẫu
  nhiên của MAC. Pass và kênh là chung cho mọi phương án trong cùng seed, nên mọi so sánh đều ghép cặp.
- **Binary:** `river-bin10` (hash 94820fddaca15499), tức CAMP-BIN5 của chiến dịch 4 cộng các bộ đếm trạng thái PHY
  và các tuỳ chọn mới. Kiểm chứng: với cùng seed, River cho kết quả trùng tới từng hop với chiến dịch 4 (cụm 6, 7,
  8 của seed 1), và T\* seed 1 = 891,9 s (chiến dịch 4: 892 s).
- **T\* (thời điểm hoàn thành nhiệm vụ):** mỗi seed có 100 Layer-1 draw ghép cặp (kho ảnh của camera, nhiễu so
  khớp, pha LoRa). ns-3 chạy **một lần** cho mỗi seed; 100 draw chỉ lấy mẫu lại Layer 1 trên cùng kết quả ns-3.
- **Thời điểm "sẵn sàng" (ground ready):** tính **từ lúc UAV rời cụm** (kết thúc pass), không phải từ lúc cất
  cánh. Mỗi (seed, cụm) lấy thời điểm critical cell cuối cùng của cụm đủ dữ liệu; chưa xong trong 900 s thì tính 900 s.

### 1.1 Cách đọc khoảng tin cậy (quan trọng khi viết bài)

Có **ba loại độ trải** khác nhau. Bài phải ghi rõ đang dùng loại nào:

| Loại | Tính trên | Dùng cho |
|---|---|---|
| **CI theo seed** | n = 5 (hoặc 3) giá trị trung bình mỗi seed, phân phối t | **Số chính trong bài**, cùng chuẩn với phần còn lại của Section VI |
| CI theo (seed, cụm) | n = 40 cặp (5 seed × 8 cụm) | độ trải giữa các cụm; chỉ dùng cho các chỉ số cấp cụm |
| CI theo draw | n = 100 Layer-1 draw **của một network realisation** | **không** phải độ bất định theo seed; chỉ phản ánh độ trải của Layer 1 |

**Trả lời câu hỏi 1:** con số "± 17,8 s" trong báo cáo trước là **CI 95 % theo 100 Layer-1 draw của một network
realisation (seed 1)**: 1,96 × sd(Δ) / √100, với sd(Δ) = 90,6 s. Đây không phải CI theo seed. Kết quả 28/46/26
(tệ hơn / bằng / tốt hơn) cũng đếm trên 100 draw đó. Mục 3 dưới đây thay nó bằng CI theo seed.

---

## 2. Thí nghiệm A: vận chuyển mặt đất trên pass CHORD cố định (River so với Deluge)

### 2.1 Các phương án

- **River:** kế hoạch SPINE → Bank → Ring do BS lập trước (`--prep=full`), kèm hai cơ chế sửa lỗi (`--repair=20`):
  - cell SPINE bù các gói của đoạn SPINE của mình từ cell kề;
  - critical cell đứng yên 20 s thì hỏi lại.
- **Deluge (cell River):** advertise–request theo Trickle trên đúng các cell mà kế hoạch River dùng.
- **Deluge (cell trên đường):** Trickle chỉ trên các cell SPINE, critical cell và các cell nằm trên đường SPINE →
  critical cell. Đây là phạm vi reviewer đề nghị.
- **Tham số Trickle (RFC 6206):** Imin 1 s, Imax 64 s, k = 1.
- **Page:** 64 gói, ngắt thêm tại ranh giới mỗi ảnh và tại ranh giới đoạn SPINE.
  - Cell SPINE bù đoạn của mình như River, để mọi page đều đủ trọn ở ít nhất một cell.
  - Không có hai điều này, Deluge kẹt ở 3/8 cụm, vì luật quảng bá của Deluge đòi page phải đủ trọn.
- **Mô hình nghe:** mọi radio **luôn bật** khi rảnh (`SetRxOnWhenIdle`). **Không có low-power listening.**
- **Năng lượng radio:** E = V·(I_tx·T_tx + I_rx·T_rx + I_rx·T_listen + I_off·T_off), thời gian lấy từ trace trạng
  thái PHY. Dòng điện theo datasheet: CC2420 (RX 18,8 mA, TX 17,4 mA, idle 426 µA, 3 V) và EFR32MG21 ở +10 dBm.
  Có hai chế độ:
  - *luôn nghe:* như mô phỏng;
  - *ngủ theo lịch:* chỉ cho River. Node ngủ sau lần phát cuối của nó. Deluge không ngủ được vì phải nghe quảng bá.
- **Tính chặt của chế độ ngủ:** River không dùng gói nghe ké. Mọi gói nó nhận là unicast có địa chỉ theo đường cell
  do BS lập. Chế độ "ngủ sau lần phát cuối" là một cận *ex-post*:
  - lạc quan: bỏ qua những lần phải thức dậy cho yêu cầu hỏi lại;
  - bi quan: giữ radio bật giữa các lượt của lịch.
- **Kéo trực tiếp:** đã được chạy (seed 1–2, và một bản thô ở seed 1) nhưng **không đưa vào bảng**, theo quyết định
  của tác giả. Số thô nằm trong `results/R1`, `results/R2` (tag `d2`, `dR`).

### 2.2 Kết quả (5 seed; CI 95 % theo seed, phân phối t với n = 5)

| | River | Deluge (cell River) | Deluge (cell trên đường) |
|---|---|---|---|
| Critical cell xong | 45/45 ở mọi seed | 45/45 | 45/45 |
| Cell cuối sẵn sàng (s, từ lúc rời cụm) | **117 ± 8** | 156 ± 3 (×1,34; 1,22–1,44) | 149 ± 3 (×1,28; 1,18–1,37) |
| Frame phát mỗi cụm (nghìn) | **958 ± 20** | 2 344 ± 11 (×2,45; 2,40–2,49) | 1 786 ± 11 (×1,87; 1,82–1,90) |
| Năng lượng radio CC2420, ngủ theo lịch (J/cụm) | **1 693 ± 59** | 14 940 ± 290 (×8,8; 8,6–9,4) | 11 000 ± 210 (×6,5; 6,2–6,9) |
| Năng lượng radio CC2420, luôn nghe (J/cụm) | 11 060 ± 690 | 14 940 ± 290 (×1,35) | 11 000 ± 210 (×1,00) |
| Node nóng nhất, CC2420, ngủ theo lịch (J) | **19,0 ± 1,6** | 28,7 ± 1,5 (×1,51) | 27,0 ± 1,1 (×1,42) |
| T\* nhiệm vụ (s) | **863 ± 88** | 906 ± 86 | 899 ± 83 |
| ΔT\* so với River, ghép cặp theo seed | — | **+43 ± 15 s** (River tốt hơn ở 5/5 seed) | **+36 ± 12 s** (5/5 seed) |

Trong ngoặc là tỉ số so với River, cùng khoảng min–max theo seed. ΔT\* theo từng seed:

| Seed | Deluge (cell River) | Deluge (cell trên đường) |
|---|---|---|
| 1 | +37 s | +34 s |
| 2 | +31 s | +27 s |
| 3 | +44 s | +31 s |
| 4 | +39 s | +33 s |
| 5 | +63 s | +53 s |

### 2.3 Câu gợi ý cho bài

> "On the same CHORD passes (8 clusters, 45 critical cells, r100, 5 paired network realisations), River readies the
> last critical cell of a cluster 32–39 s earlier than Deluge and lowers T\* by 36–43 s (±12–15 s, 95 % CI over
> seeds; River faster in 5/5 seeds). It sends 1.9–2.5× fewer frames and, because its nodes can sleep on the
> pre-computed schedule while Deluge must keep listening for advertisements, needs 6.5–8.8× less radio energy; its
> hottest node uses ~30 % less. Trickle: I_min = 1 s, I_max = 64 s, k = 1, 64-packet pages aligned to image and
> SPINE-segment boundaries."

Lưu ý khi viết:

- Lợi thế năng lượng của River phụ thuộc chế độ ngủ theo lịch. Nếu cả hai phương án luôn nghe, River ngang Deluge
  (cell trên đường) và chỉ hơn Deluge (cell River) 1,35 lần. Bài cần nói rõ giả định này.
- Số 4,7× frame trong bản thảo cũ (16 bản đồ open) **không** áp dụng cho r100. Dùng 1,9–2,5×.

---

## 3. Thí nghiệm B: sai số quỹ đạo (gió)

### 3.1 Thiết kế

- BS lập kế hoạch River (SPINE, đoạn SPINE, Bank, Ring) trên **đường bay dự kiến**. Pass ns-3 bay một **đường bị
  lệch**. Trên mặt đất, River chạy với kế hoạch không còn khớp.
- **Mô hình lệch** (`uav-l2/tools/wind_path.py`):
  - lệch ngang và lệch dọc là nhiễu trắng làm mượt bằng nhân Gauss 10 s;
  - độ lệch chuẩn dừng: σ (ngang) và σ/2 (dọc);
  - cột thời gian giữ nguyên, nên gói s vẫn phát tại s × 10 ms và chỉ số gói khớp với kế hoạch. Chỉ vị trí phát thay đổi.
- Pass được build lại với tuỳ chọn `--offPlan` để bỏ kiểm tra "đường bay qua CH". Trên đường dự kiến, bitmap trùng
  hệt bản cũ (đã kiểm).
- Chạy ba seed (1–3) cho σ = 50 m và σ = 100 m; σ = 200 m chỉ chạy seed 1. So với River không gió cùng seed.

### 3.2 Độ lệch thực tế (trả lời câu hỏi 2)

σ là **tham số của quá trình ngẫu nhiên**, không phải độ lệch của từng lượt bay. Mỗi pass chỉ dài khoảng 50–56 s,
tức chỉ vài lần thời gian tương quan, nên độ lệch thực tế của từng pass dao động quanh σ:

| σ danh nghĩa | Độ lệch chuẩn ngang thực tế mỗi pass (24 pass) | Trung bình | Lệch ngang cực đại mỗi pass |
|---|---|---|---|
| 50 m | 9–80 m | 29 m | 31–173 m |
| 100 m | 18–160 m | 58 m | 62–346 m |
| 200 m (1 seed) | 67–206 m | 137 m | 223–692 m |

Trong bài nên báo **độ lệch thực tế** (ví dụ "per-pass cross-track RMS 9–80 m, mean 29 m, peak ≤ 173 m"), kèm mô
hình sinh. Không chỉ ghi "50 m".

### 3.3 Tính bay được

| σ | Gia tốc pháp tuyến lớn nhất | Thời gian vượt 1 g (bank 45°) | Thời gian bay trong cụm so với kế hoạch |
|---|---|---|---|
| 50 m | ≤ 2,8 m/s² (≤ 0,29 g; seed 1–3) | 0 % | 0,96–1,03 (seed 1) |
| 100 m | ≤ 5,7 m/s² (≤ 0,58 g; seed 1–3) | 0 % | 0,84–1,02 (seed 1) |
| 200 m | 7,6–10,0 m/s² (seed 1) | 0,5 % ở 1 cụm | 0,77–1,02 (seed 1) |

- Gia tốc dưới 1 g nghĩa là bán kính quay ≥ v²/9,81 m, tức ≥ 63,7 m ở 25 m/s và ≥ 255 m ở 50 m/s.
- σ = 50 m và σ = 100 m bay được.
- σ = 200 m ở sát giới hạn: vượt 1 g ngắn hạn, và thời gian trong cụm giảm tới 23 %. Chỉ dùng làm chỉ dấu.

### 3.4 Kết quả

| σ danh nghĩa | Seed | Critical cell xong | Cell cuối sẵn sàng (s) | T\* không gió → có gió (s) | ΔT\* ghép cặp |
|---|---|---|---|---|---|
| 50 m | 1 | 45/45 | 115 (không gió 126) | 892 → 897 | +5,2 s |
| 50 m | 2 | 45/45 | 113 (112) | 849 → 845 | −4,1 s |
| 50 m | 3 | 45/45 | 115 (115) | 972 → 972 | +0,2 s |
| **50 m, 3 seed** | | **135/135** | 114 (118) | 904 → 905 | **+0,5 ± 11,5 s (CI theo seed, t, n = 3)** |
| 100 m | 1 | 33/45 | 305 (126) | 892 → 1 218 | +326 s |
| 100 m | 2 | 40/45 | 214 (112) | 849 → 955 | +106 s |
| 100 m | 3 | 33/45 | 313 (115) | 972 → 1 423 | +452 s |
| **100 m, 3 seed** | | **106/135** | 277 (118) | 904 → 1 198 | **+294 s (+33 %); CI theo seed ± 435 s (n = 3, rộng)** |
| 200 m | 1 | 3/45 | 900 (giới hạn) | 892 → 3 576 | +2 684 s |

Ghi chú thống kê:

- CI theo draw của từng seed (chỉ để tham khảo, không đưa vào bài như CI chính):
  - σ = 50 m: ± 17,8 / ± 8,9 / ± 6,7 s;
  - σ = 100 m: ± 134 / ± 77 / ± 167 s.
- Ở σ = 100 m, CI theo seed rất rộng (± 435 s) vì chỉ có 3 seed và độ suy giảm khác nhau nhiều giữa các seed.
  Kết luận về chiều thì vững: cả 3 seed đều suy giảm (+106 đến +452 s) và đều có critical cell không xong.
- Lượng dữ liệu cụm nhận từ UAV gần như không đổi: tổng D ở seed 1 là 32 891 gói khi không gió và 32 763 gói ở
  σ = 100 m (−0,4 %). Suy giảm đến từ **kế hoạch**, không phải từ việc mất dữ liệu.

### 3.5 Cơ chế

- BS giao đoạn SPINE cho từng cell SPINE theo vị trí phát dự kiến. Khi đường bay lệch khoảng một bán kính nhận trở
  lên (R50 ≈ 99 m ở r100), gói của một đoạn SPINE rơi vào những cell không phải cell SPINE đó, cũng không kề nó.
- Cơ chế bù đoạn SPINE chỉ hỏi cell kề, nên không tìm được các gói này. Chuỗi SPINE → Bank → Ring của một số critical
  cell vì thế đứng yên tới hết giới hạn 900 s.
- Ở σ = 50 m (lệch thực tế trung bình 29 m), gói vẫn rơi vào cell SPINE dự kiến hoặc cell kề, nên River không bị
  ảnh hưởng.

### 3.6 Câu gợi ý cho bài

> "We fly each pass along a path displaced from the plan by a smoothed random disturbance (cross-track RMS per pass
> 9–80 m, mean 29 m, peak ≤ 173 m; normal acceleration ≤ 0.29 g, so every path is flyable) while River keeps the
> plan computed on the nominal path. River is unaffected: all 135 critical cells of 3 paired network realisations
> are ready, and T\* changes by +0.5 ± 11.5 s (95 % CI over seeds). Doubling the disturbance (per-pass RMS 18–160 m,
> mean 58 m, about half to one effective reception radius at r100; still flyable, ≤ 0.58 g) breaks the pre-computed SPINE-segment assignment:
> 106/135 critical cells become ready within 900 s and T\* grows by 33 % (+106 to +452 s per realisation), although the
> cluster still hears 99.6 % of the data. Re-planning on the flown track, or widening the SPINE-segment repair beyond
> adjacent cells, is left to future work."

---

## 4. Giới hạn và việc còn mở

- Chỉ một bản đồ (k8-s1) và một kênh (r100), là kịch bản khắt khe nhất về bán kính nhận. Kênh rộng hơn nên chịu
  được độ lệch lớn hơn (chưa đo).
- Deluge **không mô hình low-power listening**. Nếu Deluge dùng LPL (kiểu BoX-MAC), chênh lệch năng lượng sẽ nhỏ đi,
  đổi lại trễ mỗi hop tăng.
- Chế độ "ngủ theo lịch" của River là cận ex-post (mục 2.1).
- Gió: chưa chạy Deluge ở σ = 100 m. Đây là phương án không dùng kế hoạch, và có thể vượt River khi kế hoạch gãy.
  Chạy thử khoảng 1 giờ cho 3 seed.
- Hệ số c1, c2 của mô hình năng lượng UAV (Zeng–Zhang) chưa đối chiếu với bài gốc.

## 5. Nguồn số liệu

| Nội dung | Tệp |
|---|---|
| Bảng ground transport, 5 seed | `logs/2026-10-30_1545-deluge-r100/table.md`; seed 3–4: `table-s3-4.md` |
| Số thô theo cụm, theo node năng lượng, theo draw | `logs/2026-10-30_1545-deluge-r100/results/R{1..5}/` |
| Gió | `logs/2026-10-31_0000-wind/README.md`, `results/s{50,100,200}-R{1,2,3}/` (kèm `wind-paths.txt`: độ lệch thực tế từng pass) |
| Mô hình năng lượng | `uav-l2/tools/energy.py`, `uav-l2/docs/ENERGY-vi.md` |
