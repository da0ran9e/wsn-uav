# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Task Completion Reporting

**After finishing any task, report the modifications quickly.**

- List each file modified and what changed
- One-line summary per file (the WHY, not WHAT)
- Include build/test results if applicable
- Format: `[file.cc] Change description — status ✓/✗`

Example:
```
[scenario1-config.cc] Moved RX callback setup to Build() — ✓
[ground-node-app.cc] Removed RX callback override in StartApplication — ✓
[CMakeLists.txt] Added lr-wpan-module include — ✓
Build: ✓ (rebuilt successfully)
Test: ✗ (RX callbacks still not firing)
```

---

## 6. UAV-SAR: READ THE STATUS DOC FIRST

**Before doing anything in `uav-sar/`, read `uav-sar/docs/STATUS.md`.** It is the
single source of current truth: what the measurements actually say, which
published numbers are stale or void, the ranked open problems, and the method
rules that were learned expensively (N ≥ 120, never trust a single seed, never
rebuild mid-campaign, assert on every scripted edit).

Two things that document will tell you but which are worth stating here too,
because they invert the project's original assumptions:

- **Cooperation does not buy the cost advantage — closing the loop does.** The
  `closed-loop` non-cooperative baseline beats `proposed` on time, energy and
  packets (0/120 paired wins on packets). What cooperation defensibly buys is a
  −29 % p90 localization error. Do not write or repeat "edge cooperation makes
  SAR faster and cheaper"; the data does not support it.
- **Numbers measured at N = 20 are void.** They missed a real 3.3 % failure mode
  and understated a delivery error by 42 %.

Note the surrounding sections were written for the older `src/wsn-uav/` layout;
the live work is in `uav-sar/` and builds via
`cd /home/user/ns3-dev && cmake --build cmake-cache -j 3`.

---

## 7. WSN-UAV Project-Specific Rules

### Build & Environment
- **Python 3.10 required** (3.14+ breaks ns-3 argparse)
- **Build command:** `python3.10 ./ns3 build` (NOT `./ns3 build wsn-uav`)
- **Configure:** `./ns3 configure --enable-examples --enable-modules=wsn-uav`
- **Run executables:** `python3.10 ./ns3 run scenario-X -- --param=value`
- **Check Python version before any build**

### Workflow Rules (User-Enforced)
- **NEVER commit unless explicitly asked** — user controls when to commit
- **Follow user instructions exactly** — don't add features beyond what's requested
- **No debug/verification code in final form** — remove probe callbacks once behavior is confirmed
- **Don't modify CMakeLists.txt** unless adding NEW source/header files

### Code Organization
- **Modify only:** `src/wsn-uav/` directory
- **Don't modify:** `src/wsn/`, root files, other modules
- **Structure:**
  - `models/common/` — No ns-3 dependencies
  - `models/application/` — ns-3 Application classes
  - `helper/` — Orchestrators (network, topology, trajectory)
  - `examples/` — Entry points with main()
  - `docs/progress/` — Session notes

### Radio Setup (Critical)
- **Always use ONE Cc2420Helper or LrWpanHelper instance** for all nodes
- **Wrong:** Separate helper instances → separate channels → no communication
- **Correct:** Single helper, all nodes installed via same instance on same channel
- Example:
  ```cpp
  LrWpanHelper lr;  // ← Single instance
  auto channel = lr.CreateChannel();
  lr.Install(groundNodes);
  lr.Install(uavNodes);  // ← Same helper instance
  ```

### LrWpanHelper lifetime (silent RX-break trap)
`LrWpanHelper::~LrWpanHelper()` calls `m_channel->Dispose()`, which empties the channel's PHY list. After that, TX still fires at the PHY level but **no packet ever reaches any RX**. If the helper is a local variable inside a setup function (e.g. `InstallRadio()`), it dies on return and silently kills the network.
- **Keep the helper alive for the entire simulation.** Store it as `std::unique_ptr<LrWpanHelper>` on the long-lived config/orchestrator (the helper has deleted copy/move).
- **Fast check:** `dev->GetChannel()->GetNDevices()` after setup — if 0 while devices look configured, the helper got destroyed.

### RX Callbacks (LrWpan-specific)
- **Callback signature:** `[](Ptr<NetDevice> dev, Ptr<const Packet> pkt, uint16_t proto, const Address& from) { return true; }`
- **Set callbacks BEFORE Simulator::Run()**
- **Call SetReceiveCallback() only once per device** (second call overwrites first)
- **Broadcast vs Unicast:** Mac16Address("ff:ff") for broadcast
- **Namespace:** LrWpan classes in `ns3::lrwpan::` namespace (e.g., `ns3::lrwpan::LrWpanNetDevice`)

### Fragment Generation
- **Algorithm:** Pixel-stride interleaving over 416×416×3 pixels
- **Formula:** `evidence_i = 1 - (1 - 0.90)^(pixelCount_i / totalPixels)`
- **Don't deviate** — paper baseline depends on exact match

### Network Parameters
- **Grid spacing:** 20.0m (NOT 45m)
- **UAV altitude:** 20.0m
- **UAV speed:** 20.0m/s
- **Broadcast radius:** 50.0m
- **All in** `models/common/parameters.h`

