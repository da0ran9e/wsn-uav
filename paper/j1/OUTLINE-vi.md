---
status: current
updated: 2026-11-26
---
# J1 · Dàn ý bài, phiên bản rừng (v2)

Dàn ý dựng từ bối cảnh rừng ([CONTEXT-vi.md](CONTEXT-vi.md)), theo yêu cầu ở chatlog mục 413: có bối cảnh rồi dựng dàn ý, chốt dàn ý
rồi mới viết bản nháp. Khung lấy từ dàn ý bản đô thị ([archive/urban-v1/OUTLINE-vi.md](archive/urban-v1/OUTLINE-vi.md)); mục nào
khác vì kịch bản rừng thì ghi rõ. Bản nháp [draft-v2](draft-v2/README-vi.md) viết trước khi có dàn ý, chỉ dùng như bản thử; sẽ
viết lại theo dàn ý này sau khi bạn duyệt.

Mỗi mục ghi trạng thái:
- **có**: đã có số và chữ, dùng được ngay;
- **sửa**: đã có nhưng phải làm lại cho kịch bản rừng;
- **thiếu**: chưa có số, hoặc còn chờ quyết định.

Ký hiệu bài toán theo pha: (P0) chọn AI cell, (P1) pha 1, (P2) pha 2.

## Tên bài và tóm tắt

- Tên bài cũ nói về pha 1 ("Flight Geometry Is the Schedule ..."). Bài nay có cả ba pha và kịch bản rừng, nên tên phải nói nhiệm vụ
  (tìm người trong rừng) và cách làm (một lượt bay, mặt đất hợp tác theo kế hoạch). Bản thử ở draft-v2: "Finding a Missing Person
  with a Forest IoT Network: Single-Pass UAV Query Delivery with Planned Ground Cooperation". **thiếu** (chờ bạn chọn)
- Tóm tắt gồm năm ý:
  1. tìm người mất tích trong rừng, thiết bị chạy pin, không có sóng di động;
  2. ba pha, mục tiêu phân vị 0,9 của T\*;
  3. ba bài toán và độ khó;
  4. chặn và thuật toán;
  5. số chính trên bản đồ rừng.

  Ý 1–3 **có**; ý 4–5 **thiếu** (chờ mục VI–VIII).

## I. Introduction

1. **Kịch bản thật, có hình.** Một người đi lạc trong một vườn quốc gia rừng đất thấp như Cát Tiên. Lõi rừng không có sóng di động.
   Ở đó có camera bẫy ảnh, cảm biến cháy, cảm biến âm thanh; chúng có thể đã thấy người này nhưng không biết phải tìm ai.
   - Hình: kịch bản trên bản đồ Cát Tiên (bản thử `figures/draft2-scenario-cattien-labelled.png`). **có**
   - Tần suất tìm kiếm cứu nạn: NPS có 2 890 vụ năm 2017. Thời gian sống còn: người tìm thấy trong 12 giờ đều sống, quá 24 giờ thì
     32 % đã chết (Koester 1998). **sửa** (số NPS mới lấy từ đoạn trích; chưa có số cho Việt Nam)
   - Rừng đang có thêm thiết bị nối mạng: Kissling 2024, Dryad, GreenOrbs. **có**
2. **Ba cách hiện có và chỗ hỏng.**
   - Gửi qua LoRa: 1,8–18 h. Phép tính không phụ thuộc kịch bản. **có**
   - Lan qua mạng mặt đất từ trạm ở bìa rừng: phải đi qua rất nhiều chặng. Số 50–95 chặng là của bản đồ đô thị k8. **sửa** (tính lại
     trên bản đồ rừng)
   - UAV phát thẳng có mã fountain: dưới tán, tầm chỉ còn 100–200 m nên bị chặn phủ (Định lý 2). Hình chặn theo R50
     (`draft-v1/figs/bound-nc.png`). **có số, sửa hình**
3. **Ý chính:** đường bay chính là lịch phát, nên trạm biết trước cell nào nhận đoạn nào và lập được kế hoạch hợp tác mặt đất. **có**
4. **Ba pha và đánh đổi giữa chúng.** **có**
   - Pha 0: chọn AI cell trước sự cố. Ở rừng, AI node chỉ đặt được ở chỗ trống có pin mặt trời.
   - Pha 1: UAV cánh bằng bay một lượt, mạng mặt đất chuyển phần còn thiếu.
   - Pha 2: UAV cánh quay xác minh.
   - Đánh đổi: nhiều AI cell thì luồng nền ngắn hơn, nhưng pha 1 nặng hơn và pha 2 nhiều báo nhầm hơn; bay sát mọi AI cell thì đường
     dài hơn; thứ tự phục vụ cụm ở pha 1 quyết định lúc pha 2 biết nên bay đi đâu.
   - Hình: sơ đồ thời gian ba pha (bản thử `figures/draft2-phases-labelled.png`).
