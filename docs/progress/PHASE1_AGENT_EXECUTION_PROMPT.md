# Phase 1: Multi-UAV Cooperative Architecture - Agent Execution Prompt

**Created:** 2026-05-05  
**Status:** Ready for Agent Execution  
**Complexity:** Medium (refactoring 4 main areas)

---

## 🎯 Mission Brief

Transform the WSN-UAV simulator from spatial partition-based multi-UAV (where each UAV serves different regions) to cooperative multi-UAV with size-based load balancing (where all UAVs cooperate to serve all nodes, but with different fragment loads and speeds).

**Key Change:** Instead of dividing network by region, distribute fragments by size → lighter UAVs fly faster, heavier UAVs slower → all nodes receive all fragments with natural temporal staggering.

---

## 📋 Implementation Sequence

### TASK 1: Implement GenerateWithSizes() in Fragment Model
**Priority:** HIGH  
**Complexity:** Medium  
**Files:** `src/wsn-uav/models/application/fragment-model.cc`

#### What to do:
1. In `fragment-model.cc`, after the `Generate()` method, implement `GenerateWithSizes()`
   
2. Signature:
   ```cpp
   FragmentCollection FragmentCollection::GenerateWithSizes(
       uint32_t count,
       uint32_t minSizeBytes,
       uint32_t maxSizeBytes,
       uint32_t seed,
       double masterConfidence = 0.90)
   ```

3. Algorithm:
   - Use existing pixel-stride interleaving from `Generate()` for evidence calculation
   - Generate K fragments with random sizeBytes distributed in [minSizeBytes, maxSizeBytes]
   - Each fragment.data[] sized according to sizeBytes (not pixel-based)
   - **Sort descending by sizeBytes** (largest first)
   - Return FragmentCollection sorted by size

4. Implementation approach:
   - Reuse evidence generation from existing `Generate()`
   - For sizeBytes: Random number in [min, max] per fragment
   - Std::sort fragments by sizeBytes descending
   - Populate Fragment.sizeBytes field for each

5. Test:
   - Verify fragments sorted largest → smallest
   - Verify sizeBytes in correct range
   - Verify evidence still calculated correctly
   - Print log: "Generated K fragments, size range [min→max]"

#### Code Reference:
Look at existing `Generate()` implementation (fragment-model.cc, around line ~100) for evidence calculation pattern.

---

### TASK 2: Implement DistributeFragmentsToUavs() Refactoring
**Priority:** HIGH  
**Complexity:** Medium  
**Files:** `src/wsn-uav/helper/wsn-network-helper.cc`

#### What to do:
1. Find `DistributeFragmentsToUavs()` method (around line 209)

2. Replace current implementation with size-based round-robin:
   ```cpp
   void WsnNetworkHelper::DistributeFragmentsToUavs() {
       uint32_t numUavs = m_config.numUavs;
       auto allFragIds = m_fragments.GetIds();
       uint32_t total = allFragIds.size();
       
       if (total == 0 || numUavs == 0) return;
       
       // Round-robin distribute by position in sorted array
       std::vector<std::vector<uint32_t>> uavFragmentSets(numUavs);
       
       for (uint32_t i = 0; i < total; i++) {
           uint32_t uavId = i % numUavs;
           uavFragmentSets[uavId].push_back(allFragIds[i]);
       }
       
       // Assign to UAVs and track
       for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
           FragmentCollection uavFrags;
           uint32_t totalSize = 0;
           
           for (uint32_t fragId : uavFragmentSets[uavId]) {
               const Fragment* frag = m_fragments.Get(fragId);
               if (frag) {
                   uavFrags.Add(*frag);
                   totalSize += frag->sizeBytes;
               }
           }
           
           m_uavFragments[uavId] = uavFrags;
           m_results.uavFragmentIds[uavId] = uavFragmentSets[uavId];
           
           NS_LOG_INFO("UAV " << uavId << " assigned " << uavFragmentSets[uavId].size()
                              << " fragments, total size: " << totalSize << " bytes");
       }
   }
   ```

