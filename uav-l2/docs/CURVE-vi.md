# Axe cong: Bank theo pháp tuyến cục bộ, và MEANDER (cluster bám địa hình, bay đường cong)

Lời gốc: CLAUDE.md §8 mục 103.
Mã:
- `uav-coop2/tools/river_plan.py` (`banks="local"`), `river_export.py --banks`
- `uav-l2/tools/curve_banks.py`, `curve_ns3.py`, `meander.py`

Log: `logs/2026-10-19_1838-curve-banks/`.

## Phần 1. Bank cho Axe không thẳng

### 1.1 Cơ chế
Bản cũ (L3‑vi.md, thuật toán 2) dựng mọi Bank trên các đường song song, cùng vuông góc với vector tổng của Axe. Khi đường bay cong, các đường này lệch khỏi pháp tuyến thật của đường bay: Bank ở phía trong khúc cong bị kéo lại gần, Bank ở phía ngoài bị đẩy ra xa hoặc ra khỏi River.

Bản mới (`banks="local"`), với mỗi cell Axe a:
1. Lấy điểm giữa của đoạn đường bay phía trên a (gói giữa của Seg(a)) và tiếp tuyến tại đó, đo trên ±10 m.
2. Đi theo pháp tuyến hai phía một khoảng ω = 1,75 W. Cell cuối cùng còn trong cluster là Bank, chuỗi cell đi qua là đường cell Axe → Bank.
3. **Phía trong khúc cong**, các pháp tuyến hội tụ tại tâm cong. Vì vậy quãng đi bị cắt ở min(ω, bán kính cong cục bộ). Bán kính cong đo từ độ đổi hướng của đường bay trên ±100 m.
4. **Phía ngoài khúc cong**, các pháp tuyến toả ra và để hở. Vì vậy bắn thêm tia mỗi 10 m dọc Seg(a), chỉ để tính cell nào thuộc River.
5. Circle xếp thành viên theo vị trí dọc đường bay (điểm gần nhất trên track) thay cho chiếu lên vector tổng.

Với đường thẳng, hai cách cho Bank gần như trùng nhau.

### 1.2 Hình (không chữ)
`figures/curve-banks-example.png`, cluster k6/C3 trên bản đồ k6.
- **Hàng trên:** Bank song song. **Hàng dưới:** Bank cục bộ.
- **Cột:** góc thoát 180° / 135° / 100° / 70°. 180° là thẳng; góc càng nhỏ thì đường càng cong.
- **Màu:** xanh đậm là Axe; xanh lá là Bank; xanh nhạt là River đúng chỗ; vàng là River thừa (cách đường bay quá ω); đỏ là cell lẽ ra thuộc River nhưng không có.
- **Nét:** nét mảnh là đường cell Axe → Bank; nét đậm là đường bay.

### 1.3 Số liệu hình học
17 cluster (bản đồ k4, k6, k8), mỗi góc một đường Dubins qua CH. "Dải" là các cell cách đoạn đường bay trong cluster ≤ ω.
- *Phủ*: phần dải nằm trong River.
- *Phủ theo đường Bank*: chỉ tính các cell trên đường Axe → Bank, là những gì ns‑3 thật sự dùng.
- *Lệch*: khoảng cách Bank–đường bay chia cho ω, bỏ Bank bị cắt ở biên cluster.

| Góc | Bank | Phủ | Phủ theo đường Bank | Thừa | Lệch |
|---|---|---|---|---|---|
| 180° | song song | 0,916 | 0,916 | 0,196 | 1,00 |
| 180° | cục bộ | 0,960 | 0,921 | 0,188 | 0,99 |
| 135° | song song | 0,892 | 0,892 | 0,179 | 0,98 |
| 135° | cục bộ | 0,964 | 0,874 | 0,195 | 0,92 |
| 100° | song song | 0,837 | 0,837 | 0,111 | **0,78** |
| 100° | cục bộ | 0,962 | 0,846 | 0,187 | **0,94** |
| 70° | song song | 0,776 | 0,776 | 0,085 | **0,63** |
| 70° | cục bộ | 0,976 | 0,825 | 0,172 | **0,88** |

Khi đường cong, Bank song song bị kéo về gần đường bay (chỉ còn 0,63 ω ở 70°), còn Bank cục bộ giữ được khoảng 0,9 ω. River theo pháp tuyến cục bộ phủ 96–98 % dải ở mọi góc.

### 1.4 Kiểm tra bằng ns‑3
Chạy lượt bay rồi River (chuẩn bị đầy đủ, MAC 802.15.4, 7 màu). Dùng cùng bitmap lượt bay cho cả hai cách. 18 cluster × góc 100° và 70° = 36 cặp, mỗi cặp một lượt.

