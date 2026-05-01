# WSN-UAV Quick Reference

## ⚠️ Prerequisites

**Python 3.13.x required** (not 3.14+)
```bash
python3 --version  # Should show 3.13.x
# If 3.14: brew unlink python@3.14 && brew link python@3.13
```

See [IMPORTANT_SETUP_NOTES.md](IMPORTANT_SETUP_NOTES.md) for details.

## One-Line Setup
```bash
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46 && \
./ns3 clean && \
./ns3 configure --enable-examples --enable-modules=wsn-uav && \
./ns3 build
```

## Run Commands

### Single run
```bash
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
```

### Batch: 10 seeds, grid 10×10
```bash
for s in {1..10}; do ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=$s --runId=$s"; done
```

### Batch: Paper baseline (N=100,400,900,1225)
```bash
for g in 10 20 30 35; do for s in {1..10}; do 
  ./ns3 run "scenario-1-single-uav --gridSize=$g --seed=$s --runId=${s}_g${g}"
done; done
```

### With custom parameters
```bash
./ns3 run "scenario-1-single-uav --gridSize=25 --numFragments=50 --simTime=400 --seed=1"
```

## Output Location
```
src/wsn-uav/results/scenario-1/run-001/
├── wsn-uav-result.html    ← Open in browser
├── metrics.csv             ← Tdetect, pathLength, cooperationGain
├── trajectories.csv        ← UAV position trace
├── packets.csv             ← Fragment transmissions
└── config.txt              ← Parameters used
```

## Key Parameters

| Parameter | Default | Example |
|-----------|---------|---------|
| `--gridSize` | 10 | 20 (20×20 nodes) |
| `--numFragments` | 10 | 50 |
| `--seed` | 1 | Any integer |
| `--runId` | 1 | Run identifier |
| `--simTime` | 500s | 300, 1000 |
| `--alertThreshold` | 0.75 | Detection at 75% fragments |
| `--suspiciousPercent` | 0.30 | 30% of nodes are candidates |

## Important Files

| File | Purpose |
|------|---------|
| `src/wsn-uav/examples/CMakeLists.txt` | Example build config (use `build_lib_example`) |
| `src/wsn-uav/CMakeLists.txt` | Main module config |
| `src/wsn-uav/examples/scenario-1-single-uav.cc` | Main entry point |
| `src/wsn-uav/helper/wsn-network-helper.cc` | Orchestrator |
| `src/wsn-uav/models/application/fragment-dissemination-app.cc` | Core simulation logic |

## Build Issues

### If build fails
```bash
./ns3 clean
cmake -Bcmake-cache -DCMAKE_BUILD_TYPE=Release
./ns3 build
```

### If ns3 run not found
```bash
./ns3 configure --enable-examples --enable-modules=wsn-uav
./ns3 build
```

## Detection Insights

- **10×10 grid, 10 fragments:** Detection at ~22s (small area, high density)
- **20×20 grid, 40 fragments:** Usually no detection (sparse coverage)
- **Threshold:** Needs 8/10 fragments (80%) with default alertThreshold=0.75
- **Candidates:** ~30% of nodes (suspiciousPercent=0.30)
- **Detection node:** Random from candidates (varies by seed)

## Documentation

| Document | Contains |
|----------|----------|
| `README.md` | Full overview, session history |
| `QUICKREF.md` | This file |
| `session5_ns3_run_integration.md` | Detailed ns3 run fix explanation |

## After Session

Just update:
- `session5_ns3_run_integration.md` with any new findings
- This `QUICKREF.md` with new common commands
- Add new session file: `session6_*.md` for next work
