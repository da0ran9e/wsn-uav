# Chuỗi gói liên tục dài nhất từ UAV bay ngang — nhánh đô thị

> ⚠️ **NHÁNH ĐÔ THỊ.** Mọi con số trong tài liệu này là của kênh không–đất **đô thị**.
> **Không** được đem sang kịch bản rừng — kịch bản đó có kênh riêng
> (`ForestA2gLossModel`) và tham số riêng (`sar-params.h`).

## 1. Câu hỏi

Mỗi node có thể nhận được **chuỗi gói liên tục** dài bao nhiêu trước khi mất một
gói? File không khôi phục được gói lỗi, nên chỉ chuỗi **liền mạch** mới có giá trị.

## 2. Kịch bản (đã chốt)

| | |
|---|---|
| Node | 7 node thẳng hàng, cách 300 m (lệch 900/600/300/0 m) |
| UAV | cao 100 m, 50 m/s, bay **vuông góc** qua đúng node 4, từ −2000 m tới +2000 m |
| Phát | PSDU 127 B (khung 133 B, **4.256 ms**), mỗi **10 ms**, đánh số → **8001 gói/lượt** |
| Công suất | TX **+10 dBm**, độ nhạy **−100 dBm**, ăng-ten **đẳng hướng** |
| Suy hao | tự do tới 100 m (**−80.05 dB**), sau đó `(d/100)^−α`, **α = 3.0** (quét 2.6, 3.35) |
| Fading | **Rician K = 2**, bốc lại **mỗi gói** |
| Che khuất | tắt |
| MAC | **bỏ qua** — bơm thẳng `LrWpanPhy::PdDataRequest`, không CSMA/ACK/beacon |
| Lặp | **200 lượt** mỗi cấu hình |

Hai đoạn suy hao chính là `ThreeLogDistancePropagationLossModel` của ns-3
(d₀ = 1 m, n₀ = 2, d₁ = 100 m, n₁ = α) — không cần lớp mới.

## 3. Kết quả — α = 3.0

| Node | Lệch | Cự ly gần nhất | Gói thu được | **Chuỗi dài nhất** | p10 – p90 |
|---|---|---|---|---|---|
| 4 | 0 m | 100 m | 4002 | **850 ± 226** | 554 – 1154 |
| 3, 5 | 300 m | 316 m | 3789 | **245 ± 85** | 155 – 355 |
| 2, 6 | 600 m | 608 m | 3077 | **50 ± 11** | 37 – 66 |
| 1, 7 | 900 m | 906 m | 1828 | **14 ± 2** | 11 – 17 |

Một gói = 10 ms = 0.5 m đường bay. Node 4 nhận liền ~850 gói ≈ **8.5 s**,
≈ **105 KB** tải 127 B/gói.

**Độ nhạy theo α** (chuỗi dài nhất, trung bình):

| α | node 4 | node 3,5 | node 2,6 | node 1,7 |
|---|---|---|---|---|
| 2.6 | 931 | 346 | 104 | 40 |
| **3.0** | **850** | **245** | **50** | **14** |
| 3.35 | 788 | 174 | 25 | 5 |

Node giữa gần như không nhạy α (−15 % từ 2.6 → 3.35); node xa nhất nhạy **8×**.

## 4. Ba điều phát hiện khi cài

### 4.1 Nakagami m = 1.8 **không** tương đương Rician K = 2 cho chỉ số này

Đặc tả đề xuất Nakagami `m = (K+1)²/(2K+1) = 1.8` vì ns-3 không có Rician. Phép
khớp đó khớp **trung bình và phương sai** công suất, nhưng **không** khớp đuôi fade
sâu. Đo trực tiếp trên 11.2 triệu lần bốc trong ns-3:

| | P(< −10 dB) | P(< −20 dB) | P(< −30 dB) |
|---|---|---|---|
| Rician K = 2 | 4.6e-2 | 4.1e-3 | 4.1e-4 |
| Nakagami m = 1.8 | 2.4e-2 | 4.3e-4 | 8.1e-6 |

Ở −30 dB Rician fade **~50×** nhiều hơn. **Tổng số gói** do vùng rìa quyết định nên
gần như không đổi; **chuỗi dài nhất** do fade sâu hiếm quyết định nên lệch mạnh:

| | node 4 | node 3,5 | node 2,6 | node 1,7 |
|---|---|---|---|---|
| Nakagami ÷ Rician | **1.66×** | **2.40×** | 1.33× | 1.02× |

→ Đã viết lớp `RicianFadingLossModel` (bốc lại mỗi gói, mỗi máy thu) và dùng nó làm
chính. Nakagami vẫn chạy được bằng `--fading=nakagami` để đối chiếu.

### 4.2 "Độ nhạy −100 dBm" trong ns-3 **không** phải ngưỡng cứng

`SetRxSensitivity(S)` của ns-3.46 chỉ đặt hệ số tạp âm `F = S − (−106.58) = 6.58 dB`
và định nghĩa S là điểm **PER 1 % cho PSDU 20 B**. Thu hay không là đường BER theo
SINR. Đo bằng `--mode=calib` cho khung 127 B, không fading:

