# LM-Tour: ý tưởng, thuật toán, bộ dự đoán và kết quả

- **Phiên bản:** 2026-10-29. Lời gốc: CLAUDE.md §8 mục 170–175 (bộ dự đoán), 184 (ξ), 187 (thuật toán hiện tại), 188 (chiến dịch 4).
- **Nguồn ý tưởng:** draft `SigDrop_ICC_draft_v5`, mục V "Flight design: LM-Tour" và Algorithm 3.
- **Mã:** `uav-l2/tools/river_surrogate.py` (bộ dự đoán), `uav-l2/tools/lm_tour.py` (`plan --dtspn`, `score`).
- **Log:** `logs/2026-10-27_1800-lm-dtspn/` (k8, mức mô hình và ns-3), `logs/2026-10-27_1714-campaign4/` (chiến dịch 4), `logs/2026-10-28_t3-surrogate/` (khảo sát Bậc 3).
- **Tài liệu đi kèm:** `paper/TECHREPORT-vi.md` (báo cáo kỹ thuật, §4.2 và §5), `paper/EXPERIMENTS-vi.md` (thực nghiệm).

---

## 0. Kết luận trong một đoạn

LM-Tour chọn đường bay của đội 1 theo hai bước:
1. dựng một tour **DTSP-N qua đĩa B(CH, ξ)** của mọi cụm, chọn hướng qua mỗi CH, chiều bay và thứ tự cụm cùng lúc;
2. trong mỗi cụm, **uốn dần đường bay về các critical cell có trọng số cao**, chừng nào hàm mục tiêu J_k còn giảm.

J_k dùng một **bộ dự đoán thời gian River** học trên các lượt ns-3 (MAE 22,8 s trên bản đồ chưa thấy).

Kết quả chiến dịch 4 (khoảng 55 % seed, số thăm dò):
- nhanh hơn CHORD + River 1–10 %;
- nhanh hơn DTSP-N + River 8–26 %;
- nhanh hơn FC + DTSP-N 10–72 %.

Đường bay ngắn hơn CHORD 14–28 %. Phần lớn lợi ích đến từ tour; bước uốn tinh chỉnh thêm 7–22 s.

---

## 1. Ý tưởng gốc (draft, mục V)

### 1.1 Nhận xét then chốt
- Trong phát quảng bá một lượt, **hình học đường bay chính là lịch phát**. Gói s được phát tại γ(d₀ + sΔ), nên BS biết trước đoạn dữ liệu nào rơi xuống cell nào.
- Vì vậy đường bay nên được thiết kế cho River, không phải cho độ phủ.
- **Ý tưởng LM-Tour:** bay qua một tập *landmark* (các node AI giá trị nhất, trải đều). River phục vụ mọi node AI trong bán kính R quanh chúng.

### 1.2 Giá trị của node
Mỗi node AI u có trọng số w(u), tổng hợp lý do nên bay sát nó:
- năng lực tính toán;
- cỡ cây camera legacy gắn vào nó;
- tiên nghiệm π_u rằng mục tiêu đã đi qua;
- **thời gian River tiết kiệm được** khi đường bay đi sát u. Phần này do một bộ dự đoán học có giám sát trên các lượt ns-3 cung cấp (§3).

### 1.3 Algorithm 3 của draft
```text
Algorithm 3  LM-TOUR  (draft)
Input: AI nodes with weights w, land graph G, R, ρ, θ, L_max
 1: A* ← AI nodes sorted by w (descending); K1 ← ∅
 2: for all u ∈ A* do
 3:     if d_G(u, K1) ≥ R then K1 ← K1 ∪ {u}
 4: clusters ← GROW(G, K1)                                   ▷ balanced Voronoi regions
 5: γ ← Dubins TSP-N through discs B(u, ξ), u ∈ K1
 6: C ← {v ∈ A* \ K1 : d(v, visited) > R/2}
 7: repeat
 8:     for all v ∈ C do ΔL(v) ← cheapest local re-route of γ into B(v, ξ) passing the window check
 9:     v* ← argmax_v w(v)/ΔL(v)
10:     if w(v*)/ΔL(v*) < θ or |γ| + ΔL(v*) > L_max then break
11:     insert v*; remove from C all nodes within R/2 of v*
12: until C = ∅
13: return γ, clusters, visited nodes
```

