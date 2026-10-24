# Bảng tham số toàn bộ giả lập, để kiểm tra nguồn (CLAUDE.md §8 mục 152)

Các giá trị lấy thẳng từ mã đang chạy (2026-10-24), không phải từ tài liệu cũ. Bảng này tiếp nối `uav-l2/docs/PARAM-SOURCES-vi.md` (mục 102) và thêm các tham số lớp 2 mới (MEANDER kiểu luống, động học bay).

**Nhãn:**
- **[chuẩn]**: tiêu chuẩn hoặc quy định.
- **[công bố]**: bài báo, datasheet hoặc benchmark có trích được.
- **[suy ra]**: tính từ các số khác có nguồn.
- **[thiết kế]**: lựa chọn của nghiên cứu. Không cần nguồn ngoài, nhưng phải nói rõ trong bài.
- **[chọn theo thử nghiệm]**: chọn từ một lượt quét của chính dự án (ghi log hoặc tài liệu).
- **[giả định]**: số tạm, **cần nguồn hoặc cần ghi rõ là giả định và quét độ nhạy**.

Cột "Ở đâu" là tệp trong repo. `coop-params.h` = `uav-coop/models/common/coop-params.h`; các tệp `.py` không ghi thư mục nằm trong `uav-l2/tools/`.

## 1. Vô tuyến IEEE 802.15.4 (cả A2G và G2G)

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| R1 | Băng tần, điều chế, tốc độ | 2,4 GHz, O‑QPSK, 250 kbps | `coop-params.h` | [chuẩn] | IEEE Std 802.15.4‑2020 |
| R2 | PSDU tối đa | 127 B | `coop-params.h` (`kPsduBytes`) | [chuẩn] | IEEE 802.15.4 |
| R3 | Khung trên không | 133 B (4 tiền tố + 1 SFD + 1 PHR + 127) | đặc tả mục 2 | [chuẩn] | IEEE 802.15.4 |
| R4 | Thời gian chiếm sóng một khung | 4,256 ms | `coop-params.h` | [suy ra] | 133 × 8 / 250 000 |
| R5 | Tải hữu ích mỗi gói | 99 B | `PAYLOAD` trong `mission_baselines.py`, `l1_mission.py` | [suy ra] | 127 B trừ tiêu đề MAC, bảo mật, FCS (đặc tả mục 2) |
| R6 | Chu kỳ phát của UAV | 10 ms (một gói mỗi 0,5 m ở 50 m/s) | `coop-params.h` (`kSlotS`) | **[giả định]** | Đặc tả mục 2 gọi là "khe mặc định 802.15.4", nhưng chuẩn không có khe 10 ms (aBaseSlotDuration = 0,96 ms). Nên ghi là chu kỳ phát chọn ≥ 2,35 × thời gian chiếm sóng |
| R7 | Công suất phát (UAV và node) | +10 dBm | `coop-params.h` (`kTxPowerDbm`) | [chuẩn] | Dưới trần 20 dBm EIRP của ETSI EN 300 328 |
| R8 | Độ nhạy máy thu | −100 dBm (ns-3: PER 1 % ở PSDU 20 B; đo PER 50 % ở 127 B = −101 dBm) | `coop-params.h` (`kRxSensDbm`) | [công bố] **cần trích** | Mức của chip đời mới (ví dụ TI CC2652R, datasheet). CC2420 chỉ −95 dBm. **Cần ghi tên chip** |
| R9 | MAC lúc River chạy | CSMA/CA không khe, ACK, phát lại theo mặc định ns-3 lr-wpan (macMinBE 3, macMaxBE 5, macMaxCSMABackoffs 4, macMaxFrameRetries 3) | `uav-coop2/examples/coop2-river.cc` | [chuẩn] | Giá trị mặc định của IEEE 802.15.4 |
| R10 | Unicast một khung kèm ACK (đội 2) | 6,88 ms | `mission_baselines.py` (`UC_FRAME`) | [suy ra] | Khung + IFS + ACK theo chuẩn |
| R11 | Multicast một khung (baseline) | 10 ms | `mission_baselines.py` (`BC_FRAME`) | [thiết kế] | Cùng chu kỳ R6 |