### Node ID Convention (Scenario 1)
Creation order in `Scenario1Network::CreateNodes()` determines node IDs:
- **BS = ID 0** (created first)
- **UAV = ID 1** (created second)
- **Sensors = IDs 2+** (created last, N×N grid)

Don't change creation order — downstream code (topology packets, k-means, log labels) depends on it.

### LR-WPAN MTU Constraint
- **PSDU = 127 bytes** (IEEE 802.15.4) includes MAC header (~13B) + FCS (2B). **App payload safe ceiling ≈ 100B**, NOT 127. Test result: 125B payload → `Send()` returns FAIL; 100B → OK.
- **Topology / control packets MUST use compact binary** (no JSON, no verbose strings).
- **Multi-packet topology format** (`BroadcastTopology` in BS app):
  - Header (6B): `[destId:u8][totalCount:u16][thisCount:u8][startIdx:u16]`
  - Entry (7B): `[id:u8, x:i16_dm, y:i16_dm, z:i16_dm]`
  - MAX_ENTRIES = (100 - 6) / 7 = 13 nodes/packet
  - UAV reassembles by `startIdx`; tracks `m_topoReceived` until `totalCount` reached
- **Back-to-back `Send()` calls need ≥200ms stagger** — otherwise MAC queue overflows and most packets FAIL. Schedule each packet via `Simulator::Schedule(Seconds(0.2 * pktIdx), ...)`. 50ms is NOT enough (verified).
- **Always check `Send()` return value** — silent FAIL appears as `sent=FAIL` in log.

### Output & Directories
- **Always create output directories explicitly:** `std::filesystem::create_directories(dirPath)`
- **Output format:**
  ```
  data/results/scenario-X/run-NNN/
  ├── metrics.csv
  ├── trajectories.csv
  ├── packets.csv
  └── config.txt
  ```

### Event Logging (`models/common/log.h`)
Never use `std::cout` in wsn-uav. Logger writes a markdown table to `src/wsn-uav/docs/visualize/result/<scenarioName>/<dd-MM-yy>/<hh-mm-ss>.md` (cwd-relative). Columns: `simtime | module | content`.

```cpp
LogN(GetNode())             << "...";  // runtime: auto t, module=Node[<id>].Application
LogN(GetNode(), "Mobility") << "...";  // override submodule
LogM("Scenario1Config")     << "...";  // info from named module, no time
Log()                       << "...";  // info, no time, no module
```

Module path: `Node[<id>].<Layer>` (Application/Phy/Mac/Mobility) for runtime; orchestrator class name (`Scenario1Config`, `Scenario1Network`) for setup. Call `LogReset(scenarioName)` first in `Build()`; `LogFlush()` at end of Build/Schedule/Run as crash-safe checkpoints. In lambdas capture `Ptr<Node>` (not just id) so `LogN(node)` works. No time/node prefix in content; `\n` and `|` are auto-escaped.

### Testing Checklist Before Each Commit
- [ ] Code compiles: `python3.10 ./ns3 build`
- [ ] No linker errors (all .cc files in CMakeLists.txt)
- [ ] Test passes: `./build/scenario-0-radio-test` or similar
- [ ] Output files exist: `ls data/results/`
- [ ] No debug stdout left behind

## 8. Mô tả gốc của người dùng (nguyên văn, không chỉnh sửa)

Dưới đây là toàn bộ mô tả và yêu cầu của người dùng, theo thứ tự thời gian, trích thẳng từ
bản ghi phiên (từ 2026-10-05). Đây là tham chiếu gốc: khi có mâu thuẫn, lời người dùng ở
đây và lời mới hơn thắng. Dòng in nghiêng phía trên mỗi khối là nhãn ngữ cảnh do Claude
thêm; nội dung trong khối là lời gốc. Khi có mô tả mới, thêm vào cuối theo cùng cách.

**Quy tắc làm việc hiện hành:** thảo luận và lên kế hoạch kỹ với người dùng trước khi chạy
bất kỳ chương trình tốn thời gian nào (xem mục cuối).

*1. 2026-10-05 · uav-sar · A2G-RUN: chuỗi gói liên tục, 7 node thẳng hàng*

```text
tôi cần bạn làm một thử nghiệm sau: với các node đều là chuẩn 802.15.4 mạng mặt đất 7 node cách nhau 300m sắp xếp trên 1 đường thẳng, UAV bay ở độ cao 100m bay với tốc độ 50m/s, phát tuần tự các gói tin liên tục có đánh số (cách nhau khoảng 10ms) vuông góc với mạng mặt đất bay trực tiếp qua node nằm giữa (node thứ 4). môi trường đô thị với hệ số 3.56 hoặc tương tự
 mục đích là test xem mỗi node có thể nhận được chuỗi packet liên tục là bao nhiêu trước khi bị lỗi (với kịch bản coi như file không thể khôi phục packet lỗi và yêu cầu nhận toàn bộ packet của file đó)
đọc qua yêu cầu này xem có thông số gì cần chốt lại trước khi triển khai không
```

*2. 2026-10-05 · uav-sar · bộ tham số A2G (đặc tả người dùng đưa)*

