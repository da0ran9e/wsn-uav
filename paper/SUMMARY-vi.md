# Tổng hợp nghiên cứu: giao truy vấn tìm kiếm bằng một lượt bay UAV cánh bằng và hợp tác mặt đất có lập kế hoạch

- **Phiên bản:** 2026-10-26, sau mục 183 của CLAUDE.md §8. Bản này thay `paper/OVERVIEW-vi.md` (21/10) làm bản tổng hợp hiện hành; OVERVIEW vẫn giữ để tra phần lớp 1 và lịch sử trước 21/10.
- **Lời gốc của mọi yêu cầu:** CLAUDE.md §8, mục 1–183. Khi có mâu thuẫn, lời người dùng ở đó và lời mới hơn thắng.
- **Ba tài liệu cho paper:**
  1. `paper/SUMMARY-vi.md` (tài liệu này): toàn bộ những gì đã làm, đã chốt, và điều được hay không được nói.
  2. `paper/EXPERIMENTS-vi.md`: mô tả, mã giả, chi tiết thực nghiệm và baseline, bảng kết quả.
  3. `paper/LMTOUR-vi.md`: LM-Tour (mục V của draft): ý tưởng, thuật toán, kết quả và phân tích.
- **Bản draft đang dùng:** `SigDrop_ICC_draft_v3.pdf` (mục 170), "Flight Geometry Is the Schedule".

> Mọi số ở đây là **số thăm dò**: bảng chính có một bản đồ cho mỗi cỡ mạng. Quy tắc dự án: N ≥ 120 mới được công bố (CLAUDE.md §6).

---

## 1. Tóm tắt một trang

**Bài toán.** Một người cần tìm có thể đã đi qua trước nhiều camera của nhiều chủ sở hữu khác nhau. Không tải được video về (không có băng rộng ở vùng xa, ràng buộc pháp lý ở đô thị). Ta đưa một **truy vấn** (12 ảnh tham chiếu, 400 kB) xuống các camera có khả năng đối sánh (**critical cell**). Chúng đối sánh tại chỗ và chỉ báo vài byte về qua LoRa.

**Kiến trúc.**
- **Pha 1:** một UAV cánh bằng bay qua mỗi cluster **một lần**, phát truy vấn trên IEEE 802.15.4.
- **Mạng mặt đất** chuyển phần còn thiếu tới critical cell.
- **Pha 2:** một UAV cánh quay đi xác minh các cell theo xác suất BS tính từ báo cáo.
- Chỉ số: **T\***, lúc xác minh xong cell thật sự có điểm cao nhất (c\*).

**Nhận xét then chốt.** Gói s được phát tại γ(d₀ + sΔ) trên đường bay γ do BS thiết kế. Vậy **hình học đường bay chính là lịch phát**: trước khi cất cánh, BS biết đoạn dữ liệu nào rơi xuống cell nào, nên lập kế hoạch được cả đường bay lẫn hợp tác mặt đất.

**Phương án đề xuất (P\*, gọi là CHORD).**
- **Lớp 2, đường bay:** mỗi cụm một đường thẳng qua CH; hướng và thứ tự cụm chọn chung để giảm độ trễ (CHORD-T); giảm tốc hoặc lượn để mỗi cụm nhận đủ một bản truy vấn.
- **Lớp 3, River:** kế hoạch tính trước Axe → Bank → Circle → critical cell, mỗi critical cell lấy bản sao truy vấn gần nó nhất; có cơ chế sửa gói thiếu.
- **Mã fountain dạng hệ thống:** cell tự giải mã được thì báo sớm, River mang phần còn lại.
- **Pha 2:** đội 2 cất cánh lúc 0, đón đầu, ngưỡng β = 1/4, đổi hướng giữa đường.

**Kết quả chính** (3 bản đồ 8/12/16 cụm × 4 môi trường × 100 lượt bốc, ns-3 với MAC 802.15.4 đầy đủ):
- CHORD nhanh nhất trong các phương án làm được ở 12/12 tổ hợp, chỉ hoà với biến thể kéo trực tiếp Pd.
- So với baseline UAV-phục-vụ-trực-tiếp tốt hơn (FC hoặc DN): nhanh hơn 2–15 % ở môi trường mở, 27–37 % ở R50 ≈ 500 m, 54–72 % ở R50 ≤ 200 m. Khoảng cách tăng theo cỡ mạng.
- Không có hợp tác mặt đất (B4): chậm hơn 1,8–5,4 lần từ R50 ≈ 500 m trở xuống.
- Không có pha 1 (B1): chậm hơn 3,3–6 lần.