## 2. Kênh truyền

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| C1 | A2G, suy hao đoạn 1 | không gian tự do tới d_ref = H = 100 m (−80,05 dB); FSPL 1 m = 40,05 dB | `coop-params.h` (`kFspl1mDb`) | [suy ra] | Friis ở 2,4 GHz (đặc tả mục 2) |
| C2 | A2G, số mũ đoạn 2 | α = 3,0 (quét 2,6 và 3,35) | `coop-params.h` (`kA2gAlpha`) | [công bố] **cần trích đầy đủ** | "Qiu 2017, A2G bán đô thị, độ cao thấp" theo đặc tả mục 2. Chưa có trích dẫn đầy đủ, chưa kiểm lại số |
| C3 | A2G, fading | Rician K = 2, bốc lại mỗi gói | `coop-params.h` (`kA2gRicianK`) | **[giả định]** | Đặc tả mục 2 không có nguồn. Quyết định số gói nhận ở vùng rìa, tức độ rộng River |
| C4 | A2G trong tính toán baseline | Nakagami m = 1,8 | `mission_baselines.py` (`M_NAK`, hàm `per`; dùng cho B3, B8 qua `orbit_per`) | **lệch với C3** | Lượt bay dùng Rician K = 2. Thí nghiệm A2G-RUN cho thấy hai mô hình khác nhau ở đuôi fade tới khoảng 50 lần. **Chưa sửa** |
| C5 | A2G, che khuất | tắt | đặc tả mục 2 | [thiết kế] | |
| C6 | Ăng-ten | đẳng hướng hai đầu | đặc tả mục 2 | [thiết kế] | |
| C7 | G2G, suy hao | n = 3,5 từ 1 m | `coop-params.h` (`kG2gExponent`) | [công bố] | 3GPP TR 38.901, UMi NLoS (35,3 log₁₀ d) |
| C8 | G2G, che khuất | σ = 7,8 dB, cố định mỗi cặp node, thuận nghịch | `coop-params.h` (`kG2gShadowDb`) | [công bố] | 3GPP TR 38.901, UMi NLoS (σ = 7,82 dB) |
| C9 | G2G, fading | Rayleigh (K = 0) theo khối | `coop-params.h` (`kG2gRicianK`) | [thiết kế] | Bi quan, khớp NLoS của 3GPP |
| C10 | G2G, độ dài khối fading | 100 ms | `coop-params.h` (`kG2gCoherenceS`) | **[giả định]** | Node đứng yên, cảnh vật di chuyển. Đã thử 10 ms |
| C11 | Che khuất giữa các cặp | độc lập | `coop2-river.cc` | [giả định] | 3GPP có mô hình tương quan không gian, chưa dùng |
| C12 | Ngưỡng bỏ qua liên kết | MaxLossDb 130 dB | `coop2-river.cc` (`maxLossDb`) | [thiết kế] | Chỉ để tăng tốc giả lập (dưới độ nhạy rất xa) |

## 3. Kênh phản hồi LoRa

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| F1 | Chu kỳ hoạt động | 1 % | `mission_policy.py` (`DUTY`) | [chuẩn] | ETSI EN 300 220‑2, băng 868,0–868,6 MHz |
| F2 | Thời gian phát một bản tin | 0,4 s | `mission_policy.py` (`AIR`) | **[giả định]** | Phải tính bằng công thức Semtech AN1200.13 theo SF, BW, cỡ gói. Khoảng 0,37 s ứng với khoảng 10 B ở SF10/125 kHz. **Cần chốt SF và cỡ báo cáo** |
| F3 | Khoảng giữa hai lần phát | 40 s | `mission_policy.py` (`GAP`) | [suy ra] | F2 / F1 |
| F4 | Pha khe LoRa của mỗi CH | đều trên [0; 40) s, bốc mỗi lần | `l1_rank.py` | [giả định] hợp lý | |
| F5 | Chuyển kết quả tới CH | 0,1 s mỗi cell | `mission_policy.py` (`HOP`) | **[giả định]** | Suy từ 802.15.4 được khoảng 15 ms (2 khung mỗi cell); 0,1 s là thận trọng |

