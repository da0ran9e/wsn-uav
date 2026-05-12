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

## 6. WSN-UAV Project-Specific Rules

### Build & Environment
- **Python 3.10 required** (3.14+ breaks ns-3 argparse)
- **Build command:** `python3.10 ./ns3 build` (NOT `./ns3 build wsn-uav`)
- **Configure:** `./ns3 configure --enable-examples --enable-modules=wsn-uav`
- **Run executables:** `python3.10 ./ns3 run scenario-X -- --param=value`
- **Check Python version before any build**

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