**Hai phát hiện phải ghi đúng trong bài.**
- **River so với kéo trực tiếp:** cho cùng T\*. River không kẹt cell nào; kéo trực tiếp kẹt 6/92 ở môi trường khó nhất. Ở R50 ≤ 200 m, kéo trực tiếp tốn ít lượt truyền hơn 15–20 %. Lợi thế "−26 % thời gian, −12 % khung" của draft chỉ đúng trên một cụm ở kênh mở.
- **LM-Tour** (mục V của draft) không hơn CHORD trên cluster có sẵn. Bộ dự đoán thời gian River đi kèm thì dùng được (MAE 22,8 s).

---

## 2. Bối cảnh và động cơ

Lời gốc: mục 38–39. Chi tiết: `paper/INTRO-vi.md`, `paper/RELATED-vi.md`.

- **Camera nhiều, đa dạng, không biết cần tìm gì.** Camera an ninh, chuông cửa, máy bán hàng, camera hành trình; năng lực và chủ sở hữu khác nhau; dữ liệu mới ghi đè dữ liệu cũ.
- **Không tải dữ liệu về được.** Vùng hoang dã chỉ có LoRa hoặc vệ tinh (vài trăm byte mỗi giờ). Đô thị vướng pháp lý.
- **Vì sao gửi ảnh chứ không gửi vector:** các camera chạy mô hình khác nhau, vector của chúng không so được với nhau. Mỗi camera tự nhúng ảnh tham chiếu bằng mô hình của mình.
- **Vì sao UAV cánh bằng:** nhanh (50 m/s), tầm xa, nhưng không lơ lửng và quay rộng (255 m), nên mỗi cụm chỉ được bay qua một lần.
- **Khoảng trống:** multicast UAV đòi mọi node nhận trọn từ UAV; giao thức phổ biến (Deluge, Trickle) khám phá dữ liệu lúc chạy và nhắm mọi node; mã fountain nới lỏng *gói nào* cần chứ không nói *gói ở đâu*.

---

## 3. Kiến trúc nhiệm vụ

| Pha | Ai | Làm gì |
|---|---|---|
| 0. Chuẩn bị | BS, trước giờ bay | Cluster, CH, CL, critical cell; đường bay và tour đội 1; bảng Axe, Bank, cửa sổ, Circle; gửi kế hoạch cho CH |
| 1. Giao truy vấn | Đội 1 (cánh bằng), mạng mặt đất | Phát truy vấn khi bay qua; River chuyển phần thiếu tới critical cell; critical cell đối sánh |
| Phản hồi | critical cell → CH → LoRa → BS | Báo điểm cao nhất và bitmap manh mối đang giữ, hai lần (tự giải mã, rồi River) |
| 2. Xác minh | Đội 2 (cánh quay) | Thăm critical cell theo xác suất là c\*, gửi bộ tham chiếu đầy đủ 1 MB, chờ đối sánh; T\* khi xong c\* |

| Lớp của pha 1 | Câu hỏi | Trạng thái trong bài |
|---|---|---|
| 1. Nhận dạng | Camera cần bao nhiêu dữ liệu, tổ chức thế nào, để chấm điểm đáng tin? | Mô hình điểm cosine tổng quát; không phải đóng góp chính (§5) |
| 2. Đường bay | Bay đường nào, chia cụm thế nào? | CHORD-T trên cluster có sẵn (§6) |
| 3. Định tuyến mặt đất | Chuyển dữ liệu tới critical cell thế nào? | River (§7) |

---

## 4. Mô hình hệ thống

Chi tiết và nguồn từng tham số: `paper/PARAMS-vi.md`, `uav-l2/docs/PARAM-SOURCES-vi.md`.

### 4.1 Mạng
- Miền sinh ngẫu nhiên (mọc Eden, lấp lõm theo độ lồi, khoét hồ), cell lục giác bán kính 100 m, mật độ khoảng 21 node mỗi cell.
- Mỗi node có ba năng lực ngẫu nhiên (quan sát, tính toán, giao tiếp); điểm năng lực là tích ba năng lực.
- **CL:** node mạnh nhất mỗi cell. **CH:** node mạnh nhất cách biên ≥ 300 m (nới dần). **Critical cell:** cell của CH, cell vượt μ + 2σ toàn cụm, cell vượt μ + σ và mạnh nhất trong 2 vòng.
- **Cluster có sẵn:** k-medoids có giới hạn 80 cell trên đồ thị cell.
- **Định tuyến PECEE tính trước:** không node cô lập; một cặp gateway giữa hai cell kề; lưới kênh 7 màu; mỗi cặp gateway một radio và kênh riêng; mỗi cell và mỗi cặp gateway một máy phát tại một thời điểm.

