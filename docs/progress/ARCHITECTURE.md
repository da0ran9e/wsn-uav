# WSN-UAV Simulation Architecture

---

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    scenario-1-single-uav.cc                     │
│                      (Entry Point / Main)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              WsnNetworkHelper (Orchestrator)                    │
│  ┌──────────────┬───────────────┬──────────────┬──────────┐    │
│  │ Build()      │ Schedule()     │ Run()        │ Results  │    │
│  └──────────────┴───────────────┴──────────────┴──────────┘    │
└─────────────────────┬────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌──────────────┐
   │ Topology│  │Trajectory│  │Applications │
   │ Helper  │  │ Helper   │  │  Management │
   └────┬────┘  └────┬────┘  └──────┬───────┘
        │            │               │
        │            │        ┌──────┴────────────────┐
        │            │        │                       │
        │            ▼        ▼                       ▼
        │    ┌──────────────┐ ┌──────────────────────────────┐
        │    │  GMC Path    │ │ FragmentDisseminationApp    │
        │    │  Planner     │ │  (UAV + Ground Nodes)      │
        │    └──────────────┘ │                            │
        │                     │ ┌────────────────────────┐ │
        │                     │ │ - Broadcast handling   │ │
        │                     │ │ - Cooperation msgmt    │ │
        │                     │ │ - Detection trigger    │ │
        │                     │ └────────────────────────┘ │
        │                     └────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│        Grid Topology (Nodes positioned on 2D plane)            │
│              CC2420 MAC + Wireless Channel                      │
└─────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│         StatisticsCollector (Records all events)               │
│  ┌──────────────┬──────────────┬──────────────────┐             │
│  │ UAV Position │ Packet Sent  │ Packet Received  │             │
│  │   History    │   Records    │ + Fragment Info  │             │
│  └──────────────┴──────────────┴──────────────────┘             │
└─────────────────────┬────────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌──────────────────┐      ┌─────────────────────┐
│  ResultWriter    │      │  ResultWriter       │
│  (CSV Export)    │      │  (HTML Viz Export)  │
└──────────────────┘      └─────────────────────┘
        │                           │
        ▼                           ▼
   ┌─────────────┐           ┌──────────────────┐
   │metrics.csv  │           │ wsn-uav-result   │
   │packets.csv  │           │   .html (JSON)   │
   │trajectories │           │  + Canvas App    │
   └─────────────┘           └──────────────────┘
```

---

## 📦 Component Details

### 1. WsnNetworkHelper (Orchestrator)

**File:** `helper/wsn-network-helper.cc/.h`

**Responsibilities:**
- Create network topology (ground nodes + UAV)
- Install wireless devices (CC2420)
- Install applications on all nodes
- Schedule UAV waypoints
- Run simulation
- Collect and export results

**Key Methods:**
- `Build()` - Creates network infrastructure
- `Schedule()` - Plans UAV trajectory and schedules events
- `Run()` - Executes simulator
- `OnDetection()` - Callback when target detected
- `OnGroundNodeMacIndication()` - Routes packets to ground apps
- `OnUavNodeMacIndication()` - Routes packets to UAV app

**State:**
```cpp
SimulationConfig m_config;          // All parameters
SimulationResults m_results;        // Output metrics
Ptr<StatisticsCollector> m_stats;   // Event tracking
NodeContainer m_groundNodes;        // 0 to gridSize²-1
Ptr<Node> m_uavNode;               // ID = gridSize²+1
std::set<uint32_t> m_candidateNodes; // Suspicious nodes
std::vector<Waypoint> m_uavWaypoints; // Flight path
```

---

### 2. FragmentDisseminationApp (Application)

**File:** `models/application/fragment-dissemination-app.cc/.h`

**Dual Role:**
- **UAV Mode:** Broadcasts fragments cyclically
- **Ground Mode:** Receives broadcasts, cooperates with neighbors

**UAV Behavior:**
```
StartApplication()
  ├─ Schedule DoBroadcast() every FRAGMENT_BROADCAST_INTERVAL
  
DoBroadcast()
  ├─ Get next fragment (round-robin)
  ├─ Call SendFragment()
  └─ Reschedule DoBroadcast()
  
SendFragment()
  ├─ Create FragmentPacket header
  ├─ Record to statistics (for position tracking)
  └─ Send via MAC layer (broadcast)
