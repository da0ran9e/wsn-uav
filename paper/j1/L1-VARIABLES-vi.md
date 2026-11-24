---
status: current
updated: 2026-11-24
---
# J1 · Biến quyết định (bản bàn, chatlog mục 389)

Đầu vào là [bản tóm tắt bối cảnh](CONTEXT-SUMMARY-vi.md). File này liệt kê các thứ có thể chọn được trong hệ thống, chia theo lúc
quyết định, và đề xuất cái nào là biến của bài toán L1, cái nào cố định hay để thuật toán xử lý. Chưa chốt.

## 1. Quyết định trước sự cố (pha 0)

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| y_v ∈ {0, 1} | node mạnh v có làm AI node không (tập critical cell K suy ra từ y) | biến của L1 |
| x_uv ∈ {0, 1} | node thường u giao cho AI node v | biến của L1 |
| lưới cell, CL, cặp gateway | cấu trúc mạng | cố định (thủ tục pha 0) |
| cột đèn chuyển tiếp | đặt ở cell cần | cố định (quy tắc đã chốt) |
| lịch kênh | 7 màu cell, kênh cặp gateway, kênh 26 cho lượt bay | cố định (K1d) |

## 2. Quyết định cho pha 1 (tính sẵn ở pha 0, dùng khi có sự cố)

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| π | thứ tự các cụm trong tour | biến của L1 |
| q(t), v(t) | quỹ đạo và tốc độ UAV (Dubins, độ cao 100 m, tránh vùng cấm) | biến của L1 |
| s(t) | gói nào được phát lúc nào (từ đó suy ra đoạn gói mỗi cell SPINE giữ) | biến của L1 |
| vai trò River (SPINE, Bank, Ring) | cell nào giữ, nhận, chuyển gì | do thuật toán River sinh từ (K, q, s) |
| luồng Bank → Ring, cây dùng chung | đường đi trên đồ thị cell | do thuật toán (lập kế hoạch cân tải) sinh; có thể viết thành bài luồng nhiều hàng có sức chứa |
| T_fb, phân công vá | hạn và cách vá cell bị sót | tham số (quét) |

## 3. Quyết định ở pha 2

| Ký hiệu | Ý nghĩa | Đề xuất |
|---|---|---|
| t₂ | lúc đội 2 cất cánh | theo chính sách (cất cánh khi có báo cáo đầu tiên) |
| thứ tự thăm | cell nào xác minh trước | chính sách thích nghi theo xác suất (đã có trong repo) |

## 4. Đại lượng ngẫu nhiên và cho trước

- Ngẫu nhiên: kênh A2G và G2G, MAC, nhiễu, lần thấy của camera, báo cáo LoRa.
- Xấu nhất: vị trí người cần tìm (cell thật), lấy max.
- Cho trước: bản đồ, node, Q, tham số UAV, ρ, tỉ lệ NPU, K mô hình.

## 5. Câu hỏi cần quyết

1. L1 gồm cả biến pha 0 (y, x) và biến pha 1 (π, q, s) trong một bài, hay tách hai tầng (chọn critical cell rồi lập tour)?
2. Kế hoạch River là biến tường minh (luồng trên đồ thị cell) hay là một hàm thời gian mặt đất T_g(K, q, s) do thuật toán cho?
3. Pha 2 là chính sách cố định, hay đưa t₂ vào làm biến?

## 6. Trả lời (chatlog mục 392)

**Câu 1, chốt.** Pha 0 và pha 1 giải riêng. Tầng pha 0 chọn (y, x), tức tập critical cell K và phép giao node; tầng pha 1 nhận K
cố định rồi lập π, q, s. Tầng pha 0 vẫn cần một ước lượng thời gian pha 1 theo K để so các tập với nhau (ví dụ surrogate của K9,
`figures/k9-surrogate-vs-ns3.png`).

**Câu 2, đề xuất: coi River là hàm.** Thời gian pha 1 của critical cell k gồm phần nghe trực tiếp lúc UAV bay qua và phần mặt đất
T_g: các gói còn thiếu được cell lân cận chuyển tới theo kế hoạch River. Có hai cách đưa phần này vào bài toán.
- Tường minh: luồng River là biến (đoạn gói nào đi từ Bank nào, qua cell nào, tới node trợ giúp nào), ràng buộc mỗi cell một lúc chỉ
  một radio phát. Bài thành bài luồng nhiều hàng có sức chứa ghép với π, q, s; nhiều biến nguyên, khó giải tới tối ưu ở hàng trăm
  cell.
- Hàm: River là thủ tục có sẵn. Cho (K, q, s), `uav-coop2/tools/river_lb.py` sinh kế hoạch, mô hình tải (hiệu chỉnh trên trace,
  R² 0,89) cho ra T_g(K, q, s) của từng critical cell. L1 chỉ tối ưu π, q, s và gọi hàm này mỗi lần đánh giá một phương án. Chặn
  dưới LP (`--lp`) cho biết River cách tối ưu bao xa.

