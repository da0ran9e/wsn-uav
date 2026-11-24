---
status: current
updated: 2026-11-23
---
# J1 · Dàn ý bài (chatlog mục 396)

Dàn ý ghép quyết định bối cảnh (CONTEXT-SUMMARY, L1-VARIABLES), kết quả kỹ thuật ([RESULTS-vi.md](RESULTS-vi.md)) và cách viết học
từ hai bài mẫu (`research_notes/literature/papers/nguyen2021-hole.md`, `nguyen2023-gambac.md`, chatlog mục 395). Mỗi mục ghi:
- nội dung;
- nguồn số liệu;
- trạng thái: **có** (số và chữ đã có), **sửa** (có trong bản thảo nhưng phải viết lại theo quyết định mới), **thiếu** (chưa có
  số hoặc chưa quyết).

Bản thảo hiện tại là `draft-v1/tex/` (kịch bản ICC, bản đồ C4); dàn ý này là đích để viết lại.

Ký hiệu bài toán theo pha: (P0) chọn AI cell, (P1) pha 1, (P2) pha 2. Bài (P0) trong bản thảo cũ (quỹ đạo cùng lịch mặt đất) đổi
thành (P1).

## Tên bài và tóm tắt

- Tên bài hiện tại: "Flight Geometry Is the Schedule: Pre-Planned Ground Cooperation for Single-Pass UAV Query Delivery to
  Edge-Camera Networks". Tên này nói về pha 1, nên cần xét lại khi bài có cả pha 0 và pha 2 (học từ lỗi tên lệch mục tiêu của
  GAMBAC). **thiếu**
- Tóm tắt gồm năm ý:
  1. bài toán tìm người trong đô thị bằng mạng camera không nối Internet;
  2. ba pha và mục tiêu phân vị 0,9 của T\*;
  3. kết quả lý thuyết (NP-khó, chặn phủ, chặn mặt đất);
  4. thuật toán (chọn AI cell, LM-Tour, River cân tải);
  5. số chính (nhanh hơn FC 59–72 % ở tầm ngắn, nhanh hơn không phát 3,5–5,8 lần).

## I. Introduction

Thứ tự đoạn theo mẫu k-MLP và GAMBAC:
1. **Kịch bản thật có hình.** Một người mất tích trong một quận như Hoàng Mai, mạng camera dày (chuông cửa, camera tường, máy bán
   hàng) nhưng không nối Internet và giữ ảnh tại chỗ. Hình bản đồ quận (`figures/map-hoangmai-labelled.png`). Tần suất khoảng
   22 vụ trên 100 000 dân mỗi năm. **có** (CONTEXT mục 1, 15, 23)
2. **Ba cách hiện có và chỗ hỏng.**
   - LoRa mất 1,8–18 h.
   - Flood mặt đất phải đi 50–95 chặng, mất 20 phút tới hơn một giờ.
   - UAV phát thẳng có mã fountain bị chặn bởi Định lý 2 khi tầm ngắn.

   Cần một hình minh hoạ chỗ hỏng, theo kiểu Fig. 2–3 của k-MLP, ví dụ chặn phủ theo R50 (`draft-v1/figs/bound-nc.png`).
   **có số, thiếu hình**
3. **Chia nhiệm vụ và nêu đánh đổi.**
   - Pha 0 chọn AI cell trước sự cố.
   - Pha 1 có UAV cánh bằng phát truy vấn một lượt, mạng mặt đất chuyển phần còn thiếu.
   - Pha 2 có UAV cánh quay xác minh.
   - Đánh đổi: nhiều AI cell thì luồng nền nhẹ hơn mỗi cell nhưng pha 1 nặng hơn; bay sát critical cell thì đường dài hơn. **có**
4. **Một câu mục tiêu.** Tối thiểu phân vị 0,9 của thời gian từ cất cánh tới lúc xác nhận đúng người, với ràng buộc luồng nền, số
   chặng, bộ nhớ và sức bền UAV. **sửa** (chờ chốt phân vị lấy qua những gì)
