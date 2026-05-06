# WSN-UAV Project Handoff

**Last Updated:** 2026-05-05
**Status:** Phase 0 + Phase 1 + Advanced Features complete. Ready for Scenario-1 model improvements.
**Single source of truth.** Older docs are referenced here for deeper context but are not required reading.

---

## 1. Project at a Glance

NS-3 simulator for UAV-assisted target detection in a grid WSN. UAVs broadcast image-fragment evidence to ground nodes; nodes accumulate confidence (`C = 1 - ∏(1 - p_i)`) and trigger an alert when `C ≥ τ_alert`. Optional ground-to-ground cooperation fills gaps via manifest exchange.

**Working scenarios:**
| Scenario | Entry point | Detection time (10×10) | Status |
|---|---|---|---|
| 1 — Single UAV (paper baseline) | [scenario-1-single-uav.cc](../../examples/scenario-1-single-uav.cc) | 14.69 s | ✅ stable, backward-compat reference |
| 3 — 3-UAV cooperative, load-balanced | [scenario-3-load-balanced-fragments.cc](../../examples/scenario-3-load-balanced-fragments.cc) | 10–11 s | ✅ 3.5× faster than S1 |

Scenario 2 (spatial filtering) was tried and **abandoned** — see [SCENARIO_COMPARISON.md](SCENARIO_COMPARISON.md). Spatial fragment partitioning is fundamentally incompatible with confidence-threshold detection (max ~60% confidence per region < 75% threshold).

---

## 2. Code Map (where things live)

All work happens inside [src/wsn-uav/](../../). Never modify files outside this directory.

```
src/wsn-uav/
├── examples/
│   ├── scenario-1-single-uav.cc            ← paper baseline, 1 UAV, all fragments
│   └── scenario-3-load-balanced-fragments.cc ← 3 UAVs, size-based load balance
├── helper/
│   ├── wsn-network-helper.{h,cc}           ← orchestrator (Build/Schedule/Run)
│   ├── topology-helper.{h,cc}              ← grid + hex cells + candidate selection
│   ├── trajectory-helper.{h,cc}            ← GMC + nearest-neighbor planners
│   └── result-writer.{h,cc}                ← CSV + interactive HTML export
├── models/
│   ├── application/
│   │   ├── fragment-model.{h,cc}           ← Fragment, FragmentCollection, Generate*
│   │   ├── confidence-model.{h,cc}         ← per-node union-probability tracker
│   │   └── fragment-dissemination-app.{h,cc} ← UAV broadcast + ground cooperation
│   ├── common/
│   │   ├── parameters.h                    ← all paper-spec constants
│   │   ├── types.h                         ← Waypoint, CoopTrigger, NodeCell
│   │   ├── packet-header.{h,cc}            ← FragmentPacket, CooperationPacket
│   │   └── statistics-collector.{h,cc}     ← packet/UAV-position event log
│   └── mac/wsn-uav-mac.{h,cc}              ← thin MAC wrapper around CC2420
└── docs/progress/                          ← this directory (37 files)
```

---

## 3. Model Inventory — What Each Model Does and Its Limits

### 3.1 Fragment Model — [models/application/fragment-model.h](../../models/application/fragment-model.h)
- **What:** Splits a 416×416×3 image evenly across K fragments. Per-fragment evidence: `p_i = 1 − (1 − C_master)^(pixels_i / total_pixels)` so `C(all K) = C_master = 0.90`.
- **APIs:** `Generate(count)` (uniform pixels, sizeBytes=0), `GenerateWithSizes(count, min, max, seed)` (random sizes 1–20 KB, sorted descending — used by Scenario 3).
- **Limits / improvement targets for S1:**
  - Pixels divided uniformly; no awareness of where the object lives in the image (real YOLO tiles have very uneven information density).
  - `evidence` is monotonic in pixel count only — no semantic salience, no class probability.
  - `data` payload is filler bytes (`i % 256`), so size doesn't drive realistic TX time in S1.

### 3.2 Confidence Model — [models/application/confidence-model.h](../../models/application/confidence-model.h)
- **What:** Per-node `FragmentCollection` plus union probability `C = 1 − ∏(1 − p_i)`. Counts UAV vs cooperation deliveries. Exposes `GetMissingIds()` for manifest replies.
- **Limits / improvement targets for S1:**
  - Independence assumption: union formula assumes fragments are independent evidence (fine for paper, but real classifier outputs are correlated).
  - No temporal decay — once received, fragments stay forever; doesn't model staleness or attacker mobility.
  - No Bayesian prior: a node "starts" at `C = 0` instead of an empirical class prior.
  - Threshold is binary; no soft-decision or hysteresis to combat threshold flapping.

