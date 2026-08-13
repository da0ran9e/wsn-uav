# Luồng hoạt động & cấu trúc giả lập — hiện tại và sắp đổi

Đọc từ mã nguồn ngày 2026-08-08, không đọc từ trí nhớ. `ARCHITECTURE.md` ghi
"Cập nhật 2026-06-30, trạng thái: thiết kế, **chưa code**" — nó mô tả ý định, tài
liệu này mô tả **cái đang chạy**.

Phần cuối (§7) là **delta** sang đặc tả `SIM-SPEC-vi.md`: mỗi quyết định D chạm
vào file nào.

---

## 1. Cấu trúc thư mục — bốn tầng, phụ thuộc một chiều

```
examples/scenario-sar.cc      ← main(): chỉ parse CommandLine rồi gọi SarScenario::Run
   │
helper/sar-config.{h,cc}      ← ORCHESTRATOR: dựng tất cả, chạy, xuất metrics (364 dòng)
   │
   ├── models/network/         ns-3 thuần: node, kênh, PHY
   │     sar-network.cc          BS + UAV + lưới NxN, một LrWpanHelper duy nhất
   │     forest-a2g-loss.cc      Al-Hourani LoS + ITU-R P.833 tán lá
   │     phy-stats.cc            đếm lỗi gói mức PHY (chỉ đo, không điều khiển)
   │
   ├── models/common/          KHÔNG phụ thuộc ns-3 (test độc lập được)
   │     cell-grid.cc            ô lục giác, CL = nút gần tâm nhất, cây BFS trong ô
   │     inter-cell-routing.cc   đồ thị kề giữa các ô
   │     clue-field.cc           trường manh mối + vật gây nhầm (ClutterSource)
   │     target-profile.h        L0..L3, 15 mảnh, 34 400 B
   │     sar-types.h             13 loại gói tin + kích thước byte
   │     sar-params.h            mọi hằng số, có ghi nguồn [Lit]/[Design]/[Measured]
   │     sar-metrics.cc          gom sự kiện → metrics.csv / events.csv / trajectories.csv
   │     gmc.h                   sinh quỹ đạo phủ (GMC) và tour VBS cho tsp-mc
   │
   └── models/application/     ns3::Application — TOÀN BỘ logic chạy ở đây
         sar-ground-app.cc       725 dòng — nút mặt đất, mặt phẳng điều khiển phân tán
         sar-data-uav-app.cc     533 dòng — UAV DATA (rotary-wing)
         sar-fast-uav-app.cc     358 dòng — UAV FAST (fixed-wing)
         sar-bs-app.cc            65 dòng — BS, chỉ nhận REPORT và chốt nhiệm vụ
         region-coordinator.cc   **CHẾT** — điều phối tập trung đã bị gỡ khỏi luồng
         flight-controller.h     Turn/Forward/Climb/Hover trên ConstantVelocity
```

Điểm quan trọng về kiến trúc: **không có bộ điều phối trung tâm**. `sar-config.cc`
dòng 140–143 ghi rõ — mọi quyết định (ai làm lãnh đạo, triệu tập ở đâu, UAV nào
đi) đều xảy ra **qua gói tin trên radio thật**, chịu cùng path loss / fading /
đụng độ như mọi gói khác. `RegionCoordinator` còn trong repo nhưng không được gọi: `sar-config.h` vẫn
`#include` và giữ một `m_coord`, còn `sar-config.cc` **không đụng tới nó lần nào**.
Đây là mã chết — tôi nêu ra chứ không xoá, vì nó không thuộc phạm vi việc đang làm.

---

## 2. Trình tự khởi tạo — `SarScenario::Run()`

| # | việc | ghi chú |
|---|---|---|
| 1 | `SarNetwork::Build()` | **một** `LrWpanHelper` cho toàn bộ node (giữ trong `unique_ptr` của scenario — helper chết là RX chết im lặng) |
| 2 | `BuildCellGrid` + `BuildInterCellRouting` | tầm liên kết = `DeriveG2gRangeM()` ≈ **37 m**, suy từ link budget chứ không đặt tay |
| 3 | vị trí nạn nhân | tất định từ `seed`; `--victimOnNode=0` thì lệch khỏi lưới rồi chọn lại nút gần nhất |
| 4 | `BuildClueField` + `BuildClutter` | mỗi nút nhận `clueQuality` (đọc bằng cue) và `clueQualityFull` (đọc khi đã đủ dữ liệu) |
| 5 | `TargetProfile::Generate()` | cue = L0+L1 = 2 400 B; full = L0..L3 = 34 400 B |
| 6 | app BS | `SetExpectedReports(numUav)` — nhiệm vụ chốt khi **mọi** UAV đã báo |
| 7 | app UAV | chia dải: FAST theo trục **x**, DATA theo trục **y** (trực giao) + đi ngược chiều |
| 8 | app mặt đất | mỗi nút nhận cha trong cây, cờ CL, id ô, tâm ô, và hai giá trị clue |
| 9 | `Simulator::Run()` | rồi `Finalize()` ghi CSV |

Mọi `SetReceiveCallback` gắn **một lần** cho mỗi thiết bị, trước `Run()`.

---

## 3. Luồng chạy — nhánh `proposed`

```mermaid
sequenceDiagram
    participant F as UAV FAST
    participant D as UAV DATA
    participant N as nút thường
    participant L as Cell Leader
    participant B as BS

    F->>N: CUE (chunk L0/L1, quảng bá khi bay quét)
    D->>N: CUE (tuần tra dải trực giao, ngược chiều)
    Note over N: bằng chứng = Confidence(mảnh đang giữ) × clueQuality
    N->>L: RPT (leo cây trong ô, kèm GPS của chính nó)
    Note over L: gộp ô (noisy-OR)
    L-->>L: SHARE (flood xuyên ô, mang aggregate + peak)
    Note over L: ô vượt ALERT → backoff theo bằng chứng
    L-->>L: RCLAIM (flood: tôi đã triệu tập, đứng xuống)
    L->>F: SUMMON (một hop, mang vị trí nút mạnh nhất)
    F->>D: A2A (chuyển tiếp SUMMON — DATA không nghe SUMMON trực tiếp)
    D-->>D: CLAIM (loại trừ tương hỗ trên radio; kẻ thua ở lại chờ)
    D->>N: FULL × 382 chunk (dwell ≥ 20 s)
    alt nút đủ dữ liệu và VẪN khớp
        N->>D: CONFIRM
    else nút đủ dữ liệu và KHÔNG khớp
        N->>D: REJECT
    end
    D->>F: HANDOFF (kèm fix — FAST 25 m/s nhanh hơn DATA 15 m/s)
    F->>B: REPORT (kèm fix, cờ kFlagHasFix)
    Note over B: đủ numUav báo cáo → chốt nhiệm vụ
```

Bốn điểm dễ hiểu sai:

1. **SUMMON là quảng bá MỘT HOP.** Đó là lý do có `RCLAIM`: lãnh đạo ô cách nhau
   63–156 m còn radio mặt đất với ~37 m, nên nửa "đứng xuống" của cuộc bầu cử
   **không thể tới nơi về mặt vật lý** nếu không flood.
2. **DATA không nghe SUMMON**, chỉ nghe `A2A` từ FAST. Đây cũng là lý do UAV DATA
   phải **tuần tra** thay vì đỗ giữa map: đỗ một chỗ thì gần như luôn ngoài tầm.
3. **CONFIRM/REJECT là cặp.** Nút đủ dữ liệu mà không khớp thì gửi REJECT — đó là
   cách một UAV rời vùng sai **bằng bằng chứng**, không phải bằng timeout.
4. **Fix đi về BS bằng byte thật** (`kFlagHasFix` + `x,y` dm trong REPORT), không
   phải đọc từ trạng thái simulator. Baseline phủ mù xoá cờ → BS không có vị trí.

---

## 4. Máy trạng thái từng tác nhân

