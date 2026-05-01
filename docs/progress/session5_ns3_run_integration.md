# Session 5: NS-3 Run Integration & Build System Setup

**Date:** 2026-05-01  
**Status:** ✅ COMPLETE

## Major Accomplishment

Successfully integrated `scenario-1-single-uav` example with ns-3 build system, enabling standard `./ns3 run` workflow.

## Problem Solved

**Issue:** Could not use `./ns3 run scenario-1-single-uav` - executable not registered with ns-3 program discovery system

**Root Cause:** 
- Used simple `add_executable()` in examples/CMakeLists.txt
- Examples weren't being automatically registered with ns-3's `.lock-ns3` file
- Manual `add_subdirectory(examples)` conflicted with automatic `build_lib_scan_examples()`

**Solution:**
1. Use `build_lib_example()` macro instead of `add_executable()` in examples/CMakeLists.txt
2. Remove manual `add_subdirectory(examples)` - let ns-3 build system handle it automatically
3. Configure with `--enable-examples --enable-modules=wsn-uav` to build only wsn-uav and its examples
4. This ensures proper executable naming: `ns3.46-scenario-1-single-uav-default`

## How It Works

### Build System Flow

The ns-3 build system automatically:
1. Calls `build_lib()` for the wsn-uav module
2. Within build_lib scope, calls `build_lib_scan_examples()` 
3. `build_lib_scan_examples()` looks for `examples/` subdirectory
4. If ENABLE_EXAMPLES is set and CMakeLists.txt exists, calls `add_subdirectory(examples)`
5. At this point, `BLIB_LIBNAME` is still in scope from the parent `build_lib()` call
6. `build_lib_example()` macro can now access `BLIB_LIBNAME` to register the executable properly

### Key Configuration

**examples/CMakeLists.txt:**
```cmake
build_lib_example(
  NAME scenario-1-single-uav
  SOURCE_FILES scenario-1-single-uav.cc
  LIBRARIES_TO_LINK
    ${libwsn-uav}
    ${libcore}
    ${libnetwork}
    ${libmobility}
    ${libspectrum}
    ${libwsn}
)
```

**Main CMakeLists.txt:**
- Just needs the standard `build_lib()` call
- Do NOT call `add_subdirectory(examples)` - automatic handling is better

## Standard Workflow

```bash
# Clean everything
./ns3 clean

# Configure: enable examples for wsn-uav module only
./ns3 configure --enable-examples --enable-modules=wsn-uav

# Build all (very fast, only builds wsn-uav + dependencies)
./ns3 build

# Run with parameters (use quotes to wrap program + args)
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"

# Or with full parameters
./ns3 run "scenario-1-single-uav --gridSize=30 --numFragments=50 --seed=1 --runId=1 --simTime=300"
```

## Tested Parameter Combinations

All runs completed successfully with proper output files generated:

| Grid | Fragments | Seed | SimTime | Result | Candidates | UAV Path |
|------|-----------|------|---------|--------|------------|----------|
| 10×10 | 10 | 3 | 200s | **DETECTED at 21.8s** | 30/100 (30%) | 634.06m |
| 15×15 | 20 | 7 | 300s | No detection | 67/225 (30%) | 1332.72m |
| 20×20 | 40 | 2 | 500s | No detection | 120/400 (30%) | 1475.48m |
| 25×25 | 30 | 5 | 400s | No detection | 187/625 (30%) | 1917.40m |
| 30×30 | 50 | 1 | 300s | No detection | 270/900 (30%) | 1307.41m |

### Key Observations
- Detection triggers correctly when target node receives enough fragments (8/10 = 80% > 0.75 threshold)
- Candidate node selection consistently results in ~30% coverage (suspiciousPercent=0.30)
- UAV path length scales appropriately with grid size
- No cooperation gain yet (cooperation system functional but candidates not meeting threshold)

## Output Files

Each run generates in `src/wsn-uav/results/scenario-1/run-XXX/`:
- `metrics.csv` - Detection time, path length, cooperation gain
- `trajectories.csv` - UAV position trace with timestamps
- `packets.csv` - Individual packet records
- `config.txt` - Simulation parameters
- `wsn-uav-result.html` - Canvas visualization (open in browser)

## Build System Files Modified

**src/wsn-uav/examples/CMakeLists.txt**
- Changed from `add_executable()` to `build_lib_example()`
- Proper ns-3 macro integration

**src/wsn-uav/CMakeLists.txt**
- Already had correct `build_lib()` structure
- No manual `add_subdirectory(examples)` needed

## Next Session Notes

If continuing work:

1. **Batch Experiments:** To run multiple seeds/configs:
   ```bash
   for seed in {1..10}; do
     ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=$seed --runId=$seed"
   done
   ```

2. **Faster Configuration:** Only enable wsn-uav module to avoid building other modules
   ```bash
   ./ns3 configure --enable-examples --enable-modules=wsn-uav
   ```

3. **Analysis:** Results can be post-processed from CSV files or parsed from HTML visualization data

4. **Parameter Tuning:** Current key parameters to adjust:
   - `--gridSize` - affects total nodes and coverage area
   - `--numFragments` - more fragments = longer detection time
   - `--alertThreshold` - default 0.75 (requires 75%+ fragments)
   - `--simTime` - detection timeout

## Status Summary

✅ Build system fully functional  
✅ NS-3 run command integration working  
✅ Parameter passing working correctly  
✅ Output generation working  
✅ Detection logic working  
✅ Visualization generation working  

Ready for batch experiments and parameter studies.