```text
Đây là bản đặc tả để anh đưa lại cho agent. Nó trả lời cả bốn câu hỏi chặn.

---

## Trả lời bốn câu hỏi

**1. Link budget — lỗi nằm ở chỗ neo suy hao, không phải ở công suất.**

Agent neo mô hình tại **1 m** rồi áp số mũ đô thị suốt từ đó tới 900 m. Sai về vật lý: UAV ở 100 m, node ngay dưới, **không có gì chắn** — đoạn đầu phải là suy hao không gian tự do.

Mô hình đúng là **hai đoạn, neo tại $d_{\rm ref}=H=100$ m**:

$$\beta(d)=\beta_{\rm ref}\left(\frac{d}{100}\right)^{-\alpha},\qquad \beta_{\rm ref}=\left(\frac{\lambda}{4\pi\cdot100}\right)^2=-80{,}05\ \text{dB}$$

Chỉ đổi chỗ neo là link budget đóng ngay: bán kính phủ đi từ 190 m lên **991 m**, cả bảy node đều nghe được.

**2. Số mũ suy hao — agent nói đúng, 3,56 là sai.** Dùng $\alpha \in \{2{,}6;\ 3{,}0;\ 3{,}35\}$, từ đo thực liên kết không–đất của Qiu 2017 (bán đô thị, độ cao thấp). Lấy **3,0 làm chính**, hai giá trị kia để quét độ nhạy.

**3. Nhịp 10 ms — giữ nguyên, bỏ qua MAC.** Agent lập luận đúng: một máy phát duy nhất, không ai tranh chấp, luật 200 ms là hiện tượng tràn hàng đợi MAC chứ không phải vật lý. **Bơm thẳng xuống PHY**, không CSMA, không ACK, không beacon. 10 ms là khe mặc định của IEEE 802.15.4, có nguồn.

**4. Phải có fading bốc lại mỗi gói — agent nói đúng.** Mô hình dùng **Rician $K_c = 2$**. ns-3 không có Rician sẵn, nên dùng **Nakagami $m = 1{,}80$**, là giá trị tương đương theo $m=(K+1)^2/(2K+1)$.

---

## Bộ tham số

| | Giá trị | Nguồn |
|---|---|---|
| **Hình học** | | |
| Độ cao bay $H$ | 100 m | |
| Tốc độ UAV | 50 m/s, đều, thẳng | theo yêu cầu |
| Đường bay | từ −2000 m đến +2000 m, vuông góc, qua đúng node 4 | |
| Node | 7 node thẳng hàng, cách 300 m, lệch 900/600/300/0 m | |
| **Vô tuyến** | | |
| Tần số | 2,4 GHz | IEEE 802.15.4 |
| Băng thông | 2 MHz | IEEE 802.15.4 |
| Tốc độ bit | 250 kbps | IEEE 802.15.4 |
| **Công suất phát UAV** | **+10 dBm** | trần pháp lý +20 dBm EIRP (EU) |
| **Độ nhạy máy thu** | **−100 dBm** | điển hình chip; chuẩn chỉ đòi ≥ −85 |
| Nền nhiễu | −106 dBm | $-174 + 10\log_{10}(2\text{M}) + 5$ |
| Hệ số tạp âm | 5 dB | |
| **Suy hao, đoạn 1** | không gian tự do tới **100 m** → **−80,05 dB** | |
| **Suy hao, đoạn 2** | $(d/100)^{-\alpha}$, $\alpha = 3{,}0$ (quét 2,6 và 3,35) | Qiu 2017, A2G |
| **Fading** | **Nakagami $m=1{,}80$**, bốc lại **mỗi gói** | tương đương Rician $K_c=2$ |
| Che khuất | **tắt** ở bản chạy đầu | bốc một lần mỗi run nên chỉ dịch cửa sổ, không bẻ chuỗi |
| Ăng-ten | **đẳng hướng hai đầu** | giả thiết của mô hình; dipole có null thiên đỉnh sẽ làm hỏng node 4 |
| **Gói và thời gian** | | |
| Khung đầy đủ | 133 B (4 tiền tố + 1 đồng bộ + 1 tiêu đề + 127 tải) | IEEE 802.15.4 |
| Tải tin hữu ích | 99 B | khung 127 B trừ 28 B tiêu đề, bảo mật, kiểm tra |
| Thời gian chiếm sóng | 4,256 ms | $133\times8/250000$ |
| **Chu kỳ gói** | **10 ms** | khe mặc định IEEE 802.15.4 |
| Số gói mỗi lượt | **8 001** | 4000 m / (50 × 0,01) |
| **Chạy** | | |
| Số lượt lặp | **≥ 200** | thống kê cực trị, phương sai lớn |
| Bỏ qua | MAC, CSMA, ACK, beacon | một máy phát, quảng bá thuần |

---

## Kết quả mong đợi, để đối chiếu

Tôi đã tính sẵn bằng mô hình giải tích. Nếu ns-3 ra khác đáng kể thì có chỗ sai:

**$\alpha = 3{,}0$:**

| Node | Lệch ngang | Cự ly gần nhất | Tổng gói thu | **Chuỗi liên tục dài nhất** |
|---|---|---|---|---|
| 1 và 7 | 900 m | 906 m | ≈ 1 362 | **11 ± 2** |
| 2 và 6 | 600 m | 608 m | ≈ 2 677 | **40 ± 9** |
| 3 và 5 | 300 m | 316 m | ≈ 3 459 | **208 ± 73** |
| 4 | 0 | 100 m | ≈ 3 691 | **823 ± 202** |

**$\alpha = 3{,}35$:** chuỗi dài nhất lần lượt **4 / 20 / 151 / 740**.

---

## Hai điểm phải ghi vào báo cáo

**Thời gian chiếm sóng dài hơn thời gian kết hợp của kênh.** Ở 50 m/s, tần số Doppler 400 Hz, thời gian kết hợp ≈ **1,06 ms**, trong khi gói chiếm sóng **4,256 ms**. Nên kênh đổi **trong lòng một gói** — giả thiết fading không đổi trong gói là xấp xỉ, và nó làm kết quả **lạc quan** khoảng hệ số 4. Agent đã phát hiện đúng chỗ này, phải ghi lại.

**Đây là thí nghiệm đô thị.** Nếu phần còn lại của dự án là kịch bản rừng thì con số rút ra ở đây **chỉ dùng cho nhánh đô thị**, không được đem sang.
```

