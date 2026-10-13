# Giả lập trọn nhiệm vụ Pha 1 — từ bản đồ tới khi đội 2 về BS

Lời gốc: CLAUDE.md §8 mục 68. Lõi của giả lập là cơ chế tầng 3 (River, [`../../uav-coop2/docs/L3-vi.md`](../../uav-coop2/docs/L3-vi.md)),
chạy trên ns-3 với MAC 802.15.4 đầy đủ, 7 màu, gateway chọn theo chất lượng liên kết. Hình không có chữ
(mục 63), mọi con số nằm trong bảng dưới đây.

**Chạy lại:**
```
python3 tools/mission.py --clusters 4 --seed 2 --work WORK/k4 --bin BIN     # tương tự: 2/3, 6/4, 8/4
python3 tools/mission_report.py --works WORK/k2,WORK/k4,WORK/k6,WORK/k8 --figs docs/figures \
    --out docs/data/mission/mission
```
`BIN` chứa các binary đóng băng: `deploy-bin`, `pass-bin` (thư viện `pass-lib/`), `river-bin` (thư viện `lib/`).
Kết quả gọn của từng bản đồ nằm ở `docs/data/mission/k{2,4,6,8}/`. Bảng tổng: `mission-summary.csv`. Từng
critical cell: `mission-cells.csv`.

**Mỗi bản đồ chỉ chạy một lượt.** Số liệu ở đây minh hoạ chuỗi nhiệm vụ, chưa phải số để công bố
(quy tắc N ≥ 120).

## Kịch bản và giả định

| Công đoạn | Mô hình |
|---|---|
| Bản đồ | Miền "khối có hồ" (`map_gen`), mọc 80 × số cluster cell, mỗi cluster một hồ 10 cell; node 1 / 35 m × 35 m. BS cách cell thấp nhất 1 km về phía nam |
| Chia cluster | `partition.py`, chặn trên 80 cell |
| Triển khai | `uav-coop-deploy` với miền và node có sẵn: CH, CL, route PECEE, gateway. CH cách biên ≥ 300 m; cluster quá mảnh hạ xuống 200, 100 hoặc 0 m |
| Đường bay đội 1 trong cluster | Thẳng qua CH theo hướng có đoạn nằm trong cluster dài nhất (quét 0–178°, bước 2°). Nếu Dubins không ra được ngoài cluster thì lấy hướng dài kế tiếp |
| Đội 1 | Một UAV cánh bằng, 50 m/s, độ cao 100 m. Tour BS → đoạn bay của mọi cluster (mỗi đoạn chọn chiều) → BS, ngắn nhất theo Held–Karp. Đoạn chuyển tiếp là đường thẳng (chưa tính bán kính quay) |
| Phát dữ liệu | `uav-coop-pass` lượt 1: một gói / 10 ms. Mỗi cluster chỉ tính gói khi UAV bay trên đoạn của chính nó (gói tràn sang cluster khác bị bỏ qua) |
| Tầng 3 | `uav-coop2-river`, cluster bắt đầu khi UAV rời nó. Ba phương án: **River chuẩn bị sẵn** (chính), **River Circle 12** (Circle động cố định 12 thành viên), **kéo thẳng** |
| Đối sánh | Bắt đầu khi critical cell có đủ D của cluster; tạm là một khoảng chờ 5 s |
| Báo cáo | Mỗi critical cell gửi vài byte về BS qua LoRa: 0,4 s phát + chờ duty cycle ngẫu nhiên 0–30 s |
| Nghi vấn | Trên toàn bản đồ: 1 critical cell là nghi vấn thật, 2–3 critical cell khác là nghi vấn giả (bốc ngẫu nhiên một lần mỗi bản đồ). Các critical cell còn lại báo không thấy gì |
| Đội 2 | Một UAV cánh quay, 15 m/s, rời BS khi mọi critical cell đã báo cáo. Bay tour TSP chính xác BS → nghi vấn → BS (không ràng buộc độ cong), theo chiều có chặng đầu ngắn hơn. Lơ lửng 30 s xác minh mỗi điểm. Tới nghi vấn thật thì bay thẳng về BS, nhiệm vụ kết thúc |

