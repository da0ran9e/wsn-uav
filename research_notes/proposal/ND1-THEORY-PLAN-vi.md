---
status: current
updated: 2026-11-08
---
# Kế hoạch ND1: mô hình và lý thuyết (12 tuần, 12/2026–02/2027)

Kế hoạch chi tiết cho giai đoạn 1 của `SIGDROP-PROPOSAL-vi.md`, mục 9, theo yêu cầu ở `docs/chatlog/2026-11.md` mục 288.
Sản phẩm cuối là hai mục **Mô hình hệ thống** và **Phân tích** của bài tạp chí J1, viết xong được. Mỗi kết quả lý
thuyết đều phải có một hình đặt đường lý thuyết chồng lên số liệu ns-3.

## 1. Mục tiêu và sản phẩm

Sau 12 tuần cần có năm thứ:
- **Mô hình hình thức:** ký hiệu thống nhất, các giả định có đánh số, và phân rã T\* thành các thành phần.
- **Các kết quả lý thuyết:** bổ đề NP-khó (L1), định lý điểm giao giữa hợp tác và bay vòng (A), mệnh đề ngưỡng lệch của
  takeover (B), cận dưới thời điểm sẵn sàng (D). Mỗi kết quả có chứng minh đầy đủ trên mô hình đơn giản.
- **Kiểm chứng:** với mỗi kết quả, một script tính đại lượng lý thuyết từ dữ liệu có sẵn và một hình so với ns-3.
- **Quyết định về định lý C** (giá trị thông tin của kế hoạch): có làm tiếp cho J1 hay không.
- **Bản nháp LaTeX** của hai mục trong J1, và cập nhật mục 7.2 (ND1) của đề cương.

Giai đoạn này gần như không cần chạy ns-3 mới. Mọi kiểm chứng dùng dữ liệu đã có:
- C4: `uav-l2/docs/data/results/campaign4.csv`, cùng điểm số theo seed;
- LMT: `river-surrogate*.csv`;
- WND và TKO: `logs/2026-10-31_0000-wind/`, `logs/2026-11-01_0600-takeover/`, gồm bit nhận, `wind-paths.txt`, `compare*.md`;
- DLG: `logs/2026-10-30_1545-deluge-r100/`.

Chỉ chạy thêm khi một kết quả cần điểm dữ liệu chưa có. Mỗi lần như vậy phải thảo luận trước, theo quy tắc ở mục 35.

## 2. Mô hình chung (tuần 1–2)

Hai tuần đầu chốt mô hình. Mọi chứng minh sau đều dựa trên nó, nên đây là việc quan trọng nhất của giai đoạn. Mô hình
gồm sáu phần.

**Mạng.** Đồ thị cell G = (V, E): mỗi đỉnh là một cell lục giác bán kính R, mỗi cạnh là một cặp gateway có dung lượng
c_e (gói/s). Mỗi cụm là một đồ thị con. Tập critical cell là K ⊆ V, và CH là một phần tử của K.

**Truy vấn.** Truy vấn có Q gói, chia thành các ảnh không thay thế được cho nhau. UAV phát một gói mỗi τ = 10 ms.

**Quỹ đạo.** γ(t) là đường bay dự kiến, γ′(t) là đường bay thật. Gói s được phát tại γ′(sτ). Độ lệch ngang lớn nhất là
e = sup_t |γ′(t) − γ(t)|.

**Kênh A2G.** Xác suất một node u nhận được gói s là p(d), với d là khoảng cách ngang từ u tới điểm UAV phát gói đó. p(d)
lấy từ mô hình hai đoạn kèm Nakagami đang dùng, có tham số R50. Giả định A1: nhận gói độc lập giữa các gói và giữa các
node. Giả định này lạc quan, sẽ được thảo luận ở phần giới hạn.

**Kế hoạch.** Bảng Seg phân hoạch Q theo các SPINE cell. Kèm theo là các vai trò Bank, Ring và các đường cell.

