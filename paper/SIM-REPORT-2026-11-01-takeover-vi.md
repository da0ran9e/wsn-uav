# Báo cáo mô phỏng 2026-11-01: cơ chế takeover (dấu ranh giới) cho River khi đường bay lệch

Nối tiếp `paper/SIM-REPORT-2026-10-31-vi.md` §3 (thử nghiệm gió). CLAUDE.md §8 mục 257–259 và yêu cầu ngày 2026-11-01.
Log, script, số liệu thô: `logs/2026-11-01_0600-takeover/` (`compare.md`, `compare.csv`).

## 1. Vấn đề

River giao cho mỗi SPINE cell *a* một đoạn gói Seg(*a*) theo đường bay **dự kiến**. Khi gió đẩy UAV lệch ngang
khoảng R50 (≈ 99 m ở r100), các gói của Seg(*a*) rơi vào cell *b* khác, không kề *a*. Cơ chế sửa cũ chỉ hỏi cell kề, nên
SPINE cell không bao giờ đủ đoạn của mình. Bank, Ring và critical cell phía sau vì thế đứng chờ tới giới hạn 900 s.
Ở σ = 200 m, River không sửa lỗi chỉ xong 3/45 critical cell, T\* = 3 576 s (danh nghĩa 892 s).

## 2. Cơ chế (bổ trợ cho River, không thay kế hoạch)

```
Algorithm TAKEOVER (River self-adapting to flight-path error)
Input: Seg(a) for every SPINE cell a (from the BS before take-off); H(c): packets gathered at CL of cell c
 1: // UAV (optional): stamp each packet with the cell id it is actually over (boundary marker, 8 B per cell change)
 2: for each cell c after in-cell gathering do
 3:     for each SPINE cell a != c with H(c) ∩ Seg(a) != ∅ do
 4:         send TAKEOVER(a, H(c) ∩ Seg(a)) to a along the shortest cell path
 5: for each SPINE cell a do
 6:     L ← Seg(a) \ (H(a) ∪ packets held by adjacent cells)     // the old repair covers adjacent cells
 7:     for each s ∈ L do b(s) ← nearest cell that reported s
 8:     for each holder b do send REQ(L_b) along path a→b; b returns the packets along b→a
 9: continue River unchanged: SPINE → Bank → Ring → critical cell
```

- SPINE cell vẫn là nơi phát lại cho Bank và Ring; chỉ nguồn gom đoạn của nó thay đổi.
- Không có UAV gắn dấu, cell *b* vẫn tự biết mình giữ gói nào của Seg(*a*) bằng cách so tập đã nghe với bảng Seg do BS
  phát trước. Dấu ranh giới chỉ giúp *a* biết sớm ai giữ mà không cần TAKEOVER đi khắp cụm.

## 3. Cài đặt trong mô phỏng

- `coop2-river.cc` có cờ `--takeover` (đi cùng `--repair`). Tag `rfT` trong `mission.py` = River `--prep=full --takeover=true --repair=20`.
- Cell giữ gói được tìm bằng BFS trên các liên kết gateway trong cụm. Yêu cầu là một frame điều khiển đi theo đường
  cell *a*→*b*; dữ liệu về theo đường ngược lại, qua các cặp gateway và lịch PECEE như mọi đường River khác.
- Mô phỏng dùng biến thể "suy từ mặt đất": vị trí người giữ lấy từ bit nhận thật. Bản tin TAKEOVER (bước 3–4) không
  được mô phỏng riêng. Chi phí của nó được gộp vào frame yêu cầu, một frame cho mỗi cặp (*a*, *b*).
- Takeover cần mọi cell của cụm có trong mô phỏng, vì cell giữ gói có thể nằm ngoài kế hoạch (cụm 1: 1 535 → 1 651 node).
- Đầu vào giữ nguyên: cùng pass gió (bit nhận của chiến dịch 2026-10-31), cùng bản đồ k8-s1, kênh r100, seed ns-3,
  100 lượt lớp 1 ghép cặp. Binary: `CAMP-BINT` = `CAMP-BINW` + river-bin mới (commit 70ef55e).

## 4. Kết quả

"Trước" là River trên đường gió, "sau" là River + takeover, "danh nghĩa" là River trên đường dự kiến (cùng seed).
"Cell cuối" tính từ lúc UAV rời cụm; 900 s nghĩa là có cell không xong. ± của ΔT\* là CI 95 % theo lượt (cùng một mạng).

