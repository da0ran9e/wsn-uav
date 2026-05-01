# WSN-UAV Scenario 1 User Guide

A clean, modular re-implementation of the Scenario 4 WSN fragment dissemination simulation from the paper baseline, supporting interactive visualization without any local server or installation requirements.

## Quick Start (5 minutes)

### 1. Build the simulation
```bash
cd ns-3-dev-git-ns-3.46
./ns3 build wsn-uav
./ns3 build  # builds the example executable
```

### 2. Run a simulation
```bash
./build/scenario-1-single-uav --gridSize=10 --numFragments=10 --seed=1
```

### 3. Visualize the results
```bash
open data/results/scenario-1/run-001/wsn-uav-visualizer.html
```

In your browser:
1. Click **"Load visualization-data.js"**
2. Select `visualization-data.js` from the results directory
3. Use the **timeline slider** to scrub through the simulation
4. Click **Play** to watch the UAV trajectory in real-time

## Command-Line Parameters

```bash
./build/scenario-1-single-uav [OPTIONS]

Network Configuration:
  --gridSize=N              Size of ground node grid (N×N), default: 10
  --gridSpacing=M           Spacing between nodes in meters, default: 20
  --suspiciousPercent=F     Fraction of network marked as candidates [0,1], default: 0.30

Fragment & Dissemination:
  --numFragments=K          Number of file fragments, default: 10
  --broadcastInterval=S     Interval between UAV broadcasts in seconds, default: 0.2
  --cooperationThreshold=τ  Confidence threshold for cooperation [0,1], default: 0.30
  --alertThreshold=τ        Confidence threshold for detection [0,1], default: 0.75

UAV Configuration:
  --uavAltitude=M           UAV flight altitude in meters, default: 20
  --uavSpeed=M/s            UAV speed in m/s, default: 20
  --useGmc=BOOL             Use Greedy Maximum Coverage trajectory (true/false), default: true

Simulation Control:
  --startupDuration=S       Startup phase before UAV flight, default: 5
  --simTime=S               Total simulation duration in seconds, default: 500
  --seed=N                  Random seed for reproducibility, default: 1
  --runId=N                 Run ID for batch experiments, default: 1

Output & Channel:
  --outputDir=PATH          Output directory for results, default: ./data/results/scenario-1/run-NNN
  --usePerfectChannel=BOOL  Use ideal channel or realistic CC2420, default: false
```

## Example Scenarios

### Paper Baseline (N=100, single run)
```bash
./build/scenario-1-single-uav \
  --gridSize=10 \
  --numFragments=10 \
  --seed=1 \
  --runId=1 \
  --simTime=500
```

### Batch experiment (100 seeds for statistics)
```bash
for seed in {1..100}; do
  ./build/scenario-1-single-uav \
    --gridSize=10 \
    --numFragments=10 \
    --seed=$seed \
    --runId=$seed \
    --simTime=500
done
# Results in: ./data/results/scenario-1/run-001 through run-100
```

### Larger network (N=400)
```bash
./build/scenario-1-single-uav \
  --gridSize=20 \
  --numFragments=10 \
  --seed=42 \
  --runId=1 \
  --simTime=500
```

### Testing with lower thresholds (faster detection)
```bash
./build/scenario-1-single-uav \
  --gridSize=10 \
  --cooperationThreshold=0.15 \
  --alertThreshold=0.50 \
  --simTime=200
```

### Nearest-neighbor baseline (disable GMC)
```bash
./build/scenario-1-single-uav \
  --gridSize=10 \
  --useGmc=false \
  --simTime=500
```

## Output Files

Each simulation produces 5 output files in `./data/results/scenario-1/run-NNN/`:

| File | Format | Purpose |
|------|--------|---------|
| `wsn-uav-visualizer.html` | HTML + JS | Interactive visualization (load in browser) |
| `visualization-data.js` | JavaScript | Simulation data in JSON format |
| `metrics.csv` | CSV | Summary statistics (detection time, path length, etc.) |
| `trajectories.csv` | CSV | UAV position history (1Hz sampling) |
| `packets.csv` | CSV | Individual packet records |
| `config.txt` | Text | Human-readable parameter dump |

## Visualization Guide

### Loading Data
1. Double-click `wsn-uav-visualizer.html` to open in browser
2. Click **"Load visualization-data.js"** button
3. Select the `visualization-data.js` file from the results directory
4. The visualization populates with network topology and UAV path

