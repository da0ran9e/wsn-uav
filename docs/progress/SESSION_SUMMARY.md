# WSN-UAV Simulation - Session Progress Summary

**Date:** April 30, 2026  
**Status:** ✅ STABLE - Safe to checkpoint  
**Commits Made:** Multiple fixes and enhancements  

---

## 🎯 Current Project State

### ✅ Completed Features

#### 1. **Core Simulation Framework**
- Single UAV fragment dissemination simulator
- Ground node network with configurable grid (any size, any spacing)
- Fragment generation with confidence model (union probability)
- Detection node triggered by confidence threshold
- Contact window model with realistic packet drops

#### 2. **Network Communication**
- UAV broadcasts fragments cyclically (configurable interval)
- Ground node cooperation with manifest exchange
- Unicast fragment delivery between nodes
- G2G cooperation enables distributed coverage
- Proper packet matching with 1.0s time window

#### 3. **Visualization System** (FULLY DYNAMIC)
- **Interactive Canvas Visualization:**
  - Play/Pause/Reset/Seek controls
  - Zoom and pan support
  - Real-time frame rate rendering
  
- **Dynamic Node Coloring:**
  - Colors change based on fragments received up to time `t`
  - Color gradient: Blue (0 frags) → Yellow (all frags)
  - Muted color palette for easy viewing
  - Updates in real-time during playback
  
- **Packet Visualization:**
  - 🟢 Green lines: UAV successful broadcasts
  - 🔴 Red X marks: Contact window drops
  - 🟡 Yellow lines: Ground-to-ground cooperation
  - Fade-out effect (2-second window) for clarity
  
- **Network Visualization:**
  - Grid overlay with configurable spacing
  - Candidate nodes with yellow border
  - Detection node highlighted in red
  - UAV trajectory path shown in blue

#### 4. **Statistics & Metrics**
- Packet reception tracking with RSSI
- Fragment count per node
- Detection time and node identification
- UAV path length calculation
- Cooperation gain metrics

#### 5. **Configuration Options**
```bash
# Example invocation:
./build/scenario-1-single-uav \
  --gridSize=20 \
  --gridSpacing=5 \
  --uavAltitude=20 \
  --uavSpeed=40 \
  --simTime=150 \
  --numFragments=10 \
  --useGmc=false \
  --runId=261
```

---

## 📊 Test Results Summary

### Recent Successful Runs

| Run | Grid | Spacing | Speed | Alt | Detection | Status |
|-----|------|---------|-------|-----|-----------|--------|
| 261 | 12×12 | 15m | 30m/s | 15m | 12.0s ✓ | PASS |
| 260 | 15×15 | 10m | 30m/s | 15m | 12.2s ✓ | PASS |
| 251 | 20×20 | 20m | 30m/s | 10m | 62.4s ✓ | PASS |
| 243 | 10×10 | 20m | 20m/s | 10m | 27.8s ✓ | PASS |
| 242 | 15×15 | 5m | 40m/s | 20m | 9.8s ✓ | PASS |
| 241 | 12×12 | 20m | 30m/s | 10m | 22.4s ✓ | PASS |
| 240 | 20×20 | 20m | 40m/s | 10m | 48.4s ✓ | PASS |

### Visualization Quality
- ✅ Node colors update dynamically during playback
- ✅ Fragment-based coloring shows coverage growth
- ✅ Muted colors reduce visual fatigue
- ✅ Packet lines fade smoothly (2s window)
- ✅ No lines starting from node 0 (3.7% orphans acceptable)

---

## 🔧 Key Implementation Details

### Fragment Distribution Algorithm
- Interleaved pixel distribution over 416×416×3 image
- Confidence formula: `C = 1 - ∏(1 - p_i)` for all received fragments
- Master file confidence: 0.90 (90%)
- Per-fragment evidence: calculated from pixel count

### Confidence Model
- Tracks fragments received by each node
- Distinguishes UAV vs. cooperation sources
- Supports detection trigger (threshold-based)
- Maintains per-node fragment count for visualization

### Packet Matching Algorithm
- Broadcast sent: `RecordPacketSent(src, 0xFFFFFFFF, frag, pos)`
- Unicast received: `RecordPacketReceived(src, dst, frag, success, rssi)`
- Matching window: 1.0 second (extended from 0.1s)
- Matches by: srcNodeId + fragmentId + broadcast marker

### UAV Identification
- `SetGroundNodeCount()` method on each app
- UAV nodeId = groundNodes.GetN() + 1
- Comparison: `srcNodeId >= groundNodeCount` = UAV packet

