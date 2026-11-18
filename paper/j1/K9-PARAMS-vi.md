---
status: current
updated: 2026-11-18
---
# K9 bước B0: tham số cho bài node thường gửi gì về AI node

Bảng tham số cho các bước B1–B6 của [PLAN-K9-DATA](PLAN-K9-DATA-vi.md) (việc K12 trong PLAN-TRACKS, phần cần ngay cho K9).
Nhãn nguồn: [repo] là ghi chú đã có, [web] là tra ngày 2026-11-18, [ước] là ước lượng của người ghi, chưa có nguồn.
Mỗi tham số có dải thấp / giữa / cao; B1 và B6 quét cả dải, không lấy một con số.

## 1. Lưu lượng người qua một camera, ρ (người/h)

| Mức | ρ | Cơ sở |
|---|---|---|
| thấp | 20 | ngõ, công viên, khu dân cư vắng [ước] |
| giữa | 200 | phố thường [ước, nằm giữa hai mức có nguồn] |
| cao | 1 500 | phố đi bộ thương mại: Elizabeth Mall (Hobart) khoảng 24 000 người từ 8 h tới nửa đêm, trung bình khoảng 1 500/h [web, đoạn trích tìm kiếm: báo cáo Gehl cho thành phố Hobart] |
| đỉnh | 3 700 | 32nd Street (Manhattan), 17–18 h ngày thường [web, đoạn trích tìm kiếm: Vital City NYC] |

- Đây là số người đi qua một điểm đếm. Một camera thấy mỗi người trong nhiều khung, nhưng các phương án D1–D3 đều gửi một bản
  ghi cho mỗi người (một vệt theo dõi), nên ρ là số bản ghi mỗi giờ.
- Dữ liệu đếm theo giờ của Melbourne, Auckland, Dublin công khai (CC BY), dùng được nếu cần phân bố thật theo giờ trong ngày.
  Container hiện không kết nối được API của Melbourne (proxy cắt kết nối).

## 2. Cỡ dữ liệu mỗi người

| Phương án | Cỡ | Cơ sở |
|---|---|---|
| D1 khung hình có người | 30–50 KB | JPEG 640×480 tới 1280×720, chất lượng vừa [ước] |
| D2 ảnh cắt người | 5–15 KB | JPEG 256×128, đúng cỡ đầu vào của OSNet [ước; cỡ đầu vào: web, Zhou et al. ICCV 2019] |
| D3 vector đặc trưng | 0,5 KB (512 chiều INT8), 1 KB (fp16), cộng khoảng 16 B thời điểm và vị trí | OSNet xuất vector 512 chiều [web: Zhou et al. 2019, mục 4.1]; cỡ INT8 [repo: `research_notes/l1-edge-recognition/edge_devices.md`] |

## 3. Thời gian xử lý theo bậc thiết bị

Bậc thiết bị theo [repo: `edge_devices.md`, bảng cuối]. Số nhà sản xuất cần chia 2–3 lần ra số ứng dụng thật [repo, cùng file].

| Bậc | Ví dụ | Phát hiện người | Trích đặc trưng mỗi ảnh cắt | Ghi chú |
|---|---|---|---|---|
| T0 MCU | ESP32-S3, STM32N6 | YOLOv8n 256 khoảng 25–29 ms trên STM32N6 [repo] | khoảng 255–287 ms một khuôn mặt trên ESP32-S3 [repo]; OSNet x0,25 (82 triệu MAC) trên STM32N6 chưa có số đo, ngoại suy từ YOLOv8n khoảng 3–10 ms [ước] | không giải mã video nén; chỉ xử lý trực tiếp |
| T1 chip camera | RV1126B, Hi3516 | khoảng 12 FPS YOLOv8n 640 (sau chia) [repo] | khoảng 100/s [repo] | node thường "tốt" |
| T2 máy nhỏ + bộ tăng tốc | Pi 5 + Hailo-8L, RK3588 | khoảng 60 FPS [repo] | 45–800/s tuỳ mô hình [repo] | ứng viên AI node |
| T3 Jetson Orin | Orin Nano | trên 100 FPS [repo] | CLIP 150–314/s [repo] | ứng viên AI node mạnh |

