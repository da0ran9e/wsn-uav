# 2026-10-24 · MEANDER kiểu luống làm thẳng dần, trên bản đồ ngẫu nhiên (CLAUDE.md §8 mục 151)

**Mục đích:** bỏ miền dải dài (mất tính tổng quát); thêm tham số độ thẳng cho đường luống, chỉ kéo về critical cell xa hơn 5 cell; thử lại trên bản đồ ngẫu nhiên (`restructure.domain(8, s)`, seed 1–3), so với CHORD-T cùng số cụm; rồi ns-3.

**Mã:** `meander_lane.py --straight KM --reach CELLS` (hàm `straighten`: làm mượt độ lệch so với dây cung giữa hai đầu luồng ở thang KM, inf là dây cung); `straight_sweep.py` (mới).

**Quét độ thẳng, hình học (`straight-table.md`):** MEANDER (`--minAxe 2.4 --reach 5`) ra 4–6 cụm. Tour ở 45°:

| seed | CHORD-T | MEANDER 0 / 0,5 / 1 / 2 / 4 / thẳng hẳn | critical trong 5 cell: CHORD-T / MEANDER 0–1 km / thẳng hẳn |
|---|---|---|---|
| 1 | 506 | 697 / 674 / 660 / 652 / 658 / 646 | 77 % / 93–98 % / 77 % |
| 2 | 515 (K 5) | 590 / 581 / 575 / 610 / 594 / 585 | 73 % / 98–100 % / 79 % |
| 3 | 552 | 701 / 673 / 653 / 638 / 667 / 646 | 89 % / 96 % / 92 % |

Làm thẳng rút tour 30–60 s nhưng MEANDER vẫn chậm hơn 60–190 s; làm thẳng hẳn thì mất lợi thế gần critical cell.

**ns-3, độ thẳng 0,5 km (`ns3-diag.md`, `l1rank/`, T\* TB 100 lần bốc, `-kt`):**

| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| k8-s1 | CHORD-T | 506 | 39 | 262 | 13 / 26 / 50 | 275 | 100% | 713 |
| k8-s1 | MEANDER | 674 | 44 | 364 | 31 / 70 / 110 | 395 | 95% | 830 |
| | critical chung | 36 / 39 / 44 | | | | | | |
| k8-s2 | CHORD-T | 515 | 37 | 238 | 21 / 49 / 135 | 259 | 100% | 652 |
| k8-s2 | MEANDER | 581 | 43 | 320 | 30 / 65 / 79 | 350 | 100% | 743 |
| | critical chung | 37 / 37 / 43 | | | | | | |
| k8-s3 | CHORD-T | 552 | 46 | 265 | 14 / 29 / 68 | 279 | 100% | 700 |
| k8-s3 | MEANDER | 673 | 49 | 357 | 22 / 45 / 69 | 379 | 100% | 859 |
| | critical chung | 44 / 46 / 49 | | | | | | |

MEANDER chậm hơn ở mọi khâu: tour, thời điểm rời cụm (+80–100 s), River (cụm to hơn, tới 182 cell), T\* (+91–159 s).

**Vì sao:** điều kiện Axe ≥ 2,4 km làm số cụm còn 5–6, tức khoảng 1,3 cụm mỗi luồng. Yếu tố có lợi chính của MEANDER (nhiều cụm trên một luồng, `logs/2026-10-23_1920-factor-sweep/`) không còn, trong khi đường luống phải phủ cả miền (23–25 km) so với 5–6 dây cung.

**Dang dở:** thử luồng rộng hơn (10–12 cell: nửa luồng ≈ 5 cell, đúng ngưỡng người dùng cho phép) để giảm số luồng và độ dài đường luống.
