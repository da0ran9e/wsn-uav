# Scenario-1 Model Improvement Roadmap

**Date:** 2026-05-05
**Scope:** Single-UAV scenario only. Multi-UAV (S3) gets the same improvements for free where applicable.
**Source framework:** 66-model catalog (categories A–J, IDs G1…A8) provided by user.

---

## 1. Purpose & Constraints

Goal: make Scenario 1 a *realistic* single-UAV intrusion-detection simulator, not just a paper-baseline reproduction. "Realistic" means each modeled phenomenon has a defensible source (paper, datasheet, or measurement) and the simulator's outputs (T_detect, energy, coverage uniformity, channel statistics) match published references within a stated tolerance.

**Hard constraints:**
- All work stays inside `src/wsn-uav/`. CC2420 reused via `${libwsn}`.
- Every change is gated by a `SimulationConfig` flag with a backward-compat default.
- The reference run **`./ns3 run "scenario-1-single-uav --gridSize=10 --seed=1"` must keep producing T_detect = 14.69 s** with default flags. New behavior is opt-in.
- Determinism: every new RNG draws from `config.seed`-derived streams.

**Out of scope for this roadmap:**
- Single-UAV scenario means models that exist purely for multi-UAV coordination (F2, F8–F10, L4–L8, A4–A5, M4) are deferred or repurposed as cross-scenario tools. They reappear in S3 work only.

---

## 2. Gap Analysis — User's 66 Models vs Current S1

Legend: ✅ implemented · 🟡 partial · ❌ missing · ⛔ not applicable to single-UAV

### A. Geometric (8)
| ID | Model | Status | Where / Notes |
|---|---|---|---|
| G1 | Node Distribution | 🟡 | Grid only ([topology-helper.cc](../../helper/topology-helper.cc)). No Poisson, cluster, road-graph. |
| G2 | UAV Deployment | ✅ | Configurable via `uavStartingX/Y/Z`. |
| G3 | Broadcast Range | ✅ | `UAV_BROADCAST_RADIUS=50 m` ([parameters.h:31](../../models/common/parameters.h)). |
| G4 | Coverage Circle | ✅ | Used implicitly in GMC and viz. |
| G5 | Distance Calculation | ✅ | NS-3 `Vector::GetDistanceFrom`. |
| G6 | Conflict Detection | ⛔ | Single-UAV → no overlapping coverage. |
| G7 | Spatial Clustering | ✅ | K-means in [trajectory-helper.cc](../../helper/trajectory-helper.cc). |
| G8 | Voronoi Diagram | ⛔ | Multi-UAV concept. |

### B. Channel/Communication (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| C1 | Path Loss | ✅ | CC2420 free-space + log-distance via `Cc2420SpectrumPropagationLossModel`. |
| C2 | Shadowing | ✅ | `EnableShadowing=!usePerfectChannel`. Log-normal σ from CC2420 default. |
| C3 | Fading (Rayleigh) | ❌ | **No fading layer. Major gap.** |
| C4 | SNR Calculation | ✅ | Internal to `Cc2420Phy`. |
| C5 | Packet Reception Probability | ✅ | `Cc2420ErrorModel` (BER → PER). Not exposed/logged. |
| C6 | Contact Window | 🟡 | `Cc2420ContactWindowModel` exists in wsn but unused in our metrics. |
| C7 | Fragment Reception Model | 🟡 | Implicit via CC2420; no analytic model. |
| C8 | Confidence Accumulation | ✅ | Union probability ([confidence-model.cc](../../models/application/confidence-model.cc)). |

### C. Mobility (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| M1 | Waypoint Trajectory | ✅ | `WaypointMobilityModel`. |
| M2 | Constant Speed | ✅ | Speed from waypoint Δt. |
| M3 | Acceleration | ❌ | Instant velocity change between waypoints. |
| M4 | Collision Avoidance | ⛔ | Single UAV. |
| M5 | Altitude Control | ✅ | Waypoint z. |
| M6 | Turning Radius | ❌ | Sharp 90° turns happen freely. |
| M7 | Wind Model | ❌ | Not modeled. |
| M8 | Continuous vs Discrete | ✅ | NS-3 event-driven. |

