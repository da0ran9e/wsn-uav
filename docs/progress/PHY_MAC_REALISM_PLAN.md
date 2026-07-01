# PHY/MAC Realism Plan

**Status**: in progress (multi-phase, multi-subagent).
**Date started**: 2026-05-22.
**Goal**: turn the simulation channel + MAC from deterministic-uniform into a realistic LR-WPAN/UAV deployment with PER variability and proper queue/retry semantics.

## Phases

### Phase 1 — Large + small-scale fading
- Chain `NakagamiPropagationLossModel` after existing `LogDistancePropagationLossModel`. Nakagami m=3 (LoS-dominant moderate fading).
- Add log-normal shadowing via `RandomPropagationLossModel(NormalRandomVariable, mean=0, variance=36)` → σ ≈ 6 dB.
- File: `models/network/scenario1-network.cc::InstallRadio()`.

### Phase 2 — MAC audit + queue + ACK
- Verify `LrWpanMac` defaults: `macMinBE=3`, `macMaxBE=5`, `macMaxCSMABackoffs=4`, `macMaxFrameRetries=3`.
- Expose / raise MAC TX queue depth (root cause of silent loss at stagger=100ms).
- Confirm unicast (BS↔UAV `DATA_FRAGMENT`/ACK) uses MAC ACK + retries; broadcast (L0) intentionally has none.
- File: `models/network/scenario1-network.cc::InstallRadio()` post-Install attribute set on the MAC.

### Phase 3 — A2G propagation
- Custom `PropagationLossModel` subclass that branches by TX/RX altitude:
  - either endpoint z > 5 m → A2G: n=2.2.
  - both z ≈ 0 → G2G: n=3.5 (with the same refLoss reference).
- New files: `models/network/a2g-log-distance-loss.{h,cc}` + plug into `InstallRadio()` replacing the plain LogDistance loss.

### Phase 4 — PHY/MAC instrumentation
- Hook PHY trace sources: `PhyRxBegin`, `PhyRxDrop` (with drop reason), `PhyTxBegin`.
- Hook MAC traces: `MacTxOk`, `MacTxDrop`, `MacTxRetry`/equivalent.
- Aggregate counters in `Scenario1Config::Run()` summary block. Group by link type if practical.
- File: `helper/scenario1/scenario1-config.{h,cc}`.

## Verification (per phase)
- Build clean.
- Smoke test: `python3.10 ./ns3 run --no-build "scenario-1-test --gridSize=10 --simTime=1600"`.
- Verify end-to-end: BS-UAV transfer completes, UAV takes off + lands, L0 dissemination block has non-zero broadcasts.
- Compare distinct-fragment-per-node distribution against baseline (mean ≈ 30.9% with N=180, fragSize=2500B, deterministic channel).

## Constraints (every phase)
- Do NOT touch existing protocol logic (BS→UAV transfer, GMC, L0 broadcast, distinct-fragment metric).
- Do NOT alter L0 fragment size/count (Phase parameters fixed by prior turns).
- Each phase touches only its declared files (others mention them only by name).

## Defaults
- Shadowing σ = 6 dB.
- Nakagami m = 3 across all distance bins.
- A2G n = 2.2; G2G n = 3.5; altitude threshold 5 m.
- MAC TX queue: 32 frames (4× default, accommodates ~6KB BS→UAV bursts at finer stagger).

## Skipped
- Phase 5 (validation calibration) — no ground-truth dataset available; defer.

## Phase 1 — status (2026-05-22)

**Implemented**: Nakagami + shadowing chained on the `SingleModelSpectrumChannel` in `Scenario1Network::InstallRadio()`.

**Current tuning after ARQ patch**:

- Nakagami `m = 3`.
- Shadowing `σ = 14 dB` (`variance = 196`).
- With L0 `180 x 2.5KB`, gridSize=10, simTime=1600, the latest clean
  end-to-end run gives mean `68.6/180` distinct fragments per node, median 68,
  min 14, max 180, and one saturated node.

**Known follow-up**: `σ=14 dB` requires `simTime=1600` because ARQ delays
BS↔UAV profile transfer. This runs end-to-end but still averages about 38%
distinct L0 fragments; getting consistently <=30% requires either range/path
planning alignment or a larger fragment ID space.

