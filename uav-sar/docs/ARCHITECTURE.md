# uav-sar — Thiết kế chi tiết trên ns-3 (implementation design)

> Đi kèm `DESIGN.md` (ý tưởng). Tài liệu này mô tả **cách hiện thực trên ns-3**:
> module dùng, cách dựng mạng/kênh, các lớp logic, packet, scheduling, kịch bản,
> metrics. Thuần ns-3 (không CC2420).

Cập nhật: 2026-06-30. Trạng thái: thiết kế, **chưa code**.

---

## 0. Triết lý: `main` chỉ để THAM KHẢO — tự viết bản mới, sạch, tôi hiểu rõ nhất

Nhánh `main` là **nguồn tham khảo**, không phải thứ để port nguyên xi. Nguyên tắc:
**học ý hay, sửa chỗ dở, rồi viết lại từ đầu các thành phần tôi tự làm chủ hoàn
toàn.** `uav-sar` là một bản mới, mạch lạc, mỗi quyết định thiết kế đều có lý do.

Phân tích tham khảo (giữ gì / sửa gì):

| Ý tưởng thấy ở `main` | GIỮ (điểm tốt) | SỬA / CẢI TIẾN khi viết lại |
|---|---|---|
| Fragment phân tầng L0..L3 + utility + union-confidence | rất khớp câu chuyện (cue nhỏ→full) | tham số hoá `layerSplit`, tài liệu hoá công thức `1-∏(1-p_i)`, gắn rõ ngưỡng alert/confirm |
| Manh mối theo khoảng cách (strong/weak radius, false-positive) | mô hình "khoanh vùng" thực tế | nối trực tiếp với confidence ngữ nghĩa + ngưỡng, không để rời rạc |
| Kênh A2G n=2.2 / G2G n=3.5 + Nakagami + shadowing | kênh sát thực tế | chọn tham số có dẫn nguồn, kiểm định PDR-vs-(distance,altitude) trước khi tin |
| cell-layer: chia cell + CL + cây trong-cell + color | đúng khung PECEE | **sửa 3 chỗ dở**: (1) bầu CL = node **gần tâm cell nhất** (main dùng "id nhỏ nhất" — tuỳ tiện); (2) dùng **HEX nhất quán** (main để helper hex mồ côi, thực chạy lưới vuông); (3) **tô màu theo kề đúng** (main dùng `cellId%6` — không đảm bảo cell kề khác màu) |
| cooperation intra/inter theo xác suất | control-plane nhẹ, hợp lý | nối với **inter-cell routing thật** (main chưa có) thay vì prob rời |
| chiến lược phát UAV + điều khiển bay | ý tốt (cyclic/utility; heading/speed/climb) | gộp gọn, **sửa overshoot waypoint** (bài học round-1: `arriveR ≥ v·tick·1.5`) |

**Thiếu hẳn trên `main` → tôi tự thiết kế mới:**
(1) **CGW + inter-cell routing**; (2) hợp tác **liên-cell** + bầu **region-leader**
+ **1 summon** thống nhất; (3) orchestration **FAST/DATA** (sweep, listen, relay,
claim, divert, deliver); (4) **report-to-BS** khép vòng; (5) metrics vòng đầy đủ.

> Hệ quả: bảng "bố cục file" (mục 11) ghi *ref: main/…* nghĩa là **tham khảo ý
> tưởng rồi viết lại sạch**, KHÔNG copy nguyên file.

---

## 1. Module ns-3 sử dụng

| Module | Dùng để |
|---|---|
| `core` | `Simulator`, `Simulator::Schedule`, `EventId`, `CommandLine`, RNG (`SeedManager`, `UniformRandomVariable`), `Time` |
| `network` | `Node`, `NodeContainer`, `NetDevice`, `Packet`, `Address`, `Mac16Address` |
| `mobility` | `MobilityHelper`, `ConstantPositionMobilityModel` (BS/sensor), `ConstantVelocityMobilityModel` (UAV) |
| `spectrum` | `SingleModelSpectrumChannel` (kênh chung) |
| `propagation` | `A2GLogDistanceLossModel` (reuse) + `NakagamiPropagationLossModel` (fading) + `RandomPropagationLossModel` (shadowing log-normal) + `ConstantSpeedPropagationDelayModel` |
| `lr-wpan` | `LrWpanHelper`, `LrWpanNetDevice`, `LrWpanSpectrumValueHelper` (radio 802.15.4) |
| `energy` | (tùy chọn) battery + device energy cho UAV/sensor |

Không dùng: `wsn` (CC2420), `internet`/IP stack (ta chạy L2 802.15.4 + app tự
định tuyến overlay PECEE).

