# Báo cáo mô phỏng 2026-11-01: cơ chế takeover (dấu ranh giới) cho River khi đường bay lệch

Nối tiếp `paper/SIM-REPORT-2026-10-31-vi.md` §3 (thử nghiệm gió). CLAUDE.md §8 mục 257–259 và yêu cầu ngày 2026-11-01.
Log, script, số liệu thô: `logs/2026-11-01_0600-takeover/` (`compare.md`, `compare.csv`).

## 1. Vấn đề

River giao cho mỗi SPINE cell *a* một đoạn gói Seg(*a*) theo đường bay **dự kiến**. Khi gió đẩy UAV lệch ngang
khoảng R50 (≈ 99 m ở r100), các gói của Seg(*a*) rơi vào cell *b* khác, không kề *a*. Cơ chế sửa cũ chỉ hỏi cell kề, nên
SPINE cell không bao giờ đủ đoạn của mình. Bank, Ring và critical cell phía sau vì thế đứng chờ tới giới hạn 900 s.
Ở σ = 200 m, River không sửa lỗi chỉ xong 3/45 critical cell, T\* = 3 576 s (danh nghĩa 892 s).

## 2. Cơ chế (bước sửa dựa trên kế hoạch, không thay kế hoạch)

Takeover **không phải khám phá nội dung lúc chạy**. Mỗi cell tra bảng Seg do BS phát trước khi bay. Nó chỉ báo khi
đã giữ gói thuộc Seg của một SPINE cell khác, tức là khi đường bay thực lệch khỏi kế hoạch. Khi bay đúng kế hoạch, bước
này không phát frame nào (σ = 50 m: 0 lần kích hoạt). Như vậy luận điểm "River không cần khám phá nội dung lúc chạy"
vẫn đúng: takeover là một bước sửa sai lệch so với kế hoạch đã có.

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
- **Khám phá người giữ gói là lý tưởng hoá (oracle):** vị trí người giữ lấy thẳng từ bit nhận thật. Bản tin TAKEOVER
  (bước 3–4) không được mô phỏng thành frame, và độ trễ của vòng báo cáo không có trong T\*. Chỉ frame yêu cầu
  *a*→*b* và dữ liệu *b*→*a* được mô phỏng. Bài phải ghi "holder discovery idealised".
- Takeover cần mọi cell của cụm có trong mô phỏng, vì cell giữ gói có thể nằm ngoài kế hoạch (cụm 1: 1 535 → 1 651 node).
- Đầu vào giữ nguyên: cùng pass gió (bit nhận của chiến dịch 2026-10-31), cùng bản đồ k8-s1, kênh r100, seed ns-3,
  100 lượt lớp 1 ghép cặp. Binary: `CAMP-BINT` = `CAMP-BINW` + river-bin mới (commit 70ef55e).

## 4. Kết quả

- "Trước" là River trên đường gió, "sau" là River + takeover, "danh nghĩa" là River trên đường dự kiến (cùng seed).
- **Sẵn sàng** dùng đúng định nghĩa của bài (117 s): với mỗi cụm, thời điểm critical cell cuối cùng xong, tính từ lúc
  UAV rời cụm (900 s nếu chưa xong), rồi lấy trung bình qua 8 cụm. *Bản đầu của báo cáo này lấy cực đại qua các cụm
  (167–203 s); con số đó đã bỏ.*
- ± của ΔT\* là CI 95 % theo lượt (cùng một mạng).

| σ (m) | seed | critical cell xong, trước → sau | sẵn sàng (s): danh nghĩa / trước / sau | gói SPINE thiếu | T\* danh nghĩa | T\* trước | T\* sau | T\* sau − danh nghĩa | ΔT\* sau − trước |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 1 | 45 → 45 | 126 / 115 / 113 | 0 → 0 | 892 | 897 | 874 | −18 | −24 ± 138 |
| 50 | 2 | 45 → 45 | 112 / 113 / 113 | 0 → 0 | 849 | 845 | 811 | −38 | −34 ± 104 |
| 50 | 3 | 45 → 45 | 115 / 115 / 114 | 0 → 0 | 972 | 972 | 1 018 | +46 | +46 ± 196 |
| 100 | 1 | 33 → **45** | 126 / 305 / **117** | 1 487 → 0 | 892 | 1 218 | 872 | −20 | −345 ± 199 |
| 100 | 2 | 40 → **45** | 112 / 214 / **112** | 9 → 0 | 849 | 955 | 814 | −35 | −141 ± 125 |
| 100 | 3 | 33 → **45** | 115 / 313 / **118** | 33 → 0 | 972 | 1 423 | 1 027 | +56 | −396 ± 231 |
| (200) | (1) | (3 → 45) | (126 / 900 / 109) | (19 202 → 0) | (892) | (3 576) | (873) | (−19) | (−2 703 ± 320) |