### 4.2 Kênh
- **A2G:** không gian tự do tới 100 m (−80,05 dB), sau đó số mũ 3; Rician K = 2 bốc lại mỗi gói; +10 dBm, −100 dBm.
- **Bốn chế độ môi trường** (mục 163): cộng suy hao η = 0 / 9,03 / 19,77 / 25,74 dB, hiệu chỉnh trên ns-3 cho bán kính hiệu quả R50 = 1015 / 498 / 199 / 99 m (open / r500 / r200 / r100). Tương ứng với các kịch bản mở, đô thị, đô thị dày, cao tầng hoặc tán rừng (`logs/2026-10-24_1056-a2g-radius/`).
- **G2G:** số mũ 3,5, che khuất σ = 7,8 dB cố định theo cặp, Rayleigh theo khối 100 ms (3GPP TR 38.901 UMi NLoS).
- **Vô tuyến:** 2,4 GHz, 250 kb/s, khung 127 B, tải 99 B, chiếm sóng 4,256 ms.

### 4.3 Đội bay, dữ liệu, phản hồi
- **Đội 1:** 50 m/s, 100 m, nghiêng 45° (ρ = 255 m), ±2 m/s², một gói 99 B mỗi 10 ms (mỗi 0,5 m). Bay chậm tối thiểu 25 m/s; lượn bán kính 63,7 m.
- **Truy vấn:** L = 12 ảnh (2 mặt, 4 dáng, 6 bộ phận), 400 kB, Q = 4 041 gói, khoảng 2,02 km đường bay một bản sao. Phát xen kẽ khía cạnh. Ảnh chỉ dùng được khi đủ gói (hoặc đủ gói mã).
- **Phản hồi:** LoRa, mỗi CH một bản tin mỗi 40 s (thời gian phát 0,4 s, duty cycle 1 %; theo công thức Semtech ở SF10, báo cáo 17–24 B mất 0,37 s).
- **Đội 2:** cánh quay 15 m/s; xác minh một cell khoảng 78 s (5 s ổn định + 10 592 khung × 6,88 ms + 0,18 s).

---

## 5. Lớp 1: mô hình điểm

Lời gốc: mục 83–102, 110–114, 118. Chi tiết: `paper/L1-MODEL-vi.md` (công thức (1)–(24), tài liệu tham khảo).

- Mỗi camera đã cắt sẵn crop người và tính sẵn vector đặc trưng; so khớp là độ giống cosine.
- Mỗi manh mối j có **độ nhận diện** r_j < 1 và **độ quan trọng** w_j do BS chấm (mặt quan trọng nhất, màu áo ít quan trọng).
- Giá trị khớp: m_ij = r_j·a_{i,v(j)} + ε_ij, nhiễu giảm theo số chiều hiệu dụng d (= 128).
- Kho mỗi critical cell M = 223 crop người lạ (suy từ điểm vận hành re-ID tập mở đầu tiên đã công bố, báo nhầm 20 % mỗi camera).
- **Điểm hai bước:** ước lượng độ giống từng khía cạnh từ các manh mối đang giữ, rồi gộp theo độ quan trọng khía cạnh; điểm cell là điểm crop cao nhất. Báo cáo: điểm (1 B) + bitmap (2 B).
- **c\*** là critical cell có điểm xác minh cao nhất; BS tính P(cell là c\*) từ báo cáo bằng hiệu chỉnh trên 2 000 camera mô phỏng.
- **Mô hình cho thấy:** đủ 12 manh mối thì cell đứng đầu theo điểm đúng là c\* 54 % số lần; thiếu mặt còn 20 %; chỉ có ảnh bộ phận còn 4 %. Phát xen kẽ giữ chất lượng khi cell chỉ nghe được một đoạn.
- **Phát biểu trong bài:** bài không đóng góp về xử lý ảnh; lớp 1 chỉ cho biết mạng phải giao gì và thiếu dữ liệu thì tốn gì.

---

## 6. Lớp 2: đường bay