### D. Energy (10)
| ID | Model | Status | Notes |
|---|---|---|---|
| E1–E7 | UAV propulsion energy | ❌ | **Completely absent. Highest-impact gap.** |
| E8 | Radio TX energy | 🟡 | `Cc2420EnergyModel` exists in wsn, not wired into wsn-uav. |
| E9 | Battery Depletion | ❌ | No battery state, no remaining-energy metric. |
| E10 | Wind-adjusted energy | ❌ | Depends on M7 + E1. |

### E. Fragment Dissemination (10)
| ID | Model | Status | Notes |
|---|---|---|---|
| F1 | Broadcast Schedule | 🟡 | Cyclic round-robin, fixed interval. No coordination scheduling. |
| F2 | Fragment-to-UAV Assignment | ⛔ | Multi-UAV concept (S3 has it). |
| F3 | Broadcast Interval | ✅ | `broadcastInterval=0.2 s`. |
| F4 | Fragment Size | 🟡 | `Fragment.sizeBytes` exists; `Generate()` sets 0; only `GenerateWithSizes()` sets real values. **No TX-time delay tied to size in S1.** |
| F5 | Packet Reception | ✅ | Via MAC. |
| F6 | Fragment Accumulation | ✅ | `ConfidenceModel`. |
| F7 | Confidence Model | 🟡 | Independent-evidence union only. No Bayesian / decay / hysteresis. |
| F8 | Replication Strategy | ❌ | UAV cycles fragments; no targeted retransmit. |
| F9–F10 | Collision-free / TDMA | ⛔ | Multi-UAV. |

### F. Fairness & Load-Balancing (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| L1 | Jain's Fairness | ❌ | **Not computed.** Easy add. |
| L2 | Coverage Coefficient | 🟡 | Per-node confidence is tracked; per-node coverage % not exported. |
| L3 | Min-Max Fairness | ❌ | Not exported. |
| L4–L8 | Multi-UAV load balance | ⛔ | S3 territory. |

### G. Performance Metrics (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| P1 | Time-to-Detection | ✅ | `detection_time_seconds`. |
| P2 | Detection Rate | ❌ | Only first-trigger node; no `% nodes ≥ τ_alert`. |
| P3 | Speedup Factor | 🟡 | Implicit when comparing S1 vs S3. |
| P4 | Energy Efficiency | ❌ | Needs E1–E9 first. |
| P5 | Energy Overhead | ❌ | Same. |
| P6 | Mission Completion Time | 🟡 | Total path / speed implied; not exported. |
| P7 | Coverage Uniformity | ❌ | Needs L1/L2. |
| P8 | Battery % Remaining | ❌ | Needs E9. |

### H. Simulation Control (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| S1 | Time Discretization | ✅ | NS-3. |
| S2 | Random Seed | ✅ | `config.seed`. |
| S3 | Monte Carlo Sampling | 🟡 | Manual loop in shell. No batch tool. |
| S4 | Event Queue | ✅ | NS-3. |
| S5 | State Management | ✅ | Per-node ConfidenceModel. |
| S6 | Statistics Collection | ✅ | `StatisticsCollector`. |
| S7 | Visualization | ✅ | HTML Canvas viewer. |
| S8 | Validation Checker | 🟡 | `SimulationConfig::Validate()` only checks config bounds. |

### I. Optimization (7)
| ID | Model | Status | Notes |
|---|---|---|---|
| O1 | K-means | ✅ | Lloyd, fixed 10 iter. |
| O2 | ACO | ❌ | Not used. |
| O3 | 2-opt | ❌ | Greedy + GMC only. |
| O4 | Greedy Fragment Assignment | ⛔ | Multi-UAV. |
| O5 | Genetic Algorithm | ❌ | Out of scope. |
| O6 | Simulated Annealing | ❌ | Out of scope. |
| O7 | Dynamic Programming | ❌ | Out of scope. |

