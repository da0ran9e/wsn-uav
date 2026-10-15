# Khung paper (bản 1) — đại ý từng phần

Lời gốc: CLAUDE.md §8 mục 74, cùng tầm nhìn ở mục 38–39. Bản này chỉ ghi ý chính để anh/chị chỉnh dần. Paper viết bằng tiếng Anh, nên tên mục ghi bằng tiếng Anh.

**Quy ước cho mọi số liệu trong bản này:** đều là số thăm dò, chạy một lượt ns-3 cho mỗi cluster trên 40 bản đồ (`uav-l2/docs/MISSION-vi.md`). Chưa số nào đủ để công bố (quy tắc N ≥ 120). Những chỗ cần chạy lại được đánh dấu **[cần chạy]**.

---

## Tên bài (để chọn)

1. *River: Ground Cooperation for Single-Pass UAV Query Delivery to Heterogeneous IoT Camera Networks*
2. *Delivering Search Queries to Edge Cameras by a Single Fixed-Wing Pass and Cell-Based Ground Cooperation*
3. *Fly Once, Share Locally: UAV-Assisted Query Dissemination for Distributed Forensic Search*

## Thông điệp chính (một câu)

Một UAV cánh bằng chỉ bay qua mỗi cluster **một lần** không thể giao trọn bộ truy vấn cho các node xử lý quan trọng. Một cơ chế hợp tác mặt đất được lập kế hoạch trước (River) lấp được phần thiếu trong vài chục giây. Nhờ vậy cả nhiệm vụ tìm kiếm nhanh hơn rõ rệt so với các cách giao bằng UAV cánh quay. Và so với việc không hợp tác, River giữ được khả năng phát hiện.

**Cách nói cần giữ (bài học uav-sar, CLAUDE.md §6):**
- Hợp tác mặt đất **không** làm nhiệm vụ nhanh hơn so với "dùng ngay những gì nhận được". Số thăm dò chỉ bớt được 2–16 s.
- Thứ hợp tác mua được là **độ đầy đủ dữ liệu**, tức khả năng phát hiện. Không hợp tác thì mất cell thật ở 25–62 % lượt.
- Lợi thế về **thời gian** đến từ kiến trúc nhiệm vụ: cánh bằng một lượt, cộng hợp tác, cộng đội 2 đi sớm. Không nên quy nó cho riêng River.

## Abstract (khung 6 câu)

1. **Bối cảnh:** hàng nghìn camera IoT đô thị đã ghi lại bằng chứng, nhưng không biết cần tìm ai. Dữ liệu thô không thể và không được phép tải về.
2. **Hướng giải:** đưa *truy vấn* (một tập dấu vết cô đọng) xuống tận node biên bằng UAV, để node tự đối sánh tại chỗ.
3. **Khó khăn:** một lượt bay của UAV cánh bằng chỉ phủ một dải. Node xa đường bay nhận được một phần, trong khi node xử lý cần trọn bộ.
4. **Đề xuất:** River, cơ chế hợp tác theo cell được BS lập kế hoạch trước, gồm:
   - Axe giữ từng đoạn dữ liệu.
   - Bank bổ sung cho Axe.
   - Circle quanh mỗi critical cell gom phần còn thiếu.

   River chạy trên 802.15.4 với lịch lưới cell PECEE.
5. **Đánh giá:** ns-3 trên 200 cluster (40 bản đồ, 2–8 cluster mỗi bản đồ).
6. **Kết quả [cần chạy]:**
   - Nhiệm vụ đầu-cuối nhanh hơn 1,5–3,7 lần các baseline dùng UAV cánh quay.
   - River ít khung hơn kéo thẳng 5–18 %.
   - Không hợp tác thì mất cell thật ở 25–62 % lượt.

---

## 1. Introduction

Chi tiết từng đoạn: [`INTRO-vi.md`](INTRO-vi.md).

- **Động cơ:**
  - Trẻ đi lạc, truy vết sau sự cố.
  - Mạng camera dày nhưng mỗi thiết bị chỉ làm việc riêng của nó.
  - Bằng chứng sẽ bị ghi đè theo thời gian.
- **Vì sao không tải dữ liệu về:**
  - Vùng hoang dã chỉ có LoRa hoặc vệ tinh, vài trăm byte mỗi giờ.
  - Ở đô thị, dữ liệu thô vướng ràng buộc pháp lý.
- **Vì sao UAV:**
  - Đưa truy vấn tới nơi không có hạ tầng băng rộng.
  - Cánh bằng phủ nhanh nhưng không hover được, chỉ bay qua một lần.