Lời gốc: mục 56–64, 70, 82, 84, 103–106, 115–118, 120–121, 133–159. Chi tiết: `paper/L2-PARTITION-vi.md`, `paper/l2-techreport/` (IEEE 4 trang), `uav-l2/docs/PROPOSE-ITER-vi.md`, `SWATH-vi.md`, `SAT-vi.md`.

### 6.1 Phương án chốt: CHORD-T
1. **Dây cung qua CH.** Mỗi hướng θ ∈ {0°, 2°, …, 178°} cho một đường thẳng qua CH; ℓ(θ) là chiều dài trong cụm (hồ, khe, cụm khác không tính).
2. **Ứng viên:** các hướng có ℓ(θ) ≥ 0,6·max ℓ và ≥ 80 % độ dài một bản truy vấn (CLUE 80 %, mục 138).
3. **Chọn chung hướng và thứ tự cụm** cực tiểu Σ_k n_k·leave_k (n_k: số critical cell của cụm; leave_k: lúc đội 1 rời cụm), nối Dubins. Held-Karp chính xác tới 13 cụm, heuristic + quy hoạch động khi nhiều hơn.
4. **Giao đủ:** cụm có dây cung ngắn hơn một bản truy vấn thì giảm tốc (25–50 m/s) hoặc lượn quanh CH; pass ns-3 bay đúng hồ sơ vận tốc này (mục 157).

Vì sao CHORD-T hơn đường dài nhất từng cụm: đường dài nhất của mỗi cụm chĩa mọi hướng, đội 1 tốn nhiều thời gian quay giữa chúng. Trên 16 bản đồ: −29 s T\* (16/16), tour −64 s.

### 6.2 Những gì đã thử và không thắng

| Hướng | Ý tưởng | Kết quả |
|---|---|---|
| LANE (mục 84) | luồng thẳng song song rộng 4,5 cell, cắt thành cụm ≤ 80 cell | thua cả k-medoids |
| MEANDER (mục 103–106) | luồng cong theo xương sống trắc địa, đường cong mượt, Bank cục bộ | thua k-medoids 62–150 s, 40/40 bản đồ |
| subCH, subCH-K (mục 114) | tách cụm lớn quanh các critical cell xa nhau | baseline lớp 2 mạnh nhất, vẫn chậm hơn P\* 15 s |
| MEANDER-K, SWATH-K (mục 133–136) | đúng K cụm cỡ đều; SWATH: một chuỗi luống liền | +64 s và +6 s so với k-medoids |
| MEANDER kiểu luống (mục 146–155) | luống rồi uốn nhẹ về critical cell | tour ngắn hơn trên dải hẹp dài (người dùng loại vì mất tổng quát); ns-3 trên bản đồ ngẫu nhiên: CHORD-T thắng 57–171 s |
| CHORD vừa đủ, uốn, ưu tiên River (mục 159) | cắt dây cung vừa đủ, uốn khi thiếu, cụm River lâu bay trước | T\* 758 / 761 / 761 s, không khác |
| LM-Tour (mục 170–180) | R-net, đĩa R/2, chèn theo giá trị với bộ dự đoán River | không hơn CHORD (§9) |

**Bài học chung:** trên cluster có sẵn cỡ đều, CHORD-T đã gần tối ưu theo T\*. T\* do tour đội 1 (rời cụm trung bình khoảng 330 s trên k8), LoRa và pha 2 quyết định; River chỉ vài chục giây.

**Ngưỡng bão hoà theo hình dạng cụm** (mục 120–121, 75 dải): cửa sổ quanh CH bão hoà ở khoảng 2 km chiều dài; cửa sổ theo từng critical cell gỡ được giới hạn đó (dải 6 × 4 km: 88 s → 25 s, 412 k → 41 k khung). Từ đó P\* dùng cửa sổ theo critical cell.

---

## 7. Lớp 3: River

Lời gốc: mục 38–55, 66–67, 103, 163, 169. Chi tiết: `paper/L3-TECHREPORT-vi.md` (+ PDF 32 trang), `paper/RIVER-L3-vi.md`, `uav-coop2/docs/L3-vi.md`.

### 7.1 Vai trò (đơn vị là cell)
- **Axe:** các cell đường bay cắt qua. Seg(a) là đoạn gói phát khi UAV ở trên cell a. Sau khi gom nội cell, cell Axe giữ Seg của nó gần như chắc chắn ở mọi môi trường.
- **Bank:** cell ở cách Axe ω = 1,75 cell (≈ 303 m) về mỗi phía, theo pháp tuyến (cục bộ nếu đường cong). River là dải giữa hai Bank.
- **Circle:** các cell kề critical cell, mỗi cell nhận một nhóm Seg liên tiếp và lấy nó từ Bank của nhóm đó.
- **Cửa sổ:** mỗi critical cell chỉ cần bản sao truy vấn gần nó nhất dọc đường bay (Q gói).

