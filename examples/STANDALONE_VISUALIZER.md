# Standalone Visualizer (All-in-One)

## Problem Solved

The original `wsn-uav-visualizer.html` + `visualization-data.js` approach had issues with `file://` protocol CORS restrictions when opening locally in browsers.

**Solution:** Generate a single `wsn-uav-standalone.html` file that contains everything - visualizer, CSS, JavaScript, AND data all in one file.

## Quick Start

### Method 1: Auto-Generate (Recommended)

After running a simulation:

```bash
# Simulation generates results in ./data/results/scenario-1/run-001/
./build/scenario-1-single-uav --gridSize=10 --seed=1

# Generate standalone HTML (combines visualizer + data into one file)
python3 src/wsn-uav/examples/generate-standalone-viz.py ./data/results/scenario-1/run-001/

# Open in browser (double-click or command below)
open data/results/scenario-1/run-001/wsn-uav-standalone.html
```

That's it! The visualization loads instantly with no dependencies.

### Method 2: Manual (Fallback)

If auto-generation fails:

```bash
# Use the regular visualizer with file picker
open data/results/scenario-1/run-001/wsn-uav-visualizer.html

# In browser: Click "Load visualization-data.js" button
# Select the visualization-data.js file from the same directory
```

## What Gets Generated

```
data/results/scenario-1/run-001/
├── wsn-uav-standalone.html      ← NEW: All-in-one file (~40-75 KB)
├── wsn-uav-visualizer.html      (original, needs separate .js file)
├── visualization-data.js        (data file)
└── [other CSV/config files]
```

## File Sizes

| File | Size | Contains |
|------|------|----------|
| wsn-uav-standalone.html (100 nodes) | 42 KB | Visualizer + CSS + JS + embedded data |
| wsn-uav-standalone.html (400 nodes) | 75 KB | Visualizer + CSS + JS + embedded data |

## Advantages of Standalone

✅ **Single File:** No file dependencies or paths needed
✅ **Works Offline:** Download and share as email attachment
✅ **No Server:** Opens with `file://` protocol in all browsers
✅ **Portable:** Copy anywhere, open directly
✅ **Fast Loading:** Data already embedded, no fetch needed

## Usage

```bash
# 1. Run simulation (generates visualization-data.js)
./build/scenario-1-single-uav --gridSize=10 --seed=1

# 2. Generate standalone file
python3 src/wsn-uav/examples/generate-standalone-viz.py data/results/scenario-1/run-001/

# 3. Open visualization (just one file!)
open data/results/scenario-1/run-001/wsn-uav-standalone.html

# That's it - no file picker, no copy-paste, instant visualization!
```

## Batch Generation

Generate standalone files for all runs:

```bash
for run_dir in data/results/scenario-1/run-*/; do
    python3 src/wsn-uav/examples/generate-standalone-viz.py "$run_dir"
    echo "Generated: $run_dir/wsn-uav-standalone.html"
done

# Now open each standalone.html file directly
open data/results/scenario-1/run-001/wsn-uav-standalone.html
open data/results/scenario-1/run-002/wsn-uav-standalone.html
```

## Script Details

**Location:** `src/wsn-uav/examples/generate-standalone-viz.py`

**What it does:**
1. Reads `visualization-data.js` from results directory
2. Extracts the embedded JSON data
3. Reads the HTML template
4. Injects data as a JavaScript constant in the HTML
5. Outputs `wsn-uav-standalone.html`

**Requirements:** Python 3.6+

## Comparing the Approaches

### Original Approach (Separate Files)
```
Files needed: wsn-uav-visualizer.html + visualization-data.js
CORS issue: Yes (file:// protocol)
Setup: Click file picker, select file
Browser support: Most modern browsers
Size: 27 KB (HTML) + 13-140 KB (data)
```

### Standalone Approach (All-in-One)
```
Files needed: wsn-uav-standalone.html only
CORS issue: No
Setup: Double-click and open
Browser support: All modern browsers
Size: 40-75 KB (everything)
Sharing: Easy (single file)
```