```

**Ground Node Behavior:**
```
OnPacketReceived()
  ├─ Parse PacketHeader (type)
  ├─ If PACKET_TYPE_FRAGMENT:
  │   ├─ Extract FragmentPacket
  │   ├─ Track fragment source (UAV vs G2G)
  │   └─ Call ProcessFragment()
  └─ If PACKET_TYPE_COOPERATION:
      ├─ Extract CooperationPacket (manifest)
      └─ Call ProcessIncomingManifest()

ProcessFragment()
  ├─ Update ConfidenceModel (adds to m_confidenceModel)
  ├─ Check detection condition
  │   └─ If nodeId == detectionNode && confidence > alertThreshold:
  │       └─ Call detection callback + stop simulator
  └─ Schedule cooperation if not already scheduled

ScheduleCooperation()
  ├─ Calculate delay = K*broadcastInterval + 0.5s + BFS_stagger + jitter
  └─ Schedule DoCooperation() at delay

DoCooperation()
  ├─ Call SendManifest() (list of fragments we have)
  └─ Wait for responses (implicit via MAC layer)

ProcessIncomingManifest()
  ├─ Compare their fragments vs ours
  ├─ Find fragments they need
  └─ Send missing fragments via SendMissingFragmentTo()
```

**Key Configuration (via Helper):**
```cpp
app->SetRole(Role::UAV_BROADCASTER or Role::GROUND_NODE)
app->SetNodeId(id)
app->SetFragments(fragmentCollection)
app->SetExpectedFragmentCount(10)
app->SetDetectionNodeId(detectionNodeId)
app->SetThresholds(cooperationThreshold, alertThreshold)
app->SetGroundNodeCount(groundNodes.GetN())
app->SetStatisticsCollector(stats)
app->SetNetDevice(device)
```

---

### 3. ConfidenceModel (Per-Node State)

**File:** `models/application/confidence-model.cc/.h`

**Tracks:**
- Fragments received by a node
- Union probability: `C = 1 - ∏(1 - p_i)`
- Source of fragments (UAV vs cooperation)
- Fragment count for visualization

**Key Methods:**
```cpp
bool OnFragment(const Fragment& f, bool fromUav)
  // Returns true if new fragment added, false if duplicate
  // Updates m_fromUav or m_fromCoop counters

double GetConfidence() const
  // Returns union probability of received fragments

bool Above(double threshold) const
  // Used for: detection trigger (alertThreshold)
  //          cooperation start (cooperationThreshold)

std::set<uint32_t> GetMissingIds() const
  // Returns set of fragment IDs not yet received
  // Used by ProcessIncomingManifest to determine what to send
```

---

### 4. FragmentModel (Fragment Data)

**File:** `models/application/fragment-model.cc/.h`

**Structure:**
```cpp
struct Fragment {
  uint32_t id;                    // 0 to numFragments-1
  double evidence;                // Confidence value [0,1]
  std::vector<uint8_t> data;      // Payload (optional)
};

class FragmentCollection {
  std::map<uint32_t, Fragment> m_frags;  // id -> fragment
  double m_totalConf;             // Cached union probability
  
  // Methods:
  bool Add(const Fragment& f)      // Add fragment, recalculate
  bool Has(uint32_t id)            // Check if have fragment
  const Fragment* Get(id)          // Retrieve fragment
  double GetTotalConfidence()      // Union probability
  uint32_t Size()                  // Count of fragments
};
```

**Generation Algorithm** (`FragmentCollection::Generate()`):
```
Pixel distribution over 416×416×3 image:
  totalPixels = 173056
  
  for i in 0..K-1:
    pixelsPerFrag = ceil(totalPixels / K)
    confidence_i = 1 - (1-0.9)^(pixelsPerFrag / totalPixels)
    fragmentSize_i = pixelsPerFrag * 3 bytes
```

---

### 5. TopologyHelper (Grid + Cell Structure)

**File:** `helper/topology-helper.cc/.h`

**Responsibilities:**
- Create grid of nodes
- Compute cell structure (hexagonal cells)
- Identify suspicious nodes (candidates)
- Calculate BFS levels for cooperation stagger

**Key Methods:**
```cpp
NodeContainer CreateGrid(uint32_t size, double spacing, double z)
  // Creates size×size grid with given spacing
  // Node ID = row*size + col