| tác nhân | trạng thái |
|---|---|
| **FAST** | `IDLE → CLIMB → CRUISE → (RELAY_HOLD) → RETURN_BS → DONE` |
| **DATA** | `IDLE → CLIMB → (GOTO_CENTER→LOITER \| PATROL) → DIVERT → DELIVER → RETURN → DONE`; baseline dùng `SWEEP → DELIVER` lặp |
| **nút mặt đất** | không có enum — điều khiển bằng cờ: `m_isCellLeader`, `m_isLeader` (thắng bầu cử), `m_confirmed`, `m_confirmHeard`, `m_rejectHeard`, `m_regionFormed` |
| **BS** | chỉ đếm `m_reporters`; đủ `m_expected` → `MarkReportAtBS` + `Simulator::Stop` |

Cơ chế bầu cử ở nút mặt đất: ô vượt `kAlertThreshold` → lên lịch SUMMON sau
**backoff tỉ lệ nghịch với bằng chứng** → nghe RCLAIM của ô khác **trong bán kính
`electScope`** thì huỷ. `aimScope` chặn lãnh đạo nhắm quá 160 m khỏi tâm ô của
mình. `MaybeRetarget` cho phép nhắm lại ứng viên tiếp theo khi không có CONFIRM.

---

## 5. Năm nhánh hiện có — khác nhau ở đúng chỗ nào

| `--scheme` | đội bay | mặt đất | ghi chú |
|---|---|---|---|
| `proposed` | FAST + DATA | **hợp tác đầy đủ** (cây ô, SHARE, bầu cử) | `SetCooperative(true)` |
| `closed-loop` | **y hệt** `proposed` | **chỉ ECHO một hop** tới UAV trên đầu | `SetEchoMode(true)` — tách "có phản hồi" khỏi "có hợp tác" |
| `nocoop` | toàn bộ là DATA, `SWEEP_DUMP` | không gì cả | phủ mù, dwell-dump cả tập ở mọi điểm |
| `tsp-mc` | DATA chạy tour VBS/TSP Zeng'18 | phục hồi **rateless** | baseline tài liệu, `mcRedundancy=1.2` |
| `pure-uav` | 1 UAV | không | **sắp bỏ** (D10) |

Sự khác biệt `proposed` vs `closed-loop` nằm gọn trong **hai dòng** của
`sar-config.cc` (`SetCooperative` / `SetEchoMode`) — đó là lý do so sánh này sạch,
và cũng là lý do kết quả của nó khó chối.

---

## 6. Đầu ra

`data/results/uav-sar/<scheme>/run-<seed>/` gồm `metrics.csv` (một dòng),
`events.csv`, `trajectories.csv`, `config.txt`. Dấu vết chống nhầm lẫn:
`binary=<mtime>,<size>` của `/proc/self/exe` và `clutter=M,min,max` — hai cái này
tồn tại vì đã **thật sự** xảy ra chuyện build lại giữa campaign.

---

## 7. Sắp đổi cái gì — delta sang `SIM-SPEC-vi.md`

Sắp xếp theo giai đoạn G1→G3 của đặc tả §11.

| D | file chạm vào | nội dung | kéo theo |
|---|---|---|---|
| **D4** | `sar-bs-app.cc`, `sar-metrics.{h,cc}` | đánh dấu **UAV đầu tiên** báo cáo → cột `timeToFirstReport_s`; giữ nguyên cột cũ | script phân tích đổi cột chính |
| **D10** | `sar-config.cc`, `scenario-sar.cc`, `tools/` | bỏ `pure-uav` | — |
| **D3** | `clue-field.cc` (một dòng nhiễu) + công cụ hiệu chuẩn mới | `q̂ = clip(q + σ(q+q₀)ε)` thay nhiễu cộng | **mọi kết quả có `senseSigma>0` thành vô hiệu**; phải hiệu chuẩn lại σ |
| **D8** | `sar-types.h`, `sar-ground-app.cc`, cả hai app UAV | CONFIRM 5 B → 10 B, thêm `evQ8` + vị trí nút xác nhận | fix báo về = vị trí nút xác nhận mạnh nhất, không còn là điểm nhắm |
| **D9** | `sar-data-uav-app.cc` | hiện nghe CONFIRM vẫn **rải hết dwell** rồi mới về; đổi thành dừng ngay khi `evQ8 ≥` ngưỡng | đây là thứ **mở khoá lợi ích của chiều B** |
| **D1** | `sar-data-uav-app.cc` (`PatrolCueTick`) | tuần tra rải **full data**, cue ưu tiên cao hơn | gói tin có thể × nhiều lần — có cổng đo, không tự động thành mặc định |
| **D27/D11** | **file mới** + `sar-ground-app.{h,cc}` + `sar-types.h` | mặt phẳng **payload**: HAVE bitmap 48 B, tiếp sức chunk thiếu, dập trùng | nút lần đầu **phát lại dữ liệu** — hiện `m_dev->Send` của nút chỉ toàn gói điều khiển |
| **D11-B2** | như trên | cùng giao thức, TTL=1 qua biên ô | |
| — | `sar-config.h/.cc`, `scenario-sar.cc` | cờ mới `--relay=0\|1\|2` | 3 scheme × 3 mức relay = 9 nhánh |
| **D30** | cả 4 app + `sar-metrics` + `sar-params` | **quét hết ứng viên** — 15 chỗ ở §8, gồm cả `closed-loop` | mất một phần lợi thế chi phí đang có (xem `SIM-SPEC-vi.md` §6.1) |
| **D18/D19** | `tools/campaign_stats.py` | Kaplan–Meier + log-rank phân tầng, giữ mọi hạt giống | Wilcoxon/McNemar giữ cho chi phí |

### Thay đổi kiến trúc lớn nhất

Hôm nay **không nút mặt đất nào từng phát lại một chunk dữ liệu** — kiểm chứng
được: mọi `m_dev->Send` trong `sar-ground-app.cc` đều là ECHO / RPT / SHARE /
RCLAIM / CONFIRM / REJECT, tức **chỉ bằng chứng**. Mặt phẳng hợp tác hiện tại chia
sẻ *ai thấy gì*, chưa bao giờ chia sẻ *chính dữ liệu*.

D2/D11/D27 thêm đường thứ hai: nút giữ `m_chunks` (đã có sẵn) sẽ quảng bá bitmap
"tôi có gì" và tiếp sức chunk hàng xóm thiếu. Đó là **thay đổi lớn nhất** trong kế
hoạch, và cũng là lập luận chi phí mạnh nhất mà bài báo có thể có: một lượt UAV
bay qua chỉ cần chạm tới vài nút, phần còn lại của ô nhận qua G2G.

### Cái KHÔNG đổi (trước khi có D30 — xem §8)

Tầng mạng/kênh, `cell-grid`, `inter-cell-routing`, `target-profile`, mô hình năng
lượng, `flight-controller`, và toàn bộ mặt phẳng bằng chứng (RPT/SHARE/RCLAIM/bầu
cử). Chiều A đã xong; mọi việc còn lại nằm ở chiều B và ở đo đạc.

---

## 8. KIỂM TOÁN: mọi chỗ làm việc tìm kiếm sập về MỘT điểm

> **Trạng thái 2026-08-08 (commit `321e3a3`):** cụm A và B **đã sửa cho nhánh
> `proposed`**; cụm C, D, E **chưa**. Xem §9 để biết đo được gì.

Rà toàn bộ mã, cả nhánh đề xuất lẫn baseline. **15 điểm**, chia năm cụm. Đây không
phải một lỗi mà là một **mẫu thiết kế xuyên suốt**: hệ thống được viết với giả
định ngầm "có đúng một chỗ đáng đến".

### A. Thăm dò TẮT ngay khi có ứng viên đầu tiên

