# 2026-10-23 · Tìm kịch bản MEANDER thắng CHORD hoàn toàn (CLAUDE.md §8 mục 147)

**Mục đích:** tìm dạng miền mà MEANDER kiểu luống (`meander_lane.py`) thắng CHORD-T 80 % trên mọi chỉ số lớp 2 đo được bằng Python (chưa chạy ns-3).

**Thay đổi mã:**
- `restructure.domain(K, seed, shape)` và `mission.py --shape`, `meander_lane.py --shape`: chọn dạng miền của `map_gen` (spine, bend, width).
- `meander_lane.py`: mỗi mảnh đất (hồ/sông cắt rời) có xương sống riêng; thử thêm chiều bay của luồng đầu (flip), để luồng chẵn có thể bắt đầu và kết thúc ở đầu gần BS.
- `l2_screen.py` (mới): bảng một dòng mỗi work (tour, giao đủ, khoảng cách critical cell tới đường bay).

**Cách so:** cùng miền, cùng seed; MEANDER chia tự nhiên ra K cụm, CHORD-T dùng `--count K` (k-medoids đúng K cụm). Tour đội 1 có hồ sơ tốc độ và bù giao đủ (`kin_time.py`).

**Dò dạng miền (seed 1, `screen-table.md`):** dải cong 10 km, 120°, rộng ~0,7 km (`spine=10,bend=120,width=0.7`) là dạng MEANDER thắng rõ nhất.

**Bốn seed liên thông của dải đó (`screen-seeds-table.md`):**

| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | critical | khoảng cách TB (m) | p90 (m) | > 606 m |
|---|---|---|---|---|---|---|---|---|---|
| b120w07-s1-CHORD | 13 | 847 | 1224 | 1287 (11) | 1395 (11) | 62 | 256 | 569 | 6 |
| b120w07-s1-MEANDER | 13 | 847 | 1110 | 1123 (6) | 1154 (5) | 66 | 209 | 389 | 1 |
| b120w07-s3-CHORD | 12 | 830 | 1147 | 1206 (12) | 1292 (12) | 58 | 303 | 705 | 9 |
| b120w07-s3-MEANDER | 12 | 830 | 1130 | 1178 (3) | 1215 (3) | 59 | 260 | 633 | 7 |
| b120w07-s5-CHORD | 10 | 853 | 950 | 981 (9) | 1045 (9) | 57 | 374 | 721 | 13 |
| b120w07-s5-MEANDER | 10 | 853 | 813 | 854 (6) | 874 (6) | 59 | 300 | 592 | 6 |
| b120w07-s6-CHORD | 13 | 834 | 1147 | 1232 (13) | 1329 (13) | 61 | 258 | 487 | 3 |
| b120w07-s6-MEANDER | 13 | 834 | 1021 | 1061 (8) | 1093 (8) | 65 | 242 | 493 | 2 |

Seed 2 và 4 có đảo một cell (đất rời), k-medoids của `partition.py` không chạy được trên đất rời, nên bỏ.

**k8-s1 (khối có hồ) sau khi thêm flip (`screen-k8-s1-table.md`):** không đổi, CHORD-T vẫn nhanh hơn 91 s.

**Dang dở:** chưa chạy ns-3 River và T\*; mới 4 seed của một dạng dải.
