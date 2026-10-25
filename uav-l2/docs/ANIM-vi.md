# Các animation (không chữ trên bản đồ)

Lời gốc: CLAUDE.md §8 mục 71, 86, 87, 105.

| Animation | Nội dung | File, công cụ | Bản đăng |
|---|---|---|---|
| **P: trọn nhiệm vụ** | Bản đồ 4 cluster, 10 bước: sinh miền, hồ, node, chia cluster, vai trò, quét hướng, tour đội 1, kế hoạch River, rồi cả nhiệm vụ (lượt phát, River trên ns-3, đối sánh, LoRa, đội 2) | `anim/mission-replay.html`, `tools/mission_anim.py` | https://claude.ai/artifact/Sd79Xy3LuP27wuNn38nTg6 |
| **P + lớp 2 (LANE)** | Bản đồ 8 cluster: quét hướng, luồng, mảnh vụn, cắt, đường bay, tour quét luống; sau đó cách chia k-medoids để so sánh. **Chỉ có phần hình học**, chưa có River trên ns-3 cho các cluster LANE (chờ duyệt chạy) | `anim/lane-replay.html`, `tools/restructure_anim.py` | https://claude.ai/artifact/UGFp5srtMjxJFMzwuQFNNY |
| **So sánh phương án** | Cùng bản đồ 4 cluster và cùng lượt bốc nghi vấn với P. Các phương án: P; ablation chính sách (tour ngắn nhất, đội 2 chờ đủ báo cáo, thứ tự TSP); ablation lớp 3 (kéo thẳng, Circle cố định 12); baseline B4-0,9, B1, B2-300/500, B3-300/500, B6, B7. Mọi phương án dùng chung một trục thời gian | `anim/compare-replay.html`, `tools/compare_anim.py` | https://claude.ai/artifact/XHjD6X7ssHFeDn7c2Z4vrf |
| **MEANDER: trọn nhiệm vụ** | Cùng bản đồ 4 cluster với P (k4-s2), chia cụm bằng MEANDER. 13 bước dựng (miền, xương sống, toạ độ s và n, luồng, mảnh, cluster, vai trò, đường cong uốn qua CH, tour, kế hoạch River) rồi cả nhiệm vụ trên ns-3 với đội 1 bay theo đường cong | `anim/meander-replay.html`, `tools/meander_anim.py` | https://claude.ai/artifact/43DQcbhZfmQ46iKFbiwDsZ |
| **CHORD (P\*) trên 8, 12, 16 cụm** (mục 164) | Bản đồ k8-s1, k12-s1, k16-s1 (8, 12, 15 cụm). Các bước dựng, rồi cả nhiệm vụ: đội 1 bay đúng quỹ đạo CHORD-T (nối Dubins, hồ sơ vận tốc), lượt phát ns-3, River ns-3 có vết, đối sánh, LoRa, đội 2. Lượt bốc gần trung vị T\* | `anim/chord-k8-s1-replay.html`, `chord-k12-s1-replay.html`, `chord-k16-s1-replay.html`; `tools/l1_anim.py --html` | chưa đăng |
| **CHORD, FC, DN cạnh nhau** (mục 168) | Bản đồ k8-s1, lượt bốc lớp 1 số 38 (gần trung vị T\* của cả ba phương án ở cả bốn kênh). Ba bản đồ chạy chung một đồng hồ, chọn kênh open / r500 / r200 / r100. Mỗi bản đồ: quỹ đạo đội 1 đúng như đã bay (CHORD: đường qua CH; FC: lượn quanh từng critical cell; DN: quỹ đạo vòng quanh nhóm, vòng nét đứt). Critical cell đậm dần theo phần dữ liệu CL đã có; viền xanh khi sẵn sàng, chấm đen khi báo cáo tới BS, viền đỏ khi đội 2 xác minh xong; sao vàng là c\*, tô kín khi xác minh. Đội 2 là chấm đỏ. Dải thời gian bên dưới, mỗi phương án một hàng: thanh xám là đội 1 còn bay, đường bậc là số critical cell đã sẵn sàng, vạch đỏ là các lần xác minh, vạch vàng là T\* | `anim/cmp3-k8-s1-replay.html` (+ `cmp3-k8-s1.json`), `tools/cmp3_anim.py --html`; khung `figures/cmp3-k8-s1-r200-mid-frame.png` | https://claude.ai/artifact/L1Fv5Yq8NVPtVYbUyrDhkh |

**Kết thúc nhiệm vụ trên lượt bốc của trang so sánh** (một lượt, chỉ để minh hoạ, không phải số thống kê):