## 4. Miền, node và cụm

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| M1 | Cell lục giác | R = 100 m (rộng 173,2 m, diện tích 25 981 m²) | `map_gen.py` (`R`), `coop-params.h` | [thiết kế] | Mục 9, 11 |
| M2 | Cỡ miền | 80 × K cell mọc ngẫu nhiên (Eden), K = 2–16 | `restructure.domain` | [thiết kế] | Mục 56–57; K lớn để thử kích thước |
| M3 | Độ lồi trước khi khoét hồ | 0,8 | `map_gen.py` (`--convexity`) | [thiết kế] | Mục 10 |
| M4 | Hồ | K hồ, mỗi hồ 10 cell | `restructure.domain` | [thiết kế] | Mục 60–61 |
| M5 | Dạng dải (chỉ ở thử nghiệm yếu tố) | xương sống dài, uốn, rộng 2σ (`--shape`) | `map_gen.py` | [thiết kế] | Mục 147–149; bỏ ở mục 151 |
| M6 | Mật độ node | 1 node / 35 × 35 m | `map_gen.py` (`--spacing`), `uav-coop-deploy --spacings=35` | [thiết kế] | Mục 9 (20–50 m). `coop-params.h` còn ghi `kSpacingM = 30`, không dùng ở lớp 2 |
| M7 | Thuộc tính node | quan sát, tính toán ~ U[0; 1); giao tiếp ~ U(0; 1]; điểm = tích ba thuộc tính | `map_gen.py` | [thiết kế] | Mục 10 |
| M8 | CH | node mạnh nhất cách biên ≥ 300 m (hạ dần 200, 100, 0 m nếu cụm mỏng) | `coop-params.h` (`kChMarginM`), `mission.py` | [thiết kế] | Mục 13 |
| M9 | CL | node mạnh nhất mỗi cell | `uav-coop-deploy` | [thiết kế] | Mục 10 |
| M10 | Tầm liên kết G2G | 50 m | `coop-params.h` (`kLinkRangeM`) | [chọn theo thử nghiệm] | G2G-CHAIN: dư trung vị 11,5 dB ở 50 m |
| M11 | BS | 1 km dưới hộp bao của miền (mặc định); thử thêm đầu xương sống, cạnh, giữa | `restructure.bs_point` | [thiết kế] | Mục 149 |
| M12 | Cụm k-medoids (CHORD-T và các bản cũ) | ≤ 80 cell; `--count K` khi so với MEANDER (cap nâng cho vừa) | `partition.py` (`CAP`), `mission.py` | [thiết kế] | |

## 5. Lớp 3: River

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| L3-1 | Bề rộng River | 3,5 cell (nửa bề rộng ω = 1,75 cell ≈ 303 m) | `river_plan.py` (`width`), `restructure.py` (`OMEGA`) | [thiết kế] | Mục 42 (3–4 cell) |
| L3-2 | Critical cell, ngưỡng toàn cục | điểm CL > μ + 2σ | `river_plan.py` (`kg`) | [thiết kế] | Mục 40–41 |
| L3-3 | Critical cell, ngưỡng cục bộ | > μ + 1σ và lớn nhất trong 2 vòng cell láng giềng thật (cả cell cụm khác) | `river_plan.py` (`kl`, `r`), `--critRing domain` | [thiết kế] | Mục 41, 135 |
| L3-4 | CH luôn là critical cell | | `river_plan.py` | [thiết kế] | Mục 41 |
| L3-5 | Cửa sổ dữ liệu mỗi critical cell | 400 kB (4 041 gói), bản sao gần nó nhất dọc Axe | `--windowKB 400 --windowAt crit` | [thiết kế] | Mục 106, 120; khớp bộ manh mối lớp 1 |
| L3-6 | Axe nhận gói ngoài cụm sát biên | có (`--axeNear`) | `river_plan.py` | [thiết kế] | Mục 135 |
| L3-7 | Banks | theo pháp tuyến cục bộ của Axe (`--banks local`) | `river_export.py` | [thiết kế] | Mục 103 |
| L3-8 | Số màu kênh lưới cell | 7 (cùng kênh cách 3 cell); cặp gateway kênh riêng | `coop2-river.cc` (`--colours`) | [chọn theo thử nghiệm] | Mục 53–54 (đã quét 3/4/7/13). `coop-params.h` còn `kTdmaReuse = 3`, không dùng ở River |
| L3-9 | Chọn cặp gateway | chất lượng liên kết tốt nhất (BS biết che khuất) | `coop2-river.cc` (`--gwSelect quality`) | [thiết kế] | |
| L3-10 | Lập lịch | một máy phát mỗi cell và mỗi cặp gateway, xoay vòng, trên MAC R9 | `coop2-river.cc` | [thiết kế] | Mục 51 (lưới PECEE) |
| L3-11 | Giới hạn thời gian River | 900 s | `mission.py` (`--limit=900`) | [thiết kế] | |
| L3-12 | Circle thích ứng (biến thể ad12) | mỗi thành viên 400 gói thiếu; 2–12 thành viên | `coop2-river.cc` (`share`, `circleMin/Max`) | [thiết kế] | Mục 66–67 |
| L3-13 | Trickle (baseline) | trang 64 gói; I_min 1 s; I_max 64 s; k = 1 | `coop2-river.cc` | [công bố] | RFC 6206 (Trickle), Deluge (Hui & Culler, SenSys 2004) |

