# Thực nghiệm, baseline và kết quả

- **Phiên bản:** 2026-10-26. Lời gốc: CLAUDE.md §8 (mục 1–8 kênh, 48–55 River, 68–73 nhiệm vụ, 120–169 lớp 2 và baseline, 182 bảng chung, 183 tài liệu này).
- **Bảng số gốc và seed:** `uav-l2/docs/RESULTS-vi.md`. Tài liệu này mô tả phương pháp và tổng hợp; khi số lệch nhau, `RESULTS-vi.md` và các log là nguồn đúng.
- **Tài liệu đi kèm:** `paper/SUMMARY-vi.md` (tổng hợp), `paper/LMTOUR-vi.md` (LM-Tour).

> **Nhãn số liệu.** Mọi số ở đây là **số thăm dò**. Bảng chính (§5) dùng một bản đồ cho mỗi cỡ mạng, một lượt ns-3 cho mỗi cụm, và 100 lượt bốc lớp 1. Quy tắc của dự án: N ≥ 120 mới được công bố (CLAUDE.md §6). Chiến dịch nhiều bản đồ (mục 165) chưa chạy.

---

## 1. Thiết lập chung

### 1.1 Công cụ
- **ns-3.46**, module `lr-wpan`: MAC IEEE 802.15.4 đầy đủ (CSMA/CA, ACK, phát lại).
- **Ba chương trình ns-3** (thư mục `uav-coop`, `uav-coop2`), đóng băng trong `scratchpad/CAMP-BIN4`:

| binary | việc | sha256 (16 ký tự đầu) |
|---|---|---|
| `deploy-bin` | sinh node, vai trò CH/CL, định tuyến cell | `e38d9e5efe2d696e` |
| `pass-bin` (v3) | lượt bay của đội 1 theo hồ sơ vận tốc, suy hao thêm `--lossDb`, bitmap gói nhận của mọi node | `6f70076266e4a657` |
| `river-bin` | River, kéo trực tiếp, Trickle; `--repair` | `2e636b6dcacf9bd5` |

- **Python** (`uav-l2/tools/`): bản đồ, chia cụm, đường bay, tour, mô hình lớp 1, toàn bộ nhiệm vụ, các baseline mức mô hình, bảng, hình.

### 1.2 Mạng mặt đất
- Miền "khối có hồ" sinh ngẫu nhiên, cell lục giác bán kính 100 m, khoảng 21 node mỗi cell.
- Cụm: k-medoids có giới hạn 80 cell trên đồ thị cell (cluster có sẵn).
- CH: node mạnh nhất cách biên ≥ 300 m (nới 200, 100, 0 m khi cụm mảnh). CL: node mạnh nhất mỗi cell.
- Critical cell: cell của CH, cell có điểm CL > μ + 2σ, và cell > μ + σ mạnh nhất trong 2 vòng cell quanh nó (vòng xét trên toàn miền, `--critRing domain`).
- Định tuyến PECEE tính trước: một cặp gateway giữa hai cell kề, lưới kênh 7 màu, mỗi cặp gateway một radio và kênh riêng.

**Ba bản đồ của bảng chính:**

| bản đồ | `--clusters` / `--seed` | cụm | critical cell |
|---|---|---|---|
| k8-s1 | 8 / 1 | 8 | 45 |
| k12-s1 | 12 / 1 | 12 | 66 |
| k16-s1 | 16 / 1 | 15 | 92 |

### 1.3 Kênh

**A2G:** không gian tự do tới 100 m (−80,05 dB), sau đó số mũ α = 3; fading Rician K = 2 bốc lại mỗi gói; UAV phát +10 dBm ở độ cao 100 m; độ nhạy −100 dBm. Bốn chế độ môi trường cộng một suy hao cố định η vào mọi liên kết UAV–node (mục 163), hiệu chỉnh trên ns-3 sao cho bán kính hiệu quả R50 (xác suất một gói 127 B tới được node còn 1/2) trúng mục tiêu:

| chế độ | η (dB) | R50 (m) | R10 (m) | p(0) | p(100 m) | p(200 m) | p(500 m) |
|---|---|---|---|---|---|---|---|
| open | 0 | 1015 | 1366 | 0,999 | 0,999 | 0,996 | 0,950 |
| r500 | 9,03 | 498 | 678 | 0,998 | 0,993 | 0,968 | 0,494 |
| r200 | 19,77 | 199 | 284 | 0,960 | 0,887 | 0,495 | 0,000 |
| r100 | 25,74 | 99 | 162 | 0,838 | 0,496 | 0,014 | 0,000 |

![p(r) bốn chế độ](../uav-l2/docs/figures/a2g-env-p-of-r-4modes.png)

*Hình 1: xác suất một gói tới được node theo khoảng cách ngang, đo trên lượt bay ns-3; bốn đường từ phải sang trái là open, r500, r200, r100.*

**G2G:** số mũ 3,5, che khuất log-normal σ = 7,8 dB cố định theo cặp node, fading Rayleigh theo khối 100 ms (3GPP TR 38.901 UMi NLoS). Một chặng có ACK mất khoảng 5–7 ms.