---

## 2. Dựng mạng & kênh (network layer)

### 2.1 Node & vị trí (thứ tự tạo cố định → ID ổn định)
```
BS      = ID 0                (ConstantPosition, ở rìa vùng, vd (-200,-200,0))
UAVs    = ID 1..M             (ConstantVelocity + UavFlightController)
Sensors = ID (M+1)..(M+N)     (ConstantPosition; grid N×N hoặc random-in-area)
```
`SarNetwork::Build()` tạo theo đúng thứ tự này (giữ convention như wsn-uav).

### 2.2 Radio: MỘT LrWpanHelper, MỘT kênh chung (bắt buộc)
```cpp
auto channel = CreateObject<SingleModelSpectrumChannel>();
auto a2g = CreateObject<A2GLogDistanceLossModel>();      // reuse
a2g->SetA2GExponent(2.2); a2g->SetG2GExponent(3.5);
a2g->SetAltitudeThreshold(zThresh); a2g->SetReferenceLoss(46.6);
channel->AddPropagationLossModel(a2g);
channel->AddPropagationLossModel(CreateObject<NakagamiPropagationLossModel>()); // fading
channel->AddPropagationLossModel(shadowing);             // log-normal
channel->SetPropagationDelayModel(CreateObject<ConstantSpeedPropagationDelayModel>());

LrWpanHelper lr;  lr.SetChannel(channel);
sensorDevs = lr.Install(sensors);
bsDev      = lr.Install(bs);
uavDevs    = lr.Install(uavs);       // cùng helper, cùng channel
// TX PSD + RX sensitivity mỗi PHY qua LrWpanSpectrumValueHelper
```
**Lưu ý sống còn:** giữ `LrWpanHelper` sống hết mô phỏng (lưu `unique_ptr` trên
orchestrator) — huỷ sớm sẽ `Dispose()` kênh và **mọi RX chết**.

### 2.3 RX callback
Mỗi device: `dev->SetReceiveCallback([app](dev,pkt,proto,from){ return app->OnReceive(...); })`.
Set TRƯỚC `Simulator::Run()`, mỗi device set **một lần**.

---

## 3. PECEE substrate — Phase 0 (tính offline trong helper)

Chạy 1 lần lúc setup (mạng tĩnh), tạo bảng định tuyến overlay cho ground plane.

### 3.1 Trong-cell (dùng lại `cell-layer`)
`BuildCellLayerPlan(sensors, cfg)` → mỗi node có: `cellId`, `cellColor`,
`cellLeaderId` (id nhỏ nhất trong cell), `neighbors`, `parentId` (next-hop về CL),
`hopToLeader`. Tùy chọn đổi `CellCoord` sang **hex** bằng `hex-cells-reference`.

### 3.2 MỚI: CGW + định tuyến liên-cell (`inter-cell-routing.{h,cc}`)
Mục tiêu: cho phép **CL của các cell khác nhau trao đổi** (hợp tác liên-cell).

**a) Cell adjacency graph.** Cell A, B kề nhau nếu ∃ node a∈A, b∈B với
`dist(a,b) ≤ neighborRange`. Lưu `std::map<int32,std::set<int32>> cellAdj`.

**b) Chọn CGW theo hướng.** Với mỗi cặp kề (A,B):
```
CGW_A→B = node a∈A có neighbor b∈B, cực tiểu theo khoá:
          (hopToLeader(a), dist(a,b), id(a))
```
(node biên gần leader nhất, cầu ngắn nhất, tie-break id). Lưu
`gateway[A][B] = {localGw:a, remoteGw:b}`. Đối xứng cho B→A.

**c) Route liên-cell.** BFS/Dijkstra trên `cellAdj` (trọng số = hop hoặc
1/successProb) → `CellRoute(cellA,cellB)` = chuỗi cell. Ghép lại thành đường
ground đầy đủ giữa 2 CL:
```
CL_A →(cây trong-cell, parent hops)→ CGW_A→X →(1 hop liên-cell)→ CGW_X→A
      →(cây trong-cell X)→ CL_X → … → CL_B
```
API cung cấp: `GroundRoute(srcNode,dstNode) -> vector<nodeId>` và
`RegionRoute(cellSet) -> spanning structure` cho hợp tác vùng.

**d) Chi phí truyền** dùng `cooperation-phy-mac`: mỗi hop intra dùng
`INTRA_CELL` (p=0.92), mỗi hop liên-cell dùng `INTER_CELL` (p=0.82) → mô phỏng
mất gói/độ tin cậy khi chia sẻ, không cần mô phỏng từng packet MAC cho control.