### J. Advanced (8)
| ID | Model | Status | Notes |
|---|---|---|---|
| A1–A2 | Network/Fountain coding | ❌ | Out of scope (defer to thesis-level). |
| A3 | Interference | ⛔ | Single TX. |
| A4–A5 | TDMA/FDMA | ⛔ | Multi-UAV. |
| A6 | Deep fading | ❌ | Subsumed by C3. |
| A7 | Doppler Effect | ❌ | UAV at 20 m/s, 2.4 GHz → ~160 Hz shift; minor for S1. |
| A8 | Blockage Model (LOS/NLOS) | ❌ | Real urban scenarios need this. Important for paper context. |

**Summary:** out of 66 models, ~22 are already in (✅), ~12 are partial (🟡), ~20 are missing-and-relevant for S1 (❌), and ~12 are not applicable (⛔). Phase plan below targets the ❌ + 🟡 set.

---

## 3. Strategic Themes

The 20 relevant gaps cluster into four themes:

1. **Energy realism** — D (E1–E10), P4/P5/P8. Without this, S1 can't justify "UAV-assisted" claims quantitatively.
2. **Channel/PHY realism** — C3, C5 logging, C6 export, A7, A8. Drives PER and contact-window stochasticity.
3. **Application-layer realism** — F4 (size→TX time), F7 (Bayesian confidence), F8 (smart replication), G1 (non-grid topology).
4. **Evaluation realism** — L1–L3, P2, P6, P7, S3 (batch sweeper), S8 (cross-checks).

We tackle them in roughly this order because (a) energy is purely additive (zero risk), (b) channel changes are the riskiest so they get a flag and validation early, (c) application-layer ties to evidence model already flagged in HANDOFF.md, (d) evaluation tooling is the lowest priority but unblocks paper-quality validation.

---

## 4. Phased Plan

Each phase: ~1.5–2 weeks of focused work. Phase exits when its acceptance gate passes.

### Phase A — Energy Modeling and Evaluation Tooling (≈1.5 weeks)

**Why first:** purely additive, zero risk to baseline T_detect. Unlocks P4, P5, P8 metrics. Cheapest realism win per LOC.

**Models added/promoted:**
- E1: Total energy = Σ(P × Δt) (new model class).
- E2: Cruise power `P_cruise(v)` — quadratic from published quad-rotor curves: `P = P0 + P1·v + P2·v²` (E7).
- E3: Hover power `P_hover` (constant ~350 W typical small quad).
- E5: Acceleration cost (small additive term).
- E8: Radio TX energy via `Cc2420EnergyModel` (already in `src/wsn`, just wire it in).
- E9: Battery depletion + remaining-energy state.
- P4, P5, P6, P8: derived metrics.
- L1, L2, L3, P2, P7: fairness + coverage metrics (per-node confidence histogram already exists, just need to aggregate).
- S3: shell wrapper / Python script for batch Monte Carlo (`tools/reproduce-fig3.sh` style).

**Files (new):**
- `src/wsn-uav/models/common/energy-model.{h,cc}` — `UavEnergyModel` class with `OnVelocityChange()`, `Step(dt)`, `GetTotalEnergy()`, `GetBatteryPercent()`. Listens to `WaypointMobilityModel` velocity trace.
- `src/wsn-uav/models/common/fairness-metrics.{h,cc}` — pure functions: `JainsIndex(vector<double>)`, `MinConfidence`, `MaxConfidence`, `Variance`, `CoverageRatio(threshold)`.
- `tools/run-monte-carlo.sh` (or `.py`) — sweeps seed + grid size, aggregates `metrics.csv` rows.

**Files (modified):**
- [helper/wsn-network-helper.cc](../../helper/wsn-network-helper.cc): instantiate `UavEnergyModel` per UAV, attach to mobility, sample at end.
- [helper/result-writer.cc](../../helper/result-writer.cc): write `energy_total_wh`, `battery_remaining_pct`, `detection_rate`, `coverage_jain`, `min_confidence`, `mission_time_s`, `mission_efficiency_wh_per_pct`.
- [helper/wsn-network-helper.h](../../helper/wsn-network-helper.h): new fields in `SimulationResults`. New `SimulationConfig` flag `enableEnergyModel = true` (default ON because purely additive).
- [examples/scenario-1-single-uav.cc](../../examples/scenario-1-single-uav.cc): print new summary lines.

