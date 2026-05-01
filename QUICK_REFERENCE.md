# WSN-UAV Quick Reference Card

## Build & Run (Copy-Paste Commands)

```bash
# Build
cd ns-3-dev-git-ns-3.46
./ns3 build wsn-uav && ./ns3 build

# Run test (10×10 = 100 nodes)
./build/scenario-1-single-uav --gridSize=10 --seed=1

# Run paper baseline (20×20 = 400 nodes)
./build/scenario-1-single-uav --gridSize=20 --seed=1

# Open results
open data/results/scenario-1/run-001/wsn-uav-visualizer.html
```

## Visualization Workflow

1. **Browser:** Double-click `wsn-uav-visualizer.html`
2. **Auto-Load:** `visualization-data.js` loads automatically (same directory)
3. **View:** Grid + candidate nodes + detection node display appears instantly
4. **Play:** Timeline slider or Play button to animate
5. **Export:** Right-click canvas → Save image (if needed)

## Key Parameters

| Parameter | Default | Range | Effect |
|-----------|---------|-------|--------|
| `--gridSize=N` | 10 | 5-35 | Network size (N×N nodes) |
| `--numFragments=K` | 10 | 1-100 | File fragments to disseminate |
| `--simTime=S` | 500 | 10-5000 | Simulation duration (seconds) |
| `--seed=N` | 1 | 1-∞ | Random seed (for reproducibility) |
| `--cooperationThreshold` | 0.30 | 0-1 | Fragment confidence for sharing |
| `--alertThreshold` | 0.75 | 0-1 | Confidence threshold for detection |
| `--useGmc` | true | true/false | Enable GMC path planning |

## Output Files Explained

```
run-001/
├── metrics.csv              → Detection time + path length
├── trajectories.csv         → UAV position history (hourly)
├── packets.csv              → Individual packet records
├── config.txt               → Parameter summary
├── visualization-data.js    → JSON data for visualizer
└── wsn-uav-visualizer.html  → Interactive viewer
```

## Common Tasks

### Task: Test the build
```bash
./build/scenario-1-single-uav --gridSize=10 --simTime=100
```

### Task: Reproduce paper Figure 3
```bash
# Run 100 seeds for N=100
for seed in {1..100}; do
  ./build/scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$seed
done
# Results in: data/results/scenario-1/run-001 through run-100
```

### Task: Compare trajectory algorithms
```bash
# GMC (cell-aware)
./build/scenario-1-single-uav --gridSize=20 --useGmc=true --seed=1

# Nearest-neighbor baseline
./build/scenario-1-single-uav --gridSize=20 --useGmc=false --seed=1

# Compare "UAV path length" values in visualization
```

### Task: Faster detection
```bash
# Lower confidence thresholds
./build/scenario-1-single-uav \
  --cooperationThreshold=0.15 \
  --alertThreshold=0.50 \
  --simTime=200
```

### Task: Larger network
```bash
./build/scenario-1-single-uav \
  --gridSize=20 \    # 400 nodes
  --simTime=500
```

### Task: View trajectory in spreadsheet
```bash
# Export trajectories.csv to Excel/Numbers
open -a Numbers data/results/scenario-1/run-001/trajectories.csv

# Plot with Python
python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('data/results/scenario-1/run-001/trajectories.csv')
plt.plot(df['x_meters'], df['y_meters'], 'b-')
plt.show()
EOF
```

## Architecture Quick View

```
Fragment model ──→ Confidence model ──→ Dissemination app ──→ Statistics
     ↓                     ↓                    ↓                  ↓
  Pixel-stride      Union probability     Protocol logic      Result export
  interleaving      calculation           (broadcast/coop)    (CSV + JSON)
     
Topology ──→ Trajectory ──→ Network Helper ──→ Simulator ──→ Result Writer
     ↓            ↓               ↓                ↓              ↓
Grid layout   GMC planning   Orchestration    NS-3 runtime   HTML/JS/CSV
Cells/leaders Greedy cover   Building/running Mobil/Radios   Visualization
Candidates    Set-cover      Results collect  Events
```

## Visualization Color Scheme

| Color | Meaning |
|-------|---------|
| 🔵 Blue | UAV and trajectory |
| 🟡 Yellow | Candidate nodes (suspicious) |
| 🔴 Red | Detection node (target n*) |
| 🟦 Teal | Regular ground nodes |
| ⬜ Gray | Grid background |

## Detection Status Indicators

### ✅ Detected (Green)
```
Detection: YES at 45.234s
Detection node 6 exceeded τ_alert=0.75
```

### ❌ Not Detected (Red)
```
Detection: NO (timeout at 500s)
No node reached alert threshold
```

## Performance (Approximate)

| Grid Size | Nodes | Time | Data |
|-----------|-------|------|------|
| 10×10 | 100 | ~5s | 13 KB |
| 20×20 | 400 | ~30s | 44 KB |
| 30×30 | 900 | ~120s | 100 KB |
| 35×35 | 1225 | ~200s | 140 KB |

All visualization files render smoothly in browser (60 FPS).

## Code Locations

| Component | File |
|-----------|------|
| Fragment algorithm | `models/application/fragment-model.cc` |
| Confidence calc | `models/application/confidence-model.cc` |
| Protocol logic | `models/application/fragment-dissemination-app.cc` |
| Topology | `helper/topology-helper.cc` |
| GMC trajectory | `helper/trajectory-helper.cc` |
| Network setup | `helper/wsn-network-helper.cc` |
| Parameters | `models/common/parameters.h` |
| Visualization | `examples/wsn-uav-visualizer.html` |

## Troubleshooting: 30-Second Guide

| Problem | Solution |
|---------|----------|
| Visualization won't load | Check file picker target file exists |
| No detection | Increase simTime, lower alertThreshold |
| UAV doesn't move | Check trajectories.csv for data |
| Build fails | `./ns3 clean` then `./ns3 build` |
| Slow rendering | Close other browser tabs, use Chrome |

## Paper References

- **Fragment generation:** Section IV.A (pixel-stride interleaving)
- **Confidence model:** Section IV.B (union probability C = 1-∏(1-p_i))
- **GMC trajectory:** Section V.A (greedy maximum coverage)
- **Cooperation:** Section V.B (τ_coop and τ_alert thresholds)
- **Figure 3:** Tdetect vs grid size N ∈ {100, 400, 900, 1225}

## Key Paper Constants

| Constant | Value | Field |
|----------|-------|-------|
| Master confidence | 0.90 | Fragment evidence |
| τ_coop | 0.30 | Cooperation trigger |
| τ_alert | 0.75 | Detection trigger |
| ρ (suspicious) | 0.30 | Candidate fraction |
| β (cell coverage) | 0.30 | Cell-aware threshold |
| α (GMC distance) | 1.0 | Trajectory scoring |
| Grid spacing | 20 m | Network layout |
| Cell radius | 80 m | Hex cells |
| Broadcast radius | 50 m | UAV coverage |

---

**For detailed docs:** See USER_GUIDE.md, VISUALIZER_README.md, IMPLEMENTATION_STATUS.md