**Thời gian nhiệm vụ.** T\* = T_bay + T_mặt đất + T_đối sánh + T_LoRa + T_pha 2, trong đó T_mặt đất là thời điểm sẵn
sàng của critical cell cuối cùng. Các kết quả ở đây chỉ xét T_bay và T_mặt đất; các thành phần khác coi như hằng số
chung cho mọi phương án.

**Việc cụ thể.**
- Viết bảng ký hiệu và danh sách giả định A1–An.
- Đối chiếu từng tham số với `params.yaml`.
- Viết đoạn "System model" khoảng 1,5 trang.
- Kiểm tra mô hình có tái hiện được các con số cơ bản không, ví dụ số gói trung bình mỗi cell nhận được ở mỗi mức kênh,
  so với bit nhận thật trong log.

**Mốc tuần 2:** mô hình và ký hiệu được đóng băng. Sau mốc này chỉ sửa khi một chứng minh bắt buộc phải sửa.

## 3. Bổ đề L1: bài toán là NP-khó (tuần 2)

- **Phát biểu:** tìm quỹ đạo và kế hoạch để T\* nhỏ nhất là bài toán NP-khó.
- **Chứng minh:** quy từ DTSP-N. Đặt Q rất nhỏ và dung lượng mặt đất vô hạn, khi đó T_mặt đất ≈ 0 và bài toán trở thành
  tìm tour Dubins ngắn nhất qua đĩa của các CH.
- Khoảng nửa trang, làm song song với việc chốt mô hình. Không cần kiểm chứng số.

## 4. Định lý A: điểm giao giữa hợp tác và bay vòng (tuần 3–5)

**Câu hỏi.** Khi nào phân phối có hợp tác mặt đất (River) đáng giá hơn việc UAV bay vòng để giao trực tiếp (FC)? Lợi thế
của River tăng thế nào khi kênh xấu đi?

**Hướng chứng minh.**
1. **FC.** Critical cell k cần Q(1 + ε) gói mã khác nhau. Khi UAV lượn quanh k, mỗi gói tới được k với xác suất p_k, là
   xác suất tốt nhất trên quỹ đạo lượn. Số gói phải phát kỳ vọng là Q(1 + ε)/p_k. Trừ phần k đã nhận khi bay ngang, ta có
   thời gian lượn kỳ vọng ở k. Cộng thêm phần bay tới các critical cell, ta được T_FC.
2. **River.** T_River = T_bay một lượt + T_mặt đất. Theo cận ở mục 6, T_mặt đất bị chặn trên bởi lượng thiếu chia cho
   dung lượng lát cắt, cộng một số hạng tỉ lệ với đường kính đồ thị cụm.
3. **Kết hợp.** Từ hai bước trên, suy ra một điều kiện đủ để River thắng. Sau đó chứng minh dạng tiệm cận: khi R50
   giảm, p_k → p_min, và T_FC/T_River tăng theo cỡ 1/p.
4. **Trường hợp kênh tốt.** Chứng minh khi R50 lớn hơn bề rộng cụm, p_k → 1 và hai phương án ngang nhau. Đây đúng là
   hiện tượng đã thấy ở kênh open.

**Kiểm chứng (tuần 5).** Script `uav-l2/tools/theory/crossover.py`:
- tính p_k cho từng critical cell từ vị trí và mô hình kênh;
- dự đoán T_FC − T_River cho từng ô của C4 (bản đồ × kênh);
- so với số đo.

Hình cần có: tỉ số T_FC/T_River theo R50, gồm điểm ns-3 và đường lý thuyết.

**Mốc tuần 5:** có phát biểu, chứng minh và hình. Đường lý thuyết phải đúng xu hướng và đúng điểm giao, chưa cần khớp
từng giá trị.