| # | vị trí | vấn đề |
|---|---|---|
| A1 | `sar-fast-uav-app.cc:202` | `DisseminateTick` chặn bởi `!m_summonSeen`: **rải cue dừng hẳn** khi có SUMMON đầu tiên ở BẤT KỲ đâu. Phần còn lại của vùng không bao giờ nhận cue → **ứng viên thứ hai không thể hình thành**. Đây là gốc rễ. |
| A2 | `sar-fast-uav-app.cc:305` | nghe A2A của đồng đội → `m_summonSeen = true`: lan cái tắt đó ra **toàn đội FAST** |
| A3 | `sar-data-uav-app.cc:200` | luật *sky-quiet*: không nghe cue trong `kSkyQuietS = 45 s` → bay về. Vì A1 đã tắt cue, bầu trời im **theo cấu trúc** → 45 s sau **đội DATA cũng về** |

A1→A2→A3 là một **dây chuyền**: một SUMMON → cue tắt → 45 s → cả hai đội về nhà.
Đúng nghĩa đen "tìm 1 điểm rồi quay về".

### B. MỘT confirm đóng cả đội

| # | vị trí | vấn đề |
|---|---|---|
| B1 | `sar-fast-uav-app.cc:285` | CONFIRM ở trạng thái CRUISE → `RETURN_BS`, **không xét vùng, không xét khoảng cách** |
| B2 | `sar-data-uav-app.cc:502` | CONFIRM + chưa có nhiệm vụ → `RETURN`. **Mâu thuẫn trực tiếp** với `stayAvailable` cách đó ~50 dòng, vốn tồn tại để giữ UAV lại cho vùng khác |
| B3 | `sar-ground-app.cc:497` | handler CONFIRM **không đọc `regionId`** dù gói có mang. Đặt `m_confirmHeard` cho mọi confirm ở mọi nơi → khoá vĩnh viễn beacon (`:431`), bầu cử, `MaybeRetarget` (`:410`) và tái-triệu-tập theo cue (`:633`) |
| B4 | `sar-ground-app.cc:520` | đứng xuống khi nghe SUMMON **cũng không xét cùng-chỗ**, trong khi RCLAIM ở `:545` **có** kiểm tra `electScope`. Hai đường làm cùng một việc mà một đường có bảo vệ, một đường không |

B3 chính là **đúng cái lỗi** đã sửa cho RCLAIM bằng `electScope` và chưa bao giờ
sửa cho CONFIRM.

### C. Chỉ MỘT điểm mang về được

| # | vị trí | vấn đề |
|---|---|---|
| C1 | `sar-fast-uav-app.cc:339` | một ô `m_pendFix` duy nhất: nghe nhiều aim thì **giữ cái cuối** — chú thích trong mã đã tự thừa nhận |
| C2 | `sar-metrics.h` `MarkVictimFix` | `if (m_tFix < 0)` — chỉ ghi **fix đầu tiên**, các fix sau bị bỏ |
| C3 | `sar-types.h` REPORT/HANDOFF | định dạng chỉ có **một** cặp `(x,y)`; không có chỗ cho nhiều điểm |
| C4 | `sar-fast-uav-app.cc:245` | `rid = 1` cứng trong REPORT |

### D. Baseline — và ở đây lệch về HAI phía khác nhau

| # | nhánh | vấn đề |
|---|---|---|
| D1 | `closed-loop` | `RelayBestEcho` bị chặn bởi `m_summonSeen` + chỉ giữ argmax đang chạy → **đúng một aim mỗi lần chạy, theo cấu trúc**. Đây là nhánh phạm lỗi nặng nhất: nó *chỉ có thể* tìm một điểm rồi về |
| D2 | `closed-loop` | `RelayBestEcho:182` đặt `rid = 1` cứng → loại trừ CLAIM **theo vùng** sập thành loại trừ **toàn cục**, cả đội DATA chỉ phục vụ được một điểm |
| D3 | `nocoop`, `tsp-mc` | ngược lại: handler CONFIRM **không** liệt kê trạng thái `SWEEP`, nên chúng **không bao giờ dừng sớm** và phủ hết mọi chỗ |
| D4 | `tsp-mc` | tour VBS tính trước từ toàn bộ vị trí nút — không có khái niệm ứng viên. Đúng với Zeng'18, nhưng nghĩa là C4 đang so **"phục vụ một điểm"** với **"phục vụ tất cả"** |

Hệ quả công bằng, phải nói thẳng: **baseline mù hiện đang quét sạch mọi điểm trong
khi nhánh đề xuất dừng ở điểm đầu tiên.** So sánh vì thế đang thiên **có lợi** cho
đề xuất về chi phí và **bất lợi** về độ phủ. Sửa D30 làm `closed-loop` **mạnh lên**,
không yếu đi — và `closed-loop` đang là nhánh thắng `proposed`.

### E. Cơ chế đa ứng viên duy nhất đang có — và nó quá yếu

`MaybeRetarget` + `m_candidates` là thứ duy nhất trong hệ thống biết tới nhiều ứng
viên. Nó **tuần tự** (mỗi lúc một điểm), **chặn ở `kMaxRetargets = 2`** (tối đa 3
aim), **giãn `kRetargetAfterS = 60 s`**, và bị **bất kỳ CONFIRM nào ở bất kỳ đâu
giết** (B3). Nó là cơ chế *sửa sai một aim*, không phải cơ chế *quét một tập ứng
viên*.


---

## 9. D30 giai đoạn 1 — đã sửa gì, đo được gì

### 9.1 Đã sửa (nhánh `proposed`)

| chỗ | trước | sau |
|---|---|---|
| A1/A2 | rải cue tắt ở SUMMON đầu tiên | cue chạy tới khi UAV bay hết dải của mình |
| A3 | *sky-quiet* kéo theo | không còn bị kích hoạt giả, vì cue không tắt nữa |
| B1 | CONFIRM cắt ngang chuyến quét | FAST bay hết dải; về nhà khi **mọi vùng nó đã điều phối** đã đóng |
| B2 | UAV DATA đang tuần tra về nhà | chỉ về khi hết kế hoạch tuần tra |
| B3 | CONFIRM khoá mọi lãnh đạo, không đọc `regionId` | chỉ khoá lãnh đạo **cùng vùng**; nút thường đóng dấu vùng nó nghe triệu tập |
| B4 | đứng xuống theo SUMMON không xét chỗ | cùng phép kiểm `electScope` như RCLAIM |
| **B5 (mới, tìm được lúc đo)** | `m_regionFormed` **chốt cứng** khi RCLAIM tới lúc ô chưa có aim → yield vô điều kiện, vĩnh viễn | quyết định đứng xuống dời sang **lúc bầu cử**, so với tập aim đã bị chiếm |

B5 là chỗ nặng nhất và chỉ lộ ra khi nhìn `events.csv`: **10 ô trải khắp 300 m
yield cho c9 trong 30 ms** ở t=46.5 s, trước khi hầu hết chúng có bằng chứng gì.
`electScope` — thứ đã đo được b=7 c=0 — trên thực tế **không scope gì** trong
trường hợp thường gặp, vì cuộc đua kết thúc trước khi có ai kịp có aim.

### 9.2 Kiểm chứng

16×16, 4 UAV, seed 7, `clutterCount=4`, `clutterResolve=0`:

| | trước | sau |
|---|---:|---:|
| số vùng triệu tập | **1** | **4** |
| vị trí nhắm | 1 chỗ | đúng 4 vị trí vật gây nhầm |
| ô yield khi chưa có aim | 10 | 3 |

12 hạt giống bắt cặp, `gridSize=16`, mặc định (`clutterResolve=1`):

| chỉ số | trước | sau | sau tốt hơn |
|---|---:|---:|---:|
| yield mù | 10–11 | **2–6** | — |
| `timeToFixAtBS_s` (med) | 83.1 | **95.1** | 2/11 |
| all-home (med) | 110.9 | 114.1 | 4/11 |
| năng lượng (med) | 82.7 kJ | 83.2 kJ | 4/12 |
| gói tin (med) | 4 611 | **4 931** | 3/12 |
| `fixOnVictim` | 11/12 | 11/12 | — |