5. **Một câu mục tiêu.** Tối thiểu phân vị 0,9 của T\*, với ràng buộc luồng nền, số chặng, bộ nhớ, năng lượng thiết bị pin và sức
   bền hai UAV. **thiếu** (chờ chốt phân vị lấy qua những gì)
6. **Đóng góp.** **sửa**
   - Kịch bản và mô hình rừng, kèm số mật độ thật.
   - Ba bài toán và độ khó.
   - Các chặn.
   - Thuật toán.
   - Đánh giá ns-3 trên bản đồ rừng.
7. **Bảng tóm tắt kết quả** theo Bảng 1 của k-MLP. **thiếu**

## II. Related work

Xếp theo hướng tiếp cận; mỗi hướng một câu về chỗ nó không giải được bài này. **sửa** (draft-v1 đã có bốn nhóm đầu)
- UAV phát chung xuống mặt đất (Zeng 2018 multicast).
- UAV thu dữ liệu từ WSN (Zhan 2018, Wu 2018, GAMBAC 2023): chiều ngược lại.
- Phổ biến dữ liệu trong WSN (Deluge, Typhoon, Splash, Pando) và lập lịch phát đa điểm (MLBS, You 2013).
- DTSP và DTSP-N (Le Ny, Isaacs).
- Mới cho bản rừng:
  - mạng trong rừng: GreenOrbs, camera bẫy ảnh nối mạng, Dryad;
  - kênh qua tán lá: Weissberger, ITU-R P.833, Nekrasov 2019;
  - lý thuyết tìm kiếm và hành vi người đi lạc: Trummel và Weisinger 1986, Sitters 2002, Hermans 2019, Koester.

## III. System operation

Kể theo bước đánh số như mục III của GAMBAC, chưa dùng ký hiệu. **có** (bản thử ở `draft-v2/tex/sec-system.tex`)
1. Trước sự cố, pha 0:
   - dựng lưới cell, chọn CL, cặp gateway và cụm;
   - chọn AI cell, giao thiết bị thường cho AI node;
   - tính sẵn kế hoạch bay và vận chuyển mặt đất cho các vùng sự cố có thể xảy ra.
2. Có sự cố: trạm kiểm lâm dựng truy vấn từ ảnh người thân cung cấp rồi phát bản tin LoRa đánh thức; không có thông tin vị trí
   (chatlog mục 414).
3. Pha 1: bay một lượt; mạng mặt đất chuyển phần còn thiếu, có bước sửa; AI node đối sánh rồi báo qua LoRa.
4. Pha 2: tính hậu nghiệm, UAV cánh quay thăm cell nghi vấn, dừng khi xác nhận đúng người.
5. Phạm vi: một UAV ở pha 1; chỉ xét rừng phẳng hoặc thoải; vườn núi để phần mở rộng.

## IV. System model

Có bảng ký hiệu. Tách riêng giả định chỉ dùng cho phân tích (mẫu k-MLP).
1. **Địa hình.** Bảng địa hình các khu khảo sát; giả định mặt đất phẳng, áp dụng cho nhóm rừng đất thấp. **có** (CONTEXT mục 6)
2. **Mạng, cell, thiết bị.** **sửa**
   - Lưới lục giác R = 100 m, cụm tối đa 80 cell, mỗi môi trường một máy phát mỗi lúc.
   - Thiết bị: camera bẫy ảnh, cảm biến; AI node ở chỗ trống có pin mặt trời; sông, đầm là lỗ của đồ thị cell.
   - Mật độ 816 thiết bị/km² là giả định hướng tới tương lai. Đặt cạnh mật độ thật (0,003–2 trên toàn vườn).
   - Hình mật độ (bản thử `figures/draft2-density-gap-labelled.png`).
   - Ngưỡng để lưới còn liền cần tính lại với suy hao tán. **thiếu**
3. **Năng lượng và đánh thức.** Mọi thiết bị chạy pin, có ngân sách năng lượng mỗi nhiệm vụ; cửa sổ thức tính từ bản tin LoRa.
   **thiếu** (số năng lượng của camera bẫy ảnh và node cảm biến; CH thức sẵn hay không)
