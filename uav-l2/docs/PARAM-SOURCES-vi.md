# Rà soát nguồn gốc tham số giả lập (CLAUDE.md §8 mục 102)

Nhãn:
- **[chuẩn]**: tiêu chuẩn hoặc quy định.
- **[công bố]**: bài báo hoặc datasheet.
- **[suy ra]**: tính từ các số có nguồn.
- **[thiết kế]**: lựa chọn của nghiên cứu, không cần nguồn nhưng phải nói rõ.
- **[giả định]**: số tạm, **cần nguồn hoặc cần nói rõ là giả định**.

Mã: `uav-coop/models/common/coop-params.h`, `uav-l2/tools/mission_*.py`, `l1_mission.py`.

## 1. Vô tuyến 802.15.4

| Tham số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| Tần số, tốc độ, PSDU | 2,4 GHz; 250 kbps; 127 B | [chuẩn] IEEE 802.15.4 O‑QPSK | |
| Thời gian chiếm sóng | 4,256 ms | [suy ra] | 133 B × 8 / 250 kbps |
| Tải hữu ích | 99 B | [suy ra] | 127 B trừ tiêu đề MAC, bảo mật, FCS |
| Chu kỳ gói 10 ms | 10 ms | **[giả định]** | Đặc tả mục 2 ghi là "khe mặc định 802.15.4", nhưng chuẩn không có khe 10 ms (aBaseSlotDuration = 60 symbol = 0,96 ms). Nên gọi là chu kỳ phát chọn ≥ 2,35 × thời gian chiếm sóng. |
| Công suất phát | +10 dBm | [chuẩn] | Dưới giới hạn 20 dBm EIRP của ETSI EN 300 328 |
| Độ nhạy | −100 dBm | [công bố] cần trích | Mức của chip đời mới (ví dụ TI CC2652R, datasheet); CC2420 chỉ −95 dBm. Cần ghi tên chip. |
| Unicast mỗi khung (đội 2) | 6,88 ms | [suy ra] | Khung + ACK + IFS theo chuẩn |

## 2. Kênh truyền

| Tham số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| A2G: tự do tới H rồi α = 3,0 (quét 2,6; 3,35) | | [công bố] | "Qiu 2017" theo đặc tả mục 2. **Cần trích đầy đủ và kiểm lại số** |
| A2G fading Rician K = 2, bốc lại mỗi gói | | **[giả định]** | Đặc tả mục 2 không có nguồn. Cần nguồn đo A2G 2,4 GHz độ cao thấp |
| **Baseline dùng Nakagami m = 1,8** (`mission_baselines.py`) | | **lệch** | A2G-RUN đã cho thấy Nakagami 1,8 ≠ Rician K = 2 (đuôi fade khác tới 50×). Lượt bay dùng Rician; tính toán baseline còn Nakagami. **Cần sửa cho thống nhất** |
| G2G: n = 3,5 từ 1 m; che khuất σ = 7,8 dB | | [công bố] | 3GPP TR 38.901, UMi NLoS (35,3 log d; σ 7,82) |
| G2G Rayleigh (mọi liên kết NLoS) | | [thiết kế] bi quan | Phù hợp NLoS của 3GPP |
| G2G thời gian kết hợp 100 ms | | **[giả định]** | Node đứng yên, cảnh vật di chuyển. Cần nguồn hoặc quét (đã thử 10 ms) |
| Che khuất độc lập giữa các cặp | | [giả định] | 3GPP có mô hình tương quan không gian; chưa dùng |

## 3. Kênh phản hồi LoRa

| Tham số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| Duty cycle 1 % | | [chuẩn] | ETSI EN 300 220, băng EU 868 MHz |
| Thời gian phát 0,4 s | | **[giả định]** | Phải tính bằng công thức Semtech theo SF, BW, kích thước gói. Khoảng 0,37 s ứng với khoảng 10 B ở SF10/125 kHz. **Cần chốt SF và kích thước báo cáo** |
| Khoảng giữa hai lần phát 40 s | | [suy ra] | 0,4 / 0,01 |
| Pha khe LoRa đều trên [0; 40) s | | [giả định] hợp lý | |

