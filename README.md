# WSN-UAV: Clean Re-implementation of Scenario 1 Simulation

## Overview

A clean, modular re-implementation of the Scenario 4 WSN fragment dissemination simulation from the paper, targeting paper baseline reproduction (single UAV over N×N grid, N ∈ {100, 400, 900, 1225}). Features **zero global state**, configurable parameters, and an **interactive HTML/JavaScript visualization** that requires no local server or installation.

## Quick Links

- 🚀 **Getting Started:** See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (30 seconds)
- 📖 **Full Manual:** See [USER_GUIDE.md](USER_GUIDE.md) (comprehensive)
- 🎨 **Visualization Guide:** See [examples/VISUALIZER_README.md](examples/VISUALIZER_README.md)
- 🏗️ **Architecture Details:** See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

## What's Included

### Core Simulation Module
```
src/wsn-uav/
├── models/common/              Parameters, types, statistics collection
├── models/application/         Fragment model, confidence calculation, protocol
├── helper/                     Topology, trajectory planning, result writing
├── examples/                   Scenario-1-single-uav entry point
└── [Documentation files]       This README + guides
```

### Key Features

✅ **Clean Architecture**
- No global state (no g_globalVariable anti-patterns)
- Modular helpers (topology, trajectory, results all independent)
- Encapsulated state (all data in objects)
- Proper ns3::Object lifecycle management

✅ **Paper Baseline Implementation**
- Fragment generation: Pixel-stride interleaving algorithm (exact)
- Confidence model: Union probability formula (1 - ∏(1-p_i))
- GMC trajectory: Greedy maximum coverage with cell-aware expansion
- Cooperation thresholds: τ_coop=0.30, τ_alert=0.75
- CC2420 PHY integration via libwsn module reuse

✅ **Interactive Visualization**
- Standalone HTML (no server needed)
- JSON/JavaScript data format (self-contained)
- Timeline controls (scrub, play, pause, reset)
- Display options (toggle trajectory, candidates, grid, etc.)
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)

## 60-Second Start

```bash
# Build
cd ns-3-dev-git-ns-3.46
./ns3 build wsn-uav && ./ns3 build

# Run
./build/scenario-1-single-uav --gridSize=10 --seed=1

# Visualize (open in browser)
open data/results/scenario-1/run-001/wsn-uav-visualizer.html
```

Browser: Click "Load visualization-data.js" → select file → play timeline.

## File Structure

```
src/wsn-uav/
├── CMakeLists.txt                      Build configuration (CMake)
├── wscript                             Empty stub (ns-3 waf support)
│
├── README.md                           This file
├── QUICK_REFERENCE.md                  30-second command cheat sheet
├── USER_GUIDE.md                       Complete user manual
├── IMPLEMENTATION_STATUS.md            Technical implementation details
│
├── models/common/
│   ├── parameters.h                   40+ constexpr constants
│   ├── types.h                        Enums, POD structs
│   ├── statistics-collector.h/.cc     Detection, position, packet tracking
│
├── models/application/
│   ├── fragment-model.h/.cc          Pixel-stride fragment generation
│   ├── confidence-model.h/.cc        Union probability confidence tracking
│   ├── fragment-dissemination-app.h/.cc  Protocol implementation
│
├── helper/
│   ├── topology-helper.h/.cc         Grid layout, cell structure, candidates
│   ├── trajectory-helper.h/.cc       GMC path planning algorithm
│   ├── result-writer.h/.cc           CSV + JSON/JS export
│   ├── wsn-network-helper.h/.cc      Orchestrator (build→schedule→run)
│
└── examples/
    ├── CMakeLists.txt                 Executable build
    ├── scenario-1-single-uav.cc       Entry point (CLI parsing, main loop)
    ├── wsn-uav-visualizer.html        Interactive HTML viewer
    ├── VISUALIZER_README.md           Visualization guide
    └── QUICK_REFERENCE.md             Command cheat sheet
```

## Key Algorithmic Implementations

### Fragment Generation (Pixel-Stride Interleaving)
```cpp
// models/application/fragment-model.cc::Generate()
// Input: K fragments, masterConfidence = 0.90
// Output: K fragments with evidence p_i
// Algorithm:
//   - Image: 416×416×3 pixels = 173056 total
//   - Fragment i gets: ⌊totalPixels/K⌋ pixels + (i < remainder ? 1 : 0)
//   - Evidence: p_i = 1 - (1-0.9)^(pixelCount_i / totalPixels)
```

### Confidence Calculation (Union Probability)
```cpp
// models/application/confidence-model.cc::Get()
// C = 1 - ∏(1 - p_i)  for all received fragments i
// Threshold checking: C >= τ_alert → detection
```

### GMC Trajectory Planning (Greedy Set Cover)
```cpp
// helper/trajectory-helper.cc::PlanGmc()
// Score formula: gain / (distance^α + eps)  where α = 1.0
// Cell-aware: If waypoint covers >30% of cell, credit all cell nodes
// Greedy loop: Repeat until all candidates covered
```

## Output Files

Each simulation run generates:

| File | Format | Size | Purpose |
|------|--------|------|---------|
| wsn-uav-visualizer.html | HTML+JS | 27 KB | Interactive visualization (open in browser) |
| visualization-data.js | JavaScript | 13-140 KB | Simulation data (JSON constant) |
| metrics.csv | CSV | <1 KB | Summary statistics |
| trajectories.csv | CSV | 1-5 KB | UAV position history |
| packets.csv | CSV | <1 KB | Packet records |
| config.txt | Text | <1 KB | Parameter summary |