**Rủi ro.** Giả định độc lập A1 có thể làm cận lỏng ở kênh xấu. Nếu vậy, phát biểu định lý dưới dạng chặn dưới cho FC và
chặn trên cho River, để kết luận vẫn đứng được.

## 5. Mệnh đề B: ngưỡng lệch của takeover (tuần 5–7)

**Câu hỏi.** Khi nào bước sửa từ cell kề là đủ? Khi đường bay lệch, cần hỏi xa bao nhiêu hop?

**Hướng chứng minh.**
1. Gọi w là khoảng cách lớn nhất từ một điểm phát tới tập a ∪ N(a), sao cho tập này vẫn có ít nhất một node nhận được
   gói với xác suất tối thiểu p_min. Đại lượng w phụ thuộc R và R50.
2. **Dưới ngưỡng.** Nếu e < w − √3·R/2, mọi gói của Seg(a) được a hoặc một cell kề của a nghe với xác suất ≥ 1 − δ.
   Chặn hợp trên các gói cho xác suất takeover phải kích hoạt.
3. **Trên ngưỡng.** Nếu e ≥ w, cell giữ gói nằm trong h(e) = ⌈(e − w)/(√3·R)⌉ + 1 hop cell tính từ a. Từ đó suy ra bán
   kính hỏi đủ, và số frame tối đa của vòng hỏi.

**Kiểm chứng (tuần 7).** Script `uav-l2/tools/theory/deviation.py`:
- với từng cụm trong WND và TKO, lấy e từ đường bay gió và số SPINE cell kích hoạt takeover từ log;
- kiểm tra mệnh đề dự đoán đúng: không kích hoạt ở σ = 50 m, kích hoạt ở σ = 100 m;
- so số hop tới cell giữ gói với h(e).

Bit nhận của các lượt gió có sẵn, nên tính được cả tỉ lệ gói nằm ngoài a ∪ N(a) theo e.

**Mốc tuần 7:** có mệnh đề và hình "số lần kích hoạt theo e" với ngưỡng lý thuyết.

## 6. Cận dưới D: thời điểm sẵn sàng (tuần 7–9)

**Câu hỏi.** Mặt đất không thể nhanh hơn bao nhiêu? River cách giới hạn đó bao xa?

**Hướng chứng minh.**
1. **Cận theo lát cắt.** Với critical cell k, xét mọi lát cắt tách k khỏi các nơi giữ dữ liệu k còn thiếu. Thời điểm sẵn
   sàng của k không nhỏ hơn lượng thiếu chia cho dung lượng lát cắt đó. Lấy max theo lát cắt và theo k ∈ K.
2. **Cận theo độ trễ.** Cộng thêm số hop tối thiểu nhân thời gian truyền một gói, vì dữ liệu phải đi hết quãng đường.
3. **Điều kiện River đạt gần cận.** Thử chứng minh River đạt cận nhân một hằng số khi các cặp gateway dùng kênh riêng. Nếu
   chưa chứng minh được, chỉ báo khoảng cách đo được.

**Kiểm chứng (tuần 9).** Script `uav-l2/tools/theory/cutbound.py`:
- ước lượng c_e bằng thông lượng thực đo của từng cặp gateway, từ các lượt River có sẵn;
- tính cận cho từng cụm;
- so với thời điểm sẵn sàng đo được.

Hình cần có: thời điểm sẵn sàng đo được và cận dưới, theo từng cụm. Khoảng cách giữa hai đường cho biết còn bao nhiêu chỗ
để cải tiến River.

**Mốc tuần 9:** có cận, có hình. Có quyết định: phát biểu River đạt gần cận thành định lý, hay chỉ là quan sát thực nghiệm.

## 7. Định lý C: quyết định có làm hay không (tuần 9–10)

C là đóng góp khái niệm mạnh nhất nhưng cũng rủi ro nhất. Hai tuần này chỉ làm một thử nghiệm nhỏ để quyết định.
- Từ bit nhận thật, ước lượng entropy của mẫu nhận gói H(X), và entropy còn lại khi đã biết kế hoạch H(X | kế hoạch), ở
  quỹ đạo danh nghĩa và ở các mức gió.
