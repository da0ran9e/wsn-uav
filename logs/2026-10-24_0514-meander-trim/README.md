# 2026-10-24 · MEANDER đường bay thẳng hẳn, giao vừa đủ (CLAUDE.md §8 mục 153)

**Mục đích:** thử luồng bay thẳng hẳn và chỉ bay đủ độ dài cần giao cho mỗi cụm, không bay thừa. Chạy trên bản đồ ngẫu nhiên `restructure.domain(8, s)`, seed 1–3, BS phía nam. So với CHORD-T cùng số cụm; chỉ tính hình học (chưa chạy ns-3).

**Chẩn đoán trước khi sửa:** ở lần chạy mục 151, đặt `--straight inf` chỉ thay đường giữa của mỗi luồng (luồng uốn theo địa hình) bằng dây cung nối hai đầu. Dây cung vì thế chạy ra ngoài luồng: ở k8-s2, cụm C5 bay 4,4 km nhưng chỉ 1,3 km nằm trên cell của chính nó. Ngoài ra, mỗi cụm nhận từ 1 đến 2 lần độ dài Axe cần, nên tổng đoạn bay trên cụm là 15,6–18,3 km, trong khi 5 cụm chỉ cần khoảng 10 km.

**Mã (`uav-l2/tools/meander_lane.py`):**

- `--parallel`: dùng luồng thẳng, song song (`swath.route`). Hướng (bước 5°) và độ lệch được chọn để tổng đường bay ngắn nhất.
- `--trim T`: chỉ dùng cùng `--minAxe`. Phần đất còn thừa của mỗi luồng (sau khi chia thành m cụm, mỗi cụm minAxe) được cắt khỏi hai đầu luồng. Mỗi đầu cắt tối đa RHO + T cell, vì đoạn dẫn vào/ra vẫn phát gói trên đoạn RHO đó. Các cell ở phần bị cắt vẫn thuộc cụm đầu hoặc cụm cuối của luồng.
- Khi có `--trim`, hướng bay được chọn theo quãng đường bay sau khi cắt, cộng thêm phần mỗi cụm còn thiếu so với minAxe (quy ra mét bay).
- `partition` trả thêm `info`, gồm số mét trên cell của từng cụm và số mét đã cắt.

`uav-l2/tools/trim_sweep.py` (mới) chạy hai biến thể với `--minAxe 2.1` (một bản tập manh mối cần 2,02 km, cộng một chút dư) và `--reach 1000` (không kéo đường bay về critical cell; đường chỉ uốn để đi qua CH, vì pass ns-3 yêu cầu dPath < 1 m):

- `par`: luồng thẳng, không cắt đầu.
- `par-trim5`: luồng thẳng, cắt đầu luồng tối đa 5 cell.

Các thư mục CHORD-T dùng lại từ lần chạy mục 151 (`SW2`, liên kết vào `T153b`, cùng lệnh và cùng số cụm). Riêng k8-s3 với K = 5 là chạy mới.

**Lệnh:** `sweep.md` chạy quét, `ml-*.md` và `chord-s3-K5.md` là từng lần chạy. Bảng kết quả ở `trim-table.md`; hình do `fig-s*.md` sinh ra.

**Kết quả: tour ở góc nghiêng 45°, đã cộng thời gian bù giao đủ (s)**

| seed | CHORD-T | MEANDER thẳng, không cắt | MEANDER thẳng, giao vừa đủ | trên cụm (km): CHORD-T / thẳng / vừa đủ | critical trong 5 cell: CHORD-T / vừa đủ |
|---|---|---|---|---|---|
| 1 | 506 (K 5) | 630 | **490** | 11,7 / 18,4 / 8,8 | 77 % / 93 % |
| 2 | 515 (K 5) | 647 | **485** | 11,4 / 19,2 / 7,7 | 73 % / 90 % |
| 3 | **490** (K 5) | 676 (K 6, CHORD-T 552) | 499 | 11,8 / 20,0 / 9,8 | 75 % / 83 % |

- Bản vừa đủ: 4 trong 5 cụm của mỗi bản đồ nhận 40,6–47,4 s trên cell của mình, sát mức cần 40,4 s.
- Mỗi bản đồ có 1 cụm ở luồng biên mỏng (61–112 cell) chỉ nhận 12–30 s, nên phải lượn bù. Phần thời gian lượn đã được tính vào tour.
- Chỉ đặt luồng thẳng mà không cắt thì còn chậm hơn bản uốn cũ: đường giữa luồng bay qua hồ và vịnh, nên phải bay 18–20 km trên cụm.
- Phần cụm vừa đủ còn thua CHORD-T là đoạn nối giữa các luồng (6,0–6,7 so với 4,8–5,8 km) và đường về BS.

**Dang dở:**

- Chưa chạy ns-3. Pass ns-3 bay đều 50 m/s nên chưa mô phỏng được phần lượn bù. Cụm luồng biên thiếu giao sẽ không đủ manh mối trong pass, và CHORD-T cũng có 1–2 cụm như vậy. Cần thống nhất cách xử lý trước khi chạy.
- Ở chỗ ghim CH, đường bay vẫn hơi gãy, lệch tới khoảng 140 m. Có thể chọn CH gần đường bay hơn để đường thẳng hơn nữa.