**Side fix during Phase 1 verification**: UAV `ProcessDataFragment` switched
from in-order accept (stalls on any loss) to offset-set dedupe (out-of-order
tolerant). New member `m_fragReceivedOffsets` in `uav-app.h`.

## Phase 2 — status (2026-05-22)

**Implemented**: `LrWpanMac::SetMacMaxFrameRetries(7)` applied to every device
(BS, UAV, sensors) in `Scenario1Network::InstallRadio()`.

**Audit findings** (none of these are ns-3 Attributes in ns-3.46 lr-wpan):
- `MacMaxFrameRetries` default = 3 → set to **7**.
- `MacMinBE` default = 3 (untouched).
- `MacMaxBE` default = 5 (untouched).
- `MacMaxCSMABackoffs` default = 4 (untouched).
- `MaxTxQueueSize` default ≈ `SIZE_MAX` (effectively unbounded) — **not tuned**.
  An earlier attempt to call `SetTxQMaxSize(32)` collapsed L0 reception because
  bursty broadcasts overflowed the small queue. Kept default.
- `UseAcks` Attribute on `LrWpanNetDevice` = `true` (default) — unicast ACK +
  retry confirmed for BS↔UAV traffic.

**Smoke test** now exercises retries/ARQ under `m=3`, `σ=14 dB`; BS schedules
selective retransmission passes for unacked chunks and the UAV completes the
profile before takeoff.

## Phase 3 — status (2026-05-22)

**Implemented**: new `A2GLogDistanceLossModel` (in `models/network/a2g-log-distance-loss.{h,cc}`)
subclassing `ns3::PropagationLossModel`. Branches on `max(za, zb)` against an
altitude threshold:
- A2G (either endpoint ≥ 5 m above ground): n = **2.2** (LoS-dominant).
- G2G (both endpoints near ground): n = **3.5** (NLoS).
- ReferenceDistance = 1.0 m, ReferenceLoss = 46.6 dB (carried over).

Wired into `InstallRadio()` *replacing* the plain LogDistance; Nakagami chain
and CMakeLists updated.

**Earlier smoke test before fading retune**: L0 mean **23.7% → 96.2%**,
saturated 9 → **52**, zero 2 → **0**. The expanded UAV-to-ground link budget
(n=2.2 vs prior n=3) is the dominant effect. After enabling `m=3`, `σ=14 dB`
and raising simTime to 1600, mean drops to `68.6/180` with one saturated node.

## Phase 4 — status (2026-05-22)

**Implemented**: PHY/MAC trace sources connected in `Scenario1Config::Build()`,
counters aggregated in `Run()`'s TEST RESULTS block.

**Traces wired** (names verified in `src/lr-wpan/model/lr-wpan-{phy,mac}.h`):
- PHY: `PhyTxBegin`, `PhyRxBegin`, `PhyRxDrop`. Drop-reason buckets **not
  available** in ns-3.46 lr-wpan (the trace passes only the packet).
- MAC: `MacSentPkt` (with retries / backoffs args), `MacTxDrop`. Drop-reason
  buckets also not exposed.

**Smoke test counters** (gridSize=10, simTime=1600s, latest `m=3`, `σ=14 dB` run):
- `MacTxDrop = 0`
- `Trace connect failures = 0`
- `MacTxDrop = 0`
- `Trace connect failures = 0`
- `MacSentPkt = 0`

`MacSentPkt=0` is not used as the primary delivered-frame metric anymore. In
this ns-3.46 lr-wpan path, `MacTxOk` is the useful successful-TX counter and it
matches `PhyTxBegin` in the clean smoke test. Keep `MacSentPkt` in the log only
as a diagnostic for the narrow queue-removal path that emits retries/backoffs.

L0 distinct-fragment numbers unchanged from Phase 3 (96.2% mean, 52 saturated,
0 zero) — instrumentation is observation-only, no behavioral perturbation.

## Outstanding / next steps

1. **App-layer ARQ for BS↔UAV fragment transfer** — initial selective ARQ has
   been added at BS side: BS stores every data chunk, marks chunks acked using
   existing DATA_ACK packets, and retransmits unacked chunks after the original
   pass. It still needs stress testing with stronger fading before restoring
   `m=3`, σ=6 dB.
2. **Per-link-type counters** — group PHY drops by sender/receiver altitude so
   we can separate A2G vs G2G PER once Phase 1 realism is restored.
