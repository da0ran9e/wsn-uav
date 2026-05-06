# Configuration & Execution Guide - WSN-UAV Simulator

**Last Updated:** 2026-05-05  
**Purpose:** How to run all simulation scenarios with proper configuration  
**Status:** Complete

---

## 🚀 Quick Start

### Prerequisites
```bash
# Verify Python 3.10 (required for NS-3, NOT 3.14)
python3 --version

# If using Python 3.14, switch to 3.10
brew unlink python@3.14
brew link python@3.10
```

### Build Once
```bash
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46
./ns3 clean
./ns3 configure --enable-examples --enable-modules=wsn-uav
./ns3 build
```

---

## 📋 Scenario 1: Single UAV Baseline

**Purpose:** Baseline detection performance, backward compatibility verification

### Basic Run
```bash
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
```

### Full Configuration with All Parameters
```bash
./ns3 run "scenario-1-single-uav \
  --gridSize=10 \
  --gridSpacing=20.0 \
  --numFragments=10 \
  --uavAltitude=20.0 \
  --uavSpeed=20.0 \
  --broadcastInterval=0.2 \
  --startupDuration=5.0 \
  --cooperationThreshold=0.30 \
  --alertThreshold=0.75 \
  --suspiciousPercent=0.30 \
  --simTime=500.0 \
  --seed=1 \
  --runId=1 \
  --usePerfectChannel=false \
  --useGmc=true"
```

### Configuration Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| gridSize | int | 10 | 5-50 | Grid dimension (N×N nodes) |
| gridSpacing | double | 20.0 | 10-50 | Distance between nodes (m) |
| numFragments | int | 10 | 1-20 | File fragments to distribute |
| uavAltitude | double | 20.0 | 10-100 | UAV flight altitude (m) |
| uavSpeed | double | 20.0 | 5-50 | UAV speed (m/s) |
| broadcastInterval | double | 0.2 | 0.1-1.0 | Broadcast interval (s) |
| startupDuration | double | 5.0 | 1-20 | Startup phase (s) |
| cooperationThreshold | double | 0.30 | 0-1.0 | Coop trigger (confidence) |
| alertThreshold | double | 0.75 | 0-1.0 | Detection trigger (confidence) |
| suspiciousPercent | double | 0.30 | 0-1.0 | Suspicious region size |
| simTime | double | 500.0 | 10-1000 | Total simulation time (s) |
| seed | int | 1 | 1-∞ | RNG seed (reproducible runs) |
| runId | int | 1 | 1-∞ | Run identifier |
| usePerfectChannel | bool | false | true/false | Ideal vs realistic channel |
| useGmc | bool | true | true/false | GMC vs nearest-neighbor |

### Expected Output

**Metrics CSV:**
```
metric,value
detected,true
detection_time_seconds,14.69
uav_count,1
uav_0_path_length_meters,662.9
total_uav_path_length_meters,662.9
cooperation_overlap_ratio,0
cooperation_gain,0
candidate_nodes,30
```

**Visualization:**
```
open src/wsn-uav/results/scenario-1/run-001/wsn-uav-result.html
```

### Batch Test (Multiple Seeds)
```bash
for seed in 1 5 10 25 50; do
  ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$seed"
done
# Creates 5 runs with different random seeds
# Check: src/wsn-uav/results/scenario-1/run-*/metrics.csv
```

---

## 📋 Scenario 2: Dual UAV (If Available)

**Purpose:** Transition from single to multi-UAV

### Run Scenario-2 (if implemented)
```bash
./ns3 run "scenario-2-multi-uav-2 --gridSize=10 --seed=1 --runId=1"
```

---

## 📋 Scenario 3: Multi-UAV Cooperative (Main New Feature)

**Purpose:** 3-UAV cooperative with size-based load balancing

### Basic Run (Default Settings)
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --seed=1 --runId=1"
```

### Full Configuration (All Options)
```bash
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --gridSpacing=20.0 \
  --numFragments=10 \
  --fragmentMinSizeBytes=100 \
  --fragmentMaxSizeBytes=20000 \
  --numUavs=3 \
  --uavAltitude=20.0 \
  --uavSpeed=20.0 \
  --broadcastInterval=0.2 \
  --startupDuration=5.0 \
  --cooperationThreshold=0.30 \
  --alertThreshold=0.75 \
  --suspiciousPercent=0.30 \
  --simTime=500.0 \
  --seed=1 \
  --runId=1 \
  --useLoadBasedSpeed=true \
  --minSpeedFactor=0.6 \
  --maxSpeedFactor=1.0 \
  --usePerfectChannel=false \
  --useGmc=true"
