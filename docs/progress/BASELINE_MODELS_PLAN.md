# Baseline Models Plan

This note records comparison baselines to add after the current cooperation
model stabilizes. These are design targets only; they are not implemented yet.

## Flight-Path Baselines

1. **NN Path**
   - Start at UAV initial position.
   - Repeatedly visit the nearest unvisited candidate node/cell centroid.
   - No cell coverage threshold.
   - Purpose: reproduce the nearest-neighbor baseline from the v1 paper.

2. **Per-Node GMC**
   - Current greedy maximum coverage without cell-aware claiming.
   - A node is covered only when it is directly within UAV broadcast radius.
   - Purpose: isolate the benefit of the 30% cell-coverage rule.

3. **Cell-Aware GMC**
   - Current primary model.
   - Candidate waypoints are node positions; if a waypoint covers at least
     `beta=0.30` of a cell, the whole cell is marked covered.
   - Purpose: proposed method.

4. **Centroid Sweep**
   - Visit cell centroids in a greedy TSP-like order.
   - Purpose: simple cell-planning baseline independent of node density.
   - Current implementation: `--flightPathModel=cell-centroid-sweep`.
   - Note: use this instead of `nearest-neighbor` for routine comparisons;
     NN is retained for reference but is too slow for the main batch.

5. **Random Waypoint**
   - Draw a fixed-seed random sequence of waypoints inside the sensor bounding
     box.
   - Waypoint budget is capped by `--randomWaypointBudget` (default `64`).
     Use `0` to revert to one waypoint per non-empty cell; that setting is
     too slow for 30x30+ networks and mostly measures excessive flight time.
   - Current implementation: `--flightPathModel=random-waypoint`.

## Broadcast Baselines

1. **Cyclic L0 Broadcast**
   - Current primary model: UAV cycles through L0 fragments continuously.

2. **Random L0 Broadcast**
   - Each packet picks a random L0 fragment.
   - Purpose: compare systematic cycling against fountain-like random spread.

3. **Utility-Weighted Broadcast**
   - Fragments sampled by semantic utility/type priority.
   - Purpose: measure early coarse-clue dissemination benefit.
   - Current implementation: `--broadcastModel=utility-weighted`; full
     fragment groups are sampled by fragment utility and L0 semantic type
     priority (COLOR/SILHOUETTE/BODY_RATIO weighted higher).

4. **Whole-Payload Flood**
   - UAV attempts to send the full reference payload sequentially.
   - Purpose: conventional large-file baseline.
   - Current implementation: `--broadcastModel=unicast-full`; UAV sends the
     whole L0 clip to one nearby ground node at a time using unicast LR-WPAN
     frames. A node counts a fragment only after every sub-packet for that
     fragment arrives. This is intentionally slower than cyclic/random
     broadcast and represents conventional per-node large-file delivery.

## Detection Baselines

1. **Fragment-Ratio Detection**
   - Detection when `|F_n| / K >= tau_alert`.
   - Purpose: simplest data-availability baseline.

2. **Local-Clue Weighted Detection**
   - Current proxy: `clueQuality * semanticOverlap * evidenceGate`.
   - Purpose: keeps the target-search story active.

3. **Noisy-OR Fragment Utility**
   - Paper-aligned confidence: `C_n = 1 - product(1 - p_i)` for received
     fragments.
   - Purpose: proposed detection model after fragment utility is finalized.

4. **No-Cooperation Detection**
   - Same detector, but only direct UAV fragments count.
   - Purpose: quantify cooperation gain.

## Minimum Metrics For Every Baseline

- Flight distance and mission completion time.
- Direct-UAV fragment distribution.
- Post-cooperation fragment distribution.
- Detection time `T_detect`.
- Target node rank and target cell rank.
- False-alarm count above threshold.
- Cooperation packet attempts, delivered packets, and drops.
