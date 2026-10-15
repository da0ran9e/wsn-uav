# Baseline và ablation — keyword

Lời gốc: CLAUDE.md §8 mục 81. Mã: `uav-l2/tools/mission_baselines.py`, `mission_policy.py`, `uav-coop2/examples/coop2-river.cc`.

## Chung cho mọi phương án
- cùng bản đồ · cùng kênh (hash theo cặp node) · cùng lượt bốc nghi vấn, điểm nghi vấn, pha LoRa → **so cặp**
- radio: 802.15.4 · unicast 6,88 ms/khung (CSMA + ACK) · broadcast 10 ms/khung, không ACK
- multicast: fountain lý tưởng · xong khi node kém nhất đủ: khung / (1 − PER_max) · PER theo A2G (m = 1,8)
- xác minh (đội 2): ổn định 5 s + tệp lớn 1 MB unicast (≈ 73 s) + đối sánh 5 s ≈ 83 s
- UAV cánh quay 15 m/s · một UAV mỗi đội · chưa tính năng lượng

## Phương án đề xuất (P)
- cánh bằng 50 m/s · một lượt qua mỗi cluster · đường thẳng qua CH (hướng dài nhất)
- River (ns-3) → đối sánh → CH → LoRa (một bản tin / 40 s) → BS
- đội 2: đi sớm · chọn theo điểm / thời gian · tour đội 1 l3first

## Baseline — bỏ hoặc thay pha 1
| | Pha 1 | Giao gì | Mô hình | Cô lập điều gì |
|---|---|---|---|---|
| **B1** | không | tệp lớn | 1 UAV cánh quay · TSP (NN + 2-opt) qua mọi critical cell · unicast · chờ đối sánh · dừng ở cell thật | giá trị của cả pha 1 |
| **B2-r** | không | tệp lớn | gom critical cell trong bán kính r (phủ tham lam) · hover tâm nhóm · multicast · chờ đối sánh | multicast thay cho pha 1 |
| **B3-r** | cánh quay | tệp nhẹ (≈ \|D\| trung bình) | hover multicast theo nhóm r → đối sánh → LoRa → đội 2 như P | cánh bằng + River vs cánh quay hover |
| **B6** | cánh quay | tệp nhẹ | hover từng critical cell · unicast → LoRa → đội 2 như P | như B3, nhóm cỡ 1 |
| **B5** | cánh bằng quét luống | như P | Dubins quét luống, khoảng luống 700 m–1 km · **chưa làm** (cần River cho nhiều luống) | đường bay (lớp 2) |

## Baseline — bỏ hợp tác / cận dưới
| | Mô hình | Cô lập điều gì |
|---|---|---|
| **B4-t** | như P nhưng không River · critical cell dùng phần cả cell nhận được (gom nội cell) · phát hiện nếu giữ ≥ t của D (t = 0,85 / 0,9 / 0,95, ngưỡng tạm) · không thì thất bại | giá trị của hợp tác (lớp 3) |
| **B7** | đội 2 biết trước cell thật · bay thẳng lúc t = 0 · xác minh · về | cận dưới, để chuẩn hoá |

## Ablation lớp 3 (ns-3, trong cluster)
- **kéo thẳng:** critical cell hỏi thẳng từng cell Axe · không Bank, không Circle
- **Circle chuẩn bị sẵn / theo yêu cầu:** thành viên lấy trước hoặc chỉ khi được hỏi
- **Circle động:** số thành viên theo lượng thiếu (tới 12, vòng 1–2) · cố định 12
- **số màu kênh:** 3 / 4 / 7 / 13
- **độ rộng River:** 2,5 / 3,5 / 4,5 / 6,5 cell
- **số critical cell:** 1 / 4 / 10 / 16 (đổi ngưỡng kg, kl)
- **chọn gateway:** theo hình học / theo chất lượng liên kết

## Ablation chính sách (tầng nhiệm vụ, 2 × 2 × 2)
- **tour đội 1:** ngắn nhất · l3first (dự báo L3 từ maxFar)
- **đội 2 xuất phát:** chờ đủ báo cáo · đi sớm
- **thứ tự thăm:** TSP · điểm / thời gian

## Chỉ số
- thời gian critical cell cuối đủ D · số khung MAC
- kết thúc nhiệm vụ · tỉ lệ tìm thấy cell thật · số lần thăm
- so cặp: chênh trung bình, tỉ lệ lượt / bản đồ tốt hơn

## Còn thiếu / cần chốt
- B5 (quét luống): cách áp River cho nhiều luống
- mô hình lớp 1 thay ngưỡng t của B4 · kích thước tệp lớn
- B8 (cánh bằng bay qua từng critical cell) — đã đề xuất, chưa chốt
