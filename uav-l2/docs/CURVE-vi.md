# Axe cong: Bank theo pháp tuyến cục bộ, và MEANDER (cluster bám địa hình, bay đường cong)

Lời gốc: CLAUDE.md §8 mục 103 (Phần 1–2), mục 104 (Phần 3), mục 106 (Phần 4).
Mã:
- `uav-coop2/tools/river_plan.py` (`banks="local"`, `reentry`), `river_export.py --banks --reentry`
- `uav-l2/tools/curve_banks.py`, `curve_ns3.py`, `meander.py`
- `uav-l2/tools/meander_mission.py`, `meander_compare.py` (Phần 3)

Log: `logs/2026-10-19_1838-curve-banks/`, `logs/2026-10-20_0222-meander-ns3/` (Phần 3), `logs/2026-10-20_0331-fixes/` (Phần 4).

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

## Phần 3. MEANDER trong cả nhiệm vụ, chạy ns‑3 (bản đồ 4, 6, 8 cluster)

### 3.1 Cách chạy
- **Bản đồ:** đúng ba bản đồ nhiệm vụ gốc k4‑s2, k6‑s4, k8‑s4 (khối có hồ). Đã kiểm tra trùng từng cell và node với bản k‑medoids đã lưu.
- **Ba cách chia cluster** trên cùng bản đồ:
  - **k‑medoids**: đề xuất gốc, đường thẳng qua CH theo hướng dài nhất. Dùng lại kết quả ns‑3 đã có, vốn chạy bằng đúng các binary hiện tại (deploy và river dựng ngày 13/10, kết quả commit sau đó).
  - **LANE 4,5**: `mission.py --partition lane`, đường thẳng dọc luồng. Lần đầu chạy ns‑3.
  - **MEANDER**: `meander_mission.py`, luồng cong theo địa hình, Bank cục bộ.
- **Mỗi cluster:**
  - Deploy để lấy CH, CL, tuyến và gateway. Biên an toàn của CH hạ dần 300 → 200 → 100 m nếu cluster mỏng.
  - Lượt bay ns‑3, rồi River chuẩn bị đầy đủ (MAC 802.15.4, 7 màu), mỗi cluster một lượt.
- **Nhiệm vụ:** chính sách P (tour l3first, đội 2 đi sớm, thăm theo điểm nghi vấn), 100 lần bốc nghi vấn mỗi bản đồ. Các cách chia có critical cell khác nhau nên các lần bốc không ghép cặp được.

### 3.2 Hai chỗ phải sửa để MEANDER chạy được trong ns‑3
1. **Đường bay phải đi qua CH.** `uav-coop-pass` kiểm tra điều này: CH luôn là critical cell và nghe UAV trực tiếp. Đường MEANDER là đường tâm luồng nên thường lệch CH 5–370 m (trung vị khoảng 70 m). Cách uốn:
   - Đẩy một "bướu" Gauss về phía CH: v = CH − điểm gần nhất, σ = √(2|v|ρ). Riêng bướu chỉ làm cong tối đa 1/(2ρ).
   - Làm trơn, giữ CH và hai đầu cố định, đến khi độ cong ≤ 1/ρ.
   - Nếu không đạt sau 2000 vòng thì nới σ (×1,5; 2; 3; 4; 6). Lý do: với CH bị ghim, làm trơn Laplace hội tụ về hai đoạn thẳng gãy tại CH.
   - **Kết quả:** 28/28 cluster khả thi; 27 đạt ngay với σ, 1 cần σ×3 (k8, CH lệch 302 m).
   - Lỗi đã gặp: lấy mẫu lại từng nửa đường tạo đoạn 0,2 m sát CH và làm phình độ cong giả. Đã sửa bằng bước chia đều.
2. **Đường cong có thể đi qua một cell hai lần.** `river_plan` vốn khẳng định Seg(a) là một khoảng liên tục (giả định đường thẳng).
   - Thêm tuỳ chọn `reentry`: Seg(a) là lượt đi qua dài nhất; các gói của lượt ngắn để trống, như gói phát ngoài cluster.
   - Đường thẳng không bao giờ chạm tới nhánh này, nên kết quả cũ không đổi.
   - Thực tế chỉ 1 gói trên 28 cluster bị bỏ.