Thứ tự thăm do TSP quyết định, nên nghi vấn thật có thể rơi vào lần thăm đầu hoặc cuối hoàn toàn do may rủi.
Vì vậy bảng có thêm cột **"TB mọi nghi vấn"**: thời điểm kết thúc trung bình nếu lần lượt coi từng nghi vấn
là thật, với cùng tour.

## Công đoạn 1–3: bản đồ, cluster, đường bay đội 1

![maps](figures/mission-maps.png)

Bốn panel từ trái sang là 2, 4, 6, 8 cluster.
- Màu: cluster. Gạch chéo: hồ. Viền đậm: biên cluster.
- Mũi tên đậm: đoạn bay phát dữ liệu trong cluster. Nét đứt: chặng chuyển tiếp.
- ■: BS. ★: CH. ○: các critical cell khác.
- Thanh ngang: 1 km.

| Bản đồ | Cell đất | Node | Cluster (cell) | Critical | Tour đội 1 | Đội 1 về BS |
|---|---|---|---|---|---|---|
| k2 | 147 | 3 118 | 80 / 67 | 12 | 11,3 km | 225 s |
| k4 | 308 | 6 532 | 80 / 80 / 80 / 68 | 27 | 16,3 km | 327 s |
| k6 | 465 | 9 862 | 80 / 80 / 80 / 80 / 78 / 67 | 45 | 26,0 km | 519 s |
| k8 | 595 | 12 619 | 80 / 80 / 74 / 78 / 70 / 72 / 68 / 73 | 52 | 32,0 km | 640 s |

- **Đoạn bay trong mỗi cluster dài 1,8–2,4 km,** nên mỗi cluster nhận |D| = 3 600–4 800 gói.
- **Hai trường hợp phải dùng phương án dự phòng:**
  - k4/C4 quá mảnh để có node cách biên 300 m, nên hạ xuống 200 m.
  - k8/C4 lõm tới mức đường vào từ điểm biên ngẫu nhiên không khả thi, nên thử điểm vào khác.

## Công đoạn 4: sau lượt phát

![pass](figures/mission-pass.png)

Màu cell là tỉ lệ D của cluster mà cell đó (gộp mọi node) đã nhận được: nhạt là ít, đậm là đủ. Đường mảnh là đoạn bay.

| Bản đồ | Cell giữ TB | Cell thấp nhất | Critical TB | Critical thấp nhất |
|---|---|---|---|---|
| k2 | 84 % | 48 % | 85 % | 64 % |
| k4 | 89 % | 40 % | 88 % | 46 % |
| k6 | 91 % | 42 % | 90 % | 42 % |
| k8 | 92 % | 22 % | 92 % | 52 % |

Ngay sau lượt bay, một critical cell trung bình đã có khoảng 9/10 dữ liệu. River chỉ phải lấp phần còn
thiếu, thường 8–15 %. Một số critical cell nằm xa đường bay thiếu tới khoảng một nửa.

## Công đoạn 5: River trong từng cluster

![river](figures/mission-river.png)

- Xanh đậm: Axe. Xanh lá: Bank. Xanh nhạt: River. Xám: phần còn lại của cluster.
- ★ / ○: critical cell.

**Thời gian từ lúc UAV rời cluster tới khi critical cell cuối cùng của cluster đủ D (s), và số khung MAC:**