**Chi phí đã tăng đúng như dự báo ở `SIM-SPEC-vi.md` §6.1** (+14 % thời gian tới
fix, +7 % gói tin), và **lợi ích chưa thể hiện** — vì ở giá trị mặc định trục
nhập nhằng đang vô hiệu (D31). N=12 chỉ đủ để nói **hướng**, không đủ để tuyên bố;
quy tắc N ≥ 120 vẫn nguyên.

Phần thời gian tăng nhiều khả năng là **tranh chấp MAC**: cue không còn tắt nên nó
va vào chính các chunk FULL đang giao. Nếu sau này muốn giảm, cách sạch là **giảm
nhịp cue** khi đã có vùng đang được phục vụ, chứ không phải tắt hẳn.

### 9.3 Chưa làm

| còn lại | vì sao chưa |
|---|---|
| cụm C (4 chỗ) | REPORT chỉ mang một fix; cần quyết định có mang nhiều điểm về hay không |
| cụm D (4 chỗ) | `closed-loop` — user yêu cầu làm `proposed` trước |
| cụm E | `kMaxRetargets` — xem lại sau khi D31 xong |
| `candidatesFound/Resolved` | chỉ số mới, làm cùng lúc với cụm C |
| **cổng G1f** | **không kiểm được** cho tới khi D31 xong: ở mặc định, M=4 cho kết quả **giống hệt M=0** ở 11/12 hạt giống |

---

## 10. D31 — kết quả sau khi sửa trọng số hai tầng

`ClueNow()` giờ nội suy theo **tỉ lệ byte đã nhận** (`PossessedFraction`) thay vì
`PossessedConfidence`. 16×16, 4 UAV, 12 hạt giống, cùng một binary trừ thay đổi này:

| | M=0 trước | M=0 sau | M=4 trước | M=4 sau |
|---|---:|---:|---:|---:|
| summon / run | 1 | 1 | 1 | **1–4 (trung vị 3)** |
| fix tới BS | 11/12 | 11/12 | 11/12 | **4/12** |
| năng lượng (med) | 83.2 kJ | 83.2 kJ | 83.2 kJ | **278.8 kJ** |
| gói tin (med) | 4 931 | 4 931 | 4 931 | **42 006** |
| fix sai người | 0 | 0 | 0 | **0** |

**M=0 không đổi một cột nào** — đúng như phải thế: không có vật gây nhầm thì
`clueQualityFull == clueQuality`, trọng số trộn không thể có tác dụng. Chế độ so
sánh chính (D14) **không bị động tới**.

**M=4 đổi hoàn toàn.** Mơ hồ thôi không còn miễn phí; nó thành một chế độ mà đội
bay hiện tại **không dọn nổi trong chân trời 400 s**: 4 UAV trải trên 3 vùng ứng
viên, mỗi vùng 34 kB phải giao. 278.8 kJ ≈ đúng bằng bốn UAV bay hết 400 s, tức
là chúng **không bao giờ xong**.

Điều **không** đổi: `fixOnVictim` sai = **0** ở mọi run. Cơ chế phân giải vẫn
đúng — nó chỉ tốn hơn nhiều so với những gì đã báo cáo trước đây.

Hệ quả: con số 400 s là chân trời, nên 8/12 run là **kiểm duyệt**, không phải thất
bại. Đây chính là O1 ($T_{\max}$ lấy từ đâu) trở thành câu hỏi cấp bách, và là lý
do D14 (M=0 cho mọi so sánh) đúng.

### Replay: `docs/visualize/replay-multicandidate.html`

Ba khung cùng seed 4, cùng nạn nhân, cùng 4 vật gây nhầm:

| khung | hành vi |
|---|---|
| 1 — trước | **1 summon**, cả đội về nhà sau confirm đầu tiên |
| 2 — D30 | quét hết, nhưng mơ hồ vẫn vô hiệu nên vẫn 1 summon |
| 3 — D30+D31 | **3 summon**; 32 REJECT loại các vật gây nhầm, 9 CONFIRM ở nạn nhân thật; fix về BS lúc 90.9 s, **sai số 0.0 m** |

---

## 11. 40×40, 2 nạn nhân thật + 4 vật gây nhầm — kết quả và chẩn đoán

Cấu hình: `--gridSize=40 --gridSpacing=20` (780×780 m, 1600 nút),
`--victimCount=2 --clutterCount=4`, chân trời 600 s, seed 1. Hai mức đội bay.

| | 4 UAV | 8 UAV |
|---|---:|---:|
| vùng triệu tập | 5 | 4 |
| CONFIRM | **0** | **0** |
| REJECT | 68 | 81 |
| divert | 2 | 4 |
| `victimsLocated` | **0 / 2** | **0 / 2** |
| `wrongFixes` | 0 | 0 |
| năng lượng | 456 kJ | **869 kJ** |
| gói tin | 80 252 | 131 915 |

### Chẩn đoán: ĐỊNH VỊ ĐÃ XONG, LẬP LỊCH MỚI LÀ NÚT THẮT

Nạn nhân thật ở **(100, 720)** và **(380, 460)**. Các điểm triệu tập:

| t (s) | điểm nhắm | cách nạn nhân gần nhất | kết luận |
|---:|---|---:|---|
| 48.9–56.6 | (100.0, 720.0) | **0.0 m** | **nạn nhân** |
| 71.1–71.7 | (380.0, 460.0) | **0.0 m** | **nạn nhân** |
| 58.5 / 48.9 | (260–280, 280) | 206–216 m | vật gây nhầm |
| 92.8 | (560, 320) | 228 m | vật gây nhầm |
| 70–159 | (640, 540) | 272 m | vật gây nhầm |

**Mặt phẳng hợp tác tìm ra CẢ HAI nạn nhân, sai số 0.0 m, trong vòng 72 giây.**
Cái hỏng không phải định vị mà là **giao hàng**: 0 CONFIRM, 68–81 REJECT — nghĩa
là các UAV đã giao xong dữ liệu ở **vật gây nhầm** (nên nút ở đó loại được chúng)
và **chưa bao giờ hoàn tất giao hàng ở một nạn nhân thật** trong 600 s.

**Gấp đôi đội bay không sửa được.** 8 UAV cho 4 divert thay vì 2, vẫn 0 CONFIRM,
và **đốt gấp đôi năng lượng** (869 kJ). Nút thắt không phải số máy bay mà là
**thời gian giao hàng trên mỗi ứng viên** (382 chunk qua LR-WPAN) nhân với **thứ
tự phục vụ**: đội bay phục vụ ứng viên theo **thứ tự nghe thấy**, không theo thứ
tự tối thiểu hoá thời gian kỳ vọng tới nạn nhân. Ở 8 UAV, ứng viên đầu tiên
(t=48.9 s) là một vật gây nhầm và nó chiếm mất chiếc DATA rảnh đầu tiên.

**Đây chính là bài toán P10** (độ trễ nhỏ nhất có trọng số / traveling repairman)
có nội dung thật, đo được, chứ không phải phát biểu cho đẹp. Nó là lập luận mạnh
nhất cho §IV của bài báo mà ta có cho tới giờ.

### Ba hướng sửa, theo thứ tự giá trị

| | cơ chế | vì sao hợp |
|---|---|---|
| **D9** | UAV dừng giao hàng ngay khi nghe CONFIRM/REJECT đủ mạnh, thay vì rải hết dwell | cắt thẳng thời gian trên mỗi ứng viên |
| **D2/D11** | tiếp sức payload nội ô | một lượt bay chỉ cần chạm vài nút, phần còn lại của ô nhận qua G2G |
| **lập lịch** | phục vụ theo **ưu tiên bằng chứng**, không theo thứ tự đến | đúng phần heuristic mà P10 dẫn tới |

Thêm UAV **không** nằm trong danh sách này — đã đo, nó chỉ nhân đôi chi phí.

### Replay: `docs/visualize/replay-40x40-multitarget.html`

