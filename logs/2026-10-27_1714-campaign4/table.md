T\* trung bình (s), K = 8 / 12 / 16 cụm; mỗi ô 100 lượt bốc lớp 1 × số seed đã xong (1); – : chưa chạy xong.

| phương án | r = 1000 m | 500 m | 200 m | 150 m |
|---|---|---|---|---|
| LM-Tour + River | – / 721 / 807 | – / 905 / 1063 | – / 959 / 1063 | – / 978 / 1093 |
| CHORD + River | – / 742 / 872 | – / 1013 / 1150 | – / 1075 / 1257 | – / 1091 / 1278 |
| DTSP-N + River | – / – / – | – / – / – | – / – / 1505* | – / – / – |
| FC + DTSP-N | – / 805 / 967 | – / 1389 / 1750 | – / 2481 / 3469 | – / 3248 / 4468 |
| No broadcast (rotary TSP) | – / 4168 / 5169 | – / 4168 / 5169 | – / 4168 / 5169 | – / 4168 / 5169 |
| Oracle | – / 402 / 404 | – / 402 / 404 | – / 402 / 404 | – / 402 / 404 |

\* ước lượng mức mô hình của DTSP-N + River đã sửa (mục 193–194): seed 1, River dự đoán bằng bộ surrogate, chưa chạy ns-3; số đo ns-3 thay vào khi tác vụ xong. Cùng cách ước lượng, CHORD và LM-Tour lệch số ns-3 của chúng: k16 r200 +9 / +19 s.

# Bảng chiến dịch (seed đã xong: k12 open 1, k12 r500 1, k12 r200 1, k12 r100 1, k16 open 1, k16 r500 1, k16 r200 1, k16 r100 1)

CHORD chấm bằng `l1_rank` và bằng `lm_tour score` lệch nhau tối đa 0.0 s ở mọi lượt bốc.

T\* trung bình (s) trên mọi seed và lượt bốc; ngoặc: số seed. Team 1: thời gian bay của đội 1 (s).

| kênh (r) | bản đồ | LM-Tour + River | CHORD + River | DTSP-N + River | FC + DTSP-N | No broadcast (rotary TSP) | Oracle | team 1 LM / CHORD / DR / DN |
|---|---|---|---|---|---|---|---|---|
| open (1 km) | k12 | 721 | 742 | – | 805 | 4168 | 402 | 1085 / 1292 / – / 913 | (1)
| open (1 km) | k16 | 807 | 872 | – | 967 | 5169 | 404 | 1394 / 1437 / – / 1134 | (1)
| r500 (500 m) | k12 | 905 | 1013 | – | 1389 | 4168 | 402 | 1085 / 1292 / – / 2011 | (1)
| r500 (500 m) | k16 | 1063 | 1150 | – | 1750 | 5169 | 404 | 1308 / 1437 / – / 2563 | (1)
| r200 (200 m) | k12 | 959 | 1075 | – | 2481 | 4168 | 402 | 1083 / 1292 / – / 4016 | (1)
| r200 (200 m) | k16 | 1063 | 1257 | – | 3469 | 5169 | 404 | 1293 / 1437 / – / 5567 | (1)
| r100 (150 m) | k12 | 978 | 1091 | – | 3248 | 4168 | 402 | 1082 / 1292 / – / 5078 | (1)
| r100 (150 m) | k16 | 1093 | 1278 | – | 4468 | 5169 | 404 | 1291 / 1437 / – / 6808 | (1)

Chênh ghép cặp so với LM-Tour (s, âm là LM-Tour nhanh hơn), ± nửa khoảng tin cậy 95 % theo trung bình từng seed; ngoặc: % lượt bốc LM-Tour nhanh hơn.

| kênh | bản đồ | LM − (CHORD) | LM − (DTSP-N + River) | LM − (FC + DTSP-N) | (DTSP-N + River) − (FC + DTSP-N) |
|---|---|---|---|---|---|
| open | k12 | −21 (34 %) | – | −84 (56 %) | – |
| open | k16 | −66 (54 %) | – | −160 (70 %) | – |
| r500 | k12 | −109 (59 %) | – | −484 (82 %) | – |
| r500 | k16 | −87 (58 %) | – | −687 (85 %) | – |
| r200 | k12 | −116 (61 %) | – | −1522 (90 %) | – |
| r200 | k16 | −193 (62 %) | −422* (75 %) | −2406 (97 %) | −1964* (96 %) |
| r100 | k12 | −113 (67 %) | – | −2270 (89 %) | – |
| r100 | k16 | −185 (63 %) | – | −3375 (94 %) | – |