- Đặt cạnh số frame điều khiển của Deluge và của River ở thí nghiệm DLG, và số frame của takeover ở TKO.

**Tiêu chí tiếp tục:** H(X | kế hoạch) phải nhỏ hơn H(X) rõ rệt ở quỹ đạo danh nghĩa, tăng theo độ lệch, và cùng chiều
với số frame điều khiển đo được.
- Nếu đạt: đưa C vào J1 dưới dạng mệnh đề cho một lớp giao thức chỉ dùng thông tin cục bộ, và hoàn tất sau giai đoạn này.
- Nếu không: ghi C thành hướng mở trong phần kết luận.

## 8. Viết và rà soát (tuần 10–12)

- Viết hai mục J1 bằng LaTeX, đặt ở `paper/j1/` (thư mục mới): **System model** khoảng 2 trang, **Analysis** khoảng 3–4
  trang, chứng minh dài đưa vào phụ lục.
- Hoàn thiện các hình lý thuyết chồng lên ns-3. Bản không chữ lưu ở `docs/figures/` kèm INDEX; bản có nhãn để cho bài.
- Rà soát nội bộ:
  - kiểm từng giả định có được dùng đúng chỗ không;
  - kiểm từng chứng minh có lỗ hổng không;
  - thử một phản ví dụ nhỏ cho mỗi kết quả.
- Cập nhật mục 7.2 của đề cương bằng các phát biểu đã chốt.

**Mốc tuần 12:** bản nháp hai mục của J1 hoàn chỉnh. Các kết quả A, B, D đã có hình kiểm chứng. Đã có quyết định về C.

## 9. Lịch tóm tắt

| Tuần | Việc chính | Mốc |
|---|---|---|
| 1–2 | Mô hình, ký hiệu, giả định; bổ đề L1 | Mô hình đóng băng (tuần 2) |
| 3–5 | Định lý A và kiểm chứng trên C4 | A xong (tuần 5) |
| 5–7 | Mệnh đề B và kiểm chứng trên WND, TKO | B xong (tuần 7) |
| 7–9 | Cận dưới D và kiểm chứng trên các lượt River | D xong (tuần 9) |
| 9–10 | Thử nghiệm quyết định cho C | Có hoặc không làm C (tuần 10) |
| 10–12 | Viết hai mục J1, rà soát, cập nhật đề cương | Bản nháp hoàn chỉnh (tuần 12) |

Nếu giai đoạn này kéo dài 2 tháng thay vì 3: bỏ thử nghiệm C (đẩy sang sau J1), và gộp việc viết vào từng mốc thay vì để
dồn cuối. Thứ tự ưu tiên khi thiếu thời gian là A, B, L1, rồi mới tới D.

## 10. Rủi ro chính

- **Giả định độc lập giữa các lần nhận gói làm cận lỏng.** Khắc phục: phát biểu dạng một chiều (chặn dưới hoặc chặn trên)
  thay vì xấp xỉ hai chiều. Thêm một hệ số tương quan lấy từ dữ liệu, nêu rõ là hiệu chỉnh thực nghiệm.
- **FC trong mô phỏng là bản lý tưởng** (ε = 5 %, lượn tối ưu). Định lý A phải so với đúng bản này, và nêu rõ điều đó trong
  bài.
- **Dung lượng cặp gateway thay đổi theo tải và lịch.** Dùng giá trị trung bình đo được, và báo cận ở hai mức dung lượng
  để thấy độ nhạy.
- **Một chứng minh bị kẹt quá một tuần.** Hạ phát biểu xuống trường hợp đặc biệt (lưới đều, một cụm, kênh đĩa) và ghi
  trường hợp tổng quát thành giả thuyết, có kiểm chứng số.