*3. 2026-10-05 · uav-sar · hình dải gói của node 4*

```text
tôi muốn một ảnh dùng để minh hoạ, ví dụ với một dải dữ liệu gửi cho node 4, các ô trên dải tượng trưng packet vậy, packet lỗi đánh dấu đỏ lấy trực tiếp từ giả lập
```

*4. 2026-10-05 · uav-sar · quét độ cao*

```text
thử với các độ cao khác nhau cho tôi thêm thông tin tương tự nhé
```

*5. 2026-10-06 · uav-sar · A2G-SWEEP: mạng lớn, quét luống*

```text
giờ hãy dùng các mô hình này và dựng một mạng sensor cỡ lớn, các node cách nhau 100 m trên một vùng rộng, uav quét theo luống cách nhau khoảng 700m đến 1km uav vẫn phát các gói tin có đánh dấu tuần tự. mục đích để xem các lượt bay lại có bù được gói mất ở các node xa đường bay không. ngoài kết quả phân tích gói tin hãy cho tôi thêm visualize đường bay
```

*6. 2026-10-06 · uav-sar · G2G-CHAIN: hợp tác tại biên trên một dải node*

```text
bây giờ hãy xét đến hợp tác tại biên, ví dụ ta có một cluster đủ rộng (uav không thể phủ một lúc hết tất cả) một số node ở đầu này sẽ có những packet mà đầu kia không có. ta dựng một giả lập các node nằm trên một dải và cách nhau 50 - 100m node ở đầu hàng nắm khoảng 100 packet cần gửi đến cuối hàng và phải đi lần lượt qua từng node một (unicast) 
cần xét đến việc liên kết G2G khác với A2G khi các node cần có lịch làm việc nghiêm ngặt hơn để tránh va chạm cũng như thông lượng có thể ít hơn nhiều kênh truyền cũng khác hơn vì có nhiều tia NLoS hơn 
mục tiêu là quan sát thời gian các gói tin đi từ đầu đến cuối cluster trên một đường cho trước
```

*7. 2026-10-06 · uav-sar · câu hỏi về G2G*

```text
lý do các gói bị lỗi chủ yếu là gì, giải thích thế nào về việc thời gian bị kéo dài nhiều lần
```

*8. 2026-10-06 · uav-sar · câu hỏi về G2G*

```text
vậy gói gửi bị hỏng phải được gửi lại và do đó nó chặn các gói khác?
```

*9. 2026-10-07 · uav-coop · bước 1: lưới lục giác, chọn miền, gen node*

```text
giờ chúng ta sẽ dùng chính những tham số thử nghiệm đó để bắt đầu 
tạo project mới và bắt đầu với cơ chế gen node ngẫu nhiên như sau:
bắt đầu với việc gen ra một lười cell lục giác đều từ toạ độ gốc với tham số kích thước là chiều rộng cell = 100m sau đó chọn ngẫu nhiên một mảng cell liền kề nhau. tiếp đến gen các node ngẫu nhiên trong vùng vừa chọn, với mật độ là tham số spacing khoảng 20-50m 
cho tôi cả visualize các bước chạy của chương trình, 
xong bước này tôi sẽ hướng dẫn tiếp
```

*10. 2026-10-07 · uav-coop · độ lồi, thuộc tính node, CH/CL*

```text
cần thêm một tham số để điều chỉnh độ lồi của miền này và điều chỉnh cho miền lồi hoàn toàn để tiếp tục thử nghiệm, trường hợp khi lồi sẽ thử nghiệm sau,
các node được gen ngẫu nhiên sẽ mang ngẫu nhiên 3 thuộc tính ngẫu nhiên: khả năng quan sát, khả năng tính toán, khả năng giao tiếp. mỗi thuộc tính nhận giá trị ngẫu nhiên >=0, khả năng giao tiếp >0. Node có cả 3 tham số này cao nhất được đánh dấu là CH, các node manh nhất của mỗi cell được đánh dấu là CL
```

*11. 2026-10-07 · uav-coop · R = 100, miền ngẫu nhiên thật, đường Dubins*