### 1.4 Bán kính đĩa ξ (draft v5, công thức (5))
$$\xi = \min\bigl(\omega,\ \rho,\ \sqrt{r^2 - h^2}\bigr) = \min(303,\ 255,\ R50) \Rightarrow 255 / 255 / 199 / 99\ \text{m}$$
cho r = 1 000 / 500 / 200 / 150 m.
- Trong ω, node nằm trong dải River.
- ξ ≤ ρ để đường còn quay được tại landmark.
- Trong √(r² − h²) (R50 ngang đã hiệu chỉnh), node nghe UAV trực tiếp.

---

## 2. Đặt ý tưởng vào giả lập

### 2.1 Cái gì cố định, LM-Tour đổi gì
- **Cố định** (giống mọi phương án của chiến dịch): cluster k-medoids có sẵn (≤ 80 cell), CH, critical cell; River (`--repair 20`), lớp 1, LoRa, chính sách đội 2.
- **LM-Tour đổi:** pass qua mỗi cụm, hướng và chiều bay, thứ tự cụm. Đổi pass thì đổi luôn kế hoạch River, phần tự giải mã và các đoạn nối.
- **Trên cluster có sẵn**, dòng 1–4 của Algorithm 3 rút về: K₁ là tập các CH (node mạnh nhất mỗi cụm), clusters là các cụm có sẵn. Dòng 5 là tour DTSP-N qua các đĩa B(CH, ξ); dòng 6–12 là bước uốn.

### 2.2 Ràng buộc giao đủ dữ liệu và hệ quả
- Mỗi cụm phải được phát **một bản sao trọn bộ manh mối** (4 041 gói, 40,4 s) trên chính các cell của nó (`pass_speed.fit`): đường ngắn thì giảm tốc, giảm tới 25 m/s vẫn chưa đủ thì lượn vòng 63,7 m tại CH.
- **Hệ quả:** một đường ngắn bay chậm tốn **cùng thời gian trong cụm** như một dây cung dài bay nhanh. Đo trên k16 r200: CHORD bay 2,1 km trong cụm ở 48 m/s, LM-Tour 1,6 km ở 38 m/s; cả hai khoảng 40 s mỗi cụm.
- Vì vậy chi phí của một chặng (dòng 5, dòng 8) phải đo bằng **thời gian sau khi giao đủ**, không bằng độ dài. Uốn thêm ở cụm phải giảm tốc gần như miễn phí.

### 2.3 Trọng số
- w_c = điểm CL của critical cell c chia cho trung bình trên bản đồ (`--weight cl`); trọng số cụm W_k = Σ_{c ∈ Crit_k} w_c.
- Ứng viên để uốn phải có w_c ≥ wmin = 1 (từ trung bình trở lên).
- Trong mô hình lớp 1 hiện tại, c\* không phụ thuộc điểm CL, nên trọng số chỉ ảnh hưởng T\* qua việc định hình tour (mức mô hình, k8 r200: trọng số CL 808 s, trọng số đều 827 s). Khi có tiên nghiệm π_u không đều, trọng số sẽ có tác động trực tiếp.

---

## 3. Bộ dự đoán thời gian River

### 3.1 Vai trò
J_k cần biết, **trước khi cất cánh**, River sẽ mất bao lâu để đưa đủ dữ liệu tới từng critical cell khi đường bay là γ. Chạy ns-3 cho mỗi ứng viên là không khả thi (2–4 phút một lượt River, hàng trăm ứng viên), nên BS dùng một mô hình thay thế f: đặc trưng của (cell, đường bay, kênh) → doneS.