**T\* sau trừ T\* danh nghĩa, trung bình theo seed (CI 95 %, t, n = 3):**
- σ = 100 m: **+0,2 ± 121 s** với takeover (từng seed −20 / −35 / +56); **+294 s** khi không có takeover.
- σ = 50 m: −3,5 ± 110 s (từng seed −18 / −38 / +46). Ở mức này takeover không kích hoạt, nên hàng này chính là dải
  nhiễu do việc thêm node ngoài kế hoạch vào mô phỏng làm đổi luồng số ngẫu nhiên của ns-3.

Cách đọc:

- **σ = 100 m (kết luận chính, 3 seed):**
  - mọi critical cell đều xong (135/135, trước 106/135);
  - sẵn sàng 112–118 s, so với danh nghĩa 112–126 s và 214–313 s khi không có takeover;
  - T\* trung bình bằng mức danh nghĩa. Độ lệch từng seed (−35 đến +56 s) nằm trong cùng dải nhiễu với hàng σ = 50 m.
    **Không viết "within 20 s".**
- **Chỉ kích hoạt khi lệch.** σ = 50 m: 0 SPINE cell kích hoạt. σ = 100 m: 2–5 cell mỗi seed.
- **Số hop không tăng** ở σ ≤ 100 m (±1,3 %).
- **σ = 200 m chỉ là minh hoạ** (1 realisation, đường bay có lúc vượt 1 g theo báo cáo 31/10). Chỉ nhắc trong ngoặc.

## 4b. Chặn trên chi phí của vòng báo cáo (oracle), tính từ log có sẵn

Không chạy mô phỏng mới. `logs/2026-11-01_0600-takeover/report_bound.py` dùng lại bit nhận, kế hoạch, bảng định tuyến và
gateway của các lượt chạy gió, và áp đúng luật chọn người giữ của mã ns-3. Số cặp tìm được khớp mô phỏng (σ = 100 m:
10 / 2 / 2 cặp ở 5 / 2 / 2 SPINE cell).

Giả thiết tính toán:
- Frame báo cáo: 2 B id SPINE cell + 4 B cho mỗi dải gói, 21 dải mỗi frame.
- τ = 7 ms cho mỗi hop radio (frame tối đa 4,3 ms + backoff CSMA không khe + ACK).
- Hop radio của một đường cell = hop từ CL tới cell kế tiếp + hop từ gateway vào tới CL của cell đó.

| σ (m) | seed | cặp (SPINE, người giữ) | SPINE cell thiếu | hop cell max | hop radio max | frame mỗi báo cáo, max | trễ đường dài nhất | trễ nếu mọi frame tuần tự, ×4 lần thử (cụm xấu nhất) | nếu mọi người giữ đều báo |
|---|---|---|---|---|---|---|---|---|---|
| 50 | 1–3 | 0 | 0 | – | – | – | 0 | 0 | ≈ 540 báo cáo |
| 100 | 1 | 10 | 5 | 3 | 25 | 2 | 0,34 s | 4,9 s | 581 |
| 100 | 2 | 2 | 2 | 2 | 17 | 1 | 0,12 s | 0,8 s | 542 |
| 100 | 3 | 2 | 2 | 2 | 15 | 1 | 0,10 s | 0,4 s | 578 |

Kết luận:

- **Phía người giữ không thể tự báo cáo**, vì họ không biết SPINE cell có thiếu gói hay không. Nếu mọi người giữ đều báo,
  sẽ có khoảng 540 báo cáo mỗi seed ngay cả khi bay đúng kế hoạch: bước này không còn "im lặng" và mâu thuẫn với luận
  điểm của bài.