### 7.2 Thực thi sau lượt bay
GATHER (về CL, chỉ trong cell có vai trò) → BANKFILL (Axe → Bank) → CIRCLEFILL (Bank → Circle, chuẩn bị sẵn hoặc khi được hỏi) → CRITPULL (Circle → critical cell). Yêu cầu là manifest "có" trong một khung. Mọi chặng có ACK và phát lại.

**Sửa gói thiếu** (`--repair 20`, mục 169): cell Axe lấy nốt gói thuộc Seg của nó từ cell kề có giữ; critical cell im lặng 20 s mà vẫn thiếu thì hỏi lại theo chuỗi Circle → Bank → Axe. Sau sửa: 0/812 critical cell kẹt (trước là 8).

**Với mã fountain:** River giữ nguyên trên các gói gốc (mã hệ thống); cell nào tự giải mã đủ từ gói mã nghe được thì báo sớm.

### 7.3 Kết quả lớp 3
- **Trên một cụm 91 cell, kênh mở** (E2): River ít khung hơn kéo trực tiếp 20–22 % và xong sớm hơn từ 4 critical cell trở lên, lợi thế tăng theo số critical cell; với 1 critical cell kéo trực tiếp rẻ hơn. Lưới 7 màu là đủ.
- **Ở cấp nhiệm vụ:** River, kéo trực tiếp và Trickle cho cùng T\* (16 bản đồ, kênh mở: 585 / 586 / 586 s); Trickle tốn gấp 4,7 lần khung.
- **Theo môi trường** (bảng chính): River xong TB 8–10 s ở open, 45–62 s ở r500, 78–126 s ở r200 và r100. Ở r500 River nhanh hơn kéo trực tiếp; ở r200 và r100 kéo trực tiếp nhanh hơn hoặc ngang và ít lượt truyền hơn 15–20 %, vì Bank ở 300 m gần như không nghe được gì nên Axe phải đẩy cả đoạn ra Bank. Hướng chưa thử: độ rộng River theo R50.
- **Độ bền:** River 0 cell kẹt ở cả 12 tổ hợp; kéo trực tiếp 6/92 ở k16 r100.

---

## 8. Phản hồi và pha 2

Lời gốc: mục 68–73, 111–114. Chi tiết: `uav-l2/docs/L1-MISSION2-vi.md`.

- **Báo hai lần** qua CH và LoRa: lần đầu khi cell tự giải mã (hoặc gom xong), lần sau khi River xong; mỗi báo cáo cộng dồn mọi thứ cell có.
- **Đội 2:** cất cánh lúc 0; chọn cell có P(c\*)/(thời gian bay + 78 s) lớn nhất; chỉ đi nếu P(c\*) ≥ P_U/4 (P_U: xác suất c\* chưa báo), không thì bay về tâm có trọng số của các cell chưa thăm và chờ; đổi mục tiêu giữa đường khi có báo cáo mới; thăm hết.
- **Đòn bẩy lớn nhất là pha 2** (ablation 20–21/10): bỏ đón đầu +95…+136 s, đi ở báo cáo đầu thay vì cất cánh lúc 0 +27…+74 s, β = 1 thay vì 1/4 +8…+70 s.

---

## 9. Baseline và kết quả (tóm tắt của `paper/EXPERIMENTS-vi.md`)

**Bảy phương án của bảng chính:** CHORD (P\*), FC (đội 1 bay TSP qua chính các critical cell, lượn tới khi đủ gói mã, không River), DN (như FC nhưng gom nhóm, DTSP-N), Pd (kéo trực tiếp thay River), B4 (không hợp tác), B1 (không pha 1), B7 (oracle).

T\* trung bình (s), k8 / k12 / k16:

| kênh | CHORD | FC | DN | Pd | B4 | B1 | B7 |
|---|---|---|---|---|---|---|---|
| open | 647 / 686 / 863 | 660 / 815 / 949 | 708 / 805 / 967 | 647 / 686 / 863 | 650 / 687 / 862 | 2926 / 4168 / 5169 | 322 / 402 / 404 |
| r500 | 784 / 950 / 1107 | 1138 / 1451 / 1801 | 1078 / 1388 / 1750 | 806 / 950 / 1115 | 1379 / 2030 / 2549 | như trên | như trên |
| r200 | 876 / 975 / 1192 | 2285 / 3288 / 3964 | 1904 / 2482 / 3469 | 850 / 990 / 1192 | 3711 / 5277 / 6298 | như trên | như trên |
| r100 | 872 / 990 / 1215 | 2463 / 3460 / 4368 | 2190 / 3248 / 4468 | 875 / 990 / 1334 | 3860 / 5308 / 6358 | như trên | như trên |

**Cơ chế:** đường bay của CHORD không đổi theo môi trường (782 / 1 152 / 1 415 s); phần thiếu do mặt đất bù. FC và DN phải lượn nhiều hơn khi R50 nhỏ đi: đội 1 bay gấp 2–6 lần chính nó ở kênh mở.

**Các baseline đã chạy ở vòng trước** (16 bản đồ, kênh mở, pipeline 23/10): Trickle, B2, B3, B5, B6, B8, k-medoids, subCH-K, MEANDER-K, SWATH-K. Tất cả chậm hơn P\*; mạnh nhất là subCH-K (+15 s) và kéo trực tiếp (+0 s). Chi tiết: `paper/EXPERIMENTS-vi.md` §4 E4.

---

## 10. LM-Tour và bộ dự đoán River (tóm tắt của `paper/LMTOUR-vi.md`)

- **Bộ dự đoán:** T̂_River = 0,71 + 2,29·hops + 1,97·lackCell/1000 + 4,26·cluLack/1000 (s); bỏ một bản đồ ra kiểm tra: MAE 22,8 s, R² 0,60; cây tăng cường kém hơn (26,1 s, 0,40). 89 % phương sai nằm giữa các cụm, theo tổng lượng River phải chuyển.
- **LM-Tour trên cluster có sẵn:** bản uốn dây cung hơn CHORD nhiều nhất 10,7 ± 7,4 s; bản tự do chậm hơn tới 63 s và tour dài thêm 53–112 s.
- **Vì sao:** uốn không đổi được tổng lượng River phải chuyển; không cell nào tự giải mã thêm được; mọi giây thêm ở pass làm trễ các cụm sau; pha 2 chiếm khoảng nửa T\*.
- **Đề xuất:** giữ bộ dự đoán làm mô hình hoàn tất River của BS; trình bày LM-Tour như hướng đã thử, kết quả trung tính.

---

## 11. Đối chiếu với draft (`SigDrop_ICC_draft_v3.pdf`)

| Chỗ trong draft | Số liệu hiện có nói gì | Đề xuất sửa |
|---|---|---|
| Abstract: "River completes the last critical camera 26 % earlier with 12 % fewer frames than direct pulling" | Đúng cho cụm C3, kênh mở (E2). Ở cấp nhiệm vụ T\* hoà; ở r200, r100 kéo trực tiếp ít lượt truyền hơn 15–20 % | Nêu rõ phạm vi (một cụm, kênh mở), thêm "River completes every critical cell in all 12 settings, direct pulling stalls 6 % under the shortest range" |
| Abstract: "fountain coding with in-cell gathering leaves X % incomplete" | FC lượn tới khi đủ nên 100 % critical cell xong; cái giá là đội 1 bay gấp 2–6 lần | Thay bằng: CHORD nhanh hơn FC/DN 27–72 % khi R50 ≤ 500 m |
| Abstract: "1.9–2.8× faster than rotary-wing alternatives" | Số của pipeline 21/10 (40 bản đồ, kênh mở, B3). Bảng chính mới chỉ có B1: 3,3–6 lần | Chạy lại B3 trên pipeline hiện tại, hoặc chỉ dẫn B1 |
| Đóng góp 3 và mục V: LM-Tour | Không hơn CHORD | Thay bằng CHORD-T + mô hình hoàn tất River (`paper/LMTOUR-vi.md` §8) |
| Mục VI-B: River vs direct pull | Như hàng đầu | Báo cả mức cell (lượt truyền, thời gian xong, cell kẹt) và mức nhiệm vụ (T\*) |
| Mục VI-C, Bảng I (TODO) | Đã có đủ cột cho r = 100, 200, 500, 1000 m: §5.3–5.4 của `EXPERIMENTS-vi.md` | Điền: tỉ lệ critical cell xong (River 100 %, kéo trực tiếp 93–100 %, không hợp tác: số tự giải đủ 0–100 %) và thời gian xong cuối |
| Mục VI-D: "Cooperation shortens the mission by 26–69 s … wins 39/40 maps" | Số kênh mở cũ. Mới: B4 − CHORD ≈ 0 ở open, +595 … +5 142 s ở r500–r100 | Thay bằng kết quả theo môi trường |
| Mục III-C: mô hình V(H) với h_v, ν_v [TODO: source] | Giả lập dùng mô hình điểm cosine của `paper/L1-MODEL-vi.md`, không dùng V(H) | Chọn một trong hai và thống nhất với giả lập |
| Mục IV: event pull từ camera legacy | Chưa cài | Bỏ hoặc ghi là hướng mở rộng |
| Mục III-A: "A fraction φ of cells host an AI node" | Giả lập chọn critical cell theo điểm năng lực (μ + σ, μ + 2σ), 5,5–6,1 mỗi cụm trên ba bản đồ chính | Mô tả đúng quy tắc chọn |

