# Tái cấu trúc cluster trước nhiệm vụ: chia theo luồng (LANE)

Lời gốc: CLAUDE.md §8 mục 84. Mã: `uav-l2/tools/restructure.py`. Hook vào giả lập trọn nhiệm vụ: `mission.py --partition=lane --lane 4.5` (đã cài, **chưa chạy ns-3**).

## 1. Ý tưởng

Pha 0 hiện tại (`partition.py`) chia miền bằng k-medoids có chặn trên 80 cell. Cluster ra tròn và đặc. Đường bay của mỗi cluster chỉ là một dây cung qua CH, nên phần lớn cell nằm xa đường bay, ngoài River.

LANE làm ngược lại: **chọn đường bay trước, rồi cắt cluster theo đường bay**.
- Miền được cắt thành các luồng song song, mỗi luồng rộng cỡ River. Mỗi luồng lại được cắt dọc thành các cluster ≤ 80 cell.
- Cluster nhờ vậy dài và hẹp, đường bay đi dọc cluster, nên gần như mọi cell nằm trong River.
- Các đường bay của những cluster liên tiếp nối nhau thành một tour quét luống. Thứ tự ghé thăm được biết trước khi chia cluster, nên có thể chọn theo yêu cầu.
- Hướng luồng được chọn theo địa hình: hướng nào ít bị hồ và vịnh cắt vụn nhất.

## 2. Mã giả ngắn

```
Algorithm LANE(Land, Cap, LaneWidth, Policy)
  θ, offset ← direction whose parallel lanes (LaneWidth wide) cut Land into the fewest clusters and fragments
  Pieces ← connected land pieces of each lane;  merge every fragment (< Cap/4) into the piece it touches most
  Clusters ← cut each piece along θ into ⌈|piece| / Cap⌉ equal chunks
  Order ← boustrophedon over lanes, choosing first lane and direction by Policy
  each cluster flies along θ through its CH
```

## 3. Mã giả đầy đủ

```
Algorithm LANE(Land, Cap, L, Policy)                      // L: lane width in cells; River = 3.5 cells
  // 1. direction and offset, by terrain
  for θ in 0°, 2°, …, 178°;  offset in {0, 1/3, 2/3}:
      Lane(h) ← ⌊ (centre(h) · n_θ − min) / (L·W) + offset ⌋        // n_θ: normal to θ
      Pieces ← connected components of each lane (lakes and bays split a lane)
      Cost(θ, offset) ← Σ_pieces ⌈|piece| / Cap⌉ + #{pieces with |piece| < Cap/4}
  keep the cheapest (ties: fewer lanes, then smaller θ)

  // 2. no slivers
  while some piece P has |P| < Cap/4 and touches another piece:
      merge the smallest such P into the touching piece with the longest shared border

  // 3. cut along the lane
  for each piece P:
      sort its cells by position along θ;  cut into m = ⌈|P| / Cap⌉ consecutive chunks of equal size
      a chunk in several parts keeps its largest; the other parts join the touching chunk of P
        with room (≤ Cap) and the longest shared border

  // 4. visit order, known before the mission
  for (first lane ∈ {lowest, highest}) × (first direction ∈ {+θ, −θ}):
      Tour ← lanes in turn, clusters along each lane in turn, direction alternating
  keep the tour that minimises
      short : tour length
      big   : Σ |cells_k| · t_enter(k)          dense : Σ nodes_k · t_enter(k)
      weak  : Σ (1 − mean capability_k) · t_enter(k)        (weights normalised to mean 1)
  flight line of each cluster: straight along θ through its CH (Dubins entry/exit as before)
```

## 4. Hình (không chữ)

