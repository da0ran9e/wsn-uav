---
status: current
updated: 2026-11-26
---
# Bản thảo journal v2 (J1), kịch bản rừng: hướng dẫn đọc

Soạn theo chatlog mục 412: viết lại phần đầu bài tới phát biểu bài toán theo kịch bản rừng đất thấp ([CONTEXT-vi.md](../CONTEXT-vi.md)),
có hình minh hoạ. Bài viết tiếng Anh, khuôn IEEEtran: `tex/main.pdf`, 8 trang. Mục VI–X (chặn, thuật toán, đánh giá, thảo luận) chưa
viết lại; phần cũ còn ở [draft-v1](../draft-v1/README-vi.md). Dựng lại PDF: `tex/build.sh` (cần TeX Live có IEEEtran).

Trong PDF, chữ đỏ [TODO] là việc phải làm hoặc số phải kiểm, chữ xanh [OPEN] là câu chưa chốt trong bối cảnh.

## Cấu trúc bài

| Mục | Tệp | Nội dung |
|---|---|---|
| Tóm tắt, tên bài | `tex/main.tex` | tên mới nói cả ba pha; câu kết quả để trống |
| I Introduction | `tex/sec-intro.tex` | SAR trong vườn quốc gia, rừng đang được gắn thiết bị, vì sao LoRa và mạng mặt đất từ trạm không đủ, vì sao phát thẳng từ UAV hỏng dưới tán (Hình 2, chặn phủ), ý chính, ba pha và đánh đổi, mục tiêu, đóng góp |
| II Related work | như trên | thêm nhóm mạng và kênh trong rừng, nhóm lý thuyết tìm kiếm và hành vi người đi lạc |
| III System operation | `tex/sec-system.tex` | bốn bước bằng lời, không ký hiệu (theo mẫu GAMBAC) |
| IV System model | `tex/sec-model.tex` | địa hình (Bảng II), mạng và mật độ (Hình 4), năng lượng và đánh thức, UAV, kênh A2G qua tán (Hình 5, 6), kênh G2G dưới tán, truy vấn, dữ liệu nền, tiên nghiệm, T\* và phân vị |
| V Problem formulation | `tex/sec-problem.tex` | (P0), (P1), (P2) theo [PROBLEMS-vi](../archive/urban-v1/PROBLEMS-vi.md) của bản đô thị, thêm cho rừng: tập AI node ứng viên nhỏ (cần chỗ trống), ràng buộc năng lượng (6e) và cửa sổ thức trong (P1); Bảng III nối ba bài; Định lý 1 và nhận xét độ khó |
| Tài liệu tham khảo | `tex/refs.tex` | 35 mục, 19 lấy từ draft-v1 |

## Hình

| Hình | Tệp | Nguồn |
|---|---|---|
| 1 | `figures/draft2-scenario-cattien-labelled.png` | mới; đường mòn, suối thật từ OSM, phần còn lại minh hoạ |
| 2 | `draft-v1/figs/bound-nc.png` | dùng lại, cần vẽ lại trên bản đồ rừng |
| 3 | `figures/draft2-phases-labelled.png` | mới |
| 4 | `figures/draft2-density-gap-labelled.png` | mới, số ở CONTEXT mục 5 |
| 5 | `figures/draft2-canopy-loss-labelled.png` | mới, Weissberger |
| 6 | `draft-v1/figs/nd1-channel-p-of-d-model-vs-ns3.png` | dùng lại |
| 7 | `draft-v1/figs/concept-river.png` | dùng lại, cần vẽ lại có critical cell |

Script: `paper/j1/analysis/fig_draft_v2.py`; log `logs/2026-11-26_1800-draft-v2/`.

## Các lựa chọn tôi tạm đặt khi viết (cần bạn xem)

1. Tiên nghiệm viết dạng tổng quát π, nêu hai trường hợp (đều, và quanh điểm thấy cuối theo phân bố khoảng cách của Koester); chưa
   chọn trường hợp chính.
2. Phân vị 0,9 lấy chung qua (ω, c\*); cách trường hợp xấu nhất theo c\* ghi là câu mở.
3. Mật độ 816 thiết bị/km² ghi thẳng là giả định hướng tới tương lai, kèm Hình 4 so với triển khai thật.
4. Ràng buộc năng lượng đặt theo cell trong (P1); (P0) chưa có ràng buộc năng lượng cho luồng nền.
5. Kênh G2G giữ mô hình log-distance của bản cũ cộng suy hao tán Weissberger; ghi rõ có thể tính trùng và cần mô hình đo trong rừng.
6. Độ khó của (P0) và (P2) mới ở dạng nhận xét (chứa SSCFLP, chứa bài độ trễ nhỏ nhất có trọng số), chưa thành mệnh đề có chứng minh.

## Số cần kiểm trước khi dùng

- Số vụ SAR của NPS (2 890 năm 2017; 11,2 vụ/ngày 1992–2007) lấy từ đoạn trích tìm kiếm, chưa đọc toàn văn Heggie và Amundson 2009.
- Số chặng 50–95 và thời gian 20 phút tới hơn một giờ của mạng mặt đất tính trên bản đồ đô thị k8, cần tính lại trên bản đồ rừng.
- Ngưỡng lưới liền khoảng 300 thiết bị/km² dùng mô hình phố đô thị, cần tính lại với suy hao tán.
- Thông tin xuất bản của Zhan 2018, Bakker 2025, Weissberger 1982, Koester 1998 chưa đối chiếu (đánh dấu trong `refs.tex`).
