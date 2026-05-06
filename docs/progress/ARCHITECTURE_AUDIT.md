# Architecture Audit Report

**Date:** 2026-05-02  
**Scope:** Current project structure for Multi-UAV readiness assessment  
**Status:** 🔴 **Multiple significant issues identified**

---

## Executive Summary

Current architecture is **single-UAV optimized** with **tight coupling** that will create major refactoring work when scaling to Multi-UAV. Many skeleton files exist for future scenarios but were never completed.

**Critical Issues:**
- ❌ WsnNetworkHelper hardcoded for single UAV (`m_uavNode` singular)
- ❌ Scenario-specific logic mixed with generic helpers
- ❌ Parameter system lacks multi-UAV support
- ❌ Result collection assumes single UAV
- ⚠️ 40+ skeleton files (empty) for unimplemented features

---

## 1. Core Architecture Issues

### A. WsnNetworkHelper - Single UAV Assumption

**File:** `helper/wsn-network-helper.h:h:90-157`

**Problems:**
```cpp
private:
    Ptr<Node> m_uavNode;              // ❌ SINGULAR - not a container
    NetDeviceContainer m_uavDevices;  // Could be multi-UAV but no logic
    Ptr<WsnUavMac> m_uavMac;          // ❌ SINGULAR
    std::vector<Waypoint> m_uavWaypoints;  // ❌ SINGULAR trajectory
```

**Impact:**
- Cannot easily extend to multiple UAVs
- Would need restructure: `m_uavNode` → `NodeContainer m_uavNodes`
- All waypoint planning assumes 1 UAV
- Callbacks wired only for one UAV

**Multi-UAV would require:**
```cpp
// Instead of:
Ptr<Node> m_uavNode;
std::vector<Waypoint> m_uavWaypoints;

// Need:
NodeContainer m_uavNodes;
std::map<uint32_t, std::vector<Waypoint>> m_uavWaypoints;  // per-UAV
```

### B. Scenario-Specific Logic Hardcoded

**File:** `helper/wsn-network-helper.cc:97-108` (CreateNodes)

```cpp
// Start 200m south of network (negative Y)
Vector initialUavPos(centerX, -200.0, m_config.uavAltitude);
```

**Problems:**
- UAV starting position hardcoded
- Distance 200m hardcoded
- Only works for grid-based scenarios
- Non-reusable for other topologies

**Similar Issues:**
- Line 189-196: GMC trajectory planning assumes single UAV can cover candidates
- Line 268: Detection node selection assumes single UAV
- Line 315-323: Waypoint scheduling only handles one UAV

### C. Parameter System Lacks Multi-UAV

**File:** `helper/wsn-network-helper.h:33-66` (SimulationConfig)

```cpp
struct SimulationConfig {
    uint32_t numUavs = 1;  // ⚠️ Field exists but NEVER USED
    
    // ... no UAV array parameters:
    // - Starting positions per UAV
    // - Trajectories per UAV
    // - Payloads per UAV
    // - Energy budgets per UAV
    // - Communication ranges per UAV
```

**Validation:**
- `Validate()` (line 22-48) **doesn't validate numUavs**
- No constraints on numUavs range
- No per-UAV configuration possible

---

## 2. Code Coupling & Reusability

### A. FragmentDisseminationApp - Role-Based But Tight

**File:** `models/application/fragment-dissemination-app.h:80-88`

```cpp
enum class Role { UAV_BROADCASTER, GROUND_NODE };

// Single app handles both roles in one class
// Works for 1 UAV, but for N UAVs:
// - Need different behavior per UAV (if they have different payloads)
// - Coordination between UAVs not supported
// - Inter-UAV communication channels not defined
```

**Issue:** No abstraction for multi-UAV coordination
- UAVs can't exchange state or coordinate coverage
- No inter-UAV packet types defined
- No UAV leader election / consensus mechanism

### B. Scenario-Specific Glue Code

**File:** `examples/scenario-1-single-uav.cc:44-199`

**Problems:**
- Scenario 1 is **only scenario compiled**
- Parameter defaults hardcoded in main()
- Output path has "scenario-1" hardcoded
- No generic scenario launcher
- No abstraction to support Scenario 2, 3, 4 (which exist as empty files)

**Consequence:**
- Each scenario needs separate entry point
- Code duplication across scenario files
- No scenario inheritance or composition

### C. Result Collection - Single UAV Metrics

**File:** `helper/wsn-network-helper.h:72-84` (SimulationResults)

```cpp
struct SimulationResults {
    double uavPathLength = 0.0;    // ❌ SINGULAR
    // Missing:
    // - Array of path lengths (one per UAV)
    // - Coordination metrics (overlap, coverage duplication)
    // - Load distribution (which nodes each UAV served)
    // - Multi-UAV efficiency (cooperative vs. solo)
};
```

---

## 3. Skeleton Files (Dead Code)

**40+ files exist but are empty:**

### Examples (not built):
- `examples/scenario-2-multi-uav-2.cc` (0 lines)
- `examples/scenario-3-large-network.cc` (0 lines)
- `examples/scenario-4-robustness.cc` (0 lines)
- `examples/tutorial-basic.cc` (0 lines)
- `examples/advanced-*.cc` (2 files, 0 lines)

### Helpers (not built, not in CMakeLists):
- `helper/configuration-helper.h` (0 lines)
- `helper/scenario-builder.h` (0 lines)

### Models (not built):
- **Energy Models** (6 files, 0 lines):
  - `models/energy/node-energy-model.h`
  - `models/energy/uav-battery-model.h`
  - `models/energy/power-profile.h`
  - `models/energy/energy-utils.h`

