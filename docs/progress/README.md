# WSN-UAV Project Progress Log

## Quick Start

To run simulations:
```bash
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46
./ns3 clean
./ns3 configure --enable-examples --enable-modules=wsn-uav
./ns3 build
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1"
```

Output: `src/wsn-uav/results/scenario-1/run-XXX/wsn-uav-result.html`

---

## Session History

### [Session 5: NS-3 Run Integration](session5_ns3_run_integration.md) - 2026-05-01
**Status: ✅ COMPLETE**

- Fixed `./ns3 run` command integration
- Switched from `add_executable()` to `build_lib_example()`
- Removed conflicting `add_subdirectory(examples)` call
- Tested with 5 different grid/parameter combinations
- All simulations running successfully

**Key Files Modified:**
- `src/wsn-uav/examples/CMakeLists.txt` - Use `build_lib_example()`

**How to Use:**
```bash
./ns3 run "scenario-1-single-uav --gridSize=X --numFragments=Y --seed=Z --runId=W"
```

---

## Project State Summary

### ✅ Working Features
- Fragment dissemination model with confidence-based detection
- K-means clustering for trajectory planning
- Ground node cooperation with manifest exchange
- CC2420 radio model with path loss & BER
- Visualization generation (HTML Canvas)
- Result CSV output (metrics, trajectories, packets)

### ✅ Working Build System
- Standard ns-3 workflow: clean → configure → build → run
- Fast build with `--enable-modules=wsn-uav` filtering
- Proper example registration with `build_lib_example()`
- Command-line parameter parsing

### 📊 Test Results
- 10×10 grid: Detection at 21.8s ✅
- 15×15 grid: No detection (30s candidates)
- 20×20 grid: No detection (larger area)
- 25×25 grid: No detection (sparse coverage)
- 30×30 grid: No detection (sparse coverage)

### ⚠️ Known Limitations
- Cooperation system exists but gain is 0% (candidates don't meet threshold)
- Detection requires fairly dense candidate selection or small grid
- No multi-UAV support (Scenario 1 baseline = single UAV)

---

## Directory Structure

```
src/wsn-uav/
├── CMakeLists.txt
├── examples/
│   ├── CMakeLists.txt
│   └── scenario-1-single-uav.cc
├── models/
│   ├── common/
│   │   ├── parameters.h
│   │   ├── types.h
│   │   ├── statistics-collector.h/.cc
│   │   └── packet-header.h/.cc
│   ├── application/
│   │   ├── fragment-model.h/.cc
│   │   ├── confidence-model.h/.cc
│   │   └── fragment-dissemination-app.h/.cc
│   └── mac/
│       └── wsn-uav-mac.h/.cc
├── helper/
│   ├── topology-helper.h/.cc
│   ├── trajectory-helper.h/.cc
│   ├── result-writer.h/.cc
│   ├── wsn-network-helper.h/.cc
│   └── wsn-uav-helper.h
├── docs/
│   └── progress/
│       ├── README.md (this file)
│       └── session5_ns3_run_integration.md
└── results/
    └── scenario-1/
        └── run-XXX/
            ├── metrics.csv
            ├── trajectories.csv
            ├── packets.csv
            ├── config.txt
            └── wsn-uav-result.html
```

---

## Key Parameters

### Simulation Config
- `--gridSize` - N for N×N ground nodes (default: 10)
- `--numFragments` - K fragments to disseminate (default: 10)
- `--gridSpacing` - Distance between nodes in meters (default: 20m)
- `--simTime` - Total simulation duration (default: 500s)

### UAV Config
- `--uavSpeed` - Speed in m/s (default: 20)
- `--uavAltitude` - Flight altitude in meters (default: 20)
- `--broadcastInterval` - Fragment broadcast interval in seconds (default: 0.2)
- `--useGmc` - Use GMC trajectory (default: true, or nearest-neighbor)

### Detection Config
- `--cooperationThreshold` - τ_coop for cooperation trigger (default: 0.30)
- `--alertThreshold` - τ_alert for detection (default: 0.75)
- `--suspiciousPercent` - Fraction of network for candidates (default: 0.30)

### Experiment Config
- `--seed` - Random seed for reproducibility
- `--runId` - Run ID for output directory naming
- `--outputDir` - Custom output path
- `--usePerfectChannel` - Bypass realistic radio model (default: false)

---

## Common Tasks

### Run Single Experiment
```bash
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
```

### Run Batch with Different Seeds
```bash
for seed in {1..10}; do
  ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$seed"
done
```

### Run Different Grid Sizes (Paper Baseline)
```bash
# N=100 (10×10)
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1"

# N=400 (20×20)
./ns3 run "scenario-1-single-uav --gridSize=20 --seed=1"

# N=900 (30×30)
./ns3 run "scenario-1-single-uav --gridSize=30 --seed=1"

# N=1225 (35×35)
./ns3 run "scenario-1-single-uav --gridSize=35 --seed=1"
```

### View Results
Results are generated in: `src/wsn-uav/results/scenario-1/run-XXX/`
- Open `wsn-uav-result.html` in browser for visualization
- Parse `metrics.csv` for detection time, path length, etc.

---

## Next Steps (Future Sessions)

1. **Batch Experiments:** Run 100+ seeds for each grid size to get statistical results
2. **Comparison:** Compare GMC vs nearest-neighbor trajectory planning
3. **Cooperation Study:** Investigate why cooperation gain is 0% - may need different parameters
4. **Paper Reproduction:** Validate against "Joint Fragment Dissemination and Edge Fusion..." paper
5. **Performance Optimization:** Profile and optimize for larger networks

---

## Technical Notes

### Why build_lib_example?
- Registers executable with ns-3's program discovery system
- Gets proper versioning/naming: `ns3.46-scenario-1-single-uav-default`
- Makes `./ns3 run scenario-1-single-uav` work automatically
- Integrates with build system's ENABLE_EXAMPLES filtering

### Why --enable-modules=wsn-uav?
- Dramatically speeds up configuration (skip ~35 other modules)
- Only builds wsn-uav and its dependencies
- For full build, just use `./ns3 configure --enable-examples`

### Output File Format
- `metrics.csv`: Tdetect, pathLength, cooperationGain, candidateNodes
- `trajectories.csv`: time, x, y, z (UAV position trace)
- `packets.csv`: time, src, dst, fragment_id, type (UAV broadcast or G2G)
- `config.txt`: All simulation parameters used

---

Last updated: 2026-05-01