> Ghi chú: control-plane (report clue, share, election) mô phỏng ở **event-level**
> qua `cooperation-phy-mac` (nhanh, đúng độ tin cậy). Data-plane (UAV giao
> fragment, report về BS) mô phỏng **packet-level** thật qua lr-wpan.

---

## 4. Fragment ngữ nghĩa & manh mối

### 4.1 Fragment (dùng lại `semantic-fragment`)
`TargetProfile::Generate(total, layerSplit={L0,L1,L2,L3})`:
- **L0 IDENTITY_CUE** (nhiều, nhỏ, utility cao: COLOR/SILHOUETTE/BODY_RATIO…) → **đội FAST** rải.
- **L1 SEMANTIC_DESCRIPTOR** → FAST (tùy chọn).
- **L2 LOCAL_DETAIL + L3 FULL_REFERENCE** (lớn) → **đội DATA** giao khi được gọi.
- `Confidence(received)` = union-probability `1-∏(1-p_i)` → độ tin cậy tích luỹ.

### 4.2 Manh mối (dùng lại `local-clue`)
`BuildLocalCluePlan(sensors, {targetNodeId, strongRadius=40, weakRadius=120,…})`
→ mỗi node có `clueQuality` (khớp footage cục bộ), `semanticOverlap`,
`falsePositiveRisk`, `matchedSemanticTypes`.

**Trigger phát hiện tại node** khi nhận cue L0 từ FAST:
```
effConf = Confidence(received L0/L1 cues) * clueQuality(node)   // khớp cue × footage
node "có manh mối" nếu effConf ≥ alertThreshold
```
→ Nạn nhân ở gần ⇒ **nhiều node quanh đó** vượt ngưỡng (có thể **thuộc nhiều cell**)
⇒ cần hợp tác liên-cell (mục 5).

---

## 5. Hợp tác & cơ chế thống nhất (control-plane) — phần cốt lõi MỚI

```
(1) Node phát hiện → REPORT clue lên CL của cell (đi theo parentId, intra-cell).
(2) CL gộp: aggConf_cell = combine(clue của các node trong cell).
(3) Nếu vùng manh mối trải nhiều cell:
    CL các cell-có-manh-mối trao đổi qua inter-cell route (CGW):
      - REGION_SHARE(cellId, aggConf, centroid) lan giữa các CL kề nhau có manh mối.
      - Bầu REGION LEADER = CL có aggConf lớn nhất (tie → cellId nhỏ nhất).
(4) CHỈ region leader phát 1 SUMMON (beacon lên trời) — kèm centroid vùng +
    aggConf. → chống loạn gọi + gộp nhiều camera/nhiều cell thành 1 lời gọi.
```
Trao đổi ở (1)(3) tính độ tin cậy/chi phí bằng `cooperation-phy-mac`
(INTRA_CELL / INTER_CELL). Có timeout: nếu không gộp kịp `regionWindow` thì CL
mạnh nhất cục bộ tự summon (send-anyway, như deadline round-1).

---

## 6. Ứng dụng UAV (data-plane, packet-level thật)

### 6.1 FAST UAV (`SarFastUavApp`)
- Bay GMC sweep (dùng `uav-flight-controller` + GMC như round-1) tốc độ cao.
- **Phát L0/L1** liên tục qua `uav-dissemination-model` (CYCLIC/UTILITY_WEIGHTED),
  stagger 0.2s, broadcast Mac16 `ff:ff`.
- **Nghe SUMMON** (A2G) từ region leader. Khi nghe → **relay A2A** (broadcast
  A2A_RELAY) để đội DATA (đang ở xa/độ cao khác) nhận.
- FAST **không** giao data lớn.

### 6.2 DATA UAV (`SarDataUavApp`)
- Mang L2/L3, bay chậm chắc, **không nghe trực tiếp** — chỉ hành động khi FAST relay.
- **Claim token dùng chung** (shared_ptr<int32>) → đúng 1 DATA UAV nhận.
- Nhận relay → **DIVERT** tới centroid vùng → tới nơi → **DELIVER full (L2/L3)**
  cho region leader/CL (packet-level, chunk ≤100B, stagger nhỏ ~20ms).
- Node đạt `Confidence ≥ confirmThreshold` (FULL) → **XÁC NHẬN**.
- DATA UAV **bay về BS → gửi 1 gói REPORT nhỏ** → kết thúc (metric chính chốt ở đây).

### 6.3 BS app (`SarBsApp`)
- Sinh `TargetProfile`, chia layer cho FAST/DATA (giao qua config, "pre-brief").
- Nhận REPORT nhỏ ở cuối → dừng sớm (`Simulator::Stop`).