Hai khung 4 UAV / 8 UAV. `make_viewer.py` đã sửa để vẽ **mọi** nạn nhân thật
(nhãn V1, V2) — trước đó nó chỉ vẽ `victimX/victimY`, tức một chiếc, và một viewer
vẽ một nạn nhân trong khi đội bay phục vụ hai là **gây hiểu sai**.

---

## 12. D32 — chia việc giữa các UAV DATA qua A2A

### 12.1 Gốc rễ: MỘT dòng

```cpp
// SUMMONED: cycle until the leader's CONFIRM stops us
SendFullChunk(0, 0);        // ← lặp VÔ HẠN
```

UAV DATA giao xong một lượt toàn bộ dataset thì **quay lại giao từ đầu, không có
điểm dừng nào ngoài CONFIRM cho đúng vùng của nó**. Ở một vật gây nhầm CONFIRM
**không bao giờ tới**, nên chiếc UAV đứng đó phát cho tới hết chân trời. Đây là
toàn bộ lý do "đội DATA chỉ phục vụ một điểm", và cũng là nguồn của 456–869 kJ ở
40×40: đội bay **đứng yên phát sóng**, không phải bay.

### 12.2 Giao thức chia việc (chỉ dùng thứ nghe được trên radio)

| thành phần | luật |
|---|---|
| **bảng công việc** | A2A = *có việc ở đâu*; CLAIM của đồng đội = *ai nhận*; CONFIRM/REJECT = *việc nào đã ngã ngũ* |
| **chọn** | ứng viên **ít được phục vụ nhất**, rồi **gần nhất**, trong số chưa ai nhận |
| **thứ tự nói** | backoff trước CLAIM **tỉ lệ khoảng cách** → chiếc gần nhất lên tiếng trước |
| **chống trùng không gian** | một việc coi là đã nhận nếu đồng đội nhận **bất kỳ việc nào trong 150 m** |
| **phá hoà** | cùng mili-giây thì **id nhỏ hơn thắng**, chỉ khi còn đang bay tới |
| **giải phóng** | hết dwell → `CLAIM role=2` báo trả vùng, rồi nhận việc kế |

A2A trước đây bị coi là **mệnh lệnh**; giờ nó là **tin tuyển việc**. Không có
`role=2` thì bảng của đồng đội giữ vùng "đã nhận" vĩnh viễn — đo được `next_task`
= 0 ở **mọi** run.

### 12.3 Kết quả — 6 hạt giống BẮT CẶP, mỗi nhánh MỘT binary

> **Sửa lỗi phương pháp của chính tôi.** Bảng dưới đây chạy ở **8 UAV**, trong khi
> D13 chốt điểm vận hành là **4 UAV (2 FAST + 2 DATA)**. Tôi đổi điểm vận hành mà
> không nêu — đó là lỗi. Số liệu ở §12.6 là bản chạy **đúng đặc tả**; giữ bảng
> 8 UAV lại chỉ để đối chiếu, **không** dùng làm kết quả.
>
> Và chỉ số **"số điểm khác nhau được phục vụ" là SAI THƯỚC ĐO**: ba UAV chồng lên
> một chỗ với một UAV đi ba chỗ đều cho "3 điểm". Nó che đúng cái phải đo. Thước
> đo đúng ở §12.6.

24×24, 8 UAV, 2 nạn nhân thật + 4 vật gây nhầm, chân trời 500 s. Dấu `binary=`
xác nhận mỗi nhánh đúng một bản dựng, và hai bản khác nhau.

| chỉ số | trước | sau |
|---|---:|---:|
| **ứng viên được phục vụ** | 10/26 = **38 %** | 22/27 = **81 %** |
| chuyển việc (`next_task`) | 0 | **32** |
| **fix SAI NGƯỜI** | **5** | **0** |
| năng lượng (trung vị) | 496 kJ | **288 kJ** (4/6 tốt hơn) |
| gói tin (trung vị) | 42 598 | **25 940** (4/6 tốt hơn) |
| nạn nhân định vị được | 6/12 | 7/12 |
| `timeToFix` (trung vị) | 99.3 s (5/6 run có) | 102.1 s (**6/6** run có) |

Ba điều phải nói cho đúng:

1. **N = 6 chỉ đủ nói HƯỚNG.** Quy tắc N ≥ 120 vẫn nguyên; đây là kiểm chứng cơ
   chế, không phải kết quả để trích dẫn.
2. **Thời gian trung vị "tăng" là ảo giác sống sót.** Bản trước chỉ 5/6 run có
   fix, bản sau 6/6 — trung vị sau tính trên tập **khó hơn**. So trực tiếp hai
   trung vị ở đây là đúng cái bẫy `STATUS.md` §5 đã ghi.
3. **Hạt giống 3 xấu đi** (2/2 → 1/2 nạn nhân, năng lượng 208 → 311 kJ). Chia
   việc rộng hơn không miễn phí: phục vụ nhiều chỗ hơn có thể lấy mất thời gian
   của chỗ đúng.

### 12.4 Hai lỗi phụ tìm được trong lúc đo

- **Ràng buộc vùng không chặt:** `if (m_boundRegion != 0xFFFF && rid != m_boundRegion)`
  — UAV chưa gắn vùng nào thì nhận **mọi** lệnh nhắm lại. Một trong các đường
  khiến cả đội dồn về một vật gây nhầm.
- **Fix đã xác nhận bị ghi đè:** UAV xác nhận nạn nhân 2 rồi nhận việc thứ ba,
  mang toạ độ việc thứ ba về BS. Cả hai nạn nhân đã nhận đủ dữ liệu mà
  `victimsLocated` vẫn 1/2.

### 12.5 Replay: `docs/visualize/replay-task-division.html`

Hạt giống 5, trước/sau. Trước: 0/2 nạn nhân, 696 kJ, 103 405 gói — đội bay đứng
phát vô hạn. Sau: **2/2 nạn nhân**, 296 kJ, 26 544 gói.


### 12.6 ĐO ĐÚNG — 4 UAV theo D13, và thước đo chồng lấn thật

Thước đo: hai **lượt giao hàng** của hai UAV khác nhau, cách nhau ≤ 150 m và
**trùng nhau về thời gian**. Đây là thứ mắt nhìn thấy trong replay.

24×24, **4 UAV (2 FAST + 2 DATA)**, 2 nạn nhân thật + 4 vật gây nhầm, 500 s,
6 hạt giống bắt cặp, mỗi nhánh một binary (dấu `binary=` đã kiểm, hai bản khác nhau).

| chỉ số | trước | sau |
|---|---:|---:|
| **giây giao hàng TRÙNG** | **431 s** | **32 s** |
| cặp chồng lấn | 3 | 2 (4/6 hạt giống về **0**) |
| lượt giao hàng | 11 | **30** |
| điểm được phục vụ | 7 | **16** |
| điểm nằm trên nạn nhân | 5 | **10** |
| **`victimsLocated`** | **5/12** | **9/12** |
| chuyển việc (`next_task`) | 0 | **14** |
| fix sai người | 0 | 0 |
| năng lượng (trung vị) | 117 kJ | 150 kJ (sau tốt hơn **2/6**) |
| gói tin (trung vị) | 17 930 | 19 810 (sau tốt hơn 3/6) |
| `timeToFix` (trung vị) | 106.3 s (5/6 run có) | 106.3 s (**6/6** run có) |

**Chi phí tăng và tôi không giấu:** năng lượng trung vị +28 %, và chỉ 2/6 hạt
giống rẻ hơn. Lý do đúng như thiết kế: đội bay giờ **thật sự đi phục vụ nhiều
chỗ** thay vì đỗ một chỗ. Hạt giống 1 vừa rẻ hơn vừa tốt hơn (357 → 148 kJ,
0/2 → 1/2); hạt giống 6 đắt hơn hẳn (109 → 283 kJ) mà không thêm nạn nhân nào.

