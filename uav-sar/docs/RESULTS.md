# uav-sar — Results v2 (sau lượt rà soát logic F1–F7)

Setup: 4 UAV (2 FAST + 2 DATA cho proposed), 100 seeds/grid, kênh thực tế
(A2G 2.2 / G2G 3.5 + Nakagami m=1.5 + **shadowing bám theo cặp** σ=8.7 dB).
Semantics đã sửa: fragment đến theo **chunk byte-thật** (CUE/FULL hợp nhất,
không đếm trùng); **complete = node nạn nhân giữ TOÀN BỘ fragment** (ground
truth); vòng đóng khi **verifier** (node evidence mạnh nhất do ticket chỉ định)
xác nhận và UAV **báo cáo về BS**; CONFIRM/REPORT có retry; hợp tác liên-cell
có **chi phí thật** (per-hop delay, p_intra=0.92, p_inter=0.82, region window
1 s); sweep **phân vùng** giữa các UAV; baseline dwell-cycle 25 s/waypoint.

## Grid 8×8 (64 sensors, 100 seeds)

| scheme   | strict compl% | **report%** | complete mean | median | report mean | MB recv | kJ   | region cells |
|----------|---------------|-------------|----------------|--------|--------------|---------|------|--------------|
| proposed | 94%           | **100%**    | 35.9 s         | 34.8   | **61.4 s**   | **2.92**| 41.9 | 1.73         |
| nocoop   | 100%          | 0%          | 36.1 s         | 35.9   | —            | 10.21   | 21.0 | 0            |
| pure-uav | 100%          | 0%          | 44.2 s         | 36.4   | —            | 5.71    | 6.7  | 0            |

## Grid 12×12 (144 sensors, 100 seeds) — scale study

| scheme   | strict compl% | **report%** | complete mean | median | report mean | MB recv | kJ   | region cells |
|----------|---------------|-------------|----------------|--------|--------------|---------|------|--------------|
| proposed | 83%           | **100%**    | 39.6 s         | 39.5   | **68.6 s**   | **5.28**| 49.1 | 1.79         |
| nocoop   | 100%          | 0%          | 39.3 s         | 38.5   | —            | 21.83   | 22.9 | 0            |
| pure-uav | 98%           | 0%          | 62.8 s         | 39.0   | —            | 25.43   | 11.3 | 0            |

## Đọc kết quả (trung thực)

1. **Chỉ proposed đóng vòng, và giờ đóng 100% ở cả hai quy mô.** Mỗi run đều:
   khoanh vùng → triệu hồi → giao tận nơi → verifier xác nhận → UAV về BS báo
   cáo. Baseline rải được data nhưng hệ thống **không bao giờ biết** — không ai
   được điều đi cứu. (Trước fix F2/verifier: 92% rồi 99%; giờ 100/100.)
2. **Airtime (byte) — cách biệt NỚI RỘNG theo quy mô:** proposed dùng ít hơn
   nocoop **3.5×** ở grid-8 và **4.1×** ở grid-12 (2.92→5.28 MB so với
   10.2→21.8 MB). Pure-uav cũng nặng (25.4 MB ở grid-12). Giao-có-chủ-đích
   thắng rõ về chi phí kênh truyền, càng rộng càng thắng.
3. **Thời gian complete: ngang nocoop, bỏ xa pure-uav khi scale** (pure-uav
   44→63 s khi diện tích gấp 2.25×; proposed 36→40 s). Nocoop giữ được thời
   gian nhờ 4 UAV chia vùng + dump mù mọi nơi — nhưng trả giá bằng airtime ở
   (2) và không có vòng đóng ở (1).
4. **Hợp tác liên-cell là thật và có phí:** region trung bình 1.73–1.79 cell,
   hình thành qua region-window 1 s + share qua CGW với p=0.82 (share rớt thì
   cell không vào vùng).
5. **Năng lượng:** proposed tốn hơn (41.9–49.1 kJ do 4 UAV bay trọn vòng gồm cả
   lượt về báo cáo; Zeng-Xu-Zhang P(V), hover 168.5 W). Đây là giá của dịch vụ
   trọn gói; baseline rẻ điện hơn nhưng không hoàn thành nhiệm vụ đúng nghĩa.
