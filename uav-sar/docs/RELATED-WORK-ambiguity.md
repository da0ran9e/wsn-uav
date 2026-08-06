# Đã có nghiên cứu nào xét yếu tố này chưa?

Ghi chép khảo sát cho phần related work, về **nhập nhằng danh tính** (nhiều vật
thể cùng khớp dữ liệu tham chiếu) trong tìm kiếm cứu nạn có UAV + mạng cảm biến.

**Phạm vi khảo sát:** vài lượt tìm kiếm có định hướng (8/2026), **không phải
khảo sát hệ thống**. Đủ để định vị bài toán và tìm tổ tiên lý thuyết; **không đủ
để tuyên bố "chưa ai làm"**. Xem §5 về việc cần làm thêm.

---

## 1. Tổ tiên lý thuyết: lý thuyết tìm kiếm với "false contacts" (đã có từ lâu)

Đây là phát hiện quan trọng nhất: **bài toán của chúng ta là một bài toán kinh
điển trong lý thuyết tìm kiếm**, chỉ là được đặt vào một hệ thống mạng.

- **"Optimal Search Among False Contacts"**, *SIAM Journal on Applied
  Mathematics*, [doi:10.1137/0152099](https://doi.org/10.1137/0152099). Mục tiêu
  nằm giữa các **false contact phân phối Poisson**; người tìm phải quyết định
  ngay tại chỗ xem một tiếp xúc có phải mục tiêu không, và **khả năng phân biệt
  chỉ đúng với một xác suất cho trước**. Đó chính xác là cấu trúc của mô hình
  `ClutterSource`. (Không lấy được tên tác giả/năm — trang SIAM trả 403; phải tra
  lại qua thư viện trước khi trích dẫn.)
- **Koopman**, *The Theory of Search* I–III, [Operations Research
  1956–57](https://dl.acm.org/doi/abs/10.1287/opre.5.5.613) — nền móng.
- **Stone, Royset, Washburn**, *Optimal Search for Moving Targets* — "tìm kiếm
  khi có mục tiêu giả" (search in the presence of false targets) là **một chủ đề
  chuẩn** trong sách, cùng với optimal search-and-stop.

**Hệ quả cho bài báo:** đừng trình bày yếu tố này như một ý tưởng mới. Cách mạnh
hơn nhiều là: *"đây là bài toán tìm kiếm giữa các tiếp xúc giả của Koopman–Stone,
lần đầu được đặt vào một hệ có ràng buộc năng lượng bay và ràng buộc truyền thông
mặt đất."* Vừa trung thực vừa nâng tầm bài toán.

## 2. Đúng kịch bản "nhiều vật giống hệt nhau" — thị giác máy tính

- **"Identification and Association of Multiple Visually Identical Targets for
  Air–Ground Cooperative Systems"**, *Drones* 9(9):612, 2025
  ([MDPI](https://www.mdpi.com/2504-446X/9/9/612)). Đúng bài toán: UAV nhìn xuống
  nhiều UGV **giống hệt nhau về ngoại hình**. Lời giải của họ xác nhận lập luận ở
  `FALSE-POSITIVE-RIGOR-vi.md` §7: họ **từ bỏ ngoại hình** và chuyển sang liên kết
  theo *hình học/topology* (ma trận chiếu, quan hệ góc, hợp nhất Dempster–Shafer)
  — tức là thêm **kênh thông tin khác**, đúng như dự đoán. Họ có chỉ số
  "False Positive Exclusion Rate" nhưng **không đưa ra cận khả phân biệt lý
  thuyết** — đây là chỗ đóng góp của ta khác họ.
- **Clothes-changing person Re-ID**: cả một dòng nghiên cứu lấy "người khác mặc
  cùng bộ đồ" làm **hard negative kinh điển**, và có bộ dữ liệu chuyên dùng người
  mặc-một-bộ làm **distractor**. Ví dụ [Try Harder: Hard Sample Generation for
  Clothes-Changing Re-ID](https://arxiv.org/html/2507.11119v1), [benchmark clothes
  variation](https://onlinelibrary.wiley.com/doi/full/10.1002/int.22276). Dùng để
  **biện minh cho tiền đề**: giả định duy nhất bị vi phạm thường xuyên là chuyện
  đã được cộng đồng thị giác máy tính ghi nhận, không phải ta bịa ra.

## 3. Dấu hiệu chuyển động — đã có người dùng, ở lĩnh vực khác

- **"Radar False Alarm Suppression Based on Target Spatial Temporal Stationarity
  for UAV Detecting"**, *Drones* 8(12):699, 2024
  ([MDPI](https://www.mdpi.com/2504-446X/8/12/699)): khác biệt về **tính dừng
  không-thời gian** giữa nhiễu nền và mục tiêu là cơ sở để triệt báo động giả.

Đây đúng là cơ chế đã đề xuất ở `FALSE-POSITIVE-RIGOR-vi.md` §7.2 (nạn nhân bị
thương thì bất động, người khoẻ mặc áo giống thì di chuyển) — **có tiền lệ trong
radar, và theo khảo sát này thì chưa thấy ai dùng cho SAR dựa trên mạng cảm biến
mặt đất.** Nếu triển khai thì trích dẫn đây làm cơ sở.

## 4. Phía UAV-SAR và WSN: dương tính giả có, nhưng ở **tầng khác**

- SAR dùng UAV có mô hình hoá FP, nhưng gần như luôn ở mức **bộ phát hiện**
  (tỉ lệ FP của bộ nhận dạng ảnh), không phải ở mức **thế giới có hai vật thật sự
  giống nhau**. Ví dụ [Victim Detection from a Fixed-Wing
  UAV](https://www.researchgate.net/publication/300124141_Victim_Detection_from_a_Fixed-Wing_UAV_Experimental_Results),
  [Reducing Object Detection Uncertainty from RGB and Thermal
  Data](https://arxiv.org/pdf/2308.10671).
- Tìm kiếm Bayes cho WiSAR ([SARBayes](https://sarbayes.org/), [Multi-UAV SAR in
  Wilderness](https://arxiv.org/abs/2411.10148),
  [SAREnv](https://doi.org/10.3390/drones9090628)) mô hình hoá **bỏ sót và báo
  động giả của cảm biến** trên bản đồ xác suất — nhưng mục tiêu vẫn là **duy
  nhất**; không có vật thể thứ hai hợp lệ.
- WSN + UAV thu thập dữ liệu ([tổng quan path
  planning](https://dl.acm.org/doi/10.1145/3560261)) tập trung vào năng lượng,
  vùng phủ, tuổi thọ mạng — **không xét nhập nhằng danh tính**.
- Định tuyến: k-traveling repairman / minimum latency có nền lý thuyết vững
  ([k-traveling repairmen](https://dl.acm.org/doi/10.1145/1290672.1290677),
  [probabilistic bounds](https://arxiv.org/abs/2211.11063)), nhưng chưa thấy bản
  kết hợp *trọng số xác suất hậu nghiệm + mục tiêu giả* trong bối cảnh này.

## 5. Khoảng trống — phát biểu thận trọng

Theo khảo sát **có giới hạn** này, ba mảnh đều đã tồn tại riêng lẻ:

| mảnh | đã có ở đâu |
|---|---|
| tìm kiếm giữa tiếp xúc giả | lý thuyết tìm kiếm hải quân, từ thập niên 1950–90 |
| nhiều vật thể giống hệt | thị giác máy tính / air–ground, 2025 |
| UAV + WSN + năng lượng | dày đặc, nhưng giả định mục tiêu duy nhất |

**Chưa thấy** công trình nào ghép cả ba: nhập nhằng danh tính **ở mức thế giới**
trong một hệ **UAV + mạng cảm biến mặt đất hợp tác**, kèm **cận khả phân biệt báo
cáo song song với hiệu năng hệ thống**, và kèm **hệ quả lên chỉ số đo** (sai số
trở thành hỗn hợp hai chế độ, phân vị gộp mất nghĩa).

**Phải làm trước khi viết câu "chưa ai làm" vào bài báo:**

1. Tra Google Scholar / IEEE Xplore với các cụm: *"search among false contacts"*,
   *"false targets" + "search theory"*, *"data association ambiguity" + "search
   and rescue"*, *"identity ambiguity" + "multi-target search"*.
2. Lần ngược trích dẫn của mục SIAM ở §1 — nhánh nào đã đưa nó sang robot/UAV?
3. Kiểm tra riêng mảng **multi-target tracking** (JPDA, MHT, PMBM): họ xử lý
   nhập nhằng liên kết một cách rất bài bản, và phản biện gần như chắc chắn sẽ
   hỏi tại sao không dùng khung đó. Cần có câu trả lời (gợi ý: ta không theo vết,
   ta **phân bổ nỗ lực phục vụ**, và ràng buộc là năng lượng bay + truyền thông).
4. Lấy đủ thông tin thư mục của mục SIAM (trang bị chặn 403).