CellInfo BuildCellStructure(NodeContainer nodes, double radius)
  // Returns:
  //   - nodeToCell: maps node ID → cell ID
  //   - cellLeader: maps cell ID → leader node
  //   - neighbors: maps node ID → set of neighbors
  //   - bfsLevel: maps node ID → distance from leader

std::set<uint32_t> SelectCandidates(
  NodeContainer nodes, CellInfo cells,
  double fraction, uint32_t seed)
  // Randomly selects fraction*nodeCount nodes as suspicious

uint32_t SelectDetectionNode(
  const std::set<uint32_t>& candidates, uint32_t seed)
  // Randomly picks one candidate as detection target
```

---

### 6. TrajectoryHelper (UAV Path Planning)

**File:** `helper/trajectory-helper.cc/.h`

**Two Planning Modes:**

**A. GMC (Greedy Maximum Coverage)** - ⚠️ Has bugs
```
candidates = suspicious_nodes + kmeans_centroids
covered = ∅

while covered ≠ candidates:
  for each candidate:
    gain = |coverage(candidate) \ covered|
    if candidate covers >β of a cell: gain += cell_nodes
    cost = distance(lastWaypoint, candidate)
    score = gain / (1 + α * cost/speed)
  
  best = argmax(score)
  add(waypoints, best)
  covered ∪= coverage(best)
```

**B. Nearest-Neighbor** - ✅ Reliable (RECOMMENDED)
```
visited = ∅
current = startPos

while visited ≠ candidates:
  next = argmin(distance(current, c) for c in candidates \ visited)
  visited.add(next)
  current = next.position
  
  arrivalTime = cumulative_distance / speed
  waypoints.append((current, arrivalTime))
```

**Key Methods:**
```cpp
std::vector<Waypoint> PlanGmc(candidates, nodes, config)
std::vector<Waypoint> PlanNearestNeighbor(candidates, nodes)
double ComputePathLength(waypoints, startPos)
```

---

### 7. StatisticsCollector (Event Recorder)

**File:** `models/common/statistics-collector.cc/.h`

**Records:**
```cpp
// UAV position over time
std::vector<UavPositionRecord> m_uavPositions
  struct: {timeSeconds, x, y, z}

// All packet events
std::vector<PacketRecord> m_packetRecords
  struct: {timeSeconds, srcNodeId, dstNodeId, fragmentId,
           success, rssiDbm, srcX, srcY, srcZ}

// Per-node fragment tracking (NEW)
std::map<uint32_t, std::set<uint32_t>> m_nodeFragments
  nodeId → set of received fragmentIds
```

**Recording Methods:**
```cpp
RecordPacketSent(srcId, dstId, fragId, srcPos)
  // Called by SendFragment() and SendMissingFragmentTo()
  // Stores broadcast marker (dstId=0xFFFFFFFF) for position tracking

RecordPacketReceived(srcId, dstId, fragId, success, rssi)
  // Called by OnPacketReceived() for successful receptions
  // Matches with sent records (1.0s window)
  // Updates m_nodeFragments[dstId] with fragmentId

RecordDetection(nodeId, timeSeconds)
  // Called when detection condition triggered
```

**Matching Logic:**
```cpp
// On RecordPacketReceived:
for each sent_record where:
  sent.srcNodeId == received.srcNodeId &&
  sent.fragmentId == received.fragmentId &&
  sent.dstNodeId == 0xFFFFFFFF &&  // Was broadcast
  now - sent.timeSeconds < 1.0:    // Within window
{
  Mark sent_record as success
  Create new received_record with sent's position
  Add fragmentId to m_nodeFragments[received.dstNodeId]
}
```

---

### 8. ResultWriter (Export)

**File:** `helper/result-writer.cc/.h`

**Exports:**

1. **metrics.csv** - Summary metrics
2. **packets.csv** - All UAV packets (filtered)
3. **trajectories.csv** - UAV position over time
4. **wsn-uav-result.html** - Interactive visualization

**HTML Structure:**
```
Data Layer:
  - JSON embedded in <script>
  - Contains nodes, packets, trajectories, config
  
