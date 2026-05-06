# Phase 0: Foundation Refactoring Plan

**Objective:** Prepare codebase for Multi-UAV by removing single-UAV hardcoding  
**Estimated Effort:** 2-3 days (5 parallel tasks)  
**Priority:** 🔴 CRITICAL - Must complete before Multi-UAV design  
**Status:** 📋 Planning

---

## Overview

This plan genericizes the architecture from **1 UAV** → **N UAVs** while keeping Scenario 1 working identically.

**Key Principle:** All changes backward-compatible. Scenario 1 still compiles and runs with same results.

---

## Task Breakdown

### Task 1: Core Data Structure Refactoring
**File:** `helper/wsn-network-helper.h`  
**Complexity:** HIGH  
**Estimated Time:** 4-6 hours  
**Blocking:** Tasks 2, 3, 4, 5

#### Changes:

**Remove (lines 120-126):**
```cpp
Ptr<Node> m_uavNode;                    // OLD: single UAV
NetDeviceContainer m_uavDevices;        // Already container but handled as one
Ptr<WsnUavMac> m_uavMac;               // OLD: single UAV MAC
std::vector<Waypoint> m_uavWaypoints;  // OLD: single trajectory
```

**Add:**
```cpp
NodeContainer m_uavNodes;                              // NEW: N UAVs
std::map<uint32_t, NetDeviceContainer> m_uavDevices;  // Map: uavId → device
std::map<uint32_t, Ptr<WsnUavMac>> m_uavMacs;        // Map: uavId → MAC
std::map<uint32_t, std::vector<Waypoint>> m_uavWaypoints;  // Map: uavId → waypoints

// Also add for tracking UAV state
std::map<uint32_t, Ptr<FragmentDisseminationApp>> m_uavApps;  // uavId → app
```

**Update struct SimulationConfig (lines 33-66):**
```cpp
// ADD (currently unused field):
uint32_t numUavs = 1;  // Now actually used!

// ADD per-UAV arrays (for future Multi-UAV):
std::vector<double> uavStartingX = {};    // Starting positions per UAV
std::vector<double> uavStartingY = {};
std::vector<double> uavStartingZ = {};
std::vector<uint32_t> uavFragmentPayloads = {};  // Fragments each UAV carries

// ADD validation flags:
bool validatePerUavConfig = false;  // When true, validate per-UAV settings
```

**Update struct SimulationResults (lines 72-84):**
```cpp
// Replace:
double uavPathLength = 0.0;

// With:
std::map<uint32_t, double> uavPathLengths;  // Per-UAV path lengths
double totalUavPathLength = 0.0;             // Sum of all UAVs

// ADD coordination metrics:
double cooperationOverlapRatio = 0.0;   // % of redundant broadcasts
uint32_t totalFragmentsDeliveredByUavs = 0;  // Across all UAVs
std::map<uint32_t, uint32_t> fragmentsPerUav;  // Per-UAV delivery
```

**Add new helper methods to class:**
```cpp
private:
    uint32_t GetUavCount() const { return m_uavNodes.GetN(); }
    void CreateUavNodes(uint32_t count);
    void InstallUavRadios();
    void InstallUavApplications();
    void ScheduleUavFlights();
    void OnUavDetection(uint32_t uavId, uint32_t nodeId, double timeSeconds);
```

**Validation:** Update `SimulationConfig::Validate()` to check:
- `0 < numUavs <= 100`
- If `validatePerUavConfig`: arrays have correct length
- UAV starting positions don't overlap

---

### Task 2: Helper Method Refactoring
**File:** `helper/wsn-network-helper.cc`  
**Complexity:** HIGH  
**Estimated Time:** 5-7 hours  
**Depends On:** Task 1  
**Blocking:** Task 4

#### Changes:

**CreateNodes() (lines 87-109):**

Current:
```cpp
m_uavNode = CreateObject<Node>();
// Only creates 1 UAV
```

