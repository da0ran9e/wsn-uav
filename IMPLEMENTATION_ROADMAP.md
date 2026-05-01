# WSN-UAV Implementation Roadmap

## Progress: Steps 1-4 Complete ✅

- ✅ Step 1: CMakeLists.txt + wscript
- ✅ Step 2: parameters.h + types.h
- ✅ Step 3: fragment-model.h/.cc (with pixel-stride interleaving)
- ✅ Step 4: confidence-model.h/.cc

## Remaining: Steps 5-13

### Step 5: statistics-collector.h/.cc
**Location:** `models/common/`
**Purpose:** Collect simulation metrics (Tdetect, path length, cooperation gain, packet statistics)
**Key Methods:**
```cpp
void RecordDetection(uint32_t nodeId, double timeSeconds);
void RecordUavPosition(double time, Vector pos);
void RecordPacketReceived(uint32_t srcId, uint32_t dstId, uint32_t fragId, bool success);
void RecordCooperation(uint32_t srcId, uint32_t dstId, uint32_t fragId);
double GetDetectionTime() const;
// ... export to CSV
```

### Step 6: topology-helper.h/.cc
**Location:** `helper/`
**Purpose:** Grid creation, hex cell assignment, candidate selection, neighbor discovery
**Key Methods:**
```cpp
static NodeContainer CreateGrid(uint32_t size, double spacing);
static CellInfo BuildCellStructure(NodeContainer nodes, double cellRadius);
static std::set<uint32_t> SelectCandidates(NodeContainer nodes, const CellInfo&, double fraction, uint32_t seed);
static uint32_t SelectDetectionNode(const std::set<uint32_t>&, uint32_t seed);
```

### Step 7: trajectory-helper.h/.cc
**Location:** `helper/`
**Purpose:** GMC path planning (greedy set-cover with k-means, cell-aware expansion)
**Key Methods:**
```cpp
static std::vector<Waypoint> PlanGmc(const std::set<uint32_t>& candidates, 
                                     NodeContainer nodes, 
                                     const std::map<uint32_t, int32_t>& nodeToCell,
                                     const Vector& startPos, double speed, const GmcConfig&);
static std::vector<Waypoint> PlanNearestNeighbor(...);
static double ComputePathLength(const std::vector<Waypoint>&, const Vector& startPos);
```

### Step 8: fragment-dissemination-app.h/.cc
**Location:** `models/application/`
**Purpose:** Main ns-3 Application for both UAV broadcast and ground node cooperation
**Key Methods:**
```cpp
enum class Role { UAV_BROADCASTER, GROUND_NODE };
void SetRole(Role r);
void SetNodeId(uint32_t id);
void SetFragments(const FragmentCollection&);
void OnPacketReceived(Ptr<const Packet>, double rssiDbm, bool fromUav);
double GetConfidence() const;
bool IsDetected() const;
// Private: DoBroadcast(), DoCooperation(), SendManifest(), ProcessManifest(), ...
```

### Step 9: result-writer.h/.cc
**Location:** `helper/`
**Purpose:** Export simulation results to CSV files
**Key Methods:**
```cpp
void Initialize() const;  // mkdir -p
void WriteMetrics(const SimulationResults&, const SimulationConfig&) const;
void WriteTrajectories(Ptr<StatisticsCollector>) const;
void WritePackets(Ptr<StatisticsCollector>) const;
void WriteConfig(const SimulationConfig&) const;
```

### Step 10: wsn-network-helper.h/.cc
**Location:** `helper/`
**Purpose:** Main orchestrator - Build/Schedule/Run simulation
**Key Methods:**
```cpp
explicit WsnNetworkHelper(const SimulationConfig&);
void Build();     // Create nodes, install radio, topology, fragments, trajectory, apps
void Schedule();  // Schedule startup phase, UAV flight, metrics logging
void Run();       // Simulator::Run()
const SimulationResults& GetResults() const;
Ptr<StatisticsCollector> GetStats() const;
// Private: CreateNodes(), InstallRadio(), BuildTopology(), SelectCandidates(), 
//          GenerateFragments(), PlanTrajectory(), InstallUavApp(), InstallGroundApps(), 
//          ScheduleUavFlight(), OnDetected(), OnGroundNodeReceive(), ...
```

### Step 11: scenario-1-single-uav.cc
**Location:** `examples/`
**Purpose:** Entry point - CLI parsing, runner, output
**Key Code:**
```cpp
int main(int argc, char* argv[]) {
    SimulationConfig config;
    CommandLine cmd(__FILE__);
    cmd.AddValue("gridSize", ..., config.gridSize);
    cmd.AddValue("numFragments", ..., config.numFragments);
    // ... more parameters
    cmd.Parse(argc, argv);
    
    WsnNetworkHelper helper(config);
    helper.Build();
    helper.Schedule();
    helper.Run();
    
    const auto& results = helper.GetResults();
    ResultWriter writer(config.outputDir);
    writer.Initialize();
    writer.WriteMetrics(results, config);
    writer.WriteTrajectories(helper.GetStats());
    writer.WritePackets(helper.GetStats());
    
    NS_LOG_INFO("Tdetect = " << results.detectionTime << "s");
    return 0;
}
```

### Step 12: Test Build & Smoke Test
```bash
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46
./ns3 build wsn-uav
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
# Verify: outputs metrics.csv, trajectories.csv, packets.csv
```

### Step 13: Validate Paper Baseline
```bash
# Run 100 seeds × 4 grid sizes = 400 simulations
for gridSize in 10 20 30 35; do
  for seed in $(seq 1 100); do
    ./ns3 run "scenario-1-single-uav --gridSize=$gridSize --seed=$seed --runId=$seed"
  done
done

# Analyze results against paper Fig.3
python tools/analysis/results-analyzer.py
```