```text
ồ ý tôi rông 100m tức là R=100 ấy nhé
tôi không muốn vẽ một hình elip trước rồi fill vào mà tôi muốn nó thực sự gen ngẫu nhiên, sau đó dựa trên tham số độ lồi mà fill thêm vào các vùng lõm của cluster cho nó lồi dần ra 
công việc tiếp theo, xác định 3 node có năng lực tốt nhất cluster (bao gồm cả CH) vẽ một đường dubin đi qua 3 điểm này với bán kính tối thiểu là một tham số cho trước (chưa cần có node UAV ở bước này mới chỉ xác định đường bay)
```

*12. 2026-10-07 · uav-coop · đường bay mở qua 2 điểm biên và CH*

```text
ý tôi không phải một đường dubin khép kín, chỉ cần là một đường đi từ ngoài cluster xuyên qua nó thôi, có thể đổi tính huống một chút, chọn ngẫu nhiên 2 điểm nằm ở biên của cluster, vẽ đường dubin đi qua 2 điểm đó và CH
```

*13. 2026-10-07 · uav-coop · CH xa biên; UAV bay và phát tin*

```text
làm cách nào để CH xuất hiện đừng quá gần biên mà không ảnh hưởng tới phân phối các node khác.
công việc tiếp theo tôi muốn chính là đưa UAV vào đường bay này với kịch bản phát tin như trước đó đã tính để xem các node nhận được bao nhiêu packet
```

*14. 2026-10-07 · uav-coop · routing PECEE elastic clustering*

```text
xây dựng đường routing sẵn cho các node như sau:

* xác định hop tiếp theo đến CL của cell hiện tại 
* xác định hop tiếp theo tới mỗi cell liền kề 
* lưu lại các đường next hop này để sử dụng trong quá trình truyền tin, và lưu lại đường gần nhất tới CH là đường chính 

đây là cơ chế routing elastic clustering của PECEE bạn đã cài trước đó. cài lại và cho tôi xem visualize đường routing đến CH xem đã chuẩn chưa
```

*15. 2026-10-07 · uav-coop · gateway duy nhất, không node cô lập*

```text
nên nhớ là các đường qua cell khác cần có 1 node đại diện làm gateway có nghĩa là dữ liệu chỉ có một đường để đi intercell, các cơ chế còn lại có thể flexible để phù hợp với ứng dụng hiện tại
phần routing này coi như đã được tính toán từ trước nên không được để bất kỳ node nào bị cô lập khỏi mạng coi như được chỉ huy tập trung tại BS
```

*16. 2026-10-07 · uav-coop · câu hỏi: gói nhận tốt nhất/tệ nhất; manifest nhẹ · kèm ảnh*

```text
một câu hỏi trước khi đi tiếp: đối với các node nằm ở vị trí tốt nhất nhận được bao nhiêu gói, các vị trí tệ nhất nhận được bao nhiêu gói. ví dụ tôi muốn các node không nhận đủ gửi một manifest những gói nó có hoặc những gói nó đang còn thiếu dần tới CH, thì gói tin manifest này có thể thiết kế như nào cho nhẹ
```

*17. 2026-10-07 · uav-coop · ý tưởng chia sẻ nội cell và manifest*

```text
ý tưởng là trong một cell các gói được tính là tài sản chung và tự trao đổi nhanh để nắm bắt tình hình của nhau, nếu cell đó thiếu mảnh nào thì manifest mảnh đó. 
gói tin manifest sẽ được gửi về hướng CH nhưng không cần phải tới được Ch. Trên đường gói tin đó đi, các cell nghe manifest nếu có thể đáp ứng thì đáp ứng luôn và sửa lại manifest theo điều kiện cell đó hiện tại, dần dần manifest sẽ được đáp ứng ngay cả khi nó chưa tới được CH 
trước khi phát triển tiếp ý tưởng này, đầu tiên cài đặt ý tưởng chia sẻ nội cell trước, đảm bảo thôg tin lan đều trong cell, node đủ bù cho node thiếu (chưa chạm sang cell bên ngoài)
```

*18. 2026-10-07 · uav-coop · chia sẻ nội cell: gom về node mạnh (gửi giữa chừng)*

```text
tôi vừa suy nghĩ lại cơ chế chia sẻ nội cell, ta không nhất thiết phải chia sẻ toàn bộ các node trong cell mà làm như sau: trong cell xác định ra vài node có khả năng mạnh hơn mức trung bình tính cả CL, sau đó các node gần đó tập hợp dữ liệu lại cho các node này đầy đủ dữ liệu là được, trong đó CL sẽ nắm thông tin chung rằng cell hiện tại có bao nhiêu và thiếu bao nhiêu
```

*19. 2026-10-07 · uav-coop · yêu cầu thời gian nội cell*

```text
công việc chia sẻ nội cell này cần được hoàn thành cực nhanh cỡ ms đến vài s
```

*20. 2026-10-07 · uav-coop · trả lời câu hỏi của Claude về chia sẻ nội cell*

```text
đừng vội cài đặt chia sẻ toàn cell chỉ làm cơ chế hợp tác nội cell trước
```

*21. 2026-10-07 · uav-coop · bản tóm tắt nội cell về CL*

