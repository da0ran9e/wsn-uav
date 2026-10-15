# Introduction — các ý chính (bản 1)

Lời gốc: CLAUDE.md §8 mục 75, khung chung ở `OUTLINE-vi.md`.

Mỗi đoạn dưới đây là một bước của mạch lập luận. Mỗi bước có câu chủ đề dự kiến (tiếng Anh, viết lại sau), các ý đỡ, và nguồn dẫn: [tr] là cần tài liệu ngoài, [ta] là số đo của chính ta. Những số [ta] chưa chạy đủ N ≥ 120 thì gắn thêm **[cần chạy]**.

---

## Đ1. Bằng chứng đã có sẵn ở biên, chỉ là chưa ai hỏi

> *Urban IoT cameras already record the evidence a search needs, but none of them knows what to look for.*

- **Mạng camera đô thị dày đặc** gồm camera an ninh, chuông cửa, máy bán hàng, camera hành trình. Mỗi thiết bị phục vụ một chủ khác nhau. [tr]
- **Ví dụ sự cố:** trẻ đi lạc, hoặc truy vết sau một vụ việc. Rất có thể đã có ống kính ghi lại đối tượng.
- **Bằng chứng có hạn dùng:** bộ nhớ ghi vòng, dữ liệu mới đè lên dữ liệu cũ. Đây là bài toán **chạy đua với thời gian**, nên đo bằng thời gian của cả nhiệm vụ.

## Đ2. Không kéo dữ liệu về được, nên phải đưa truy vấn xuống

> *Moving the footage to the analyst is neither feasible nor lawful; moving the query to the footage is.*

- **Băng thông:** vùng hoang dã chỉ có LoRa hoặc vệ tinh, vài trăm byte mỗi giờ. Ở đô thị, đường truyền ngược của từng thiết bị cũng hẹp. [tr]
- **Pháp lý và quyền riêng tư:** dữ liệu thô của chủ khác không thể tải về một cách đơn giản. [tr, quy định bảo vệ dữ liệu]
- **Đảo chiều:** gửi một truy vấn cô đọng (tập dấu vết, cỡ vài trăm KB) xuống node biên. Node tự đối sánh tại chỗ và chỉ báo về vài byte. [tr: edge analytics, query-based search]
- **Ba pha:** Pha 0 chia cụm, Pha 1 giao truy vấn, phản hồi qua LoRa, Pha 2 xác minh. Giới thiệu ngắn ở đây; Pha 1 là phần khó.

## Đ3. Vì sao dùng UAV, và vì sao một lượt bay là không đủ

> *A fixed-wing UAV can bring the query to thousands of devices in minutes, but a single pass leaves most of them with an incomplete copy.*

- **Cánh bằng:** nhanh và bay xa, nhưng không hover được, nên mỗi cluster chỉ được bay qua một lần.
- **Cánh quay:** hover được nhưng chậm, tầm bay ngắn. Giao từng nơi một thì không đuổi kịp quy mô mạng. [ta: không có pha 1 thì chậm gấp 1,6–3,7 lần — **cần chạy**]
- **Một lượt bay chỉ phủ trọn một dải hẹp.** Ra xa đường bay, gói nhận được vẫn nhiều nhưng rời rạc, mà truy vấn cần trọn bộ.
  - [ta, ns-3, A2G-RUN] Ở độ cao 100 m, bay 50 m/s, chuỗi gói liên tục dài nhất là **850** ngay dưới đường bay, rồi **245** ở 300 m, **50** ở 600 m, và chỉ **14** ở 900 m.
  - [ta] Sau lượt bay, một critical cell trung bình đã có khoảng 90 % dữ liệu, nhưng hiếm khi đủ 100 %.
- **Câu hỏi đặt ra:** làm sao để những node cần trọn bộ có được trọn bộ, mà không phải bay lại?

## Đ4. Hợp tác mặt đất là lời giải tự nhiên, nhưng làm ngây thơ thì đắt

> *Neighbours collectively hold what each one misses, yet low-power multi-hop exchange is slow and fragile.*

- **Hợp tác tự nhiên:** các node gần nhau giữ những phần dữ liệu bù cho nhau, nên trao đổi qua D2D/G2G là hướng hiển nhiên. [tr: gossip, epidemic, D2D caching, network coding]
- **Nhưng 802.15.4 nhiều hop vừa chậm vừa mong manh:**
  - Che khuất tĩnh làm hop yếu nhất quyết định thời gian; thời gian giãn ra đúng bằng 1/p của hop nghẽn. [ta, G2G-CHAIN]
  - Flooding hoặc gossip không định hướng làm tốn khung và gây va chạm.