## Command-Line Interface

```bash
./build/scenario-1-single-uav [OPTIONS]

Essential parameters:
  --gridSize=10              10×10 = 100 nodes (default)
  --numFragments=10          10 fragments (default)
  --seed=1                   Random seed (default: 1)
  --simTime=500              Simulation duration in seconds (default: 500)

Tuning:
  --cooperationThreshold=0.30    Fragment share threshold (default)
  --alertThreshold=0.75          Detection threshold (default)
  --useGmc=true                  Trajectory algorithm (default: GMC)
  --usePerfectChannel=false      Realistic radio (default)

Output:
  --outputDir=./data/results/scenario-1/run-001    Configurable path
```

## Visualization Usage

### Loading Data
1. Double-click `wsn-uav-visualizer.html`
2. Click "Load visualization-data.js" button
3. Select `visualization-data.js` from same directory

### Navigation
- **Slider:** Scrub timeline (0 to simTime seconds)
- **Play:** Animate UAV movement in real-time
- **Pause:** Freeze at current time
- **Reset:** Jump to t=0

### Display Options
- Toggle "Show UAV Trajectory" (historical path)
- Toggle "Show Waypoints" (planned path)
- Toggle "Highlight Candidates" (color suspicious nodes)
- Toggle "Show Grid Background" (grid lines)

### Information
- Detection status (YES/NO) and time
- Grid configuration and node count
- UAV path length (meters)
- Cooperation gain (%)

## Test Results

### 10×10 Grid (100 nodes)
```
Runtime: ~5 seconds
Candidates: 30 nodes
UAV waypoints: 2
Path length: 154.57 m
Visualization: ✅ Loads correctly, shows trajectory
```

### 20×20 Grid (400 nodes)
```
Runtime: ~30 seconds
Candidates: 120 nodes
UAV waypoints: ~8-12
Path length: 493.39 m
Visualization: ✅ Smooth rendering, detailed grid
```

## Paper Baseline Reference

Reproducing **Figure 3: Tdetect vs. Network Size**

Target: Compare detection time across N ∈ {100, 400, 900, 1225}

```bash
# Example: N=100 with 100 seeds
for seed in {1..100}; do
  ./build/scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$seed
done

# Extract Tdetect from metrics.csv files
# Compute mean, stddev, compare against paper
```

## Architecture Highlights

### No Global State
Every component encapsulates its state:
- ❌ NO: `static WsnNetworkState g_state;`
- ✅ YES: `class WsnNetworkHelper { ... m_state ... };`

### Separation of Concerns
- **Fragment model:** Pure data (no ns3 dependency)
- **Confidence model:** State machine (pure C++)
- **Dissemination app:** ns3::Application (protocol logic)
- **Helpers:** Utilities (topology, trajectory, results)
- **Orchestrator:** WsnNetworkHelper (build→schedule→run)

### Configurable Everything
- Grid size, spacing, node count
- Fragment count and evidence
- Thresholds (cooperation, alert, cell coverage)
- UAV altitude, speed, broadcast interval
- Output directory and filename
- Channel model (perfect vs realistic)
- Trajectory algorithm (GMC vs nearest-neighbor)

## Building from Scratch

### Requirements
- NS-3.46+ (with mobility, spectrum, and wsn modules)
- CMake 3.16+
- C++17 compiler
- macOS/Linux/Windows (CMake cross-platform)

### Build Steps
```bash
cd ns-3-dev-git-ns-3.46

# Build library
./ns3 build wsn-uav

# Build examples
./ns3 build

# Result: ./build/scenario-1-single-uav executable
```

### Verify
```bash
./build/scenario-1-single-uav --help 2>&1 | grep -i grid
```

## Extending the Code

### Add a New Trajectory Algorithm
1. Create `trajectory-helper.cc::PlanMyAlgorithm()`
2. Add CLI option: `cmd.AddValue("myAlgo", ...)`
3. Call in `wsn-network-helper.cc::PlanTrajectory()`

### Add Custom Output Format
1. Extend `result-writer.h` with `WriteMyFormat()`
2. Call in `scenario-1-single-uav.cc::main()`

### Modify Fragment Evidence
1. Edit `fragment-model.cc::Generate()`
2. Change evidence formula or distribution

### Change Topology
1. Edit `topology-helper.cc::CreateGrid()`
2. Implement circular, random, or custom layout

## Documentation Map

| Document | Length | Purpose |
|----------|--------|---------|
| This README | 5 min | Overview + quick links |
| QUICK_REFERENCE.md | 1 min | Command cheat sheet |
| USER_GUIDE.md | 20 min | Complete manual + examples |
| VISUALIZER_README.md | 10 min | Visualization system guide |
| IMPLEMENTATION_STATUS.md | 15 min | Architecture + porting notes |

Start with **QUICK_REFERENCE.md** for immediate use, or **USER_GUIDE.md** for learning.

## License & Attribution

This is a clean re-implementation based on the paper methodology:
> Scenario 4 WSN fragment dissemination simulation
> Paper: Multi-UAV Fragment Dissemination over Ground Networks

Code written from specification, not copied from original implementation.

## Support

- 🔍 **Check QUICK_REFERENCE.md** for common commands
- 📖 **Check USER_GUIDE.md** for detailed guidance
- 🎨 **Check examples/VISUALIZER_README.md** for visualization issues
- 🏗️ **Check IMPLEMENTATION_STATUS.md** for architecture questions

---

**Version:** 1.0 (Clean implementation, 10×10 and 20×20 test runs verified)

**Last Updated:** April 2026

**Status:** ✅ Fully functional with visualization