---

## Key Implementation Notes

### CC2420 Radio Integration (in wsn-network-helper.cc)
```cpp
#include "ns3/cc2420-helper.h"  // from src/wsn

void WsnNetworkHelper::InstallRadio() {
    ns3::wsn::Cc2420Helper cc2420;
    auto channel = cc2420.CreateChannel();
    
    cc2420.SetPhyAttribute("TxPower", DoubleValue(0.0));
    cc2420.SetPhyAttribute("RxSensitivity", DoubleValue(-95.0));
    cc2420.SetPhyAttribute("EnableShadowing", BooleanValue(true));
    
    cc2420.SetChannel(channel);
    auto groundDevs = cc2420.Install(m_groundNodes);
    auto uavDevs = cc2420.Install(NodeContainer(m_uavNode));
    
    // Wire RX callbacks
    for (uint32_t i = 0; i < m_groundNodes.GetN(); i++) {
        auto dev = DynamicCast<wsn::Cc2420NetDevice>(groundDevs.Get(i));
        dev->SetReceiveCallback(MakeCallback(&WsnNetworkHelper::OnGroundNodeReceive, this));
    }
}
```

### UAV Mobility (WaypointMobilityModel)
```cpp
void WsnNetworkHelper::ScheduleUavFlight() {
    auto mob = m_uavNode->GetObject<WaypointMobilityModel>();
    for (const auto& wp : m_waypoints) {
        mob->AddWaypoint(ns3::Waypoint(
            Seconds(params::STARTUP_DURATION + wp.arrivalTimeSec),
            Vector(wp.x, wp.y, wp.z)));
    }
}
```

### Packet Format (for cooperation)
Add a simple header to distinguish UAV broadcast from node-to-node cooperation:
```cpp
// In FragmentDisseminationApp
struct FragmentPacketHeader {
    uint8_t packetType = 0;  // 0=UAV_BROADCAST, 1=COOPERATION_MANIFEST, 2=FRAGMENT_SHARE
    uint32_t sourceNodeId = 0;
    uint32_t fragmentId = 0;
    double confidence = 0.0;
    // ... serialize/deserialize as ns3::Header
};
```

### Cooperation Logic (in fragment-dissemination-app.cc)

**Ground node receives fragment:**
```cpp
void FragmentDisseminationApp::OnPacketReceived(Ptr<const Packet> pkt, double rssi, bool fromUav) {
    // Deserialize fragment
    Fragment frag = DeserializeFragment(pkt);
    
    // Update confidence
    bool changed = m_conf.OnFragment(frag, fromUav);
    
    // Check detection
    if (m_nodeId == m_detectionNode && m_conf.Above(params::ALERT_THRESHOLD)) {
        if (m_detectionCb) m_detectionCb(m_nodeId, Simulator::Now().GetSeconds());
        m_detected = true;
        Simulator::Stop(Seconds(1.0));
    }
    
    // Schedule cooperation (on first fragment)
    if (changed && !m_coopScheduled) {
        m_coopScheduled = true;
        Time delay = Seconds(m_expectedCount * params::BROADCAST_INTERVAL + 0.5);
        delay += Seconds(m_bfsLevel * params::COOPERATION_STAGGER_STEP);
        delay += Seconds(Simulator::Now().GetSeconds() % 1000 / 1000.0 * params::COOPERATION_JITTER_MAX);
        Simulator::Schedule(delay, &FragmentDisseminationApp::DoCooperation, this);
    }
}

void FragmentDisseminationApp::DoCooperation() {
    if (m_conf.IsComplete()) return;  // already have all
    
    // Broadcast manifest (set of fragment IDs we have)
    std::set<uint32_t> missing = m_conf.GetMissingIds();
    SendManifest(missing);
}
```

---

## Build & Test Commands

```bash
# Build the module
./ns3 build wsn-uav

# Run single test
./ns3 run scenario-1-single-uav -- --gridSize=10 --numFragments=10 --seed=1 --runId=1

# Run with custom output directory
./ns3 run scenario-1-single-uav -- --gridSize=20 --outputDir=/tmp/wsn-uav-results/

# Check output
ls /tmp/wsn-uav-results/
cat /tmp/wsn-uav-results/metrics.csv
cat /tmp/wsn-uav-results/trajectories.csv
```

---

## Paper Baseline Validation

**Expected Results from Fig.3 (single UAV):**
- N=100  (gridSize=10):  Tdetect ≈ 40-60 seconds
- N=400  (gridSize=20):  Tdetect ≈ 60-90 seconds
- N=900  (gridSize=30):  Tdetect ≈ 100-150 seconds
- N=1225 (gridSize=35):  Tdetect ≈ 120-180 seconds

**Expected Cooperation Gain (Fig.5):**
- With cooperation: 30-40% of fragments from node-to-node sharing
- Without cooperation (baseline): 0% (all from UAV)

---

## Files Completed ✅

1. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/CMakeLists.txt`
2. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/wscript`
3. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/common/parameters.h`
4. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/common/types.h`
5. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/application/fragment-model.h`
6. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/application/fragment-model.cc`
7. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/application/confidence-model.h`
8. `/Users/mophan/Github/ns-3-dev-git-ns-3.46/src/wsn-uav/models/application/confidence-model.cc`

## Next Steps

Continue with Step 5 onwards using this roadmap as the specification. Each step builds on the previous ones (bottom-up dependency order).