- **Khoảng trống trong các công trình trước:**
  - Giao dữ liệu bằng UAV thường giả định UAV dừng, quay lại, hoặc phủ đủ dày. [tr]
  - Hợp tác mặt đất thường bỏ qua một điều quan trọng: **đường bay đã biết trước**.

## Đ5. Nhận xét then chốt: đường bay đã biết, nên hợp tác lập kế hoạch trước được

> *Because the trajectory is planned, the base station knows before take-off which cell will hold which part of the query, and can plan the cooperation.*

- **Biết trước ai giữ gì:** từ toạ độ dọc đường bay, BS biết mỗi cell dưới đường bay (Axe) sẽ giữ đoạn dữ liệu nào.
- **Dựng sẵn dòng chảy dữ liệu:**
  - Bank song song với Axe nhận phần bổ sung từ Axe.
  - Quanh mỗi node xử lý quan trọng (critical cell), một vòng hàng xóm (Circle) lấy từng đoạn từ đúng Bank của đoạn đó.
  - Dữ liệu đi theo cell path cố định, qua đúng một gateway cho mỗi cặp cell, trên lịch lưới cell PECEE.
- **Đặt tên:** gọi toàn bộ là **River**, dòng chảy của dữ liệu đổ xuống từ đường bay.

## Đ6. Đóng góp

1. **Kiến trúc nhiệm vụ ba pha:**
   - Pha 1 chia ba lớp (nhận dạng, đường bay, định tuyến mặt đất); bài này giải lớp 3.
   - Phản hồi đi qua LoRa của CH.
   - Pha 2 xác minh bằng tệp lớn.
2. **River:** cơ chế hợp tác theo cell, lập kế hoạch trước từ đường bay, gồm bảng Axe, Bank, chọn critical cell, Circle và Circle động. Có mã giả và chi phí điều khiển.
3. **Các chính sách cấp nhiệm vụ đi kèm:**
   - Đường bay qua CH theo hướng có đoạn trong cluster dài nhất.
   - Đội 2 xuất phát ngay khi có nghi vấn đầu tiên, thăm theo điểm nghi vấn.
4. **Đánh giá trên ns-3 với MAC 802.15.4 đầy đủ:**
   - Bản đồ có hồ, không lồi, 2–8 cluster.
   - So với các baseline không có pha 1, pha 1 bằng UAV cánh quay, không hợp tác, và cận dưới lý tưởng.

## Đ7. Kết quả chính (viết cẩn thận, đúng điều số liệu nói)

> *Cooperation is what makes a single pass sufficient; the speed comes from the mission design as a whole.*

- **[ta, cần chạy] Hợp tác mua được độ đầy đủ, không mua thời gian:**
  - Không hợp tác thì nhiệm vụ chỉ nhanh hơn 2–16 s, nhưng mất cell thật ở 25–62 % lượt.
  - Con số này phụ thuộc mô hình lớp 1, hiện còn là ngưỡng tạm.
- **[ta, cần chạy] Cả kiến trúc so với giao bằng UAV cánh quay:**
  - Nhanh hơn 1,5–2,5 lần khi pha 1 dùng cánh quay.
  - Nhanh hơn 1,6–3,7 lần khi không có pha 1.
  - Khoảng cách nới rộng theo kích thước mạng.
- **[ta, cần chạy] River so với kéo thẳng từ Axe:** ít khung hơn 5–18 %, critical cell cuối có đủ dữ liệu sớm hơn ở 17/20 cluster.
- **Không viết** "hợp tác làm nhiệm vụ nhanh hơn và rẻ hơn" (bài học uav-sar, CLAUDE.md §6).

## Đ8. Bố cục bài

Một câu liệt kê các mục 2–10.

---

## Cần anh/chị cho ý kiến

1. **Câu mở bài:** đi từ ví dụ cụ thể (trẻ đi lạc) hay từ xu hướng (mạng camera IoT bùng nổ)?
2. **Đ3 có cần số đo A2G-RUN không?**
   - Có số thì thuyết phục hơn.
   - Nhưng đó là số lạc quan, vì giả định kênh không đổi trong một gói.
   - Đặc tả mục 2 yêu cầu ghi chú điều này nếu trích.
3. **Đ7 nên mạnh tới đâu:** chỉ nêu chiều thay đổi, hay nêu cả con số? Con số cuối cùng sẽ thay sau khi chạy N ≥ 120.
4. **Có nêu Pha 0 / Pha 2 trong intro không**, hay chỉ nhắc qua để bài tập trung vào Pha 1?
