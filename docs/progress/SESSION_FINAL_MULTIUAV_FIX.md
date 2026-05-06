# Session: Final Multi-UAV Crash Fix

**Date:** 2026-05-04 (continued)  
**Focus:** Fix null pointer dereference in multi-UAV scenarios  
**Status:** ✅ **COMPLETELY FIXED** - All scenarios working

---

## Root Cause Found & Fixed

### The Bug
Multi-UAV scenarios (Scenario 2 and 3) crashed at +502.31s with null pointer dereference because:

1. **UAVs were receiving MAC layer callbacks**
   - During `InstallUavApplications()`, MAC callbacks were set on UAV devices
   - When UAVs received any packet, `OnPacketReceived()` was called
   
2. **UAVs accumulated fragments**
   - Ground nodes → broadcast to all
   - UAVs received these broadcasts and processed them
   - UAVs' confidence models accumulated to trigger detection threshold

3. **UAVs triggered false detection**
   - Detection callback fired when confidence > threshold
   - UAVs called `ScheduleCooperation()` (which should only be for ground nodes)
   - UAVs tried to send manifests and cooperate

4. **Memory/pointer corruption**
   - Cooperation scheduling + manifest sending in UAV apps corrupted state
   - Eventually leads to null pointer dereference in cooperation logic

### The Fix
**Remove MAC callbacks from UAVs** - UAVs should ONLY broadcast, never receive:

```cpp
// BEFORE (lines 374-379 in wsn-network-helper.cc)
uavMac->SetMcpsDataIndicationCallback(
    [uavApp](Ptr<Packet> pkt, Mac16Address src, double rssi) {
        if (uavApp) {
            uavApp->OnPacketReceived(pkt, rssi);  // ❌ WRONG - UAVs shouldn't receive
        }
    });

// AFTER
// INTENTIONALLY NOT SETTING CALLBACK FOR UAVs
// UAVs are broadcasters only - they do not receive
```

---

## Verification

All scenarios now pass with full 500-second simulations:

### Scenario 1 (Single-UAV) ✅
```bash
$ python3.10 ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
Output: Detection=YES, Tdetect=14.4s
Status: WORKS ✓
```

### Scenario 2 (3-UAV) ✅
```bash
$ python3.10 ./ns3 run "scenario-2-multi-uav-2 --gridSize=10 --seed=1 --runId=1"
Output: Detection=YES, Tdetect=14.2s  
Status: WORKS ✓ (Previously crashed at +502.31s)
```

### Scenario 3 (Load-Balanced) ✅
```bash
$ python3.10 ./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --seed=1 --runId=1"
Output: Detection=YES, Tdetect=14.2s
Status: WORKS ✓ (Previously crashed at +502.31s)
```

---

## Files Modified

### wsn-network-helper.cc (lines 369-379)
- **Removed** MAC callback setup for UAVs
- **Added** comment explaining UAVs are broadcasters only
- This prevents UAVs from receiving and processing packets

### fragment-dissemination-app.cc
- **Cleaned up** temporary debug logging added during troubleshooting
- Removed checks for simulation time > 500s
- Removed RNG null checks (no longer needed)

### scenario-2-multi-uav-2.cc
- **Added** `Simulator::Destroy()` call after results collection for proper cleanup
- Reset simTime back to 500.0 (was temporarily set to 10.0 for debugging)

---

## Architecture Insight

**Key Design Principle:**
- Ground nodes: Receive broadcasts from UAVs, trigger detection, initiate cooperation
- UAVs: ONLY broadcast fragments, no reception/detection/cooperation logic

The bug occurred because UAVs were inadvertently processing received packets, acting like ground nodes. This violated the intended broadcast-only architecture.

---

## Summary of All Fixes in This Session

1. ✅ **OnDetection callback** - Made static to eliminate dangling `this` pointer
2. ✅ **Ground node MAC callback** - Captures app directly instead of `this`
3. ✅ **UAV node MAC callback** - Captures app directly instead of `this`
4. ✅ **Periodic recording lambda** - Captures containers directly instead of `this`
5. ✅ **Debug trace callback** - Captures stats directly instead of `this`
6. ✅ **UAV MAC callbacks** - REMOVED to prevent false reception/detection

---

## Lessons Learned

1. **Architecture enforcement matters** - UAVs and ground nodes have different roles; the code should strictly enforce this
2. **Broadcast-only vs receive-enabled** - When a device should only transmit, don't set reception callbacks
3. **Multi-node scenarios expose hidden issues** - Single-UAV Scenario 1 worked because UAV never received packets
4. **Systematic debugging** - Reducing simulation time to 10s helped isolate the problem to early detection phase

---

## Build & Test

```bash
# Rebuild
python3.10 ./ns3 configure --enable-examples --enable-modules=wsn-uav
python3.10 ./ns3 build

# Test all scenarios
python3.10 ./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"   # ✓
python3.10 ./ns3 run "scenario-2-multi-uav-2 --gridSize=10 --seed=1 --runId=1"  # ✓
python3.10 ./ns3 run "scenario-3-load-balanced-fragments --gridSize=10 --seed=1 --runId=1"  # ✓

# Check outputs
ls src/wsn-uav/results/scenario-*/run-001/metrics.csv
```

---

## Final Status

| Feature | Status |
|---------|--------|
| Single-UAV scenario | ✅ WORKING |
| Multi-UAV scenario (2) | ✅ WORKING |
| Multi-UAV scenario (3) | ✅ WORKING |
| Fragment size generation | ✅ WORKING |
| Fragment CSV output | ✅ WORKING |
| Detection/cooperation | ✅ WORKING |
| Full 500s simulation | ✅ WORKING |

**All scenarios complete successfully with no crashes or errors.**

---

**Created:** 2026-05-04  
**Status:** ✅ Complete - All scenarios passing