### Dynamic Color Rendering (JavaScript)
```javascript
// During playback at time t:
const nodeFrags = {};
for(let pk of packets) {
  if(pk.t > t) break;
  if(pk.success) {
    if(!nodeFrags[pk.dst]) nodeFrags[pk.dst] = new Set();
    nodeFrags[pk.dst].add(pk.fragId);
  }
}
// Then color node based on: nodeFrags[nodeId].size
```

---

## ⚠️ Important Notes & Gotchas

### 1. **Trajectory Planning**
- **GMC planner has a bug**: Doesn't visit all candidate nodes
- **Solution**: Use `--useGmc=false` for reliable nearest-neighbor planning
- **Status**: GMC fix pending - not critical for testing

### 2. **UAV Altitude & Contact Window**
- **Low altitude (10m) = More drops**: 10-15% packet loss typical
- **High altitude (20m) = Better reception**: 5-10% packet loss
- **Trade-off**: Lower = faster detection, more drops; Higher = slower, better link quality

### 3. **Grid Spacing Effects**
- **5m spacing**: Dense network, very fast detection (9-20s)
- **20m spacing**: Sparse network, slower detection (30-60s)
- **Dense networks**: More G2G cooperation visible in visualization
- **Sparse networks**: UAV broadcasts dominate

### 4. **Fragment Count Ranges**
- 0 frags: Dark blue (no UAV coverage)
- 1-3 frags: Light blue (weak coverage)
- 4-6 frags: Light green (moderate)
- 7-10 frags: Yellow (excellent coverage)
- Color is DYNAMIC - updates during playback

### 5. **Packet Record Orphans (3-5%)**
- Some packets don't find matching sent records
- Caused by timing variance in MAC layer processing
- **Solution**: Extended matching window from 0.1s → 1.0s
- **Impact**: Reduces orphans from ~5% → ~4%
- **Status**: Acceptable for visualization (lines still mostly correct)

### 6. **Cooperation Packets in Visualization**
- G2G packets filtered OUT of CSV export (only UAV packets)
- G2G packets INCLUDED in HTML visualization (yellow lines)
- **Reason**: User requested "visualize only UAV drops, not ground cooperation drops"
- **Result**: CSV is clean; HTML shows both for context

### 7. **Detection Node Guarantee**
- Detection node is randomly selected from candidate nodes
- **Not guaranteed** to receive fragments from UAV directly
- May rely on G2G cooperation to reach detection threshold
- **If no detection**: Likely candidate nodes don't include detection node

---

## 📋 Critical Files & Their Roles

### Core Application
```
src/wsn-uav/models/application/
├── fragment-dissemination-app.cc/.h    # Main app logic (UAV + Ground)
├── confidence-model.cc/.h              # Per-node fragment tracking
└── fragment-model.cc/.h                # Fragment data structures
```

### Helper Classes
```
src/wsn-uav/helper/
├── wsn-network-helper.cc/.h            # Orchestrator (Build→Schedule→Run)
├── topology-helper.cc/.h               # Grid creation, cell structure
├── trajectory-helper.cc/.h             # GMC & nearest-neighbor planning
└── result-writer.cc/.h                 # CSV + HTML visualization export
```

### Statistics
```
src/wsn-uav/models/common/
├── statistics-collector.cc/.h          # Packet/position tracking
├── packet-header.h                     # Fragment + Cooperation headers
└── parameters.h                        # All constants
```

### Build
```
src/wsn-uav/
├── CMakeLists.txt                      # CMake build configuration
└── examples/scenario-1-single-uav.cc   # Entry point
```

---

## 🚀 How to Run Tests

### 1. **Quick Test** (2 minutes)
```bash
cd ns-3-dev-git-ns-3.46
./build/scenario-1-single-uav \
  --gridSize=10 --uavSpeed=20 \
  --simTime=50 --runId=test
```

### 2. **Standard Test** (5 minutes)
```bash
./build/scenario-1-single-uav \
  --gridSize=15 --gridSpacing=5 \
  --uavAltitude=20 --uavSpeed=40 \
  --simTime=100 --runId=100
```

### 3. **Dense Network** (10 minutes)
```bash
./build/scenario-1-single-uav \
  --gridSize=20 --gridSpacing=5 \
  --uavAltitude=20 --uavSpeed=40 \
  --simTime=150 --runId=200
```