### 3.2 Dựng bộ dữ liệu
- **Nhãn:** doneS của từng critical cell, số giây từ lúc đội 1 rời cụm tới lúc CL giữ đủ cửa sổ của nó (bản sao 4 041 gói gần nó nhất), đo bằng River ns-3.
- **Nguồn:** 3 bản đồ (k8, k12, k16) × 4 kênh, River ns-3 `--repair 20`. 812 critical cell, 0 cell kẹt. doneS trung bình 67,3 s, độ lệch 54,8 s, từ 1,7 tới 311,3 s.
- **Quy trình** (`river_surrogate.dataset`):
  1. nạp hình học từng cụm;
  2. tính lại kế hoạch River bằng `river_plan.plan`, đúng tham số đã dùng cho ns-3;
  3. `check_plan`: đối chiếu từng dòng AXE / CRIT / NEED với `plan{k}.txt` của ns-3 (lệch tối đa 2 gói ở biên cell);
  4. tính đặc trưng từ đường bay và mô hình nghe của kênh, ghép với nhãn;
  5. ghi `uav-l2/docs/data/results/river-surrogate.csv`, mỗi dòng một critical cell.
- Lượng thiếu dự đoán khớp ns-3 gần như tuyệt đối (tương quan r = 1,000 cho cell và CL; trung bình 2 200 so với 2 183 gói).

### 3.3 Đặc trưng (BS biết hết trước khi cất cánh)

| Đặc trưng | Nghĩa |
|---|---|
| hops | số cell từ critical cell tới cell Axe gần nhất trong cửa sổ của nó |
| dpath | khoảng cách (m) từ tâm cell tới đường bay trong cửa sổ |
| lackCell | số gói của cửa sổ mà các node của cell (hợp lại) dự đoán là thiếu, theo mô hình nghe của kênh |
| lackCL | như trên, riêng CL |
| naxe | số cell Axe mà cửa sổ trải qua |
| ring1, ring2 | số cell của cụm trong vòng 1, vòng 2 (ứng viên Circle) |
| ncrit | số critical cell của cụm |
| share, shareLack | số critical cell khác có cửa sổ chồng lên, và tổng lackCell của chúng |
| **cluLack** | tổng lackCell của mọi critical cell trong cụm: toàn bộ lượng River phải chuyển |
| loss | suy hao thêm của kênh (dB) |

### 3.4 Huấn luyện và chọn mô hình
Kiểm tra chéo bỏ một bản đồ (3 lượt) và bỏ một kênh (4 lượt); tập thử luôn là bản đồ hoặc kênh mô hình chưa thấy.

| Mô hình | Cách học | Bỏ một bản đồ: MAE (s) / R² | Bỏ một kênh: MAE / R² |
|---|---|---|---|
| trung bình | hằng số | 42,4 / −0,02 | 51,9 / −0,40 |
| **công thức 3 biến (đang dùng)** | bình phương tối thiểu | **22,8 / 0,60** | **22,3 / 0,63** |
| tuyến tính, 12 đặc trưng | bình phương tối thiểu | 23,0 / 0,60 | 24,1 / 0,61 |
| cây tăng cường | sâu 2, 200 cây, lr 0,05, lá ≥ 20 | 26,1 / 0,40 | 28,6 / 0,55 |

$$\widehat{T}_{\text{River}}(c) = 0{,}71 + 2{,}29\,\text{hops}_c + 1{,}97\,\frac{\text{lackCell}_c}{1000} + 4{,}26\,\frac{\text{cluLack}_{k(c)}}{1000}\quad\text{(s)}$$

![Dự đoán so với ns-3](../uav-l2/docs/figures/lm-surrogate-pred-vs-ns3.png)

*Hình 1: mỗi chấm một critical cell (812 cell). Trục ngang là doneS ns-3; trục dọc là dự đoán khi bản đồ của nó bị giữ lại làm tập thử. Màu theo kênh; đường chéo là dự đoán đúng.*