### 3.3 Fragment Dissemination App — [models/application/fragment-dissemination-app.h](../../models/application/fragment-dissemination-app.h)
- **What:** Single class with two roles via `Role::{UAV_BROADCASTER, GROUND_NODE}`.
  - UAV: cyclic round-robin broadcast every `broadcastInterval=0.2s`.
  - Ground: receive → update confidence → schedule cooperation → manifest exchange → send missing fragments to neighbors.
- **Cooperation timing:** `delay = K · broadcastInterval + 0.5 s + bfsLevel · 0.02 + Uniform(0, 0.015)`.
- **Limits / improvement targets for S1:**
  - UAV broadcast cadence is fixed; no MAC-aware backoff or adaptive rate.
  - Cooperation manifest is broadcast (any neighbor replies) — duplicate replies and wasted airtime; no leader/aggregation.
  - No retransmission on packet drop (the channel quietly loses ~35% with realistic CC2420).
  - Detection trigger only fires at the pre-selected `detectionNode`, not at any node crossing `τ_alert` — this hides distributed-detection behavior.

### 3.4 Topology Helper — [helper/topology-helper.h](../../helper/topology-helper.h)
- **What:** Builds N×N grid (spacing 20 m), partitions into hex cells (radius 80 m), picks cell leaders, computes BFS levels and neighbor sets, randomly selects `suspiciousPercent` (30%) candidate nodes and one `detectionNode`.
- **Limits / improvement targets for S1:**
  - Candidate selection is uniform random — doesn't model traffic hotspots, road grids, or attacker concentration.
  - Cell structure is geometric only; no actual radio-connectivity check.
  - Hard-coded square grid; no support for irregular/clustered topologies.

### 3.5 Trajectory Helper — [helper/trajectory-helper.h](../../helper/trajectory-helper.h)
- **What:** Two planners.
  - `PlanGmc()`: greedy set-cover scoring `gain / (1 + α · cost/speed)`. Candidates = suspicious nodes + k-means centroids (k dynamic, capped at `MAX_KMEANS_CENTROIDS=128`). Cell-aware expansion if waypoint covers >β of a cell.
  - `PlanNearestNeighbor()`: visits every candidate in greedy nearest order (used as baseline; reliable but path-suboptimal).
- **Limits / improvement targets for S1:**
  - GMC uses static `α=0.2`; not tuned per grid size or fragment count.
  - K-means uses 10 fixed iterations and Lloyd's algorithm only — no convergence check, no k++ init in the non-random path.
  - No re-planning during flight (no adaptive coverage feedback).
  - Return-to-start is post-hoc; not part of the optimization objective.

### 3.6 Statistics Collector & Result Writer
- **Statistics:** `RecordPacketSent/Received/Detection`, UAV position trace, per-node received fragments. Sent records use broadcast marker `0xFFFFFFFF` and 1.0 s matching window.
- **Outputs:** `metrics.csv`, `packets.csv`, `trajectories.csv`, `config.txt`, `wsn-uav-result.html` (interactive Canvas viz with time scrubbing and fragment-count node coloring).

### 3.7 Channel / PHY (CC2420 from `src/wsn`)
- Wired in [wsn-network-helper.cc:140-160](../../helper/wsn-network-helper.cc). Set: `TxPower=-10 dBm`, `RxSensitivity=-95 dBm`, `EnableShadowing=!usePerfectChannel`, `PerfectChannel=usePerfectChannel`.
- Default (realistic) channel produces ~35% PER, matching paper Section V.C.
- **Limits:** no Doppler/multipath model; shadowing is the only stochastic component; no MAC contention modeling beyond CC2420's own CSMA-CA.

---

## 4. Validated Parameters and Results

