# Phase 1: Multi-UAV Cooperative Architecture Design

**Date:** 2026-05-05  
**Focus:** Refactor from spatial partitioning → cooperative coverage with size-based load balancing  
**Status:** 📋 Design Phase (Ready for Implementation)

---

## 🎯 Vision Statement

**From:** UAVs divide network into separate regions (no cooperation)  
**To:** UAVs cover different regions optimally, but all fragment reach all nodes through cooperation

```
Current (Bad):
  UAV0 → Region A only
  UAV1 → Region B only
  UAV2 → Region C only
  Result: Node in Region A never hears UAV1 or UAV2 ❌

Desired (Good):
  UAV0 → Optimized path through mixed regions (carries heavy fragments, slower)
  UAV1 → Optimized path through mixed regions (carries medium fragments, medium speed)
  UAV2 → Optimized path through mixed regions (carries light fragments, faster)
  
  Region A sees:
    t=0s: UAV2 arrives, broadcasts light fragments {light}
    t=2s: UAV1 arrives, broadcasts medium fragments {medium}
    t=5s: UAV0 arrives, broadcasts heavy fragments {heavy}
    
    Result: Node_A has {light, medium, heavy} = COMPLETE ✅

  Region B sees:
    t=1s: UAV0 arrives, broadcasts heavy fragments {heavy}
    t=3s: UAV2 arrives, broadcasts light fragments {light}
    t=6s: UAV1 arrives, broadcasts medium fragments {medium}
    
    Result: Node_B has {heavy, light, medium} = COMPLETE ✅
```

---

## 🏗️ Architecture Changes Required

### Layer 1: Fragment Generation & Distribution

#### 1.1 Fragment Model: Support Variable Sizes
**File:** `models/application/fragment-model.h/.cc`

**Current State:**
```cpp
struct Fragment {
    uint32_t id;
    double evidence;
    uint32_t sizeBytes = 0;  // ← Present but not used
    std::vector<uint8_t> data;
};

// GenerateWithSizes() declared but NOT implemented
```

**Required Changes:**
```cpp
// 1. Implement GenerateWithSizes() in fragment-model.cc
static FragmentCollection GenerateWithSizes(
    uint32_t count,
    uint32_t minSizeBytes,    // e.g., 100
    uint32_t maxSizeBytes,    // e.g., 20000
    uint32_t seed,
    double masterConfidence = 0.90);

// 2. Algorithm:
//    - Generate K fragments with random sizeBytes in [min, max]
//    - Each fragment.data[] sized = sizeBytes
//    - Sort descending by sizeBytes
//    - Result: Fragment[0] = largest, Fragment[K-1] = smallest
```

**Implementation Notes:**
- Fragments interleaved over 416×416×3 pixel image (preserve evidence calculation)
- sizeBytes randomly assigned in range, preserving evidence distribution
- Sorted descending: [largest → smallest]

---

### Layer 2: UAV Fragment Assignment

#### 2.1 Fragment Distribution by Size
**File:** `helper/wsn-network-helper.cc` → `DistributeFragmentsToUavs()`

**Current State:**
```cpp
void DistributeFragmentsToUavs() {
    // All UAVs get all fragments (no load balancing)
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        m_uavFragments[uavId] = m_fragments;  // ← All same
    }
}
```

**Required Changes:**
```cpp
void DistributeFragmentsToUavs() {
    uint32_t numUavs = m_config.numUavs;
    auto allFragIds = m_fragments.GetIds();  // Sorted by size (large→small)
    uint32_t total = allFragIds.size();
    
    if (total == 0 || numUavs == 0) return;
    
    // Distribute fragments by size to UAVs
    // UAV[0] gets largest, UAV[N-1] gets smallest
    std::vector<std::vector<uint32_t>> uavFragmentSets(numUavs);
    
    for (uint32_t i = 0; i < total; i++) {
        uint32_t uavId = i % numUavs;  // Round-robin by fragment order
        uavFragmentSets[uavId].push_back(allFragIds[i]);
    }
    
    // Assign to UAVs
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        FragmentCollection uavFrags;
        for (uint32_t fragId : uavFragmentSets[uavId]) {
            const Fragment* frag = m_fragments.Get(fragId);
            if (frag) {
                uavFrags.Add(*frag);
            }
        }
        m_uavFragments[uavId] = uavFrags;
        m_results.uavFragmentIds[uavId] = uavFragmentSets[uavId];
        
        // Log UAV assignment
        uint32_t totalSize = 0;
        for (auto fid : uavFragmentSets[uavId]) {
            const Fragment* f = m_fragments.Get(fid);
            if (f) totalSize += f->sizeBytes;
        }
        NS_LOG_INFO("UAV " << uavId << " assigned " << uavFragmentSets[uavId].size() 
                           << " fragments, total size: " << totalSize << " bytes");
    }
}
```