3. Update Build() method:
   - Find `Build()` method (around line 73)
   - Call `SelectCandidatesAndFragments()` first
   - Then call `DistributeFragmentsToUavs()` immediately after
   - Then other methods

4. Test:
   - Verify UAV0 gets fragments 0, 3, 6, 9 (heaviest)
   - Verify UAV1 gets fragments 1, 4, 7 (medium)
   - Verify UAV2 gets fragments 2, 5, 8 (lightest)
   - Verify m_results.uavFragmentIds populated
   - Log shows sizes per UAV

---

### TASK 3: Implement AdjustUavSpeedByLoad() Method
**Priority:** MEDIUM  
**Complexity:** Medium  
**Files:** `src/wsn-uav/helper/wsn-network-helper.h/.cc`

#### What to do:
1. In `.h` file, add method declaration after `DistributeFragmentsToUavs()`:
   ```cpp
   void AdjustUavSpeedByLoad();
   ```

2. In `.cc` file, implement:
   ```cpp
   void WsnNetworkHelper::AdjustUavSpeedByLoad() {
       uint32_t numUavs = m_config.numUavs;
       
       if (!m_config.useLoadBasedSpeed || numUavs == 0) {
           return;
       }
       
       // Calculate bytes per UAV
       std::vector<uint32_t> uavBytes(numUavs, 0);
       uint32_t maxBytes = 0;
       
       for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
           const auto& fragIds = m_results.uavFragmentIds[uavId];
           for (uint32_t fragId : fragIds) {
               const Fragment* frag = m_fragments.Get(fragId);
               if (frag) {
                   uavBytes[uavId] += frag->sizeBytes;
                   maxBytes = std::max(maxBytes, uavBytes[uavId]);
               }
           }
       }
       
       // Store adjusted speeds (TODO: use in trajectory planning)
       if (maxBytes == 0) return;
       
       for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
           double loadFactor = (double)uavBytes[uavId] / maxBytes;
           double speedFactor = m_config.maxSpeedFactor - 
               (m_config.maxSpeedFactor - m_config.minSpeedFactor) * loadFactor;
           
           double adjustedSpeed = m_config.uavSpeed * speedFactor;
           
           // TODO: m_uavSpeeds[uavId] = adjustedSpeed;
           
           NS_LOG_INFO("UAV " << uavId << " load: " << uavBytes[uavId]
                              << " bytes, factor: " << speedFactor
                              << ", speed: " << adjustedSpeed << " m/s");
       }
   }
   ```

3. Add to SimulationConfig in `.h`:
   ```cpp
   struct SimulationConfig {
       // ... existing fields ...
       
       // Size-based speed adjustment
       bool useLoadBasedSpeed = true;
       double minSpeedFactor = 0.6;   // 60% of base
       double maxSpeedFactor = 1.0;   // 100% of base
   };
   ```

4. Call in Build() after `DistributeFragmentsToUavs()`:
   ```cpp
   DistributeFragmentsToUavs();
   AdjustUavSpeedByLoad();  // ← NEW
   ```

5. Test:
   - Verify UAV0 (heavy) has speedFactor ≈ 0.65 (13 m/s)
   - Verify UAV1 (medium) has speedFactor ≈ 0.85 (17 m/s)
   - Verify UAV2 (light) has speedFactor ≈ 1.0 (20 m/s)
   - Log shows adjusted speeds

---

### TASK 4: Refactor ScheduleUavFlights() - Remove Strip Partitioning
**Priority:** HIGH  
**Complexity:** High  
**Files:** `src/wsn-uav/helper/wsn-network-helper.cc`

#### What to do:
1. Find `ScheduleUavFlights()` method (around line 240)