### 4.1 Paper-spec constants (in [parameters.h](../../models/common/parameters.h))
```
GRID_SPACING=20 m, UAV_ALTITUDE=20 m, UAV_SPEED=20 m/s
HEX_CELL_RADIUS=80 m, UAV_BROADCAST_RADIUS=50 m
DEFAULT_NUM_FRAGMENTS=10, MASTER_FILE_CONFIDENCE=0.90
COOPERATION_THRESHOLD=0.30, ALERT_THRESHOLD=0.75, SUSPICIOUS_COVERAGE_PERCENT=0.30
STARTUP_DURATION=5 s, FRAGMENT_BROADCAST_INTERVAL=0.2 s
TX_POWER_DBM=-10, RX_SENSITIVITY_DBM=-95, DATA_RATE_BPS=250000
GMC_ALPHA=0.2, MAX_KMEANS_CENTROIDS=128
```

### 4.2 Known-good results (seed=1)
| Scenario | Grid | T_detect | UAV path | Notes |
|---|---|---|---|---|
| S1 | 10×10 | 14.69 s | 662.9 m | reference baseline; reproducible |
| S1 | 30×30 | ~14.7 s | 1305.8 m | detection time invariant in N |
| S3 (3 UAV) | 10×10 | 10.31 s | 1988.8 m total | speed ratio 1.84×, 100% coverage |
| S3 | 30–70 grids | 10.0–10.9 s | linear scaling | dynamic-k GMC keeps coverage |

### 4.3 Build & Run
```bash
# Python 3.10 or 3.13 (NOT 3.14 — NS-3 wrapper bug at line 129)
cd /Users/mophan/Github/ns-3-dev-git-ns-3.46
./ns3 configure --enable-examples --enable-modules=wsn-uav
./ns3 build

# Scenario 1 (paper baseline)
./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1 --runId=1"
open src/wsn-uav/results/scenario-1/run-001/wsn-uav-result.html

# Batch over seeds for paper Fig.3 reproduction
for seed in $(seq 1 100); do
  for g in 10 20 30 35; do
    ./ns3 run "scenario-1-single-uav --gridSize=$g --seed=$seed --runId=$seed"
  done
done
```

Full CLI matrix in [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md).

---

## 5. Next Phase: Improving the Scenario-1 Models

The user has chosen **Scenario 1 model improvements** as the next focus. The candidates below are ordered by expected impact-vs-effort. Each lists the model touched, why it matters for paper reproduction, and a suggested entry point.

### 5.1 Tier 1 — High impact, contained scope

**A. Realistic fragment evidence model**
- *Why:* current `evidence ∝ pixelCount` ignores object salience. Paper Fig.3 detection times depend on which fragments are most informative. A non-uniform evidence distribution would produce more realistic `T_detect` curves and make `τ_alert` tuning meaningful.
- *Files:* [fragment-model.cc:67-83](../../models/application/fragment-model.cc) (`EvidenceFromPixelCount`), and a new generator variant.
- *Suggested API:* `Generate(count, masterConf, EvidenceProfile profile)` where `profile ∈ {Uniform, ZipfHotspot, Gaussian2D, External(csv)}`.
- *Validation:* compare `T_detect` distribution at N=100 vs paper Fig.3.

**B. Channel-aware retransmissions in dissemination app**
- *Why:* with realistic channel ~35% PER, fragments are silently dropped — current S1 detection time is artificially low because we don't model the loss-driven retry cost.
- *Files:* [fragment-dissemination-app.cc](../../models/application/fragment-dissemination-app.cc) (`SendFragment`, `OnPacketReceived`).
- *Approach:* lightweight ARQ — UAV maintains a per-fragment broadcast counter; ground nodes ACK via piggyback in next manifest. Bound retries to avoid runaway airtime.
- *Validation:* PER vs `T_detect` curve, with/without retry; toggle via new `SimulationConfig.useArq`.

**C. Distributed detection trigger**
- *Why:* currently only `m_detectionNodeId` can fire detection. Real systems trigger on *any* node crossing `τ_alert`; this also lets us measure spatial detection latency.
- *Files:* [fragment-dissemination-app.cc](../../models/application/fragment-dissemination-app.cc) (`ProcessFragment`).
- *Change:* drop the `nodeId == detectionNode` gate; record first-trigger node id and time. Keep `detectionNodeId` as a *seed* for candidate selection only.
- *Validation:* check that S1 `T_detect` is unchanged when seed places candidate near UAV start; otherwise expect a slight decrease.

### 5.2 Tier 2 — Algorithmic, higher leverage