| P | P·short | P·wait | P·tsp | L3·direct | L3·circle12 | B4·0,9 | B1 | B2·300 | B2·500 | B3·300 | B3·500 | B6 | B7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 952 s | 971 | 1 109 | 952 | 952 | 952 | thất bại (1 004) | 2 276 | 2 548 | 1 883 | 2 011 | 1 691 | 1 931 | 671 |

**Ghi chú:**
- Kéo thẳng và Circle 12 cho cùng thời điểm kết thúc với P trên lượt này. Phần chênh của River (vài giây đến vài chục giây) bị nuốt vào khe LoRa 40 s.
- B4 thất bại vì cell thật chỉ giữ dưới 90 % của D. Ngưỡng này là số tạm (xem `L1-PARAMS-vi.md`, câu S1).
- Thời gian xác minh mỗi lần thăm là khoảng 83 s (tệp 1 MiB), theo `mission_baselines.py`.

## MEANDER: từng bước (`anim/meander-replay.html`, mục 104–105)

Bản đồ k4-s2, đúng bản đồ của animation P ở trên; mở hai trang cạnh nhau để so.
Dữ liệu lấy từ lần chạy ns-3 ở `logs/2026-10-20_0222-meander-ns3/`. River được chạy lại có `--trace`, kết quả trùng từng critical cell (`logs/2026-10-20_0314-meander-anim/`).
Hình tĩnh 18 khung, một khung mỗi bước, đọc trái → phải, trên → dưới: `figures/meander-anim-steps.png`.
Thanh bước dưới bản đồ: 13 ô bằng nhau cho phần dựng, ô dài cuối là cả nhiệm vụ. Nút ◀ ▶ nhảy bước, thanh trượt đổi tốc độ.

| # | Bước | Cơ chế | Trên bản đồ (không chữ) |
|---|---|---|---|
| 1 | Mọc miền | `map_gen`: 320 cell mọc ngẫu nhiên từ gốc, R = 100 m | cell xám hiện dần |
| 2 | Lấp lõm | thêm 28 cell vào các vịnh hẹp (độ lồi) | cell lấp hơi đậm hơn |
| 3 | Hồ | 4 hồ, 40 cell; miền còn 308 cell đất | cell xanh nước, viền xanh |
| 4 | Node | 6 532 node, một node mỗi ô 35 m × 35 m, năng lực ngẫu nhiên | chấm xám |
| 5 | Xương sống và toạ độ dọc s | Dijkstra trên cell đất (hồ là lỗ): từ một cell tới cell xa nhất A, từ A tới xa nhất B; đường ngắn nhất A → B là xương sống (34 cell, khoảng 5,7 km). s = (d_A − d_B)/2 chạy từ −2,9 đến +2,9 km và uốn theo miền, vòng qua hồ | xương sống vẽ dần từ A; hai chấm đen là A, B; cell tô xanh nhạt → đậm theo s, lan dọc xương sống |
| 6 | Toạ độ ngang n | khoảng cách trắc địa có dấu tới xương sống (Dijkstra nhiều nguồn; bên trái hay phải đặt ở chỗ sóng rời xương sống), từ −1,3 đến +2,5 km | lan từ xương sống ra hai phía: xanh một phía, vàng cam phía kia, xám đậm trên xương sống |
| 7 | Luồng | cắt n thành dải rộng 4,5 cell (779 m), thử 3 độ lệch, chọn cách ít cluster và mảnh vụn nhất: 6 luồng | hai sắc xanh xen kẽ, hiện từng luồng |
| 8 | Mảnh và mảnh vụn | mỗi luồng tách thành mảnh liền (hồ cắt luồng): 10 mảnh. Mảnh nhỏ hơn 1/4 trần (20 cell) là mảnh vụn, nhập vào mảnh kề chung nhiều cạnh nhất (21 cell) | mỗi mảnh một màu; cell gạch chéo nhấp nháy là mảnh vụn bị nhập |
| 9 | Cắt thành cluster | mảnh lớn hơn trần 80 cell cắt thành khúc đều theo s: 6 cluster gồm 78, 67, 67, 37, 37, 22 cell | màu cluster lan theo s trong từng cluster, viền đen hiện dần |
| 10 | Vai trò | `uav-coop-deploy` mỗi cluster: CL mạnh nhất mỗi cell, CH mạnh nhất cách biên ≥ 300 m (4 cluster) hoặc ≥ 100 m (2 cluster mỏng), tuyến và gateway; 26 critical cell | chấm đen nhỏ là CL, vòng trắng là critical cell, sao là CH |
| 11 | Đường cong qua CH | (a) đường tâm luồng: trung bình tâm cell theo từng nửa cell của s, trung bình trượt 7 bin, làm trơn tới bán kính ≥ ρ = 255 m. (b) vector v từ điểm gần nhất tới CH (35–370 m). (c) đẩy bướu Gauss v·exp(−Δs²/2σ²), σ = √(2·|v|·ρ), giữ CH và hai đầu, làm trơn lại tới ≤ 1/ρ (σ ×1 đủ cho cả 6 cluster). (d) thêm đoạn vào và ra thẳng dài ρ. Đường dài 1,1–3,3 km | nét đứt là đường tâm luồng; mũi tên màu cluster là v; đường biến hình từ nét đứt sang nét liền; cuối bước hiện đoạn vào, ra |
| 12 | Tour đội 1 | l3first (`mission_policy`): Held-Karp chính xác theo thời điểm mọi critical cell xong, chuyển tiếp thẳng; thứ tự C4, C1, C2, C3, C5, C6, về BS ở 483 s | nét đứt xám là chuyển tiếp; nét đen có mũi tên là đường cong theo chiều bay |
| 13 | Kế hoạch River | `river_plan` với Bank cục bộ: Axe là cell dưới đường bay (8–24 mỗi cluster), Bank trên pháp tuyến cục bộ ±1,75 cell, River 16–74 cell, Circle cho mỗi critical cell; một cell bị đi qua hai lần giữ lượt dài nhất | xanh đậm là Axe, xanh lá là Bank, xanh nhạt là River; lục giác viền màu nối về critical cell là thành viên Circle |
| 14 | Cả nhiệm vụ | xem dưới | |