**N = 6 vẫn chỉ đủ nói hướng.** Quy tắc N ≥ 120 không đổi.

### 12.7 Chuỗi ba lần đo — chồng lấn giảm dần

| bản | cấu hình | giây trùng |
|---|---|---:|
| trước D32 | 8 UAV | 4 454 |
| D32 v1 | 8 UAV | 243 |
| D32 v1 | 4 UAV | 431 |
| **D32 v2** (mục ma + kiểm lúc tới nơi) | **4 UAV** | **32** |

Hai lỗ đã bịt ở v2: `m_tasks[crid]` tạo mục **(0,0)** khi nghe CLAIM của một vùng
chưa biết vị trí (phép kiểm cùng-chỗ so với gốc toạ độ, và mục ma còn được chọn
làm việc); và không có kiểm tra **lúc tới nơi** — đồng đội có thể chiếm chỗ trong
lúc mình bay tới, mất hàng chục giây.

---

## 13. D33 — đường bay fixed-wing thật, và giá của nó

### 13.1 Đường bay cũ KHÔNG bay được

Đo từ chính quỹ đạo đã bay (`trajectories.csv`), 6 hạt giống, 4 UAV:

| | |
|---|---|
| bán kính lượn cần ($v=25$ m/s, nghiêng 30°) | $R = v^2/(g\tan\varphi)$ = **110 m** |
| bán kính nhỏ nhất **đã bay** | **1–8 m** |
| mẫu đòi khúc gấp quá khả năng | **305/1500 = 20.3 %** |

Nguyên nhân là **hai** thứ, và sửa một cái thôi thì không đủ:

1. **Quy hoạch**: `BuildGmc` chọn tham lam waypoint "lời" nhất kế tiếp → đường bay
   bẻ ngược liên tục. Thay bằng **quét luống xen kẽ**: luống dọc cạnh dài, thứ tự
   `0, k, 2k, …` rồi `1, 1+k, …` với $k=\lceil 2R/\text{giãn luống}\rceil$, để mỗi
   lần quay đầu có đủ **một đường kính lượn**.
2. **Mô hình bay**: `FlightController::Turn()` đặt hướng **tức thì** — không có
   giới hạn nào. Thêm $\omega_{\max}=g\tan\varphi/v$ (≈13°/s), `Turn()` chỉ ra
   lệnh, `Step(dt)` xoay dần. **Chỉ áp cho FAST**; DATA là rotary-wing.

### 13.2 Sửa mô hình bay làm HỎNG nhiệm vụ, và vì sao

Bản chỉ có giới hạn lượn: **0 lượt giao, 0 nạn nhân, cả 6 hạt giống**, và cả 6 có
tổng góc đổi hướng **giống hệt 70°**. Hướng chỉ được ra lệnh **lúc tới waypoint**
— đúng khi `Turn()` là tức thì, sai hẳn khi có giới hạn: cung lượn ban đầu đẩy máy
bay lệch, rồi nó bay thẳng mãi mà không bao giờ nhắm lại.

Sửa: dẫn đường **mỗi control tick**, và chấp nhận waypoint khi **bay ngang qua** —
máy bay bán kính 110 m không phải lúc nào cũng lọt vào vòng chấp nhận 37 m, nó sẽ
bay vòng vô hạn.

### 13.3 Kết quả — 6 hạt giống, mỗi bản một binary

| bản | khúc gấp quá khả năng | ứng viên phục vụ | `victimsLocated` | E trung vị | tFix trung vị |
|---|---:|---:|---:|---:|---:|
| trước D32 | 20.3 % | 7/24 = 29 % | 5/12 | 117 kJ | 106.3 s (5/6) |
| D32 (chia việc) | 20.3 % | 16/20 = 80 % | **9/12** | 150 kJ | 106.3 s (6/6) |
| + quét luống | 10.8 % | 19/21 = **90 %** | 7/12 | 352 kJ | 107.0 s |
| **+ giới hạn lượn (D33)** | **0.2 %** | 17/20 = 85 % | 7/12 | **355 kJ** | 118.4 s |

### 13.4 Giá phải trả — nói thẳng

**Làm đội FAST đúng vật lý là ĐẮT.** Năng lượng trung vị 117 → 355 kJ (**3×**),
thời gian tới fix +11 %, và `victimsLocated` **không** tốt hơn bản chia-việc
(7/12 so với 9/12). Lý do: $R=110$ m so với luống 50 m, nên máy bay dành phần lớn
thời gian để quay đầu, và bước xen kẽ $k=5$ kéo dài mỗi chặng chuyển luống.

Hệ quả cho việc so sánh, giống hệt bài học đã ghi ở `STATUS.md` §2 khi đổi khung
máy bay: **mọi số đo trước D33 không so được với số sau D33.** So sánh hợp lệ chỉ
là giữa các lược đồ **dưới cùng một mô hình bay**.

Hai chỗ chưa sạch, ghi lại chứ không giấu: hạt giống 6 còn **1 mẫu** khúc gấp
(7 m) — nhiều khả năng ở chặng về BS hoặc lúc chuyển `RELAY_HOLD`, chưa áp dẫn
đường liên tục; và chồng lấn quay lại **3 cặp / 33 giây** (bản trước đó là 0), vì
FAST chậm hơn làm đổi toàn bộ mốc thời gian. Một `wrongFix` cũng xuất hiện.

---

## 14. D34 — RCLAIM làm tin tuyển việc, và 100 % ứng viên được phục vụ

### 14.1 Gốc rễ: ứng viên không tới được bầu trời

Không phải "không ai rảnh đi", mà là **không ai biết nó tồn tại**. SUMMON là
quảng bá **một hop**; một vùng chỉ tới được đội DATA nếu tình cờ có FAST trong
~50 m đúng lúc lãnh đạo phát. Sau D33 (luống cách nhau 250 m) chuyện đó thành
hiếm. Đo ở 24×24 seed 1: **3 vùng triệu tập, bảng công việc của DATA chỉ có 2**,
vùng thứ ba không ai phục vụ.

**Sửa:** dùng chính **flood RCLAIM** làm tin tuyển việc. Nó vốn được phát để các ô
khác đứng xuống, mang sẵn `cellId` + toạ độ nhắm, và **flood toàn vùng** — nên ở
đâu có UAV thì ở đó có một nút đang chuyển tiếp nó. DATA nghe RCLAIM thì thêm vào
bảng; FAST chuyển tiếp thành A2A cho DATA ngoài tầm mặt đất.

Đây là mặt phẳng hợp tác mặt đất làm đúng việc nó sinh ra để làm: **bù cho một
bầu trời không thể có mặt khắp nơi.** Trước đó nó chỉ dùng để dập bầu cử.

### 14.2 Kiểm chứng — 8 hạt giống, MỘT `module=`

24×24, 4 UAV (2 FAST + 2 DATA), 2 nạn nhân thật + 4 vật gây nhầm, 500 s.

| chỉ số | giá trị |
|---|---|
| **ứng viên được phục vụ** | **25/25 = 100 %** (0 bỏ sót ở mọi hạt giống) |
| chồng lấn giao hàng | 1 cặp / **5 giây** trên 8 run |
| khúc gấp quá khả năng fixed-wing | 5/2217 = **0.2 %** |
| `victimsLocated` | **8/16** |
| `wrongFixes` | **2** (đều ở hạt giống 7) |
| năng lượng trung vị | 355 kJ |
| `timeToFix` trung vị | 88.9 s (**8/8** run có fix) |

**Cái ĐẠT:** mọi điểm nghi vấn đều được một UAV mang dữ liệu đầy đủ tới. Đó là
yêu cầu, và nó đã đúng ở mọi hạt giống.