### 1.4 Đội bay, dữ liệu, phản hồi
- **Đội 1:** UAV cánh bằng, 50 m/s, độ cao 100 m, nghiêng 45° (bán kính quay 255 m), gia tốc ±2 m/s², không lơ lửng. Phát một gói 99 B mỗi 10 ms, tức mỗi 0,5 m.
- **Bộ manh mối:** 12 ảnh (2 mặt, 4 dáng, 6 bộ phận), 400 kB, 4 041 gói mỗi bản sao, phát xen kẽ khía cạnh. Một ảnh chỉ dùng được khi đủ mọi gói của nó (hoặc đủ gói mã khi mã fountain).
- **Phản hồi:** critical cell → CH (0,1 s mỗi cell trên đường) → LoRa: mỗi CH một bản tin mỗi 40 s, pha ngẫu nhiên.
- **Đội 2:** UAV cánh quay, 15 m/s, xác minh một cell khoảng 78 s (ổn định 5 s, bộ tham chiếu 1 MB bằng unicast có ACK, đối sánh 0,2 s).

### 1.5 Lớp 1 (mô hình điểm)
Chi tiết: `paper/L1-MODEL-vi.md`.
- Mỗi manh mối j có độ nhận diện r_j < 1 và độ quan trọng w_j do BS chấm.
- Mỗi critical cell có M = 223 crop người lạ; giá trị khớp m_ij = r_j·a_{i,v(j)} + ε_ij, nhiễu theo số chiều hiệu dụng d = 128.
- Điểm cell S_c tính hai bước (trong khía cạnh rồi giữa các khía cạnh) trên tập manh mối cell giữ trọn vẹn. Báo cáo: S_c và bitmap 12 bit.
- c\* là critical cell có điểm xác minh U_c cao nhất. BS suy ra P(cell là c\*) từ các báo cáo.

### 1.6 Thiết kế và chỉ số
- **Ghép cặp:** mọi phương án trên cùng bản đồ và cùng kênh dùng cùng bitmap ns-3 (mission index 100000·K + 100·seed + k), cùng realisation thu gói mã fountain (khoá theo bản đồ và kênh), cùng 100 lượt bốc lớp 1 (khoá theo bản đồ, lượt, cell).
- **Chỉ số chính:** **T\***, thời điểm đội 2 xác minh xong c\*. Phụ: phân vị 90 của T\*, hạng của c\* trong thứ tự thăm, T_all (thăm hết và về BS), thời gian bay của đội 1, thời điểm critical cell sẵn sàng, số lượt truyền mặt đất.
- **Thống kê:** trung bình ± nửa khoảng tin cậy 95 % theo lượt bốc; chênh ghép cặp so với CHORD và tỉ lệ lượt bốc CHORD nhanh hơn.

---

## 2. Phương án đề xuất: CHORD (P\*)

### 2.1 Thành phần

| Lớp | Lựa chọn | Cờ |
|---|---|---|
| Lớp 2: đường bay | Mỗi cụm một đường thẳng qua CH (dây cung). Hướng và thứ tự cụm chọn chung theo độ trễ (CHORD-T, CLUE 80 %). Nối Dubins. Giảm tốc hoặc lượn để mỗi cụm nhận đủ một bản bộ manh mối | `--chordTour 0.6,0.8 --kinPass` |
| Mã | Bộ manh mối mã fountain dạng hệ thống, phát suốt chuyến bay | `-fcd` |
| Lớp 3: River | Cửa sổ 400 kB theo từng critical cell, Axe gồm cả gói phát sát mép cụm, Circle chuẩn bị sẵn, sửa gói thiếu sau 20 s | `--windowKB 400 --windowAt crit --axeNear --riverRepair 20` |
| Phản hồi | Báo hai lần: tự giải mã + gom trong cell, rồi River; mỗi báo cáo cộng dồn mọi thứ cell đã có | `P+prog` |
| Pha 2 | Cất cánh lúc 0, đón đầu, ngưỡng β = 1/4, đổi hướng giữa đường | `-zero -stage -puq -redir` |

Tên phương pháp trong `l1_rank`: `P+prog-kin-puq-stage-zero-redir-kt-fcd`.

### 2.2 Mã giả

```text
Algorithm CHORD-T  (BS, before take-off)
Input: clusters with CH and critical cells (n_k), BS, ρ = 255 m, clue-set length L_Q = QΔ ≈ 2.02 km
 1: for each cluster k:
 2:     for each bearing θ ∈ {0°, 2°, …, 178°}: ℓ_k(θ) ← length of the line through CH_k at θ inside k
 3:     Cand_k ← {θ : ℓ_k(θ) ≥ 0.6 · max ℓ_k and ℓ_k(θ) ≥ 0.8 · L_Q}         ▷ FRAC 0.6, CLUE 80 %
 4:     each θ ∈ Cand_k gives a leg (entry → CH → exit) in two directions; its time = ℓ/v + delivery fix
 5: choose one leg and direction per cluster and the visiting order minimising Σ_k n_k · leave_k
        (Held-Karp over (cluster, bearing, direction) for ≤ 13 clusters, else heuristic + DP; Dubins links)
 6: for each cluster in order: SPEEDFIT(leg)

Algorithm SPEEDFIT(leg)                                   ▷ pass_speed.fit
 1: if the packets sent over cluster cells at 50 m/s ≥ Q: fly at 50 m/s
 2: else cap ← largest speed in [25, 50] m/s (bisection) with ≥ Q packets over the cluster's cells
 3: if even 25 m/s is short: n loops of radius 63.7 m tangent at the CH, at 25 m/s
 4: speed profile with 45° bank, ±2 m/s²; the ns-3 pass follows the profile (column t)

Algorithm RIVER  (short form; full: paper/L3-TECHREPORT-vi.md, Appendix A)
 before:  Axe and Seg(a) from γ; Banks at ±ω (ω = 1.75 cells) on the normal; critical cells;
          Need(k) ← the Q Axe packets around where γ passes closest to k; Circle(k) splits Need(k) into groups
 after:   GATHER → BANKFILL (Axe → Bank) → CIRCLEFILL (Bank → Circle) → CRITPULL (Circle → k)
 repair:  an Axe cell takes missing packets of its Seg from a neighbour that heard them; a critical cell silent
          for 20 s while still lacking asks again along Circle → Bank → Axe

Algorithm REPORT(k)                                       ▷ fountain-coded clue set, two reports
 1: t1 ← own decode of the coded stream heard along the whole flight + in-cell gather
 2: t2 ← leave_k + River done(k)
 3: at min(t1, t2): report S_k and the bitmap of what k holds; at max(t1, t2): report again with the union
 4: each report → CH → next LoRa slot of the CH (every 40 s)

Algorithm TEAM2  (BS, from t = 0)                         ▷ -zero -stage -puq -redir
 1: take off at t = 0
 2: loop until every critical cell is verified:
 3:     P(c) ← P(c is c*) for reported cells;  P_U ← P(c* has not reported yet)
 4:     c ← argmax over reported unvisited cells of P(c) / (flight time + 78 s)
 5:     if P(c) ≥ P_U / 4: fly to c and verify it (on a new report in flight: decide again from here)
 6:     else: fly towards the P-weighted centre of the unvisited cells and wait for the next report
 7: T* ← time c* is verified
```

