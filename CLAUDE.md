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

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

**All project-specific guidance** see `ns-3-dev-git-ns-3.46/src/wsn-uav/docs/progress/WORKING_WITH_REPO.md` for detailed instruction