**Cái CHƯA đạt, phải nói rõ:** 12 nạn nhân (trên 16) có UAV giao hàng tới nơi,
nhưng chỉ **8** fix về được tới BS. Bốn cái mất ở chặng cuối. Nguyên nhân đã biết
và chưa sửa — **cụm C của D30**: REPORT chỉ mang **một** cặp toạ độ, và một UAV
chỉ giữ được một fix, nên với 2 UAV DATA thì trần cứng là 2 fix mỗi run dù có
phục vụ bao nhiêu chỗ. Hạt giống 7 còn tệ hơn: 2 `wrongFix` và 0/2 nạn nhân.

### 14.3 LỖI PHƯƠNG PHÁP tìm được khi kiểm: guard chống nhầm build bị MÙ

`binary=` chụp mtime+size của **file thực thi**, nhưng mọi app/model/helper nằm
trong **thư viện module** `libns3.46-uav-sar.so`, và ninja **không relink** file
thực thi khi chỉ thư viện đổi. Một bản build đổi hoàn toàn hành vi vẫn để lại dấu
`binary=` **giống hệt từng byte**.

Bắt được tại trận: hai batch cho kết quả khác hẳn (cùng seed 1: 2/3 so với 4/4
ứng viên được phục vụ) mà mang **cùng** `binary=1786355023,82512`. Tái hiện có
kiểm soát — sửa một file model, rebuild:

```
trước:  binary=1786355023,82512   module=1786411514,829304
sau:    binary=1786355023,82512   module=1786411527,829336
        ↑ KHÔNG đổi                ↑ đổi cả mtime lẫn size
```

Đã thêm `module=` (giải qua `dladdr` từ một symbol trong chính module) và cho
`assert_one_build` ưu tiên nó. Đây mới là cái guard mà `STATUS.md` open problem 5
định làm, ở đúng tầng.

---

## 15. D35 — chấm dứt phục vụ lặp

### 15.1 Đo được trước khi sửa

| | |
|---|---:|
| lượt giao / điểm | **2.40** (60 lượt cho 25 điểm) |
| lượt lặp | **35 = 58 % công sức** |

Tách nguyên nhân: **21 lượt** do UAV **khác** quay lại, **14 lượt** do **cùng** UAV.

### 15.2 Bốn lỗi, bốn nguyên nhân khác nhau

| # | lỗi | sửa |
|---|---|---|
| 1 | `served` chỉ là **thứ tự ưu tiên** — hết một vòng thì cả đội quay lại từ đầu | một chỗ đã có **trọn một dwell** là **đóng** cho toàn đội; `CLAIM role=2` báo cho đồng đội |
| 2 | mỗi lần lãnh đạo nhắm lại, UAV **khởi động lại 382 chunk** và reset dwell | đồng hồ dwell chỉ chạy ở **lần tới đầu tiên** của vùng |
| 3 | lần tiếp tục vẫn phát sự kiện `deliver_start` → phép đo **đếm nhầm** thành lượt phục vụ mới | tách `deliver_move` |
| 4 | nút đóng dấu CONFIRM/REJECT bằng "vùng gần nhất tôi nghe thấy", kể cả cách hàng trăm mét → **đóng oan** một ứng viên chưa ai phục vụ | chỉ nhận vùng khi nút **thật sự ở trong** (≤ 100 m) |

Lỗi 3 đáng nói riêng: **12 trong 13 lượt "lặp" còn lại sau khi sửa lỗi 1 là do nhãn
sai của phép đo, không phải hành vi.** Đây là lần thứ ba trong phiên thước đo nói
sai về hành vi (trước đó: "số điểm khác nhau", và "chồng lấn").

### 15.3 Kết quả — 8 hạt giống, một `module=`

| chỉ số | trước | sau |
|---|---:|---:|
| **lượt giao / điểm** | **2.40** | **1.08** |
| lượt lặp | 35 (58 %) | **2 (7 %)** |
| chồng lấn giao hàng | 1 cặp / 5 s | **0 / 0 s** |
| ứng viên được phục vụ | 25/25 = 100 % | 26/27 = **96 %** |
| khúc gấp quá khả năng fixed-wing | 0.2 % | 0.3 % |
| `victimsLocated` | 8/16 | 8/16 |
| `wrongFixes` | 2 | 2 |

### 15.4 CÒN LẠI — chưa sửa được, ghi lại đúng hiện trạng

**Một ứng viên trong một hạt giống (s3) vẫn không được phục vụ.** Chẩn đoán đọc
`known=3 closed=2 taken=1` trên **cả hai** UAV cùng lúc — mỗi chiếc tưởng chiếc kia
đang giữ ứng viên thứ ba. Tôi đã thử hai bản sửa (ràng buộc vùng cho nút; chỉ ghi
nhận CLAIM của đồng đội khi nó thật sự thắng) và **cả hai đều không đổi một con số
nào** trên toàn bộ 8 hạt giống, dù `module=` xác nhận binary có đổi. Nghĩa là
đường đi thật của lỗi này **chưa được xác định**, và hai bản sửa kia là đúng về
nguyên tắc nhưng không phải nguyên nhân. Không được coi là đã sửa.

**`victimsLocated` vẫn 8/16.** 12 nạn nhân có UAV giao hàng tới nơi, chỉ 8 fix về
tới BS — trần cứng của cụm C (REPORT mang một cặp toạ độ, một UAV giữ một fix).

**Hạt giống 7: 2 `wrongFix`, 0/2 nạn nhân.** Chưa truy.

---

## 16. D36 — độ phủ FAST, và một ĐÁNH ĐỔI không thể tránh

### 16.1 Độ phủ: gốc rễ không nằm ở hình dạng đường bay

| bản | độ phủ FAST | ứng viên phục vụ | tFix trung vị |
|---|---:|---:|---:|
| xen kẽ luống | 73.4 % | 96 % | 90.0 s |
| quay đầu ngoài vùng | **67.9 %** | 96 % | 98.6 s |
| + courier phải quét xong | **100.0 %** | **100 %** | **351.9 s** |
| + fix về ngay | **100.0 %** | 66 % | **112.0 s** |

Hai phát hiện, cả hai đều **không** phải chuyện hình học đường bay:

1. **Xen kẽ luống không làm được việc nó được viết ra để làm.** Dải rộng 230 m,
   đường kính lượn 220 m; thứ tự `[0,5,1,2,3,4]` giãn được hai lần quay đầu đầu
   tiên (250 m, 200 m) rồi để ba lần cuối ở **50 m**. Không thứ tự nào cứu được —
   phải quay đầu **ngoài vùng**, như máy bay khảo sát thật.
2. **Một trong hai chiếc FAST bỏ dở giữa chừng để làm courier.** Đo được: chiếc
   courier bay 2.1 km, hạ cánh lúc t=90 s; chiếc kia bay 5.7 km tới t=264 s. Với
   đúng 2 chiếc theo D13, mất một chiếc là mất nửa độ phủ cue. Sửa: chỉ chiếc
   **đã quét xong** mới được ứng cử → **độ phủ 100 % ở mọi hạt giống**.

### 16.2 Đánh đổi: cứu người sớm ĐỐI LẬP quét sạch

8 hạt giống bắt cặp, **một `module=`**, 24×24, 4 UAV, 2 nạn nhân + 4 vật gây nhầm:

| chỉ số | `--fixFirst=1` | `--fixFirst=0` |
|---|---:|---:|
| độ phủ FAST | 100 % | 100 % |
| **ứng viên được phục vụ** | 21/32 = **66 %** | 35/35 = **100 %** |
| **`victimsLocated`** | **14/16** | 8/16 |
| **`timeToFix`** (trung vị) | **112.0 s** | 351.9 s |
| năng lượng (trung vị) | **218 kJ** | 383 kJ |
| gói tin (trung vị) | **20 499** | 23 904 |
| lượt giao / điểm | **1.00** | 1.11 |
| chồng lấn | **0 s** | 22 s |
| khúc gấp quá khả năng | 0.2 % | 0.2 % |