```text
hiện tại góc nhìn của ta đang nằm trong 1 cell nhé, giả sử sau khi UAV bay qua, các node trong cell đều nhận được một phần dữ liệu, cần một bản tóm tắt ngắn gọn những gì mình có về CL để CL chuẩn bị đưa ra quyết định manifest
```

*22. 2026-10-07 · uav-coop · mở thảo luận manifest*

```text
tiếp theo chúng ta chỉ thảo luận kỹ trước về cơ chế manifest này, sau khi các CL có thông tin nội bộ thì nó cần chuẩn bị một bản tin manifest để gửi tới các cell tiếp theo, vậy các cell nằm xa đường bay nhất là các cell nên chủ động manifest. theo bạn cơ chế nên như nào
```

*23. 2026-10-07 · uav-coop · thiết kế manifest (MANIFEST-vi.md §0 b)*

```text
theo tôi như này: 
khu vực vốn đã lên kế hoạch ký nên các cell vốn đã biết được vị trí của nhau rồi. cell nằm ở biên ngay sau khi tóm tắt nội cell xong( không còn nhận được gói mới từ uav nữa) nó chủ động manifest tới cell tiếp theo. các cell không phải biên thì chỉ chờ mà không chủ động. nếu sau khoảng thời gian đó các cell khác thấy cell biên đáng lẽ phải manifest cho mình thì tự manifest ngược đến nó ( vì đây nằm trong hai trường hợp hoặc là cell biên đã nhận đủ hoặc là cell biên chưa nhận được gói nào nên manifest chưa được trigger) cell nhận được môt manifest ngược sẽ tự hiểu ra tình hình. 
nội dung gói manifest như bạn đề xuất 
trong lúc đang manifest các cell cũng không nằm yên mà tiếp tục tiến hành trao đổi dữ liệu nội cell như đã tóm tắt từ trước để tiết kiệm thời gian, dữ liệu mới đến thì nó cũng được truyền theo đường này đến các node quan trọng
khi manifest đến nếu cell đó có một trong số các gói được manifest thì nó gửi luôn và cắt bới manifest đồng thời dữ liệu đi qua cell đó mà nó thấy thiếu thì nó cũng tự lưu một bản sao cho bản thân 
về lý thuyết, chỉ các cell ở biên manifest nhưng các cell còn lại đều hưởng lợi 
nếu manifest đến CH mà CH vẫn không thể đáp ứng, nó có thể đoán được hướng đang có và hướng đang thiếu để manifest tiếp (hướng nào không có manifest đến thì coi như là có đủ) nhưng pha manifest cơ sở coi như dừng lại tại đây khi mà manifest tới CH, cluster vấn tiếp tục chạy manifest tiếp nhưng sẽ gọi la bước manifest thứ cấp, chạy song song với nhiệm vụ nhận diện (tạm thơi chưa bàn)
với khe thời gian, với mỗi cell các cặp gateway có kênh riêng để giao tiếp intercell, 
mảnh nhận lưu luôn tại CL và các node mạnh
```

*24. 2026-10-07 · uav-coop · trả lời đề xuất 1–7 (MANIFEST-vi.md §0 c)*

```text
trả lời các đề xuất của bạn:
1. không cần gửi gói thông báo đủ, nếu cell biên đủ thì cell bên trong cũng có khả năng đã đủ tất nhiên cũng không cần manifest ngược nữa. cho nên cell trong cũng dựa trên trạng thái của bản thân đánh giá tình hình, nếu nó đủ cũng có nghĩa là cell biên ít nhiều cũng có được thông tin, nếu nó thiếu thì mới manifest ngược (cell trong ở đây chỉ các cell cận biên nằm ngay cạch cell biên, không phải cell nào cũng chờ
2 đề xuất 2 tôi đồng ý
3 đề xuất này tôi sẽ đính chính thêm về thiết kế manifest như sau: các manifest mang thông tin về những cell đi qua có gì ví dụ: có tổng 3 file ABC với các gói lần lượt là 1,2,3,4,5,6,7,8,9 cell biên gửi manifest A4689 tức là nó đang có đủ file A thiếu gói 5 của file B và gói 7 của file C.  cell bên trong nhận được đối chiếu bộ dữ liệu thấy mình có gói 5 thì ngay lập tức gửi cho cell biên và sửa lại nội dung manifest là AB89 cho cell tiếp theo, cell tiếp theo gửi gói 7 trở lại thì nó lưu một bản sao và chuyển tiếp cho cell biên
tôi đồng ý với đề xuất 4 cần có lập lịch tốt cho gateway
đề xuất 5 6 7 cũng như ví dụ tôi nêu trên 
trong khi viết đặc tả, lưu lại nguyên văn đoạn mô tả của thôi không chỉnh sửa để làm bản tham chiếu gốc và bắt đầu cài đặt thử
```

*25. 2026-10-08 · uav-coop · đính chính (MANIFEST-vi.md §0 d)*