**D. Adaptive GMC alpha and k**
- *Why:* `α=0.2` was hand-tuned. Larger grids favor coverage (low α); small grids favor short paths (high α).
- *Files:* [trajectory-helper.cc](../../helper/trajectory-helper.cc) (`PlanGmc`).
- *Approach:* set `α = f(N, broadcastRadius, gridSpacing)` analytically, or grid-search per N and curve-fit.

**E. Confidence model with Bayesian prior + temporal decay**
- *Why:* makes the threshold mechanism robust and lets `τ_alert` reflect a calibrated false-alarm rate.
- *Files:* [confidence-model.{h,cc}](../../models/application/confidence-model.h).
- *Approach:* track `logOdds = Σ log(p_i / (1-p_i))` instead of raw union probability; decay older fragments by half-life parameter.

**F. Topology variants**
- *Why:* paper validates square grid; defending it as general requires testing irregular layouts (Poisson cluster, road-graph, blocked cells).
- *Files:* [topology-helper.{h,cc}](../../helper/topology-helper.h).
- *Approach:* add `TopologyHelper::CreateClustered/CreateFromCsv` alongside `CreateGrid`.

### 5.3 Tier 3 — Infrastructure / quality

**G. Unit-test harness for fragment + confidence models** (no test layer today; agree on `tests/` layout before writing).
**H. Reproducibility report:** automate the seed=1..100 sweep into a single `tools/reproduce-fig3.sh` and emit a CSV that the analysis notebook can ingest.
**I. Channel model knobs:** Doppler / Rician option in CC2420 wrapper (impacts `usePerfectChannel=false` runs).

### 5.4 Recommended starting point
Begin with **A** (evidence profile) — it's a single-file change, gated behind a new enum, and the resulting metrics shift will tell us whether B and C are worth doing in their current form.

---

## 6. Conventions and Gotchas

- **Python 3.10 or 3.13 only.** 3.14 fails NS-3's wrapper at `./ns3 line 129` (`store_true` on positional). Don't patch the wrapper.
- **Touch only `src/wsn-uav/`.** Treat the rest of NS-3 as read-only framework code.
- **CC2420 reuse:** include via `${libwsn}` in `LIBRARIES_TO_LINK`; do not fork CC2420 sources.
- **Backwards-compat rule:** any change must keep S1 baseline at 14.69 s on `seed=1, gridSize=10`. Add new behavior behind a flag in `SimulationConfig`.
- **Determinism:** all RNGs must take `config.seed` (or a derived seed). Avoid `time(0)`.
- **No global state.** Phase 0 removed the legacy `g_groundNetworkPerNode` and `g_resultFileStream`; don't reintroduce them.
- **Output paths:** results land in `src/wsn-uav/results/scenario-N/run-NNN/`. The HTML viewer is the primary debugging tool.

---

## 7. Pointers to Deeper Docs (only if needed)

| Topic | Doc |
|---|---|
| Architecture diagrams, packet headers, simulation flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Why Scenario 2 was abandoned | [SCENARIO_COMPARISON.md](SCENARIO_COMPARISON.md) |
| Phase 1 multi-UAV design rationale | [PHASE1_MULTIUAV_COOP_DESIGN.md](PHASE1_MULTIUAV_COOP_DESIGN.md) |
| Phase 1 implementation details and metrics | [PHASE1_FINAL_STATUS.md](PHASE1_FINAL_STATUS.md) |
| Advanced features (dynamic k, per-UAV path complexity) | [SESSION_ADVANCED_FEATURES.md](SESSION_ADVANCED_FEATURES.md) |
| Full CLI parameter reference | [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) |
| Build system / Python version notes | [IMPORTANT_SETUP_NOTES.md](IMPORTANT_SETUP_NOTES.md) |
| Phase 0 refactor (single → N UAV plumbing) | [PHASE0_COMPLETION_REPORT.md](PHASE0_COMPLETION_REPORT.md) |

Older session logs (`SESSION_*.md`, `session*.md`) are kept for historical record but are superseded by the docs above.

---

## 8. Open Questions for Next Working Session

1. Which of A/B/C in §5.1 do we tackle first? (Recommendation: A, then re-measure B/C value.)
2. Do we want a `tests/` directory before changing the fragment model, or after?
3. Is paper Fig.3 reproduction (mean + 95% CI over 100 seeds) a deliverable for this phase, or just a sanity check?
4. Should improvements be additive (new flag, default off) or replace the existing behavior?