**New CLI parameters:** `--p0 --p1 --p2` (cruise power coeffs), `--pHover`, `--batteryWh` (default 90.2 Wh per user spec).

**Acceptance gate (Phase A):**
1. Default S1 run: T_detect = 14.69 s ± 0.01 s (unchanged).
2. New energy column appears in `metrics.csv` and is non-zero.
3. Cross-check: at `uavSpeed=20 m/s, P0=0, P1=0, P2=0.085, T_path=33 s` → `E ≈ 1.12 Wh`, battery_pct ≈ 98.8%.
4. Jain's index computed on per-node confidence: ≥ 0.85 for default S1 (consistency check, not paper claim).
5. Monte Carlo script can run 100 seeds × 4 grid sizes in <2 hours, emits aggregated CSV.

---

### Phase B — Channel/PHY Realism (≈2 weeks)

**Why second:** highest-risk-to-baseline. Behind a flag with paper-comparable validation.

**Models added/promoted:**
- C3: Rayleigh / Rician fading layer composed onto CC2420 path-loss + shadowing.
- C5 export: per-packet PER + chosen-modulation outcome surfaced into `packets.csv` (so we can plot PER vs distance like paper Section V.C).
- C6: Contact-window export — for each (UAV, ground-node) pair, log `(t_enter, t_exit, duration)`.
- C7: Analytic fragment-reception model — predicted vs simulated # fragments in a contact window.
- A7: Doppler shift logged (informational only — at 20 m/s, 2.4 GHz: Δf ≈ 160 Hz, well within CC2420 tolerance).
- A8: Blockage model — Boolean LOS/NLOS map, NLOS adds extra attenuation. Optional grid layer.

**Files (new):**
- `src/wsn-uav/models/channel/fading-loss-model.{h,cc}` — `RayleighFadingLossModel : SpectrumPropagationLossModel`. Composes onto CC2420's existing chain.
- `src/wsn-uav/models/channel/blockage-map.{h,cc}` — load grid layer from CSV; query `IsBlocked(p1, p2)`.

**Files (modified):**
- [helper/wsn-network-helper.cc](../../helper/wsn-network-helper.cc): if `useFading=true`, attach fading model. If `useBlockage=true`, load blockage CSV.
- [helper/result-writer.cc](../../helper/result-writer.cc): new columns in `packets.csv` (`per`, `los`, `doppler_hz`).
- New `tools/plot-per-vs-distance.py` to validate channel realism.

**New CLI parameters:** `--useFading=false` (default off — backward-compat), `--fadingType=rayleigh|rician`, `--ricianK=4`, `--useBlockage=false`, `--blockageFile=path.csv`.

**Acceptance gate (Phase B):**
1. With all new flags off: T_detect = 14.69 s (unchanged).
2. With `useFading=true, fadingType=rayleigh`: PER at 50 m matches Rayleigh theory `PER = 1 - exp(-γ_th/γ̄)` within 5% over 1000-packet sample.
3. PER-vs-distance curve from `packets.csv` matches paper Section V.C (35.3% mean PER) within ±5 percentage points at default config.
4. Contact window durations logged for ≥95% of (UAV, candidate) pairs.

---

### Phase C — Application-Layer Realism (≈2 weeks)

**Why third:** depends on Phase B (need realistic PER to test confidence/replication strategies).

**Models added/promoted:**
- F4 wire-up: actual TX duration `t_tx = (sizeBytes·8) / DATA_RATE_BPS` consumed in S1 (already done in S3, port to S1 with flag).
- F7 upgrade — Bayesian confidence: `logOdds = Σ log(p_i / (1-p_i))`; threshold expressed in log-odds; optional half-life decay `λ`.
- F8 — replication: UAV detects PER feedback (via missing-fragment manifests it overhears) and re-broadcasts under-delivered fragments. Bound by max-replication factor.
- F1 evolution: instead of fixed cycle, prioritize fragments with lowest delivered-confidence-mass.
- G1 alternates: `TopologyHelper::CreatePoissonPP(area, density, seed)` and `CreateClustered(K, σ, area, seed)`.
- The fragment-evidence enum from HANDOFF.md §5.1.A merges in here (`EvidenceProfile`).