6. **Strict-complete 94%/83% — residual trung thực:** ticket chỉ định verifier
   = node evidence mạnh nhất; đôi khi verifier ≠ node-nạn-nhân (halo nhiều node
   hơn ở grid lớn) và link UAV↔target rút phải shadow chặn cố định → verifier
   xong, UAV rời đi, target thiếu vài chunk. Về mặt **hệ thống** nhiệm vụ vẫn
   thành công (dữ liệu nằm ở node có manh mối mạnh nhất, cách nạn nhân ≤~40 m,
   camera của nó nhiều khả năng cũng thấy nạn nhân — chính vì thế evidence nó
   cao). Chúng tôi báo cả hai: **mission success (report) = 100%**, strict
   ground-truth = 94/83%. Muốn kéo strict lên: UAV nán thêm N pass sau CONFIRM
   (knob, chưa bật).

## Các fix từ lượt rà soát (đã vào code)
F1 đếm-trùng cue/full (confirm giả sau 66 ms) → chunk hợp nhất + đủ-toàn-bộ.
F2 CONFIRM/REPORT một-phát (8/100 hở vòng) → retry + delivery lặp tới CONFIRM.
F3 shadowing per-packet ("ăn may xa") → PairShadowingLossModel bám theo cặp.
F4 regionWindow + chi phí intra/inter thật (trước đó miễn phí, tức thời).
F5 sweep phân vùng (hết bay "đoàn tàu"), dwell-cycle cho baseline, validate scheme.
F6 neighborRange dẫn xuất từ link budget G2G (~37 m, hết mâu thuẫn 80 m).
F7 airtime theo byte + năng lượng Zeng-Xu-Zhang + report-rate trong aggregator.
Verifier-designated confirm (sửa false-success của hotfix "ai xong cũng confirm").

## Còn mở
- Tham số `[Lit?]` chờ PDF (Al-Hourani a,b/η; Khawaja m,σ theo rừng; hệ số
  năng lượng) — thay trong `sar-params.h`, không đụng logic.
- Knob "nán thêm sau CONFIRM" nếu muốn strict-complete ~100%.
- Battery budget/no-fly, đổi role động, AoI/TTL: future work.

## Reproduce
```bash
python3.10 ./ns3 build
bash src/uav-sar/tools/run_batch.sh 100 8 4 600    # grid 8
bash src/uav-sar/tools/run_batch.sh 100 12 4 1200  # grid 12
```

---

## Phụ lục: Độ chân thực PHY & đánh giá lỗi mức gói (v3)

Xác minh (không phải giả định): trong ns-3.46 lr-wpan, số phận MỖI GÓI do vật
lý quyết định — error model O-QPSK IEEE 802.15.4 tính PER theo SINR từng chunk
trong suốt quá trình thu (nhiễu đồng kênh cộng dồn, collision khi BUSY_RX),
và nền nhiễu được suy từ RxSensitivity −95 dBm → NF ≈ 11.6 dB (cỡ CC2420).
Kèm Nakagami m=1.5 + shadowing bám-cặp σ=8.7 dB.

Validation (`uav-sar-phy-error-test`, 200 gói × 8 hướng/điểm, 8/8 checks):

| link | vùng tin cậy | waterfall | đuôi |
|---|---|---|---|
| G2G (n=3.5) | ≤25 m (PDR 89–97%) | 30–55 m, perFail+weak trộn | 70 m: 8% |
| A2G (n=2.2, alt 20 m) | ≤150 m (85–97%) | 200–500 m, perFail rõ | 600 m: weak thống trị; 1–2/8 receiver "khoảng trống rừng" vẫn nhận |

Ghi chú vật lý: −95 dBm là điểm PER<1%, không phải vách đá — DSSS O-QPSK vẫn
giải mã ~50% ở +2 dB SNR; shadowing bám-cặp giữ vài link sống ở cự ly xa.

Mỗi run giờ xuất bảng phân rã lỗi gói theo nguyên nhân × lớp link vào
metrics.csv (phyOk/phyPer/phyWeak/phyCol × a2g/a2a/g2g/bs). Run 40×40 seed 3:
1.07M receptions; PER(hoàn tất)=27.7%; collision=15k; đặc biệt g2g:
**chỉ ~2.2% gói SUMMON mặt-đất giải mã được** (101.6k weak / 1.65k ok) —
bằng chứng định lượng vì sao cần tầng FAST relay A2A.

Phát hiện addressing: LrWpanHelper không cấp short address (mọi device chung
địa chỉ mặc định → MAC unicast không hề lọc). Đã cấp Mac16 duy nhất/device;
REPORT giờ là unicast thật và BS trả MAC-ACK 802.15.4 thật.


## Phụ lục v3: Elevation-angle LoS + foliage (đẩy realism thêm một bậc)