---

## 3. Baseline và ablation

### 3.1 Danh sách

| Tên | Thay gì so với CHORD | Cô lập điều gì | Mức |
|---|---|---|---|
| **FC** | Đội 1 bay TSP qua chính các critical cell, lượn ở 25 m/s (bán kính 64 m) tới khi đủ gói mã; không River, chỉ gom trong cell | đường bay qua landmark thay cho River | mô hình thu + gom (mục 166) |
| **DN** | Như FC, nhưng gom critical cell gần nhau thành nhóm, bay quỹ đạo tròn quanh nhóm theo DTSP-N | DTSP-N thay cho River | như FC (mục 168) |
| **Pd** | Kéo trực tiếp thay River: mỗi critical cell hỏi thẳng từng cell Axe | tổ chức River (Bank, Circle) | ns-3 |
| **B4** | Không hợp tác mặt đất: chỉ báo phần cell tự giải mã được | giá trị của hợp tác | ns-3 lượt bay + mô hình thu |
| **B1** | Không pha 1: đội 2 thăm mọi critical cell theo TSP với tệp lớn | giá trị của cả pha 1 | mô hình |
| **B7** | Đội 2 biết trước c\*, bay thẳng từ t = 0 | cận dưới | mô hình |
| CHORD-0 | CHORD không mã fountain | phần đóng góp của mã | ns-3 |
| Trickle (Pt) | Phổ biến kiểu Deluge theo cell (RFC 6206: Imin 1 s, Imax 64 s, k = 1, trang 64 gói) | so với giao thức phổ biến chuẩn | ns-3 (mục 139) |
| B2-r, B3-r, B6 | Cánh quay: multicast tệp lớn theo nhóm (B2); lơ lửng multicast bộ manh mối theo nhóm (B3); unicast từng cell (B6) | cánh bằng + River so với cánh quay | mô hình |
| B5 | Cánh bằng quét luống phủ cả miền, phát lặp bộ manh mối | quét luống so với dây cung | mô hình |
| B8-r | Cánh bằng bay vòng quanh nhóm của B3 | bay vòng so với dây cung | mô hình |
| k-medoids | Đường dài nhất qua CH, chọn riêng từng cụm | phần lợi của CHORD-T | ns-3 |
| subCH-K, MEANDER-K, SWATH-K | Cách chia cụm khác (lớp 2), cùng số cụm K | tái cấu trúc cụm | ns-3 |

Bảng chính (§5) gồm CHORD, FC, DN, Pd, B4, B1, B7 (mục 181–182). Các phương án còn lại chạy ở các vòng trước, với phiên bản pipeline cũ hơn (§4).

### 3.2 Mã giả các baseline của bảng chính

```text
Algorithm FC  (fc_baseline.py)
 1: code each of the 12 files with an ideal fountain code (decodes at 1.05·K_j coded packets, any);
    interleave the files' packets by size, one every 10 ms, never repeated
 2: order ← TSP of the critical cells from the BS (nearest neighbour + 2-opt)
 3: E[c][j] ← expected coded packets of file j held by cell c (union of its nodes, channel model)
 4: target_j ← 1.05·K_j + 3·sqrt(1.05·K_j)
 5: for c in order, skipping cells already served:
 6:     Dubins (ρ = 255 m) to c's centre, heading for the next
 7:     while some E[c][j] < target_j: circle at 25 m/s, radius 64 m (through or about c's centre;
        the BS plans both and flies the shorter tour)
 8: back to the BS; speed profile over the whole flight
 9: realised reception (one draw per map and channel); report at decode + in-cell gather
        (0.07 + 0.00789 × packets moved s); then LoRa and TEAM2

Algorithm DN  (dn_baseline.py)
 1: for r_g ∈ {200, 300, 400} m:
 2:     groups ← bottom-up merge of the closest centroids while every member is within r_g of the centroid
 3:     each group: orbit about its centroid, radius = farthest member clipped to [64, 255] m, speed sqrt(g·r)
 4:     laps(g) ← laps that bring every member to target in expectation
 5:     sequence ← Euclidean TSP of the centroids; DP over 12 entry angles × 2 directions per group,
        Dubins links (DTSP-N, sequence first)
 6: fly the shortest of the three tours; leave an orbit as soon as every member is served (counting
    what it heard on the way); skip groups already served; report, LoRa and TEAM2 as FC

Algorithm Pd  (coop2-river --scheme direct)
 1: same flight, coding and REPORT as CHORD
 2: after the pass, each critical cell k asks every Axe cell a for Need(k) ∩ Seg(a) \ have(k),
    along the precomputed cell path a → k; no Banks, no Circle; no repair

Algorithm B4
 1: same flight and coded reception as CHORD
 2: each critical cell reports once: its own decode + in-cell gather; no River, no pull

Algorithm B1
 1: team 2 leaves at t = 0 with the full reference set; TSP over every critical cell
 2: at each cell: hover, send 1 MB by unicast, match (≈ 78 s); T* when c* is verified

Algorithm B7
 1: team 2 flies straight to c* at t = 0 and verifies it; T* = flight + 78 s
```

