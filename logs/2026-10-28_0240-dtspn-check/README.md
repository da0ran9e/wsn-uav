# 2026-10-28 · DTSP-N + River có thật sự zigzag và bay chậm hơn CHORD không (CLAUDE.md §8 mục 192)

**Dữ liệu:** các thư mục chạy seed 1 của `logs/2026-10-27_1714-campaign4` (scratchpad `C4/{CP,LMD,DR}`). Không chạy mô phỏng mới.

**Lệnh:**
- `passes.py ENV K`: với mỗi cụm, đọc pass như đã bay (`c{k}-path-s35.csv` có cột t của `pass_speed.fit`, cùng `c{k}-speed.json`), rồi tính:
  - độ dài và thời gian trên cell của cụm, tốc độ, tổng góc quay;
  - số lần giảm tốc và lượn;
  - số critical cell nằm trong đĩa ξ quanh đường bay.
  - Kết quả: `passes-<env>-k<K>.md`.
- `zigzag_bound.py ENV K`: cận dưới độ dài một đường đi vào đĩa của **mọi** critical cell. Cách tính: lấy TSP mở qua tâm các critical cell, trừ phần đĩa cho phép cắt góc. Kết quả: `zigzag-<env>-k<K>.md`.

## Kết quả (trung bình mỗi cụm)

| kênh, bản đồ | phương án | độ dài trong cụm (m) | thời gian trong cụm (s) | tốc độ (m/s) | góc quay trong cụm | crit trong ξ | tổng pass (s) |
|---|---|---|---|---|---|---|---|
| r200 k16 | CHORD | 2099 | 43,3 | 48,3 | 14° | 42/92 | 850 |
| | LM-Tour | 1560 | 40,5 | 38,5 | 111° | 36/92 | 784 |
| | DTSP-N + River | 1674 | 40,5 | 41,3 | 103° | 47/92 | 879 |
| r200 k12 | CHORD | 2079 | 42,5 | 48,9 | 14° | 32/66 | 655 |
| | DTSP-N + River | 1772 | 40,6 | 43,6 | 101° | 45/66 | 668 |
| r100 k12 | CHORD | 2079 | 42,5 | 48,9 | 14° | 24/66 | 655 |
| | DTSP-N + River | 1834 | 42,4 | 43,0 | 129° | 35/66 | 687 |
| r500 / open k16 | CHORD | 2099 | 43,3 | 48,3 | 14° | 49/92 | 850 |
| | DTSP-N + River | 1666 | 40,5 | 41,1 | 101° | 51/92 | 902 |

## Đọc
1. **Thời gian trên mỗi cụm bị chốt ở khoảng 40,4 s cho mọi phương án.** Một bản truy vấn 400 kB là 4041 gói, mỗi gói 10 ms.
   - CHORD bay dây cung dài nhất, 2,1 km, ở 48 m/s.
   - DTSP-N + River bay 1,7 km ở 41–44 m/s.
   - LM-Tour bay 1,5 km ở 38 m/s, đôi khi lượn thêm.
   - Đường dài hay ngắn trong cụm không đổi thời gian, trừ khi đường dài hơn 50 m/s × 40,4 s ≈ 2 km. Chỗ chậm nhất (25 m/s) là do giảm tốc để đủ gói, không phải do khúc cua.
2. **Khúc cua không bắt UAV giảm tốc.**
   - `bend_lane` giữ độ cong ≤ 1/(2ρ), với ρ = 255 m là bán kính quay ở 50 m/s, nghiêng 45°.
   - `kin_time.profile` chỉ hạ tốc khi độ cong vượt giới hạn đó.
3. **Đường DTSP-N + River hiện nay không phải zigzag qua mọi critical cell.**
   - Tổng góc quay trong cụm chỉ khoảng 100°, ngang LM-Tour.
   - Chỉ 35–51 critical cell (khoảng 50–70 %) nằm trong đĩa ξ của đường bay. CHORD bay thẳng mà tình cờ cũng được 24–49 cell.
   - Hai nguyên nhân trong `lm_tour.every_crit`:
     - `bend_lane` đẩy đường bằng các bump Gauss liên tiếp, bump sau kéo lệch bump trước;
     - mọi bump làm đường ra khỏi cụm rồi vào lại đều bị bỏ.
   - Vậy baseline chưa làm đúng mô tả "uốn vào đĩa của mọi critical cell" (mục 187). Đây có thể chính là lỗi người dùng nghi.
4. **Nếu sửa cho đi vào mọi đĩa:**
   - Cận dưới (TSP qua tâm, cắt góc trong đĩa) cho thấy ở ξ ≥ 199 m, mọi cụm vẫn nằm trong 2 km, nên không chậm thêm.
   - Ở ξ = 99 m (r100) có 9/15 cụm k16 vượt 2 km, chậm thêm ít nhất 58 s tổng cộng.
   - Đường thật phải quay theo Dubins (ρ = 255 m) nên dài hơn cận dưới này. Mức chậm thật chỉ biết khi dựng lại.
5. **Đội 1 ở k16:** DTSP-N + River 1445–1449 s, CHORD 1437 s.
   - Tổng các pass của DTSP-N + River dài hơn 3–6 % (879–902 so với 850 s).
   - Đổi lại, thứ tự tour DTSP-N cho đoạn chuyển giữa các cụm ngắn hơn.