**Câu 3, đề xuất: cố định chính sách pha 2.** Chính sách gồm lúc đội 2 cất cánh t₂ và thứ tự thăm các cell nghi vấn. Cố định
nghĩa là L1 không tối ưu hai thứ này mà dùng quy tắc sẵn: t₂ là lúc có báo cáo đầu tiên (CONTEXT mục 33); thứ tự thăm theo xác
suất hậu nghiệm trên thời gian bay tới (bản thảo, `draft-v1/tex/sec-model.tex`), mỗi lần xác minh V1 khoảng 78 s, dừng khi xác
nhận đúng. Thời gian pha 2 khi đó là kết quả mô phỏng, phụ thuộc pha 1 qua thời điểm và độ chính xác của các báo cáo. Đưa t₂ và
thứ tự thăm vào làm biến thì pha 2 thành bài tìm kiếm ngẫu nhiên riêng, nặng và lệch khỏi trọng tâm của bài. Phần đánh giá có thể
so vài quy tắc (cất cánh ở báo cáo đầu tiên, hay đợi pha 1 xong).

## 7. Chốt câu 2 và 3 (chatlog mục 393)

**Câu 2.** Phần mặt đất đưa vào bài tối ưu (cách tường minh). Đề xuất cách viết: biến luồng f theo từng critical cell k và từng
nhóm đoạn gói, đi trên đồ thị cell từ Bank tới node trợ giúp; ràng buộc sức chứa mỗi môi trường (cell, cặp gateway: một radio phát
một lúc) theo khe thời gian; thời gian xong của k là lúc UAV qua cộng thời gian mặt đất do f quyết định. Để giải được: vòng ngoài
tìm (π, q, s), vòng trong giải LP của luồng (bản đầu là LP tải lớn nhất trong `river_lb.py --lp`), làm tròn ra kế hoạch nguyên bằng
bộ lập kế hoạch cân tải. River gốc là một nghiệm khả thi của bài này, LP là chặn dưới.

**Câu 3.** Pha 2 cũng là đối tượng tối ưu, cần tìm hiểu thêm. Đặt bài: cho bản đồ xác suất hậu nghiệm trên các cell nghi vấn (cập
nhật mỗi khi có báo cáo), chọn t₂ và lộ trình đội 2 để tối thiểu thời gian tới khi xác nhận đúng (phân vị 0,9 hoặc kỳ vọng).
- Bản tĩnh (đủ báo cáo, mục tiêu đứng yên, xác minh gần chắc chắn): tối thiểu kỳ vọng là bài độ trễ nhỏ nhất có trọng số, một dạng
  của bài đường đi tìm kiếm tối ưu, NP-khó (Trummel và Weisinger 1986) [web]. Quy tắc hiện tại (xác suất trên thời gian bay) là
  heuristic tham lam của bài này.
- Bản động: báo cáo tới dần trong lúc pha 1 chạy, nên là bài trực tuyến; hướng làm là giải lại khi có báo cáo mới (rolling horizon).
- t₂: cất cánh sớm thì đến gần vùng nghi vấn sớm nhưng có thể bay phí, đợi thì có thêm thông tin.
- Kiểm chất lượng: với ít cell nghi vấn (khoảng 15 trở xuống) giải đúng bằng quy hoạch động để so với tham lam.
- Câu còn mở: tối ưu pha 2 khi kế hoạch pha 1 đã cố định, hay chọn thứ tự cụm của pha 1 cùng với pha 2 (thứ tự cụm quyết định lúc
  báo cáo tới).

## 8. Các mục tiêu tối ưu (chatlog mục 394)

Một mục tiêu chung cho cả bài, mỗi bài con một mục tiêu riêng thay cho nó.

| Mức | Biến | Mục tiêu | Ràng buộc chính |
|---|---|---|---|
| Chung | toàn bộ | tối thiểu phân vị 0,9 của T\* (lúc xác nhận đúng người, tính từ cất cánh), báo kèm trung bình | sức bền hai UAV |
| Pha 0 | y, x | tối thiểu ước lượng phân vị 0,9 của T\* theo tập K (surrogate, vì pha 0 giải riêng) | H chặng, bộ nhớ, luồng nền |
| Pha 1 | π, q, s, luồng mặt đất f | tối thiểu phân vị 0,9 của lúc critical cell cuối cùng nhận đủ truy vấn | Dubins, vùng cấm, sức chứa môi trường |
| Pha 2 | t₂, lộ trình đội 2 | tối thiểu thời gian tới khi xác nhận đúng, theo bản đồ xác suất hậu nghiệm | sức bền đội 2 |

Câu còn mở:
- Phân vị 0,9 lấy qua phần ngẫu nhiên (kênh, MAC, lần thấy) với vị trí người lấy xấu nhất, hay lấy qua cả vị trí người theo tiên
  nghiệm đều? Cách đầu khớp "trường hợp xấu nhất" của mục 13; cách sau mềm hơn và khớp tiên nghiệm đều (mục 384).
- Mục tiêu pha 2 dùng cùng thước đo với mục tiêu chung (phân vị 0,9) hay kỳ vọng (bài độ trễ nhỏ nhất có trọng số dùng kỳ vọng)?
- Pha 1 tối ưu riêng như trên, hay chọn cùng pha 2 (mục 7)? Nếu chọn cùng thì mục tiêu pha 1 thay bằng mục tiêu chung.

Dạng cốt lõi của ba bài (biến, ràng buộc, mục tiêu, lớp bài kinh điển) ở [PROBLEMS-vi.md](PROBLEMS-vi.md) (chatlog mục 399).