```

### Additional Parameters (Phase 1)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| fragmentMinSizeBytes | int | 100 | Min fragment size (bytes) |
| fragmentMaxSizeBytes | int | 20000 | Max fragment size (bytes) |
| numUavs | int | 3 | Number of UAVs (2-10) |
| useLoadBasedSpeed | bool | true | Enable speed by load |
| minSpeedFactor | double | 0.6 | Min speed = baseSpeed × 0.6 |
| maxSpeedFactor | double | 1.0 | Max speed = baseSpeed × 1.0 |

### Expected Output

**Metrics CSV:**
```
metric,value
detected,true
detection_time_seconds,17.74
uav_count,3
uav_0_path_length_meters,680.2
uav_1_path_length_meters,650.5
uav_2_path_length_meters,658.1
total_uav_path_length_meters,1988.8
cooperation_overlap_ratio,0.45
cooperation_gain,0.25
candidate_nodes,30
```

**Per-UAV Log Output:**
```
UAV 0 assigned 4 fragments, total size: 40200 bytes
  Load factor: 1.00, speed factor: 0.60, adjusted speed: 12.0 m/s
  Trajectory planned: 5 waypoints, 680m distance

UAV 1 assigned 3 fragments, total size: 35500 bytes
  Load factor: 0.88, speed factor: 0.65, adjusted speed: 13.0 m/s
  Trajectory planned: 4 waypoints, 651m distance

UAV 2 assigned 3 fragments, total size: 23200 bytes
  Load factor: 0.58, speed factor: 0.73, adjusted speed: 14.6 m/s
  Trajectory planned: 4 waypoints, 658m distance
```

### Different Grid Sizes

**Small Grid (5×5 = 25 nodes):**
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=5 --seed=1 --simTime=100"
# Fast execution: ~30 seconds, good for testing
```

**Medium Grid (10×10 = 100 nodes):**
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --seed=1 --simTime=500"
# Standard execution: ~2 minutes, typical test
```

**Large Grid (30×30 = 900 nodes):**
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=30 --seed=1 --simTime=500"
# Long execution: ~10 minutes, comprehensive test
```

**Very Large Grid (50×50 = 2500 nodes):**
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=50 --seed=1 --simTime=500"
# Extended execution: ~30+ minutes, scalability test
```

### Configuration Variants

**Variant A: Light Fragments Only**
```bash
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --numFragments=10 \
  --fragmentMinSizeBytes=100 \
  --fragmentMaxSizeBytes=1000 \
  --numUavs=3"
# Light load: all UAVs fly ~20 m/s
```

**Variant B: Heavy Fragments Only**
```bash
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --numFragments=10 \
  --fragmentMinSizeBytes=10000 \
  --fragmentMaxSizeBytes=50000 \
  --numUavs=3"
# Heavy load: UAV0 ~8 m/s, UAV2 ~20 m/s
```

**Variant C: Perfect Channel (No Fading)**
```bash
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --numUavs=3 \
  --usePerfectChannel=true"
# Ideal conditions: faster detection, no errors
```

**Variant D: Nearest-Neighbor Baseline**
```bash
./ns3 run "scenario-3-load-balanced-fragments \
  --gridSize=10 \
  --numUavs=3 \
  --useGmc=false"
# Compare: GMC vs simple nearest-neighbor
```

### Batch Experiment (Vary Seeds)
```bash
# Run 10 seeds for reproducibility analysis
for seed in 1 2 3 4 5 10 25 50 75 100; do
  ./ns3 run "scenario-3-load-balanced-fragments \
    --gridSize=10 --numUavs=3 --seed=$seed --runId=$seed"
done

# Analysis:
# cat src/wsn-uav/results/scenario-3/run-*/metrics.csv | grep detection_time
```

### Scalability Test (Vary UAV Count)
```bash
# Test 1, 2, 3, 5 UAVs
for numUavs in 1 2 3 5; do
  ./ns3 run "scenario-3-load-balanced-fragments \
    --gridSize=10 --numUavs=$numUavs --seed=1 --runId=uav$numUavs"