Thêm một lỗi chỉ số trong nhánh `banks="local"`: khi một Axe cell nằm sát cuối đường, chỉ số vượt mảng. Lỗi này không lộ với đường deploy vì đường đó có đoạn ra 255 m ngoài cluster. Đã kẹp chỉ số.

Hình `figures/meander-bend-ch.png` (không chữ):
- Ba cluster: lệch nhỏ (k6‑C7), lệch 370 m ở cluster hình chữ L (k4‑C6), và lệch 302 m ở cluster chữ U quanh hồ (k8‑C5).
- Đường đứt: đường MEANDER gốc. Đường liền: đường đã uốn qua CH (sao trắng), kể cả đoạn vào và ra.
- Ở hai ca sau, ràng buộc qua CH kéo đường lệch hẳn khỏi trục luồng.

### 3.3 Kết quả (`data/meander/ns3-summary.csv`, `ns3-cells.csv`, `ns3-draws.csv`)

| Bản đồ | Cách | Cluster | Critical cell | Đường bay qua cluster (km) | Tour đội 1 (s) | D TB/cluster (kB) | River xong, TB / chậm nhất (s) | Mọi critical cell đủ D (s) | Kết thúc nhiệm vụ P, TB [95 % CI] (s) | p90 (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| k4 | k‑medoids | 4 | 27 | 11,2 | **327** | 415 | 24 / 60 | **314** | **734** [±32] | 915 |
| | LANE | 7 | 34 | 17,6 | 564 | 312 | 22 / 105 | 489 | 764 [±35] | 996 |
| | MEANDER | 6 | 26 | 17,0 | 483 | 455 | 41 / 115 | 455 | 867 [±41] | 1118 |
| k6 | k‑medoids | 6 | 45 | 16,2 | **560** | 417 | 18 / 71 | **482** | **866** [±48] | 1166 |
| | LANE | 9 | 47 | 25,6 | 786 | 388 | 28 / 113 | 684 | 1078 [±47] | 1379 |
| | MEANDER | 11 | 51 | 25,4 | 770 | 362 | 18 / 67 | 690 | 999 [±51] | 1330 |
| k8 | k‑medoids | 8 | 52 | 20,9 | **680** | 412 | 16 / 46 | **567** | **906** [±53] | 1256 |
| | LANE | 11 | 63 | 31,7 | 934 | 405 | 34 / 139 | 884 | 1044 [±68] | 1489 |
| | MEANDER | 11 | 60 | 32,2 | 929 | 481 | 66 / 192 | 823 | 1106 [±72] | 1577 |

Không critical cell nào thiếu dữ liệu ở giới hạn 900 s.

**Đọc kết quả:**
- **k‑medoids kết thúc sớm nhất trên cả ba bản đồ**, sớm hơn MEANDER 133–200 s và sớm hơn LANE 30–212 s.
- **Nguyên nhân thứ nhất: đội 1 bay nhiều hơn.**
  - Cả LANE và MEANDER phủ kín miền bằng luồng, nên đường bay qua cluster dài hơn 50–60 % (17–32 km so với 11–21 km). Tour đội 1 dài hơn 155–255 s.
  - Số cluster cũng tăng (6–11 so với 4–8). Lý do: hồ cắt luồng thành mảnh, và cluster bị chặn ở 80 cell.
- **Nguyên nhân thứ hai: River chậm hơn ở cluster có Axe dài.**
  - Tính trên 73 cluster của cả ba cách, thời gian của critical cell chậm nhất tương quan với chiều dài Axe (Spearman 0,73), và mạnh hơn nữa với D (0,84).

    | Axe (cell) | Cluster | Critical chậm nhất, TB / trung vị (s) |
    |---|---|---|
    | ≤ 12 | 25 | 19 / 18 |
    | 13–15 | 18 | 37 / 30 |
    | 16–19 | 16 | 54 / 45 |
    | ≥ 20 | 14 | 88 / 70 |

  - 36 % cluster MEANDER có Axe ≥ 20 cell (tới 27). Con số này ở LANE là 15 %, ở k‑medoids là 0 % (tối đa 18).
  - Mỗi critical cell phải gom **toàn bộ D**, mà D tỉ lệ với chiều dài Axe. Dữ liệu lại phải chảy dọc cả dòng sông, nên khối lượng truyền tăng gần như bình phương chiều dài. Cụ thể: k8‑C10 MEANDER có Axe 27 cell, D 6 940 gói, 600 nghìn chặng, xong sau 192 s. Cluster k‑medoids lớn nhất cùng bản đồ: Axe 17, 68 nghìn chặng, 27 s.
- **Cái MEANDER làm đúng:**
  - Critical cell nằm sát Axe: trung bình 0,8 cell, 94 % trong vòng 2 cell, xa nhất 4. Ở k‑medoids là 2,0 cell, 63 % và xa nhất 9; LANE 1,1 cell, 90 % và 6.
  - D trung bình lớn nhất (k4, k8). Nghĩa là mỗi cluster nhận nhiều dữ liệu hơn cho lớp 1.
  - Nhưng ns‑3 cho thấy khoảng cách tới Axe không phải nút thắt. Nút thắt là chiều dài dòng sông và lượng D phải gom.
- **Bank cục bộ không phải nguyên nhân.** Kiểm tra lại bằng MEANDER với Bank song song, cùng bitmap lượt bay (`works/meanderParallel`):

  | Bản đồ | River xong TB (cục bộ / song song) | Kết thúc nhiệm vụ |
  |---|---|---|
  | k4 | 41,4 / 41,1 s | 867 / 875 s |
  | k6 | 17,9 / 18,8 s | 999 / 997 s |
  | k8 | 65,9 / 61,5 s | 1106 / 1103 s |

  Khớp với Phần 1.4.
- **LANE**, đề xuất lớp 2 cũ (mục 84), giờ mới có số ns‑3 lần đầu. Nó cũng không thắng k‑medoids: tour dài hơn, D nhỏ hơn ở k4 (312 kB), River chậm hơn ở k6, k8.

**Mức tin cậy:**
- Đây là số thăm dò: 3 bản đồ, mỗi cluster một lượt bay và một lượt River. Chỉ phần nghi vấn được bốc 100 lần.
- Quy tắc N ≥ 120 chưa đạt, chưa dùng được cho paper.
- Tuy vậy, chiều chênh lệch giống nhau trên cả ba bản đồ, và cỡ chênh (130–200 s) lớn hơn khoảng tin cậy.

Animation từng bước của nhiệm vụ MEANDER trên bản đồ 4 cluster: `anim/meander-replay.html` (mô tả trong `ANIM-vi.md`), hình tĩnh `figures/meander-anim-steps.png`.

### 3.4 Ý nghĩa và hướng sửa (chưa làm, cần bàn)
- **Hàm mục tiêu của tái cấu trúc lớp 2 đang sai.**
  - LANE và MEANDER tối ưu "độ phủ River" (critical cell gần Axe). Nhưng thời gian nhiệm vụ do **tổng quãng bay** và **chiều dài Axe / D mỗi cluster** quyết định.
  - k‑medoids thắng vì cluster gọn: đường xuyên ngắn, Axe ≤ 18 cell, và đội 1 không phải quét kín miền.
- **Hướng sửa 1: giới hạn chiều dài Axe.** Cắt luồng thành đoạn ≤ 12–15 cell thay vì chỉ chặn 80 cell. Cái giá là nhiều cluster hơn và tour dài hơn.
- **Hướng sửa 2: không bắt critical cell gom toàn bộ D.**
  - Nếu lớp 1 chỉ cần L ảnh × F kB (khoảng 400 kB), BS có thể chỉ giao phần đó cho mỗi cluster.
  - Khi đó cluster dài không còn bị phạt theo bình phương. Hướng này cần chốt cùng mô hình lớp 1.
- **Hướng sửa 3: đổi tiêu chí chia cụm.** Dùng lại k‑medoids, nhưng chọn đường bay cong qua CH bám địa hình trong cluster gọn, thay vì luồng kín miền.

## Phần 4. Ba hướng sửa của §3.4 (mục 106), chạy ns‑3

### 4.1 Cài đặt
| Hướng | Cài đặt | Tham số |
|---|---|---|
| 1. Giới hạn chiều dài Axe | `meander.partition_meander(span=…)`: mỗi mảnh luồng cắt thành số khúc lớn nhất giữa ⌈cell/80⌉ và ⌈độ dài theo s / (span·W)⌉ (`meander_mission.py --span`) | span = 12 cell (khoảng 2,1 km) |
| 2. Chỉ giao phần lớp 1 cần | `river_plan.plan(window=Q)`: chỉ giữ Q gói Axe liên tiếp, đặt quanh chỗ UAV bay qua CH; Axe cell ngoài cửa sổ không còn là nguồn. Cluster nhận ít hơn Q thì giữ toàn bộ D, đếm là "thiếu" (`--windowKB`) | Q = 400 kB = 4 041 gói (khoảng 2,0 km Axe) |
| 3. k‑medoids + đường cong | `meander_mission.py --partition kmedoids`: cluster gọn của k‑medoids, mỗi cluster có xương sống và s riêng (`meander.coords`), bay theo đường tâm uốn qua CH | như MEANDER |

- **Bản đồ:** cùng 3 bản đồ (k4‑s2, k6‑s4, k8‑s4) và cùng binary.
- **k‑medoids đường thẳng chạy lại:** tour và mọi critical cell khớp từng số với kết quả cũ trên cả 3 bản đồ.
- **Cửa sổ:** chỉ chạy lại River, dùng lại bitmap lượt bay.
- **Khối lượng:** 199 lượt River, không lỗi.
- **Nhiệm vụ:** chính sách P, 100 lần bốc mỗi bản đồ.

### 4.2 Kết quả (`data/meander/fixes-{summary,cells,draws}.csv`)

**Kết thúc nhiệm vụ P (s), trung bình 100 lần bốc, k4 / k6 / k8:**

| Cách chia | Đầy đủ D | Cửa sổ 400 kB | Cluster thiếu < 400 kB |
|---|---|---|---|
| k‑medoids, đường thẳng (P gốc) | 734 / 866 / 906 | **725 / 867 / 899** | 1/4, 2/6, 4/8 |
| k‑medoids + đường cong (hướng 3) | 772 / 929 / 965 | 740 / 915 / 955 | 0/4, 2/6, 2/8 |
| LANE | 764 / 1078 / 1044 | 760 / 1072 / 1034 | 6/7, 4/9, 6/11 |
| MEANDER | 867 / 999 / 1106 | 831 / 986 / 1062 | 2/6, 6/11, 3/11 |
| MEANDER, span 12 (hướng 1) | 788 / 969 / 1096 | 788 / 968 / 1079 | 7/9, 8/12, 10/15 |

Khoảng tin cậy 95 % của mỗi số khoảng ±32 đến ±75 s.

**Tác dụng của cửa sổ.** Chênh ghép cặp (cùng critical cell, cùng lần bốc), k4 / k6 / k8:
- k‑medoids: −9 / +2 / −7 s.
- k‑medoids + đường cong: −32 / −14 / −10 s.
- LANE: −5 / −6 / −10 s.
- MEANDER: −36 / −13 / −44 s.
- MEANDER span: 0 / −1 / −18 s.

Thời gian critical cell chậm nhất của mỗi cluster:

| Cách chia | Đầy đủ D, TB / tối đa (s) | Cửa sổ, TB / tối đa (s) | Cluster quá 60 s (đầy đủ → cửa sổ) |
|---|---|---|---|
| MEANDER | 54 / 192 | 32 / 111 | 36 % → 18 % |
| k‑medoids + đường cong | 46 / 108 | 30 / 56 | 28 % → 0 % |
| k‑medoids | 34 / 71 | 31 / 60 | 6 % → 0 % |

**Đọc kết quả:**
- **Hướng 2 (cửa sổ) là sửa đúng chỗ.**
  - River nhanh hơn ở mọi cách chia, mạnh nhất ở cluster Axe dài (MEANDER k8: chậm nhất 192 → 111 s).
  - Thời điểm kết thúc nhiệm vụ chỉ sớm hơn 0–44 s: khe LoRa 40 s và đội 2 nuốt phần lớn phần lợi. Với k‑medoids, cluster vốn gọn, nên lợi chỉ vài giây.
- **Hướng 1 (span) làm River nhanh** (MEANDER k4: TB 41 → 6 s) và kéo MEANDER lại gần (−79 / −31 / −9 s).
  - Nhưng nó cắt thêm cluster (9 / 12 / 15), nên tour dài hơn; MEANDER span vẫn chậm hơn k‑medoids 54–190 s.
  - Phần lớn cluster thiếu dữ liệu cho lớp 1: 7/9, 8/12, 10/15 dưới 400 kB.
  - Span đo theo s (dọc xương sống), nên ở luồng xa xương sống tại khúc cong, đường bay vẫn dài: k8 còn 2 cluster có Axe 21–24 cell, chậm tới 164 s. Nên đo span trên chính đường tâm luồng.
- **Hướng 3 (k‑medoids + đường cong) thua đường thẳng:** +38 / +63 / +59 s, còn +15 / +48 / +56 s sau khi áp cửa sổ.
  - Đường theo xương sống riêng của cluster dài hơn đường thẳng qua CH, nên tour dài hơn (k4: 409 so với 327 s) và D lớn hơn.
  - Cửa sổ xoá được phần phạt River, nhưng không xoá được quãng bay thêm.
  - Cái được là ít cluster thiếu dữ liệu hơn (0/4, 2/6, 2/8 so với 1/4, 2/6, 4/8).
- **Tốt nhất trên cả 3 bản đồ: k‑medoids đường thẳng + cửa sổ (725 / 867 / 899 s).** Nhưng hơn P gốc chỉ vài giây, trong biên sai số.
  - Kết luận của Phần 3 không đổi: cluster gọn và đường bay ngắn quyết định thời gian nhiệm vụ.
  - Tái cấu trúc theo luồng (LANE, MEANDER) chưa bù được quãng bay thêm.

**Phát hiện phụ quan trọng cho lớp 1–2:** với Q = 400 kB, ngay cả k‑medoids cũng có 1/4, 2/6, 4/8 cluster nhận dưới Q. Lý do: Q cần khoảng 2,0 km Axe (một gói mỗi 0,5 m). Nếu lớp 1 thật sự cần 400 kB mỗi critical cell, lớp 2 phải bảo đảm mỗi cluster có ít nhất khoảng 2 km đường bay trên cell của nó, hoặc giảm Q (L ảnh × F kB).

**Mức tin cậy:** 3 bản đồ, mỗi cluster một lượt; số thăm dò, N < 120. Chênh giữa P gốc và P + cửa sổ nằm trong biên sai số. k‑medoids sớm hơn mọi cách chia theo luồng trên cả 3 bản đồ (30–212 s), cùng chiều ở mọi cặp.

Hình (không chữ):
- `figures/fixes-results.png`: năm ô.
  - Bốn ô đầu là River xong TB, thời điểm mọi critical cell đủ dữ liệu, kết thúc nhiệm vụ (± CI 95 %), và D TB (kB), mỗi ô ba cụm k4 / k6 / k8.
  - Ô cuối: mỗi điểm là một cluster; trục ngang là chiều dài Axe của toàn D, trục dọc là critical cell chậm nhất.
  - Màu theo cách chia: xanh dương tròn k‑medoids, vàng thoi k‑medoids + đường cong, cam vuông LANE, xanh lục tam giác MEANDER, hồng tam giác ngược MEANDER span. Điểm đặc là đầy đủ D, điểm rỗng là cửa sổ.
- `figures/fixes-maps.png`: hàng k4 / k6 / k8, cột k‑medoids, k‑medoids + đường cong, LANE, MEANDER, MEANDER span. Critical cell tô theo thời gian River của bản đầy đủ D.

