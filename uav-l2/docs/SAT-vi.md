# Ngưỡng bão hoà và điểm tối ưu theo hình dạng cụm

Lời gốc: CLAUDE.md §8 mục 120–121.
Mã: `tools/sat_strip.py` (một cụm dạng dải qua ns‑3), `tools/sat_report.py` (bảng, hình, chi phí cấp miền); River cửa sổ theo từng critical cell: `uav-coop2/tools/river_plan.py`, `river_export.py --windowAt crit`, `uav-coop2/examples/coop2-river.cc`.
Log: `logs/2026-10-21_1738-saturation/`. Dữ liệu: `docs/data/sat/{strips,shapes,crit,domain}.csv`.

## Tóm tắt

1. **River hiện tại (một cửa sổ 400 kB quanh CH) bão hoà theo chiều dài ở khoảng 2 km.** Đó đúng là độ dài của cửa sổ dọc đường bay. Từ 2 lên 3 km, critical cell cuối xong chậm hơn 2,7–4,8 lần (13–33 s thành 53–102 s), và số khung trên mỗi critical cell tăng 2–7 lần.
2. **Điều chỉnh: mỗi critical cell một cửa sổ, là bản sao bộ manh mối gần nó nhất.** Cách này gỡ giới hạn chiều dài. Ở 6 km, critical cell cuối vẫn xong trong 19–32 s.
3. **Cận dưới của chiều dài là khoảng 2 km.** Cụm dài 1,5 km không chứa trọn một bản bộ manh mối, nên không critical cell nào nhận đủ.
4. **Bề ngang: thời gian River tăng dần, chưa gãy tới 10 cell.** Critical cell cách đường bay trong 600 m xong trong 7–10 s; xa hơn thì 15–39 s. Từ 6 lên 10 cell, critical cell cuối chậm thêm 5–18 s, còn số khung trên mỗi critical cell tăng 1,6–2,7 lần.
5. **Điểm tối ưu cấp miền:** luồng càng rộng thì tour đội 1 càng ngắn, và khoản lợi này lớn hơn nhiều so với River chậm thêm. Trong lưới đã thử, tốt nhất là **luồng rộng 8–10 cell, cụm dài 2–4 km**, tức khoảng 110–260 cell mỗi cụm. Bề ngang nên chọn để miền chia thành ít luồng nhất.

Mọi số ở đây là số thăm dò: 3 seed cho mỗi hình dạng.

## 1. Cách làm

- **Cụm dạng dải:** rộng W cell (W × 173 m), dài L km. Node một trên 35 × 35 m, thuộc tính ngẫu nhiên như mọi bản đồ.
- **Vai trò:** CH, CL và critical cell chọn như trong nhiệm vụ.
- **Lượt bay:** UAV bay dọc trục dải, qua CH (Dubins, vào và ra ngoài dải).
- **ns‑3:** lượt phát, rồi River: Circle chuẩn bị sẵn, MAC 802.15.4 đầy đủ, lưới 7 màu, gateway theo chất lượng liên kết.
- **Hai cách đặt cửa sổ 400 kB** (4 041 gói):
  - **quanh CH:** một cửa sổ chung cho cả cụm, như nhiệm vụ hiện tại;
  - **theo từng critical cell:** mỗi critical cell cần Q gói liền nhau của Axe quanh chỗ UAV bay gần nó nhất.
    - UAV phát lặp bộ manh mối liên tục, nên bất kỳ đoạn 400 kB liền nhau nào cũng là một bản đủ.
    - Giả định thêm: gói cùng vị trí ở hai bản phát liền nhau là một, nên thay thế được cho nhau.
- **Lưới quét:** W ∈ {3; 4,5; 6; 8; 10} × L ∈ {1,5; 2; 3; 4; 6} km × seed 1–3, tức 75 dải.
  - Cửa sổ theo từng critical cell chạy ở mọi hình dạng.
  - Cửa sổ quanh CH chỉ chạy với L ≤ 3 km. Chạy thử cho thấy ở 4 km nó đã quá đắt: dải 6 × 4 km tốn 14 phút máy, dải 10 × 4 km không xong sau 25 phút.
- Chiến dịch mất 2,5 giờ, cả 75 dải thoát bình thường.

## 2. Ngưỡng thứ nhất: chiều dài, với cửa sổ quanh CH

Lúc critical cell cuối có đủ cửa sổ (s, sau khi UAV rời cụm), L = 1,5 / 2 / 3 km:

| W (cell) | Cửa sổ quanh CH | Cửa sổ theo critical cell |
|---|---|---|
| 3 | 4 / 13 / **62** | 4 / 12 / 20 |
| 4,5 | 7 / 20 / **53** | 7 / 18 / 20 |
| 6 | 8 / 22 / **75** (4 km: 88) | 8 / 21 / 26 (4 km: 20) |
| 8 | 10 / 26 / **86** | 10 / 25 / 32 |
| 10 | 18 / 33 / **102** | 18 / 31 / 39 |