Một UAV đang giữ **fix đã xác nhận** hoặc mang nó về ngay, hoặc đi phục vụ tiếp
và để fix ngồi trên một khung 15 m/s. Với 2 UAV DATA thì **hai mục tiêu loại trừ
nhau**, và biên độ không hề nhỏ: 3× thời gian, 1.75× năng lượng, đổi lấy 34 %
điểm nghi vấn.

Đây là **P10 (độ trễ nhỏ nhất có trọng số) hiện ra thành một cái núm đo được**,
không còn là một phát biểu suông trong §IV. Vì thế nó là **một nhánh khai báo**
chứ không phải một lựa chọn giấu trong bộ lập lịch — `--fixFirst`.

**Chưa giải quyết:** `wrongFixes = 2` ở cả hai nhánh (đều ở hạt giống 7), và
`victimsLocated` trần ở 14/16 ngay cả ở nhánh tốt nhất.

---

## 17. D37/D38 — trạng thái hiện tại: phủ hết, phục vụ hết, và chi phí quay đầu

### 17.1 Ba phát hiện, mỗi cái sửa một con số khác nhau

**D37 — REPORT mang 4 toạ độ, không phải 1.** Một khe fix mỗi UAV là **trần cứng
của cả nhiệm vụ**: 2 UAV DATA thì tối đa 2 toạ độ về được mỗi run dù tìm ra bao
nhiêu nạn nhân, nên **mọi** thay đổi giữ đội bay ở lại phục vụ thêm đều đổi thẳng
bằng số nạn nhân báo được. Đo: 12/16 nạn nhân có UAV tới nơi mà chỉ 8 fix về BS.
Sửa xong: **8/16 → 13/16**, mọi chỉ số khác không đổi.

**Cổng chờ FAST báo quét xong.** DATA không được hạ cánh khi FAST còn đang quét.
Ứng viên được phục vụ 73 % → **94 %**. Giá: `tFix` = **đúng thời điểm quét xong**,
giống hệt ở mọi hạt giống — vì không thể báo sớm hơn lúc được phép rời đi.

**D38 — góc nghiêng 30° → 45°.** Chi phí quay đầu là **cung lượn**, không phải vị
trí waypoint: một lần đảo chiều tốn tối thiểu $\pi R$, ở 30° là 345 m so với 460 m
luống hữu ích, năm lần mỗi lượt quét. Dời waypoint từ 2R về 1.2R **gần như không
ăn thua** (53.1 % → 52.7 %). $R=v^2/(g\tan\varphi)$ nên **bank là đòn bẩy duy
nhất**; 45° cắt R còn 64 m và cung còn 200 m.

### 17.2 Kết quả — 8 hạt giống, một `module=`

| chỉ số | 30° | **45°** |
|---|---:|---:|
| độ phủ FAST | 98.1 % | **99.8 %** |
| tổng quãng đường FAST | 110.5 km | **88.5 km** |
| phần bay TRONG vùng | 33.4 % | **43.8 %** |
| phần quay đầu | 52.7 % | **38.8 %** |
| **ứng viên được phục vụ** | 31/33 = 94 % | **32/32 = 100 %** |
| `victimsLocated` | 11/16 | **13/16** |
| năng lượng (trung vị) | 376 kJ | 367 kJ |
| `timeToFix` (trung vị) | 303.2 s | **248.2 s** |
| khúc gấp quá khả năng | 0.4 % (theo tiêu chí 45°) | 0.4 % |

Từng hạt giống: **ứng viên bỏ sót = 0 ở cả 8**, `fixesAtBS` 2–5.

### 17.3 Còn lại

- **`wrongFixes = 2`, vẫn chỉ ở hạt giống 7** — cùng một hạt giống suốt nhiều
  vòng. Chưa truy.
- **`victimsLocated` 13/16**, không phải 16/16. Ba nạn nhân được giao dữ liệu
  nhưng không sinh CONFIRM đủ mạnh.
- **Chồng lấn giao hàng quay lại 2 cặp / 31 s** (trước đó 0). Đổi mốc thời gian
  làm lộ lại đường đua CLAIM.
- **Bay ngoài vùng vẫn 38.8 %.** Đây là chi phí *nội tại* của cánh cố định trên
  một vùng nhỏ: 460 m luống với bán kính lượn 64 m thì mỗi lần đảo chiều vẫn tốn
  200 m. Muốn giảm nữa phải đổi hình học bài toán (vùng dài hơn, hoặc nhiều UAV
  với dải hẹp hơn), không phải đổi thuật toán.

---

## 18. UAV bay lạc — bốn lần sửa, chỉ lần thứ tư đúng

### 18.1 Hiện tượng

Hạt giống 8: một UAV DATA giao hàng xong lúc t=47 s, rồi bay **thẳng nam với tốc
độ không đổi** tới cuối lượt chạy — **6 177 m** ngoài bản đồ, ngoài tầm radio, và
không phục vụ gì nữa. Nó cũng là một phần lý do ứng viên bị bỏ sót.

### 18.2 Ba lần sửa ĐÚNG nhưng KHÔNG phải nguyên nhân

Cả ba lần đều cho kết quả **giống hệt từng cột trên cả 8 hạt giống**, trong khi
dấu `module=` xác nhận bản dựng có đổi. Ba lỗi đều thật và đều được giữ lại:

| # | lỗi | vì sao không phải nguyên nhân |
|---|---|---|
| 1 | `m_targets[m_ti]` đọc **quá cuối mảng** khi vào `PATROL` lúc kế hoạch đã hết | có xảy ra, nhưng chiếc UAV này có `m_ti < size` |
| 2 | `LOITER` dựa vào **người gọi** đã `Hover()` | nó không ở `LOITER` |
| 3 | hai UAV **khoá chết** quyền sở hữu của nhau | không liên quan đường bay |

### 18.3 Dừng đoán, đặt máy đo

Đến lần thứ ba thì rõ là đoán không còn là phương pháp. Thêm một sự kiện `lost`
ghi **trạng thái** của UAV ngay khi nó rời khỏi thế giới:

```
t=288.2  DATA4  lost  state=PATROL spd=15.0 hdg=-90   at (74, -3012)
```

`state=PATROL` — nó vẫn "đang tuần tra" ở 3 km về phía nam.

### 18.4 Nguyên nhân thật

Nhánh `PATROL` ra lệnh hướng **chỉ khi tới waypoint**. Chiếc nào vào `PATROL` từ
trạng thái khác — `ReleaseAndContinue`, hai nhánh nhường việc — giữ nguyên hướng
đang có và bay theo hướng đó mãi. **Đúng cùng một lỗi đã sửa cho đội FAST**, ở
một chỗ thứ hai không ai nhìn tới. Sửa: dẫn đường liên tục mỗi chu kỳ.

### 18.5 Kết quả — 8 hạt giống, một `module=`

| chỉ số | trước | sau |
|---|---:|---:|
| **UAV bay lạc** | 1/8 hạt giống | **0/8** (xa nhất 430 m = vị trí BS, đúng thiết kế) |
| **độ phủ DATA** | 45.7 % | **99.7 %** |
| độ phủ ANY | 99.9 % | **100.0 %** |
| **năng lượng** | 367 kJ | **228 kJ** |
| ứng viên được phục vụ | 97 % | 94 % |
| **`wrongFixes`** | **2** | **7** |
| victims | 11/16 | 11/16 |

**Độ phủ DATA nhảy từ 45.7 % lên 99.7 %** — đội DATA trước đây không hề bay hết
dải của mình, nó trôi đi; và năng lượng giảm 38 % vì không còn ai bay ra vô tận.

**`wrongFixes` tăng 2 → 7, và đây là hồi quy thật.** Từng hạt giống:
`[0,0,0,0,0,0,2,0]` → `[0,0,0,0,3,1,3,0]` — hai hạt giống mới xuất hiện lỗi. Cơ
chế hợp lý: DATA phủ đủ nghĩa là **nhiều cue hơn tới mọi nơi**, nên vật gây nhầm
cũng tích được bằng chứng và sinh thêm vùng ứng viên. Chưa truy, **không được coi
là đã xong**.