**Distribution Pattern:**
```
Example: 10 fragments sorted by size, 3 UAVs

AllFragments (sorted descending): [F0:20KB, F1:18KB, F2:15KB, F3:2KB, F4:100B, ...]
                                   ^^^^^^ Heavy          ^^^^^^ Light

UAV0 gets: F0(20KB), F3(2KB), F6(...)   ← Mix of sizes, but heavier on avg
UAV1 gets: F1(18KB), F4(100B), F7(...)  ← Mix of sizes
UAV2 gets: F2(15KB), F5(...), F8(...)   ← Mix of sizes, but lighter on avg

Total load per UAV:
  UAV0 ≈ ~45% of total bytes
  UAV1 ≈ ~35% of total bytes
  UAV2 ≈ ~20% of total bytes
```

---

### Layer 3: UAV Speed Adjustment

#### 3.1 Speed Based on Fragment Load
**File:** `examples/scenario-3-load-balanced-fragments.cc` (or helper)

**Add to SimulationConfig:**
```cpp
struct SimulationConfig {
    // ... existing fields ...
    
    // Size-based UAV speed adjustment
    bool useLoadBasedSpeed = true;     // Enable speed adjustment
    double baseUavSpeed = 20.0;        // m/s (default)
    double minSpeedFactor = 0.6;       // Min speed = 60% of baseSpeed
    double maxSpeedFactor = 1.0;       // Max speed = 100% of baseSpeed
};
```

**Implementation in helper:**
```cpp
void WsnNetworkHelper::AdjustUavSpeedByLoad() {
    uint32_t numUavs = m_config.numUavs;
    
    if (!m_config.useLoadBasedSpeed || numUavs == 0) {
        return;  // Use base speed for all
    }
    
    // Calculate total bytes per UAV
    std::vector<uint32_t> uavTotalBytes(numUavs, 0);
    uint32_t globalMaxBytes = 0;
    
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        const auto& fragIds = m_results.uavFragmentIds[uavId];
        for (uint32_t fragId : fragIds) {
            const Fragment* frag = m_fragments.Get(fragId);
            if (frag) {
                uavTotalBytes[uavId] += frag->sizeBytes;
                globalMaxBytes = std::max(globalMaxBytes, uavTotalBytes[uavId]);
            }
        }
    }
    
    // Adjust speeds: heavier UAVs slower, lighter UAVs faster
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        double loadFactor = (globalMaxBytes > 0) ? 
            (double)uavTotalBytes[uavId] / globalMaxBytes : 0.5;
        
        // Speed = base * (max - (max-min)*loadFactor)
        double speedFactor = m_config.maxSpeedFactor - 
            (m_config.maxSpeedFactor - m_config.minSpeedFactor) * loadFactor;
        
        double adjustedSpeed = m_config.uavSpeed * speedFactor;
        
        // TODO: Store adjusted speed per UAV
        // m_uavSpeeds[uavId] = adjustedSpeed;
        
        NS_LOG_INFO("UAV " << uavId << " load: " << uavTotalBytes[uavId] 
                           << " bytes, speed factor: " << speedFactor 
                           << ", adjusted speed: " << adjustedSpeed << " m/s");
    }
}
```

**Call in Build():**
```cpp
void WsnNetworkHelper::Build() {
    // ... existing code ...
    SelectCandidatesAndFragments();
    DistributeFragmentsToUavs();      // ← NEW: Distribute by size
    AdjustUavSpeedByLoad();           // ← NEW: Adjust speeds
    PlanTrajectory();                 // ← Uses adjusted speeds
    // ... rest of build ...
}
```

