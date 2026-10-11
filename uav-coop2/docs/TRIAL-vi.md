# Kế hoạch cài đặt thử nghiệm cơ chế River (lớp 3)

Cơ chế: [L3-vi.md](L3-vi.md), Thuật toán 1–7. Mô tả gốc: CLAUDE.md §8, mục 38–47.

## 1. Rà soát: cơ chế đã đủ để cài đặt chưa

| bước | ai chạy, khi nào | thuật toán | trạng thái |
|---|---|---|---|
| Lập bảng Axe, giao đoạn Seg | BS, trước giờ bay | 1 | đủ |
| Dựng River: Bank và cell path | mỗi cell Axe, trước giờ bay | 2 | đủ |
| Chọn critical cell | CH, trước giờ bay | 3 | đủ |
| Dựng Circle, giao nhiệm vụ cho hàng xóm | CH, trước giờ bay | 4 | đủ (đã sửa: mỗi đoạn Seg lấy từ Bank của chính đoạn đó) |
| Gom dữ liệu trong cell về CL | mọi cell, ngay khi UAV rời đi | quy ước 1 | dùng lại cơ chế tóm tắt của `uav-coop`, thêm phần chuyển dữ liệu |
| Axe bổ sung cho Bank | sau lượt bay | 5 | đủ |
| Circle kéo dữ liệu về và giao | sau lượt bay | 6 | đủ |
| Critical cell yêu cầu | sau lượt bay | 7 | đủ |
| Chuyển cell path thành đường node | mọi chặng | quy ước 2 | dùng lại bảng tuyến của `uav-coop` |
| Định dạng yêu cầu | mọi yêu cầu | quy ước 3 | dùng lại bộ mã manifest của `uav-coop` |

Những điểm đã sửa trong lần rà soát này:
1. **Thuật toán 4:** trước đây mỗi hàng xóm chỉ lấy từ một Bank. Nhưng một Bank chỉ được bổ sung
   đúng đoạn Seg của Axe của nó, nên bây giờ hàng xóm lấy **từng đoạn Seg từ Bank của chính
   đoạn đó**.
2. **Cell path từ Bank tới Circle được đi qua River.** Nếu cấm, Axe cắt cụm làm hai, và một Bank
   ở bờ bên kia không còn đường nào tới Circle. Điều này đã thấy trên cụm thử.
3. **Bổ sung ba thuật toán chạy sau lượt bay (5–7) và ba quy ước thực thi.** Trước đây chỉ có
   phần lập kế hoạch.

## 2. Tham số của bản thử đầu

| tham số | giá trị |
|---|---|
| triển khai | seed 1, 109 cell, spacing 35 m, 2 312 node, CH #136 |
| đường bay | thẳng qua CH, `--angle=180` (`docs/data/path-a180.csv`) |
| luồng phát | 50 m/s, 10 ms một gói; $\lvert\mathcal{D}\rvert\approx4\,600$ gói trong cụm |
| River | $W=3{,}5$ cell ($\omega=303$ m, PER 1,1 %) |
| critical cell | $\kappa_g=2$, $\kappa_l=1$, $r=2$ → 7 critical cell |
| Circle | 6 hàng xóm, không gộp các Circle |
| kênh G2G | n = 3,5, che khuất tĩnh σ = 7,8 dB, Rayleigh theo khối 100 ms (`coop-g2g.h`) |

## 3. Đầu vào còn thiếu

**Bitmap thu của đường bay thẳng chưa có.** Lượt chạy trước chỉ lưu số gói nhận và chuỗi dài
nhất của mỗi node, không lưu từng gói. Bản thử cần biết chính xác node nào có gói nào.

Cần chạy `uav-coop-pass --bits` trên `path-a180.csv`:
- 120 lượt bay, 4 tiến trình;
- khoảng **40 phút**, khoảng 210 MB, đặt trong thư mục scratch.

Đây là việc tốn thời gian nên **chỉ chạy khi người dùng đồng ý**. Trong lúc chờ, có thể viết và
kiểm tra bản thử trên bitmap đã có của đường bay cơ sở (đường hình chữ U).

## 4. Bản thử bước 1: mô phỏng mức logic