**Đọc kết quả:**
- **89 % phương sai doneS nằm giữa các cụm** và đi theo cluLack (độ quan trọng trong cây 0,54, tiếp theo lackCell 0,24). River dùng chung Bank, gateway và kênh, nên thời gian của một cell chủ yếu do lượng dữ liệu cả cụm phải chuyển; khoảng cách riêng của cell góp khoảng 2,3 s mỗi hop.
- Cây không hơn công thức với 3 bản đồ; cây sâu hơn học thuộc hai bản đồ và kém trên bản thứ ba.
- Phần đuôi (River 150–310 s) bị dự đoán thấp.

### 3.5 Kiểm chứng ở mức nhiệm vụ
- `lm_tour.py score --mode pred` thay doneS ns-3 bằng T̂; dùng để so các đường bay chưa chạy ns-3.
- k8, CHORD: T\* dự đoán 672 / 816 / 897 / 917 s so với ns-3 672 / 802 / 877 / 892 s.
- Chênh LM-Tour − CHORD (k8, seed 1): dự đoán −38 / −93 / −89 / −90 s so với ns-3 −38 / −83 / −84 / −90 s.
- DTSP-N + River (k12, k16): ước lượng trước khi chạy ns-3 lệch số ns-3 0–17 s ở 8 ô.

### 3.6 Khảo sát các mức mô hình học (ba bậc theo `SigDrop2_LMTour_Surrogate_guide.pdf`)

| Bậc | Nội dung | Điều học được | Vai trò |
|---|---|---|---|
| 1. Công thức vật lý | w = V·[Lack(u, d̄) − Lack(u, 0)]·τ_f·h | lượng thiếu tính từ mô hình nghe khớp ns-3 (r = 1,000): đại lượng vật lý là đặc trưng tốt | nguồn đặc trưng lackCell, hops |
| 2. Hiệu chỉnh trên ns-3 | T ≈ a + b·hops + c·lackCell + d·cluLack | 3 biến ngang 12 biến; biến quyết định là cluLack | **đang dùng** trong J_k |
| 3. Cây kiểu LightGBM | 400 vòng, lr 0,05, đơn điệu theo khoảng cách và lượng thiếu | chưa chọn đường tốt hơn Bậc 2 với dữ liệu hiện có | **còn cân nhắc** |

**Khảo sát Bậc 3** (`logs/2026-10-28_t3-surrogate/`): 192 lượt pass + River ns-3 trên k8. Mỗi (kênh, cụm) có 5–10 đường bay (đường DTSP-N không uốn, 5 biến thể uốn, và các đường khác đã chạy); tổng 253 đường bay, 1 457 kết quả cell. Mô hình học trên k12, k16 và phải chọn đường tốt nhất trong mỗi cụm của k8.

| Mô hình | Spearman (xếp hạng đường trong cụm) | Regret (s mỗi cụm) | Chọn đúng đường tốt nhất |
|---|---|---|---|
| công thức (Bậc 2) | 0,52 | 26 ± 30 | 34 % |
| cây kiểu LightGBM (Bậc 3) | 0,47 | 44 ± 46 | 28 % |
| chọn ngẫu nhiên | 0 | 59 | – |

Khi cho học thêm đường của chính bản đồ (bỏ riêng cụm đang thử), Bậc 3 nhỉnh hơn công thức 12,5 ± 37,4 s, trong nhiễu.

**Vì sao Bậc 3 còn đáng cân nhắc:**
1. **Dữ liệu học còn nhỏ:** 632 cell từ hai bản đồ, so với khoảng 50 bản đồ và 7 000 mẫu trong kế hoạch của hướng dẫn. Khi thêm dữ liệu cùng bản đồ, khoảng cách đảo chiều (+18 thành −12 s).
2. **Phần đuôi:** công thức dự đoán thấp các cell 150–310 s; mô hình phân vị p90 nhắm đúng phần này, chưa thử.
3. **Mục tiêu học lệch mục tiêu dùng:** mô hình học sai số từng cell nhưng được dùng để xếp hạng đường bay; học trực tiếp thứ hạng theo cặp đường bay chưa thử.
4. **Kịch bản giàu hơn:** với π_u không đều, cây camera legacy, tần suất sự kiện, trọng số có tương tác phi tuyến, là chỗ mô hình cây có lợi thế.
5. **Trần chưa biết:** chưa đo nhiễu lặp lại của một lượt River (cùng đường, khác seed).