**Files (new):**
- `src/wsn-uav/models/application/replication-policy.{h,cc}` — pluggable strategy: `Uniform`, `LowestConfidence`, `LongestSinceTx`.
- `src/wsn-uav/models/application/evidence-profile.{h,cc}` — `Uniform | ZipfHotspot | Gaussian2D | ExternalCsv`.

**Files (modified):**
- [models/application/confidence-model.{h,cc}](../../models/application/confidence-model.h): add log-odds path behind `useLogOdds=false` flag (default keeps the union formula). Add optional `decayHalfLife` in seconds.
- [models/application/fragment-dissemination-app.cc](../../models/application/fragment-dissemination-app.cc): replace `m_nextFragmentIndex` cycler with policy-driven scheduler when `useSmartReplication=true`.
- [models/application/fragment-model.cc](../../models/application/fragment-model.cc): add `Generate(count, masterConf, profile, seed)`.
- [helper/topology-helper.{h,cc}](../../helper/topology-helper.h): add Poisson and clustered topologies behind `topologyType` enum.

**New CLI parameters:** `--useLogOdds=false`, `--decayHalfLife=0`, `--useSmartReplication=false`, `--replicationPolicy=uniform`, `--maxReplications=3`, `--evidenceProfile=uniform`, `--topologyType=grid`.

**Acceptance gate (Phase C):**
1. Defaults preserved: T_detect = 14.69 s.
2. With `useLogOdds=true` and equivalent threshold transform: T_detect within ±0.5 s of baseline (numerical equivalence sanity check).
3. With `useSmartReplication=true` over a Phase-B realistic channel: T_detect ≤ baseline T_detect, energy unchanged ±10%.
4. With `evidenceProfile=zipfHotspot`: detection probability concentrates near hotspots (qualitative — visualization shows it).

---

### Phase D — Mobility Physics + Trajectory Polish (≈1.5–2 weeks)

**Why last:** smallest realism payoff for S1 (paper-rate effect on T_detect is small), but completes the picture.

**Models added/promoted:**
- M3: Acceleration / deceleration ramps (`a_max=3 m/s²`).
- M6: Turning radius — `r_min = v² / a_lateral_max`; insert circular arc segments when waypoint angles exceed limit.
- M7: Wind model — constant or randomly-varying wind vector; UAV ground velocity = airspeed + wind; affects energy via E10.
- E10: wind-adjusted energy (depends on E2 and M7).
- O3: 2-opt local search post-pass on GMC waypoints.
- O6: simulated annealing variant of trajectory polish (optional research lever).
- S8: simulator validation pass — sanity-check that no waypoint distances are zero, that trajectory closes, energy is monotone, etc.

**Files (new):**
- `src/wsn-uav/models/mobility/uav-physics-model.{h,cc}` — wraps `WaypointMobilityModel` + applies accel limits + turn radius + wind.
- `src/wsn-uav/helper/trajectory-helper.cc::TwoOptPolish()` — local-search refinement step.

**Files (modified):**
- [helper/wsn-network-helper.cc](../../helper/wsn-network-helper.cc): swap mobility model when `useUavPhysics=true`.
- [helper/trajectory-helper.cc](../../helper/trajectory-helper.cc): optional 2-opt pass after `PlanGmc()` / `PlanNearestNeighbor()`.

**New CLI parameters:** `--useUavPhysics=false`, `--aMax=3.0`, `--latAccelMax=2.0`, `--windVx=0`, `--windVy=0`, `--windRandomStd=0`, `--use2Opt=false`.

**Acceptance gate (Phase D):**
1. Defaults preserved: T_detect = 14.69 s.
2. With `useUavPhysics=true, aMax=3, latAccelMax=2`: T_detect within +0–10% of baseline (slower because of accel ramps); energy increases proportional to speed-square integral (sanity check).
3. With `use2Opt=true` on S3 large grids: total UAV path length decreases by ≥3% on at least 50% of seeds (since GMC is already greedy-good, 2-opt is a polish, not a revolution).
4. Wind: with `windVx=5 m/s` against UAV direction, energy increases by a measurable amount matched to E10 closed-form.