Canvas Layer:
  - Interactive canvas 2D rendering
  - Real-time animation with play/pause
  
Features:
  - Dynamic node coloring (based on fragments at time t)
  - Packet visualization (green=success, red=drop, yellow=G2G)
  - UAV trajectory with position interpolation
  - Zoom, pan, time scrub controls
  - Color legend and layer toggles
```

**Dynamic Coloring Algorithm (JavaScript):**
```javascript
// During animation render at time t:
const nodeFrags = {};

for(let pk of packets) {
  if(pk.t > t) break;  // Only count packets up to time t
  if(pk.success) {
    if(!nodeFrags[pk.dst]) nodeFrags[pk.dst] = new Set();
    nodeFrags[pk.dst].add(pk.fragId);
  }
}

// Color each node based on fragments at time t:
for(let nid in nodes) {
  const fragCount = nodeFrags[nid] ? nodeFrags[nid].size : 0;
  const ratio = fragCount / numFragments;
  const hue = 240 - (ratio * 240);
  const color = `hsl(${hue}, 60%, 55%)`;  // Muted
  drawNode(nid, color);
}
```

---

## 🔄 Simulation Flow

### Initialization Phase (t=0 to t=5s)
```
1. WsnNetworkHelper::Build()
   ├─ CreateNodes() - 400 ground + 1 UAV
   ├─ InstallRadios() - CC2420 on all
   ├─ BuildTopology() - Cell structure
   ├─ SelectCandidatesAndFragments()
   └─ InstallApplications()

2. WsnNetworkHelper::Schedule()
   ├─ Plan UAV trajectory (GMC or NN)
   └─ Add waypoints to WaypointMobilityModel

3. All nodes: StartApplication() called
   ├─ UAV: Schedule first DoBroadcast() at t=5.0s
   └─ Ground: Ready to receive (passive)
```

### Operation Phase (t=5 to t=simTime)
```
UAV Thread:
  t=5.0s → DoBroadcast() fragment 0
           └─ SendFragment() → MAC layer
           └─ RecordPacketSent(401, 0xFFFFFFFF, 0, uavPos)
  t=5.2s → DoBroadcast() fragment 1
  ...
  t=7.0s → DoBroadcast() fragment 0 (cycle repeats)

Ground Node Thread (example node 50):
  t=9.6s → Receive fragment 0 from UAV
           └─ OnPacketReceived() → MAC callback
           └─ ProcessFragment() → confidence increases
           └─ RecordPacketReceived(401, 50, 0, success=true, rssi=-90)
           └─ m_nodeFragments[50].add(0)
           
  t=10.2s → ScheduleCooperation() fires
            └─ SendManifest() to broadcast
            
  t=12.4s → Receive manifest from node 60
            └─ ProcessIncomingManifest()
            └─ Find fragments we're missing
            └─ SendMissingFragmentTo(60, fragIds)

Detection (if confidence > alertThreshold):
  t=48.4s → Node 305 receives enough fragments
            └─ ProcessFragment() detects threshold
            └─ OnDetection() callback
            └─ Simulator::Stop(Seconds(1.0))

Shutdown Phase:
  t=49.4s → Simulator::Destroy()
            ├─ All applications StopApplication()
            └─ Cancel all pending events
```

---

## 🔌 Packet Headers

### PacketHeader (Base)
```cpp
// Identifies packet type
enum {
  PACKET_TYPE_FRAGMENT = 1,
  PACKET_TYPE_COOPERATION = 2
};

class PacketHeader : public Header {
  uint8_t m_type;
  
  void SetType(uint8_t t) { m_type = t; }
  uint8_t GetType() const { return m_type; }
};
```

### FragmentPacket (Type 1)
```cpp
class FragmentPacket : public Header {
  uint32_t m_fragmentId;
  double m_confidence;      // Evidence value
  uint32_t m_sourceId;      // Who sent this
  
  // Setters/getters...
};
```

### CooperationPacket (Type 2)
```cpp
class CooperationPacket : public Header {
  uint32_t m_requesterId;
  int32_t m_cellId;         // Broadcast to cell
  std::vector<uint32_t> m_availableFragments;
  