| Cluster | Axe | \|D\| | Crit | River chuẩn bị | Circle 12 | Kéo thẳng | Khung: River / Circle 12 / kéo thẳng (nghìn) |
|---|---|---|---|---|---|---|---|
| k2-C2 | 16 | 4 628 | 6 | 66,9 | 63,4 | 75,4 | 217 / 193 / 244 |
| k2-C1 | 15 | 4 538 | 6 | 27,9 | 21,1 | 36,2 | 65 / 42 / 66 |
| k4-C3 | 15 | 4 324 | 7 | 21,5 | 25,6 | 32,0 | 68 / 36 / 77 |
| k4-C1 | 14 | 3 735 | 7 | 59,6 | 62,2 | 61,2 | 160 / 135 / 171 |
| k4-C4 | 12 | 4 157 | 6 | 36,3 | 30,9 | 48,8 | 92 / 56 / 88 |
| k4-C2 | 18 | 4 548 | 7 | 60,0 | 53,5 | 65,0 | 148 / 113 / 156 |
| k6-C6 | 13 | 4 104 | 7 | 16,8 | 17,8 | 20,6 | 24 / 14 / 29 |
| k6-C1 | 16 | 4 325 | 7 | 20,6 | 20,1 | 22,7 | 52 / 28 / 67 |
| k6-C5 | 15 | 3 870 | 7 | 17,1 | 21,2 | 18,9 | 26 / 17 / 31 |
| k6-C4 | 17 | 4 757 | 7 | 71,3 | 71,1 | 94,0 | 182 / 126 / 236 |
| k6-C2 | 13 | 3 631 | 9 | 32,8 | 33,3 | 57,1 | 142 / 110 / 151 |
| k6-C3 | 16 | 4 580 | 8 | 37,3 | 40,6 | 56,0 | 146 / 112 / 183 |
| k8-C6 | 13 | 3 939 | 7 | 46,1 | 41,4 | 42,2 | 108 / 90 / 122 |
| k8-C3 | 16 | 4 549 | 6 | 22,4 | 23,2 | 35,6 | 60 / 41 / 71 |
| k8-C1 | 14 | 3 870 | 7 | 17,4 | 17,7 | 19,2 | 24 / 15 / 28 |
| k8-C5 | 13 | 3 905 | 7 | 26,6 | 26,6 | 42,1 | 54 / 39 / 68 |
| k8-C7 | 15 | 3 847 | 6 | 19,6 | 19,3 | 19,6 | 21 / 9 / 16 |
| k8-C8 | 14 | 4 369 | 4 | 32,6 | 25,7 | 28,4 | 44 / 32 / 49 |
| k8-C4 | 17 | 4 548 | 7 | 27,0 | 28,1 | 32,3 | 68 / 43 / 83 |
| k8-C2 | 15 | 4 247 | 8 | 43,3 | 44,9 | 58,9 | 123 / 86 / 142 |

Mọi critical cell của cả 20 cluster đều nhận đủ D ở cả ba phương án.

- **River chuẩn bị sẵn so với kéo thẳng:**
  - Nhanh hơn ở 17/20 cluster, hoà 1, chậm hơn 2 (k8-C6, k8-C8).
  - Ít khung hơn ở 18/20 cluster.
  - Tổng khung trên bản đồ giảm 9 % (k2), 5 % (k4), 18 % (k6), 13 % (k8).
- **Circle 12 so với River chuẩn bị sẵn:**
  - Ít khung hơn ở **cả 20/20** cluster. Tổng giảm 17 / 27 / 29 / 29 %.
  - Về thời gian thì lẫn lộn: nhanh hơn ở 9 cluster, chậm hơn ở 10, hoà 1.
  - Phát hiện của lượt C3 (Circle càng lớn càng tiết kiệm khung) lặp lại trên mọi cluster. Lợi thế về thời gian thì không.
- **Thời gian tầng 3 của một cluster là 17–95 s.** Các cluster chậm nhất (k2-C2, k4-C1/C2, k6-C4) có Axe dài và nhiều critical cell nằm xa đường bay.

## Công đoạn 6–7: đối sánh, báo cáo, nghi vấn và đội 2

![suspects](figures/mission-suspects.png)

- ●: critical cell. Đỏ: nghi vấn thật. Cam: nghi vấn giả.
- Mũi tên đỏ: đường đội 2 đã bay. Nét đứt đỏ: chặng về BS. Chấm xám: phần tour TSP không cần bay tiếp.

![timeline](figures/mission-timeline.png)

**Dòng thời gian** (River chuẩn bị sẵn). Mỗi khối là một bản đồ, mỗi hàng là một cluster theo thứ tự tour,
hàng cuối là đội 2. Lưới dọc cách nhau 60 s.
- **Mỗi hàng cluster:**
  - Xanh đậm: UAV bay trên cluster.
  - Xanh lá: tầng 3, tới critical cell cuối.
  - Tím: 5 s đối sánh của từng critical cell.
  - Chấm: lúc báo cáo tới BS (đỏ là thật, cam là giả, trắng là không thấy gì).
- **Hàng đội 2:** đỏ là bay, ô trắng là 30 s xác minh, hồng là đường về.
- Nét đứt dọc: lúc đội 1 về BS.