New:
```cpp
void WsnNetworkHelper::CreateUavNodes(uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        Ptr<Node> uav = CreateObject<Node>();
        
        // Compute starting position
        double startX = m_config.uavStartingX.size() > i 
            ? m_config.uavStartingX[i] 
            : ComputeDefaultUavStart(i, count);
        double startY = m_config.uavStartingY.size() > i 
            ? m_config.uavStartingY[i] 
            : ComputeDefaultUavStart(i, count);
        
        Vector startPos(startX, startY, m_config.uavAltitude);
        
        MobilityHelper mobility;
        mobility.SetMobilityModel("ns3::WaypointMobilityModel");
        mobility.Install(NodeContainer(uav));
        
        auto mob = uav->GetObject<MobilityModel>();
        mob->SetPosition(startPos);
        
        m_uavNodes.Add(uav);
        NS_LOG_INFO("Created UAV " << i << " at (" << startX << ", " << startY << ")");
    }
}

// Helper: compute default starting positions (spread around network)
Vector WsnNetworkHelper::ComputeDefaultUavStart(uint32_t uavId, uint32_t totalUavs) {
    double gridDiameter = (m_config.gridSize - 1) * m_config.gridSpacing;
    double centerX = gridDiameter / 2.0;
    double angle = (2.0 * M_PI * uavId) / totalUavs;
    double radius = 250.0;  // Start 250m from center
    double startX = centerX + radius * cos(angle);
    double startY = -200.0 + radius * sin(angle);
    return Vector(startX, startY, m_config.uavAltitude);
}
```

**InstallRadios() (lines 115-135):**

Current:
```cpp
m_uavDevices = cc2420.Install(NodeContainer(m_uavNode));
```

New:
```cpp
void WsnNetworkHelper::InstallUavRadios() {
    wsn::Cc2420Helper cc2420;
    auto channel = cc2420.CreateChannel();
    
    // ... configure cc2420 ...
    
    for (uint32_t i = 0; i < m_uavNodes.GetN(); i++) {
        auto dev = cc2420.Install(NodeContainer(m_uavNodes.Get(i)));
        m_uavDevices[i] = dev;
        NS_LOG_INFO("Installed radio on UAV " << i);
    }
}
```

**InstallApplications() (lines 212-299):**

Current:
```cpp
// Only installs 1 UAV app
auto uavApp = CreateObject<FragmentDisseminationApp>();
m_uavNode->AddApplication(uavApp);
// ... config one UAV ...
```

New:
```cpp
void WsnNetworkHelper::InstallUavApplications() {
    for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
        auto uavApp = CreateObject<FragmentDisseminationApp>();
        Ptr<Node> uav = m_uavNodes.Get(uavId);
        uav->AddApplication(uavApp);
        
        uavApp->SetRole(FragmentDisseminationApp::Role::UAV_BROADCASTER);
        uavApp->SetNodeId(uav->GetId());
        uavApp->SetFragments(m_fragments);  // All UAVs carry same fragments (for Scenario 1)
        uavApp->SetExpectedFragmentCount(m_config.numFragments);
        uavApp->SetThresholds(m_config.cooperationThreshold, m_config.alertThreshold);
        uavApp->SetGroundNodeCount(m_groundNodes.GetN());
        uavApp->SetStatisticsCollector(m_stats);
        uavApp->SetNetDevice(m_uavDevices[uavId].Get(0));
        uavApp->SetStartTime(Seconds(m_config.startupDuration));
        uavApp->SetStopTime(Seconds(m_config.simTime));
        
        // Wire MAC callbacks
        auto uavDev = DynamicCast<wsn::Cc2420NetDevice>(m_uavDevices[uavId].Get(0));
        if (uavDev) {
            auto uavMac = uavDev->GetMac();
            if (uavMac) {
                uavMac->SetMcpsDataIndicationCallback(
                    [this, uavId](Ptr<Packet> pkt, Mac16Address src, double rssi) {
                        this->OnUavNodeMacIndication(uavId, pkt, src, rssi);
                    });
            }
        }
        
        m_uavApps[uavId] = uavApp;
        NS_LOG_INFO("Installed app on UAV " << uavId);
    }
}
```

**PlanTrajectory() (lines 175-206):**

Current:
```cpp
m_uavWaypoints = TrajectoryHelper::PlanGmc(...);
```