```text
1. manifest mô tả những gì mình có, không phải những gì mình thiếu, những mảnh nó chưa có thì đều là mảnh thiếu 
2. chỉ những cell biết phía trước mình có một cell biên khác mới chờ, nếu nó cũng vừa là biên nhưng lại vừa là bước tiếp theo của cell biên khác vậy thì nó cũng chờ, chỉ những cell biên không có biên khác của mình sẽ chủ động gửi manifest
3. ta sẽ thử bằng thử nghiệm sau 
4. dữ liệu về CL đi qua các node mạnh thì nó tự lưu lại một bản sao cho mình chứ không chủ động yêu cầu dữ liệu
```

*26. 2026-10-08 · uav-coop · yêu cầu hình*

```text
cho tôi xem visualize
```

*27. 2026-10-08 · uav-coop · yêu cầu hình*

```text
cho tôi xem phân bổ dữ liệu sau quá trình manifest
```

*28. 2026-10-08 · uav-coop · so sánh mức cell*

```text
nếu xét ở mức độ cell thì mỗi cell chênh lệnh nhau bao nhiêu gói, cho tôi xem visualize cũng bản đồ này nhưng thay vì so các node hãy so các cell
```

*29. 2026-10-08 · uav-coop · tiêu chí; thử kịch bản khác*

```text
các gói nằm ở node quan trọng là được,
hãy thử nghiệm với một vài kịch bản khác xem sao
```

*30. 2026-10-08 · uav-coop · nhiều đường bay, K = 2000 · kèm ảnh*

```text
giả sử mỗi file có khoảng 2000 gói đi, tôi muốn thử nghiệm nhiều kịch bản đường bay khác nhau, giống 3 trường hợp đầu này
```

*31. 2026-10-08 · uav-coop · mã giả*

```text
mô tả lại thuật toán thành pseudo code học thuật vào file mô tả đi
```

*32. 2026-10-08 · uav-coop · câu hỏi thời gian*

```text
toàn bộ pha manifest cơ sở diễn ra trong bao lâu sau khi UAV rời đi
```

*33. 2026-10-08 · uav-coop2 · đóng gói uav-coop, mở giải pháp mới*

```text
được rồi đóng gói lại, tạo folder mới chuẩn bị cho một giải pháp khác. 
giải pháp mới này chúng ta cũng bắt đầu với một mạng và đường bay tương tự, uav cũng phát gói như vậy nhưng sẽ thử nghiệm một cơ chế hợp tác biên mới. đầu tiên cho tôi lại tình huống sau khi uav đi qua cluster
```

*34. 2026-10-09 · uav-coop2 · độ cong đường bay; chỉ gói liền nhau mới thành file*

```text
thêm một tham số để có thể điều chỉnh độ cong của đường bay bằng cách chọn vị trí 2 điểm ở biên 
và cho tôi xem nếu file khoảng 1000packet và 2000packet thì có bao nhiêu node nhận đủ file, nên nhớ, các packet liền nhau mới coi là đủ một file (3000 packet rời rạc cũng không ghép được thành một file
```

*35. 2026-10-09 · quy tắc làm việc*

```text
tiếp theo tôi và bạn cùng thảo luận, lên kế hoạch thật kỹ trước khi chạy bất cứ chương trình tốn thời gian nào nhé. 
nếu bạn có thể hãy gom tất cả những mô tả của tôi lại thành một bản trong CLAUDE.md tránh quên khi đổi session (dùng lời gốc của tôi, không chỉnh sửa)
```

*36. 2026-10-09 · quy tắc làm việc · hỏi về nén/mã hoá bản ghi*

```text
có cách nào nén hoặc mã hoá đoạn hội thoại kiểu vậy không, chỉ cần mã hoá đơn giản để không thể đọc bằng mắt thường mà bạn vẫn có thể dễ dàng giải mã để đọc bất cứ lúc nào ngay cả khi đổi sesssion
```

*37. 2026-10-09 · quy tắc làm việc · hoàn tác mã hoá, repo private*

```text
thôi hoàn tác đi, ta chỉ cần set repo private là được
```

*38. 2026-10-09 · uav-coop2 · nhiều file nối tiếp, node được trao đổi gói; tầm nhìn nghiên cứu (ví dụ, chưa phải bản cuối)*