| Bản đồ | Phương án | Critical cuối đủ D | Đội 2 xuất phát | Thấy nghi vấn thật (lần thăm) | Kết thúc | TB mọi nghi vấn |
|---|---|---|---|---|---|---|
| k2 | River chuẩn bị | 194,8 s | 215,5 s | 513,0 s (3) | **716,7 s** | 570,7 s |
| | Circle 12 | 188,0 | 206,8 | 504,3 | 708,0 | 562,0 |
| | kéo thẳng | 203,1 | 221,2 | 518,7 | 722,4 | 576,4 |
| k4 | River chuẩn bị | 366,5 | 397,2 | 498,3 (1) | **629,3** | 811,0 |
| | Circle 12 | 360,0 | 390,7 | 491,8 | 622,8 | 804,5 |
| | kéo thẳng | 371,5 | 402,3 | 503,3 | 634,4 | 816,1 |
| k6 | River chuẩn bị | 513,3 | 540,7 | 1 117,5 (3) | **1 485,2** | 1 305,9 |
| | Circle 12 | 516,6 | 547,2 | 1 124,1 | 1 491,7 | 1 312,4 |
| | kéo thẳng | 532,0 | 560,4 | 1 137,3 | 1 504,9 | 1 325,7 |
| k8 | River chuẩn bị | 652,7 | 676,2 | 1 129,0 (2) | **1 577,9** | 1 515,2 |
| | Circle 12 | 654,3 | 673,1 | 1 125,9 | 1 574,8 | 1 512,1 |
| | kéo thẳng | 668,3 | 682,7 | 1 135,5 | 1 584,4 | 1 521,7 |

## Đọc kết quả

1. **Nhiệm vụ do đường bay chi phối, không do tầng 3.**
   - Đội 1 cần 225–640 s. Đội 2 cần thêm 230–950 s.
   - Tầng 3 chỉ kéo dài 17–95 s sau khi UAV rời mỗi cluster, và phần lớn chồng lên lúc đội 1 đang bay cluster kế tiếp.
   - Vì vậy, đổi phương án tầng 3 chỉ dịch thời điểm kết thúc khoảng 6–20 s (1–3 %).
2. **Đường găng là cluster đội 1 bay qua cuối cùng.**
   - Đội 2 phải chờ báo cáo chậm nhất. Báo cáo đó gần như luôn thuộc cluster cuối tour (hoặc cluster có tầng 3 dài như k4-C2), cộng 5 s đối sánh và tới 30 s chờ LoRa.
   - Ở k4, đội 2 xuất phát sau khi đội 1 đã về BS 70 s.
   - Tầng 3 nhanh có ý nghĩa nhất ở cluster cuối tour.
3. **Đội 2 chiếm phần lớn nửa sau.**
   - Ví dụ k6: 3 nghi vấn rải trên 3–4 km, 15 m/s, 30 s xác minh mỗi điểm.
   - Thứ tự TSP không biết nghi vấn nào là thật. Ở k4 thăm trúng ngay lần đầu (629 s), nhưng trung bình mọi nghi vấn là 811 s.
4. **Tầng 3 vẫn là nơi tiết kiệm tài nguyên.**
   - River giảm 5–18 % khung so với kéo thẳng. Circle 12 giảm thêm 17–29 % so với River chuẩn bị.
   - Mạng càng lớn thì mức giảm càng ổn định.
5. **Chưa mô hình hoá:**
   - Bán kính quay của đội 1 ở chặng chuyển tiếp.
   - Gói tràn sang cluster láng giềng khi bay ngang (dữ liệu "miễn phí", hiện bị bỏ).
   - Năng lượng.
   - Đối sánh thật (lớp 1).
   - Điểm nghi vấn có xác suất (đội 2 có thể ưu tiên theo điểm).

## Hướng phát triển gợi ý (chưa làm)

- **Cho đội 2 xuất phát sớm:** ngay khi có nghi vấn đầu tiên, hoặc khi các cluster đã báo đủ phần lớn, thay vì chờ mọi critical cell. Theo dòng thời gian, cách này rút được tới vài trăm giây ở bản đồ lớn.
- **Sắp tour đội 1 sao cho cluster có tầng 3 dài được bay sớm,** để phần River của nó chồng hết lên thời gian bay.
- **Thăm nghi vấn theo điểm nghi vấn × khoảng cách** thay cho TSP thuần.
- **Chạy nhiều lượt** (N ≥ 120) trên mỗi kích thước trước khi rút kết luận định lượng.