---

## 7. Packet formats (nhị phân gọn, ≤100B payload; PSDU 127B)

Byte[0]=MsgType, byte[1]=dst (0xFF broadcast). Little-endian; toạ độ dm (i16).

| MsgType | Layout | Hướng |
|---|---|---|
| `CUE_L0` | `[t][0xFF][fragId:u16][layer:u8][semType:u8][utilQ8:u8]` | FAST→ground (bcast) |
| `CLUE_REPORT` | `[t][dstCL][nodeId:u8][cellId:i16][confQ8:u8]` | node→CL (intra, event-lvl) |
| `REGION_SHARE` | `[t][dstCL][cellId:i16][aggQ8:u8][cx:i16][cy:i16]` | CL↔CL (inter, event-lvl) |
| `SUMMON` | `[t][0xFF][regionId:u16][cx:i16][cy:i16][aggQ8:u8]` | CL→sky (bcast) |
| `A2A_RELAY` | `[t][0xFF] + SUMMON body` | FAST→DATA (bcast) |
| `FULL_FRAG` | `[t][0xFF][fragId:u16][seq:u16][total:u16][layer:u8][payload…]` | DATA→ground (bcast) |
| `CONFIRM` | `[t][dst][regionId:u16][nodeId:u8]` | ground→DATA |
| `REPORT_BS`| `[t][dstBS][regionId:u16][resultQ8:u8]` | UAV→BS (kết thúc) |

Fragment lớn (L2/L3) chunk theo `total`; node ghép đủ `total` seq ⇒ frag complete;
đủ tất cả frag ⇒ `Confidence`→FULL ⇒ confirm.

---

## 8. Scheduling / timeline (dùng `Simulator::Schedule`)

| Thời điểm | Sự kiện |
|---|---|
| t=0 | `SarConfig::Build` (mạng, substrate Phase 0, apps, callbacks) |
| t≈0.1 | BS sinh TargetProfile; pre-brief layer cho UAV |
| t=1+0.3·i | UAV i cất cánh (stagger) → CLIMBING |
| mỗi 0.1s | `ControlTick` (state machine bay: CLIMB/CRUISE/DIVERT/DELIVER/RETURN/LAND) |
| mỗi 0.2s | FAST `DisseminateTick` phát cue (khi CRUISING) |
| khi node nhận cue | tính effConf → nếu ≥alert: REPORT lên CL |
| khi CL nhận report | gộp; mở `regionWindow` (vd 1s) chờ REGION_SHARE |
| hết regionWindow | bầu region leader → SUMMON (lặp tần thấp tới khi confirm hoặc quota) |
| FAST nghe SUMMON | A2A_RELAY |
| DATA nghe relay | claim → DIVERT |
| DATA tới vùng | DELIVER full (chuỗi `SendFullChunk` mỗi ~20ms) |
| node confirm | DATA → RETURN về BS |
| DATA tới BS | gửi `REPORT_BS` → `Simulator::Stop(+1s)` (dừng sớm) |
| t=simTime | dừng (nếu chưa xong ⇒ metric = -1) |

Nguyên tắc: giữ `arriveR ≥ speed·tick·1.5` (tránh overshoot waypoint — bài học round-1).

---

## 9. Kịch bản & orchestrator (`helper/sar/sar-config.{h,cc}`)

`Build()`: SeedManager(seed) → SarNetwork.Build → Phase 0 substrate
(cell-layer + inter-cell) → LocalCluePlan (target theo seed, độc lập scheme) →
TargetProfile → gán layer FAST/DATA → cài apps + RX callbacks + shared claim token.
`Schedule()`: stagger nhỏ. `Run()`: `Simulator::Run`; cuối cùng `metrics.Finalize`.

**Tham số CLI:** `gridSize, spacing, numUav, fastRatio, cellSize|hex, cellRadius,
numFrag(layerSplit), maxFragBytes, alertThreshold, confirmThreshold, regionWindow,
beaconQuota, seed, scheme, simTime, outputDir`.

**Scheme:** `proposed` | `nocoop` (multi-UAV dump khắp nơi, không CL/summon) |
`pure-uav` (không WSN, UAV tự quét tới khi bay qua nạn nhân).

**Chọn target** deterministic theo seed (`std::mt19937(seed)`), độc lập scheme →
so sánh công bằng. ≥100 seed.

---

## 10. Metrics (`models/common/sar-metrics` — mở rộng từ round-1)

CSV: `metrics.csv` (1 dòng/run), `events.csv`, `trajectories.csv`, `config.txt`.