- **Thiết kế đúng là SPINE cell khởi xướng.** Sau bước sửa từ cell kề, nếu vẫn thiếu gói của Seg(*a*), SPINE cell *a*
  hỏi trong phạm vi tối đa 3 hop cell; chỉ cell có gói mới trả lời. Ở σ = 50 m không SPINE cell nào thiếu, nên không có
  frame nào. Ở σ = 100 m có 2–5 SPINE cell khởi xướng.
- **Độ trễ thêm** (đi và về, nên gấp đôi đường dài nhất):
  - khoảng 0,2–0,7 s, so với thời điểm sẵn sàng 112–118 s;
  - chặn trên bi quan (mọi frame của cụm tuần tự, 4 lần thử) là 0,4–4,9 s cho cụm xấu nhất, nên trung bình 8 cụm tăng
    dưới 1 s.
- **Đính chính (sau câu hỏi của người dùng):**
  - **Bảng trên chưa tính frame của vòng hỏi lan.** Mỗi lần khởi xướng gửi tới 6–36 cell nằm trong 3 hop qua
    gateway, tức 39–219 lần phát radio. Tính cả các frame này, chặn trên bi quan (mọi frame tuần tự, 4 lần thử) là
    **6,6–15,6 s cho cụm xấu nhất**, không phải "dưới 5 s". Trễ theo đường dài nhất không đổi, vì các frame lan
    song song: khoảng 0,1–0,35 s mỗi chiều.
  - **Mô phỏng gửi yêu cầu takeover cùng lúc với gom nội cell và sửa từ cell kề**, chứ không chờ hai bước này xong.
    Thiết kế thật phải chờ, nên thời điểm sẵn sàng ở các cụm có takeover bị đánh giá lạc quan. Phần trễ thêm (thời
    gian gom và sửa từ cell kề của SPINE cell đó) không tính được từ log.
- **Câu gợi ý cho bài:** "(holder discovery idealised; a SPINE-initiated query over at most 3 cell hops (≤ 25 radio
  hops, ≤ 2 frames per reply) adds an estimated 0.2–0.7 s along its longest path; the repair is not sequenced after the adjacent-cell repair in our simulation)". Chưa nên viết "under 5 s".
- Đây vẫn là ước lượng, không phải số đo. Mô phỏng tường minh (cách 2) và ánh xạ theo đường bay thực (cách 3) để cho
  bản journal.

## 5. Câu gợi ý cho bài (tiếng Anh, SPINE)

> River assigns each SPINE cell the packet range of the *planned* track. With a cross-track error of about one R50,
> part of that range falls on non-adjacent cells. At σ = 100 m, 29 of 135 critical cells miss the 900 s limit, and T\*
> grows by 294 s. We add a plan-based *takeover* repair. No content is discovered at run time: each cell checks the
> Seg table it already holds and reports only packets of another SPINE cell's segment. The step therefore stays silent
> when the flown track matches the plan. The SPINE cell pulls those packets along its gateway path, and Bank and Ring
> proceed unchanged. With takeover (holder discovery idealised), all 135 critical cells complete at σ = 100 m
> (3 seeds), readiness returns to 112–118 s, and mean T\* equals the on-plan value (+0.2 ± 121 s, 95 % CI over seeds).
> The per-seed deviations lie in the same band as at σ = 50 m, where takeover never triggers (one realisation at
> σ = 200 m: 45/45 cells, T\* −19 s).

## 6. Giới hạn

- σ = 200 m mới có 1 seed. Seed 2, 3 cần pass gió mới cho cả River trước và sau (khoảng 2 lượt × 8 cụm).
- Khám phá người giữ là oracle. Về frame, chi phí có thể nhỏ (khoảng 1 frame điều khiển mỗi cặp, 2–10 cặp ở σ = 100 m).
  Về thời gian, chi phí chưa đo: vòng báo cáo TAKEOVER chạy sau khi gom nội cell và trước khi sửa SPINE, nên sẽ cộng
  thêm vào thời điểm sẵn sàng.
- Ba seed cho CI theo seed rộng (±110–121 s). Chỉ khẳng định "trung bình bằng danh nghĩa", không khẳng định chặt hơn.
- Năng lượng chưa tính lại cho rfT. Số hop cho thấy không tăng.
