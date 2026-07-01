# UAV Mission — Phase 1 Progress

**Status:** working, verified across grids 5×5 / 10×10 / 20×20 / 30×30
**Last updated:** 2026-05-18
**Scope:** Scenario 1 — BS hands the UAV everything, UAV plans + flies the first
mission and broadcasts layer-0 cues. Later phases (L1–L3 dissemination, ground
cooperation) are not implemented yet — see `SEMANTIC_FRAGMENTATION_STORY.md`.

---

## Overview

Phase 1 pipeline, in order:

1. **BS → UAV transfer.** BS sends the network topology, then the 28-fragment
   semantic profile (metadata + data volume), over LR-WPAN. Every packet is
   ACKed by the UAV.
2. **UAV gate.** UAV reassembles both streams; takes off only once topology
   AND fragment data are complete (+2 s prep delay).
3. **Mission planning.** UAV computes its broadcast radius, its flight speed,
   and a two-range GMC waypoint path.
4. **Flight + L0 broadcast.** UAV flies the path (climb → cruise → land) and
   continuously broadcasts layer-0 fragments.
5. **Measurement.** Scenario aggregates real L0 coverage vs the UAV's
   GMC-assumed coverage.

---

## Components (files)

| File | Role |
|---|---|
| `models/common/semantic-fragment.{h,cc}` | `Fragment`, `SemanticLayer`, `TargetProfile` (Generate, noisy-OR confidence) |
| `models/application/uav-flight-controller.{h,cc}` | Level-2 autopilot: `Forward/Turn/Hover/SetClimb` over `ConstantVelocityMobilityModel` |
| `models/application/uav-app.{h,cc}` | Flight state machine, topology+data reassembly, 2-range GMC, speed calc, L0 broadcast |
| `models/application/basestation-app.{h,cc}` | Topology + fragment-data dispatch, ACK handling, `TargetProfile` generation |
| `models/application/ground-node-app.{h,cc}` | L0 RX tracking (beacon TX disabled) |
| `models/network/scenario1-network.{h,cc}` | Radio: LogDistance n=3.0, RX sens −95 dBm; UAV uses `ConstantVelocityMobilityModel` |
| `helper/scenario1/scenario1-config.{h,cc}` | Orchestration + L0 coverage aggregation in `Run()` |

---

## Wire protocol

First payload byte is `msgType`. App payload capped at 100 B (LR-WPAN MTU is
127 B PSDU incl. MAC+FCS). Multi-packet streams are staggered 200 ms apart to
avoid MAC queue overflow.

| msgType | Name | Header | Notes |
|---|---|---|---|
| 1 | TOPO_FRAGMENT | 7 B `[type][destId][totalCount:u16][thisCount][startIdx:u16]` | + 7 B entries `[id][x,y,z:i16 dm]`, ≤13/pkt |
| 2 | TOPO_ACK | 7 B `[type][destId][recv:u16][total:u16][complete]` | UAV → BS |
| 3 | DATA_FRAGMENT | 16 B `[type][destId][numFrags][fragId][layer][util:u16][totalBytes:u32][offset:u32][chunkLen]` | + ≤84 B filler |
| 4 | DATA_ACK | 7 B `[type][destId][fragsDone:u16][fragsTotal:u16][complete]` | UAV → BS |
| 5 | L0_BCAST | 5 B `[type][fragId][layer][utilMilli:u16]` | + filler; broadcast `ff:ff` |

---

## Key algorithms

### Two-range GMC mission planner (`UavApp::BuildMission`)
- `r_main` = computed broadcast radius (~35.85 m); `r_sec` = 1.35 × r_main.
- **Pass 1:** greedy max-coverage with `r_sec` until all nodes covered (sparse
  coarse sweep).
- **Strip:** nodes covered only by the secondary ring `[r_main, r_sec]` are
  un-covered.
- **Pass 2:** greedy continues with `r_main` to re-cover the stripped nodes →
  new waypoints land near the old path → UAV revisits for report collection.