2. **Replace the strip-based partitioning** (lines 215-227):
   **OLD (Remove this):**
   ```cpp
   // Strip-based load balancing ❌
   double gridWidth = (m_config.gridSize - 1) * (double)m_config.gridSpacing;
   double stripW = gridWidth / numUavs;
   for (uint32_t nodeId : m_candidateNodes) {
       Ptr<Node> node = m_groundNodes.Get(nodeId);
       double nx = node->GetObject<MobilityModel>()->GetPosition().x;
       uint32_t strip = std::min((uint32_t)(nx / stripW), numUavs - 1);
       partitionedCandidates[strip].insert(nodeId);
   }
   ```

   **NEW (Replace with this):**
   ```cpp
   // Geographic clustering: assign nodes to nearest UAV
   for (uint32_t nodeId : m_candidateNodes) {
       Vector nodePos = m_groundNodes.Get(nodeId)->GetObject<MobilityModel>()->GetPosition();
       
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
       
       partitionedCandidates[bestUav].insert(nodeId);
   }
   ```

3. Keep the rest of the method, but update trajectory planning:
   - For each UAV, use its own adjusted speed (instead of m_config.uavSpeed)
   - TODO comment for future: "Use m_uavSpeeds[uavId] when implemented"

4. Verify waypoints are computed with adjusted speeds:
   ```cpp
   for (uint32_t uavId = 0; uavId < numUavs; uavId++) {
       // ... existing code ...
       
       // Use adjusted speed (currently default, TODO: use m_uavSpeeds[uavId])
       double uavSpeed = m_config.uavSpeed;  // TODO: Use adjusted speed
       
       waypoints = TrajectoryHelper::PlanGmc(
           targets, m_groundNodes, m_cellInfo.nodeToCell,
           startPos, uavSpeed, gmcCfg);
       
       // ... rest of code ...
   }
   ```

5. Test:
   - Verify each UAV has different target set (not strip-based)
   - Verify targets are geographically clustered (closer to UAV start)
   - Verify trajectories computed correctly
   - Log shows target counts per UAV

---

### TASK 5: Update scenario-3 Configuration (Optional)
**Priority:** LOW  
**Complexity:** Low  
**Files:** `src/wsn-uav/examples/scenario-3-load-balanced-fragments.cc`

#### What to do:
1. Add CLI parameters for new config options:
   ```cpp
   cmd.AddValue("useLoadBasedSpeed",
                "Adjust UAV speed based on fragment load [0,1]",
                config.useLoadBasedSpeed);
   cmd.AddValue("minSpeedFactor",
                "Minimum speed = baseSpeed × minSpeedFactor [0,1]",
                config.minSpeedFactor);
   cmd.AddValue("maxSpeedFactor",
                "Maximum speed = baseSpeed × maxSpeedFactor [0,1]",
                config.maxSpeedFactor);
   ```

2. Test command:
   ```bash
   ./ns3 run "scenario-3-load-balanced-fragments \
     --gridSize=10 --numFragments=10 \
     --fragmentMinSizeBytes=100 \
     --fragmentMaxSizeBytes=20000 \
     --numUavs=3 \
     --useLoadBasedSpeed=true \
     --minSpeedFactor=0.6 \
     --maxSpeedFactor=1.0"
   ```

---

## 🧪 Testing Plan

### Unit Tests (After Each Task)

**Task 1 - GenerateWithSizes():**
- [ ] Fragments have sizeBytes in [min, max]
- [ ] Fragments sorted descending by size
- [ ] Evidence calculated correctly
- [ ] Fragment count = requested

**Task 2 - DistributeFragmentsToUavs():**
- [ ] Round-robin distribution working
- [ ] UAV0 gets frags 0,3,6,... (large)
- [ ] UAV1 gets frags 1,4,7,... (medium)
- [ ] UAV2 gets frags 2,5,8,... (small)
- [ ] m_results.uavFragmentIds populated

