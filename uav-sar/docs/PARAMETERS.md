# uav-sar — Tham số & căn cứ (parameters & citations)

> Cột **Nguồn/độ tin cậy**: `[Lit✓]` giá trị chuẩn, tái lập rộng rãi;
> `[Lit?]` cần bản PDF gốc để xác nhận con số chính xác; `[Design]` lựa chọn
> thiết kế của bạn (không cần paper); `[Assume]` giả định cần kiểm định.
> Các số `[Lit?]` liệt kê ở mục F (IEEE cần tải PDF).

Cập nhật: 2026-07. Trạng thái: bản nghiên cứu sơ bộ (self-research, public sources).

---

## A. Kênh A2G / G2G (802.15.4 @ 2.4 GHz)

| Tham số | Giá trị đề xuất | Nguồn / tin cậy |
|---|---|---|
| Tần số sóng mang | 2.4 GHz (kênh 11–26 IEEE 802.15.4) | [Lit✓] IEEE 802.15.4 |
| FSPL tại d0=1 m | ≈ 40.05 dB (`20log10(4πd0f/c)`) | [Lit✓] Friis |
| Path-loss exponent **A2G (LoS)** | **n_A2G ≈ 2.0–2.3** (dùng 2.2) | [Lit✓] 3GPP TR 36.777 (LoS ~ free-space α≈2.2); Khawaja 2019 |
| Path-loss exponent **G2G (NLoS/mặt đất)** | **n_G2G ≈ 3.0–4.0** (dùng 3.5) | [Lit✓] mô hình log-distance đô thị/rừng |
| Ngưỡng độ cao chuyển A2G↔G2G | ~ 10–20 m (dùng đỉnh tán cây) | [Assume] |
| **LoS probability** (Al-Hourani) | `P_LoS(θ)=1/(1+a·e^{-b(θ-a)})`, θ = góc ngẩng (độ) | [Lit✓] Al-Hourani 2014 |
| — (a,b) Suburban | (4.88, 0.43) | [Lit?] xác nhận bảng gốc |
| — (a,b) Urban | (9.61, 0.16) | [Lit?] |
| — (a,b) Dense Urban | (12.08, 0.11) | [Lit?] |
| **Excess loss** η_LoS / η_NLoS (dB) Suburban | 0.1 / 21 | [Lit?] Al-Hourani 2014 |
| — Urban | 1.0 / 20 | [Lit?] |
| — Dense Urban | 1.6 / 23 | [Lit?] |
| **Suy hao tán cây** (vegetation) | 0.3–0.8 dB/m @2 GHz (lá rụng có lá); mô hình mũ `A_max(1-e^{-dγ/A_max})`, A_max≈10–40 dB | [Lit✓] ITU-R P.833-10 |
| **Shadowing** (log-normal σ) | σ ≈ 8–9 dB (đo woodland ~8.7 dB) | [Lit✓/Assume] ITU-R P.833; đo rừng |
| **Fading nhỏ (Nakagami m)** | m≈1 (Rayleigh, NLoS rừng dày) → m≈2–3 (có LoS một phần) | [Assume] cần Khawaja 2019 để chốt theo môi trường |

> Ghi chú: `main` dùng A2G=2.2 / G2G=3.5 + Nakagami + shadowing → **khớp literature**;
> ta giữ hướng này, chỉ cần chốt (a,b), η, m theo môi trường "rừng/vườn quốc gia".

---

## B. Radio IEEE 802.15.4 (lr-wpan ns-3)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Data rate | 250 kbps (O-QPSK, 2.4 GHz) | [Lit✓] IEEE 802.15.4 |
| PSDU tối đa | 127 B (payload app an toàn ~100 B) | [Lit✓] spec |
| TX power | 0 dBm (dải −25…+5) | [Lit✓] CC2420/CC2650 datasheet |
| RX sensitivity | spec −85 dBm; thực tế −95 dBm (CC2420), −100 dBm (CC2650) | [Lit✓] datasheet |
| Kênh | 11 (2.405 GHz) | [Design] |

---

## C. UAV: bay & năng lượng

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Mô hình năng lượng rotary-wing | `P(V)=P0(1+3V²/U_tip²)+P_i(√(1+V⁴/4v0⁴)−V²/2v0²)^{1/2}+½ d0 ρ s A V³` | [Lit✓] Zeng-Xu-Zhang 2019 |
| P0 (blade profile) | 79.86 W | [Lit?] xác nhận bảng sim |
| P_i (induced) | 88.63 W | [Lit?] |
| U_tip (tip speed) | 120 m/s | [Lit?] |
| v0 (mean rotor induced velocity hover) | 4.03 m/s | [Lit?] |
| d0 (fuselage drag ratio) | 0.6 | [Lit?] |
| ρ (air density) | 1.225 kg/m³ | [Lit✓] |
| s (rotor solidity) | 0.05 | [Lit?] |
| A (rotor disc area) | 0.503 m² | [Lit?] |
| Hover power (P0+P_i) | ≈ 168.5 W | [Lit✓ dẫn xuất] |
| Tốc độ FAST / DATA | 20–30 / 10–20 m/s | [Design] |
| Độ cao bay | 20 m (round-2: 1 mode) | [Design] |
| Dung lượng pin | vd 10–20 Wh | [Design/Assume] |

---

