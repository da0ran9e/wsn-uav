# Baseline và ablation — keyword

Lời gốc: CLAUDE.md §8 mục 81; cập nhật theo mục 110–114 (mô hình lớp 1 mới, pha 2 hoàn thành khi xác minh xong c\*).
Mã: `uav-l2/tools/l1_rank.py` (mọi phương án), `uav-l2/tools/subch.py`, `uav-l2/tools/mission.py --partition subch`, `uav-l2/tools/meander_mission.py`, `uav-coop2/examples/coop2-river.cc`.
Kết quả: `uav-l2/docs/L1-MISSION2-vi.md`.

## Chung cho mọi phương án
- cùng bản đồ · cùng kho ảnh của từng camera (gắn theo cell, nên giống nhau dù cách chia khác) · cùng nhiễu đối sánh · cùng pha LoRa → **so cặp**
- **chỉ số chính: T\*** = lúc đội 2 xác minh xong c\*, cell có điểm xác minh cao nhất trong các critical cell của phương án đó · phụ: hạng của c\* trong thứ tự thăm, T_all (thăm hết rồi về BS)
- radio: 802.15.4 · unicast 6,88 ms/khung (CSMA + ACK) · broadcast 10 ms/khung, không ACK
- multicast: fountain lý tưởng · xong khi node kém nhất đủ: khung / (1 − PER_max) · PER theo A2G (m = 1,8)
- xác minh (đội 2): ổn định 5 s + bộ tham chiếu đầy đủ 1 MB unicast (≈ 72,9 s) + đối sánh ≈ 0,2 s ≈ 78,1 s
- UAV cánh quay 15 m/s · một UAV mỗi đội · chưa tính năng lượng

## Phương án đề xuất (P\*)
- lớp 2: cluster ≤ 80 cell · đường thẳng qua CH (hướng dài nhất) · tour đội 1 theo **độ trễ có trọng số** (Σ số critical cell × lúc rời cluster)
- lớp 1: 12 manh mối (mặt, dáng, bộ phận), r và w do BS đặt · phát xen kẽ · điểm hai bước
- lớp 3: River cửa sổ 400 kB quanh CH (ns‑3)
- phản hồi: **báo hai lần** (sau gom nội cell, sau River) · CH → LoRa (một bản tin / 40 s)
- pha 2: BS tính P(c\*) · đội 2 **cất cánh cùng đội 1** · đi xác minh khi P ≥ P_U / 4 (P_U: xác suất c\* nằm trong các cell chưa báo), không thì **đón đầu** về tâm xác suất · chọn theo P / (bay + xác minh) · thăm hết

## Ablation của P\* (mỗi cái đổi một phần)
| Tên | Đổi gì |
|---|---|
| đi ở báo cáo đầu | đội 2 cất cánh khi có báo cáo đầu tiên thay vì t = 0 |
| chỉ báo sau River | bỏ báo cáo lần 1 |
| **không hợp tác (B4)** | bỏ River: cell chỉ dùng manh mối tự nghe được |
| tour l3first / tour ngắn nhất | thay tour theo độ trễ |
| ngưỡng chờ β | β = 0 (đi ngay, vẫn đón đầu) · 1/2 · 1 thay cho 1/4 |
| ngưỡng theo thời gian | P_U chỉ tính các cell sẽ báo trong lúc đội 2 bận với cell này (không tham số) |
| đội 2 tham lam | quy tắc cũ: đi ngay ở báo cáo đầu, không chờ, không đón đầu |
| chờ không đón đầu | chờ tại chỗ |
| xếp nhóm | phát theo khía cạnh thay xen kẽ (với và không có River) |
| trọng số đều | bỏ độ quan trọng |
| P cũ | River, báo một lần, tour l3first, tham lam (phương án của vòng trước) |

## Ablation và baseline lớp 2 (cách chia cluster, cùng chính sách P\*)
| Tên | Cluster | Ghi chú |
|---|---|---|
| **cluster có sẵn** | k‑medoids ≤ 80 cell | trước đây là P; nay là ablation "không tái cấu trúc" (mục 114) |
| **MEANDER** | luồng cong theo địa hình, Bank cục bộ | tái cấu trúc của lớp 2 (mục 103–106) |
| **subCH** | cluster có sẵn cắt quanh các critical cell cách nhau ≥ 6 cell (gộp mảnh < 20 cell); mỗi cluster con bay qua CH của nó | baseline mới (mục 114) |
| LANE | luồng thẳng 4,5 cell | chỉ còn 3 bản đồ (vòng 1); bỏ khỏi chiến dịch 40 bản đồ |