---

## 4. Các thực nghiệm theo thời gian

Mỗi thực nghiệm ghi: câu hỏi, thiết lập, kết quả chính, nơi lưu. Các phiên bản pipeline thay đổi qua thời gian (bảng cuối mục này), nên số của các thực nghiệm khác nhau không so thẳng với nhau.

### E1. Kênh A2G và G2G (05–06/10, `uav-sar/`)
- **A2G-RUN:** 7 node cách 300 m, UAV 100 m, 50 m/s, 200 lượt, α = 3:

| lệch ngang | 0 m | 300 m | 600 m | 900 m |
|---|---|---|---|---|
| gói nhận (trên 8 001) | 4 002 | 3 789 | 3 077 | 1 828 |
| chuỗi liền dài nhất | 850 ± 226 | 245 ± 85 | 50 ± 11 | 14 ± 2 |

- **G2G-CHAIN:** chuyển một file qua chuỗi node; thời gian do chặng yếu nhất quyết định (giãn theo 1/p), chặng yếu do che khuất tĩnh.
- **Ý nghĩa:** node xa đường bay nghe nhiều gói nhưng rời rạc, không ghép được file: cần hợp tác mặt đất.

### E2. River so với kéo trực tiếp trên một cụm (12–13/10, `uav-coop2/docs/data/camp54/`)
Cụm 91 cell, đường thẳng, kênh open, 20 lượt ghép cặp:

| số critical cell | TB critical cell xong | critical cell cuối | khung |
|---|---|---|---|
| 1 | −0,3 s | −0,3 s | River tốn hơn 0,8 k |
| 4 | −2,5 s (19/20) | −2,7 s (16/20) | −20 % (20/20) |
| 7 | −4,0 s (20/20) | −5,2 s (19/20) | −21 % (20/20) |
| 16 | −10,6 s (20/20) | −19,7 s (20/20) | −22 % (20/20) |

Cụm C3 (80 cell, 4 critical cell): River 37,2 s, 89,7 k khung; kéo trực tiếp 50,3 s, 102,2 k khung. Lưới 7 màu là đủ (3 màu chậm hơn, 13 màu không nhanh hơn); bề rộng River 2,5–6,5 cell gần như không đổi kết quả.

### E3. Ngưỡng bão hoà theo hình dạng cụm (21/10, `uav-l2/docs/SAT-vi.md`)
75 dải: rộng 3–10 cell × dài 1,5–6 km × 3 seed.
- Cửa sổ quanh CH bão hoà ở khoảng 2 km chiều dài (dải 6 × 4 km: 88,4 s và 412 k khung).
- Cửa sổ theo từng critical cell gỡ giới hạn chiều dài (cùng dải: 24,8 s, 41,4 k khung). Đây là lý do P\* dùng `--windowAt crit`.
- Giới hạn còn lại là bề ngang: phẳng tới khoảng 600 m từ đường bay, rồi tăng dần.

### E4. Chốt lớp 2: các biến thể trên 16 bản đồ (22–23/10, `uav-l2/docs/PROPOSE-ITER-vi.md`)
16 bản đồ (4 mỗi cỡ k2–k8), ghép cặp, chênh so với k-medoids (đường dài nhất):

| phương án | ΔT\* (số bản đồ tốt hơn) | Δ tour đội 1 | critical cell đủ 12 manh mối |
|---|---|---|---|
| SWATH-K | +6 s (8/16) | +22 s | – |
| CHORD-T CLUE 90 % | −14 s (13/16) | −20 s | 100 % |
| **CHORD-T CLUE 80 %** | **−29 s (16/16)** | −64 s | 84 % |
| CHORD-T CLUE 70 % | −38 s (16/16) | −83 s | 63 % |

Người dùng chốt CLUE 80 % (mục 138). Lợi của hợp tác (B4 − P\*): k-medoids +19 s, CHORD-T +50 s.

**Bảng baseline nhanh trên cùng 16 bản đồ** (23/10, kênh open, pass 50 m/s, chưa mã fountain):

| phương án | T\* TB (s) | so với P\* | khung mặt đất / bản đồ |
|---|---|---|---|
| P\* (CHORD-T) | 585 | – | 252 k |
| kéo trực tiếp / Trickle | 586 / 586 | +0 / +1 | 284 k / 1 182 k |
| không hợp tác (B4) | 635 | +50 (15/16) | – |
| k-medoids / SWATH-K / MEANDER-K / subCH-K | 614 / 621 / 650 / 600 | +29 / +35 / +64 / +15 | 147 / 185 / 92 / 224 k |
| B5 / B8-500 / B3-500 / B1 | 697 / 953 / 1 478 / 1 859 | +112 / +368 / +892 / +1 274 | – |
| B7 | 299 | −286 | – |

