# Tầng 2 — bước 1: bản đồ nhiều cluster

Lời gốc: CLAUDE.md §8 mục 56.

![steps](figures/map-steps.png)

## Cách sinh

Mỗi cluster được tạo **đúng như một cluster của `uav-coop`** (`models/common/region.cc`,
`deploy.h`), chỉ khác là nhiều cluster cùng nằm trên một bản đồ rộng:

1. **Bản đồ:** lưới lục giác R = 100 m (rộng cell 173 m), là một đĩa bán kính `--mapRadius` cell. Mặc định 22 cell, rộng khoảng 8 km.
2. **Hạt giống:** mỗi cluster bốc một cell đều trong đĩa, cách các hạt khác ≥ `--seedGap` cell (12).
3. **Mọc Eden** tới `--cells` cell (60, như `uav-coop`): mỗi bước thêm một cell bốc đều từ biên. Một cell không bao giờ được lấy nếu nó nằm ngoài bản đồ hoặc gần cell của cluster khác dưới `--gap` cell (3).
4. **Lấp chỗ lõm** tới độ lồi `--convexity` (1): lấp ô lõm bị bao nhiều nhất trước, hoà thì bốc ngẫu nhiên. Ô nào vi phạm khoảng cách với cluster khác thì bỏ qua, nên độ lồi có thể dừng dưới mục tiêu.
5. **Node:** round(diện tích / spacing²) node (spacing 35 m), đặt đều trong cluster. Mỗi node có obs, cpu ~ U[0,1) và comm ~ U(0,1].
   - CH là node mạnh nhất (tích obs·cpu·comm) trong số các node cách biên ≥ 300 m.
   - CL là node mạnh nhất của mỗi cell.

Các cluster mọc lần lượt. Nếu một cluster không đủ chỗ mọc, toàn bộ hạt giống được bốc lại.
Bộ sinh số ngẫu nhiên là của Python, nên cùng `--seed` không cho đúng cluster như bản C++ của
`uav-coop`; chỉ thuật toán là giống.

## Bản đồ seed 1 (`docs/data/map-s1-*.csv`)

| Cluster | Cell (mọc → sau khi lấp) | Diện tích | Độ lồi | Node |
|---|---|---|---|---|
| C1 | 60 → 89 | 2,31 km² | 0,67 → 1,00 | 1 888 |
| C2 | 60 → 89 | 2,31 km² | 0,67 → 1,00 | 1 888 |
| C3 | 60 → 93 | 2,42 km² | 0,65 → 1,00 | 1 972 |
| C4 | 60 → 87 | 2,26 km² | 0,68 → 0,99 (1 ô lõm bị khoảng cách chặn) | 1 845 |
| C5 | 60 → 86 | 2,23 km² | 0,70 → 1,00 | 1 824 |

- Tổng cộng 9 417 node, khoảng 11,5 km² có node, trên một bản đồ rộng khoảng 8 km.
- Các cluster sát nhau nhất (C1–C4, C1–C5, C3–C5) có tâm cell gần nhất cách nhau 458 m, tức khoảng 280 m đất trống giữa hai biên.
- Xa nhất là C1–C3: 2,7 km.
- Khoảng cách CH–CH từ 1,9 km (C1–C4) tới 4,9 km (C1–C3).

**Miền phải bay qua vì thế không lồi:** gồm 5 vùng lồi rời nhau, xen giữa là đất trống không
có node. Vật cản (vùng cấm bay, vùng che khuất, §8 mục 38) chưa được đưa vào.

Chạy lại:
```
python3 tools/map_gen.py --seed 1 --clusters 5 --out docs/data/map-s1 --figs docs/figures
```