## Baseline — bỏ hoặc thay pha 1
| | Pha 1 | Giao gì | Mô hình | Cô lập điều gì |
|---|---|---|---|---|
| **B1** | không | bộ tham chiếu đầy đủ | 1 UAV cánh quay · TSP (NN + 2‑opt) qua mọi critical cell từ t = 0 · unicast · chờ đối sánh | giá trị của cả pha 1 |
| **B2‑r** | không | bộ tham chiếu đầy đủ | gom critical cell trong bán kính r (phủ tham lam) · hover tâm nhóm · multicast | multicast thay cho pha 1 |
| **B3‑r** | cánh quay | bộ manh mối (400 kB) | hover multicast theo nhóm r → đối sánh → LoRa → đội 2 như P\* | cánh bằng + River vs cánh quay hover |
| **B6** | cánh quay | bộ manh mối | hover từng critical cell · unicast → LoRa → đội 2 như P\* | như B3, nhóm cỡ 1 |
| **B7** | — | — | đội 2 biết trước c\*, bay thẳng lúc t = 0, xác minh | cận dưới |
| **B8‑r** | cánh bằng (đội 1) | bộ manh mối | bay thẳng tới tâm từng nhóm r (như B3), **bay vòng** bán kính 255 m quanh tâm, multicast tới khi node kém nhất đủ (fountain lý tưởng, PER trung bình trên vòng) → LoRa → đội 2 như P\* · không River | cánh bằng tự phục vụ thay cho River |
| **B5** | cánh bằng quét luống | bộ manh mối, phát lặp liên tục | đường luống của SWATH phủ cả miền (Dubins ở đầu luống), một khung mỗi 0,5 m · thu như pass: cell có khung khi một node của nó có (PER A2G độc lập từng node), có manh mối khi đủ mọi khung của một bản · luống rộng nhất trong 12…3 cell mà mọi critical cell đủ 12 manh mối · không River · báo khi đủ (hoặc sau khung cuối trong 1,5 km) + gom nội cell + đối sánh → LoRa → đội 2 như P\* | đường bay phủ kín thay cho hợp tác |

## Ablation lớp 1 (ngoài nhiệm vụ, `paper/L1-MODEL-vi.md` §4)
- đủ / thiếu manh mối · nửa luồng xen kẽ / xếp nhóm · thiếu mặt · chỉ bộ phận · trọng số đều
- độ nhạy: D (64 / 128 / 256) · tỉ lệ người mặc giống (0 / 2 / 5 %) · M (105 / 223 / 693)

## Ablation lớp 3 (ns‑3, trong cluster; giữ từ trước)
- kéo thẳng · Circle chuẩn bị sẵn / theo yêu cầu / động · số màu kênh · độ rộng River · số critical cell · chọn gateway
- **Trickle** (mục 134, 139; `coop2-river.cc --scheme=trickle`): phổ biến kiểu Deluge, không kế hoạch, trên **cùng các cell, cùng lưới kênh và gateway** với River. Đối tượng = mọi gói mà một critical cell nào đó cần, chia trang 64 gói; mỗi cell gom về CL phần node của nó có; CL chạy bộ định thời Trickle (RFC 6206; Imin 1 s, Imax 64 s, k = 1): giữa nửa sau mỗi khoảng, nếu chưa nghe đủ k quảng bá trùng khớp thì gửi mỗi cell kề danh sách trang đã đủ; cell nghe thấy trang mình thiếu thì xin hàng xóm đó phần còn thiếu của trang thấp nhất (một yêu cầu một lúc, hỏi lại sau hạn chờ); cell thấy hàng xóm thiếu trang của mình hoặc vừa đủ một trang thì đặt lại khoảng về Imin. Ở cấp nhiệm vụ: phương án `Pt+prog`.

## Còn thiếu / cần chốt
- tham số lớp 1 cần neo vào số đo thật (trước hết D), kích thước tệp lớn
- N: 10 bản đồ mỗi cỡ, dưới quy tắc N ≥ 120