Số khung trên mỗi critical cell ở L = 3 km: 27–42 nghìn với cửa sổ quanh CH, 4–12 nghìn với cửa sổ theo critical cell.

**Nguyên nhân.** Với cửa sổ quanh CH, thời gian xong tăng theo khoảng cách tới CH dọc đường bay (mọi dải L ≥ 2 km):

| Cách CH dọc đường bay | 0–0,5 km | 0,5–1 km | 1–1,5 km | 1,5–2 km |
|---|---|---|---|---|
| Xong, trung bình (s) | 12 | 32 | 43 | 62 |
| Xong, phân vị 90 (s) | 27 | 59 | 85 | 88 |

Critical cell xa CH không nghe được đoạn quanh CH. Chúng kéo dữ liệu từ đúng đoạn Axe đó, nên mọi luồng dồn về cùng một chỗ.

## 3. Cửa sổ theo từng critical cell: không còn bão hoà theo chiều dài

| W \ L (km) | 1,5 | 2 | 3 | 4 | 6 |
|---|---|---|---|---|---|
| Cell mỗi cụm, W = 6 | 63 | 84 | 122 | 164 | 245 |
| Critical cell cuối xong (s), W = 3 | 4 | 12 | 20 | 18 | 19 |
| W = 4,5 | 7 | 18 | 20 | 15 | 24 |
| W = 6 | 8 | 21 | 26 | 20 | 27 |
| W = 8 | 10 | 25 | 32 | 29 | 20 |
| W = 10 | 18 | 31 | 39 | 38 | 32 |
| Critical cell nhận đủ bộ manh mối | 0 % | 100 % | 100 % | 100 % | 100 % |

- **Từ 3 km trở lên, thời gian xong không tăng theo chiều dài nữa.** Mỗi critical cell chỉ cần bản sao gần nó, phần lớn đã nghe được trong lượt bay.
- **L = 2–3 km tốn khung hơn L = 4–6 km**, ví dụ W = 8: 9–11 nghìn so với 4–6 nghìn khung mỗi critical cell. Ở cụm ngắn, cửa sổ của critical cell gần hai đầu bị kẹp vào cả đoạn Axe, nên phải kéo từ xa.
- **L = 1,5 km xong nhanh nhưng vô ích:** đoạn bay trong cụm ngắn hơn bộ manh mối (khoảng 2 km), nên không critical cell nào có đủ 12 manh mối.

## 4. Ngưỡng thứ hai: bề ngang

Thời gian xong theo khoảng cách tới đường bay (cửa sổ theo critical cell, mọi dải L ≥ 2 km):

| Cách đường bay | 0–200 m | 200–400 m | 400–600 m | 600–800 m | 800–1 000 m | > 1 000 m |
|---|---|---|---|---|---|---|
| Critical cell | 253 | 151 | 82 | 65 | 26 | 6 |
| Xong, trung bình (s) | 7 | 10 | 10 | 15 | 22 | 26–39 |
| Gói cả cell không nghe được (TB) | 149 | 207 | 144 | 320 | 499 | 525–1 372 |

- **Điểm gãy ở khoảng 600 m**, tức nửa bề rộng River (303 m) cộng khoảng 300 m. Ngoài đó, critical cell nghe được ít hơn trong lượt bay và phải nhận thêm qua River.
- Vì đường bay phải qua CH, mà CH có thể lệch trục tới (nửa bề rộng − 300 m), dải càng rộng càng có critical cell xa đường bay. Ở W = 10, có critical cell cách đường bay tới 1,25 km.
- Theo bề ngang, chi phí tăng dần chứ không gãy hẳn. Ở L = 4 km, W = 3 → 10 cell: critical cell cuối xong 18 → 38 s, khung mỗi critical cell 2,8 → 10 nghìn. Tỉ lệ MAC bỏ cuộc giữ ở 26–42 trên 1 000 khung ở mọi hình dạng, nên chưa có dấu hiệu nghẽn MAC.

**Dải thử rộng 14 cell × 4 km (400 cell, 26 critical cell):** đang chạy; kết quả sẽ thêm vào đây.

## 5. Điểm tối ưu cấp miền

**Mô hình.**
- Một miền chữ nhật dài 6 km, cao DY km, được bay theo các luồng rộng W cell dọc chiều dài, đổi chiều ở cuối mỗi luồng (quay đầu bằng đường Dubins bán kính 255 m). BS ở 1 km phía dưới giữa miền.
- Mỗi luồng cắt thành cụm dài L.
- Critical cell của một cụm có đủ dữ liệu lúc UAV rời cụm cộng thời gian River đo được của hình dạng đó.
- Chỉ số: thời điểm trung bình các critical cell có đủ dữ liệu.