- **Khoảng trống:**
  - Các công trình giao dữ liệu bằng UAV thường giả định UAV dừng hoặc quay lại đủ lâu để mọi node nhận trọn.
  - Hợp tác mặt đất (D2D, gossip) thường không được lập kế hoạch theo đường bay.
- **Đóng góp:**
  1. Kiến trúc nhiệm vụ ba pha: Pha 0 chia cụm, Pha 1 giao truy vấn, phản hồi qua LoRa, Pha 2 xác minh. Pha 1 tách thành ba lớp, và bài này tập trung vào lớp 3.
  2. **River:** cơ chế hợp tác theo cell, lập kế hoạch trước từ đường bay, gồm Axe/Seg, Bank, critical cell, Circle và Circle động.
  3. Chính sách cấp nhiệm vụ:
     - Đường bay qua CH theo hướng dài nhất trong cluster.
     - Tour đội 1.
     - Phản hồi LoRa qua CH.
     - Đội 2 đi sớm, thăm theo điểm nghi vấn.
  4. Đánh giá ns-3 với MAC 802.15.4 đầy đủ, so với các baseline có và không có pha 1, và có hoặc không có hợp tác.

## 2. Related Work

Keyword: [`RELATED-vi.md`](RELATED-vi.md).

- **UAV giao và thu dữ liệu cho WSN:**
  - Data ferrying, UAV-aided dissemination.
  - Lập đường bay phủ: quét luống, TSP, Dubins.
- **Broadcast/multicast từ UAV và mã fountain:** khác ở chỗ ở đây chỉ có một lượt, không phát lại.
- **Hợp tác và cache tại biên, D2D, gossip, network coding** trong WSN.
- **Phân cụm và định tuyến theo cell, lập lịch kênh dạng lưới:** PECEE elastic clustering, công trình trước của nhóm (cần trích).
- **Tìm kiếm và xác minh bằng đội UAV;** truy vết phân tán, nhận dạng tại biên.
- **[cần bổ sung]** danh sách tài liệu cụ thể. Có thể dùng skill deep-research khi anh/chị muốn.

## 3. System Model and Problem

- **Mạng mặt đất:**
  - N node không đồng nhất (quan sát, tính toán, giao tiếp).
  - Lưới cell lục giác R = 100 m. Mỗi cell có CL, mỗi cluster có CH.
  - Cluster có chặn trên 80 cell. Miền không lồi, có hồ.
- **Định tuyến nền:**
  - PECEE: next hop về CL.
  - Mỗi cặp cell kề nhau có đúng một cặp gateway.
  - Kênh 802.15.4 theo lưới 7 màu; gateway có kênh riêng.
- **Kênh truyền:**
  - A2G: không gian tự do tới 100 m, sau đó α = 3; fading Nakagami m = 1,8 mỗi gói.
  - G2G: n = 3,5; shadowing σ = 7,8 dB; Rayleigh theo khối 100 ms.
- **Dữ liệu:**
  - UAV phát liên tục một gói mỗi 10 ms.
  - D là tập gói cluster nhận được trong lượt bay.
  - Các node quan trọng cần đủ D (hoặc đủ lượng cho đối sánh, nếu dùng mã fountain).
- **Đội bay:**
  - Đội 1: cánh bằng 50 m/s, độ cao 100 m.
  - Đội 2: cánh quay 15 m/s, hover để xác minh với tệp lớn.
- **Phản hồi:** LoRa qua CH, duty cycle 1 %.
- **Bài toán:**
  - (a) Lớp 3: tối thiểu thời gian để mọi critical cell có đủ D, đồng thời ít khung.
  - (b) Cấp nhiệm vụ: tối thiểu thời điểm xác minh được nghi vấn thật và đội 2 về BS.

## 4. Mission Overview

- Ba pha, ba lớp của Pha 1, và lớp 3 nằm ở đâu trong đó.
- Hình tổng quan: một bản đồ có các cluster, đường bay đội 1, River, nghi vấn và đường bay đội 2. Có thể lấy một khung từ trang replay.

## 5. River: Planned Ground Cooperation (đóng góp chính)

1. **Bảng Axe tại BS:** từ d_track, mỗi cell Axe biết nó sẽ nhận đoạn Seg nào.
2. **Bank:** đường vuông góc với vector tổng của Axe, cách ±ω (độ rộng River 3,5 cell). Bank ở biên cluster thì chính biên là Bank.
3. **Critical cell:** gồm cell của CH, ngoại lệ toàn cục, và ngoại lệ cục bộ trong 2 vòng.
4. **Circle:**
   - Hàng xóm chia nhau các nhóm Seg liên tiếp, mỗi Seg lấy từ đúng Bank của nó.
   - Biến thể Circle động: CL ước lượng lượng thiếu rồi gọi tới 12 hàng xóm.