- **Mobility Models** (5 files, 0 lines):
  - `models/mobility/realistic-uav-mobility.h`
  - `models/mobility/simple-uav-mobility.h`
  - `models/mobility/sixdof-uav-mobility.h`
  - `models/mobility/collision-avoidance.h`
  - `models/mobility/trajectory-generator.h`

- **Propagation Models** (6 files, 0 lines):
  - `models/propagation/a2g-channel-model.h`
  - `models/propagation/path-loss-model.h`
  - `models/propagation/fading-model.h`
  - `models/propagation/doppler-calculator.h`
  - `models/propagation/shadowing-model.h`
  - `models/propagation/channel-utils.h`

- **PHY/Reception Models** (4 files, 0 lines):
  - `models/phy/error-model.h`
  - `models/phy/modulation-model.h`
  - `models/phy/packet-reception-model.h`
  - `models/phy/reception-utils.h`

- **Coordination/Protocol Models** (3 files, 0 lines):
  - `models/application/broadcast-protocol.h`
  - `models/application/cooperation-protocol.h`
  - `models/common/contact-window.h`
  - `models/common/configuration-manager.h`

### Tests (not built):
- **Integration tests** (3 files, 0 lines)
- **Regression tests** (3 files, 0 lines)
- **Unit tests** (5 files, 0 lines)

**Implication:** Someone designed file structure but never implemented. This is a **good skeleton** to build on, but needs implementation.

---

## 4. Missing Components for Multi-UAV

### Not Implemented:
1. ❌ **UAV Coordination Protocol** - How do UAVs decide who covers what?
2. ❌ **Load Balancing** - Distribute fragments fairly across UAVs
3. ❌ **Energy Management** - Battery constraints per UAV
4. ❌ **Collision Avoidance** - Physical UAVs can't occupy same space
5. ❌ **Realistic Mobility** - Waypoint-based is too simple
6. ❌ **Inter-UAV Communication** - UAVs need to talk to each other
7. ❌ **Coverage Coordination** - Avoid redundant broadcasts
8. ❌ **Failure Handling** - What if one UAV goes offline?

---

## 5. Parameter Hardcoding

**Critical parameters embedded in code:**

| Parameter | Location | Issue |
|-----------|----------|-------|
| UAV starting position `(-200, 0, alt)` | wsn-network-helper.cc:102 | Only works for grid |
| Number of UAVs = 1 | WsnNetworkHelper.cc:92 | No loop over m_uavNodes |
| Packet drop callback | wsn-network-helper.cc:290 | Wired only for one UAV |
| Detection algorithm | fragment-dissemination-app.cc:244 | Single target node |
| Trajectory planning | trajectory-helper.cc | Assumes single coverage agent |

---

## 6. Build System Issues

**CMakeLists.txt only includes Scenario 1:**
```cmake
# Only builds scenario-1-single-uav.cc
# Other scenario .cc files not listed
```

**Consequence:**
- Can't build/test other scenarios without manual editing
- No build variants (scenario1, scenario2, etc.)
- No test suite wiring

---

## Summary: Technical Debt

| Issue | Severity | Effort to Fix | When |
|-------|----------|---------------|------|
| Single UAV assumptions | 🔴 HIGH | 2-3 days | **Before Multi-UAV** |
| Scenario-specific hardcoding | 🔴 HIGH | 2-3 days | **Before Multi-UAV** |
| Parameter system needs multi-UAV | 🟡 MEDIUM | 1-2 days | **Before or with Multi-UAV** |
| Result metrics | 🟡 MEDIUM | 1 day | **Before or with Multi-UAV** |
| Empty skeleton files cleanup | 🟢 LOW | 0.5 days | **During implementation** |
| Build system generalization | 🟡 MEDIUM | 1 day | **With scenario framework** |
| Test suite creation | 🟡 MEDIUM | 2-3 days | **Ongoing** |

---

## Recommendations

### **Phase 0: Refactor (Before Multi-UAV)**
1. ✏️ Genericize WsnNetworkHelper:
   - `m_uavNode` → `m_uavNodes` (NodeContainer)
   - `m_uavWaypoints` → `m_uavWaypoints` (map per UAV)
   - `InstallUavApp()` → loop over all UAVs

2. ✏️ Extract scenario logic:
   - Create ScenarioBuilder interface
   - Implement GridBasedScenario
   - Make parameters less hardcoded

3. ✏️ Extend SimulationResults:
   - Per-UAV metrics
   - Coordination metrics
   - Coverage analysis

4. ✏️ Generalize parameters:
   - Remove hardcoded positions
   - Add scenario-specific defaults
   - Support per-UAV configuration

### **Phase 1: Foundation (For Multi-UAV)**
1. Implement UAV coordination protocol
2. Add inter-UAV communication channels
3. Implement basic load balancing
4. Extend trajectory planning for multiple UAVs

### **Phase 2: Advanced (Optional but planned)**
1. Energy models (UAV batteries, power profiles)
2. Realistic mobility models (6-DOF, collision avoidance)
3. Advanced propagation (A2G channels, fading, shadowing)
4. Failure handling & recovery

---

## Conclusion

**Current state:** ✅ Good foundation (Session 1-7 works well)

**For Multi-UAV:** ⚠️ Needs significant refactoring

**Recommended approach:**
1. **Do Phase 0 refactoring first** (2-3 days)
2. Then design Multi-UAV architecture on solid foundation
3. Use skeleton files as implementation roadmap

**Not recommended:** Jump to Multi-UAV without refactoring → will require rework of entire helper layer