### Flight speed (`UavApp::ComputeFlightSpeed`)
- Dynamic, derived from `r_main` — not a config parameter.
- `v = 2·r_main / Δ`, `Δ = max(L0_airtime, L0_BROADCAST_PERIOD_S=1.0 s)`.
- Contact window for an on-path node = `2·r_main/v`; setting it equal to one
  broadcast period gives the fastest "guaranteeing" speed → ~71.7 m/s.
- Raw L0 airtime (~0.7 ms) is far too small to bind speed; the 1.0 s period
  floor is the real binding factor. **If L0 delivery is poor, raise the
  period floor (lowers speed).**

### Broadcast radius (`UavApp::ComputeBroadcastRadius`)
- Solves LogDistance for RX power = sensitivity, then projects slant range to
  horizontal at cruise altitude.

### Arrival detection
- `ControlTick` CRUISING uses an overshoot test (target behind heading vector)
  in addition to the arrival radius — required at 72 m/s where one 0.1 s tick
  steps 7.2 m.

---

## Tunable constants

| Constant | Value | Location |
|---|---|---|
| pathLossExponent / refLoss / refDist | 3.0 / 46.6 dB / 1.0 m | `NetworkConfig` + UAV pre-flight calibration |
| txPower / rxSensitivity | 0 dBm / −95 dBm | same |
| SECONDARY_RANGE_FACTOR | 1.35 | `uav-app.cc` |
| GMC_ALPHA | 1.0 | `uav-app.cc` |
| L0_BROADCAST_PERIOD_S | 1.0 s | `uav-app.cc` |
| DATA_RATE_BPS | 250000 | `uav-app.cc` |
| CLIMB_RATE_MPS / CONTROL_TICK_S | 5.0 / 0.1 s | `uav-app.cc` |
| Default profile | 28 frags: L0 4×16B, L1 8×48B, L2 12×128B, L3 4×2048B (10176 B) | `TargetProfile::Generate` |
| Per-layer utility | 0.30 / 0.12 / 0.05 / 0.40 | `semantic-fragment.cc` |
| Packet stagger / max payload | 200 ms / 100 B | BS app |

---

## Test results (2026-05-18, multi-subagent)

| Grid | N | v (m/s) | L0 broadcasts | L0 pkts RX | real coverage | deviation |
|---|---|---|---|---|---|---|
| 5×5 | 25 | 71.7 | 14 | 111 | 23/25 (92.0%) | 2 |
| 10×10 | 100 | 71.7 | 37 | 432 | 100/100 (100%) | 0 |
| 20×20 | 400 | 71.7 | 132 | 1767 | 397/400 (99.2%) | 3 |
| 30×30 | 900 | 71.7 | 263 | 3651 | 891/900 (99.0%) | 9 |

- UAV's GMC assumes 100% coverage; real L0 coverage is 92–100%.
- Smallest grid is worst: short path → few broadcasts → sparse coverage
  corridor → edge nodes missed.
- Phase-1 transfer takes ~14 s (grid 10) to ~41 s (grid 30) of sim time.

---

## Known limitations / open items

- `GroundNodeApp::StopApplication` per-node L0 log does not fire — ns-3 skips
  `StopApplication` when app stop-time equals `Simulator::Stop` time. The
  aggregate block in `Scenario1Config::Run()` is unaffected (reads counters
  directly).
- Flight speed's `Δ` floor (1.0 s) is a modeling constant, not derived from
  physics — the literal airtime is degenerate.
- Ground-ground beacons are disabled (`SendBeacon()` call commented in
  `GroundNodeApp::StartApplication`).
- BS→UAV transfer is reliability-by-ACK only; no retransmission of lost
  fragments (channel is reliable in tests, 0 FAIL observed).

## Next steps

Per `SEMANTIC_FRAGMENTATION_STORY.md`: L1–L3 dissemination phases, ground-node
cooperation (fragment + evidence exchange), region-aware re-planning, and
final full-payload delivery.