New:
```cpp
void WsnNetworkHelper::ScheduleUavFlights() {
    for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
        // For now, all UAVs plan same trajectory (Scenario 1 baseline)
        // Future: per-UAV candidate regions, load balancing, etc.
        
        Vector startPos = m_uavNodes.Get(uavId)->GetObject<MobilityModel>()->GetPosition();
        
        std::vector<Waypoint> waypoints;
        if (m_config.useGmc) {
            waypoints = TrajectoryHelper::PlanGmc(
                m_candidateNodes, m_groundNodes, m_cellInfo.nodeToCell,
                startPos, m_config.uavSpeed, gmcConfig);
        } else {
            waypoints = TrajectoryHelper::PlanNearestNeighbor(
                m_candidateNodes, m_groundNodes, startPos, m_config.uavSpeed);
        }
        
        m_uavWaypoints[uavId] = waypoints;
        m_results.uavPathLengths[uavId] = TrajectoryHelper::ComputePathLength(waypoints, startPos);
        m_results.totalUavPathLength += m_results.uavPathLengths[uavId];
        
        NS_LOG_INFO("UAV " << uavId << " path: " << m_results.uavPathLengths[uavId] << "m");
    }
}
```

**Schedule() (lines 305-346):**

Current:
```cpp
// Only schedules one UAV
Ptr<WaypointMobilityModel> uavMobility = m_uavNode->GetObject<WaypointMobilityModel>();
```

New:
```cpp
void WsnNetworkHelper::Schedule() {
    // Schedule all UAVs
    for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
        Ptr<WaypointMobilityModel> uavMobility = 
            m_uavNodes.Get(uavId)->GetObject<WaypointMobilityModel>();
        
        Vector startPos = m_uavNodes.Get(uavId)->GetObject<MobilityModel>()->GetPosition();
        uavMobility->AddWaypoint(ns3::Waypoint(Seconds(m_config.startupDuration), startPos));
        
        for (const auto& wp : m_uavWaypoints[uavId]) {
            Time arrivalTime = Seconds(m_config.startupDuration + wp.arrivalTimeSec);
            Vector pos(wp.x, wp.y, wp.z);
            uavMobility->AddWaypoint(ns3::Waypoint(arrivalTime, pos));
        }
    }
    
    // Position recording for all UAVs
    for (double t = 0; t <= m_config.simTime; t += 1.0) {
        Simulator::Schedule(Seconds(t), [this]() {
            for (uint32_t uavId = 0; uavId < m_uavNodes.GetN(); uavId++) {
                auto mob = m_uavNodes.Get(uavId)->GetObject<MobilityModel>();
                Vector pos = mob->GetPosition();
                m_stats->RecordUavPosition(Simulator::Now().GetSeconds(), pos, uavId);
            }
        });
    }
}
```

**Build() method (lines 68-81):**

Update to call new methods:
```cpp
void WsnNetworkHelper::Build() {
    NS_LOG_INFO("Building network with " << m_config.numUavs << " UAVs, "
                << m_config.gridSize << "x" << m_config.gridSize << " ground nodes");
    
    CreateNodes();
    CreateUavNodes(m_config.numUavs);  // NEW: explicit UAV creation
    InstallRadios();
    InstallUavRadios();                 // NEW: separate method
    BuildTopology();
    SelectCandidatesAndFragments();
    ScheduleUavFlights();               // RENAMED from PlanTrajectory
    InstallApplications();
    InstallUavApplications();            // NEW: separate method
}
```

**Callback updates (lines 349-400):**

Update `OnUavNodeMacIndication()`:
```cpp
// Current: assumes m_uavNode
// New: takes uavId parameter
void WsnNetworkHelper::OnUavNodeMacIndication(uint32_t uavId, Ptr<Packet> pkt, 
                                              Mac16Address src, double rssiDbm) {
    // ... handle UAV uavId receiving packet ...
    NS_LOG_DEBUG("UAV " << uavId << " received packet");
}
```

---

### Task 3: Result Metrics Update
**File:** `helper/result-writer.cc` + `helper/wsn-network-helper.h`  
**Complexity:** MEDIUM  
**Estimated Time:** 3-4 hours  
**Depends On:** Task 1

#### Changes:

**Update metrics output:**
```cpp
// result-writer.cc: WriteMetrics()

// OLD: single path length
// metrics.csv:
// uav_path_length_meters,664.69

// NEW: per-UAV + total
// metrics.csv:
// uav_count,2
// uav_0_path_length_meters,664.69
// uav_1_path_length_meters,580.34
// total_uav_path_length_meters,1245.03
// cooperation_overlap_ratio,0.05
```

