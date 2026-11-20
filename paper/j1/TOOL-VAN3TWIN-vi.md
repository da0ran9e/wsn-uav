---
status: current
updated: 2026-11-20
---
# VaN3Twin: có dùng được cho J1 không (2026-11-20, chatlog mục 361)

Tìm hiểu trong session riêng, chưa build hay chạy gì. Nguồn ghi ở từng ý: [mã] là đọc mã nguồn VaN3Twin (clone nông ở
commit `c8fd5aa`, 2026-10-06), [bài] là bài arXiv 2505.14184 v3, [repo] là tài liệu trong repo này.

## VaN3Twin là gì

VaN3Twin là ms-van3t đổi tên và thêm ray tracing: bộ module ns-3 cho mô phỏng V2X theo chuẩn ETSI (802.11p, LTE-V2X,
NR-V2X), xe chạy theo SUMO qua TraCI, có thể nối CARLA, và từ 2025 nối Sionna RT của NVIDIA [mã: README]. Giấy phép
GPL-2.0, nhóm Politecnico di Torino và Milano, commit cuối 2026-10-06, nên vẫn được bảo trì.

Nền ns-3 là nhánh `ns-3-dev-v2x-v0.2` của CTTC (5G-LENA), khai báo `NS3_VERSION=3.35`, RELEASE_NOTES đến 3.36.1
[mã: `sandbox_builder.sh`]. Script cài đặt chép đè vào module `propagation` và `spectrum` của ns-3 các file đã sửa, và
sửa cả `yans-wifi-phy.h`. Mô phỏng của ta chạy trên ns-3.46, cách khoảng 10 bản.

## Phần ray tracing chạy thế nào

- ns-3 nói chuyện với một tiến trình Python chạy Sionna RT qua UDP, đồng bộ, timeout 120 s [mã:
  `sionna-connection-handler.cc`].
- Lớp gốc `PropagationLossModel::CalcRxPower` bị sửa: khi bật Sionna thì mỗi lần tính công suất thu đều hỏi path gain và
  LoS từ Sionna rồi dùng số đó thay số của mô hình ns-3 [mã: `files/propagation/propagation-loss-model.cc`]. Vì sửa ở lớp
  gốc nên về nguyên tắc mọi công nghệ dùng `PropagationLossModel` đều đi qua đây, kể cả lr-wpan.
- Vật thể được nhận diện theo tên `car_<id>` và vị trí gửi bằng `LOC_UPDATE`. Khi một cặp chưa có trong cache, server
  dò tia cho mọi cặp giữa mọi vật thể đang có. Một vật thể dời quá 3 m (mặc định) là xoá toàn bộ cache [mã:
  `sionna_v1_server_script.py`, `compute_rays`, `manage_location_message`].
- Mặc định 5 lần tương tác, 10⁴ mẫu tia mỗi nguồn, 5,89 GHz, GPU mặc định 2 [mã: tham số dòng lệnh]. Cảnh dựng trong
  Blender 3.6 với addon mitsuba-blender, toà nhà lấy từ OSM qua addon Blosm [mã: README; bài: mục II-A].
- Quy mô đã thử trong bài: 5 tới 60 xe; mỗi lần dò toàn bộ mất trung bình 168 ms (5 xe) tới 446 ms (60 xe) trên RTX 3090,
  cache trúng 93–99 % [bài: bảng V, đọc qua bản tóm tắt, chưa đối chiếu bảng gốc].
- So với đo thật (802.11p, CAM): chênh lệch tỉ lệ nhận gói giữa mô phỏng và đo ở đô thị giảm từ 27,9 % (ms-van3t, mô hình
  thống kê) xuống 8,2 % [bài: mục III, cùng lưu ý trên]. Bài không có UAV, không có 802.15.4.

## Đối chiếu với nhu cầu của J1

