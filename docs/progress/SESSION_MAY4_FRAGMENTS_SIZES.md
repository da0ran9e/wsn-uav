# Session May 4: Load-Balanced Fragments Implementation

**Date:** 2026-05-04  
**Focus:** Implement fragments with random sizes and load-balanced distribution  
**Outcome:** ✅ Partial success - single-UAV works, multi-UAV needs debugging

---

## What Was Implemented

### 1. Fragment Size Generation ✅

**Files Modified:** `fragment-model.h/.cc`

- Added `sizeBytes` field to `Fragment` struct
- Implemented `FragmentCollection::GenerateWithSizes()` method:
  - Generates K fragments with random sizes in `[minSizeBytes, maxSizeBytes]`
  - Sorts fragments by size descending (largest first)
  - Re-assigns IDs: ID 0 = largest, ID K-1 = smallest
  - Uses `std::mt19937` with configurable seed for reproducibility

**Example Output:**
```
Fragment 0: 18289 bytes (largest)
Fragment 1: 17332 bytes
...
Fragment 9: 1144 bytes (smallest)
```

### 2. Configuration Fields ✅

**Files Modified:** `wsn-network-helper.h`

Added to `SimulationConfig`:
```cpp
uint32_t fragmentMinSizeBytes = 1000;   // 1 KB
uint32_t fragmentMaxSizeBytes = 20000;  // 20 KB
```

Added to `SimulationResults`:
```cpp
std::map<uint32_t, std::vector<uint32_t>> uavFragmentIds;
std::map<uint32_t, uint32_t> fragmentSizesBytes;
```

### 3. CSV Output ✅

**Files Modified:** `result-writer.cc`

Metrics CSV now includes:
```
uav_0_fragment_count,10
uav_0_fragment_ids,0,1,2,3,4,5,6,7,8,9
fragment_0_size_bytes,18289
fragment_1_size_bytes,17332
...
fragment_9_size_bytes,1144
```

### 4. Scenario 3 Creation ✅

**New File:** `examples/scenario-3-load-balanced-fragments.cc`

- 3 UAVs with size-dependent fragment distribution
- CLI args for fragment size range
- Detailed logging of UAV→fragment assignments
- Registered in CMakeLists.txt

---

## Test Results

### ✅ Scenario 1 (Single UAV) - WORKING

```bash
python3.10 ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
```

**Output:**
- Detection time: 14.6 seconds
- Fragment sizes correctly generated and output to CSV
- All 10 fragments present (0-9)
- Sizes sorted: 18289 → 17332 → ... → 1144 bytes

**Metrics CSV:**
```
fragment_0_size_bytes,18289
fragment_1_size_bytes,17332
...
uav_0_fragment_ids,0,1,2,3,4,5,6,7,8,9
```

### ⚠️ Scenario 2 (3 UAVs) - CRASHES

```bash
python3.10 ./ns3 run "scenario-2-multi-uav-2 --gridSize=10 --seed=1 --runId=1"
```

**Status:** Runs ~500s into simulation, then crashes with:
```
NS_ASSERT failed, cond="m_ptr", msg="Attempted to dereference zero pointer"
```

**Root Cause:** Unknown - needs debugging. Likely issue in:
- Multi-UAV callbacks (OnDetection)
- Statistics collector with 3 UAVs
- Fragment distribution in multi-UAV scenario
- Pointer dereference in ptr.h line 712

### ⚠️ Scenario 3 (Load-Balanced) - CRASHES

Same crash as Scenario 2 (both multi-UAV scenarios affected).

---

## Code Changes Summary

| File | Changes | Status |
|------|---------|--------|
| `fragment-model.h` | Added `sizeBytes` field, `GenerateWithSizes()` method | ✅ |
| `fragment-model.cc` | Implemented `GenerateWithSizes()` with sorting & seeding | ✅ |
| `wsn-network-helper.h` | Added config/result fields, `DistributeFragmentsToUavs()` method | ✅ |
| `wsn-network-helper.cc` | Call new fragment generation, distribute fragments | ✅ |
| `fragment-dissemination-app.cc` | Simplified DoBroadcast (uses fixed interval for now) | ✅ |
| `result-writer.cc` | Output fragment sizes to CSV | ✅ |
| `scenario-3-load-balanced-fragments.cc` | New scenario file | ✅ |
| `examples/CMakeLists.txt` | Registered Scenario 3 | ✅ |

