# Thiết kế thực nghiệm — ghi chép thảo luận

Tài liệu sống, cập nhật trong lúc thảo luận. Mỗi phần ghi: **hiểu biết hiện tại**,
**câu hỏi mở**, và **quyết định đã chốt** (kèm ngày). Chưa chốt thì để nguyên là
câu hỏi — không suy diễn thành kết luận.

Lộ trình: (1) mục tiêu & chỉ số → (2) nhánh so sánh → (3) điểm vận hành →
(4) thiết kế thống kê → (5) bố cục bài báo.

---

## Phần 1 — Mục tiêu và chỉ số

### 1.1 Ba kết cục đang bị gộp làm một

Hệ thống có **ba** kết cục khác nhau, và số liệu hôm nay chứng minh chúng có thể
đi **ngược chiều nhau**:

| # | kết cục | cột trong `metrics.csv` | ý nghĩa vận hành |
|---|---|---|---|
| (a) | **nạn nhân được phục vụ** | `timeToCompleteData_s` | nút gần nạn nhân đã tái tạo đủ tập tham chiếu |
| (b) | **vị trí báo về đúng** | `fixOnVictim`, `reportErr_m`, `timeToFixAtBS_s` | đội cứu hộ biết phải đi đâu, và chỗ đó đúng |
| (c) | **nhiệm vụ kết thúc** | `timeToReportAtBS_s` | mọi UAV đã về và báo cáo (`--allHome`) |

Bằng chứng chúng độc lập nhau — quét `kConfirmThreshold`, 24×24, N=40:

| ngưỡng | (a) cứu được | (b) báo **đúng** chỗ | (c) **không** kết thúc |
|---:|---:|---:|---:|
| 0.30 | 52.5 % | 55.0 % | 1/40 |
| 0.45 | 52.5 % | 57.5 % | 8/40 |
| 0.55 | 53.3 % | **66.7 %** | **12/30** |

(a) phẳng, (b) tăng, (c) xấu đi nhanh. Ba đường cong khác nhau từ **một** tham số.

### 1.2 Ý kiến của tôi (chưa phải quyết định)

**(b) mới là kết cục của bài báo, không phải (a).**

Lý do: về mặt vận hành, thứ đội cứu hộ nhận được là **toạ độ**. (a) là *phương
tiện* — nút của nạn nhân giữ đủ dữ liệu để **tự xác nhận danh tính**, và giá trị
của việc đó nằm ở chỗ nó làm (b) đáng tin. (c) là **quy ước mô phỏng**
(`--allHome`), không phải mục tiêu cứu nạn.

Nguy hiểm cụ thể nếu lấy (a) làm chỉ số chính: đã **đo được** trường hợp *cứu
được nạn nhân nhưng chỉ đường cho đội cứu hộ tới chỗ khác* — 52.5 % phục vụ được
đi kèm sai số báo về median 90 m. Một bài báo tối ưu theo (a) sẽ trông tốt lên
trong khi hệ thống tệ đi.

### 1.3 Hệ quả: dữ liệu bị **kiểm duyệt**, nên không có trung bình

Ở ngưỡng 0.55, **40 %** số run không bao giờ kết thúc trong chân trời 1200 s.
Với những run đó $T=\infty$, nên $\mathbb{E}[T]$ **không xác định** và mọi
"median thời gian nhiệm vụ" hiện đang tính trên **tập sống sót** — đúng loại
survivorship bias mà `STATUS.md` §5 đã cảnh báo ở chỗ khác.

Cách trình bày đúng, theo thứ tự ưu tiên:

1. **Đường cong** $\Pr[\text{fix đúng tới BS trước } t]$ — xử lý kiểm duyệt tự
   nhiên, và cho thấy toàn bộ hình dạng thay vì một con số.
2. $\Pr[T\le T_d]$ tại một **hạn chót khai báo** $T_d$ (kiểu "giờ vàng").
3. Trung bình có kiểm duyệt, với chân trời ghi rõ — chỉ khi cần một con số.

### 1.4 Câu hỏi mở — cần bạn trả lời

- **Q1.1** Kết cục chính của bài báo là (a), (b), hay một tổ hợp? Nếu (b) thì
  `victim served` xuống vai trò chỉ số phụ / cơ chế.
- **Q1.2** Câu chuyện vận hành là "đội cứu hộ nhận được toạ độ đúng" hay "thiết
  bị của nạn nhân nhận được dữ liệu"? Hai cái dẫn tới hai chỉ số khác nhau.
- **Q1.3** Có chấp nhận công bố **đường cong** thay vì một con số trung bình
  không? Nếu có thì vấn đề kiểm duyệt biến mất.
- **Q1.4** Có hạn chót $T_d$ nào có nghĩa trong SAR để báo $\Pr[T\le T_d]$?
  Nếu có, nó nên đến từ tài liệu SAR chứ không phải từ số liệu của ta.
- **Q1.5** Có tính "báo cáo sai" (fix về BS nhưng sai người) như một **thất bại
  riêng** không? Tôi nghiêng về **có**, vì nó tệ hơn "không báo gì" — nó điều
  động đội cứu hộ đi sai chỗ.