4. **UAV.** VTOL ở 100 m, 25–50 m/s; UAV cánh quay 15 m/s, xác minh mỗi cell 78 s. **có**
5. **Kênh A2G qua tán.** **có**
   - Giữ bốn chế độ kênh.
   - Đối chiếu với Weissberger: hình suy hao theo góc ngẩng (bản thử `figures/draft2-canopy-loss-labelled.png`); ghi rõ áp cho đường
     xiên là ngoại suy.
   - Hình p(d) mô hình so với ns-3 (draft-v1); thiếu bản có nhãn.
   - Biến thể suy hao theo góc ngẩng để ở phần độ nhạy.
6. **Kênh G2G dưới tán.** **thiếu** (mô hình cũ là phố đô thị; cần một mô hình đo cho node đặt sát đất trong rừng; tránh tính trùng
   suy hao)
7. **Truy vấn, mã, thời điểm hoàn tất.** 12 ảnh, Q = 4 041 gói. **có**
8. **Dữ liệu nền.** Ở rừng ít người qua lại nên luồng nền nhẹ. **thiếu** (tần suất ảnh có người của camera bẫy ảnh, lấy từ một bộ dữ
   liệu đã công bố)
9. **Tiên nghiệm, báo cáo, xác minh.** Tiên nghiệm đều trên vùng mạng phủ, không có điểm thấy cuối (chatlog mục 414). Mô hình điểm
   binormal; báo cáo qua LoRa. **có**
10. **Độ đo.** Phân vị 0,9 của T\*, trung bình, tỉ lệ tìm thấy trong sức bền UAV. **thiếu** (phân vị lấy qua những gì)

## V. Problem formulation and complexity

Khuôn viết theo Zeng 2018 và Zhan 2018 ([FORMULATION-EXAMPLES-vi.md](FORMULATION-EXAMPLES-vi.md)); dạng cốt lõi từ
[PROBLEMS-vi.md](archive/urban-v1/PROBLEMS-vi.md) của bản đô thị.
1. **Vì sao tách ba bài.** Pha 0 chạy trước sự cố. Phân vị của một tổng không bằng tổng các phân vị. Bảng ghi ba bài nối nhau qua đại
   lượng nào. **có**
2. **(P0) Chọn AI cell.** Facility location có sức chứa, một nguồn, thêm ràng buộc số chặng và ràng buộc nghẽn. **sửa**
   - Thêm cho rừng: tập AI node ứng viên nhỏ (cần chỗ trống).
   - Có cần ràng buộc năng lượng cho luồng nền không. **thiếu**
   - Mục tiêu ở dạng phân vị. **thiếu**
3. **(P1) Pha 1.** Dubins TSP với lân cận, ghép với luồng nhiều hàng theo thời gian; hai giai đoạn (lập kế hoạch trên bản đồ nhận dự
   báo, rồi sửa). **sửa**
   - Thêm cho rừng: ràng buộc năng lượng và cửa sổ thức của từng cell.
   - Hình bản đồ nhận gói của một cụm, có đánh dấu critical cell. **thiếu**
4. **(P2) Pha 2.** Bài độ trễ nhỏ nhất có trọng số trực tuyến, hoặc quota TSP; hậu nghiệm chỉ đến từ điểm số của AI node.
   **sửa** (đang bàn ở [PROBLEMS-vi.md](PROBLEMS-vi.md))
5. **Độ khó.**
   - Định lý 1 cho (P1). **có**
   - (P0) chứa SSCFLP; (P2) chứa bài độ trễ nhỏ nhất có trọng số. Cần viết thành mệnh đề có chứng minh. **thiếu**

## VI. Limits

1. **Định lý 2 (chặn phủ) và Mệnh đề 1.** Bản đồ C4 vốn mô tả là rừng nên phần lớn số dùng lại được. **có** (vẽ lại hình cho bản rừng)
2. **Mệnh đề 2:** chặn một radio cho lớp mặt đất. **có**
3. **Chặn LP của phần mặt đất của (P1).** **có** số cho hai cụm; **thiếu** phát biểu
4. **Giới hạn của Định lý 2 khi truy vấn nhỏ.** **có**
5. **Chặn năng lượng** (mới): mỗi critical cell cần ít nhất bao nhiêu khung, quy ra năng lượng tối thiểu của các cell trên đường.
   **thiếu**, là đề xuất

## VII. Algorithms