## 6. Lớp 2: đường bay và chia cụm

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| L2-1 | Độ cao, tốc độ đội 1 | 100 m; 50 m/s | `coop-params.h` | [thiết kế] | Mục 1. Nên kèm một UAV cánh bằng thực tế làm tham chiếu |
| L2-2 | Góc nghiêng khi rẽ | 45° (độ nhạy 30°, 60°) | `kin_time.py` (`PHIS`) | **[giả định]** | Cần nguồn cho UAV cánh bằng cỡ nhỏ |
| L2-3 | Bán kính rẽ tối thiểu | 254,9 m | `coop-params.h` (`kMinTurnRadiusM`) | [suy ra] | v² / (g tan φ) với L2-1, L2-2 |
| L2-4 | Tốc độ tối thiểu khi giảm tốc | 25 m/s | `kin_time.py` (`VMIN`) | **[giả định]** | Trên tốc độ thất tốc (mục 38: cánh bằng không hover) |
| L2-5 | Gia tốc dọc đường bay | ±2 m/s² | `kin_time.py` (`ACC`) | **[giả định]** | Cần nguồn |
| L2-6 | Hồ sơ tốc độ | v ≤ min(50, √(g tan φ / κ)), giới hạn gia tốc, hai lượt tiến/lùi | `kin_time.py` | [công bố] dạng | Hồ sơ thời gian tối thiểu cổ điển (ràng buộc gia tốc ngang và dọc) |
| L2-7 | Điều kiện giao đủ | mỗi cụm bay ≥ Q × 10 ms trên cell của nó (40,4 s với 400 kB); thiếu thì giảm tốc tới L2-4, rồi lượn vòng | `kin_time.py` | [thiết kế] | Mục 144 |
| L2-8 | CHORD-T: hướng ứng viên | quét 0–178°, bước 2°; giữ ≤ 6 hướng cách nhau ≥ 10°, dài ≥ 60 % hướng dài nhất và ≥ 80 % một bộ manh mối | `mission.py` (`--chordTour 0.6,0.8`) | [chọn theo thử nghiệm] | Mục 136–138 (CLUE 80 % do người dùng chốt) |
| L2-9 | CHORD-T: chọn tour | tổng độ trễ của critical cell nhỏ nhất, Held-Karp tới 13 cụm, gần đúng (thứ tự + quy hoạch động + dời/2-opt) từ 14 cụm | `chord_tour.py` (`EXACT`) | [thiết kế] | Mục 149. Held-Karp hiện tại chưa chính xác hoàn toàn với mục tiêu độ trễ |
| L2-10 | MEANDER: bề rộng luồng | 8 cell (khoảng 1,39 km) | `meander_lane.py` (`--lane`) | [chọn theo thử nghiệm] | `SAT-vi.md` (điểm bão hoà 8–10 cell) |
| L2-11 | MEANDER: luồng mỏng | luồng < 47 cell (CAPL / 4) gộp vào luồng kề | `meander_lane.py` | [thiết kế] | |
| L2-12 | MEANDER: cắt cụm | theo độ dài đất dưới đường bay, Axe mỗi cụm ≥ 2,4 km (`--minAxe 2.4`), ≤ 190 cell | `meander_lane.py` (`CAPL`, `--minAxe`) | [chọn theo thử nghiệm] | Mục 149: Axe < 2,02 km thì cụm không nhận đủ bộ manh mối ở 50 m/s |
| L2-13 | MEANDER: cắt theo số cell (bản cũ) | ≤ 14 cell dọc luồng (`SPAN`) | `meander_lane.py` | [chọn theo thử nghiệm] | `SAT-vi.md`; thay bằng L2-12 |
| L2-14 | MEANDER: độ thẳng | thang làm mượt 0,5 km (quét 0; 0,5; 1; 2; 4 km; thẳng hẳn) | `meander_lane.py` (`--straight`) | [chọn theo thử nghiệm] | Mục 151 |
| L2-15 | MEANDER: kéo về critical cell | chỉ cell xa hơn 5 cell; mỗi lần kéo ≤ 1 cell | `meander_lane.py` (`--reach 5`, `BEND`) | [thiết kế] | Mục 151 (người dùng đặt 5 cell) |
| L2-16 | Nối liền giữa hai cụm | đầu cụm sau cách cuối cụm trước ≤ 1 km, lệch hướng ≤ 30° | `mission_policy.py` (`SEAM_GAP`, `SEAM_DEG`) | [thiết kế] | |