Đối sánh trên chỉ mục vector (tích vô hướng 512 chiều) tốn khoảng 1 µs mỗi cặp trên CPU ARM [ước], nên 10⁵ vector mất cỡ
0,1 s; đối sánh lúc truy vấn chỉ đáng kể khi phải trích đặc trưng lúc đó (nhận xét 1, PLAN-K9-DATA mục 8).

## 4. Độ chính xác re-ID theo cỡ mô hình (Market-1501)

| Mô hình | Tham số | MAC | Rank-1 | mAP | Nguồn |
|---|---|---|---|---|---|
| OSNet x1,0 | 2,2 triệu | 979 triệu | 94,8 % | 84,9 % | [web: Zhou et al. ICCV 2019, Bảng 6] |
| OSNet x0,75 | 1,3 triệu | 572 triệu | 94,5 % | 84,1 % | cùng bảng |
| OSNet x0,5 | 0,6 triệu | 273 triệu | 93,4 % | 82,6 % | cùng bảng |
| OSNet x0,25 | 0,2 triệu | 82 triệu | 92,2 % | 77,8 % | cùng bảng |
| TransReID | lớn | — | 95,0 % | 88,2 % | [repo: `research_notes/l1-signature-matching/coarse_to_full.md`] |

- Chênh giữa mô hình nhẹ (D3 ở node thường, x0,25) và mô hình đầy đủ ở AI node (D2, x1,0) trên cùng tập là 2,6 điểm Rank-1 và 7,1
  điểm mAP. Chênh do đổi miền (camera khác, tập khác) lớn hơn nhiều: Rank-1 rơi khoảng 55 điểm khi thử thẳng sang tập khác
  [repo: `research_notes/l1-signature-matching/cross_device_scores.md`]. Đổi quần áo còn 56–74 % Rank-1 [repo].
- Số dương tính giả tăng gần tuyến tính theo số phép so sánh [repo: `partial_set_thresholds.md`]. AI node giữ nhiều bản ghi hơn
  (ít critical cell) thì phải nâng ngưỡng để giữ cùng tỉ lệ báo động giả, nên recall giảm. Đây là một kênh thứ hai qua đó số
  critical cell ảnh hưởng pha 2.

## 5. Mạng và bộ nhớ

| Tham số | Giá trị | Cơ sở |
|---|---|---|
| Dung lượng một môi trường cell | khoảng 15 KB/s (99 B mỗi khung, khoảng 6,5 ms mỗi khung) | [repo: trace River, PLAN-K9-DATA mục 2] |
| Khung mỗi gói theo vai trò cell | 1,7 cell trung chuyển, 1,5 cell nguồn và đích, 1 mỗi cặp gateway | [repo: mô hình tải của `uav-coop2/tools/river_lb.py`, R² 0,89] |
| Tỉ lệ thời gian luồng nền được dùng | 10 / 20 % (đề xuất, chờ người dùng quyết) | PLAN-K9-DATA mục 7 |
| Tỉ lệ node là camera | 0,1 / 0,3 / 1 | [ước; chưa chốt: CONTEXT coi node là camera hoặc cảm biến] |
| Bộ nhớ AI node | thẻ 32–256 GB | [repo: CONTEXT mục 14] |
| Ứng viên AI node | node có `cpu` thuộc 20 % cao nhất của bản đồ (khoảng 4 ứng viên mỗi cell ở 816 node/km²) | PLAN-K9-DATA mục 3 |

## Nguồn web

- Gehl, *Hobart public life data* (Elizabeth Mall): https://www.hobartcity.com.au/files/assets/public/strategies-and-plans/gehl-report/04_final_report_-_public_life_data.pdf
- Vital City NYC, đếm người đi bộ Manhattan: https://www.vitalcitynyc.org/pedestrian-foot-tracking-nyc-map-model-mit.md
- Zhou et al., *Omni-Scale Feature Learning for Person Re-Identification*, ICCV 2019, arXiv 1905.00953: https://ar5iv.labs.arxiv.org/html/1905.00953
- Dữ liệu đếm theo giờ: City of Melbourne https://discover.data.vic.gov.au/dataset/pedestrian-counting-system-counts-per-hour ; Auckland https://www.hotcity.co.nz/pedestrians-in-the-city ; Dublin https://data.smartdublin.ie/dataset/dublin-city-centre-footfall-counters