## 4. UAV và nhiệm vụ

| Tham số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| Đội 1: H = 100 m, 50 m/s | | [thiết kế] (mục 1) | Nên kèm một UAV cánh bằng thực tế làm tham chiếu |
| Bán kính rẽ 254,9 m | | [suy ra] | v² / (g tan φ) với φ = 45° [giả định] |
| Đội 2: 15 m/s | | [thiết kế] (mục 73) | |
| Đội 2 lơ lửng 30 s (`HOVER`) | | **[giả định]** | |
| Đội 2 ổn định 5 s (`SETTLE`) | | **[giả định]** | |
| Tệp xác minh 1 MiB (`BIG`) | | **[giả định]** (mục 73: tạm) | |
| Chuyển kết quả 0,1 s mỗi cell (`HOP`) | | **[giả định]** | Có thể suy từ 802.15.4: khoảng 2 khung mỗi cell, khoảng 15 ms; 0,1 s là thận trọng |
| BS cách miền 1 km | | [thiết kế] | |

## 5. Mạng và cơ chế (thiết kế, không cần nguồn ngoài)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Cell R | 100 m | mục 9, 11 |
| Mật độ node | 1 node / 35 × 35 m | mục 9 (20–50 m) |
| Cluster tối đa | 80 cell | |
| CH cách biên | ≥ 300 m | |
| Thuộc tính node | ~ U[0; 1) | mục 10 |
| Critical cell | μ + 2σ toàn cục, μ + σ cục bộ | |
| Bề rộng River | 3–4 cell, ω = 1,75 | mục 42 |
| Số màu kênh | 7 (đã quét 3 / 4 / 7 / 13) | |
| Tầm liên kết G2G | 50 m | suy từ G2G-CHAIN |

## 6. Lớp 1

| Tham số | Giá trị | Nhãn | Ghi chú |
|---|---|---|---|
| f, TTR | 0,1 %; 82,26 % / 80,00 % | [công bố] [7] Bảng 4 | |
| M, k, nghi vấn nhầm | | [suy ra] | Từ P_cam [thiết kế] |
| Một crop mỗi lượt, k lượt độc lập | | [giả định] | Cần nói rõ trong paper |
| Hailo‑8L 257,6 ảnh/s | | [công bố] yếu | Benchmark cộng đồng Hailo, chưa bình duyệt |
| CPU Pi 5 79 ms | | [công bố] yếu | arXiv:2609.16085, chưa rõ nơi đăng |
| Giải mã 5 ms; băng thông 8 GB/s; 20 GMAC/s | | **[giả định]** | Ảnh hưởng không đáng kể (T_match < 0,3 s) |
| DIM = 2 048 | | [công bố] | Kiến trúc ResNet‑50 (He et al., 2016) |
| `S_TRUE`, `S_FALSE`, 2–3 nghi vấn giả (`mission_policy.py`) | | đã thay | P cũ còn dùng; thay bằng mô hình §11 |

## 7. Cần làm, theo mức ảnh hưởng

1. **Nakagami trong `mission_baselines.py`** lệch với Rician của lượt bay. Sửa trực tiếp được.
2. **Rician K = 2 cho A2G** chưa có nguồn. Nó quyết định số gói nhận ở vùng rìa, tức độ rộng River.
3. **Thời gian phát LoRa 0,4 s:** chốt SF và kích thước báo cáo rồi tính theo Semtech. Nó quyết định khe 40 s, đang là độ trễ lớn nhất.
4. **"Qiu 2017" cho α = 3,0:** trích đầy đủ và kiểm lại.
5. **Pha 2 (`HOVER`, `SETTLE`, `BIG`):** giả định, chờ mô hình xác minh.
6. **Chu kỳ 10 ms:** đổi cách gọi trong paper (không phải khe chuẩn).
7. **Độ nhạy −100 dBm:** ghi tên chip và datasheet.
8. **Thời gian kết hợp G2G 100 ms:** tìm nguồn hoặc giữ phần quét độ nhạy.
