# Vì sao lớp 2 đề xuất (MEANDER) chưa thắng cluster có sẵn

Lời gốc: CLAUDE.md §8 mục 115. Kết quả cấp nhiệm vụ: `L1-MISSION2-vi.md` §5.5.
Mã: `tools/l2_diag.py` (đo trên các lần chạy ns‑3 đã có), `tools/l2_lanes.py` (chỉ hình học, quét độ rộng luồng).
Log: `logs/2026-10-21_0010-l2-diag/`. Dữ liệu: `data/l2diag/diag-maps.csv`, `data/l2diag/lanes.csv`.

Không chạy ns‑3 mới. Mọi số dưới đây lấy trên đúng 40 bản đồ của E2, theo cỡ k2 / k4 / k6 / k8 (trung bình 10 bản đồ mỗi cỡ).

## 1. Số lượng cluster

| | k‑medoids (có sẵn) | MEANDER | subCH |
|---|---|---|---|
| cluster | 2 / 4 / 6 / 8 | 3,3 / 6,2 / 9,0 / 12,1 | 2,7 / 6,4 / 8,3 / 11,5 |
| critical cell | 13,5 / 26,9 / 39,9 / 50,1 | 16,5 / 30,6 / 47,3 / 59,0 | 12,2 / 25,0 / 37,4 / 46,7 |

MEANDER tạo nhiều hơn 50–65 % cluster. Có ba lý do:
- Luồng rộng 4,5 cell bị hồ cắt thành nhiều mảnh.
- Mỗi mảnh lại bị chặt thành cluster ≤ 80 cell.
- Mảnh vụn được gộp sang mảnh bên cạnh.

Mỗi cluster thêm một CH, nên số critical cell tăng 3–9 trên mỗi bản đồ. Đội 2 vì thế phải chọn giữa nhiều ứng viên hơn (mục 5.5 của báo cáo nhiệm vụ: hạng của c\* 2,19–2,58 so với 1,93–2,37).

## 2. Đường bay (tour độ trễ của đội 1, như P\*, giây ở 50 m/s)

| | k‑medoids | MEANDER | subCH |
|---|---|---|---|
| bay trong cluster (gồm đường vào/ra) | 111 / 224 / 321 / 426 | 166 / 341 / 481 / 646 | 127 / 276 / 377 / 509 |
| bay nối giữa cluster và từ BS | 45 / 86 / 122 / 183 | 67 / 122 / 179 / 220 | 66 / 134 / 180 / 222 |
| bay về BS | 57 / 59 / 70 / 73 | 53 / 66 / 78 / 85 | 40 / 70 / 75 / 76 |
| **tổng (về tới BS)** | **213 / 369 / 512 / 682** | **285 / 529 / 738 / 950** | 232 / 480 / 632 / 807 |

- **Phần lớn chênh lệch nằm ở bay trong cluster: +50 %.** MEANDER phủ kín miền bằng các luồng cách nhau 780 m. Còn k‑medoids chỉ bay một đường thẳng dài nhất qua CH của mỗi cluster.
- Tỉ lệ cell nằm trong dải River (±1,75 cell quanh đường bay) cho thấy điều đó: MEANDER 76–82 %, k‑medoids chỉ 54 %. Phần còn lại của k‑medoids do River và Circle lo, và chỉ cần cho critical cell.
- Đường của k‑medoids không ngẫu nhiên: đó là hướng có đoạn nằm trong cluster dài nhất qua CH (`FLIGHTLINE-vi.md`), và tour được tối ưu (Held–Karp). Đây là một baseline mạnh.

**Quét độ rộng luồng (chỉ hình học, `l2_lanes.py`, `figures/l2-lanes.png`).** km bay = trong cluster + nối; với MEANDER chưa tính đường vào/ra, nên con số còn thấp hơn thực tế.

| Cách chia | cluster (k8) | km bay k2 / k4 / k6 / k8 | độ phủ dải River |
|---|---|---|---|
| k‑medoids | 8 | 9,5 / 15,1 / 21,5 / 27,5 | 54 % |
| MEANDER, luồng 4,5 cell (780 m) | 12,1 | 12,9 / 23,9 / 33,1 / 42,9 | 76–82 % |
| MEANDER, luồng 7,5 cell | 10,3 | 11,8 / 21,1 / 27,4 / 35,0 | 65–73 % |
| MEANDER, luồng 12 cell (2,1 km) | 9,5 | 11,4 / 19,0 / 24,3 / 34,3 | 56–72 % |

**Ngay cả khi luồng rộng tới mức độ phủ chỉ còn ngang k‑medoids, MEANDER vẫn bay dài hơn** (k8: 34,3 so với 27,5 km). Ở cùng độ phủ, quãng bay *trong* cluster đã ngang nhau (17,3 so với 16,7 km). Phần dư nằm ở quãng bay nối (17,0 so với 10,8 km), vì:
- MEANDER có nhiều cluster hơn, và mỗi cluster có đường vào/ra riêng dài 2 × 255 m.
- Thứ tự luống (boustrophedon) cố định chạy qua các luồng bị hồ cắt vụn, nên phải bay chéo nhiều lần (nét đứt trong `figures/l2-diag-k6-s4.png`).

## 3. Lượng dữ liệu thu được

