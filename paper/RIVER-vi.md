# River — keyword

Lời gốc: CLAUDE.md §8 mục 79. Mã giả: `uav-coop2/docs/L3-vi.md` §3–4.

## A. Ý tưởng
- đường bay biết trước → ai giữ gì biết trước → lập kế hoạch tại BS / CH trước giờ bay
- dữ liệu "chảy" từ Axe ra Bank, từ Bank vào Circle, từ Circle tới critical cell
- mọi đơn vị là **cell** · mọi đường đi là **cell path** cố định

## B. Trước giờ bay (tính sẵn)
1. **Bảng Axe** (BS): d_track → cell dưới đường bay → Seg(a) = đoạn gói của mỗi cell Axe → gửi CH → CH phát xuống các Axe
2. **Bank** (Axe): đường vuông góc với vector tổng của Axe · cách ±ω (độ rộng 3,5 cell) · Bank song song · chạm biên thì biên là Bank
3. **Critical cell** (CH): cell CH + CL vượt trội toàn cục (μ + 2σ) + vượt trội cục bộ (μ + σ, mạnh nhất trong 2 vòng)
4. **Circle** (CH): hàng xóm của critical cell · chia Axe thành nhóm Seg liên tiếp · mỗi Seg lấy từ **đúng Bank của nó** · theo cell path

## C. Sau lượt bay (thực thi)
1. **gom nội cell:** node → CL (đường ETX nhỏ nhất)
2. **BANKFILL:** Bank báo thiếu → Axe bù phần Seg còn thiếu
3. **CIRCLEFILL:** thành viên Circle lấy nhóm Seg từ Bank · biến thể *chuẩn bị sẵn* / *theo yêu cầu*
4. **CRITPULL:** critical cell hỏi Circle phần còn thiếu → nhận về
5. xong khi critical cell có đủ D → đối sánh

## D. Biến thể
- **Circle động:** CL tóm tắt lượng thiếu → gọi tới 12 hàng xóm (vòng 1–2) · thiếu nhiều gọi nhiều
- **kéo thẳng** (ablation): critical cell hỏi thẳng từng cell Axe

## E. Ràng buộc truyền
- 802.15.4 đầy đủ · lưới kênh 7 màu · một gateway mỗi cặp cell · một máy phát mỗi cell / cặp gateway
- dữ liệu đi qua cell khác → giữ bản sao (không chủ động xin)

## F. Phân tích (để viết)
- số bản tin điều khiển: O(|Axe| + |crit| · |Circle|)
- tính toán tại BS / CH: tuyến tính theo số cell
- vì sao Bank: Bank đã gần đủ → Axe chỉ bù ít · phân tán tải khỏi Axe
- vì sao Circle: chia tải vào critical cell qua nhiều hướng · tránh nghẽn một gateway

## G. Hình dự kiến
- sơ đồ Axe / Bank / Circle trên một cluster (đã có, không chữ)
- dòng dữ liệu theo pha (gom → bankfill → circlefill → pull)

## H. Câu hỏi mở (để ở Discussion)
- độ rộng River tối ưu · Bank song song với đường bay cong · ghép Circle khi critical cell kề nhau