---

### Layer 4: Trajectory Planning - Independent Optimization

#### 4.1 GMC Per-UAV with Own Trajectory
**File:** `helper/wsn-network-helper.cc` → `ScheduleUavFlights()`

**Current Problem:**
```cpp
// CURRENT: Strip-based partitioning
std::vector<std::set<uint32_t>> partitionedCandidates(numUavs);
if (numUavs > 1) {
    // Divide candidates by X coordinate into strips
    for (uint32_t nodeId : m_candidateNodes) {
        double nx = node->GetObject<MobilityModel>()->GetPosition().x;
        uint32_t strip = (uint32_t)(nx / stripW);
        partitionedCandidates[strip].insert(nodeId);  // ← WRONG: Spatial partition
    }
}
```

**Required Changes:**
```cpp
void WsnNetworkHelper::ScheduleUavFlights() {
    uint32_t numUavs = m_uavNodes.GetN();
    
    if (numUavs == 1) {
        // Single UAV: visit all candidates
        PlanGmcTrajectory(0, m_candidateNodes, m_config.uavSpeed);
        return;
    }
    
    // Multi-UAV: Each UAV optimizes its own trajectory
    // Strategy: Distribute candidates evenly, let each UAV plan independently
    
    std::vector<std::set<uint32_t>> uavTargets(numUavs);
    
    // Method 1: Geographic clustering (better coverage)
    // Divide candidates by proximity to starting positions
    for (uint32_t nodeId : m_candidateNodes) {
        Vector nodePos = m_groundNodes.Get(nodeId)->GetObject<MobilityModel>()->GetPosition();
        
        // Find closest UAV starting position
        uint32_t bestUav = 0;
        double minDist = std::numeric_limits<double>::max();
        
        for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
            Vector uavPos = m_uavNodes.Get(uavId)->GetObject<MobilityModel>()->GetPosition();
            double dist = (nodePos - uavPos).GetLength();
            if (dist < minDist) {
                minDist = dist;
                bestUav = uavId;
            }
        }
        
        uavTargets[bestUav].insert(nodeId);
    }
    
    // Method 2 (Alternative): Load balancing by fragment count
    // Distribute candidates such that each UAV visits ~equal number
    // uint32_t nodesPerUav = m_candidateNodes.size() / numUavs;
    // ... distribute evenly ...
    
    // Plan trajectory for each UAV independently
    for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
        if (uavTargets[uavId].empty()) {
            NS_LOG_WARN("UAV " << uavId << " has no target nodes");
            continue;
        }
        
        Vector startPos = m_uavNodes.Get(uavId)->GetObject<MobilityModel>()->GetPosition();
        double adjustedSpeed = m_config.uavSpeed;  // TODO: Use m_uavSpeeds[uavId]
        
        // GMC planning for this UAV's targets
        std::vector<Waypoint> waypoints = TrajectoryHelper::PlanGmc(
            uavTargets[uavId],
            m_groundNodes,
            m_cellInfo.nodeToCell,
            startPos,
            adjustedSpeed,
            m_gmcConfig);
        
        m_uavWaypoints[uavId] = waypoints;
        double pathLen = TrajectoryHelper::ComputePathLength(waypoints, startPos);
        m_results.uavPathLengths[uavId] = pathLen;
        m_results.totalUavPathLength += pathLen;
        
        NS_LOG_INFO("UAV " << uavId << " trajectory: " << waypoints.size() 
                           << " waypoints, " << pathLen << "m distance, "
                           << uavTargets[uavId].size() << " target nodes");
    }
}
```

**Result:**
```
UAV0 (Heavy): 
  Targets: Nodes closest to its starting position
  Speed: Reduced (60-70% of base)
  Path: Optimized for its region + neighborhood
  Arrival: Latest (due to lower speed)

UAV1 (Medium):
  Targets: Different set of nodes
  Speed: Medium (80-90% of base)
  Path: Optimized for its region
  Arrival: Medium timing

UAV2 (Light):
  Targets: Remaining nodes
  Speed: Full (100% of base)
  Path: Optimized for its region
  Arrival: Fastest
```