Lớp 3 trên các thư mục này (lúc critical cell đủ cửa sổ, tính từ khi UAV rời cụm): River TB 12,6 s, p90 24,9 s, 252 k khung; kéo trực tiếp 14,4 / 32,3 s, 284 k; Trickle 22,3 / 44,8 s, 1 182 k.

### E5. MEANDER so với CHORD-T (23–24/10, `logs/2026-10-23_1920-factor-sweep/`, `logs/2026-10-24_0714-ns3-given-ch/`)
- Quét từng yếu tố (60 cặp bản đồ, hình học + động học): MEANDER kiểu luống có tour ngắn hơn trên dải hẹp dài (52/54 cặp). Người dùng loại dạng miền này vì mất tính tổng quát (mục 151).
- ns-3 trên bản đồ k8 seed 1–3, cùng CH có sẵn: CHORD-T uốn nhẹ thắng T\* cả 3 bản đồ (662 / 632 / 692 s so với 721–833 s). MEANDER rời cụm muộn hơn và River chậm gấp 2–4 lần vì Axe chỉ mang đúng một bản sao.

### E6. CHORD vừa đủ, uốn, thứ tự theo River (24/10, mục 159, `logs/2026-10-24_1857-chord-fit/`)
k8 seed 1–3: T\* gộp 300 lượt bốc A (CHORD-T) 758, B (vừa đủ + uốn) 761, D (B + ưu tiên River) 761 s. Không khác nhau: dây cung qua CH vốn đã ngắn hơn 2,02 km, River chỉ 6–9 s, T\* do tour và pha 2 quyết định.

### E7. P\* ở bốn chế độ kênh (25/10, mục 163, `logs/2026-10-25_0330-env-modes/`)
k8-s1, pass theo hồ sơ vận tốc, chưa mã fountain:

| chế độ | River xong TB / p90 / max (s) | T\* P\* (s) | T\* kéo trực tiếp (s) | T\* không hợp tác (s) |
|---|---|---|---|---|
| open | 8 / 18 / 35 | 762 | 762 | 781 |
| r500 | 54 / 103 / 160 | 808 | 806 | 1 408 |
| r200 | 99 / 208 / 216 | 860 | 858 | 3 122 |
| r100 | 121 / 233 / 270 | 878 | 872 | 3 402 |

Hợp tác mặt đất chuyển từ "có cũng được" (open, +19 s) sang bắt buộc (r200, r100: không hợp tác chậm hơn 2 262–2 524 s).

### E8. Bảng chính: bảy phương án (25–26/10, mục 166–169, 182) → §5

### E9. LM-Tour (25–26/10, mục 170–180) → `paper/LMTOUR-vi.md`

**Phiên bản pipeline:**

| thời điểm | thay đổi | ảnh hưởng tới |
|---|---|---|
| 22/10 | cửa sổ theo critical cell, `--critRing domain`, `--axeNear`; ghép cặp theo tên bản đồ | từ E4 |
| 24/10 (mục 157) | pass ns-3 bay theo hồ sơ vận tốc (giảm tốc, lượn) | từ E6 |
| 25/10 (mục 161) | seed ns-3 theo bản đồ và cụm (`--mapRuns`), binary đóng băng | từ E7 |
| 25/10 (mục 163) | bốn chế độ kênh, cổng gói sát mép theo kênh | từ E7 |
| 25/10 (mục 169) | mã fountain cho CHORD (`-fcd`), River `--repair 20` | E8 |

---

## 5. Kết quả chính (E8)

3 bản đồ × 4 kênh × 100 lượt bốc lớp 1. Nguồn: `uav-l2/docs/data/results/baselines.{md,csv}`, `chord-fc.csv`; log `logs/2026-10-25_0600-fc-baseline/`, `logs/2026-10-25_0800-chord-win/`, `logs/2026-10-26_0900-baselines/`.

### 5.1 T\* trung bình ± 95 % (s)

| kênh | bản đồ | CHORD | FC | DN | Pd | B4 | B1 | B7 |
|---|---|---|---|---|---|---|---|---|
| open | k8-s1 | **647 ± 100** | 660 ± 103 | 708 ± 101 | 647 ± 100 | 650 ± 100 | 2926 ± 313 | 322 ± 17 |
| open | k12-s1 | **686 ± 69** | 815 ± 82 | 805 ± 81 | 686 ± 69 | 687 ± 70 | 4168 ± 465 | 402 ± 20 |
| open | k16-s1 | 863 ± 96 | 949 ± 105 | 967 ± 95 | 863 ± 96 | 862 ± 95 | 5169 ± 593 | 404 ± 21 |
| r500 | k8-s1 | **784 ± 96** | 1138 ± 127 | 1078 ± 121 | 806 ± 97 | 1379 ± 207 | 2926 ± 313 | 322 ± 17 |
| r500 | k12-s1 | **950 ± 75** | 1451 ± 144 | 1388 ± 126 | 950 ± 75 | 2030 ± 259 | 4168 ± 465 | 402 ± 20 |
| r500 | k16-s1 | **1107 ± 108** | 1801 ± 174 | 1750 ± 176 | 1115 ± 108 | 2549 ± 378 | 5169 ± 593 | 404 ± 21 |
| r200 | k8-s1 | 876 ± 97 | 2285 ± 214 | 1904 ± 162 | **850 ± 98** | 3711 ± 303 | 2926 ± 313 | 322 ± 17 |
| r200 | k12-s1 | **975 ± 76** | 3288 ± 279 | 2482 ± 230 | 990 ± 76 | 5277 ± 420 | 4168 ± 465 | 402 ± 20 |
| r200 | k16-s1 | 1192 ± 111 | 3964 ± 376 | 3469 ± 330 | 1192 ± 113 | 6298 ± 617 | 5169 ± 593 | 404 ± 21 |
| r100 | k8-s1 | **872 ± 98** | 2463 ± 229 | 2190 ± 217 | 875 ± 98 | 3860 ± 316 | 2926 ± 313 | 322 ± 17 |
| r100 | k12-s1 | 990 ± 76 | 3460 ± 288 | 3248 ± 294 | 990 ± 76 | 5308 ± 412 | 4168 ± 465 | 402 ± 20 |
| r100 | k16-s1 | **1215 ± 111** | 4368 ± 415 | 4468 ± 355 | 1334 ± 162 | 6358 ± 598 | 5169 ± 593 | 404 ± 21 |