---

## 12. Giả định, giới hạn, việc còn mở

**Giả định:** mỗi cụm bay qua một lần, không phát lại; một UAV mỗi đội; chưa xét năng lượng, bộ nhớ, quyền sở hữu, vật cản cứng; fading A2G không đổi trong một gói (lạc quan); mọi camera chung mô hình đặc trưng; xác minh bằng bộ đầy đủ là chính xác.

**Việc còn mở cho paper:**
1. Chiến dịch nhiều bản đồ: 3 cỡ × 4 môi trường × 10 bản đồ (mục 165), với danh sách phương án của bảng chính.
2. Thêm `--repair` cho kéo trực tiếp để so công bằng ở môi trường khó.
3. Thử độ rộng River theo R50 (Bank ở 300 m vô ích khi R50 ≤ 200 m).
4. Thống nhất mô hình PER của các baseline mức mô hình (Nakagami m = 1,8) với lượt bay (Rician K = 2), và cho chúng chạy theo chế độ môi trường.
5. Nguồn cho tham số: Qiu 2017 (α), K = 2, khối fading G2G 100 ms, tham số lớp 1 (d trước tiên).
6. Hình cho bản nộp cần nhãn trục (hình trong kho không có chữ theo mục 63).

---

## 13. Lịch sử phát triển

| Thời gian | Thư mục | Mục §8 | Nội dung |
|---|---|---|---|
| 05–06/10 | `uav-sar/` | 1–8 | Thí nghiệm kênh: A2G-RUN, A2G-SWEEP, G2G-CHAIN |
| 07–08/10 | `uav-coop/` | 9–32 | Lưới lục giác, miền, thuộc tính node, CH/CL, Dubins qua CH, định tuyến PECEE, Manifest |
| 08–13/10 | `uav-coop2/` | 33–55 | River, Axe, Bank, critical cell, Circle; ns-3 MAC đầy đủ; quét màu, độ rộng, số critical cell |
| 13–14/10 | `uav-l2/` | 56–73 | Miền lớn có hồ, chia cụm, nhiệm vụ trọn vẹn, LoRa, đội 2, baseline B1–B7 |
| 14–15/10 | `paper/` | 74–82 | Khung paper, mã giả FlightLine |
| 15–20/10 | `paper/`, `uav-l2/` | 83–113 | Lớp 1: từ ngưỡng công bố sang mô hình cosine tổng quát; LANE, MEANDER |
| 20–21/10 | `uav-l2/`, `paper/` | 114–121 | Nhiệm vụ với lớp 1 mới, subCH, chẩn đoán lớp 2, OVERVIEW, bão hoà hình dạng cụm |
| 22/10 | `paper/`, `uav-l2/` | 122–136 | Báo cáo kỹ thuật lớp 3 và lớp 2; cửa sổ theo critical cell; MEANDER-K, SWATH-K; **CHORD-T** |
| 23/10 | `uav-l2/` | 137–149 | CLUE 80 %; baseline Trickle, B5, B8, subCH-K, MEANDER-K; MEANDER kiểu luống, quét yếu tố |
| 24/10 | `uav-l2/` | 150–159 | MEANDER thẳng, CH có sẵn; CHORD uốn; **pass ns-3 theo hồ sơ vận tốc**; bán kính A2G; CHORD vừa đủ |
| 25/10 | `uav-l2/` | 160–169 | Rà soát, seed theo bản đồ, binary đóng băng; **bốn chế độ môi trường**; **FC, DN**; mã fountain cho CHORD, River `--repair` |
| 25–26/10 | `uav-l2/`, `paper/` | 170–183 | Draft v3; bộ dự đoán River; LM-Tour (uốn, tự do); **bảng chung bảy phương án**; ba tài liệu này |