Bản thử này tương tự `coop-manifest` của `uav-coop`: hướng sự kiện, nhanh, và cho cận lạc quan.

- **Mã nguồn:** module ns-3 `uav-coop2` mới, liên kết với `uav-coop` để dùng lại tuyến, bộ mã
  manifest và kênh. Chương trình chính là `examples/coop2-river.cc`.
- **Vào:** triển khai, đường bay, bitmap thu theo từng lượt bay.
- **Mô hình liên kết:**
  - mỗi khung đi qua một chặng chiếm một khe 10 ms;
  - mỗi chặng thành công với xác suất tính từ kênh G2G; nếu thất bại thì gửi lại;
  - mỗi node chỉ phát hoặc nhận một khung mỗi khe (bán song công);
  - các cặp gateway có kênh riêng;
  - trong một cell, mỗi khe chỉ một node được phát.
- **Gom trong cell về CL:** chuyển phần hợp dữ liệu của cell lên CL theo cây tới CL, mỗi chặng tốn
  một khe.
- **Ra cho mỗi lượt bay:**
  - với mỗi critical cell: thời điểm có đủ $\mathcal{D}$, số gói thiếu ban đầu, số gói nhận được
    từ từng hàng xóm;
  - với mỗi liên kết: số khung đi qua, để thấy nút thắt;
  - tổng số lần phát.
- **Kiểm tra trong chương trình** (CHECK như các bản trước):
  - mỗi critical cell cuối cùng có đủ $\mathcal{D}$, trừ những gói không node nào nhận được;
  - dữ liệu chỉ đi qua các cell path đã định và gateway đã định;
  - không node nào phát hoặc nhận hai khung trong cùng một khe;
  - thời gian của mỗi critical cell không nhỏ hơn cận dưới $\lvert\mathrm{Lack}(k)\rvert\cdot\tau$.

## 5. Phương án so sánh

| phương án | mô tả |
|---|---|
| **River** | Thuật toán 1–7 |
| **Kéo thẳng** | mỗi critical cell yêu cầu trực tiếp từng cell Axe theo cell path ngắn nhất, không có Bank hay Circle |
| **Manifest** | cơ chế manifest của `uav-coop` (đã đóng gói), chỉnh lại cho đích là các critical cell |
| **Cận dưới** | $\lvert\mathrm{Lack}(k)\rvert\cdot\tau$ cho mỗi critical cell |

**Thước đo:**
- thời gian hoàn tất: trung vị, p90, max qua các critical cell và qua 120 lượt bay;
- tổng số lần phát;
- tải của liên kết bận nhất.

## 6. Thứ tự làm và thời gian

1. Viết `coop2-river.cc` (Thuật toán 1–7 và các kiểm tra), thử trên bitmap của đường cơ sở.
   Mỗi lần chạy mất vài phút.
2. *(cần đồng ý)* Chạy pass có bitmap cho đường bay thẳng, khoảng 40 phút.
3. Chạy River, Kéo thẳng và Manifest trên cùng 120 lượt bay, mỗi phương án vài phút. Vẽ hình
   và viết kết quả.
4. Nếu kết quả hợp lý thì bàn tiếp về bản mô phỏng mức vô tuyến (ns-3) cho một vài cấu hình.

## 7. Câu hỏi nghiên cứu phụ (ngoài phạm vi bài này)

1. **Độ rộng River tối ưu:** cân bằng giữa chi phí bổ sung Axe → Bank (tăng nhanh theo $\omega$
   khi PER vượt khoảng 5 %) và chi phí Bank → Circle (giảm theo $\omega$).
2. **Bank với đường bay cong:** các đường song song không còn phù hợp. Hướng thay thế: lấy Bank
   trên đường cách đều đường bay một khoảng $\omega$, rồi ghép mỗi Bank với cell Axe có
   $d_{\mathrm{track}}$ gần nhất.
3. **Hai critical cell kề nhau:** gộp thành một Circle chung (ví dụ chuỗi (−5,0), (−5,1), (−4,−1)
   trong cụm thử).
4. **Circle 12:** quy tắc mở rộng theo lượng dữ liệu thiếu. Mở rộng giúp kéo dữ liệu về nhanh
   hơn, nhưng không tăng tốc độ dữ liệu vào critical cell.
