# WSN-UAV Scenario 1 Visualization System

## Overview

The wsn-uav simulation exports results in a self-contained visualization system that requires **no local server** or installation. Simply open the HTML file with any modern web browser.

## Quick Start

1. **Run the simulation:**
   ```bash
   ./build/scenario-1-single-uav --gridSize=10 --numFragments=10 --seed=1
   ```

2. **Open the visualizer:**
   - Locate the generated `wsn-uav-visualizer.html` in the results directory
   - Double-click to open in your default browser, or:
     ```bash
     open data/results/scenario-1/run-001/wsn-uav-visualizer.html
     ```

3. **Load the simulation data (Automatic or Manual):**
   - **Automatic:** If `visualization-data.js` is in the same directory, it loads automatically
   - **Manual:** Click "Load visualization-data.js" button and select the file if needed
   - The visualization will populate with network topology and UAV trajectory

## Features

### Visualization Elements

- **Ground Nodes (teal circles):** Standard ground network nodes
- **Candidate Nodes (yellow circles):** Nodes in suspicious region selected by GMC algorithm
- **Detection Node (red circle):** The target node (n*) where detection should occur
- **UAV Trajectory (blue line):** Historical UAV path up to current time
- **UAV Position (blue circle with halo):** Current UAV location
- **Waypoints (dashed line):** Planned future UAV path

### Timeline Controls

- **Slider:** Scrub through the 0–100s (default) simulation timeline
- **Current Time Display:** Shows exact time in seconds with 0.1s precision
- **Play Button:** Animate the UAV movement in real-time (speed: 1x simulation)
- **Pause Button:** Freeze at current time
- **Reset Button:** Jump back to t=0s
- **Clear Button:** Unload current data and reset visualizer

### Display Options

- **Show UAV Trajectory:** Toggle historical path visualization
- **Show Waypoints:** Toggle planned future path
- **Highlight Candidates:** Toggle candidate node coloring
- **Show Grid Background:** Toggle grid line background

### Information Panel

**Simulation Results:**
- Detection status (YES/NO) and time
- Grid configuration (size, spacing, total nodes)
- Candidate node count
- UAV path length (meters)
- Cooperation gain percentage

**Simulation Config:**
- Grid spacing
- Number of fragments
- Total simulation time
- UAV speed

## Output Files

Each simulation run generates:

1. **visualization-data.js** (13 KB example)
   - Self-contained JavaScript constant: `WSN_UAV_DATA`
   - No external dependencies
   - Includes: config, nodes array, UAV trajectory array

2. **wsn-uav-visualizer.html** (27 KB)
   - Standalone HTML with embedded CSS and JavaScript
   - Loads visualization-data.js directly (file picker dialog)
   - Canvas-based rendering for performance

3. **metrics.csv**
   - Detection results and statistics
   - Suitable for batch analysis across multiple runs

4. **trajectories.csv**
   - UAV position samples (time, x, y, z)
   - One record per second during simulation

5. **packets.csv**
   - Individual packet records (source, destination, fragment ID, success, RSSI)
   - For detailed link analysis

6. **config.txt**
   - Human-readable simulation parameters

## Data Format

The `visualization-data.js` file contains:

```javascript
const WSN_UAV_DATA = {
  config: {
    gridSize: 10,              // N × N nodes
    gridSpacing: 20,           // meters
    numNodes: 100,             // gridSize²
    numUavs: 1,                // always 1 for Scenario 1
    numFragments: 10,          // K fragments
    simTime: 100,              // total seconds
    detectionTime: -1,         // -1 if not detected
    detected: false,           // detection success
    uavPathLength: 154.57,     // meters (from GMC plan)
    cooperationGain: 0.0000    // frags_coop / total_frags
  },
  nodes: [
    { id: 0, x: 0.0, y: 0.0, z: 0.0, isCandidate: false, isDetectionNode: false },
    // ... 100 nodes total
  ],
  uavTrajectory: [
    { t: 0.0, x: 0.0, y: 0.0, z: 20.0 },
    // ... 100 position samples (t = 0, 1, 2, ..., 99 seconds)
  ]
};
```

## Batch Visualization

To visualize multiple runs side-by-side:

1. Copy `wsn-uav-visualizer.html` to each run's directory
2. Run simulations for different parameters:
   ```bash
   for seed in {1..10}; do
     ./build/scenario-1-single-uav --seed=$seed --runId=$seed
     cp src/wsn-uav/examples/wsn-uav-visualizer.html data/results/scenario-1/run-$(printf %03d $seed)/
   done
   ```
3. Open each HTML file in a separate browser tab
4. Load each `visualization-data.js` file independently

## Browser Compatibility

The visualizer is tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Modern browsers with HTML5 Canvas and ES6 support required.

## Technical Notes

- **No server required:** Uses browser's File API to load local JSON
- **Canvas rendering:** Efficient 2D rendering for 100–1225 nodes
- **Linear interpolation:** UAV position smoothly interpolated between seconds
- **Responsive layout:** Adapts to window resize
- **Color scheme:** Accessible (colorblind-friendly teal, yellow, red, blue)

## Common Issues

**Q: "Load visualization-data.js button doesn't work"**
- A: Ensure the HTML and JS files are in the same directory
- Make sure your browser allows File API (some sandboxed environments block this)

**Q: UAV trajectory appears stationary**
- A: This is expected if simulation runs short (<10 seconds) or all waypoints are at same location
- Check GMC plan with `--useGmc=false` (nearest-neighbor) for comparison

**Q: Detection node not highlighted**
- A: If detection never occurred (detectionTime=-1), the detection node circle stays standard size
- This is expected for long simulations with high thresholds

**Q: Grid too large/small on screen**
- A: Window zoom (Ctrl+/-) or fullscreen (F11) to adjust view
- Visualization auto-scales to canvas size

## Integration with Paper Results

For reproducing paper baseline (Fig. 3):

```bash
# Run 100 seeds for N = 10×10 = 100 nodes
for seed in {1..100}; do
  ./build/scenario-1-single-uav --gridSize=10 --numFragments=10 --seed=$seed
done

# Process metrics.csv from all runs
python3 tools/analysis/batch-analyzer.py data/results/scenario-1/ > results.txt
```

Compare Tdetect mean and variance against paper Fig. 3 values for validation.
