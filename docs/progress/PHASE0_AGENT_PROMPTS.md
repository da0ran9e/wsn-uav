# Phase 0 Refactoring: Agent Prompts

These prompts are designed for **parallel agent execution**. Each agent handles one task independently.

**Prerequisites:** Read `/Users/mophan/Github/wsn-uav/docs/PHASE0_REFACTORING_PLAN.md` first.

---

## Prompt 1: Data Structure Refactoring

**Agent Type:** Code modification specialist  
**Files:** `src/wsn-uav/helper/wsn-network-helper.h`  
**Task Duration:** 4-6 hours  
**Status:** 🔴 BLOCKING (do this first)

### Context

You're refactoring a wireless sensor network simulator from single-UAV to multi-UAV support. The project currently hardcodes `Ptr<Node> m_uavNode` (singular). You need to make the data structures generic for N UAVs while maintaining 100% backward compatibility.

**Current state:** Single UAV hardcoded in WsnNetworkHelper class  
**Target state:** Support 1 to N UAVs without API changes for Scenario 1

### Your Task

Modify `src/wsn-uav/helper/wsn-network-helper.h` (lines 106-150) to replace single-UAV assumptions with N-UAV capable data structures:

**Specific Changes:**

1. **Replace these members (lines 120-126):**
   - Remove: `Ptr<Node> m_uavNode;`
   - Remove: `Ptr<WsnUavMac> m_uavMac;`
   - Remove: `std::vector<Waypoint> m_uavWaypoints;`
   
   With:
   - Add: `NodeContainer m_uavNodes;`
   - Add: `std::map<uint32_t, Ptr<WsnUavMac>> m_uavMacs;`
   - Add: `std::map<uint32_t, std::vector<Waypoint>> m_uavWaypoints;`
   - Add: `std::map<uint32_t, Ptr<FragmentDisseminationApp>> m_uavApps;`

2. **Update `SimulationConfig` struct (lines 33-66):**
   - Field `numUavs` already exists (line 42) but unused - keep it
   - Add new fields for per-UAV configuration:
     ```cpp
     std::vector<double> uavStartingX = {};
     std::vector<double> uavStartingY = {};
     std::vector<double> uavStartingZ = {};
     ```
   - Add validation flag: `bool validatePerUavConfig = false;`

3. **Update `SimulationResults` struct (lines 72-84):**
   - Replace: `double uavPathLength = 0.0;`
   - With: 
     ```cpp
     std::map<uint32_t, double> uavPathLengths;
     double totalUavPathLength = 0.0;
     double cooperationOverlapRatio = 0.0;
     std::map<uint32_t, uint32_t> fragmentsPerUav;
     ```

4. **Add new private method declarations (after line 146):**
   ```cpp
   uint32_t GetUavCount() const { return m_uavNodes.GetN(); }
   void CreateUavNodes(uint32_t count);
   void InstallUavRadios();
   void InstallUavApplications();
   void ScheduleUavFlights();
   void OnUavDetection(uint32_t uavId, uint32_t nodeId, double timeSeconds);
   ```

5. **Update existing callback signature (line 110):**
   ```cpp
   // OLD: void OnUavNodeMacIndication(uint32_t nodeId, ...);
   // NEW: void OnUavNodeMacIndication(uint32_t uavId, Ptr<Packet> packet, ...);
   ```