In đậm: phương án làm được nhanh nhất (không tính oracle B7); ô không in đậm là hoà trong nhiễu. B1, B7 không dùng kênh của đội 1.

### 5.2 Chênh ghép cặp so với CHORD (phương án − CHORD, s; ngoặc: % lượt bốc CHORD nhanh hơn)

| kênh | bản đồ | FC | DN | Pd | B4 | B1 |
|---|---|---|---|---|---|---|
| open | k8-s1 | +13 ± 34 (66 %) | +61 ± 40 (60 %) | 0 ± 0 (2 %) | +3 ± 6 (18 %) | +2278 ± 313 (91 %) |
| open | k12-s1 | +130 ± 49 (77 %) | +120 ± 52 (80 %) | 0 ± 0 (0 %) | +2 ± 3 (3 %) | +3482 ± 468 (97 %) |
| open | k16-s1 | +86 ± 38 (74 %) | +104 ± 73 (60 %) | 0 ± 0 (0 %) | −1 ± 2 (0 %) | +4306 ± 570 (93 %) |
| r500 | k8-s1 | +354 ± 74 (81 %) | +294 ± 73 (81 %) | +21 ± 19 (54 %) | +595 ± 197 (74 %) | +2141 ± 309 (89 %) |
| r500 | k12-s1 | +501 ± 113 (75 %) | +438 ± 98 (77 %) | 0 ± 8 (39 %) | +1080 ± 253 (81 %) | +3218 ± 468 (95 %) |
| r500 | k16-s1 | +694 ± 105 (90 %) | +643 ± 159 (71 %) | +8 ± 8 (42 %) | +1442 ± 368 (80 %) | +4062 ± 565 (92 %) |
| r200 | k8-s1 | +1409 ± 168 (93 %) | +1028 ± 131 (93 %) | −26 ± 25 (36 %) | +2835 ± 297 (97 %) | +2050 ± 308 (88 %) |
| r200 | k12-s1 | +2313 ± 252 (99 %) | +1507 ± 197 (91 %) | +15 ± 16 (60 %) | +4302 ± 426 (100 %) | +3193 ± 466 (96 %) |
| r200 | k16-s1 | +2772 ± 302 (97 %) | +2277 ± 315 (94 %) | 0 ± 13 (41 %) | +5106 ± 620 (96 %) | +3977 ± 559 (92 %) |
| r100 | k8-s1 | +1590 ± 184 (93 %) | +1318 ± 175 (87 %) | +3 ± 21 (39 %) | +2987 ± 307 (98 %) | +2053 ± 308 (88 %) |
| r100 | k12-s1 | +2471 ± 262 (99 %) | +2259 ± 286 (86 %) | 0 ± 12 (49 %) | +4318 ± 422 (100 %) | +3178 ± 467 (96 %) |
| r100 | k16-s1 | +3153 ± 340 (97 %) | +3253 ± 358 (95 %) | +119 ± 97 (38 %) | +5142 ± 597 (98 %) | +3954 ± 559 (92 %) |

B7 − CHORD: −283 … −810 s (cận dưới, 0 % lượt bốc CHORD nhanh hơn).

### 5.3 Đội 1 và thời điểm sẵn sàng

| kênh | bản đồ | đội 1 bay CHORD / FC / DN (s) | sẵn sàng TB / max CHORD (s) | FC | DN | FC: ghé / vòng lượn | DN: ghé / vòng lượn (nhóm, bán kính) |
|---|---|---|---|---|---|---|---|
| open | k8 | 782 / 683 / 669 | 238 / 655 | 255 / 590 | 271 / 594 | 15 / 6,3 | 16 / 5,3 (27, 300 m) |
| open | k12 | 1152 / 971 / 913 | 262 / 671 | 431 / 918 | 409 / 831 | 22 / 4,8 | 20 / 9,1 (36, 400 m) |
| open | k16 | 1415 / 1190 / 1134 | 419 / 1052 | 514 / 1132 | 536 / 1041 | 29 / 7,5 | 29 / 7,8 (80, 200 m) |
| r500 | k8 | 782 / 1499 / 1320 | 364 / 719 | 695 / 1452 | 617 / 1289 | 34 / 28,1 | 22 / 24,6 (22, 400 m) |
| r500 | k12 | 1152 / 2228 / 2011 | 523 / 1008 | 1013 / 2167 | 967 / 1979 | 49 / 34,3 | 38 / 35,0 (41, 300 m) |
| r500 | k16 | 1415 / 2839 / 2563 | 642 / 1204 | 1320 / 2784 | 1238 / 2529 | 69 / 45,1 | 42 / 46,2 (44, 400 m) |
| r200 | k8 | 782 / 3357 / 2687 | 437 / 769 | 1717 / 3310 | 1370 / 2659 | 45 / 98,6 | 27 / 74,6 (27, 300 m) |
| r200 | k12 | 1152 / 4976 / 4016 | 566 / 1054 | 2505 / 4916 | 1964 / 3968 | 64 / 150,3 | 41 / 112,3 (41, 300 m) |
| r200 | k16 | 1415 / 6631 / 5567 | 720 / 1398 | 3264 / 6591 | 2746 / 5523 | 90 / 197,8 | 44 / 144,9 (44, 400 m) |
| r100 | k8 | 782 / 3621 / 3305 | 454 / 895 | 1867 / 3589 | 1678 / 3269 | 45 / 123,3 | 37 / 114,2 (37, 200 m) |
| r100 | k12 | 1152 / 5285 / 5078 | 585 / 1064 | 2663 / 5231 | 2559 / 5034 | 65 / 178,4 | 58 / 168,2 (58, 200 m) |
| r100 | k16 | 1415 / 7296 / 6808 | 735 / 1395 | 3619 / 7257 | 3424 / 6761 | 92 / 244,8 | 80 / 233,6 (80, 200 m) |