### Display Elements

**Nodes:**
- **Teal circles:** Regular ground network nodes
- **Yellow circles:** Candidate nodes (in suspicious region)
- **Red circle:** Detection node (target n*)
- **Blue circle:** UAV current position

**Trajectories:**
- **Solid blue line:** UAV's historical path (up to current time)
- **Dashed blue line:** Planned future waypoints
- **Blue halo:** UAV broadcast range visualization

**Grid:**
- **Gray background lines:** Network topology grid
- **Spacing:** 20m between nodes (configurable)

### Timeline Controls

| Control | Action |
|---------|--------|
| Slider | Scrub to any time in simulation |
| **Play** | Animate UAV movement in real-time (1x speed) |
| **Pause** | Freeze at current time |
| **Reset** | Jump back to t=0s |
| **Clear** | Unload data and reset visualizer |

### Display Options

- **Show UAV Trajectory:** Toggle historical path visualization
- **Show Waypoints:** Toggle planned future path
- **Highlight Candidates:** Color candidate nodes differently
- **Show Grid Background:** Show/hide grid lines

### Info Panel

**Simulation Results:**
- Detection status (YES/NO)
- Detection time (seconds)
- Grid configuration
- UAV path length (meters)
- Cooperation gain percentage

**Simulation Config:**
- Grid spacing
- Number of fragments
- Total simulation time
- UAV speed

## Key Concepts

### Fragment Dissemination
The simulation models dissemination of K fragments of a data file across an N×N grid:

1. **Master file:** Confidence 0.90
2. **Fragment generation:** Pixel-stride interleaving (416×416×3 image)
3. **Evidence formula:** p_i = 1 - (1-0.9)^(pixels_i/total_pixels)
4. **Total confidence:** C = 1 - ∏(1-p_i) for all received fragments

### UAV Trajectory Planning
Uses **Greedy Maximum Coverage (GMC)** algorithm:

1. **Candidates:** Suspicious region nodes (default: 30% of network)
2. **Greedy loop:** Select waypoint maximizing coverage gain per distance cost
3. **Cell-aware:** If waypoint covers >30% of cell, include all cell members
4. **Score:** gain / (distance^α + eps) where α=1.0

### Cooperation Trigger
Ground nodes cooperate to exchange fragments:

1. **Cooperation threshold (τ_coop):** Default 0.30 (30% confidence)
2. **Alert threshold (τ_alert):** Default 0.75 (75% confidence)
3. **Trigger:** If node reaches τ_alert, detection event fires
4. **Detection node:** n* = randomly selected seed node from candidates

### Thresholds

| Parameter | Symbol | Default | Meaning |
|-----------|--------|---------|---------|
| Cooperation Threshold | τ_coop | 0.30 | Confidence needed to start sharing fragments |
| Alert Threshold | τ_alert | 0.75 | Confidence needed to trigger detection alert |
| Suspicious Percent | ρ | 0.30 | Fraction of nodes marked as candidates |
| Cell Coverage | β | 0.30 | Coverage threshold for cell-aware expansion |
| GMC Alpha | α | 1.0 | Distance cost exponent in trajectory scoring |

## Integration with Research

### Reproducing Paper Results (Fig. 3)

Paper baseline: Tdetect vs. grid size N ∈ {100, 400, 900, 1225}

```bash
# Generate 100 runs for N=100
for seed in {1..100}; do
  ./build/scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$(printf "%03d" $seed)
done

# Generate 100 runs for N=400
for seed in {1..100}; do
  ./build/scenario-1-single-uav --gridSize=20 --seed=$seed --runId=$(printf "%03d" $((seed+100)))
done

# Analyze results (requires Python analysis script)
python3 tools/analysis/batch-analyzer.py data/results/scenario-1/ > results.txt
```

### Comparing Trajectory Algorithms

```bash
# GMC (cell-aware)
./build/scenario-1-single-uav --gridSize=20 --useGmc=true --seed=1 --runId=1

# Nearest-neighbor baseline
./build/scenario-1-single-uav --gridSize=20 --useGmc=false --seed=1 --runId=2

# Compare UAV path lengths in visualization
```

### Channel Model Validation