5. **Đóng góp,** mỗi ý kèm loại kết quả:
   - phát biểu ba bài và độ khó (định lý);
   - chặn của cách không hợp tác và chặn mặt đất (định lý, mệnh đề);
   - thuật toán chọn AI cell, đường bay và vận chuyển mặt đất cân tải;
   - so với nghiệm đúng hoặc chặn LP ở bài nhỏ;
   - đánh giá ns-3 trên bản đồ tổng hợp và bản đồ thật. **sửa**
6. **Bảng tóm tắt kết quả** ngay sau phần đóng góp, theo Bảng 1 của k-MLP: T\*, mức hơn baseline, khoảng cách tới chặn.
   **thiếu** (chờ số nhiều seed)

## II. Related work

Xếp theo hướng tiếp cận, mỗi hướng một câu về chỗ nó không giải được bài của mình. **sửa** (bản thảo đã viết lại theo đợt ngày
12/11, cần thêm hai nhóm cuối)
- UAV phát chung xuống mặt đất (Zeng 2018): một chặng, không hợp tác mặt đất.
- UAV thu dữ liệu, phân cụm và lập tour (GAMBAC 2023, CHP): hướng ngược (thu lên), có ràng buộc quãng bay.
- DTSP và DTSP-N (Le Ny, Isaacs, Savla): chỉ phần bay.
- Phổ biến dữ liệu trong WSN (Deluge, Splash, Pando, Typhoon): không có UAV, độ sâu mạng nhỏ.
- Định tuyến quanh lỗ và cân tải (k-MLP 2021): gần với việc đi vòng cell nước.
- Lý thuyết tìm kiếm và người đi lạc (Trummel và Weisinger 1986, Koester): cho pha 2 và tiên nghiệm. Hai bài lý thuyết tìm kiếm
  chưa có ghi chú.

## III. System operation

Tả theo bước đánh số như mục III của GAMBAC, chưa dùng ký hiệu. **thiếu** (nội dung có ở CONTEXT-SUMMARY, chưa viết thành mục)
1. **Pha 0, định kỳ.**
   - Trạm gốc dựng lưới cell, chọn CL, gateway và cột đèn.
   - Chọn AI cell, giao node thường.
   - Tính sẵn tour và kế hoạch River, phát xuống mọi cell.
   - Cập nhật nhẹ mỗi đêm.
2. **Có sự cố.** Trạm gốc phát bản tin LoRa khởi động. Node cắm điện tính cửa sổ chuyển sang kênh 26.
3. **Pha 1.**
   - Đội 1 bay một lượt và phát truy vấn.
   - Mạng mặt đất chuyển phần còn thiếu theo kế hoạch.
   - AI node đối sánh và báo điểm qua LoRa.
   - Cell chưa đủ sau hạn T_fb thì được vá.
4. **Pha 2.** Đội 2 cất cánh, thăm cell nghi vấn theo xác suất hậu nghiệm, xác minh V1, dừng khi xác nhận đúng.

## IV. System model

Mục giả định tách riêng và ghi rõ giả định nào chỉ dùng để phân tích (mẫu k-MLP). Định nghĩa đánh số, có bảng ký hiệu.
1. **Mạng và cell.** Lưới lục giác R = 100 m. Mật độ 816 node/km², xem thêm 400 và 280. Node cắm điện và node pin. Cột đèn ở cell cần.
   Cell nước. **có** (CONTEXT mục 2–4, 20, 21)
2. **UAV.** Một VTOL ở 100 m, 25–50 m/s, giới hạn bán kính quay, vùng cấm theo OSM. Một UAV cánh quay 15 m/s. **có**
3. **Kênh.**
   - A2G: hai đoạn cộng suy hao môi trường, Rician K = 2, bốn chế độ R50. Hình 9.1 của CONTEXT dùng làm hình kênh.
   - G2G: 3GPP UMi NLoS.
   - Biến thể có tường.
   - Nhiễu 2,4 GHz (K1d) nằm ở phần thảo luận.

   **có**, riêng hình kênh có nhãn **thiếu**
