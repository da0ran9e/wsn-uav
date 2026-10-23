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

## Sửa lỗi đo và phân tích yếu tố (mục 148)

**Lỗi trong `kin_time.py`:** ở chỗ hai cụm nối liền (seam), đường đo vẫn chèn đoạn nối từ cuối đoạn dẫn ra tới đầu đoạn dẫn vào, tức bay tới rồi quay lại, cộng cả phạt độ cong của chỗ quay đầu. Lỗi này chỉ ảnh hưởng MEANDER (tour `route`), làm nó chậm thêm 60–180 s. Đã sửa (chỗ nối liền không có đoạn nối) và `kin_time.run` tách độ dài tour theo loại: trên cụm, dẫn vào/ra, nối giữa cụm (kể cả quay đầu giữa các luồng), đi/về BS. Mọi số MEANDER trước bản sửa (bảng ở trên và `logs/2026-10-23_18*-meander-lane/`) bị thay bằng `screen-all-fixed-table.md`:

| | cụm | cell | 50 m/s (s) | 45° + giao đủ (s, số cụm phải bù) | 30° + giao đủ | trên cụm (km) | dẫn vào/ra (km) | nối giữa cụm (km) | BS (km) | critical | khoảng cách TB (m) | p90 (m) | > 606 m |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k8s1-CHORD | 9 | 617 | 743 | 790 (9) | 854 (9) | 17.8 | 4.6 | 9.1 | 5.6 | 47 | 346 | 805 | 11 |
| k8s1-MEANDER | 9 | 617 | 731 | 791 (5) | 840 (5) | 18.8 | 2.0 | 6.2 | 9.5 | 45 | 275 | 568 | 4 |
| b200w1-CHORD | 11 | 716 | 925 | 992 (11) | 1067 (11) | 19.2 | 5.6 | 13.3 | 8.1 | 53 | 274 | 648 | 6 |
| b200w1-MEANDER | 11 | 716 | 784 | 830 (5) | 865 (5) | 24.0 | 1.5 | 4.1 | 9.5 | 57 | 237 | 544 | 3 |
| b90w1-CHORD | 8 | 677 | 763 | 788 (7) | 860 (7) | 15.2 | 4.1 | 10.6 | 8.3 | 46 | 377 | 891 | 9 |
| b90w1-MEANDER | 8 | 677 | 770 | 790 (2) | 814 (2) | 18.5 | 1.0 | 1.5 | 17.5 | 50 | 250 | 516 | 2 |
| b300w08-CHORD | 11 | 764 | 942 | 1004 (11) | 1083 (11) | 19.8 | 5.6 | 14.1 | 7.7 | 51 | 343 | 701 | 10 |
| b300w08-MEANDER | 11 | 764 | 752 | 864 (6) | 899 (6) | 24.1 | 1.5 | 3.9 | 8.0 | 56 | 242 | 513 | 3 |
| b120w07-s1-CHORD | 13 | 847 | 1224 | 1287 (11) | 1395 (11) | 24.5 | 6.6 | 22.3 | 7.8 | 62 | 256 | 569 | 6 |
| b120w07-s1-MEANDER | 13 | 847 | 910 | 945 (7) | 977 (6) | 27.6 | 1.5 | 4.6 | 11.7 | 66 | 209 | 389 | 1 |
| b120w07-s3-CHORD | 12 | 830 | 1147 | 1206 (12) | 1292 (12) | 21.3 | 6.1 | 16.5 | 13.5 | 58 | 303 | 705 | 9 |
| b120w07-s3-MEANDER | 12 | 830 | 950 | 1004 (4) | 1041 (4) | 26.0 | 1.5 | 7.3 | 12.7 | 59 | 260 | 633 | 7 |
| b120w07-s5-CHORD | 10 | 853 | 950 | 981 (9) | 1045 (9) | 19.2 | 5.1 | 12.0 | 11.2 | 57 | 374 | 721 | 13 |
| b120w07-s5-MEANDER | 10 | 853 | 653 | 714 (6) | 735 (6) | 21.1 | 1.0 | 1.7 | 8.8 | 59 | 300 | 592 | 6 |
| b120w07-s6-CHORD | 13 | 834 | 1147 | 1232 (13) | 1329 (13) | 22.2 | 6.6 | 20.8 | 7.7 | 61 | 258 | 487 | 3 |
| b120w07-s6-MEANDER | 13 | 834 | 821 | 867 (9) | 900 (9) | 26.2 | 1.5 | 3.4 | 10.0 | 65 | 242 | 493 | 2 |