## Which to Use?

- **Use Standalone** for:
  - Viewing results locally
  - Sharing results with others
  - Presentations or reports
  - Email attachments
  - USB drives

- **Use Separate Files** for:
  - Updating just the data without regenerating HTML
  - Custom visualizer modifications
  - Batch processing scripts

## Troubleshooting

**Q: "Template not found" error**
- A: Run script from ns-3 root directory
  ```bash
  cd ns-3-dev-git-ns-3.46
  python3 src/wsn-uav/examples/generate-standalone-viz.py ./data/results/scenario-1/run-001/
  ```

**Q: "Visualization-data.js not found" error**
- A: Make sure simulation has completed and created the file
  ```bash
  # Check if file exists
  ls -lh data/results/scenario-1/run-001/visualization-data.js
  ```

**Q: Generated file is very small (few KB)**
- A: Data extraction failed, try running simulation again

**Q: Standalone HTML doesn't load in browser**
- A: Try Firefox or Chrome (best file:// support)
- Or: Check browser console (F12) for JavaScript errors

## Integration with Simulation

The standalone generation is optional - the regular simulation workflow is unchanged:

```bash
# Simulation outputs same files as always
./build/scenario-1-single-uav --gridSize=10 --seed=1

# results/run-001/ now contains:
# - visualization-data.js      (auto-generated)
# - wsn-uav-visualizer.html    (copied from examples/)
# - metrics.csv
# - trajectories.csv
# - etc.

# NEW: Generate standalone version
python3 src/wsn-uav/examples/generate-standalone-viz.py ./data/results/scenario-1/run-001/

# Results/run-001/ now also contains:
# - wsn-uav-standalone.html    (NEW! All-in-one file)
```

## Advanced: Scripted Workflow

```bash
#!/bin/bash
# run-and-visualize.sh

GRID_SIZE=${1:-10}
NUM_SEEDS=${2:-10}

for seed in $(seq 1 $NUM_SEEDS); do
    echo "Running seed $seed..."
    ./build/scenario-1-single-uav --gridSize=$GRID_SIZE --seed=$seed --runId=$seed

    RUN_DIR="./data/results/scenario-1/run-$(printf %03d $seed)"
    echo "Generating standalone visualizer..."
    python3 src/wsn-uav/examples/generate-standalone-viz.py "$RUN_DIR"
done

echo "All done! Open any of these files:"
for f in ./data/results/scenario-1/run-*/wsn-uav-standalone.html; do
    echo "  $f"
done
```

Run with:
```bash
chmod +x run-and-visualize.sh
./run-and-visualize.sh 10 5  # 10×10 grid, 5 seeds
```

## Technical Details

### How Embedding Works

**Original:**
```html
<script src="visualization-data.js"></script>  <!-- Loaded from file -->
```

**Standalone:**
```html
<script>
    // Data embedded directly
    const WSN_UAV_DATA = {
        config: {...},
        nodes: [{...}, ...],
        uavTrajectory: [{...}, ...]
    };
</script>
```

### Data Conversion

The script converts JavaScript object notation to JSON:
- Input: `{gridSize: 10, ...}` (JavaScript)
- Output: `{"gridSize": 10, ...}` (Valid JSON)

### File Size Analysis

- HTML template: ~28 KB
- Data overhead: varies with node count
  - 100 nodes (10×10): ~14 KB
  - 400 nodes (20×20): ~47 KB
  - 900 nodes (30×30): ~100 KB

Total standalone files are roughly: template + data + small overhead

## Summary

| Feature | Regular | Standalone |
|---------|---------|-----------|
| File picker | ✓ | ✗ |
| Single file | ✗ | ✓ |
| Works offline | ✓ | ✓ |
| Easy sharing | ✗ | ✓ |
| Setup time | ~30 sec | ~2 sec |
| Browser compatibility | Good | Excellent |
| CORS issues | Possible | No |

Both approaches work. Choose based on your use case!