4. **Truy vấn và dữ liệu nền.** Ảnh 400 KB. Phương án lai: vector hoặc ảnh cắt. Luồng nền ≤ 10–20 % thời gian kênh. K mô hình mỗi AI
   node. **có** (CONTEXT mục 27–29, K9)
5. **Xác minh và tiên nghiệm.** Pha 2 dùng V1, 78 s mỗi lần. Tiên nghiệm đều. Mô hình điểm binormal. **có**
6. **Độ đo.** T\*, phân vị 0,9, trung bình. Tỉ lệ thành công. **sửa** (bản thảo dùng T\* trung bình)

## V. Problem formulation and complexity

Viết thành công thức, khác hai bài mẫu. Khuôn tham khảo là bài (P1) ở phương trình (12) của Zeng 2018. **sửa** (bản thảo có một bài
gộp, cần tách)
1. **Mục tiêu chung.** min Q₀,₉(T\*), báo kèm E[T\*]. Ràng buộc sức bền hai UAV.
2. **(P0) Chọn AI cell.**
   - Biến: y_v (node v làm AI node) và x_uv (node u giao cho AI node v).
   - Ràng buộc: số chặng H, bộ nhớ, luồng nền mỗi môi trường ≤ u_max.
   - Mục tiêu: ước lượng Q₀,₉(T\*) theo tập K, qua surrogate.
   - Đây là bài facility location có sức chứa.

   **có** dạng giải (K9 `cc_select.py`), **thiếu** mục tiêu phân vị
3. **(P1) Pha 1.**
   - Biến: thứ tự cụm π, quỹ đạo q(t), tốc độ v(t), lịch phát s(t), luồng mặt đất f.
   - Ràng buộc: Dubins, vùng cấm, sức chứa mỗi môi trường theo khe thời gian.
   - Mục tiêu: Q₀,₉ của lúc critical cell cuối nhận đủ.

   **thiếu** dạng công thức của f (đã chốt đưa vào bài, chatlog mục 393)
4. **(P2) Pha 2.**
   - Biến: lúc cất cánh t₂ và lộ trình đội 2.
   - Mục tiêu: thời gian tới khi xác nhận đúng, theo hậu nghiệm cập nhật.
   - Bản tĩnh của bài là NP-khó (Trummel và Weisinger 1986).

   **thiếu**
5. **Lý do tách ba bài.** Pha 0 chạy trước sự cố. Pha 1 và pha 2 nối nhau qua thời điểm và độ chính xác của báo cáo. **có** (L1-VARIABLES)
6. **Độ khó.** Định lý 1 (P1 NP-khó, quy từ Exact Cover theo Le Ny 2012). Nhận xét độ khó của (P0) và (P2). **có** cho P1

## VI. Limits

1. **Định lý 2, chặn phủ của mọi cách không hợp tác.** Mệnh đề 1 tính thêm quãng bay. Hệ quả: điều kiện để hợp tác thắng; vùng cấm
   bay. **có**
2. **Mệnh đề 2, chặn một radio của lớp mặt đất.** **có**
3. **Chặn LP của (P1) phần mặt đất** (nới lỏng tuyến tính của tải lớn nhất). Theo mạch của GAMBAC: chặn, rồi điều kiện đạt chặn
   (tải các môi trường cân nhau), rồi thuật toán cân tải. **có** số cho hai cụm, **thiếu** phát biểu
4. **Giới hạn của Định lý 2** khi truy vấn nhỏ (Q = 400–1 000). Ghi thẳng ở đây. **có**

## VII. Algorithms

1. **Chọn AI cell.** Tìm số cell ít nhất khả thi bằng nhân đôi rồi chia đôi, sau đó tìm kiếm cục bộ, mục tiêu là surrogate. **có**,
   cần đổi mục tiêu sang phân vị