Đội 1 của CHORD, Pd và B4 bay cùng một đường ở mọi kênh. Mọi critical cell đủ 12 manh mối ở cả CHORD, FC, DN.

**Số critical cell tự giải đủ 12 manh mối từ lượt bay của CHORD** (không River): open 45/45, 66/66, 92/92; r500 29/45, 42/66, 61/92; r200 0/45, 0/66, 1/92; r100 0/45, 0/66, 0/92.

### 5.4 River so với kéo trực tiếp ở mức cell (ns-3)
*xong*: giây từ lúc đội 1 rời cụm tới lúc CL giữ đủ cửa sổ. *lượt truyền*: tổng số lượt chuyển gói một chặng.

| kênh | bản đồ | cell | xong TB River / kéo (s) | xong max (s) | kẹt | cell kéo nhanh hơn | lượt truyền (nghìn) | MAC lỗi (nghìn) |
|---|---|---|---|---|---|---|---|---|
| open | k8 | 45 | 8 / 8 | 35 / 30 | 0 / 0 | 22/45 | 146 / 138 | 5 / 5 |
| open | k12 | 66 | 8 / 8 | 50 / 47 | 0 / 0 | 35/66 | 247 / 254 | 8 / 9 |
| open | k16 | 92 | 10 / 10 | 69 / 47 | 0 / 0 | 48/92 | 517 / 530 | 19 / 19 |
| r500 | k8 | 45 | 54 / 71 | 159 / 206 | 0 / 0 | 10/45 | 1612 / 1621 | 61 / 61 |
| r500 | k12 | 66 | 45 / 57 | 90 / 106 | 0 / 0 | 19/66 | 2112 / 2084 | 79 / 77 |
| r500 | k16 | 92 | 62 / 67 | 244 / 134 | 0 / 0 | 26/92 | 3721 / 3492 | 147 / 133 |
| r200 | k8 | 45 | 108 / 95 | 311 / 235 | 0 / 0 | 30/45 | 3107 / 2481 | 135 / 93 |
| r200 | k12 | 66 | 78 / 83 | 136 / 164 | 0 / 0 | 25/66 | 3897 / 3315 | 165 / 123 |
| r200 | k16 | 92 | 99 / 90 | 259 / 170 | 0 / 0 | 57/92 | 6169 / 5185 | 264 / 196 |
| r100 | k8 | 45 | 126 / 113 | 300 / 283 | 0 / 0 | 35/45 | 3542 / 2825 | 168 / 109 |
| r100 | k12 | 66 | 96 / 95 | 183 / 184 | 0 / 0 | 34/66 | 4736 / 3795 | 222 / 145 |
| r100 | k16 | 92 | 115 / 105 | 225 / 197 | 0 / 6 | 56/86 | 7114 / 5801 | 334 / 227 |

### 5.5 Đóng góp của mã fountain và của sửa River (mục 169)
T\* trung bình (s), theo `RESULTS-vi.md` §2.2:

| | k8 open | k12 open | k16 open | k8 r500 | k16 r500 | k16 r100 |
|---|---|---|---|---|---|---|
| CHORD trước mục 169 | 762 | 939 | 1 161 | 808 | 1 137 | 1 412 |
| + River sửa (CHORD-0) | 762 | 939 | 1 115 | 808 | 1 137 | 1 214 |
| + mã fountain (CHORD) | 647 | 686 | 863 | 784 | 1 107 | 1 215 |

- Sửa River chỉ có tác dụng ở các ô có cell kẹt (k16 open, k16 r100). Hai lỗ hổng: gói thuộc Seg của một cell Axe mà chỉ cell bên cạnh nghe được; và ACK nhầm do số thứ tự 8 bit của 802.15.4.
- Mã fountain có tác dụng lớn ở open, nhỏ ở r500, gần 0 ở r200 và r100, nơi một cell gần như không tự giải đủ được.

