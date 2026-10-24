# 2026-10-24 · Bán kính phát hiệu quả của UAV theo môi trường (CLAUDE.md §8 mục 158)

**Mục đích:** xem kịch bản nào khiến UAV chỉ phát hiệu quả trong bán kính khoảng 100–200 m, và hệ quả với file mã hoá fountain.

**Mã:** `uav-l2/tools/a2g_radius.py`, tính giải tích, không chạy ns-3.
- UAV bay ở độ cao 100 m. Gói 127 B qua được khi công suất sau fading ≥ −101 dBm (điểm PER 50 % đo trên PHY ns-3).
- Các môi trường so sánh:
  - kênh đang dùng (`coop-a2g.h`): không gian tự do tới 100 m, sau đó số mũ 3; Rician K = 2; UAV phát +10 dBm;
  - kênh đang dùng cộng thêm suy hao xuyên tường 15 hoặc 20 dB;
  - radio cỡ CC2420: phát 0 dBm, độ nhạy −95 dBm;
  - mô hình Al-Hourani et al. 2014 (IEEE WCL 3(6)) cho đô thị, đô thị dày và cao tầng.
- Mô hình Al-Hourani:
  - Xác suất LoS theo góc ngẩng: 1 / (1 + a·exp(−b(θ − a))).
  - Suy hao không gian tự do cộng thêm η_LoS (fading Rician K = 2) hoặc η_NLoS (Rayleigh).
  - Lấy trung bình theo hai trạng thái LoS/NLoS.
- "Gói nghe được" là số gói một node ở độ lệch ngang x nhận được trong một lượt bay thẳng dài, một gói mỗi 0,5 m.
- "File fountain tối đa" = số gói nghe được / 1,05.

**Lệnh:** `radius.md`.

**Kết quả** (R50, R10: khoảng cách ngang tại đó xác suất qua gói còn 50 %, 10 %):

| môi trường | R50 (m) | R10 (m) | gói nghe được (lệch 0 / 200 m) | file fountain tối đa một node tự giải (kB) |
|---|---|---|---|---|
| kênh đang dùng | 1015 | 1355 | 3988 / 3896 | 376 |
| + 15 dB xuyên tường | 310 | 420 | 1194 / 852 | 113 |
| + 20 dB xuyên tường | 195 | 275 | 750 / 258 | 71 |
| CC2420 (0 dBm, −95 dBm) | 280 | 385 | 1094 / 720 | 103 |
| đô thị (Al-Hourani) | 350 | 675 | 1809 / 1502 | 171 |
| đô thị, UAV 0 dBm | 225 | 510 | 1150 / 712 | 108 |
| đô thị dày | 235 | 470 | 1296 / 885 | 122 |
| đô thị dày, UAV 0 dBm | 145 | 360 | 789 / 355 | 74 |
| cao tầng | 45 | 120 | 281 / 81 | 26 |

**Dang dở:**
- Chưa chọn kịch bản nào làm kênh chính hoặc để quét độ nhạy.
- Nếu đưa vào ns-3, trạng thái LoS phải nhất quán theo không gian cho mỗi node: thay đổi theo góc ngẩng dọc lượt bay, không bốc độc lập cho từng gói.