---

### Layer 5: Cooperation & Fragment Dissemination

#### 5.1 Ground Node Cooperation (Unchanged from Phase 0)
**File:** `models/application/fragment-dissemination-app.cc`

**Already Implemented:**
- Ground nodes share fragments via manifest protocol
- Cooperative trigger at τ_coop confidence threshold
- Spreads fragments through network after initial UAV broadcasts

**Enhancement:** Better coordination
```cpp
// When node receives fragments from UAV, log it
void OnUavPacketReceived(...) {
    // Node learns fragments {fragIds} from UAV at time T
    // Schedules cooperation to fill gaps at time T + delay
    // Manifest shares what's missing
}
```

---

## 📊 Complete Data Flow

```
[Phase 0: Initialization]
  ├─ CreateUavNodes(3)
  │  └─ Position at starting points (can be same or different)
  │
  ├─ SelectCandidatesAndFragments()
  │  ├─ Generate K fragments with GenerateWithSizes()
  │  │  └─ Fragments[0]:20KB, Fragments[1]:18KB, ..., Fragments[9]:100B
  │  └─ Select suspicious nodes as candidates
  │
  └─ DistributeFragmentsToUavs()  [NEW]
     ├─ UAV0: {F0:20KB, F3:2KB, F6:...}   (heavy)
     ├─ UAV1: {F1:18KB, F4:100B, F7:...}  (medium)
     └─ UAV2: {F2:15KB, F5:..., F8:...}   (light)

[Phase 1: Speed Adjustment]
  └─ AdjustUavSpeedByLoad()  [NEW]
     ├─ UAV0: 20 m/s × 0.65 = 13 m/s   (heavy load)
     ├─ UAV1: 20 m/s × 0.85 = 17 m/s   (medium load)
     └─ UAV2: 20 m/s × 1.0 = 20 m/s    (light load)

[Phase 2: Trajectory Planning]
  └─ ScheduleUavFlights() [REFACTORED]
     ├─ UAV0: GMC({nodes near start}) → 40 waypoints, 800m
     ├─ UAV1: GMC({nodes near start}) → 35 waypoints, 700m
     └─ UAV2: GMC({nodes near start}) → 30 waypoints, 600m

[Phase 3: Broadcasting]
  ├─ t=0s: UAV2 starts at first waypoint
  │  └─ Broadcasts F2, F5, F8 to nearby nodes
  │
  ├─ t=2s: UAV1 reaches next waypoint
  │  └─ Broadcasts F1, F4, F7
  │
  ├─ t=5s: UAV0 reaches waypoint
  │  └─ Broadcasts F0, F3, F6
  │
  └─ Ground nodes in overlap zones receive from multiple UAVs
     └─ Nodes cooperate to fill gaps via manifest exchange

[Phase 4: Cooperation]
  └─ When node reaches τ_alert confidence
     ├─ Detection triggered ✅
     └─ Ground coop spreads remaining fragments
```

---

## 🔧 Implementation Sequence

### Step 1: Fragment Model (Days 1-2)
- [ ] Uncomment Fragment.sizeBytes field ✅ (already done)
- [ ] Implement GenerateWithSizes() in fragment-model.cc
- [ ] Test: Verify fragments have random sizeBytes, sorted descending
- [ ] Verify: Fragment confidence calculation still works with sized frags

### Step 2: Distribution Logic (Days 2-3)
- [ ] Implement DistributeFragmentsToUavs() with round-robin by size
- [ ] Track uavFragmentIds per UAV
- [ ] Track fragmentSizesBytes in results ✅ (already enabled)
- [ ] Test: Verify 3 UAVs get different fragment sets

### Step 3: Speed Adjustment (Days 3-4)
- [ ] Add useLoadBasedSpeed, minSpeedFactor, maxSpeedFactor to config
- [ ] Implement AdjustUavSpeedByLoad()
- [ ] Store adjusted speeds (m_uavSpeeds map)
- [ ] Test: Verify speed reduces proportionally to load