### 5.6 Đọc kết quả
1. **CHORD nhanh nhất trong các phương án làm được** ở 12/12 tổ hợp (hoà với Pd). So với baseline tốt hơn trong FC, DN: nhanh hơn 2 / 15 / 9 % ở open, 27 / 32 / 37 % ở r500, 54 / 61 / 66 % ở r200, 60 / 70 / 72 % ở r100 (k8 / k12 / k16). Ngoại lệ gần hoà: k8 open (−13 ± 34 s).
2. **Khoảng cách tăng khi môi trường khó lên và mạng lớn lên.** Đường bay của CHORD không đổi theo kênh (782 / 1 152 / 1 415 s), vì phần thiếu do mặt đất bù. FC và DN phải lượn nhiều hơn: đội 1 bay gấp 2–6 lần chính nó ở open.
3. **Hợp tác mặt đất là bắt buộc từ r500.** B4 chậm hơn CHORD 1,8–5,4 lần, và ở r200, r100 chậm hơn cả B1 (không có pha 1).
4. **Tổ chức River không làm T\* nhanh hơn kéo trực tiếp.** Pd hoà CHORD ở open; ở 9 ô còn lại, chênh nằm trong nhiễu ở 5 ô, chênh 1–3 % ở 3 ô (CHORD nhanh hơn ở r500 k8 và r500 k16, Pd nhanh hơn ở r200 k8); Pd chậm hơn rõ ở k16 r100 (+119 ± 97 s) vì 6 cell kéo trực tiếp bị kẹt (chưa có cơ chế sửa như River). Ở mức cell, River xong sớm hơn ở r500; kéo trực tiếp xong sớm hơn hoặc ngang ở r200, r100 và tốn ít lượt truyền hơn 15–20 %. River không kẹt cell nào ở cả 12 tổ hợp.
5. **B1 chậm hơn CHORD 3,3–6 lần**, nhưng thắng ở 3–12 % số lượt bốc, khi c\* nằm sớm trong tour TSP của B1.
6. **Còn cách cận dưới B7 283–810 s:** phần lớn nằm ở pha 2 (đội 2 xác minh các cell sai trước c\*, mỗi lần khoảng 78 s cộng thời gian bay) và độ trễ báo cáo qua LoRa.

### 5.7 Điều được nói và không được nói
**Được nói** (kèm nhãn số thăm dò):
- Một lượt bay qua CH cộng hợp tác mặt đất nhanh hơn rõ các baseline phục vụ trực tiếp bằng UAV (FC, DN, B1), và khoảng cách tăng khi bán kính A2G nhỏ đi và mạng lớn lên.
- Hợp tác mặt đất là điều kiện cần khi R50 ≤ 500 m.
- River không kẹt critical cell nào; kéo trực tiếp kẹt 6/92 ở k16 r100.
- Trên một cụm, kênh open, River ít khung hơn kéo trực tiếp 20–22 % từ 4 critical cell trở lên (E2).

**Không được nói:**
- "River làm nhiệm vụ nhanh hơn kéo trực tiếp." T\* hoà.
- "River luôn tốn ít khung hơn kéo trực tiếp." Ở r200, r100 trên bảng chính thì ngược lại. Câu −12 % / −26 % trong abstract của draft chỉ đúng cho cụm C3 ở kênh open (E2).
- "FC + gom để lại X % critical cell chưa xong" (TODO trong draft): với lượn tới khi đủ, FC và DN giao đủ 100 % critical cell; cái giá là tour dài hơn.
- Bất kỳ số nào như số công bố trước khi chạy đủ N.

---

## 6. Giới hạn và việc còn mở
- **Một bản đồ mỗi cỡ.** Chiến dịch 3 cỡ × 4 kênh × 10 bản đồ (mục 165) chưa chạy.
- **FC, DN, B4 dùng mô hình thu giải tích** cho gói mã (cùng mô hình nghe với pass ns-3); gom trong cell bằng công thức khớp trên ns-3 (R² 0,83), không tính tranh kênh khi UAV còn phát gần đó. FC hơi lạc quan.
- **Mã fountain lý tưởng:** phần dư 5 %, không tính chi phí giải mã.
- **Kéo trực tiếp chưa có `--repair`.** So sánh ở k16 r100 nghiêng về River.
- **Fading A2G không đổi trong một gói** (thời gian kết hợp ≈ 1 ms < 4,256 ms chiếm sóng): kết quả A2G lạc quan.
- **Các baseline cánh quay và B5, B8** dùng PER Nakagami m = 1,8 thay vì Rician K = 2, chưa theo chế độ kênh.
- **Tham số lớp 1** (d, độ giống người lạ, tỉ lệ mặc giống) là giả định kịch bản; d quyết định mức T\* nhiều nhất.

---

## 7. Tái lập
Lệnh đầy đủ và khoá seed: `uav-l2/docs/RESULTS-vi.md` §3–4 và §6.4. Tóm tắt (từ gốc repo, BIN = `scratchpad/CAMP-BIN4`):

```text
# 1. nhiệm vụ CHORD + River (và kéo trực tiếp: --schemes rf,d) trên một bản đồ, một kênh
python3 uav-l2/tools/mission.py --clusters K --seed 1 --bin BIN --windowKB 400 --windowAt crit --critRing domain \
  --axeNear --chordTour 0.6,0.8 --kinPass --mapRuns --env ENV --riverRepair 20 --schemes rf,d --jobs 2 --work WORK
# 2. chấm mọi phương án (FC, DN chạy bên trong)
python3 uav-l2/tools/l1_rank.py --set ENV WORK[,...] [--set ...] --draws 100 --jobs 4 \
  --methods P+prog-kin-puq-stage-zero-redir-kt-fcd,FC-puq-stage-zero-redir,DN-puq-stage-zero-redir,\
Pd+prog-kin-puq-stage-zero-redir-kt-fcd,B4-kin-puq-stage-zero-redir-kt-fcd,B1,B7 --out L1
# 3. bảng
python3 uav-l2/tools/cmp_table.py OUT L1-draws.csv
```

Dữ liệu 12 thư mục nhiệm vụ: `uav-l2/docs/data/results/raw/<kênh>-<bản đồ>.tar.xz` (20 MB). Giải nén rồi chạy lại lệnh 1: chỉ bitmap pass được dựng lại, giống hệt từng byte.