---

## What Works

1. **Fragment Size Generation:**
   - Random sizes generated correctly
   - Sorted by size descending
   - Reproducible with seed parameter

2. **Single-UAV Scenarios:**
   - Scenario 1 runs to completion
   - Fragment sizes output to CSV
   - No crashes or errors

3. **CSV Output:**
   - New fields written correctly
   - Backward compatible format
   - Fragment assignments tracked

---

## Known Issues

### Issue #1: Multi-UAV Crash

**Symptom:** Scenario 2 and 3 crash after ~500 seconds with null pointer dereference

**Affected Code Paths:**
- All multi-UAV scenarios (numUavs > 1)
- Crash occurs during or after detection phase

**Investigation Needed:**
- Check OnDetection callback for multi-UAV scenarios
- Verify StatisticsCollector handles 3 UAVs correctly
- Check if issue existed before our changes

### Issue #2: Transmission Time Model

**Current Status:** Deferred - uses fixed `FRAGMENT_BROADCAST_INTERVAL`

**To Implement Later:**
- Compute TX time as `(sizeBytes * 8) / DATA_RATE_BPS`
- Propagate sizeBytes through packet headers
- Handle ground node reception of size-aware packets

---

## Feature Completeness

### Implemented ✅
- [x] Random fragment size generation
- [x] Size-based sorting (large → small)
- [x] CSV output of fragment sizes
- [x] Config fields for size range
- [x] Single-UAV scenarios working
- [x] Scenario 3 framework created

### Deferred ⏳
- [ ] Multi-UAV fragment distribution (causes crash)
- [ ] Dynamic TX time based on fragment size
- [ ] Per-UAV transmission timing
- [ ] Debug multi-UAV crash

---

## Recommendations

### Immediate
1. Debug the multi-UAV crash (likely in statistics collection or detection callbacks)
2. Verify original Scenario 2 works without our changes
3. Isolate whether crash is new or pre-existing

### Short-term
1. Implement proper per-UAV fragment distribution once multi-UAV works
2. Add transmission time model when per-fragment sizes are in headers
3. Test Scenario 3 with size-dependent broadcasting

### Long-term
1. Benchmark detection time improvement with distributed fragments
2. Compare UAV broadcast rates: large vs small fragments
3. Optimize fragment assignment algorithm

---

## Build & Test Commands

```bash
# Build with new code
python3.10 ./ns3 clean
python3.10 ./ns3 configure --enable-examples --enable-modules=wsn-uav
python3.10 ./ns3 build

# Test Scenario 1 (works)
python3.10 ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"

# Test Scenario 2 (crashes)
python3.10 ./ns3 run "scenario-2-multi-uav-2 --gridSize=10 --seed=1 --runId=1"

# Test Scenario 3 (crashes)
python3.10 ./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --seed=1 --runId=1"

# Check output
cat src/wsn-uav/results/scenario-1/run-001/metrics.csv | grep -E "fragment|uav_.*count"
```

---

## Files Created/Modified

**New Files:**
- `examples/scenario-3-load-balanced-fragments.cc` (271 lines)

**Modified Files:**
- `models/application/fragment-model.h` (5 lines added)
- `models/application/fragment-model.cc` (70 lines added)
- `helper/wsn-network-helper.h` (6 lines added)
- `helper/wsn-network-helper.cc` (30+ lines added/modified)
- `models/application/fragment-dissemination-app.cc` (10 lines modified)
- `helper/result-writer.cc` (20 lines added)
- `examples/CMakeLists.txt` (12 lines added)

**Total:** 1 new file, 7 modified files

---

**Session Status:** ✅ Core feature working, debugging needed for multi-UAV  
**Recommended Next Step:** Debug multi-UAV crash before proceeding with full feature

---

**Created:** 2026-05-04  
**Last Updated:** 2026-05-04