| Metric | Ý nghĩa |
|---|---|
| `timeToReportAtBS_s` | **CHÍNH** — cả vòng đến khi report tới BS |
| `timeToLocalize_s` | tới khi region leader SUMMON (khoanh vùng xong) |
| `timeToCompleteData_s` | node nhận đủ + confirm |
| `intraShares/interShares` | số lần hợp tác trong/liên cell |
| `regionCells` | số cell tham gia vùng manh mối |
| `pdr, pktSent, pktRecv` | tin cậy + airtime |
| `beaconCount, custodyHandoffs, routeDeviation_m, uavEnergyJ` | overhead/chi phí |

Visualizer HTML: thêm lớp vẽ **cell (hex/vuông) + CL + CGW + đường inter-cell** và
tô vùng manh mối; tái dùng `sar-viz.html` round-1.

---

## 11. Bố cục file `uav-sar/`

```
uav-sar/
├── CMakeLists.txt                 # + libpropagation; KHÔNG libwsn
├── docs/{DESIGN.md, ARCHITECTURE.md}
│   (tất cả VIẾT MỚI; "ref: main/…" = tham khảo ý tưởng, không copy)
├── models/common/
│   ├── cell-grid.{h,cc}           # hex cell + bầu CL(gần tâm) + cây trong-cell + màu-kề (ref: cell-layer,hex-cells-reference)
│   ├── inter-cell-routing.{h,cc}  # MỚI hẳn: CGW + inter-cell route
│   ├── target-profile.{h,cc}      # fragment L0..L3 + Confidence (ref: semantic-fragment)
│   ├── clue-field.{h,cc}          # manh mối theo khoảng cách (ref: local-clue)
│   ├── coop-link.{h,cc}           # chia sẻ intra/inter theo prob (ref: cooperation-phy-mac)
│   ├── sar-metrics.{h,cc}         # metrics vòng đầy đủ
│   └── sar-types.h                # MsgType/packet consts
├── models/network/
│   ├── air-ground-loss.{h,cc}     # A2G/G2G + fading + shadowing (ref: a2g-log-distance-loss)
│   └── sar-network.{h,cc}         # BS+M UAV+N sensor, kênh thực tế
├── models/application/
│   ├── flight-controller.{h,cc}   # điều khiển bay (ref: uav-flight-controller; sửa overshoot)
│   ├── sar-fast-uav-app.{h,cc}    # MỚI
│   ├── sar-data-uav-app.{h,cc}    # MỚI
│   ├── sar-ground-app.{h,cc}      # MỚI (node/CL/CGW roles)
│   └── sar-bs-app.{h,cc}          # MỚI
├── helper/sar/sar-config.{h,cc}   # MỚI orchestrator
├── examples/scenario-sar.cc       # MỚI entry (CLI + scheme)
└── tools/run_batch.sh             # ≥100 seed
```

---

## 12. Kế hoạch hiện thực theo pha (mỗi pha có verify)

1. **Substrate**: viết `cell-grid` (hex, CL=gần tâm, màu-kề) + `inter-cell-routing`
   (CGW) → unit test: in ra cell/CL/CGW/route; verify adjacency & route trên lưới nhỏ.
2. **Network+kênh**: sar-network với A2G+Nakagami+shadowing → smoke: 1 UAV bay,
   ground nhận gói, kiểm PDR theo khoảng cách/độ cao.
3. **Fragment+clue**: port semantic-fragment + local-clue → verify Confidence,
   phân bố clueQuality quanh target.
4. **FAST + phát hiện**: FAST sweep phát L0 → node vượt alert → REPORT lên CL.
5. **Hợp tác + summon**: CL gộp + inter-cell share + region-leader + 1 SUMMON.
6. **DATA + deliver + confirm + report**: relay→claim→divert→deliver→confirm→
   về BS→REPORT → chốt `timeToReportAtBS`.
7. **Metrics + baselines + batch ≥100 seed** + visualizer.

Mỗi pha build (`python3.10 ./ns3 build`) + chạy smoke trước khi sang pha sau.

---

## 13. Điểm rủi ro cần canh
- Overshoot waypoint (đặt arriveR theo tốc độ).
- Giữ `LrWpanHelper` sống suốt sim.
- MTU 100B: control-plane event-level, chỉ data-plane mới packet-level.
- Summon phải tới được DATA (persistent low-rate + FAST relay) — như round-1.
- Nhiều DATA cùng lao tới → shared claim token.
- Kênh thực tế (fading/shadow) làm mất chunk lúc giao → giao point-blank + có thể lặp.
```