**Kết quả** (số luồng / thời điểm trung bình, s; tốt nhất theo L ≥ 2 km):

| DY \ W (cell) | 3 | 4,5 | 6 | 8 | 10 |
|---|---|---|---|---|---|
| 3 km | 6 / 507 | 4 / 383 | 3 / 317 | 3 / 329 | **2 / 260** |
| 4 km | 8 / 643 | 6 / 524 | 4 / 390 | **3 / 329** | 3 / 340 |
| 5 km | 10 / 779 | 7 / 595 | 5 / 463 | 4 / 406 | **3 / 340** |
| 6 km | 12 / 915 | 8 / 666 | 6 / 537 | 5 / 482 | **4 / 421** |
| 8 km | 16 / 1 188 | 11 / 878 | 8 / 683 | 6 / 559 | **5 / 501** |

- **Tour đội 1 chi phối:** bớt một luồng là bớt 4–6 km bay và một lần quay đầu, tức 100–150 s. Thời gian xong trung bình của River ở cụm rộng 10 cell chỉ hơn cụm rộng 6 cell 4–7 s.
- **Vì vậy, chọn bề ngang sao cho miền chia thành ít luồng nhất.** Trong khoảng đã đo (≤ 10 cell), River chưa đắt tới mức đổi được kết luận này. Ví dụ DY = 4 km: 8 cell tốt hơn 10 cell, vì cả hai đều cần 3 luồng nhưng luồng 10 cell quay đầu xa hơn.
- **Chiều dài: 2–4 km.** Ngắn hơn 2 km thì thiếu bộ manh mối. Dài hơn không làm River chậm, nhưng cụm lớn hơn, nhiều critical cell hơn trên một CH.
- **Điểm tối ưu đề xuất:** luồng rộng **8–10 cell** (1,4–1,7 km), cụm dài **2–3 km**, khoảng **110–190 cell** mỗi cụm, với River **cửa sổ theo từng critical cell**. Chặn trên 80 cell hiện nay là quá nhỏ cho cụm dạng luồng.

**Giới hạn của mô hình cấp miền:**
- Đây chưa phải T\*. Chưa tính khe LoRa của CH và pha 2.
- Miền là hình chữ nhật không hồ. Trên bản đồ thật, luồng bị hồ cắt (`L2-DIAG-vi.md` §2).
- Dải chỉ có một hướng bay thẳng; chưa có đường cong.

## 6. Bước tiếp theo (chờ duyệt)

1. Chạy lại nhiệm vụ trên 40 bản đồ với cửa sổ theo từng critical cell cho **cả k‑medoids lẫn MEANDER‑K**, để so công bằng: cùng River, đúng K cluster.
2. Đặt MEANDER‑K ở điểm tối ưu trên: luồng 8 cell, cụm khoảng 2–3 km.
3. Tăng số seed ở các hình dạng quanh điểm tối ưu (quy tắc N ≥ 120 cho số công bố).

## Hình (không chữ)

- `figures/sat-grid.png`: bốn ô lưới; trong mỗi ô, hàng là bề ngang (dưới lên: 3, 4,5, 6, 8, 10 cell), cột là chiều dài (trái sang: 1,5, 2, 3, 4, 6 km). Màu đậm là giá trị lớn.
  - Ô 1 (xanh dương): critical cell cuối xong, cửa sổ theo từng critical cell.
  - Ô 2 (tím): khung trên mỗi critical cell, cửa sổ theo từng critical cell.
  - Ô 3 (xanh lá): tỉ lệ critical cell có đủ bộ manh mối; cột 1,5 km nhạt (0 %), còn lại đậm (100 %).
  - Ô 4 (cam): critical cell cuối xong, cửa sổ quanh CH; ô trắng là chưa chạy. Cột 3 km đậm hẳn: ngưỡng chiều dài.
- `figures/sat-lateral.png`: mỗi chấm là một critical cell (cửa sổ theo từng critical cell). Trục ngang là khoảng cách tới đường bay (vạch lưới mỗi 200 m), trục dọc là thời gian xong (vạch lưới mỗi 10 s). Màu theo bề ngang dải, từ tím (3 cell) tới vàng (10 cell). Các chấm nằm thấp và phẳng tới khoảng 600 m, rồi tản lên cao.
- `figures/sat-domain.png`: miền 6 × 4 km. Trục ngang là bề ngang luồng (3 tới 10 cell). Trái: thời điểm trung bình critical cell có đủ dữ liệu; phải: thời điểm muộn nhất. Mỗi đường là một chiều dài cụm, từ xanh đậm (1,5 km) tới vàng (6 km). Đáy ở 8 cell.