5. **Thực thi:** BANKFILL, CIRCLEFILL (chuẩn bị sẵn hoặc theo yêu cầu), CRITPULL. Đi theo cell path, qua đúng một gateway cho mỗi cặp cell.
6. **Mã giả ngắn** (đã có, `uav-coop2/docs/L3-vi.md` §3) và phân tích số thông điệp điều khiển.

## 6. Mission-Level Policies

- Chọn hướng bay qua CH để đoạn trong cluster dài nhất.
- Tour đội 1 (Held–Karp). Tour l3first chỉ có ích khi đội 2 chờ đủ báo cáo.
- Phản hồi LoRa qua CH, mỗi bản tin một khe 40 s.
- Đội 2:
  - Đi ngay khi có báo cáo nghi vấn đầu tiên.
  - Chọn nghi vấn theo điểm / thời gian.
  - Xác minh = hover + tệp lớn 1 MB (khoảng 73 s) + đối sánh.

## 7. Evaluation Setup

- ns-3.46, lr-wpan có MAC đầy đủ, binary đóng băng.
- Bản đồ: 2 / 4 / 6 / 8 cluster, 10 bản đồ mỗi kích thước. **[cần chạy]** nâng lên N ≥ 120 cho số chính.
- **Chỉ số:**
  - Thời gian tới khi critical cell cuối có đủ D.
  - Số khung MAC.
  - Thời điểm kết thúc nhiệm vụ.
  - Xác suất tìm thấy cell thật.
  - Số lần thăm nghi vấn.
- **Baseline:**
  - Kéo thẳng (ablation lớp 3).
  - B1: không pha 1, unicast.
  - B2: không pha 1, multicast.
  - B3 và B6: pha 1 bằng cánh quay.
  - B4: không hợp tác.
  - B5: quét luống, **[cần chạy, chờ quyết định thiết kế]**.
  - B7: cận dưới lý tưởng.

## 8. Results (các hình dự kiến)

1. **Lớp 3:**
   - River so với kéo thẳng: thời gian, số khung, phân bố theo cluster.
   - Ảnh hưởng của số critical cell, độ rộng River và số màu kênh. Đã có kết quả 20 lượt (`uav-coop2/docs/RIVER-NS3-vi.md`).
2. **Hợp tác so với không hợp tác (B4):**
   - Thời gian gần như bằng nhau, nhưng tỉ lệ tìm thấy khác hẳn.
   - Hình: tỉ lệ thành công theo ngưỡng phát hiện. **[cần mô hình lớp 1]**
3. **Nhiệm vụ đầu-cuối so với các baseline:** thời điểm kết thúc theo kích thước mạng (`base-end.png`).
4. **Ablation chính sách:** đi sớm, thăm theo điểm, l3first (`policy-end.png`).
5. **Một nhiệm vụ minh hoạ:** dòng thời gian (`mission-timeline.png`), hoặc các khung lấy từ trang replay.

## 9. Discussion and Limitations

- Mô hình lớp 1 mới là ngưỡng tạm; tệp lớn 1 MB là số tạm.
- Đường bay chỉ là đường thẳng. Đường cong và quét luống còn mở.
- Chưa tính năng lượng; một UAV mỗi đội.
- Fading giả định không đổi trong một gói, nên kết quả A2G lạc quan (mục 2).
- Đây là kịch bản đô thị; không đem số sang nhánh rừng.

## 10. Conclusion

- Tóm tắt các đóng góp.
- Hướng tiếp:
  - Mô hình nhận dạng (lớp 1).
  - Đường bay tối ưu theo River (lớp 2).
  - Ghép Circle.
  - Độ rộng River tối ưu.

---

## Cần anh/chị chốt

1. **Nơi gửi và giới hạn trang:** hội nghị 6 trang (ICC / Globecom / VTC / WCNC) hay tạp chí? Phạm vi các mục 5–8 phụ thuộc vào điều này.
2. **Trọng tâm:** River là đóng góp chính duy nhất (mục 39), còn các chính sách cấp nhiệm vụ chỉ là phần phụ trợ. Hay giữ cả hai ngang nhau?
3. **Tên bài và cách gọi:** dùng "River / Axe / Bank / Circle" xuyên suốt, hay đặt tên khác cho paper?
4. **Công trình PECEE:** có bài nào của nhóm để trích không?