2. **Đường bay.** CHORD và LM-Tour, có ràng buộc giao hàng. **có**
3. **Vận chuyển mặt đất.** River (vai trò SPINE, Bank, Ring), cây dùng chung, lập kế hoạch cân tải, chọn lại thành viên Ring. **có**
   (1 seed)
4. **Takeover và bán kính hỏi thích nghi.** **có**, bán kính thích nghi chưa chạy ns-3
5. **Pha 2.**
   - Chính sách tham lam (xác suất chia thời gian bay).
   - Giải lại khi có báo cáo mới.
   - So với quy hoạch động khi có tới khoảng 15 cell nghi vấn.

   **thiếu**
6. **Cơ chế vá cell bị sót** (K15). **thiếu**

## VIII. Evaluation

1. **Thiết lập.**
   - Bản đồ C4: k8, k12, k15 hoặc k16.
   - Bản đồ thật: ít nhất Hoàng Mai và một khu nước ngoài.
   - Bốn chế độ kênh.
   - Seed theo quy tắc N ≥ 120 cho số định lượng.

   **sửa** (bản đồ thật **thiếu**)
2. **Thời gian nhiệm vụ.** Bảng III và Hình 7 của bản thảo; thêm phân vị 0,9. **có** trung bình, **thiếu** phân vị
3. **Cấu trúc pha 1.** Bảng IV. **có**
4. **Lớp mặt đất.** Lập kế hoạch so với khám phá (River, Deluge, kéo trực tiếp). Thuật toán cân tải, khoảng cách tới chặn một radio
   và chặn LP. **có** (cân tải 1 seed)
5. **Lệch quỹ đạo và takeover.** Bảng VI. **có**
6. **Đặt AI node.** Mục VIII-F, Bảng VII, Hình 8–9, phương án lai. **có** (1 seed, mục tiêu trung bình)
7. **Khoảng cách tới tối ưu ở bài nhỏ.**
   - (P0) so với nghiệm đúng.
   - (P1) mặt đất so với LP.
   - (P2) tham lam so với quy hoạch động.

   Kèm thời gian giải, như Bảng II của GAMBAC. **thiếu**
8. **Độ nhạy.** Mật độ 400 và 280, cỡ truy vấn, kênh có tường, thiết bị vắng, nhiễu. **thiếu** phần ns-3 (K10, K14, K1c, K1d)

## IX. Discussion and limitations

Gồm:
- chưa có chặn trên cho River;
- Định lý 2 chỉ chứng nhận lợi thế ở tầm ngắn và truy vấn lớn;
- một UAV, nhiều UAV để sau;
- tiên nghiệm có thông tin (Koester);
- dữ liệu OSM thiếu chiều cao;
- thời tiết làm cận trên;
- pháp lý bay BVLOS.

**có** nội dung rời ở CONTEXT, cần gom

## X. Conclusion và phụ lục

- Kết luận. **thiếu**
- Phụ lục A: chứng minh Định lý 1. **có**
- Phụ lục B: chứng minh Mệnh đề 1. **có**
- Thêm chứng minh cho chặn LP và cho kết quả của (P2) nếu có. **thiếu**

## Thứ tự việc đề xuất

1. Chốt ba câu còn mở về mục tiêu (L1-VARIABLES mục 8).
2. Viết mục III và V (hoạt động hệ thống, ba bài toán) bằng tiếng Anh vào bản thảo.
3. Chạy đủ seed cho thuật toán mặt đất mới và K9 (đã có lệnh; thuật toán mặt đất khoảng 1,5 giờ cho 5 seed, K9 khoảng 2,5 giờ mỗi seed thêm vì B4 chạy 8 cấu hình trong 2 giờ 20 phút). Cần bàn trước khi chạy (mục 35).
4. Dựng bản đồ ns-3 từ bản đồ thật (K14, K10) cho phần đánh giá đô thị.
5. Tìm hiểu và thử pha 2 tối ưu; ghi chú hai bài lý thuyết tìm kiếm.