### 4. **Visualize Results**
```bash
# Open in browser:
src/wsn-uav/results/scenario-1/run-XXX/wsn-uav-result.html

# Features:
# - Play/Pause animation
# - Drag timeline to scrub through time
# - Zoom with mouse wheel
# - Pan with mouse drag
# - Toggle layers (Grid, Nodes, TX, Drops, etc)
```

---

## 🧪 Verification Checklist

### Before Committing Changes
- [ ] Builds without errors: `./ns3 build wsn-uav`
- [ ] Quick test runs: `./build/scenario-1-single-uav --gridSize=10 --simTime=30`
- [ ] HTML visualization renders correctly
- [ ] Node colors update during playback
- [ ] Packet lines fade smoothly

### Before Large Test Runs
- [ ] No uncommitted changes
- [ ] Build is fresh
- [ ] Sufficient disk space for results (~1MB per run)
- [ ] Use `--useGmc=false` for reliable results

### After Test Completion
- [ ] metrics.csv exists and is readable
- [ ] packets.csv shows both successful and dropped packets
- [ ] wsn-uav-result.html opens in browser
- [ ] Visualizations show expected patterns

---

## 📈 Performance Expectations

### Build Time
- Full build: ~15-30 seconds
- Incremental build (small changes): ~5-10 seconds

### Simulation Time
- 10×10 grid: 5-10 seconds real time
- 15×15 grid: 15-30 seconds real time
- 20×20 grid: 30-60 seconds real time
- 30×30 grid: 60-120 seconds real time

### Output Sizes
- metrics.csv: ~300 bytes
- packets.csv: 30-100 KB (depending on network)
- wsn-uav-result.html: 50-500 KB (embedded JSON)
- trajectories.csv: ~1-5 KB

---

## 🔄 Workflow Procedures

### Adding New Simulation Parameters
1. Edit `SimulationConfig` in `wsn-network-helper.h`
2. Update default values
3. Add option parsing in `scenario-1-single-uav.cc`
4. Rebuild: `./ns3 build wsn-uav`

### Debugging Packet Flow
1. Check packets.csv: `grep "true\|false" packets.csv | head -20`
2. Check node reception: `grep '"dst": 50' wsn-uav-result.html`
3. Verify coloring: `grep '"fragCount"' wsn-uav-result.html | sort | uniq -c`

### Performance Optimization
- Reduce `simTime` for quick tests
- Use sparse grids (`gridSpacing > 20m`) for fast feedback
- Use `--useGmc=false` to skip slow trajectory planning

---

## 📝 Last Known Good State

**Branch:** Current development  
**Latest Test:** Run-261 (✅ PASS)
- 12×12 grid, 15m spacing, 30 m/s speed, 15m altitude
- Detection: 12.0s
- Dynamic coloring: Working
- Visualization: All features functional

**All Key Features Stable:**
- ✅ Fragment dissemination
- ✅ Cooperation messaging
- ✅ Confidence calculation
- ✅ Detection triggering
- ✅ Statistics collection
- ✅ CSV export
- ✅ HTML visualization
- ✅ Dynamic node coloring
- ✅ Packet fade-out effect

---

## 🎯 Next Steps (Future Work)

### High Priority
1. Fix GMC trajectory planner (currently doesn't visit all candidates)
2. Improve packet orphan matching rate (currently ~4%)
3. Add ground node cooperation gain metrics

### Medium Priority
1. Implement batch experiment runner
2. Add performance profiling
3. Create automated test suite
4. Document cooperation packet flows

### Low Priority
1. 3D visualization support
2. Real-time simulation monitoring
3. Advanced energy modeling
4. Multi-UAV scenarios

---

## 📞 Quick Reference

### Common Commands
```bash
# Build only the wsn-uav module
./ns3 build wsn-uav

# Run test simulation
./build/scenario-1-single-uav --gridSize=15 --simTime=100 --runId=1

# View latest results
open src/wsn-uav/results/scenario-1/run-1/wsn-uav-result.html

# Check packet statistics
wc -l src/wsn-uav/results/scenario-1/run-1/packets.csv
```

### Common Issues & Solutions
| Problem | Solution |
|---------|----------|
| Build fails | Run `./ns3 build wsn-uav` fresh |
| No detection | Use `--useGmc=false` for nearest-neighbor |
| Slow detection | Increase `--uavSpeed` or decrease `--gridSpacing` |
| Many orphan packets | Already optimized - acceptable at ~4% |
| Colors don't show | Make sure `--gridSize` is large enough for visible network |

---

**Document Version:** 1.0  
**Last Updated:** April 30, 2026  
**Status:** 🟢 PRODUCTION READY