Animation toàn bộ các bước, trên bản đồ 8 cluster, không chữ: `anim/lane-replay.html` (tạo bởi `tools/restructure_anim.py`; bản đăng: https://claude.ai/artifact/UGFp5srtMjxJFMzwuQFNNY).


| File | Nội dung |
|---|---|
| `figures/restructure-k4-s2-steps.png`, `…-k8-s4-steps.png` | 6 bước, đọc trái → phải, trên → dưới. (1) Miền, hồ (gạch chéo), node, BS (ô vuông). (2) Quét hướng: bán kính càng dài thì cách cắt càng ít mảnh; chấm đỏ là hướng được chọn. (3) Các luồng ở hướng đã chọn, tô xen kẽ hai sắc. (4) Các mảnh luồng trước khi gộp; mảnh vụn có gạch chéo đen. (5) Cluster LANE: màu đậm là ghé trước, mũi tên đậm là bay trong cluster, mũi tên đứt là bay chuyển tiếp, sao là CH. (6) Cluster k-medoids hiện tại với dây cung dài nhất và tour Held–Karp, cùng cách tô |
| `figures/restructure-k4-s2-river.png`, `…-k8-s4-river.png` | Cell trong River (xanh đậm, cách đường bay ≤ ω = 1,75 cell) và ngoài River (xanh nhạt). Trái là LANE, phải là k-medoids; đường đỏ là đường bay |
| `figures/restructure-k4-s2-policy.png`, `…-k8-s4-policy.png` | Cùng các cluster LANE, sắp thứ tự theo 4 chính sách: short / big / dense / weak (đậm = ghé trước) |

## 5. Số liệu: 40 bản đồ của chiến dịch nhiệm vụ, chỉ tính hình học

Đây là số tính hình học, chưa phải số đo ns-3.
- CH dùng một đại diện thay thế (CH proxy): cell xa biên cluster nhất.
- D = 2 gói mỗi mét bay trong cluster.
- "Phủ River" = tỉ lệ cell cách đường bay ≤ ω.
- Bảng dưới là trung bình trên 40 bản đồ; dữ liệu gốc ở `data/restructure/restructure-maps.csv`.

| | k-medoids (hiện tại) | LANE 3,5 | **LANE 4,5** | LANE 6 |
|---|---|---|---|---|
| Số cluster | 5,0 | 7,9 | 7,5 | 6,6 |
| Cluster nhỏ nhất, cell | 66,5 | 28,4 | 29,5 | 36,2 |
| D trung bình / nhỏ nhất, gói | 4251 / 3783 | 4167 / 2373 | 3560 / 2219 | 3407 / 2299 |
| **Phủ River** | **54 %** | 87 % | **80 %** | 67 % |
| **Cell xa đường bay nhất**, cell | **7,0** | 4,3 | **4,1** | 4,3 |
| Bay trong cluster, km | 10,5 | 16,3 | 13,6 | 11,3 |
| Bay chuyển tiếp, km (thứ tự luống) | 7,9 | 10,9 | 10,8 | 10,1 |
| Bay chuyển tiếp, km (Held–Karp trên cùng cluster) | 7,9 | 9,0* | 9,9 | 9,3 |
| Tổng góc rẽ, độ | 879 | 1267 | 1209 | 1083 |

\* Chỉ 32/40 bản đồ: Held–Karp bị bỏ qua khi có quá 12 cluster.

**So từng cặp, LANE 4,5 với k-medoids trên cùng bản đồ:**
- Phủ River tốt hơn ở 40/40 bản đồ.
- Cell xa nhất gần đường bay hơn ở 37/40.
- Tổng quãng bay ngắn hơn hoặc bằng ở 0/40 với thứ tự luống, và 1/40 với Held–Karp.

**Đọc bảng:**
- **LANE mua được gì:**
  - 80 % cell nằm trong River, so với 54 %.
  - Cell xa nhất cách đường bay khoảng 4 cell, so với 7. Critical cell nằm ngoài River ít hơn, Circle có ít đường dài hơn.
  - Tổng dữ liệu phát xuống tăng khoảng 29 %, vì bay trong miền nhiều hơn (13,6 so với 10,5 km).
- **LANE trả giá gì:**
  - Đội 1 bay thêm khoảng 6 km. Tổng 24,4 so với 18,4 km, tức khoảng +120 s ở 50 m/s.
  - Số cluster tăng khoảng 50 %, kéo theo nhiều CH, nhiều báo cáo LoRa hơn.
  - Cluster nhỏ nhất chỉ còn khoảng 30 cell, nhận D nhỏ nhất khoảng 2200 gói, so với 3800.
- **Chọn bề rộng luồng:**
  - 3,5 cell (đúng bằng River) phủ tốt nhất, nhưng sinh nhiều cluster và bay nhiều nhất.
  - 6 cell gần lại với k-medoids.
  - 4,5 là điểm giữa.
- **Thứ tự luống so với Held–Karp:** tour theo luống dài hơn Held–Karp khoảng 1 km. Đó là cái giá của việc cố định thứ tự trước nhiệm vụ.

## 6. Giới hạn hiện tại

- CH là đại diện hình học, chưa phải CH thật của `uav-coop-deploy` (node mạnh nhất cách biên ≥ 300 m). Cluster hẹp khoảng 4,5 cell có tâm cách biên chỉ khoảng 390 m, nên ngưỡng 300 m có thể phải hạ.
- Chính sách thứ tự chỉ chọn trong 4 tour luống, nên big / dense / weak thường cho cùng một thứ tự. Muốn "cluster to ghé trước, nhỏ ghé sau" thật sự, phải cắt mỗi luồng thành các khúc có kích thước giảm dần theo thứ tự ghé. Việc này chưa cài.
- Chỉ một hướng θ cho cả miền. Miền cong (chữ C, chữ S) có lẽ cần chia vùng, mỗi vùng một hướng.
- Chưa tính bán kính rẽ của cánh bằng khi nối hai luồng: luồng cách 780 m, gấp hơn 2ρ = 510 m, nên vòng chữ U bay được. Chưa tính phần đường bay thêm của vòng rẽ.
- Chưa có số ns-3: chưa biết thời gian lớp 3 giảm bao nhiêu, và có bù được khoảng +120 s bay thêm hay không.

## 7. Đề xuất chạy ns-3 (chờ anh/chị duyệt)

- **Lệnh:** `mission.py --partition=lane --lane 4.5 --schemes rf` trên 4 bản đồ gốc (k2-s3, k4-s2, k6-s4, k8-s4).
- **Đầu ra:** pass + River, rồi `mission_policy` / `mission_report` để so thời điểm kết thúc nhiệm vụ với P (k-medoids) đã có.
- **Thời gian:** khoảng 7 / 11 cluster cho k4 / k8, ước lượng 1–2 giờ máy với 3 luồng.
- **Lưu ý:** đây là số thăm dò một lượt. Muốn công bố thì cần N ≥ 120.