---

## 5. Cross-Cutting Concerns

### 5.1 Validation & Acceptance
Every phase ends with: (a) baseline preservation, (b) at least one quantitative external-reference cross-check (paper figure, datasheet curve, theory), (c) regression test in `tests/` (start the directory in Phase A — minimal smoke + numerical-equivalence checks).

### 5.2 Configuration discipline
All new fields live in `SimulationConfig` with explicit defaults. No silent global flags. New flags are listed in `CONFIGURATION_GUIDE.md` as part of the same PR that adds them.

### 5.3 Result schema evolution
`metrics.csv` has been growing. Treat it as a versioned schema: every new column documented in `result-writer.cc` header with its phase tag (e.g., `// Phase A`). Keep it append-only; never reorder existing columns.

### 5.4 Reproducibility
A `tools/repro-baseline.sh` should run after every phase and assert the baseline T_detect line. CI-able. Expand into a pytest harness in Phase D.

### 5.5 Documentation updates
At end of each phase: update `HANDOFF.md` §4 and §5 to reflect new state, and append a one-page session note. Don't write multi-doc fanouts like the May 5 batch.

---

## 6. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Energy-model parameter values lack good source | Med | Cite published quadrotor power curves in code comment; expose via CLI for user calibration. |
| Rayleigh fading composition breaks CC2420 numeric stability | Low-Med | Add unit tests for the composed loss model; smoke run before merging. |
| Bayesian confidence diverges from paper formulation | Low | Keep both paths; default = union (paper). |
| Smart replication interacts with cooperation in unexpected ways | Med | Phase C gate explicitly tests it on top of Phase B realistic channel. |
| 2-opt overshoots on large k waypoint sets | Low | Cap iterations; benchmark wall-clock. |
| Schema sprawl in `metrics.csv` | Med | Per-phase column tagging; column-count diff in CI. |

---

## 7. Order of Operations & Time Estimate

```
Week 1–1.5:  Phase A  (energy + metrics + batch tooling)   ← start here
Week 2–4:    Phase B  (fading, blockage, contact-window export)
Week 4–6:    Phase C  (log-odds confidence, evidence profile, smart replication, alt topologies)
Week 6–8:    Phase D  (UAV physics, wind, 2-opt polish)
Week 8:      Final paper-Fig.3 reproduction sweep, write-up
```

Total: ~8 weeks of focused effort assuming a single contributor and no major NS-3 surprises.

---

## 8. What to Decide Before Phase A Starts

These are your calls — they shape the work:

1. **Energy parameter source:** do we cite a specific quadrotor (e.g., DJI Mavic 3, custom platform) or use generic published curves? This affects which numbers we hard-code as defaults.
2. **`tests/` directory:** create it in Phase A or only when needed? I recommend Phase A — even one test prevents silent regressions.
3. **Backward-compat policy:** is `enableEnergyModel=true` (default ON, since it's purely additive) acceptable, or do you want every new model gated OFF by default?
4. **Paper Fig.3 reproduction tolerance:** what counts as a match — within 5% mean? Within 95% CI? This sets validation strictness.
5. **Phase A vs HANDOFF §5.1 ordering:** HANDOFF.md proposed evidence-profile (item A) as the first model change. This roadmap puts it in Phase C. Do you want energy first (this roadmap) or evidence-model first (HANDOFF)? Energy first is lower risk; evidence first has higher conceptual payoff.

---

## 9. References

- Current state and code map: [HANDOFF.md](HANDOFF.md)
- Architecture diagrams: [ARCHITECTURE.md](ARCHITECTURE.md)
- Why S2 was abandoned: [SCENARIO_COMPARISON.md](SCENARIO_COMPARISON.md)
- Phase 1 multi-UAV (for cross-references): [PHASE1_FINAL_STATUS.md](PHASE1_FINAL_STATUS.md)
- CC2420 reuse: `src/wsn/model/radio/cc2420/` — `cc2420-energy-model.h`, `cc2420-error-model.h`, `cc2420-contact-window-model.h` are already there and underused.