---

## 4. Hàm mục tiêu của một pass

$$J_k = \sum_{c \in \text{Crit}_k} w_c\,\text{ready}_c + \Bigl(\sum_{c} w_c\Bigr) t^{\text{in}}_k + \theta\, W^{\text{after}}_k \bigl(t^{\text{in}}_k + \text{dur}_k + t^{\text{out}}_k\bigr)$$

- **ready_c = min(own_c, dur_k + T̂_River(c))**, tính từ đầu pass:
  - own_c: lúc cell tự giải mã bộ manh mối mã fountain dọc pass (kỳ vọng: hợp theo cell của xác suất nghe từng gói, tới mục tiêu 1,05·K_j + 3√(1,05·K_j) mỗi file), cộng thời gian gom nội cell 0,07 + 0,00789 × số gói chuyển về CL;
  - T̂_River(c): bộ dự đoán §3 trên **kế hoạch River của chính pass này**.
- **dur_k:** thời lượng pass sau khi giao đủ (§2.2).
- **t_in, t_out:** đoạn nối Dubins (ρ = 255 m) tới pass trước và pass sau, hoặc từ/về BS với hướng tự do. Uốn pass đổi tư thế đầu/cuối nên đổi luôn hai đoạn này.
- **W_after:** tổng trọng số critical cell của các cụm bay sau; mỗi giây thêm vào pass hoặc đoạn nối làm trễ tất cả chúng. θ = 1.
- **Liên hệ với draft:** quy tắc w(v)/ΔL(v) ≥ θ trở thành "chèn nếu J_k giảm", với ΔL đo bằng thời gian. J_k chấm lại cả kế hoạch River của cụm cho từng ứng viên, nên lợi ích của một lần uốn được tính đúng trên cả cụm, không cộng dồn riêng từng cell.

---

## 5. Thuật toán

```text
Algorithm LM-TOUR(map, ξ, θ, weights w, wmin)
 1: for each cluster k, bearing b ∈ {0°, 30°, …, 150°}:
 2:     ℓ_{k,b} ← straight line through CH_k at bearing b, cut to its run over cluster k (lakes < 300 m bridged)
 3:     L_{k,b} ← V1 · dur(FIT(ℓ_{k,b}))                 ▷ cost of the leg = its delivery-feasible time
 4: (b_k, dir_k, order) ← argmin Σ_k W_k · leave_k        ▷ DTSP-N through the discs B(CH_k, ξ):
                          Held-Karp over (cluster, leg, direction), Dubins transits (chord_tour.choose)
 5: W_after, neighbours nb from order
 6: for each cluster k: γ_k ← LM-PASS(k, ℓ_{k,b_k}, nb_k, W_after_k)
 7: fly the passes in ns-3; RIVER

Function LM-PASS(k, ℓ, nb, W_after)
 1: base ← EVAL(BEND(ℓ, pulls = ∅, pin = CH_k)); cur ← base; pulls ← ∅
 2: repeat
 3:     Cand ← {c ∈ Crit_k \ pulls : w_c ≥ wmin, dist(c, cur) > ξ}
 4:     for c ∈ Cand: γ_c ← BEND(ℓ, pulls ∪ {c}, ξ, pin = CH_k); keep γ_c only if it crosses k once
 5:     c* ← argmin_c J(EVAL(γ_c))
 6:     if no candidate or J(EVAL(γ_c*)) ≥ J(cur) then break      ▷ benefit saturated
 7:     pulls ← pulls ∪ {c*}; cur ← EVAL(γ_c*)
 8: return cur

Function EVAL(γ)
 1: FIT(γ) → dur, packet positions
 2: River plan of γ (Axe, Seg, Bank, per-cell windows) → features x_c → T̂_River(c)
 3: own_c ← expected fountain decode along γ (+ in-cell gather); ready_c ← min(own_c, dur + T̂_River(c))

BEND(ℓ, P, ξ, pin) = meander_lane.bend_lane: Gaussian bumps pull ℓ into every disc B(c, ξ), c ∈ P,
                     the CH pinned, curvature ≤ 1/ρ
FIT(γ) = pass_speed.fit: slow down (≥ 25 m/s) or loop (63.7 m at the CH) until 4 041 packets fall on the cluster
```