| Nhu cầu | VaN3Twin | Đánh giá |
|---|---|---|
| 802.15.4 (lr-wpan) | Không có; ngăn xếp là ITS-G5 và C-V2X | Phải tự ghép lr-wpan của ns-3.35 |
| ns-3.46 | Nền 3.35, chép đè file lõi | Hoặc lùi mã của ta về 3.35, hoặc tự chuyển phần Sionna lên 3.46 |
| Khoảng 13 000 node | Dò tia mọi cặp, đã thử tới 60 vật thể | Không chạy được ở quy mô này |
| UAV bay liên tục | Dời 3 m là xoá cache và dò lại tất cả | UAV 10 m/s thì 0,3 s dò lại một lần, mỗi lần với mọi node |
| Bản đồ OSM thật (K14) | Cảnh lấy từ OSM qua Blender | Ta đã có đường viền và chiều cao từ `osm_district.py`, chỉ thiếu bước xuất mesh |
| Phần cứng | Bài dùng GPU RTX 3090 | Container cloud không có GPU (4 nhân, 15 GB RAM); Sionna chạy CPU được nhưng chậm hơn, chưa đo |

Phần đáng giá với ta là Sionna RT. Lớp V2X, SUMO, CARLA của VaN3Twin không dùng được, và cách nó gọi Sionna theo từng lần
truyền chỉ hợp với vài chục vật thể.

## Các phương án

1. Dùng nguyên VaN3Twin. Không nên: phải lùi về ns-3.35 hoặc chuyển bản vá lõi lên 3.46, thêm 802.15.4, và vẫn vướng
   quy mô. Chi phí lớn nhất trong các phương án, lợi ít nhất.
2. Lấy riêng đoạn nối ns-3 với Sionna (khoảng 400 dòng C++ và 600 dòng Python) ghép vào ns-3.46. Phần chép thì rẻ, nhưng
   cơ chế hỏi theo từng gói và dò mọi cặp phải viết lại gần hết mới chạy được với hàng nghìn node, nên lợi chẳng hơn
   phương án 3.
3. Dùng thẳng Sionna RT ngoại tuyến, không qua VaN3Twin. Node đứng yên, nên G2G chỉ cần dò một lần cho các cặp trong
   khoảng 150 m của một khu bản đồ, lưu bảng path gain và cờ LoS; A2G dò từ các điểm lơ lửng hoặc một lưới điểm trên
   đường bay ở độ cao 100 m xuống node (Sionna có radio map cho việc này). ns-3.46 chỉ đọc bảng, kiểu
   `MatrixPropagationLossModel`. Mesh toà nhà sinh thẳng từ đa giác OSM đã có (đùn theo chiều cao), không cần Blender.
4. Chỉ tham khảo. Trích bài VaN3Twin làm bằng chứng rằng mô hình thống kê và ray tracing cho tỉ lệ nhận gói khác nhau rõ
   ở đô thị, để biện minh cho LoS hình học ở K1a, K1c.

## Đề xuất

Không dùng VaN3Twin. K1a, K1c và phần ns-3 của K14 giữ hướng đang có: LoS A2G bằng hình học từ chiều cao toà nhà, xác suất
LoS theo góc ngẩng, suy hao xuyên tường cho G2G [repo: `PLAN-TRACKS-vi.md` K1a, K1c, K14]. Cách này rẻ và chạy được ở
13 000 node.

Phương án 3 đáng giữ làm bước hiệu chỉnh tuỳ chọn cho K1c: dò tia trên một ô nhỏ (khoảng 0,4 km² của Punggol hoặc
Downtown Core, vài trăm node) để chỉnh con số 15 dB mỗi toà và đường P_LoS theo góc ngẩng, rồi đưa kết quả vào mô hình
hình học. Việc này chưa cần cho J1 và chưa ước lượng được thời gian chạy: phải cài `sionna` (kéo theo TensorFlow,
Mitsuba, Dr.Jit), thử trên CPU với một ô nhỏ rồi mới bàn tiếp. Cần kiểm thêm vật liệu ITU của Sionna có hợp với 2,4 GHz
không (theo tài liệu Sionna thì có, tôi chưa kiểm lại).

Phương án 4 làm được ngay khi viết phần kênh của bài, nếu người dùng muốn ghi chú bài VaN3Twin.

## Bài báo nên cân nhắc ghi chú

- Pegurri và cs., "VaN3Twin: the Multi-Technology V2X Digital Twin with Ray-Tracing in the Loop", arXiv 2505.14184
  (https://arxiv.org/abs/2505.14184): số liệu đo so mô phỏng ở đô thị và chi phí dò tia, dùng cho phương án 4.
- Hoydis và cs., "Sionna RT: Differentiable Ray Tracing for Radio Propagation Modeling", arXiv 2303.11103
  (https://arxiv.org/abs/2303.11103): chỉ cần nếu chọn phương án 3.