| σ (m) | seed | critical cell xong, trước → sau | cell cuối (s) | gói SPINE thiếu | T\* danh nghĩa | T\* trước | T\* sau | ΔT\* sau − trước | lượt sau tốt / xấu hơn |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 1 | 45 → 45 | 187 → 187 | 0 → 0 | 892 | 897 | 874 | −24 ± 138 | 50 / 50 |
| 50 | 2 | 45 → 45 | 198 → 203 | 0 → 0 | 849 | 845 | 811 | −34 ± 104 | 51 / 49 |
| 50 | 3 | 45 → 45 | 177 → 167 | 0 → 0 | 972 | 972 | 1 018 | +46 ± 196 | 47 / 53 |
| 100 | 1 | 33 → **45** | 900 → 188 | 1 487 → 0 | 892 | 1 218 | **872** | −345 ± 199 | 58 / 42 |
| 100 | 2 | 40 → **45** | 900 → 201 | 9 → 0 | 849 | 955 | **814** | −141 ± 125 | 55 / 45 |
| 100 | 3 | 33 → **45** | 900 → 182 | 33 → 0 | 972 | 1 423 | **1 027** | −396 ± 231 | 66 / 34 |
| 200 | 1 | 3 → **45** | 900 → 167 | 19 202 → 0 | 892 | 3 576 | **873** | −2 703 ± 320 | 94 / 6 |

Tổng theo mức lệch (T\* sau trừ T\* danh nghĩa cùng seed):

| σ (m) | độ lệch ngang thực tế: sd / max (m) | trước | sau |
|---|---|---|---|
| 50 | 9–80 / 31–173 | +0,5 s | −3 s (takeover không kích hoạt) |
| 100 | 18–160 / 62–346 | +294 s (+33 %) | **+0,2 s** |
| 200 | 67–206 / 223–692 | +2 684 s | **−19 s** |

Cách đọc:

- **Takeover đưa River về lại mức danh nghĩa ở mọi mức lệch đã thử.** Mọi critical cell đều xong (135/135 ở σ = 100 m,
  45/45 ở σ = 200 m) và cell cuối sẵn sàng sau 167–203 s, như trên đường danh nghĩa. T\* chỉ cách danh nghĩa trong
  phạm vi nhiễu của lớp 1.
- **Chỉ kích hoạt khi cần.** σ = 50 m: 0 SPINE cell dùng takeover. σ = 100 m: 2–5 cell mỗi seed. σ = 200 m: 42 cell, 83
  cặp (SPINE cell, cell giữ).
- **Chi phí rẻ hơn không sửa.** Ở σ = 200 m, số hop dữ liệu giảm từ 6,04 M xuống 3,24 M: không còn cảnh critical cell
  hỏi lại mãi khi đang kẹt. Ở σ ≤ 100 m, số hop gần như không đổi (±1,3 %).
- **ΔT\* ở σ = 50 m chỉ là nhiễu.** Takeover không chạy ở đây. T\* khác 24–46 s vì mô phỏng thêm các node ngoài kế hoạch,
  làm đổi luồng số ngẫu nhiên của ns-3 (thời điểm CSMA, thứ tự xong của từng cell). Lượt tốt/xấu là 50/50, 51/49,
  47/53, và CI theo lượt (±104–196 s) phủ cả 0. Trong triển khai thật, khi không kích hoạt thì không có gì thay đổi.

## 5. Câu gợi ý cho bài (tiếng Anh, SPINE)

> River assigns each SPINE cell the packet range of the *planned* track. A cross-track error of about one R50 (≈100 m)
> moves part of that range to non-adjacent cells, so the SPINE cell never completes its segment. At σ = 100 m, 21 of
> 135 critical cells miss the 900 s limit, and T\* grows by 33 %. We add a *takeover* step. A cell that heard packets
> of another SPINE cell's segment reports them, optionally keyed by boundary markers that the UAV broadcasts at each
> actual cell change. The SPINE cell then pulls them along the gateway path, and Bank and Ring proceed as planned.
> With takeover, all critical cells complete at σ = 100 m (3 seeds) and σ = 200 m (cross-track error up to 692 m).
> T\* stays within 20 s of the on-plan value, and ground hops do not increase. The step is inactive at σ = 50 m.

## 6. Giới hạn

- σ = 200 m mới có 1 seed. Seed 2, 3 cần pass gió mới cho cả River trước và sau (khoảng 2 lượt × 8 cụm).
- Bản tin TAKEOVER và dấu ranh giới của UAV chưa được mô phỏng thành frame riêng; vị trí người giữ lấy từ bit nhận thật
  (oracle). Chi phí thực thêm vào khoảng 1 frame điều khiển cho mỗi cặp, tối đa 83 cặp ở σ = 200 m, nhỏ so với 3,2 M hop.
- ΔT\* theo lượt có phương sai lớn, nên ở σ = 50 m không kết luận được tốt hơn hay xấu hơn; chỉ khẳng định "không đổi".
- Năng lượng chưa tính lại cho rfT. Số hop cho thấy không tăng.
