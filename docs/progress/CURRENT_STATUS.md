# WSN-UAV Simulator - Current Status

**Last Updated:** 2026-05-05  
**Overall Status:** ✅ **PHASE 1 EXTENDED COMPLETE**

---

## What's Working

### ✅ Core Simulation
- Single UAV (Scenario-1): 14.69s detection
- 3-UAV cooperative (Scenario-3): 10-11s detection  
- Grid sizes: 10×10 to 70×70
- Fragments: 10 per scenario

### ✅ Multi-UAV Features
- Load-balanced fragment distribution (round-robin by size)
- Adaptive speed adjustment (0.4 - 1.2 factor range)
- Dynamic trajectory planning (k scales with grid size)
- Random path generation (each UAV unique)
- Ground cooperation (enabled)

### ✅ Advanced Features (New This Session)
- **GMC Algorithm:** Dynamic k calculation based on coverage geometry
- **Per-UAV Path Complexity:** Fast UAV 20% more waypoints
- **Speed Differentiation:** 1.84× ratio (slow 32 m/s → fast 59 m/s at 80 m/s base)
- **Random Initialization:** Each UAV k-means with unique seed
- **Return Path Correction:** UAVs return to physical position

---

## Performance Summary

### Detection Times (base speed 80 m/s)
| Grid | Time | Status |
|------|------|--------|
| 10×10 | 10.31s | ✓ |
| 30×30 | 10.03s | ✓ |
| 50×50 | 10.93s | ✓ |
| 70×70 | 10.31s | ✓ |

### Waypoint Distribution (50×50 grid)
- UAV 0 (slow, 32 m/s): 76 waypoints
- UAV 1 (medium, 39.5 m/s): 76 waypoints
- UAV 2 (fast, 59 m/s): 94 waypoints

### Coverage
- All grids: Full coverage ✓
- All candidates reachable ✓
- No dead zones ✓

---

## Key Parameters

```cpp
// Speed adjustment
minSpeedFactor = 0.4   // Slow UAV
maxSpeedFactor = 1.2   // Fast UAV

// Trajectory complexity
MAX_KMEANS_CENTROIDS = 128  // Supports large grids
k = max(minCentroids, nodeBasedCentroids)

// Path randomization
randomSeed = uavId + 1000 + configSeed
```

---

## Quick Start

```bash
# Build
python3.10 ./ns3 build

# Run with doubled speed difference
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=50 --seed=1 --uavSpeed=80"

# Check results
open src/wsn-uav/results/scenario-3/run-001/wsn-uav-result.html
```

---

## Known Limitations

- Max centroids capped at 128 (performance)
- Very large grids (100×100+) may need larger cap
- k-means convergence: 10 iterations fixed

---

## Documentation

- **Full details:** `SESSION_ADVANCED_FEATURES.md`
- **Phase 1 Design:** `PHASE1_MULTIUAV_COOP_DESIGN.md`
- **Final Status:** `PHASE1_FINAL_STATUS.md`

---

## Next Phase Ideas

1. Adaptive speed based on coverage progress
2. ML-based k prediction for new grid sizes
3. Energy optimization
4. 100+ fragment scenarios
5. Advanced cooperation protocols