## 7. Nhiệm vụ và đội 2

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| T1 | Tốc độ đội 2 (cánh quay) | 15 m/s | `l1_rank.py` (`V2`) | [thiết kế] | Mục 73 |
| T2 | Ổn định trước khi phát | 5 s | `mission_baselines.py` (`SETTLE`) | **[giả định]** | |
| T3 | Tệp xác minh | 1 MiB (khoảng 20 ảnh tham chiếu) | `mission_baselines.py` (`BIG`), `l1_rank.py` (`REF_IMAGES`) | **[giả định]** | Mục 73: số tạm |
| T4 | Thời gian xác minh | 78,1 s = T2 + unicast T3 + đối sánh 20 ảnh | `l1_rank.py` (`VERIFY`) | [suy ra] | |
| T5 | Chính sách đội 2 | xuất phát cùng đội 1, chờ ở tâm có trọng số, đổi đích giữa đường, đi khi p ≥ β·P_U với β = 1/4 | `l1_rank.py` (`-puq-stage-zero-redir`) | [chọn theo thử nghiệm] | `L1-MODEL-vi.md` (β chọn trên 40 bản đồ) |
| T6 | Thời gian rời cụm | 50 m/s đều, hoặc theo động học L2-6/L2-7 (`-kt`) | `l1_rank.py` | [thiết kế] | Mục 149 |
| T7 | Chỉ số chính | T\*: lúc xác minh xong cell có điểm xác minh cao nhất | `l1_rank.py` | [thiết kế] | Mục 113–114 |
| T8 | Số lần bốc mỗi bản đồ | 100 | `l1_rank.py --draws` | [thiết kế] | |
| T9 | Đối sánh cố định (mô hình cũ) | 5 s; lơ lửng 30 s | `mission_policy.py` (`MATCH`, `HOVER`) | [giả định] | Chỉ còn ở chính sách cũ; T\* hiện dùng T4 và L1-12 |