### Step 4: Trajectory Refactoring (Days 4-6)
- [ ] Replace strip-based partitioning with geographic clustering
- [ ] Each UAV plans GMC for its own targets
- [ ] Use adjusted speeds in TrajectoryHelper::PlanGmc()
- [ ] Test: Verify each UAV has different trajectory & coverage

### Step 5: Integration & Testing (Days 6-7)
- [ ] Build scenario-3 with new multi-UAV coop model
- [ ] Test small grid (5×5) first, then 10×10
- [ ] Verify detection times with 3 UAVs vs 1 UAV
- [ ] Compare coverage speed (should be faster with parallel UAVs)

### Step 6: Validation (Days 7-8)
- [ ] Run Scenario-1 (1 UAV) → should work identically
- [ ] Run Scenario-2 (2 UAVs) → should be faster than Scenario-1
- [ ] Run Scenario-3 (3 UAVs) → should be fastest
- [ ] Measure T_detect improvement

---

## 📈 Expected Outcomes

### Metrics to Track

| Metric | Scenario-1 (1 UAV) | Scenario-3 (3 UAVs) | Speedup |
|--------|-------------------|----------------------|---------|
| T_detect | ~20s | ~8-10s | 2-2.5× |
| Path length per UAV | 800m | 300m | - |
| Total path length | 800m | 900m | - |
| Coverage time | 800/20 = 40s | 900/(avg 16.7) ≈ 54s | - |
| Nodes with complete frags | ~15 | ~30 | 2× |
| Cooperation overlay | 20-30% | 50-60% | - |

---

## 🎯 Design Principles

1. **Independent Optimization**: Each UAV optimizes for its assigned targets
2. **Load Balancing**: Fragment size determines UAV load & speed naturally
3. **Parallel Coverage**: Multiple UAVs reduce detection time via concurrency
4. **Cooperation**: Ground nodes fill gaps via manifest protocol
5. **Backward Compatible**: Scenario-1 (1 UAV) unchanged

---

## 🔗 Dependencies

### Files to Modify
```
src/wsn-uav/
├── models/application/
│   ├── fragment-model.h          [LOW PRIORITY - mostly done]
│   └── fragment-model.cc         [HIGH: Implement GenerateWithSizes()]
├── helper/
│   ├── wsn-network-helper.h      [MEDIUM: Add AdjustUavSpeedByLoad() method]
│   ├── wsn-network-helper.cc     [HIGH: Refactor DistributeFragments + ScheduleFlight]
│   └── trajectory-helper.cc      [LOW: May need to use adjusted speeds]
└── examples/
    └── scenario-3-load-balanced-fragments.cc  [MEDIUM: Update config]
```

### Files NOT Changed
- `fragment-dissemination-app.cc` (cooperation already works)
- `topology-helper.cc` (cell structure unchanged)
- `result-writer.cc` (CSV format fine)

---

## 💾 Configuration Example

```bash
# Scenario-3: Cooperative Multi-UAV with Size-Based Load Balancing
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --numFragments=10 \
  --fragmentMinSizeBytes=100 \
  --fragmentMaxSizeBytes=20000 \
  --numUavs=3 \
  --useLoadBasedSpeed=true \
  --minSpeedFactor=0.6 \
  --maxSpeedFactor=1.0 \
  --useGmc=true \
  --seed=1 \
  --runId=1"
```

---

## ✅ Success Criteria

- [ ] Fragment generation with variable sizes
- [ ] Distribution: UAVs get different fragments by size
- [ ] Speed adjustment: Heavy UAVs slower, light UAVs faster
- [ ] Trajectory: Each UAV optimizes own path
- [ ] Detection: All nodes receive complete fragment set
- [ ] Performance: Faster detection with 3 UAVs vs 1 UAV
- [ ] Backward compat: Scenario-1 unchanged
- [ ] Build: No compilation errors
- [ ] Tests: Scenario-1 ✅, Scenario-3 ✅ (no crashes)

---

**Design Status:** ✅ Complete  
**Ready for:** Agent-based implementation  
**Estimated Effort:** 5-7 days  
**Complexity:** Medium (refactoring existing structures)