| | k‑medoids | MEANDER | subCH |
|---|---|---|---|
| gói trên Axe mỗi cluster (D) | 4 270 / 4 320 / 4 120 / 4 160 | 3 980 / 4 440 / 4 340 / 4 410 | 3 540 / 3 160 / 3 370 / 3 280 |
| tổng gói cả bản đồ | 8 530 / 17 300 / 24 700 / 33 300 | 12 900 / 27 400 / 38 600 / 52 500 | 9 260 / 20 100 / 27 800 / 37 600 |
| cluster có Axe đủ cho bộ manh mối (≥ 4 036 gói, khoảng 2 km) | 55 / 63 / 50 / 55 % | 35 / 62 / 59 / 60 % | 26 / 11 / 15 / 15 % |

MEANDER thu tổng cộng nhiều hơn 51–58 % gói, vì bay nhiều hơn. Tính theo từng cluster thì ngang nhau. Tỉ lệ cluster đủ chỗ cho bộ manh mối cũng không tốt hơn; ở k2 còn kém hơn.

## 4. Độ thấm dữ liệu

| | k‑medoids | MEANDER | subCH |
|---|---|---|---|
| cell nghe ≥ 50 % D của cluster mình | 100 / 99 / 99 / 100 % | 99 / 99 / 99 / 98 % | 99 / 100 / 100 / 100 % |
| cell tự giữ đủ cả 12 manh mối (không cần River) | 13 / 14 / 10 / 11 % | 17 / 28 / 22 / 23 % | 5 / 2 / 4 / 4 % |
| trọng số manh mối TB mỗi cell tự giữ | 77 / 77 / 77 / 78 % | 74 / 79 / 77 / 78 % | 72 / 69 / 72 / 71 % |
| critical cell cuối cùng có dữ liệu River (s) | 198 / 346 / 470 / 632 | 255 / 485 / 680 / 881 | 214 / 412 / 567 / 733 |

- **Gói thô đã thấm gần hết ở mọi cách chia:** sóng A2G với tới khoảng 1 km, nên gần như mọi cell nghe được phần lớn dữ liệu của cluster mình.
- **Cái khác nhau là bản sao manh mối liền mạch:** MEANDER cho gấp đôi số cell tự giữ đủ 12 manh mối (17–28 % so với 10–14 %). Cảm quan "dữ liệu đầy đủ hơn" đúng ở điểm này.
- Nhưng trọng số manh mối trung bình mỗi cell tự giữ thì như nhau (khoảng 77 %).
- Sau River, critical cell của k‑medoids còn giữ nhiều hơn: 97 % so với 91 %. Cluster nhỏ của MEANDER có Axe ngắn.
- Vì tour dài hơn, critical cell cuối cùng của MEANDER có dữ liệu muộn hơn 57–249 s.

## 5. Kết luận

Cảm quan "đường luống nhanh hơn và dữ liệu đầy đủ hơn" đúng với bài toán **phủ**, tức khi mọi node phải tự nhận được dữ liệu. Nhiệm vụ của ta chỉ cần bộ manh mối có mặt ở **critical cell**, và River lấp phần thiếu trong vài chục giây. Với mục tiêu đó, một đường thẳng qua mỗi cluster có sẵn làm tour đội 1 ngắn hơn 25–31 %. Thêm vào đó, cách dựng MEANDER hiện tại có ba khoản hao không thuộc về ý tưởng luống:
1. **Nhiều cluster hơn** (+50–65 %): thêm đường vào/ra, thêm bay nối, thêm critical cell.
2. **Luồng bị hồ cắt vụn:** dù UAV bay qua hồ được, mỗi mảnh vẫn được bay riêng.
3. **Mỗi cluster một đoạn bay riêng:** không có một đường luống liền từ đầu tới cuối.

Vì vậy chưa thể kết luận ý tưởng luống là sai. Thứ thua là *cách hiện thực* hiện tại. Một phương án luống đúng nghĩa (một đường bay liền, bay qua hồ, cluster là các đoạn liên tiếp trên đường bay) chưa được thử.

## Hình (không chữ)
- `figures/l2-diag.png`: ba ô, mỗi ô bốn nhóm k2–k8; trong nhóm: k‑medoids (xanh dương), MEANDER (xanh lá), subCH (tím).
  - (1) Tour đội 1 xếp chồng: bay trong cluster (đậm), bay nối (vừa), bay về (nhạt).
  - (2) Độ thấm: cột nhạt là tỉ lệ cell nghe ≥ 50 % D, phần đậm là tỉ lệ cell tự giữ đủ 12 manh mối.
  - (3) Cột nhạt là số critical cell, phần đậm là số cluster.
- `figures/l2-diag-k6-s4.png`: bản đồ k6‑s4, trái sang phải: k‑medoids, MEANDER, subCH.
  - Cell tô theo phần D của cluster mà cell nghe được (nhạt đến đậm).
  - Đường bay đen liền, bay nối nét đứt, critical cell vòng trắng, BS ô vuông đen.
- `figures/l2-lanes.png`: mỗi ô một cỡ (k2, k4, k6, k8). Trục ngang là độ phủ dải River, trục dọc là km bay.
  - Chấm xanh dương là k‑medoids.
  - Đường xanh lá là MEANDER với luồng 4,5 / 6 / 7,5 / 9 / 12 cell; luồng rộng nhất ở bên trái.