6. **Update `SimulationConfig::Validate()` return type to be more detailed:**
   - Already defined in .h, implementation in .cc (you don't modify this, just make sure it compiles)

### Constraints

- ✅ Keep full backward compatibility (numUavs=1 → same behavior)
- ✅ All data in private section (don't expose implementation)
- ✅ Add include guards if needed: `#include <map>`
- ❌ Do NOT implement the methods, just declare them
- ❌ Do NOT modify .cc file (Task 2 does that)
- ✅ Code must compile (check with clang or compiler lint)

### Verification

After your changes, compile should work (even if linking fails):
```bash
# In ns-3-dev-git-ns-3.46 directory
./ns3 build 2>&1 | grep "error"
# Should output: (nothing, or only linking errors)
```

### Testing Notes

- Scenario 1 will still work because default `numUavs = 1`
- Old code paths using `m_uavNode` will fail to compile in Task 2 (that's expected)
- Single-UAV specific hardcoding lives in .cc file (Task 2 refactors that)

---

## Prompt 2: Helper Method Implementation

**Agent Type:** C++ implementation specialist  
**Files:** `src/wsn-uav/helper/wsn-network-helper.cc` (multiple methods)  
**Task Duration:** 5-7 hours  
**Depends On:** Task 1 (must be complete)  
**Status:** 🟡 BLOCKING (blocks Task 4)

### Context

You're implementing the refactored multi-UAV methods in WsnNetworkHelper.cc. The data structures are now ready (Task 1), so you need to rewrite the helper methods to:
- Create N UAVs instead of 1
- Install radios and apps on each UAV
- Plan trajectories for each UAV
- Schedule flights for each UAV

All while keeping Scenario 1 (1 UAV) producing identical results to before.

### Your Task

Modify `src/wsn-uav/helper/wsn-network-helper.cc` to implement N-UAV methods:

**Specific Changes:**

1. **Refactor `CreateNodes()` (lines 87-109):**
   - Keep ground node creation exactly the same
   - Replace UAV creation block with call to new method: `CreateUavNodes(m_config.numUavs);`
   - Ground nodes part unchanged

2. **Add new method `CreateUavNodes(uint32_t count)` (after CreateNodes):**
   ```cpp
   void WsnNetworkHelper::CreateUavNodes(uint32_t count) {
       for (uint32_t i = 0; i < count; i++) {
           // See PHASE0_REFACTORING_PLAN.md Task 2 for full implementation
           // Create node, mobility model, compute starting position
           // Default: spread UAVs around network perimeter
           // If config provides positions: use those instead
       }
   }
   ```
   
   Use this helper to compute default positions:
   ```cpp
   Vector ComputeDefaultUavStart(uint32_t uavId, uint32_t totalUavs) {
       double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
       double centerX = gridDiameter / 2.0;
       double angle = (2.0 * M_PI * uavId) / totalUavs;
       double radius = 250.0;  // 250m from center
       double startX = centerX + radius * cos(angle);
       double startY = -200.0 + radius * sin(angle);
       return Vector(startX, startY, m_config.uavAltitude);
   }
   ```

3. **Refactor `InstallRadios()` (lines 115-135):**
   - Keep ground radio installation exactly the same (lines 131)
   - Split UAV radio installation into new method: `InstallUavRadios();`
   - Call both in `Build()`

4. **Add new method `InstallUavRadios()` (after InstallRadios):**
   ```cpp
   void WsnNetworkHelper::InstallUavRadios() {
       wsn::Cc2420Helper cc2420;
       auto channel = cc2420.CreateChannel();
       
       // Configure (same as current code)
       cc2420.SetPhyAttribute("TxPower", DoubleValue(params::TX_POWER_DBM));
       // ... other attributes ...
       
       // Install on each UAV
       for (uint32_t i = 0; i < m_uavNodes.GetN(); i++) {
           auto dev = cc2420.Install(NodeContainer(m_uavNodes.Get(i)));
           m_uavDevices[i] = dev;
       }
   }
   ```

5. **Refactor `InstallApplications()` (lines 212-299):**
   - Keep ground app installation loop exactly the same
   - Replace UAV app installation with call to: `InstallUavApplications();`
   - Only move UAV-related code (lines 213-257)

6. **Add new method `InstallUavApplications()` (after InstallApplications):**
   ```cpp
   void WsnNetworkHelper::InstallUavApplications() {
       for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
           // For each UAV: create app, configure, wire callbacks
           // All UAVs carry same fragments (Scenario 1 baseline)
           // See PHASE0_REFACTORING_PLAN.md for full details
       }
   }
   ```

7. **Update `PlanTrajectory()` → `ScheduleUavFlights()` (lines 175-206):**
   - Rename method: `PlanTrajectory()` → `ScheduleUavFlights()`
   - For each UAV, compute trajectory using TrajectoryHelper
   - Store in `m_uavWaypoints[uavId]`
   - Track in `m_results.uavPathLengths[uavId]`

8. **Update `Schedule()` (lines 305-346):**
   - Loop over all UAVs
   - Call `ScheduleUavFlights()` instead of `PlanTrajectory()`
   - Add waypoints to each UAV's WaypointMobilityModel

9. **Update `Build()` (lines 68-81) to call new methods:**
   ```cpp
   void WsnNetworkHelper::Build() {
       CreateNodes();
       CreateUavNodes(m_config.numUavs);    // NEW
       InstallRadios();
       InstallUavRadios();                   // NEW
       BuildTopology();
       SelectCandidatesAndFragments();
       ScheduleUavFlights();                 // RENAMED
       InstallApplications();
       InstallUavApplications();             // NEW
   }
   ```

10. **Update callback `OnUavNodeMacIndication()` signature:**
    - Add `uint32_t uavId` parameter
    - Route to correct UAV app using `m_uavApps[uavId]`

### Constraints

- ✅ Keep exact same logic for ground nodes (no changes)
- ✅ Scenario 1 (1 UAV) produces identical results
- ✅ All UAVs carry same fragments (Scenario 1 constraint)
- ✅ Use maps: `m_uavWaypoints[uavId]`, `m_uavApps[uavId]`, etc.
- ❌ Don't change physics/detection logic
- ❌ Don't change parameters.h constants
- ✅ Add `#include <cmath>` if not present (for sin/cos)

### Testing

After Task 4 (validation), run:
```bash
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=refactor-test"
# Compare metrics.csv with original:
# Detection time, path length should be identical
```

---

## Prompt 3: Result Metrics Refactoring

**Agent Type:** Data processing specialist  
**Files:** `src/wsn-uav/helper/result-writer.cc`  
**Task Duration:** 3-4 hours  
**Depends On:** Task 1 (data structures ready)

### Context

You're updating the results output to track per-UAV metrics. Currently the code assumes single UAV and outputs single `uavPathLength`. You need to modify ResultWriter to:
- Output per-UAV path lengths
- Output total UAV path length
- Output new coordination metrics
- Maintain readability

### Your Task

Modify `src/wsn-uav/helper/result-writer.cc` method `WriteMetrics()`:

**Current Output (metrics.csv):**
```
metric,value
detected,false
detection_time_seconds,-1
uav_path_length_meters,664.694  ← SINGULAR
cooperation_gain,0
```

**New Output (metrics.csv):**
```
metric,value
detected,false
detection_time_seconds,-1
uav_count,2                           ← NEW
uav_0_path_length_meters,664.694     ← PER-UAV
uav_1_path_length_meters,580.340     ← PER-UAV
total_uav_path_length_meters,1245.03 ← NEW SUM
cooperation_overlap_ratio,0.05        ← NEW
cooperation_gain,0
```

**Specific Changes:**

1. **Update WriteMetrics() function (find in result-writer.cc):**
   - After existing detection/time metrics, add UAV section
   - Loop: `for (const auto& [uavId, pathLen] : r.uavPathLengths)`
   - Output per-UAV metric with UAV ID in name
   - Output total sum

2. **Format:** Each line is `metric_name,value`
   - Use consistent naming: `uav_N_path_length_meters`
   - Keep other metrics unchanged (backward compat)

3. **Add to SimulationResults tracking:**
   - Already added in Task 1, but verify metrics match:
     - `uavPathLengths` map
     - `totalUavPathLength` field
     - `cooperationOverlapRatio` field

4. **Verify CSV parsing still works:**
   - Old code that reads `uav_path_length_meters` will not find it
   - But that's OK - new code will read per-UAV metrics
   - Scenario 1 validation (Task 4) will verify this

### Constraints

- ✅ Keep all other metrics unchanged
- ✅ Maintain CSV format (metric,value pairs)
- ✅ Use consistent naming convention
- ❌ Don't change trajectory/packet CSV files yet
- ✅ Document new metric meanings in comments

### Notes

- `SimulationResults` struct already has `uavPathLengths` map (from Task 1)
- Just need to write it out properly
- Scenario 1 validation will verify format is correct

---

## Prompt 4: Scenario 1 Validation & Testing

**Agent Type:** Testing & validation specialist  
**Files:** Multiple (testing/verification only)  
**Task Duration:** 2-3 hours  
**Depends On:** Tasks 1, 2, 3 (all changes merged)

### Context

You're validating that the refactored code produces identical results to the original for Scenario 1 (single UAV). This is critical - we promised 100% backward compatibility. You need to:
1. Build the refactored code
2. Run Scenario 1 with same parameters as baseline
3. Compare metrics and ensure identical results (except for CSV format)
4. Document any discrepancies

### Your Task

Execute validation tests:

**Step 1: Build**
```bash
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46
./ns3 clean
./ns3 configure --enable-examples --enable-modules=wsn-uav
./ns3 build 2>&1 | tee build.log
# Check for errors (not warnings)
grep -i "error:" build.log
```

**Expected:** Clean build, no errors

**Step 2: Run Baseline Test**

Run with same parameters as Session 7 tests:

```bash
# Test 1: seed=1, gridSize=10
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=refactor-v1" 2>&1 | tee run1.log

# Test 2: seed=10, gridSize=10
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=10 --runId=refactor-v2" 2>&1 | tee run2.log

# Test 3: different grid
./ns3 run "scenario-1-single-uav --gridSize=20 --seed=5 --runId=refactor-v3" 2>&1 | tee run3.log
```

**Expected:** Simulations complete without errors

**Step 3: Validation**

Compare metrics with Session 7 baseline:

```bash
# Session 7 results:
# seed=1: Tdetect=-1s (no detection), pathLength=664.69m
# seed=10: Tdetect=18.8s, pathLength=780.35m

# Compare new results:
cat src/wsn-uav/results/scenario-1/run-refactor-v1/metrics.csv
# Should have:
# - same detected value (true/false)
# - same detection_time_seconds
# - same total_uav_path_length_meters (was uav_path_length_meters)

cat src/wsn-uav/results/scenario-1/run-refactor-v2/metrics.csv
# Should have: detected=true, detection_time~18.8s
```

**Step 4: Detailed Comparison**

Create a comparison table in document:

| Metric | Seed=1 Original | Seed=1 Refactored | Match? |
|--------|-----------------|-------------------|--------|
| Detected | false | false | ✅ |
| Tdetect | -1 | -1 | ✅ |
| Total UAV Path | 664.69 | 664.69 | ✅ |

**Step 5: Log Analysis**

Check logs for any warnings about multiple UAVs or unexpected behavior:
```bash
grep -i "uav\|error\|warning" run1.log | head -20
```

**Expected:** No UAV-related warnings (system handles 1 UAV correctly)

**Step 6: Documentation**

Create validation report:
```
VALIDATION REPORT: Phase 0 Refactoring
======================================
Date: 2026-05-02
Refactoring Commit: [hash]

TESTS PASSED:
✅ Build: Clean, no errors
✅ Seed=1, gridSize=10: Identical metrics
✅ Seed=10, gridSize=10: Identical metrics
✅ Seed=5, gridSize=20: Identical metrics

BACKWARD COMPATIBILITY: 100%

METRICS FORMAT CHANGE:
  OLD: uav_path_length_meters,664.69
  NEW: total_uav_path_length_meters,664.69
       uav_0_path_length_meters,664.69
       uav_count,1

Notes:
- Single UAV case (numUavs=1) works identically
- CSV format changed but values identical
- Ready for Multi-UAV design
```

### Constraints

- ✅ Run with default config (Scenario 1 only, numUavs=1)
- ✅ Use same seed/gridSize parameters as Session 7
- ✅ Check exact numeric values (path length, detection time)
- ✅ Verify no hidden errors in logs
- ❌ Don't try multi-UAV testing yet (Task done when numUavs=1 works)

### Success Criteria

All tests pass with identical results:
- Detection outcomes match
- Path lengths match (within floating point tolerance)
- No errors or warnings in logs
- Code compiles cleanly

---

## Prompt 5: Build System & Documentation

**Agent Type:** Documentation & build specialist  
**Files:** `CLAUDE.md`, `README.md`, `CMakeLists.txt`  
**Task Duration:** 2-3 hours  
**Depends On:** Task 4 (validation passes)

### Context

You're finalizing Phase 0 by updating documentation and build configuration. The code changes are complete and validated, so you need to:
1. Create CLAUDE.md project guidelines
2. Update README with Phase 0 completion note
3. Update any build-related docs
4. Document the CSV format change

### Your Task

1. **Create CLAUDE.md** in project root:

```markdown
# WSN-UAV Project: Claude Code Guidelines

## Project Structure
- `src/wsn-uav/`: Core module (only modify this directory)
- `examples/`: Scenario entry points
- `helper/`: Network helpers (topology, trajectory, results)
- `models/`: Application logic, physics models
- `tests/`: (To be implemented in Phase 1)

## Architecture (Post-Phase 0)

### Multi-UAV Support
- WsnNetworkHelper supports N UAVs via NodeContainer
- Data structures use std::map<uint32_t, T> for per-UAV tracking
- Scenario 1: single UAV (backward compatible)
- Scenario 2+: multiple UAVs (future)

### Current Constraints
1. **Single-UAV only:** Use Scenario 1 entry point
2. **All UAVs carry same fragments:** No load balancing yet
3. **Python 3.13.x required:** (Not 3.14+ - NS-3 issue)
4. **Gridimport-based network:** Fixed grid topology

## Key Files

| File | Purpose |
|------|---------|
| `helper/wsn-network-helper.h` | Orchestrator (Phase 0 refactored) |
| `models/application/fragment-dissemination-app.h` | Core protocol |
| `helper/trajectory-helper.h` | UAV path planning (GMC algorithm) |
| `models/common/parameters.h` | Constants (no changes needed) |

## Important Notes

### Backward Compatibility
- Phase 0 refactoring maintains 100% compatibility
- Scenario 1 produces identical results
- CSV metrics format slightly changed (per-UAV tracking)

### Next Phase (Multi-UAV - Phase 1)
Before implementing Phase 1:
- Read ARCHITECTURE_AUDIT.md
- Understand current single-UAV design
- Plan UAV coordination protocol

## Build Commands

```bash
# Configure
./ns3 configure --enable-examples --enable-modules=wsn-uav

# Build
./ns3 build

# Run Scenario 1
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"

# View results
open src/wsn-uav/results/scenario-1/run-001/wsn-uav-result.html
```
```

2. **Update docs/README.md:**

Add at top:
```markdown
## 📋 Project Status

### ✅ Phase 0: Foundation Refactoring - COMPLETE
- Generalized WsnNetworkHelper for N UAVs
- Maintained 100% backward compatibility
- Scenario 1 produces identical results
- Ready for Phase 1 (Multi-UAV design)

**Changes since Phase 0:**
- CSV metrics format updated (now includes per-UAV path lengths)
- No API changes for Scenario 1 users
- Internal data structures now multi-UAV capable
```

3. **Document CSV format change:**

Create `docs/METRICS_FORMAT.md`:
```markdown
# Simulation Metrics Format

## Session 7 and Earlier (Single-UAV)
```
metric,value
detected,false
detection_time_seconds,-1
uav_path_length_meters,664.69
cooperation_gain,0
```

## Phase 0 and Later (Multi-UAV Ready)
```
metric,value
detected,false
detection_time_seconds,-1
uav_count,1
uav_0_path_length_meters,664.69
total_uav_path_length_meters,664.69
cooperation_overlap_ratio,0.0
cooperation_gain,0
```

### Migration Notes
- Old scripts reading `uav_path_length_meters` will fail
- Use `total_uav_path_length_meters` instead
- For single UAV: `total` = `uav_0` value
```

4. **Check CMakeLists.txt:**

Should already be correct (no changes needed). Verify:
```bash
cat src/wsn-uav/CMakeLists.txt | grep -A5 "SOURCE_FILES"
# Should list all .cc files
```

5. **Verify No Breaking Changes:**

List all user-facing API changes:
- ❌ No changes to SimulationConfig (just added fields)
- ❌ No changes to main() in scenario-1-single-uav.cc
- ✅ CSV metrics format changed (documented above)
- ✅ Backward compatible with numUavs=1 default

### Constraints

- ✅ Document clearly for future developers
- ✅ Make Phase 0 completion obvious
- ✅ Explain CSV format change
- ✅ Keep it concise (not over-document)
- ❌ Don't change code (only Task 1-4 do that)

### Deliverables

1. CLAUDE.md created
2. README.md updated with Phase 0 note
3. METRICS_FORMAT.md created
4. All docs committed

---

## Parallel Execution Note

**These tasks can run in parallel after Task 1 completes:**
- Task 1: Data structures (must be first)
- Then in parallel:
  - Task 2: Helper methods
  - Task 3: Result metrics
  - Task 5: Documentation (after Task 4 validates)
- Task 4: Validation (needs all code merged)

**Recommended parallel groups:**
- Group A: Tasks 2, 3 (implementation)
- Group B: Task 5 (docs, after Task 4)
- Sequential: 1 → [2, 3 parallel] → 4 → 5

**Total time:** ~16 hours compressed to 8-10 hours with parallel work