- Lệnh: `lm_tour.py plan CHORD_WORK --out LM_WORK --dtspn --weight cl --wmin 1 --xi auto --theta 1 --rounds 1`.
- Ràng buộc: CH luôn được ghim (pass ns-3 cần đi qua CH); đường cắt mỗi cụm đúng một lần (khe hở do hồ < 300 m), nên mỗi cụm một River.

![LM-Tour + River, k8-s1, r500](../uav-l2/docs/figures/c4-phase1/c4-phase1-k8-s1-r500-lmtour-mono.png)

*Hình 2: LM-Tour + River, k8-s1, kênh r500. Tour DTSP-N qua các CH (sao), đường qua mỗi cụm ngắn (các vòng lượn là phần bù giao đủ), uốn nhẹ về critical cell; tour 30,8 km, đội 1 bay 699 s.*

---

## 6. Kết quả

### 6.1 Phân tách lợi ích (k8, mức mô hình, 100 lượt bốc ghép cặp)
T\* so với CHORD + River (s):

| Kênh | DTSP-N qua CH, không uốn | LM-Tour (có uốn) | phần do uốn | số lần uốn (8 cụm) |
|---|---|---|---|---|
| open | −19 ± 35 | −38 ± 31 | −19 ± 26 | 9 |
| r500 | −82 ± 37 | −93 ± 37 | −11 ± 14 | 10 |
| r200 | −66 ± 34 | −89 ± 33 | −22 ± 8 | 11 |
| r100 | −83 ± 34 | −90 ± 34 | −7 ± 7 | 9 |

### 6.2 Chiến dịch 4 (ns-3, khoảng 55 % seed)
T\* (s), bản đồ k8 / k12 / k16 (8 / 12 / 15 cụm), xếp theo T\* giảm dần. Bảng đầy đủ và số seed từng ô: `paper/TECHREPORT-vi.md` §3.

| Phương án | r = 1 000 m | 500 m | 200 m | 150 m |
|---|---|---|---|---|
| Rotary TSP | 2926 / 4122 / 5248 | 2941 / 4165 / 5178 | 2884 / 4165 / 5173 | 2884 / 4227 / 5242 |
| FC + DTSP-N | 708 / 841 / 1067 | 1060 / 1489 / 1877 | 1893 / 2608 / 3689 | 2192 / 3366 / 4523 |
| DTSP-N + River | 783 / 821 / 1092 | 915 / 1153 / 1452 | 952 / 1300 / 1669 | 1019 / 1374 / 1658 |
| CHORD + River | 672 / 758 / 946 | 762 / 1054 / 1190 | 826 / 1117 / 1322 | 839 / 1173 / 1335 |
| **LM-Tour + River** | **633 / 753 / 917** | **692 / 948 / 1164** | **765 / 1009 / 1229** | **779 / 1063 / 1262** |

Đường bay đội 1: LM-Tour 30,8–31,1 / 46,3–46,5 / 56,1–60,5 km so với CHORD 38,6 / 64,0 / 70,7 km. Thời gian đội 1: LM-Tour 697–708 / 1082–1085 / 1291–1394 s so với CHORD 784 / 1292 / 1437 s.

### 6.3 Pass trong từng cụm (k16, r200, trung bình mỗi cụm)

| Phương án | Độ dài trong cụm (m) | Thời gian trong cụm (s) | Tốc độ (m/s) | Critical cell trong ξ |
|---|---|---|---|---|
| DTSP-N + River | 2 438 | 62,4 | 39,6 | 92/92 |
| CHORD | 2 099 | 43,3 | 48,3 | 42/92 |
| LM-Tour | 1 560 | 40,5 | 38,5 | 36/92 |