| | Bank song song | Bank cục bộ |
|---|---|---|
| Critical cell xong, trung bình | 9,0 s | 9,1 s |
| Critical cell chậm nhất | 21,1 s | 21,5 s |
| Bank cục bộ nhanh hơn | | 18/36 (TB), 12/36 (chậm nhất) |
| Số chặng truyền | 41 953 | 45 187 (+7,7 %) |
| Critical cell thiếu dữ liệu | 0 | 0 |

**Kết luận:** Bank cục bộ đúng về hình học nhưng **không rút ngắn thời gian River** trong các cluster này. Nó tốn thêm khoảng 8 % chặng truyền, vì Bank xa đường bay hơn nên Axe phải đẩy dữ liệu xa hơn.

Lý do có thể: các cluster nhỏ (≤ 80 cell), khúc cong thường nằm gần biên nên đường bay sớm ra khỏi cluster, và thời gian chủ yếu do gom nội cell và Circle quyết định.

Số này là thăm dò: N = 36 < 120, mỗi cluster một lượt.

## Phần 2. MEANDER: tái cấu hình cluster cho đường bay cong bám địa hình

### 2.1 Ý tưởng
LANE (RESTRUCTURE-vi.md) cắt miền thành các luồng **thẳng** song song. Miền cong (thung lũng sông, chữ C) hoặc nhiều hồ khiến luồng thẳng bị cắt vụn, và mỗi cluster chỉ bay một đường thẳng.

MEANDER giữ ý tưởng của LANE: luồng rộng cỡ River, cluster cắt dọc luồng, tour quét luống biết trước. Điểm khác là "dọc" và "ngang" được đo bằng **toạ độ cong của chính địa hình**, và đường bay là đường cong mượt thoả bán kính rẽ tối thiểu ρ = 255 m.

### 2.2 Các bước (hình `figures/meander-<bản đồ>-steps.png`, 8 ô, đọc trái → phải, trên → dưới)

| Ô | Bước | Mô tả |
|---|---|---|
| 1 | Địa hình | Đất, hồ (gạch chéo), BS (ô vuông) |
| 2 | Xương sống và toạ độ dọc s | Đường kính trắc địa của đất: Dijkstra trên cell đất, hồ và sông là lỗ. Từ một cell bất kỳ tới cell xa nhất A, từ A tới cell xa nhất B; xương sống là đường ngắn nhất A → B (nét đen, hai chấm là A, B). s(h) = (d_A − d_B)/2 tô màu từ tím tới vàng; s uốn theo miền và vòng quanh hồ |
| 3 | Toạ độ ngang n | Khoảng cách trắc địa có dấu tới xương sống: Dijkstra nhiều nguồn từ các cell xương sống. Phía trái/phải được gán khi mặt sóng rời xương sống, theo tiếp tuyến cục bộ (đỏ ↔ xanh). Mỗi mảnh đất rời có xương sống riêng |
| 4 | Luồng | Cắt n thành dải rộng L·W (L = 4,5 cell), chọn độ lệch 0, 1/3 hoặc 2/3 luồng cho ít cluster và ít mảnh vụn nhất. Hai sắc xen kẽ |
| 5 | Mảnh và mảnh vụn | Mỗi luồng vỡ thành mảnh liền (màu riêng). Mảnh < Cap/4 (gạch chéo đen) nhập vào mảnh kề có biên chung dài nhất |
| 6 | Cluster và thứ tự | Mỗi mảnh cắt thành ⌈mảnh/Cap⌉ khúc bằng nhau theo s; khúc rời giữ phần lớn nhất. Màu đậm là ghé trước: quét luống theo luồng, trong luồng theo s, đổi chiều mỗi luồng; chọn 1 trong 4 tour ngắn nhất |
| 7 | Đường bay cong | Mỗi cluster: tâm các cell theo từng nửa W của s, trung bình trượt 7 bậc (~600 m), lấy mẫu mỗi 10 m, làm mượt Laplace (giữ hai đầu) tới khi độ cong ≤ 1/ρ; thêm đoạn thẳng ρ vào và ra. Nét đứt là bay chuyển tiếp |
| 8 | Phủ River | Cell cách đường bay của cluster mình ≤ ω (đậm) và không (nhạt) |

So sánh trên cùng bản đồ (`figures/meander-<bản đồ>-compare.png`), trái → phải: k‑medoids (đường thẳng dài nhất qua CH), LANE 4,5, MEANDER.

Hai bản đồ minh hoạ:
- `k6-s3-b220-w1`: khối cong 220°, rộng.
- `k6-s1-b90-w0.6`: dải hẹp như thung lũng sông. Ở đây MEANDER phủ 95,5 % so với 81 % (LANE) và 53 % (k‑medoids).

### 2.3 Chiến dịch hình học (60 bản đồ cong, 57 dùng được)
Thông số: độ rộng miền 1,0 / 0,6 km × K = 4, 6 cluster × độ cong 90 / 180 / 270° × 5 seed. Ba bản đồ bị bỏ vì k‑medoids (`partition.py`) lỗi khi đất bị chia thành nhiều mảnh.