## 8. Lớp 1: mô hình điểm

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| L1-1 | Số crop mỗi camera | M = 223 | `l1_model.py` (`M`) | [suy ra] | Từ điểm vận hành đầu tiên của Li et al. ECCV 2018 (nhận nhầm 0,1 % mỗi crop) và báo nhầm 20 % mỗi camera: ln(0,8)/ln(0,999) |
| L1-2 | Bộ manh mối | 12 ảnh: 2 mặt × 24,9 kB, 4 dáng × 49,9 kB, 6 bộ phận × 24,9 kB; 4 036 gói (≤ 4 041 của 400 kB) | `l1_model.py` (`CLUESET`) | [thiết kế] | Mục 94, 99 (ảnh 15–50 kB, 3–6 góc cộng crop bộ phận) |
| L1-3 | Độ nhận diện r_j | mặt 0,80–0,90; dáng 0,88–0,95; bộ phận 0,95–0,99 | `l1_model.py` | **[giả định]** | Giả định kịch bản (mặt khó chụp trung thành nhất) |
| L1-4 | Độ quan trọng w_j (do BS chấm) | mặt 4; dáng 2; bộ phận 2/3 (khía cạnh 40/40/20 %) | `l1_model.py` | [thiết kế] | Mục 113–114 |
| L1-5 | Số chiều hiệu dụng | d = 128 (quét 64, 256) | `l1_model.py` (`DIM`) | **[giả định]** | Số chiều nội tại nhỏ hơn danh nghĩa: Ansuini et al., NeurIPS 2019 |
| L1-6 | Độ giống của người lạ (TB / độ lệch) | mặt 0,10 / 0,10; dáng 0,35 / 0,12; bộ phận 0,45 / 0,15 | `l1_model.py` (`STRANGER`) | **[giả định]** | Thứ tự theo ArcFace (CVPR 2019), BoT re-ID (CVPRW 2019), Ye et al. TPAMI 2022, Lin et al. PR 2019; giá trị là giả định |
| L1-7 | Người mặc giống | ρ = 2 % (quét 0, 5 %); độ giống bộ phận 0,85 / 0,05 | `l1_model.py` (`RHO`, `LOOK`) | **[giả định]** | Tập mở: Li et al. ECCV 2018; Zheng et al. TPAMI 2016 |
| L1-8 | Thứ tự phát manh mối | xen kẽ theo khía cạnh | `l1_model.py` (`order`) | [thiết kế] | Mục 113 |
| L1-9 | Thiết bị critical cell | Raspberry Pi 5 + Hailo-8L: 257,56 ảnh/s (ResNet-50, batch 8) | `l1_mission.py` (`DEVICES`) | [công bố] yếu | Hailo Community benchmark, 06/2024 (chưa bình duyệt) |
| L1-10 | CPU Pi 5 (độ nhạy) | 79,08 ms mỗi ảnh (ResNet-50 INT8, ONNX Runtime) | `l1_mission.py` | [công bố] yếu | arXiv:2609.16085, Bảng 2 (chưa rõ nơi đăng) |
| L1-11 | Giải mã, băng thông, MAC | 5 ms mỗi ảnh; 8 GB/s; 20 GMAC/s; vector 2 048 chiều | `l1_mission.py` | **[giả định]** (vector: [công bố] ResNet-50) | Ảnh hưởng nhỏ: thời gian đối sánh < 0,3 s |
| L1-12 | Thời gian đối sánh | L × giải mã + L / thông lượng + tìm trong kho M | `l1_mission.match_time` | [suy ra] | Mục 95–97 |
| L1-13 | Hiệu chuẩn tại BS | 2 000 camera mô phỏng | `l1_model.py` | [thiết kế] | |

## 9. Baseline

| # | Tham số | Giá trị | Ở đâu | Nhãn | Nguồn / ghi chú |
|---|---|---|---|---|---|
| B-1 | B3/B8: bán kính nhóm critical cell | 300 m, 500 m | `mission_baselines.py` (`RADII`) | [thiết kế] | Mục 72 |
| B-2 | B5 quét luống: bề rộng luống | thử 12 → 3 cell, lấy luống rộng nhất mà mọi critical cell đủ manh mối với xác suất ≥ 0,9 | `l1_rank.py` (`LANES`) | [thiết kế] | Mục 134 |
| B-3 | B8 bay vòng | bán kính L2-3 quanh tâm nhóm | `l1_rank.py` | [suy ra] | |
| B-4 | Kênh baseline | xem C4 (Nakagami, lệch) | | **lệch** | |

## 10. Cần kiểm hoặc bổ sung nguồn, xếp theo mức ảnh hưởng

1. **C4: Nakagami trong baseline lệch với Rician của lượt bay.** Sửa trực tiếp được.
2. **C3: Rician K = 2 cho A2G** chưa có nguồn. Quyết định số gói nhận ở vùng rìa, tức độ rộng River.
3. **F2: thời gian phát LoRa 0,4 s.** Chốt SF và cỡ báo cáo rồi tính theo Semtech. Nó quyết định khe 40 s, đang là độ trễ lớn nhất của nhiệm vụ.
4. **C2: "Qiu 2017" cho α = 3,0.** Trích đầy đủ và kiểm lại.
5. **L2-2, L2-4, L2-5: động học UAV cánh bằng** (góc nghiêng 45°, tốc độ tối thiểu 25 m/s, gia tốc 2 m/s²). Cần một mẫu UAV thực tế làm nguồn.
6. **T2, T3: pha 2** (ổn định 5 s, tệp 1 MiB). Giả định, chờ mô hình xác minh.
7. **L1-3, L1-5, L1-6, L1-7: tham số kịch bản lớp 1.** Đã có quét độ nhạy; trong bài ghi rõ là giả định.
8. **R6: chu kỳ 10 ms.** Đổi cách gọi trong bài (không phải khe chuẩn).
9. **R8: độ nhạy −100 dBm.** Ghi tên chip và datasheet.
10. **C10: khối fading G2G 100 ms.** Tìm nguồn hoặc giữ phần quét.