```text
UAV sẽ phát nhiều file nối tiếp nhau và coi như các file không thay thế được cho nhau và các node hoàn toán có thể trao đổi các gói mà nó cần cho nhau để ghép lại thành file 

trước tiên tôi sẽ nhắc lại về tầm nhìn của nghiên cứu một chút để bạn cập nhật lại, dưới đây là một tình huống giả định ví dụ đọc và bám ý chính là được, không nên coi đây là phiên bản cuối cùng: 
"Một khu vực đô thị được phủ bởi hàng nghìn node IoT mỗi thiết bị đang phục vụ một mục tiêu khác nhau do đó năng lực cũng khác nhau. 

* Một số được tích hợp sẵn camera, ví dụ: camera an ninh, chuông cửa, máy bán hàng tự động…thậm chí là camera hành trình của ô tô (node di động)
* Một số có khả năng tính toán tại biên mạnh
* Một số có kênh vô tuyến tốt 

Tính chất chung của các camera là nó ghi hình liên tục và được lưu vào bộ nhớ. Bộ nhớ mỗi thiết bị khác nhau nên thông tin cũng có hạn khác nhau. Tổng lại là một khối dữ liệu khổng lồ.
Giả sử một đứa trẻ đi lạc, hoặc một đối tượng cần được truy vết sau một vụ việc. 
Phần mạng có hàng nghìn ống kính chĩa vào ngõ nhỏ, mặt tiền cửa hàng, sân chung cư và lối vào toà nhà. Hoàn toàn có khả năng thông tin đối tượng đang được tìm kiếm đã được ghi lại.
Có thể có nhiều mục tiêu tìm kiếm hoặc đối tượng di chuyển tạo thành một vệt đường đi nhiều camera bắt được 
Vấn đề là chúng chỉ đang làm nhiệm vụ của mình, hoành toàn không hay biết sự kiện gì vừa sảy ra hay cần tìm ai.
Một số it camera giao thông có đường dữ liệu riêng về BS nhưng:

* Độ phủ nhỏ, ít điểm quan sát
* Tốn thời gian tải và xử lý khối dữ liệu lớn 

Cái thiếu là truy vấn: một mô tả cô đọng về đối tượng, đặt được vào tay từng nút biên trước khi bằng chứng bị ghi đè.
Tại sao không tải dữ liệu về:

* Trong các kịch bản ở nơi hoang dã (rừng quốc gia, khu bảo tồn…) camera từ các thiết bị an ninh chỉ có LoRa, vệ tinh chuyển được vài trăm byte/h. 
* Trong trường hợp đô thị, dữ liệu thô về mặt pháp lý không thể được tải về một cách đơn giản.

Để đưa được các truy vấn này đến các thiết bị, UAV là một sự lựa chọn hiển nhiên. 
Truy vấn này được mô tả là một tập ảnh tham chiếu hoặc video.
Phương án
Chiến lược 3 Pha:
Pha 0 (phát tán). Các thiết bị mặt đất được chia thành các Cluster có chặn trên kích thước. bầu CH cho mỗi cụm.
Pha 1. Đội bay 1 xuất phát mang theo tập dấu vết mô tả đối tượng và bay theo một quỹ đạo sao cho giao được cho mọi cụm mặt đất đủ lượng.
Phản hồi. Mỗi cụm đã khôi phục được tập dấu vết sẽ quét ngược kho lưu trữ cục bộ của mình, tính một điểm nghi vấn, và gửi một báo cáo ngắn qua đường truyền tầm xa tốc độ thấp sẵn có về BS. BS tập hợp thành một danh sách cụm nghi vấn đã xếp hạng.
Pha 2 (xác minh). Đội bay 2 tới các cụm nghi vấn theo thứ tự xếp hạng để xác nhận hoặc bác bỏ.
Mô hình hệ thống
Mạng mặt đất và các lớp năng lực
Mạng mặt đất gồm N node tổ chức thành C cụm. Mỗi cụm c có một cluster head và các node lá của nó nằm trong bán kính nội cụm Rc. Cluster head là thiết bị mạnh hơn hẳn lá.
Mạng mặt đất không đồng nhất, mỗi node có những năng lực và quyền sở hữu riêng:

* Camera
* Khả năng tính toán 
* Kênh truyền không dây
* Bộ nhớ lưu trữ (dữ liệu mới sẽ ghi đè lên dữ liệu cũ)
* Các node không cùng chủ sở hữu có thể sẽ không chấp nhận việc hợp tác do bảo mật 

Miền không lồi: địa hình khu vực đô thị phức tạp, có vật cản 

* Vật cản mềm: sông, hồ có thể bay qua nhưng hoàn toàn không có thiết bị nào 
* Vật cản cứng: khu vực cấm bay, cao ốc UAV không thể bay vào nhưng vẫn có thể truyền tin được từ bên ngoài 
* Vật cản che khuất: hẻm núi không thể bay cũng không có thiết bị để truyền tin 

Tập dấu vết (dùng cho phase 1)
Đối tượng được mô tả bằng một tập dữ liệu là ảnh tham chiếu được trích ra từ tập ảnh gốc rõ nét hoặc video. Có 4 cách mô tả tập dấu vết:

* Là tập ảnh có manh mối độc lập, là các ảnh khác nhau. 
* Là các ảnh khác nhau nhưng liên quan đến nhau (cùng được trích ra từ một video) 
* Là từ một ảnh được chia ra theo pattern (mỗi manh mối đều mang đặc trưng của ảnh gốc nhận càng nhiều càng khôi phục được ảnh gốc rõ nét)
* Là một ảnh được chia ra theo fountain coding (cần thu thập một lượng cố định mới có thể khôi phục ảnh) 

Động học phương tiện
Đội bay gồm các UAV fixed wing cho phase 1 và rotary wing cho phase 2 chịu ràng buộc độ cong phụ thuộc tốc độ. Với fixed wing còn chịu ràng buộc về tốc độ trên ngưỡng thất tốc và không thể hover.
Kênh phản hồi
Mỗi cụm bị gắn cờ gửi một báo cáo về BS khoảng vài byte qua LoRa hoặc vệ tinh có giới hạn chu kỳ phát do đó có độ trễ phản hồi khác nhau với mỗi Cluster."
```

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

**All project-specific guidance** see `ns-3-dev-git-ns-3.46/src/wsn-uav/docs/progress/WORKING_WITH_REPO.md` for detailed instruction