done

# Compare detection times across UAV counts
```

---

## 📊 Results Analysis

### View Metrics
```bash
# Single run
cat src/wsn-uav/results/scenario-3/run-001/metrics.csv

# Compare multiple runs
grep "detection_time" src/wsn-uav/results/scenario-3/run-*/metrics.csv

# Extract detection times
for f in src/wsn-uav/results/scenario-3/run-*/metrics.csv; do
  echo "$f:"
  grep "detection_time" "$f"
done
```

### View Trajectories
```bash
# UAV paths
head -20 src/wsn-uav/results/scenario-3/run-001/trajectories.csv

# Count waypoints per UAV
grep "^100" src/wsn-uav/results/scenario-3/run-001/trajectories.csv | wc -l  # UAV0
grep "^101" src/wsn-uav/results/scenario-3/run-001/trajectories.csv | wc -l  # UAV1
grep "^102" src/wsn-uav/results/scenario-3/run-001/trajectories.csv | wc -l  # UAV2
```

### View Packets Log
```bash
# All packets sent
head -50 src/wsn-uav/results/scenario-3/run-001/packets.csv

# Count packets per node
awk -F, '{print $2}' src/wsn-uav/results/scenario-3/run-001/packets.csv | sort | uniq -c
```

### Open HTML Visualization
```bash
# Browser view with interactive map
open src/wsn-uav/results/scenario-3/run-001/wsn-uav-result.html
```

---

## 🧪 Common Test Scenarios

### Test 1: Verify Backward Compatibility
```bash
# Should get same results as Phase 0
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1"
# Expected: detection_time_seconds ≈ 14.69s
```

### Test 2: Verify Phase 1 Works with 2 UAVs
```bash
./ns3 run "scenario-3-load-balanced-fragments --numUavs=2 --gridSize=10"
# Expected: 2 UAVs, different speeds, cooperation
```

### Test 3: Compare Load Impact
```bash
# Without speed adjustment
./ns3 run "scenario-3-load-balanced-fragments --useLoadBasedSpeed=false"

# With speed adjustment
./ns3 run "scenario-3-load-balanced-fragments --useLoadBasedSpeed=true"
# Compare: Time difference should be minimal but all frags delivered
```

### Test 4: Scalability to Large Grid
```bash
./ns3 run "scenario-3-load-balanced-fragments --gridSize=30 --numUavs=3"
# Expected: Still works, slightly longer time, linear scaling
```

### Test 5: Different Fragment Sizes
```bash
# Small fragments
./ns3 run "scenario-3-load-balanced-fragments \
  --fragmentMinSizeBytes=100 \
  --fragmentMaxSizeBytes=500"

# Large fragments
./ns3 run "scenario-3-load-balanced-fragments \
  --fragmentMinSizeBytes=10000 \
  --fragmentMaxSizeBytes=50000"
# Compare: How load distribution affects performance
```

---

## 🐛 Troubleshooting

### Build Fails
```bash
# Problem: Python 3.14 incompatible
# Solution:
brew unlink python@3.14
brew link python@3.10
./ns3 clean && ./ns3 build
```

### No Output Files
```bash
# Check output directory exists
ls -la src/wsn-uav/results/scenario-3/

# Create if missing
mkdir -p src/wsn-uav/results/scenario-3/run-001
```

### Simulation Hangs
```bash
# Kill long-running process
pkill -f "ns3.46-scenario"

# Run with timeout
timeout 300 ./ns3 run "scenario-3-load-balanced-fragments --gridSize=5"
```

### High CPU Usage
```bash
# Use perfect channel (faster)
./ns3 run "scenario-3-load-balanced-fragments --usePerfectChannel=true"

# Reduce grid size
./ns3 run "scenario-3-load-balanced-fragments --gridSize=5"
```

---

## 📝 Notes

- **Python 3.10 required:** NS-3 doesn't support 3.14+ (framework limitation)
- **Reproducibility:** Same seed produces identical results
- **Detection time:** Varies by grid size, seed, network topology
- **All fragments delivered:** Guaranteed via cooperation protocol
- **Results persist:** All files in src/wsn-uav/results/ until deleted

---

**Guide Version:** May 5, 2026  
**Ready for:** Production use, batch experiments, scalability testing
