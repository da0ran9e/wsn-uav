# Auto-Load Feature for Visualization

## What Changed

The `wsn-uav-visualizer.html` now **automatically loads** `visualization-data.js` if it's in the same directory.

### Before (Manual)
```
1. Open wsn-uav-visualizer.html
2. Click "Load visualization-data.js" button
3. Select visualization-data.js file
4. Wait for data to appear
```

### After (Automatic)
```
1. Open wsn-uav-visualizer.html
2. Visualization loads automatically!
```

## How It Works

1. **Auto-Detection:** When the HTML loads, it checks for `visualization-data.js` in the same directory
2. **Fallback:** If file not found, the file picker button remains available for manual loading
3. **Script Injection:** Uses dynamic script loading to include the data file

## Benefits

✅ **Zero User Friction**
- Open HTML file → see visualization immediately
- No file picker needed
- Faster workflow

✅ **Backward Compatible**
- Manual file picker still works if auto-load fails
- Works with file:// URLs (local files)
- No server required

✅ **Batch Visualization**
- Copy HTML and data.js to results directory
- Double-click HTML
- Instantly see results

## Implementation Details

```javascript
// Auto-load on initialization
autoLoadData() {
    const script = document.createElement('script');
    script.src = 'visualization-data.js?t=' + Date.now();
    script.onerror = () => {
        console.log('File not found, using file picker');
    };
    script.onload = () => {
        if (typeof WSN_UAV_DATA !== 'undefined') {
            this.data = WSN_UAV_DATA;
            this.onDataLoaded();
            // Hide file picker since data loaded
            document.getElementById('fileInput').style.display = 'none';
            document.querySelector('.file-input-label').style.display = 'none';
        }
    };
    document.head.appendChild(script);
}
```

## Typical Workflow

```bash
# Run simulation
./build/scenario-1-single-uav --gridSize=10 --seed=1

# Results in: ./data/results/scenario-1/run-001/
# Contains:
#   - wsn-uav-visualizer.html    (auto-load enabled)
#   - visualization-data.js       (auto-loaded)

# Open visualization
open data/results/scenario-1/run-001/wsn-uav-visualizer.html

# → Visualization loads automatically, no file picker needed!
```

## Troubleshooting

**Q: File picker still shows**
- A: Auto-load failed (file not in same directory)
  - Solution: Ensure `visualization-data.js` is in same folder as HTML
  - Or: Use manual file picker

**Q: Data not showing after opening**
- A: Check browser console (F12) for errors
  - Verify `visualization-data.js` exists
  - Ensure file has correct format

## File Structure

```
results/run-001/
├── wsn-uav-visualizer.html      ← Open this
├── visualization-data.js         ← Auto-loads
├── metrics.csv
├── trajectories.csv
└── ...
```

All files must be in the same directory for auto-load to work.