---

## 7. Phân tích thiết kế
1. **Tour làm phần chính.** Thời gian trong cụm bị chốt ở khoảng 40 s bởi ràng buộc giao đủ, nên đường ngắn qua CH không mất gì trong cụm mà rút ngắn được các đoạn nối. Chọn hướng qua CH chung với thứ tự cụm (DTSP-N) cho phần lớn lợi ích (§6.1).
2. **Bước uốn tinh chỉnh và bão hoà nhanh.** Kéo đường về một cell chỉ đổi hops và một phần lackCell của cell đó, còn cluLack của cả cụm gần như không đổi. Lợi ích bão hoà sau 1–2 lần uốn mỗi cụm, đúng tiêu chí dừng của LM-PASS.
3. **Chọn đúng landmark quan trọng hơn bay sát nhiều cell.** LM-Tour đưa ít critical cell vào trong ξ nhất (36/92) nhưng nhanh nhất; DTSP-N + River vào mọi đĩa (92/92) nhưng phải bay 62 s mỗi cụm thay vì 40 s. River lo phần còn lại.
4. **Pha 2 làm loãng lợi ích.** Thời điểm critical cell sẵn sàng của LM-Tour sớm hơn CHORD 58–105 s, nhưng chênh T\* nhỏ hơn, vì đội 2 còn bay và xác minh khoảng 78 s mỗi cell.

---

## 8. Cho paper
- **Mục V (Flight design):** LM-Tour trên cluster có sẵn = tour DTSP-N qua đĩa B(CH, ξ) với chi phí chặng là thời gian giao đủ, rồi uốn theo J_k tới khi bão hoà. Algorithm 3 cần cập nhật theo §5 (`paper/icc-v5/alg3-lmtour.tex`).
- **Bộ dự đoán:** công thức ba biến hiệu chỉnh trên ns-3 (MAE 22,8 s trên bản đồ chưa thấy; sai số mức nhiệm vụ ≤ 10–25 s). Bậc 3 trình bày như hướng đã khảo sát: "một bộ hồi quy cây tăng cường kiểu LightGBM, ràng buộc đơn điệu, học trên hai bản đồ chưa chọn đường bay tốt hơn công thức ba biến trên bản đồ thứ ba; mở rộng dữ liệu và học trực tiếp thứ hạng là hướng tiếp theo".
- **Số liệu:** chờ đủ 10 seed (N ≥ 120). Không lấy riêng seed 1: ở k16, seed 1 cho chênh LM-Tour − CHORD lớn gấp 2–3 lần các seed khác.

---

## 9. Tái lập
```text
# từ gốc repo; CHORD_WORK là thư mục nhiệm vụ CHORD thường (mission.py, không --chordTour)
python3 uav-l2/tools/river_surrogate.py --works W1,...,W12 --out uav-l2/docs/data/results/river-surrogate   # bộ dự đoán
python3 uav-l2/tools/lm_tour.py plan CHORD_WORK --out LM_WORK --R 450 --xi auto --theta 1 --rounds 1 \
  --dtspn --weight cl --wmin 1
python3 uav-l2/tools/mission.py --clusters K --seed 1 --bin BIN --windowKB 400 --windowAt crit --critRing domain \
  --axeNear --kinPass --mapRuns --env ENV --riverRepair 20 --schemes rf --work LM_WORK [--runSeed R]
python3 uav-l2/tools/lm_tour.py score CHORD_WORK,LM_WORK --mode ns3 --out OUT      # hoặc --mode pred
```
- Một tác vụ đầy đủ của chiến dịch: `logs/2026-10-27_1714-campaign4/task.sh R ENV K` hoặc `job.sh SCH R ENV K`.
- Khảo sát Bậc 3: `logs/2026-10-28_t3-surrogate/run.sh ENV`, rồi `t3.py`.
