# 2026-10-23 · Quét yếu tố MEANDER kiểu luống vs CHORD-T, rồi ns-3 trên kịch bản chốt (CLAUDE.md §8 mục 148–149)

**Mục đích:** tìm các yếu tố có lợi cho MEANDER kiểu luống (`meander_lane.py`) so với CHORD-T 80 % (P\*), quét từng yếu tố một kể cả kích thước miền; chốt một kịch bản tốt rồi chạy ns-3 (River, T\*) trên vài bản đồ, chỉ so với CHORD-T.

## Mã

- `factor_sweep.py` (mới): 60 cặp bản đồ, 3 seed mỗi mức; CHORD-T lấy đúng số cụm MEANDER tự chia; chỉ hình học + `kin_time`.
- `factor_fig.py` (mới): bảng tổng hợp và hình `factor-sweep-meander-vs-chordT.png`.
- `restructure.bs_point` + `--bs` (south/end/side/centre) cho `mission.py` và `meander_lane.py`; `meander_lane.py --span`, `--minAxe` (cắt luồng theo độ dài đất dưới đường bay).
- `chord_tour.choose_heur`: trên 13 cụm, thứ tự heuristic + quy hoạch động chính xác cho hướng/chiều, cải thiện bằng dời/2-opt (thử ngẫu nhiên K = 8: kém Held-Karp 0–1,4 %).
- `mission.py`: ngưỡng CLUE của CHORD-T theo `--windowKB`.
- `kin_time.py`: nghiêng 60°, cỡ bộ manh mối `q_kb`, thời điểm rời từng cụm (`leave`); `l1_rank.py`: tour `route` và tuỳ chọn `-kt` (T\* dùng thời điểm rời cụm theo động học bay 45° kể cả bù giao đủ).
- `l2_screen.py`: cột 60°, `--q`; `iter_fig.py`: không vẽ đoạn nối ở chỗ nối liền.

## 1. Quét yếu tố (`sweep-table.md`, `factor-summary.md`, `factor-correlation.md`)

Base: dải 10 km uốn 120°, rộng 0,7 km, 80 × 8 cell, BS south, luồng 8 cell, cụm dài ≤ 14 cell, bộ manh mối 400 kB, nghiêng 45°.

| yếu tố | mức | seed | tour 45° CHORD-T / MEANDER (s) | chênh TB (min–max) | MEANDER thắng | chênh 30° | khoảng cách critical TB CHORD-T / MEANDER (m) | cụm |
|---|---|---|---|---|---|---|---|---|
| size | K 4, spine 7.07, width 0.49 | 3 | 677 / 486 | +191 (+111…+269) | 3/3 | +220 | 300 / 218 | 6.7 |
| size | K 6, spine 8.66, width 0.61 | 3 | 768 / 573 | +195 (+171…+232) | 3/3 | +216 | 370 / 262 | 8.0 |
| size | K 8, spine 10, width 0.7 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| size | K 12, spine 12.25, width 0.86 | 3 | 1472 / 1246 | +226 (+133…+372) | 3/3 | +279 | 353 / 272 | 15.7 |
| size | K 16, spine 14.14, width 0.99 | 3 | 2072 / 1611 | +461 (+318…+723) | 3/3 | +580 | 320 / 255 | 23.0 |
| aspect | spine 0 | 3 | 812 / 734 | +78 (-1…+148) | 2/3 | +97 | 321 / 267 | 8.7 |
| aspect | spine 5, width 1.4 | 3 | 666 / 628 | +38 (+20…+60) | 3/3 | +58 | 393 / 275 | 7.7 |
| aspect | spine 7, width 1 | 3 | 656 / 558 | +98 (+11…+168) | 3/3 | +134 | 323 / 284 | 7.7 |
| aspect | spine 10, width 0.7 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| aspect | spine 14, width 0.5 | 3 | 1568 / 1260 | +308 (+242…+368) | 3/3 | +393 | 319 / 247 | 16.7 |
| bend | bend 0 | 3 | 977 / 722 | +255 (+63…+376) | 3/3 | +302 | 310 / 204 | 10.0 |
| bend | bend 60 | 3 | 1073 / 744 | +329 (+318…+341) | 3/3 | +375 | 311 / 239 | 10.3 |
| bend | bend 120 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| bend | bend 180 | 3 | 1053 / 880 | +173 (+81…+318) | 3/3 | +223 | 328 / 223 | 11.7 |
| bend | bend 240 | 3 | 887 / 777 | +110 (+15…+213) | 3/3 | +148 | 295 / 276 | 10.3 |
| bs | bs south | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| bs | bs end | 3 | 1170 / 832 | +338 (+204…+438) | 3/3 | +396 | 329 / 256 | 11.7 |
| bs | bs side | 3 | 993 / 812 | +180 (+76…+307) | 3/3 | +241 | 323 / 258 | 11.7 |
| bs | bs centre | 3 | 1018 / 818 | +200 (+150…+261) | 3/3 | +256 | 319 / 256 | 11.7 |
| span | span 10 | 3 | 1392 / 1022 | +371 (+303…+486) | 3/3 | +476 | 252 / 240 | 16.0 |
| span | span 14 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| span | span 18 | 3 | 915 / 853 | +62 (-4…+178) | 2/3 | +91 | 384 / 256 | 9.3 |
| q | q 300 | 3 | 1021 / 849 | +172 (-25…+287) | 2/3 | +215 | 324 / 256 | 11.7 |
| q | q 400 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| q | q 500 | 3 | 1271 / 965 | +306 (+219…+411) | 3/3 | +387 | 299 / 256 | 11.7 |
| bank | bank 30 | 3 | 1244 / 918 | +326 (+251…+418) | 3/3 | +326 | 311 / 256 | 11.7 |
| bank | bank 45 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |
| bank | bank 60 | 3 | 1158 / 888 | +270 (+202…+342) | 3/3 | +326 | 311 / 256 | 11.7 |