```bash
# Realistic CC2420 PHY (with path loss, shadowing, BER)
./build/scenario-1-single-uav --usePerfectChannel=false --seed=1

# Ideal channel (upper bound on performance)
./build/scenario-1-single-uav --usePerfectChannel=true --seed=1

# Expected PER with CC2420: ~35.3% (from paper Section V.C)
```

## Architecture Overview

### Module Structure
```
wsn-uav/
├── models/
│   ├── common/          (parameters, types, statistics)
│   └── application/     (fragments, confidence, dissemination app)
├── helper/              (topology, trajectory, result writing)
└── examples/            (scenario-1-single-uav entry point)
```

### No Global State
- ✅ All state encapsulated in objects (no g_globalVariable patterns)
- ✅ Configurable paths (no hardcoded /tmp or relative paths)
- ✅ Thread-safe result collection via StatisticsCollector
- ✅ Clean separation of concerns (fragments ≠ dissemination ≠ network)

### Clean Abstractions
- **FragmentModel:** Pure data (no ns3 dependency)
- **ConfidenceModel:** State machine (no network ops)
- **FragmentDisseminationApp:** ns3::Application (handles protocol)
- **TopologyHelper:** Network layout (no simulation dependency)
- **TrajectoryHelper:** Path planning (no simulation dependency)
- **ResultWriter:** Output formatting (no simulation dependency)

## Troubleshooting

### Q: Simulation runs but doesn't detect
**A:** Detection requires:
1. Sufficient simulation time (try --simTime=500+)
2. UAV reaching detection node's vicinity
3. Detection node receiving enough fragments to exceed τ_alert
4. Try lower thresholds: --alertThreshold=0.50

### Q: Visualization shows stationary UAV
**A:** This occurs when:
1. UAV completes trajectory quickly (small grid or few candidates)
2. Try larger grid: --gridSize=20
3. Check trajectories.csv for actual position history

### Q: Can't open wsn-uav-visualizer.html
**A:** 
1. Ensure file is in same directory as visualization-data.js
2. Use file:// URL or any HTTP server (no special requirements)
3. Check browser console (F12) for JavaScript errors
4. Try different browser (Chrome, Firefox, Safari all supported)

### Q: File picker shows empty
**A:**
1. Check that visualization-data.js exists in results directory
2. Verify file permissions: `chmod 644 visualization-data.js`
3. Try from command line: `open results/run-001/wsn-uav-visualizer.html`

### Q: UAV path is very short or has no waypoints
**A:**
1. GMC algorithm failed to find diverse candidates
2. Try: --suspiciousPercent=0.50 (increase candidate pool)
3. Or disable GMC: --useGmc=false (nearest-neighbor baseline)

## Performance Notes

- **100 nodes (10×10):** ~5 seconds runtime, 10 KB visualization data
- **400 nodes (20×20):** ~30 seconds runtime, 44 KB visualization data
- **900 nodes (30×30):** ~120 seconds runtime, ~100 KB visualization data
- **1225 nodes (35×35):** ~200 seconds runtime, ~140 KB visualization data

Rendering in browser: All sizes smooth on modern hardware (60 FPS).

## Advanced Usage

### Custom Network Topology
Modify `src/wsn-uav/helper/topology-helper.cc::CreateGrid()` to use different layouts (circular, random, etc.).

### Different Trajectory Algorithms
Modify `src/wsn-uav/helper/trajectory-helper.cc::PlanGmc()` to implement custom algorithms (A*, TSP, etc.).

### Real-time Monitoring
Modify `src/wsn-uav/helper/wsn-network-helper.cc::Schedule()` to add custom event logging.

### Custom Result Export
Extend `src/wsn-uav/helper/result-writer.cc` to add new CSV columns or export formats.

## References

- **Pixel-stride fragment generation:** Section IV.A (pixel interleaving algorithm)
- **Confidence model:** Section IV.B (union probability formula)
- **GMC trajectory:** Section V.A (greedy set-cover with cell awareness)
- **Cooperation protocol:** Section V.B (confidence threshold + manifest exchange)
- **Paper baseline:** Figure 3 (Tdetect vs. grid size N)

## Support

For issues or questions:
1. Check VISUALIZER_README.md for visualization-specific guidance
2. Check IMPLEMENTATION_STATUS.md for architectural details
3. Review VISUALIZER_README.md for data format documentation
4. Examine example CMake and C++ code for extending functionality