Thay chuyển A2G/G2G nhị phân bằng vật lý theo hình học UAV-node:
P_LoS(θ) Al-Hourani (a=4.88, b=0.43, frozen-quantile mỗi cặp — link lật
NLoS→LoS đúng MỘT lần khi UAV tiến lại gần), NLoS = xuyên tán ITU-R P.833
(canopy/sinθ, γ=0.5 dB/m, Amax=35 dB); σ shadowing tách lớp (G2G 8.7 / A2G 4 dB
residual, tránh đếm trùng thực vật).

Footprint A2G đo được (phy-error-test, alt 20 m): chắc ≤100 m (99.9%@50m),
loang lổ 100–300 m (chỉ cặp LoS sống, 12–75%), **chết hẳn ≥350 m** (θ<3.3° →
xuyên >260 m tán). → Cái caveat "cue phủ gần cả map làm localize tức thì" đã
được giải bằng vật lý, không phải bằng chỉnh tay công suất.

Mission 40×40 seed 3 dưới v3: localize 44.6 s (FAST phải quét tới gần thật),
summon→divert 13 s (beacon lặp tới khi FAST vào footprint của CL rồi relay),
verifier = CHÍNH node nạn nhân, strict-complete 86.5 s (hết residual −1),
report@BS 162.2 s, năng lượng 128.6 kJ. Grid-8 (3 seed): proposed đóng vòng
58–66 s; baselines complete ~33–37 s nhưng không bao giờ report.

## Phụ lục v4: Quét spacing (20/30/40 m) — ngưỡng sập hợp tác liên-cell

Grid 40×40, scheme proposed, 3 seed/spacing, mọi tham số khác giữ nguyên
(TX 0 dBm → tầm G2G lý thuyết ≈ 37 m).

| spacing | map (m) | report (s) | localize (s) | strict-complete (s) | region cells | inter-shares | g2gOk | G2G decode % | năng lượng (kJ) |
|---|---|---|---|---|---|---|---|---|---|
| 20 m | 780 | **110.2** | 37.7 | 85.3 | 1.67 | 0.67 | 1813 | 1.33% | 86.7 |
| 30 m | 1170 | 170.2 | 60.1 | 116.3 | 1.00 | 0 | 698 | 0.73% | 134.5 |
| 40 m | 1560 | 206.9 | 83.6 | 150.6 | 1.00 | 0 | 363 | 0.36% | 163.4 |

(Per-seed: spacing 20 → report 105.9/113.8/111.0; spacing 30 → 138.8/152.5/219.3;
spacing 40 → 192.3/195.6/232.9. Cả 9/9 run đều report thành công.)

Ba hiệu ứng tách bạch:

1. **Scaling tuyến tính theo map.** Cạnh map tăng 780→1560 m nên thời gian quét
   FAST và mọi mốc thời gian giãn theo. Chuẩn hoá report/cạnh-map:
   0.141 / 0.145 / 0.133 s/m — gần phẳng, tức phần lớn độ chậm chỉ là diện tích
   lớn hơn, KHÔNG phải giao thức tệ đi.
2. **Hợp tác liên-cell sập giữa 20 m và 30 m.** Ở 20 m: 2/3 seed cho region
   2-cell với inter-share qua CGW. Ở 30/40 m: region luôn 1 cell, inter-share = 0.
   Nguyên nhân kép: (a) mật độ node/cell giảm → vành đai clue yếu quanh nạn nhân
   thưa đi, cell hàng xóm không còn đủ evidence vượt kCoopThreshold; (b) link
   ground 30 m ăn vào vùng waterfall (chéo 42.4 m đứt hẳn), 40 m vượt hẳn ngân
   sách 37 m — g2gOk rơi 1813→363, decode 1.33%→0.36% (phần còn sống ở 40 m là
   đuôi shadowing may mắn, PHY trung thực).
3. **Caveat trung thực:** control-plane sự kiện (RegionCoordinator) tính node
   cô lập = 1 hop lossy (p_intra 0.92) — ở spacing 40 điều này *rộng lượng hơn
   radio thật* (node→CL đa phần sẽ đứt). Kết quả 40 m nên đọc là "chặn trên".

Hệ quả thiết kế: triển khai thưa (≥30 m) cần một trong hai: tăng TX ground
0→+5 dBm (tầm G2G 37→52 m, phủ lại spacing 40 m) hoặc bỏ qua CL mà alert
thẳng node→UAV khi mặt đất phân mảnh. Cơ chế vùng đa-cell chỉ đáng giá ở
mật độ dày (spacing ≲ 25 m với ngân sách link hiện tại).