Tương quan (54 cặp, 400 kB):

| đại lượng | Spearman với chênh tour 45° | khoảng |
|---|---|---|
| số cụm K | +0.50 | 6.0–24.0 |
| số cụm / số luồng | +0.70 | 2.2–6.5 |
| số cell | +0.35 | 404.0–1674.0 |
| cell / cụm | -0.31 | 47.1–106.6 |
| số luồng | -0.01 | 2.0–4.0 |
| km dẫn + nối CHORD-T tiết kiệm được | +0.76 | 5.2–45.4 |
| km đi/về BS MEANDER bay thêm | -0.36 | -9.6–7.9 |
| km trên cụm MEANDER bay thêm | +0.18 | -2.3–11.8 |

54 cặp (clue set 400 kB), MEANDER nhanh hơn ở 52.
TB km: MEANDER tiết kiệm 16.9 km dẫn + nối, bay thêm 1.5 km đi/về BS và 3.9 km trên cụm.

## 2. Kịch bản chốt

Dải 10 km, uốn 60°, rộng 0,7 km, BS ở đầu dải (`--shape spine=10,bend=60,width=0.7 --bs end`), seed 1–3 (`scenario-table.md`).

## 3. ns-3 vòng 1: cắt luồng theo số cell (`ns3-diag.md`, `l1rank/`)

| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| band-s1 | CHORD-T | 1095 | 51 | 448 | 9 / 17 / 40 | 457 | 63% | 988 |
| band-s1 | MEANDER | 672 | 52 | 364 | 8 / 24 / 49 | 372 | 29% | 1271 |
| | critical chung | 42 / 51 / 52 | | | | | | |
| band-s2 | CHORD-T | 1064 | 51 | 400 | 13 / 24 / 90 | 413 | 49% | 874 |
| band-s2 | MEANDER | 690 | 53 | 287 | 6 / 12 / 22 | 293 | 25% | 899 |
| | critical chung | 44 / 51 / 53 | | | | | | |
| band-s3 | CHORD-T | 967 | 54 | 429 | 10 / 19 / 53 | 439 | 80% | 1000 |
| band-s3 | MEANDER | 665 | 55 | 367 | 10 / 31 / 65 | 377 | 11% | 1013 |
| | critical chung | 47 / 54 / 55 | | | | | | |

MEANDER sẵn sàng sớm hơn nhưng chỉ 11–29 % critical cell đủ 12 manh mối. Một cụm giao đủ khi và chỉ khi Axe ≥ 2,02 km (ở cả hai phương án); MEANDER có 7–9/10–11 cụm Axe 0,7–1,8 km vì cắt luồng theo số cell; ns-3 bay đều 50 m/s nên không có giảm tốc bù.

## 4. ns-3 vòng 2: cắt luồng theo độ dài, `--minAxe 2.4` (`ns3b-diag.md`, `l1rank2/`)

| bản đồ | phương án | tour 45° (s) | critical | rời cụm TB (s) | River xong TB / p90 / max (s) | sẵn sàng TB (s) | đủ 12 manh mối | T* TB (s) |
|---|---|---|---|---|---|---|---|---|
| band-s1 | CHORD-T | 928 | 50 | 362 | 30 / 115 / 165 | 391 | 90% | 993 |
| band-s1 | MEANDER | 561 | 50 | 303 | 20 / 55 / 69 | 323 | 100% | 918 |
| | critical chung | 44 / 50 / 50 | | | | | | |
| band-s2 | CHORD-T | 680 | 46 | 285 | 20 / 55 / 83 | 304 | 100% | 752 |
| band-s2 | MEANDER | 561 | 49 | 252 | 20 / 49 / 53 | 272 | 100% | 733 |
| | critical chung | 41 / 46 / 49 | | | | | | |
| band-s3 | CHORD-T | 720 | 51 | 324 | 15 / 29 / 50 | 338 | 100% | 825 |
| band-s3 | MEANDER | 564 | 52 | 322 | 20 / 43 / 68 | 343 | 94% | 842 |
| | critical chung | 49 / 51 / 52 | | | | | | |

T\* là TB 100 lần bốc, `P+prog-<tour>-puq-stage-zero-redir-kt`. MEANDER nhanh hơn ở s1 (−75 s), s2 (−19 s), chậm hơn ở s3 (+17 s; còn một cụm Axe 1,83 km).

## Lưu ý

- Mới 3 bản đồ. Critical cell của hai cách chia trùng 41–49 trên 46–55, nên c\* có thể khác: T\* không ghép cặp chặt.
- Pass ns-3 bay đều 50 m/s; phần giảm tốc bù giao đủ chỉ có trong thời gian (`-kt`), không làm tăng số gói nhận.
- `chord_tour.choose` (Held-Karp) giữ một trạng thái tốt nhất theo tổng độ trễ, nên với mục tiêu này không hoàn toàn chính xác (thử ngẫu nhiên: heuristic đôi khi tốt hơn 0,2 %). Chưa sửa vì đây là P\* đã dùng cho các số cũ.

**Dang dở:** thứ tự luống chưa tối ưu độ trễ (luôn đi hết luồng 1 rồi luồng 2); bước nối mảnh sau khi cắt có thể làm một cụm hụt Axe (s3); chưa chạy nhiều bản đồ.
