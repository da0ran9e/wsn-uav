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
