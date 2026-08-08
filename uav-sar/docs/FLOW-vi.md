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

### Cái KHÔNG đổi

Tầng mạng/kênh, `cell-grid`, `inter-cell-routing`, `target-profile`, mô hình năng
lượng, `flight-controller`, và toàn bộ mặt phẳng bằng chứng (RPT/SHARE/RCLAIM/bầu
cử). Chiều A đã xong; mọi việc còn lại nằm ở chiều B và ở đo đạc.
