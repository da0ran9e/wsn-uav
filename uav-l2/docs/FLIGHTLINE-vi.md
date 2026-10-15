# Chọn đường bay qua mỗi cluster (FlightLine)

Lời gốc: CLAUDE.md §8 mục 82. Ý tưởng gốc: mục 12, 13, 41, 44 (ý 4) và 64.
Mã nguồn: `uav-l2/tools/mission.py` (`bearings`, bước deploy) và `uav-coop/examples/coop-deploy.cc` (`AssignRoles`, `onRay`, `HeadingOk`, `LeadOutside`, `PlanPath`).

## 1. Mã giả ngắn (bản conference)

```
Algorithm 1  FlightLine(Cluster, ρ)
  CH ← strongest node at least Margin from the edge of Cluster
  for each bearing θ ∈ {0°, 2°, …, 178°}:
      Len(θ) ← length of the line through CH at θ that lies inside Cluster
  for θ in order of decreasing Len(θ):
      Entry, Exit ← farthest points of that line still in Cluster, one on each side of CH
      Path ← Dubins(Entry → CH → Exit, turn radius ρ)
      if Path crosses the edge and its leads stay outside Cluster: return Path
```

## 2. Mã giả đầy đủ

```
Algorithm 2  FlightLine(Cells, Nodes, ρ)        // Cells: the cluster's hexagons; ρ: minimum turn radius
  // 1. CH, kept away from the edge (mục 13); a thin cluster relaxes the margin
  for Margin in (300, 200, 100, 0) m:
      CH ← argmax Strength(n) over n ∈ Nodes with EdgeDist(n) ≥ Margin
      if CH exists: break

  // 2. Score every direction by its length inside the cluster
  for θ in 0°, 2°, …, 178°:                     // θ and θ+180° are the same line
      u ← (cos θ, sin θ)
      for side in (+1, −1):
          Far[side] ← max { s ∈ {0, 5, …, 8000} m : CellAt(CH + side·s·u) ∈ Cells }
      Len(θ) ← 5 m · #{ s ∈ [−Far[−1], Far[+1]] step 5 m : CellAt(CH + s·u) ∈ Cells }
                                                 // lakes, gaps, other clusters' cells do not count

  // 3. Longest first; take the first line on which a flyable path exists
  for θ in order of decreasing Len(θ):
      Entry ← last crossing of the cluster edge on the ray from CH at θ + 180°
      Exit  ← last crossing of the cluster edge on the ray from CH at θ
      Allowed(Entry) ← headings h with  h · InwardNormal(edge at Entry) > 0
                                     and  segment [Entry − ρ·h, Entry] outside Cells
      Allowed(Exit)  ← headings h with  h · InwardNormal(edge at Exit) < 0
                                     and  segment [Exit, Exit + ρ·h] outside Cells
      Path ← shortest Dubins path Entry → CH → Exit, turn radius ρ, end headings in Allowed
      if Path ≠ ∅: return (θ, Entry, Exit, Path)
  fail
```

Ghi chú:
- Entry và Exit lấy điểm xa nhất còn trong cluster, nên UAV vẫn bay qua hồ và qua cell của cluster khác nằm giữa hai điểm đó. Những vùng này là vật cản mềm.
- Trong lần deploy đầu (khi chưa có hướng, chỉ để tìm CH), entry được bốc ngẫu nhiên trên biên. Nếu không có đường Dubins khả thi, chương trình bốc lại điểm khác (`--pick` 0–9).

## 3. Ý tưởng gốc và phần tôi thêm

**Ý tưởng gốc (của anh/chị):**
- Mục 12: đường bay mở, đi từ ngoài vào, xuyên qua cluster: một đường Dubins qua 2 điểm biên và CH.
- Mục 13: CH không được nằm quá gần biên. Từ đây có ngưỡng 300 m.
- Mục 41 và 44 (ý 4): trước mắt chỉ xét đường bay tương đối thẳng và đẹp; đường cong để sau.
- Mục 64: với cluster vàng (C3), bay xuyên qua chỗ gần khoảng trống thì River dài hơn.

**Phần tôi thêm:**
- Biến nhận xét ở mục 64 thành một tiêu chí chọn tự động cho mọi cluster: trong các đường thẳng qua CH, chọn đường có đoạn nằm trong cluster dài nhất.
- Lý do chọn tiêu chí này:
  - UAV phát 1 gói mỗi 0,5 m, nên độ dài trong cluster quyết định lượng dữ liệu D. Trên C3, đổi sang đường dài nhất làm D tăng 88 %.
  - Axe dài hơn thì River dài hơn, và nhiều critical cell nằm gần nó hơn.
  - CH luôn là critical cell và nằm ngay trên đường bay.
- Cách tìm: quét rời rạc hướng 2°, lấy mẫu 5 m. Không giải bài toán hình học chính xác.
- Thêm các bước dự phòng để luôn có đường bay được: hạ ngưỡng CH, bốc lại entry, lấy hướng dài kế tiếp.

**Các khái niệm kinh điển gần với cách này (cần kiểm tra trích dẫn trước khi đưa vào paper):**
- Đường Dubins (Dubins 1957).
- Dây cung dài nhất qua một điểm, và bề rộng của đa giác.
- Chọn hướng quét theo bề rộng đa giác trong coverage path planning (ví dụ Huang 2001). Ở đó bài toán là chọn hướng quét luống cho ít lượt rẽ nhất. Ở đây chỉ có một đường, buộc phải qua CH, và mục tiêu là độ dài trong miền.

## 4. Các bước dự phòng đã dùng bao nhiêu lần

Kiểm tra trên toàn bộ 200 cluster (4 bản đồ gốc và 36 bản đồ chiến dịch):

| Bước dự phòng | Số cluster |
|---|---|
| Ngưỡng CH 300 m | 186 |
| Ngưỡng CH hạ xuống 200 m | 14 |
| Ngưỡng CH 100 m hoặc 0 m | 0 |
| Phải lấy hướng dài kế tiếp | 0 |
| Bốc lại entry ở lần deploy đầu | có, ở k8/C4 |

Hướng dài nhất luôn bay được, nên trên các bản đồ hiện tại, bước "lấy hướng dài kế tiếp" chỉ là lưới an toàn.

## 5. Giới hạn

- Chỉ xét đường thẳng qua CH. Đường cong (mục 44, ý 4) và nhiều lượt bay chưa xét.
- Tiêu chí chỉ tối đa hoá D của từng cluster. Nó không xét thời gian của cả tour đội 1; thứ tự tour được tối ưu riêng (Held–Karp, `MISSION-vi.md`).
- Quét 2° và lấy mẫu 5 m là xấp xỉ. Độ dài thật có thể lệch vài chục mét.