**Ba bước ngoặt:**
- **Manifest → River** (mục 33, 49): từ cell biên chủ động gửi danh sách "có" sang kế hoạch tính trước từ đường bay.
- **Tái cấu trúc cụm → CHORD-T trên cluster có sẵn** (mục 135–159): mọi cách chia lại cụm theo đường bay đều thua; lợi ích thật nằm ở chọn hướng dây cung chung với tour.
- **Một môi trường → bốn môi trường** (mục 163–169): ở kênh mở, River gần như không cần; từ R50 ≈ 500 m trở xuống, hợp tác mặt đất là bắt buộc, và đó là nơi CHORD bỏ xa các baseline.

---

## 14. Bản đồ kho

| Loại | Đường dẫn |
|---|---|
| Lời gốc người dùng | `CLAUDE.md` §8 |
| Ba tài liệu cho paper | `paper/SUMMARY-vi.md`, `paper/EXPERIMENTS-vi.md`, `paper/LMTOUR-vi.md` |
| Kết quả và seed | `uav-l2/docs/RESULTS-vi.md`; `uav-l2/docs/data/results/` (CSV, bản lưu 12 nhiệm vụ trong `raw/`) |
| Lớp 1 | `paper/L1-MODEL-vi.md`; mã `uav-l2/tools/l1_model.py` |
| Lớp 2 | `paper/L2-PARTITION-vi.md`, `paper/l2-techreport/`; mã `uav-l2/tools/{mission,chord_tour,pass_speed,kin_time}.py` |
| Lớp 3 | `paper/L3-TECHREPORT-vi.md`, `paper/techreport/`; ns-3 `uav-coop2/examples/coop2-river.cc`; kế hoạch `uav-coop2/tools/river_plan.py`, `river_export.py` |
| Nhiệm vụ và chấm | `uav-l2/tools/l1_rank.py`, `cmp_table.py`, `fc_table.py` |
| Baseline | `uav-l2/tools/fc_baseline.py`, `dn_baseline.py`, `mission_baselines.py` |
| LM-Tour | `uav-l2/tools/river_surrogate.py`, `lm_tour.py` |
| Tham số và nguồn | `paper/PARAMS-vi.md`, `uav-l2/docs/PARAM-SOURCES-vi.md` |
| Hình | `uav-l2/docs/figures/` (+ `INDEX.md`), `uav-coop2/docs/figures/` |
| Animation | `uav-l2/docs/anim/` (CHORD 8/12/16 cụm; CHORD, FC, DN trên cùng bản đồ) |
| Log mọi lần chạy | `logs/<ngày_giờ>-<tên>/` (README mỗi thư mục) |
| Bàn giao phiên | `docs/progress/HANDOFF.md` |

---

## 15. Thuật ngữ nhanh

| Thuật ngữ | Nghĩa |
|---|---|
| critical cell | cell có camera đủ mạnh để đối sánh; luôn gồm cell của CH |
| c\* | critical cell có điểm xác minh cao nhất; T\* là lúc đội 2 xác minh xong nó |
| Axe, Seg(a) | các cell đường bay cắt qua; đoạn gói phát trên cell a |
| Bank, River | cell ở mép dải cách Axe ω ≈ 303 m; dải giữa hai Bank |
| Circle | các cell kề một critical cell, mỗi cell lấy sẵn một nhóm Seg |
| cửa sổ | bản sao truy vấn (Q gói liên tiếp trên Axe) gần critical cell nhất |
| CHORD, CHORD-T | đường thẳng qua CH; bản chọn hướng chung với tour độ trễ |
| CLUE | tỉ lệ tối thiểu của một bản truy vấn mà dây cung phải chứa (80 %) |
| R50 | khoảng cách ngang mà xác suất một gói tới được node còn 1/2 |
| FC, DN | baseline: UAV bay qua chính các critical cell (FC) hoặc quỹ đạo quanh nhóm (DN), mã fountain, không River |
| Pd | CHORD với kéo trực tiếp thay River |
| B1, B4, B7 | không pha 1; không hợp tác; oracle |
| mã fountain hệ thống | gói gốc phát trước, gói mã sau; cell giải được từ bất kỳ đủ 1,05·K gói |
| ghép cặp | mọi phương án dùng cùng kênh, cùng bitmap ns-3, cùng lượt bốc lớp 1 |