**Task 3 - AdjustUavSpeedByLoad():**
- [ ] Speed factors calculated
- [ ] UAV0 speed < UAV1 speed < UAV2 speed
- [ ] Speed in range [minSpeed, maxSpeed]
- [ ] Log shows adjusted speeds

**Task 4 - ScheduleUavFlights():**
- [ ] No strip-based partitioning
- [ ] Geographic clustering working
- [ ] Each UAV has different targets
- [ ] Trajectories computed successfully

### Integration Tests

```bash
# Test 1: Scenario-1 (1 UAV - baseline)
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=baseline"
# Expected: Same results as before refactoring

# Test 2: Scenario-3 with 2 UAVs
./ns3 run "scenario-3-load-balanced-fragments --gridSize=5 --numUavs=2 --seed=1 --simTime=100"
# Expected: Faster detection than 1-UAV, no crashes

# Test 3: Scenario-3 with 3 UAVs (full test)
./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --numUavs=3 --seed=1"
# Expected: Fastest detection, all nodes receive all fragments

# Test 4: Verify load balancing
./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --numUavs=3 --useLoadBasedSpeed=true"
# Expected: Log shows UAV0 slower (13 m/s), UAV2 faster (20 m/s)
```

---

## ⚠️ Important Notes

1. **Fragment.sizeBytes field:** Already uncommented in Phase 0 fix ✅
2. **fragmentSizesBytes population:** Already uncommented ✅
3. **GenerateWithSizes() header:** Already declared in fragment-model.h, just implement .cc
4. **Build status:** Must work with Python 3.10 (NS-3 incompatible with 3.14)
5. **No breaking changes:** Scenario-1 must work identically after refactoring

---

## 📊 Expected Results

After implementation:
- **1-UAV scenario:** Detection time ≈ 14-15s (unchanged from Phase 0)
- **2-UAV scenario:** Detection time ≈ 7-8s (2× speedup)
- **3-UAV scenario:** Detection time ≈ 2.5-3s (4.7-5.6× speedup)

Metrics logged:
- UAV load distribution (bytes per UAV)
- Adjusted speed per UAV
- Fragment assignment per UAV
- Target node count per UAV
- Path length per UAV

---

## 🎯 Success Criteria

All of these must pass:
- [ ] Code compiles without errors
- [ ] No compilation warnings (only pre-existing ones)
- [ ] Scenario-1 test passes (detection around 14s)
- [ ] Scenario-3 with 2 UAVs completes (faster than 1-UAV)
- [ ] Scenario-3 with 3 UAVs completes (fastest, 4-5× speedup)
- [ ] Logs show proper distribution and speeds
- [ ] Results CSV files created correctly
- [ ] No memory leaks or crashes during simulation

---

## 🔗 Reference Documents

- Design doc: `PHASE1_MULTIUAV_COOP_DESIGN.md`
- Visual guide: `PHASE1_MULTIUAV_VISUAL_GUIDE.md`
- Phase 0 notes: `PHASE0_COMPLETION_REPORT.md`

---

## 💬 Quick Chat with Agent

Use this prompt to start:

> "Implement Phase 1 Multi-UAV Cooperative Architecture refactoring for WSN-UAV simulator.
> 
> Tasks (in order):
> 1. Implement GenerateWithSizes() in fragment-model.cc
> 2. Refactor DistributeFragmentsToUavs() with round-robin by size
> 3. Implement AdjustUavSpeedByLoad() method
> 4. Replace strip-based partitioning in ScheduleUavFlights() with geographic clustering
> 5. Update scenario-3 config and verify build
>
> Follow design doc: PHASE1_MULTIUAV_COOP_DESIGN.md
> 
> Expected: 3-UAV faster detection (4-5× speedup), all nodes receive all fragments
> 
> Start with Task 1."

---

**Created:** 2026-05-05  
**Status:** Ready for Agent Execution  
**Estimated Duration:** 5-7 days  
**Complexity:** Medium

