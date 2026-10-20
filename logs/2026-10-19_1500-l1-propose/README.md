# 2026-10-19 · Layer-1 model in the proposed mission (CLAUDE.md §8 items 92–94)

**Purpose:** rerun the proposed mission P with the layer-1 parameters M (crops per camera), L (signature images), F (file size, kB), f (per-crop false-YES rate), k (target crops at the true camera).

**Commands**
1. `regeom-k4.md`, `regeom-all.md`: `uav-l2/tools/regeom.py` rebuilt the geometry of the 40 saved maps. It ran stage 1 of mission.py plus uav-coop-deploy with the saved bearings into the scratchpad `W/`, which is not committed.
   - The rebuild took about 2 min.
   - Map, clusters, flight segments and critical cells were all checked against the saved data: 40/40 match.
   - No ns-3 traffic run.
2. `l1m.md`: `uav-l2/tools/l1_mission.py`.
   - 240 configurations × 1 200 missions.
   - Took about 10 min.

**Inputs:** `uav-l2/docs/data/mission/{k2,k4,k6,k8,camp/*}`, which hold the saved River results.

**Outputs:**
- `uav-l2/docs/data/mission/l1m-summary.csv`
- `uav-l2/docs/data/mission/l1m-draws.csv.gz`
- report: `uav-l2/docs/L1-MISSION-vi.md`

**Main result:** f = 0.1 % (TTR 82 %) works when k ≥ 3; large M does not reduce misses but dilutes the ranking; L helps up to 3 views; F (15 vs 50 kB) has no effect while River delivers all of D.

**Open:** the L/F effect on layer-3 timing needs the pass bitmaps, i.e. an ns-3 pass rerun. Awaiting approval.