**Bước 14, cả nhiệm vụ** (thời gian chậm lại khi UAV ở trên cluster và khi River chạy; vạch dọc trên dải thời gian là "bây giờ"):
- **Lượt phát (ns-3 `uav-coop-pass`).** Đội 1 (tam giác đen) bay theo đường cong, phát một gói mỗi 0,5 m (vòng sóng xanh). Mỗi cell đậm dần theo phần D mà các node trong cell đã nhận. D mỗi cluster là 2 277–6 836 gói.
- **River (ns-3 `uav-coop2-river`, 802.15.4, 7 màu, trace từng chặng).** Bắt đầu khi UAV rời cluster. Màu đường nối giữa hai cell là pha truyền:
  - xanh: gom về CL trong cell;
  - lục: Axe đổ ra Bank;
  - vàng: Bank lấp Circle;
  - đỏ: critical cell kéo phần còn thiếu;
  - xám: điều khiển.

  Vòng quanh critical cell là phần D đang giữ, chuyển đen khi đủ. Cluster nhanh nhất xong sau 1,6 s (C6, Axe 8 cell); C4 (Axe 24, D 6 836) mất 115 s, vì vậy C4 được bay trước.
- **Đối sánh.** Quầng tím nhấp nháy 5 s tại critical cell. Vạch tím tới CH là báo kết quả, 0,1 s mỗi cell.
- **LoRa.** Cung tím quanh CH là đồng hồ chu kỳ 40 s. Mỗi bản tin (chấm tím) chạy từ CH về BS, mất 0,4 s; một bản tin mang mọi kết quả đã có ở CH.
- **Nghi vấn và đội 2.** Lượt bốc này có 3 nghi vấn:

  | Nghi vấn | Cluster | Điểm | Tới BS lúc |
  |---|---|---|---|
  | giả | C5 | 0,56 | 429 s |
  | giả | C3 | 0,55 | 462 s |
  | thật | C3 | 0,74 | 462 s |

  Hình tròn cam ở BS là nghi vấn đã biết; to hơn là điểm cao hơn. Đội 2 (chấm đỏ, 15 m/s) cất cánh ngay khi có báo cáo đầu tiên (429 s). Nó tới C5 lúc 634 s và hover 30 s (vòng đỏ); nghi vấn hoá xám. Sau đó nó chọn nghi vấn thật của C3 theo điểm / thời gian bay, tới lúc 740 s; nghi vấn hoá đỏ. Đội 2 về BS lúc **1 050 s** thì nhiệm vụ kết thúc. Đây là một lượt minh hoạ; số trung bình 100 lượt là 867 s (CURVE-vi.md Phần 3).
- **Dải thời gian:**
  - hàng trên: đội 1 cả chuyến;
  - mỗi hàng giữa là một cluster theo thứ tự bay: xanh là bay qua, lục là River, vạch tím là khe LoRa gửi, chấm là nghi vấn tới BS (đỏ thật, cam giả);
  - hàng dưới: đội 2 (đỏ nhạt là bay, đen là hover).