| Rộng | Cong | Cách | Cluster | Nhỏ nhất (cell) | Phủ River | Xa nhất (cell) | Bay trong cluster (km) | Chuyển tiếp (km) |
|---|---|---|---|---|---|---|---|---|
| 1,0 | 90° | k‑med / LANE / MEANDER | 5,7 / 7,2 / 7,1 | 60 / 30 / 43 | 0,56 / 0,84 / 0,84 | 5,2 / 2,4 / 2,7 | 11,6 / 15,5 / 18,9 | 8,4 / 12,3 / 11,2 |
| 1,0 | 180° | | 5,9 / 7,5 / 7,4 | 53 / 29 / 34 | 0,57 / 0,81 / 0,84 | 4,8 / 2,4 / 2,6 | 11,8 / 15,1 / 19,4 | 8,3 / 11,5 / 10,0 |
| 1,0 | 270° | | 5,2 / 7,3 / 7,4 | 66 / 31 / 33 | 0,55 / 0,81 / 0,83 | 5,0 / 2,4 / 2,8 | 11,0 / 14,3 / 17,1 | 6,9 / 11,3 / 11,2 |
| 0,6 | 90° | | 6,5 / 8,2 / 8,0 | 61 / 32 / 42 | 0,55 / 0,82 / **0,90** | 5,0 / 2,4 / 2,2 | 13,1 / 18,1 / 25,2 | 12,1 / 14,3 / 13,0 |
| 0,6 | 180° | | 7,8 / 9,3 / 9,3 | 54 / 31 / 34 | 0,56 / 0,85 / 0,87 | 5,3 / 2,3 / 2,3 | 15,3 / 20,5 / 27,1 | 10,2 / 13,8 / 12,2 |
| 0,6 | 270° | | 7,1 / 8,8 / 9,2 | 62 / 34 / 40 | 0,56 / 0,87 / 0,87 | 4,8 / 2,2 / 2,3 | 14,6 / 19,5 / 25,0 | 8,8 / 13,4 / 13,7 |

So từng cặp phủ River, MEANDER − LANE, trên cùng bản đồ:

| Rộng | Cong | Chênh trung bình | MEANDER tốt hơn |
|---|---|---|---|
| 1,0 | 90° | +0,000 | 6/9 |
| 1,0 | 180° | +0,031 | 9/10 |
| 1,0 | 270° | +0,026 | 7/10 |
| 0,6 | 90° | **+0,082** | **10/10** |
| 0,6 | 180° | +0,020 | 6/9 |
| 0,6 | 270° | −0,005 | 6/10 |

**Đọc kết quả:**
- **Khi nào MEANDER thắng:** rõ nhất ở **dải hẹp có khúc gãy** (rộng 0,6, cong 90°: +8 điểm, 10/10). Đó là dạng thung lũng sông, nơi luồng thẳng bị cắt vụn. Ở miền rộng, LANE thẳng đã phủ 81–84 %, nên MEANDER chỉ thêm 0–3 điểm.
- **Cái giá:**
  - Đường cong dài hơn đường thẳng xuyên cluster, nên bay trong cluster nhiều hơn khoảng 20–40 %. Cluster vì vậy cũng nhận nhiều dữ liệu D hơn theo cùng tỉ lệ.
  - Tổng góc rẽ lớn gấp khoảng 3 lần LANE (đo trên bước 50 m). Mọi đoạn vẫn thoả ρ = 255 m: 100 % cluster khả thi.
- **Bay chuyển tiếp** ngang LANE hoặc ít hơn một chút. **Cluster nhỏ nhất** lớn hơn LANE (33–43 so với 29–34 cell).
- **Ở dải nghiêng gắt** (rộng 0,6, cong 270°), MEANDER hoà LANE: khúc gãy hẹp hơn 2ρ nên đường cong bị làm mượt cắt góc.

### 2.4 Giới hạn và việc tiếp theo
- **Chỉ tính hình học.** CH là đại diện hình học, chưa phải CH thật; chưa chạy lượt bay và River trên đường cong của MEANDER. ns‑3 đã nhận được đường bay tuỳ ý (Phần 1 dùng đường Dubins cong), nên bước tiếp có thể là: deploy từng cluster MEANDER để có vai trò và tuyến, thay đường bay bằng đường cong MEANDER, rồi chạy lượt bay, River và nhiệm vụ.
- **Xương sống là đường trắc địa trên lưới lục giác**, gồm các đoạn thẳng gãy. Một xương sống mượt (trục trung vị) có thể cho n đẹp hơn.
- **Cluster ghép ngang luồng** (từ mảnh vụn) có đường bay ngắn, cắt ngang luồng (thấy trong ô 7). Nên cho bay theo trục chính của cluster.
- **Chuyển tiếp giữa các cluster vẫn là đoạn thẳng**, chưa tính vòng rẽ chữ U.
- Bank cục bộ (Phần 1) là cách dựng River hợp với MEANDER, nhưng ns‑3 chưa cho thấy lợi về thời gian.