1. Chọn AI cell (`cc_select.py`). **có**; cần đổi mục tiêu và thêm tập ứng viên ở chỗ trống
2. Đường bay: CHORD, LM-Tour. **có**
3. Vận chuyển mặt đất: River, cây dùng chung, lập kế hoạch cân tải. **có** (1 seed)
4. Takeover, bán kính hỏi thích nghi. **có** (bán kính thích nghi chưa chạy ns-3)
5. Pha 2: chính sách tham lam, giải lại khi có báo cáo mới; so với quy hoạch động ở bài nhỏ. **thiếu**
6. Cơ chế vá cell bị sót (K15). **thiếu**

## VIII. Evaluation

1. **Thiết lập.** **sửa**
   - Bản đồ: C4 (k8, k12, k15), thêm ít nhất một bản đồ ns-3 dựng từ cửa sổ Cát Tiên. Bản đồ Cát Tiên **thiếu**.
   - Bốn chế độ kênh, N ≥ 120 seed cho số định lượng.
2. **Thời gian nhiệm vụ:** phân vị 0,9 và trung bình. **có** trung bình; **thiếu** phân vị
3. **Cấu trúc pha 1.** **có**
4. **Lớp mặt đất:** River so với Deluge và kéo trực tiếp; khoảng cách tới chặn. **có**
5. **Lệch quỹ đạo, takeover.** **có**
6. **Đặt AI node:** thêm ràng buộc chỗ trống. **sửa**
7. **Năng lượng** (mới): số khung và năng lượng mỗi thiết bị cho một nhiệm vụ, so với Deluge. **thiếu**
8. **Khoảng cách tới tối ưu ở bài nhỏ** cho (P0), (P1) và (P2). **thiếu**
9. **Độ nhạy:** **thiếu**
   - mật độ 816, 400, 280 thiết bị/km² và thấp hơn;
   - suy hao theo góc ngẩng;
   - kênh G2G dưới tán;
   - cỡ truy vấn.

## IX. Discussion and limitations

**sửa** (nội dung rời ở CONTEXT mục 3, 6, 7)
- Mật độ thật thấp hơn giả định hàng trăm lần; phương án sub-GHz cho mạng thưa.
- Vườn núi: che khuất địa hình, bay bám địa hình.
- Một UAV; nhiều UAV để sau.
- Chưa có chặn trên cho River.
- Thời tiết, pháp lý bay ngoài tầm nhìn.
- Dữ liệu OSM thiếu đường mòn và lớp rừng.

## X. Conclusion và phụ lục

- Kết luận. **thiếu**
- Phụ lục A: chứng minh Định lý 1. **có**
- Phụ lục B: chứng minh Mệnh đề 1. **có**
- Chứng minh cho chặn LP, cho độ khó của (P0) và (P2). **thiếu**

## Kế hoạch hình

| Mục | Hình | Trạng thái |
|---|---|---|
| I | kịch bản trên bản đồ Cát Tiên | bản thử có (`draft2-scenario-cattien`) |
| I | chặn phủ theo R50 | dùng lại `draft-v1/figs/bound-nc.png`, cần vẽ lại |
| I | sơ đồ thời gian ba pha | bản thử có (`draft2-phases`) |
| IV | mật độ thật so với mô hình | bản thử có (`draft2-density-gap`) |
| IV | suy hao tán theo góc ngẩng | bản thử có (`draft2-canopy-loss`) |
| IV | p(d) mô hình so với ns-3 | có, thiếu bản có nhãn |
| V | bản đồ nhận gói một cụm, có critical cell | thiếu (`concept-river.png` là bản cũ) |
| VIII | bản đồ ns-3 dựng từ Cát Tiên | thiếu |
| VIII | T\* theo chế độ kênh, các hình đánh giá | có cho C4, thiếu cho bản đồ rừng |

## Câu cần chốt trước khi viết bản nháp

1. Tên bài.
2. ~~Tiên nghiệm chính~~: đã chốt là tiên nghiệm đều (chatlog mục 414).
3. Phân vị lấy chung qua cả vị trí người, hay lấy trường hợp xấu nhất theo vị trí.
4. Năng lượng có vào bài toán không: chỉ (P1), cả (P0), hay chỉ báo trong phần đánh giá.
5. Đánh giá có thêm bản đồ ns-3 dựng từ Cát Tiên không. Việc này tốn chạy máy, cần bàn trước (mục 35).

## Thứ tự việc đề xuất

1. Bạn duyệt dàn ý và chốt năm câu trên.
2. Tra số còn thiếu: mô hình G2G dưới tán, năng lượng thiết bị, tần suất ảnh có người, phân bố khoảng cách của người đi rừng (không cần nữa, mục 414).
3. Viết lại mục I–V theo dàn ý (sửa từ bản thử draft-v2).
4. Bàn kế hoạch chạy cho mục VI–VIII trên bản đồ rừng.