## D. Ứng dụng SAR (chủ yếu THIẾT KẾ của bạn)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Ảnh gốc | 416×416×3 px | [Design] baseline của bạn |
| Fragment: dải kích thước | 100 B – 20 KB | [Design] |
| Phân tầng L0/L1/L2/L3 | vd {180,8,24,4} (tổng 216) | [Design] tham số hoá |
| Utility fragment p_i | L0 cao (cue), giảm dần | [Design] |
| Confidence hợp nhất | `C=1-∏(1-p_i)` (p0=0.90) | [Design] baseline của bạn |
| alertThreshold (phát hiện) | 0.75 | [Design] (round-1) |
| confirmThreshold (xác nhận full) | ~0.95 | [Design] |
| cooperationThreshold | 0.30 | [Design] (round-1) |
| Coop success intra / inter | 0.92 / 0.82 (nên **dẫn xuất từ PDR kênh**, không hardcode) | [Assume]→[Lit] |
| regionWindow (chờ gộp liên-cell) | ~1 s | [Design] |
| beaconQuota / interval | 60 / 1 s | [Design] |

---

## E. Topology / PECEE

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Grid spacing sensor | 20 m | [Design] |
| Hex cell radius | 80 m | [Lit?/Design] PECEE / scenario4 |
| Neighbor discovery radius | 80–120 m | [Design] |
| UAV broadcast radius | ~50 m (dẫn xuất link budget) | [Lit✓ dẫn xuất] |
| Bầu CL | node gần **tâm cell** nhất | [Design] (sửa so với main) |
| Color scheme | tô màu theo cell kề | [Design] (sửa so với main) |
| Số seed | ≥ 100 | [Design] |

---

## F. DANH SÁCH IEEE CẦN BẠN TẢI PDF

Cần con số chính xác trong bảng/công thức (abstract cũng giúp định hướng). Ưu tiên ★.

1. ★ **Al-Hourani, Kandeepan, Lardner (2014)** — *Optimal LAP Altitude for Maximum Coverage*, IEEE WCL 3(6):569–572. DOI 10.1109/LWC.2014.2342736.
   → Cần: bảng (a,b) sigmoid LoS + η_LoS/η_NLoS (dB) từng môi trường; tần số.
2. ★ **Zeng, Xu, Zhang (2019)** — *Energy Minimization for Wireless Communication with Rotary-Wing UAV*, IEEE TWC 18(4):2329–2345. DOI 10.1109/TWC.2019.2902559.
   → Cần: bảng hệ số P0, P_i, U_tip, v0, d0, s, A (mục C). (Có preprint arXiv 1804.02238 nhưng bị chặn tải ở đây.)
3. ★ **Khawaja, Guvenc, Matolak, Fiebig, Schneckenburger (2019)** — *A Survey of A2G Propagation Channel Modeling for UAV Communications*, IEEE COMST 21(3):2361–2391. DOI 10.1109/COMST.2019.2915069.
   → Cần: Nakagami m + shadowing σ theo môi trường (đặc biệt **rừng/vegetation/over-foliage**).
4. **3GPP TR 36.777** — *Enhanced LTE support for aerial vehicles* (public, không phải IEEE).
   → Cần: mô hình path-loss + LoS probability + ngưỡng độ cao cho **RMa (rural)**. Tôi có thể tự tải bản ETSI/3GPP; sẽ thử.
5. **Le, Vu, Nguyen (2025)** — *An Elastic Clustering Framework for Large-Scale WSNs Maximizing Network Lifetime* (PECEE.pdf, bản local của bạn).
   → Cần: định nghĩa CL/CGW/CFT, bán kính cell, lịch màu, overhead — để `cell-grid`/`inter-cell-routing` bám đúng PECEE gốc.
6. (nếu có) **Bài baseline SAR/semantic-fragment của bạn** — nguồn của 416×416, p=0.90, ngưỡng 0.75/0.30.

> Bạn tải được cái nào cứ đưa vào repo (vd `uav-sar/reference/papers/`) hoặc dán abstract; tôi sẽ cập nhật các ô `[Lit?]` thành `[Lit✓]` và ghi số trang.

---

## G. Claim ↔ paper (để biện luận trong báo cáo)

| Claim trong thiết kế | Paper hỗ trợ |
|---|---|
| A2G nhiều LoS, suy hao thấp hơn G2G | 3GPP 36.777; Khawaja 2019; Al-Hourani 2014 |
| Độ cao ảnh hưởng LoS/coverage (chọn độ cao) | Al-Hourani 2014 |
| Năng lượng bay phụ thuộc tốc độ (U-shaped) | Zeng-Xu-Zhang 2019 |
| Tán cây gây suy hao/shadowing lớn (rừng) | ITU-R P.833; Khawaja 2019 |
| Cell overlay + CL/CGW kéo dài lifetime, giảm overhead | PECEE (Le et al. 2025) |
| Cue nhỏ nhận diện cao → khoanh vùng nhanh; giao data có chủ đích | **đóng góp mới của bạn** (không có sẵn) |

---

**Sources (public):** Al-Hourani 2014 (IEEE WCL, DOI 10.1109/LWC.2014.2342736);
3GPP TR 36.777; Zeng-Xu-Zhang 2019 (IEEE TWC, DOI 10.1109/TWC.2019.2902559);
Khawaja 2019 (IEEE COMST, DOI 10.1109/COMST.2019.2915069); ITU-R P.833-10;
IEEE 802.15.4 standard; CC2420/CC2650 datasheets.