| | |
|---|---|
| PER ≤ 99 % từ | −102.25 dBm |
| **PER 50 %** tại | **−101.0 dBm** |
| PER ≤ 1 % từ | −99.25 dBm |

Tức ns-3 **hào phóng hơn ngưỡng cứng ~1 dB**. Lưu ý: hệ số tạp âm suy ra là 6.58 dB,
không phải 5 dB như bảng tham số — trong ns-3 hai đại lượng này **không độc lập**;
tôi giữ độ nhạy −100 dBm (in đậm trong đặc tả) và để F tự suy ra.

### 4.3 Bảng giải tích của đặc tả được tái tạo — và chênh lệch được giải thích trọn

| α = 3.0, chuỗi dài nhất | node 4 | node 3,5 | node 2,6 | node 1,7 |
|---|---|---|---|---|
| bảng trong đặc tả | 823 | 208 | 40 | 11 |
| giải tích, ngưỡng cứng −100 dBm | 817 | 203 | 40 | 10 |
| giải tích, **đường PER đo từ ns-3** | 845 | 244 | 52 | 14 |
| **mô phỏng ns-3** | **850** | **245** | **50** | **14** |

- Hàng 1 ≈ hàng 2: bảng của đặc tả đúng là **ngưỡng cứng + Rician K = 2**.
- Hàng 3 ≈ hàng 4: thay ngưỡng cứng bằng đường PER của ns-3 thì giải tích **trùng**
  mô phỏng. **Toàn bộ** chênh lệch giữa đặc tả và ns-3 là ~1 dB của mục 4.2.
- Đồng thời đây là kiểm chứng rằng mô phỏng làm đúng điều ta nghĩ.

α = 3.35 cũng vậy: đặc tả 740/151/20/4 · ngưỡng cứng 749/143/20/4 · ns-3 788/174/25/5.

## 5. Hai điểm phải ghi khi trích

### 5.1 Gói dài hơn thời gian kết hợp — kết quả **lạc quan**

50 m/s ở 2.4 GHz → Doppler 400 Hz → thời gian kết hợp ≈ **1.06 ms**, gói chiếm
sóng **4.256 ms**. Kênh đổi **trong lòng gói**, còn ns-3 (và đặc tả) giữ một mức
fade cho cả gói. Ước lượng cận bằng cách chia mỗi gói thành **4 khối fade độc lập**:

| α = 3.0, chuỗi dài nhất | node 4 | node 3,5 | node 2,6 | node 1,7 |
|---|---|---|---|---|
| ns-3 (1 fade / gói) | 850 | 245 | 50 | 14 |
| 4 fade / gói (cận bi quan) | 548 | 106 | 19 | 5 |
| **hệ số lạc quan** | **1.6×** | **2.3×** | **2.6×** | **2.8×** |

Hệ số là **1.6–2.8×, không phải ×4**. Và 4 khối độc lập là **cận bi quan** — tương
quan giảm dần chứ không cắt phẳng ở 1.06 ms — nên giá trị thật nằm **giữa hai hàng**.

### 5.2 Đây là thí nghiệm đô thị

Chỉ dùng cho nhánh đô thị. Không đưa sang kịch bản rừng.

## 6. Kiểm chứng tự động

Mỗi lần chạy kiểm (CHECK, không phải `assert` — ns-3 build NDEBUG):

- TX đo **từ chính tín hiệu** (trace `TxSigParams`) = **+10.000 dBm**, mọi gói.
- Suy hao trace (`PathLoss`) khớp công thức hai đoạn **sai số 0 dB** khi tắt fading
  → ăng-ten đúng 0 dBi, cấu hình suy hao đúng.
- Fading thực áp có công suất trung bình 1.0001 và đuôi khớp tham chiếu (±5 % ở −10 dB).
- Đủ **8001/8001** gói rời ăng-ten mỗi lượt; không trùng, không số thứ tự lạ.

Đối chứng không fading (`x30.csv`): chuỗi vẫn bị bẻ nhẹ ở rìa cửa sổ — đó là vùng
chuyển tiếp ~3 dB của đường PER, không phải lỗi.

## 7. Chạy lại

```bash
B=/home/user/ns3-dev/build/src/uav-sar/examples/ns3.46-uav-sar-a2g-run-test-optimized
$B --mode=calib --out=calib.csv
$B --alpha=3.0  --fading=rician   --passes=200 --out=r30.csv
$B --alpha=2.6  --fading=rician   --passes=200 --out=r26.csv
$B --alpha=3.35 --fading=rician   --passes=200 --out=r335.csv
$B --alpha=3.0  --fading=nakagami --passes=200 --out=n30.csv
python3 tools/a2g_run_report.py <thư mục csv> a2g-run.png
```

Mỗi cấu hình 200 lượt chạy ~30 s. Dữ liệu và hình: `docs/visualize/result/a2g-run/`,
`docs/visualize/result/a2g-run.png`.