**Modify WriteMetrics():**
```cpp
void ResultWriter::WriteMetrics(const SimulationResults& r, const SimulationConfig& cfg) const {
    std::ofstream file(m_dir + "/metrics.csv");
    file << "metric,value\n";
    
    // ... existing metrics ...
    
    // NEW: UAV metrics
    file << "uav_count," << r.uavPathLengths.size() << "\n";
    for (const auto& [uavId, pathLen] : r.uavPathLengths) {
        file << "uav_" << uavId << "_path_length_meters," << pathLen << "\n";
    }
    file << "total_uav_path_length_meters," << r.totalUavPathLength << "\n";
    file << "cooperation_overlap_ratio," << r.cooperationOverlapRatio << "\n";
    
    // ... rest ...
}
```

---

### Task 4: Scenario 1 Validation & Testing
**File:** `examples/scenario-1-single-uav.cc`  
**Complexity:** LOW  
**Estimated Time:** 2-3 hours  
**Depends On:** Task 2

#### Changes:

**Minimal changes needed:**
```cpp
// scenario-1-single-uav.cc already works!
// Just verify that with m_config.numUavs = 1 (default),
// same results as before.

// Possibly add validation:
if (config.numUavs != 1) {
    NS_LOG_ERROR("Scenario 1 is single-UAV only. Use scenario-2 for multi-UAV.");
    return 1;
}
```

**Testing:**
- Build with Task 2 changes
- Run: `./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=v1"`
- Compare metrics with pre-refactoring baseline
- Should be identical (except format change in CSV)

---

### Task 5: Build System & Documentation
**Files:** `CMakeLists.txt`, `CLAUDE.md`, docs  
**Complexity:** LOW  
**Estimated Time:** 2-3 hours  
**Depends On:** Task 4

#### Changes:

**CMakeLists.txt:**
- Already correct, no changes needed
- Comment clarifying single-UAV → multi-UAV ready

**Create CLAUDE.md:**
```markdown
# WSN-UAV Project Guidelines

## Architecture (Post-Phase 0 Refactor)

### Multi-UAV Ready
- WsnNetworkHelper supports N UAVs
- All data structures use maps/containers
- Per-UAV metrics tracked

### Important Constraints
1. Only modify src/wsn-uav/ - never edit NS-3 core
2. Python 3.13.x required (not 3.14+)
3. All UAVs in Scenario 1 carry same fragments
4. Keep backward compatibility with Scenario 1

## Next Steps
- Phase 1: Multi-UAV Coordination Protocol
- Phase 2: Advanced Features (energy, mobility, propagation)
```

**Documentation:**
- Update README.md with "Phase 0 Complete" note
- Document per-UAV metrics format change
- Add backward compatibility note

---

## Implementation Order

```
┌─────────────────────────────────────────────────────┐
│ Task 1: Data Structure Refactoring                  │
│ (4-6 hrs) - CRITICAL PATH                           │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴───────────────────┐
        │                                │
        ▼                                ▼
┌──────────────────────────────┐  ┌────────────────────────┐
│ Task 2: Helper Methods       │  │ Task 3: Result Metrics │
│ (5-7 hrs)                    │  │ (3-4 hrs)              │
└──────────────────────────────┘  └────────────────────────┘
        │                                │
        └────────────────┬───────────────┘
                         │
                         ▼
                ┌─────────────────────┐
                │ Task 4: Validation  │
                │ (2-3 hrs)           │
                └─────────────────────┘
                         │
                         ▼
                ┌─────────────────────┐
                │ Task 5: Docs & Build│
                │ (2-3 hrs)           │
                └─────────────────────┘
```

**Total Time:** 16-23 hours (~2-3 days with parallel work)

---

## Backward Compatibility Guarantee

All changes maintain **100% backward compatibility**:

```cpp
// OLD code
WsnNetworkHelper helper(config);  // config.numUavs = 1 (default)
helper.Build();
// Results in same behavior as before

// NEW code with N UAVs
config.numUavs = 3;
WsnNetworkHelper helper(config);
helper.Build();
// Each UAV gets own node, app, trajectory
// Scenario 1: still works with 1 UAV
```

---

## Success Criteria

✅ **Scenario 1 still runs identically** (same detection times, path lengths)  
✅ **Per-UAV metrics properly tracked**  
✅ **All data structures support N UAVs**  
✅ **No hardcoded single-UAV assumptions**  
✅ **Code compiles without warnings**  
✅ **Ready for Multi-UAV design**