  // Setters/getters...
};
```

---

## 📊 Data Flow: Packet to Visualization

```
1. SendFragment(id) [UAV App]
   ├─ Create FragmentPacket
   ├─ Add PacketHeader(PACKET_TYPE_FRAGMENT)
   ├─ RecordPacketSent(401, 0xFFFFFFFF, id, uavPos)
   └─ device->Send(packet, broadcast)
   
2. MAC Layer [CC2420]
   ├─ Propagates to nodes in range
   └─ Delivers to receiving nodes
   
3. OnPacketReceived() [Ground App]
   ├─ Extract headers
   ├─ If fragment:
   │   └─ RecordPacketReceived(401, nodeId, id, success=true, rssi)
   │   └─ m_nodeFragments[nodeId].insert(id)
   └─ StatisticsCollector gets both sent and received
   
4. ResultWriter::WriteVisualizationData()
   ├─ Iterate all packets
   ├─ Filter: only srcNodeId >= groundNodeCount (UAV packets)
   └─ Output to JSON:
       {
         "packets": [
           {"t": 5.2, "src": 401, "dst": 0xFFFFFFFF, "fragId": 0, 
            "success": true, "rssi": -90, "srcX": 72.5, "srcY": -200},
           ...
         ]
       }
   
5. HTML Canvas Renderer [JavaScript]
   ├─ Parse JSON packets and nodes
   ├─ During playback at time t:
   │   ├─ Scan packets with t <= currentTime
   │   ├─ Build nodeFrags[nodeId] = set of received fragmentIds
   │   └─ Color node based on nodeFrags.size
   └─ Render animation frame
```

---

## 🎯 Key Design Decisions

### 1. **Single Application Class with Dual Roles**
- **Why:** Reduces code duplication, cleaner packet handling
- **Trade-off:** Requires role checking in methods
- **Alternative:** Separate UAV and Ground app classes (rejected)

### 2. **Broadcast Marker (0xFFFFFFFF) for Position Tracking**
- **Why:** Separates "sent this broadcast" from "node received it"
- **Trade-off:** Extra packet records (1 sent + N received)
- **Benefit:** Preserves UAV position at transmission time

### 3. **1.0 Second Packet Matching Window**
- **Why:** Accounts for MAC/PHY processing variance
- **Trade-off:** ~4% orphan packets (acceptable)
- **Previous:** 0.1s (too tight, many orphans)

### 4. **Dynamic Color Calculation in JavaScript**
- **Why:** Supports time-based visualization during playback
- **Trade-off:** ~O(packets) per frame (mitigated by fade-out)
- **Benefit:** Watches coverage grow in real-time

### 5. **Muted Color Palette (HSL 60% sat, 55% light)**
- **Why:** Reduces eye strain, cleaner appearance
- **Trade-off:** Less vibrant than 100% saturation
- **Alternative:** Full saturation (too bright)

### 6. **Nearest-Neighbor Trajectory (GMC disabled)**
- **Why:** Simple, reliable, guarantees all candidates visited
- **Trade-off:** Not optimized for path length
- **Future:** Fix GMC algorithm

---

## 🔍 Debugging Tips

### Trace Fragment Distribution
```cpp
// In ConfidenceModel::OnFragment():
NS_LOG_INFO("Node " << m_nodeId << ": received fragment " << frag.id
            << " from " << (fromUav ? "UAV" : "G2G")
            << " (confidence=" << GetConfidence() << ")");
```

### Trace Packet Flow
```cpp
// In SendFragment():
NS_LOG_INFO("Node " << m_nodeId << ": broadcast fragment "
            << fragmentId << " at position (" << nodePos.x
            << "," << nodePos.y << ")");

// In OnPacketReceived():
NS_LOG_INFO("Node " << m_nodeId << ": received fragment "
            << fragHeader.GetFragmentId() << " from node "
            << srcNodeId << " (rssi=" << rssiDbm << ")");
```

### Trace Cooperation
```cpp
// In ScheduleCooperation():
NS_LOG_INFO("Node " << m_nodeId << ": scheduling cooperation at t+"
            << totalDelay.GetSeconds() << "s");

// In ProcessIncomingManifest():
NS_LOG_INFO("Node " << m_nodeId << ": received manifest from "
            << srcNodeId << " with " << theirFragments.size()
            << " fragments, missing " << toSend.size());
```

---

**Document Version:** 1.0  
**Last Updated:** April 30, 2026
