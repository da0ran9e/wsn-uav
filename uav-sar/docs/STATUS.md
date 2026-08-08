# UAV-SAR — project status and handover

**Read this first in any new session.** It is the single place that says what is
true right now, what is stale, and what to do next. Everything else in
`docs/` is either a historical audit record or a results file that this document
tells you how far to trust.

- Branch: `claude/document-review-xslwgg`
- Last commit at time of writing: see `git log`; this file was last revised after the airframe + false-positive work
- Build: `cd /home/user/ns3-dev && /usr/bin/cmake --build cmake-cache -j 3`
- Binary: `build/src/uav-sar/examples/ns3.46-scenario-sar-optimized`

---

## 1. The one finding that changes the paper

**Cooperation does not buy the cost advantage. Closing the loop does.**

Every baseline except one is *open-loop* — it blankets the field and never
reacts. The large cost gap over those baselines therefore confounded two things:
having feedback at all, and aggregating it cooperatively. `--scheme=closed-loop`
(audit W4) separates them: identical fleet, cue sweep, delivery and completion
rule; the only difference is the ground has **no cooperative substrate** — a node
answers whatever UAV is overhead with a direct single-hop ECHO, with no cell
tree, no cross-cell SHARE and no election.

16×16, N = 120 paired seeds, realistic sensing:

| metric | proposed | closed-loop | proposed wins | Cliff δ | p |
|---|---:|---:|---:|---:|---:|
| mission time | 103.9 s | **99.2 s** | 17/117 | +0.479 | 6.6e-15 |
| UAV energy | 68.3 kJ | **61.1 kJ** | 15/120 | +0.569 | 7.5e-18 |
| application packets | 3 471 | **1 616** | **0/120** | +0.997 | 2.0e-21 |
| fix error (median) | **14.6 m** | 19.0 m | 51/117 | −0.159 | 0.0047 |
| fix error (p90) | **29.9 m** | 42.0 m | — | — | — |
| victim served | **92.5 %** | 87.5 % | — | — | — |

**What cooperation defensibly buys**, for +5 % time, +12 % energy, +115 % packets:
a **−29 % p90 fix error** (tail robustness — the strongest of the three), a small
median gain (δ = −0.159, wins by margin not frequency), and a directional-only
reliability edge.

**The claim the data supports:** *closing the loop delivers the cost advantage
over blind coverage; edge cooperation buys a markedly better tail on the
delivered position, at a stated cost.* Anything stronger is not supported.

---

## 2. Trust level of every number

> **ALL head-to-head numbers below are STALE as of the airframe change.** Every
> published comparison was measured with all roles at 20 m/s; the DATA/hovering
> role is now 15 m/s (rotary-wing) against the FAST role's 20 m/s (fixed-wing),
> which moves every scheme including all four baselines. They also predate the
> false-positive work (resolution on complete data, REJECT closure, en-route
> cueing). Re-run before quoting anything in this table.

| source | status |
|---|---|
| `RESULTS-ambiguity-vi.md` §1–5 | **current** — measured on the false-positive build, N=120 |
| `RESULTS-ambiguity-vi.md` §5b | **RETRACTED in §5c** — degenerate configuration |
| `RESULTS-honest.md` §W4 (closed-loop) | **STALE** — airframe change |
| `RESULTS-honest.md` 16×16 head-to-head | **STALE** — airframe change + false-positive work |
| `RESULTS-honest.md` 8×8 head-to-head | **STALE** — not re-run since `b4ac588` either |
| all baseline arms (`tsp-mc`, `nocoop`, `pure-uav`) | **STALE** — they never touch the cooperative plane, but they all fly the hovering airframe, so 20 → 15 m/s moves every one of them |
| anything measured at N = 20 | **VOID** — see §5 |
| `RESULTS.md` | **VOID**, banner at top |
| `docs/visualize/replay-40x40.html` | pre-false-positive build, keep as a "before" |
| `docs/visualize/replay-40x40-ambiguity.html` | pre-false-positive build, both arms |
| `docs/visualize/replay-40x40-patrol.html` | patrol vs parked, duplicate-band build |
| `docs/visualize/replay-40x40-current.html` | **current build**, proposed vs closed-loop |

---

## 3. Where the scheme stands mechanically

### 3.1 The false-positive work (newest, and it changed the premise)

A node judging on the FAST team's cue fragments can match a similar-looking
object; a node holding the COMPLETE reference cannot. Ambiguity is therefore a
function of how much has been delivered, and **delivering is an act of
disambiguation**, not only of service.

- **`--clutterCount / --clutterSimMin / --clutterSimMax`** — M confusable objects
  producing evidence through the *same* spatial kernel as the victim. Default 0 =
  the uniqueness assumption, byte-identical to every earlier result.
- **`--clutterResolve`** (default 1.0) — how much the complete dataset removes.
  `ClueField` emits two readings from one noise draw; the app interpolates by
  possession, so no node knows which regime it is in.
- **REJECT** — holding the dataset no longer confirms; the node must hold it AND
  still match. A leader hearing REJECT with no CONFIRM re-aims immediately.
- Measured, 16×16, N=120, M=2 at similarity 0.9: **0/120 wrong-object closures**
  (46.7 % with resolution off), victim served 90.0 % vs 44.2 %, and resolution
  **saves** 41 % of packets. Full detail in `RESULTS-ambiguity-vi.md`.

### 3.1b The multi-candidate chain — four independent single-target assumptions

The system was built around "there is one place to go", in four separate layers,
and three of them failed **silently**. Each fault was only visible once the
previous one was fixed, and none is observable while a single region is served.

| # | change | what it exposed |
|---|---|---|
| 1 | `--aimScope=160` — a leader may only aim within 2 cells of its own centre | multi-place runs 5 % → 40 %, but victim served 55 % → 37.5 % (McNemar b=7 c=0, p=0.0156) |
| 2 | — | one CLAIM sent the **whole** DATA team home: `SendClaim` hardcoded `rid = 1`, the handler ignored the region, and yielding meant "no task left". Only 1 of 16 multi-place runs served the victim |
| 3 | per-region CLAIM + `--stayAvailable` | 37.5 % → **52.5 %** (b=0 c=6, p=0.0312) — but the reported error got *worse*, 47.8 → 90.0 m |
| 4 | `--fixOnConfirm` | measured as an exact no-op. The gate worked; CONFIRM itself was firing at decoys |
| 5 | `kConfirmThreshold` split from `kCoopThreshold` | being swept (0.30/0.45/0.55/0.70) |

**Why 4 happened:** closure used `kCoopThreshold = 0.30`, the bar for "I might be
relevant". At σ = 0.20 a node with no signal clears it on noise alone with
probability Q(1.5) = 6.7 %, so a delivery footprint of a few dozen nodes produces
spurious confirmations every run. `kAlertThreshold` is not available as the fix
either: the node nearest the victim is ≤ 14.1 m away on a 20 m lattice, so its
true reading is at worst 0.75 — exactly that bar, which its own node would then
fail half the time.

**The paper claim this supports** (stronger than a bug list): *a cooperative
search system optimised for a unique target fails in four independent ways when
the world contains several candidates, and three of the four fail silently.*

### 3.2 Fleet and coverage

- **FAST = fixed-wing at 25 m/s (90 km/h), DATA = rotary-wing at 15 m/s (54 km/h).** The roles cannot
  be the same aircraft: sweeping and couriering want something that never stops,
  a 20–40 s delivery dwell wants something that can hold position. Not audit F1
  in reverse — it is a *penalty* on the hovering role, applied uniformly to every
  hovering airframe including all four baselines. Published cruise bands are
  80–110+ km/h fixed-wing and 40–60 km/h multirotor, so the old common 20 m/s
  (72 km/h) was wrong for both. It **does** advantage the proposed scheme, which
  alone flies a scout that never stops, so the paper owes an all-rotary ablation
  (`--fastSpeed=15`). See `FIXED-WING-FAST-vi.md` for what else this implies
  (the 30 s relay hold breaks; the energy curve is still the rotary one).
- **`--dataPatrol` — default ON.** It was off twice on measurements that were
  taken on a **degenerate configuration**: both teams were banded on the same
  axis, so a FAST and a DATA UAV flew a median **2.0 m** apart and the patrol
  added no coverage at all. Fixed by banding DATA on **y** (orthogonal) and
  traversing **reversed**. Separation 2.0 m → 224–310 m. Re-measured at N=120:
  energy penalty gone (p=0.958, was 4.6e-4), everything else neutral.
- **`--dataCueEnroute` — default ON.** Cue on legs already being flown. Energy
  unchanged (68.0 vs 68.3 kJ), packets +16 %. Costs radio, not airtime.
- **Cue-triggered SUMMON re-announce** (`b4ac588`) — an elected leader
  re-announces whenever it hears a CUE chunk, because that chunk proves a UAV is
  within one hop right now. Fixed 40×40 outright: victim served 0/5 → 5/5.
- **Adaptive observation window + bounded relay hold** (A10) — summon when the
  leader's own evidence stops growing; a FAST UAV holds station 30 s after its
  sweep so a relay stays airborne. *(The relay hold is the mechanism the
  fixed-wing decision threatens — see §4.)*
- **`--deliverDwell`** — reliability/cost knob, density-dependent, default 20 s.
  **Numbers stale**, measured before the airframe change.

Known-bad, do not retry without a new idea:

- **Splitting cue coverage across all 4 airframes**: victim served 90.0 → 42.5 %
  at N = 120, localization firing in only 70 % of runs. A DATA UAV diverts,
  yields or goes home mid-patrol, so any band it owns is left half-cued.
  Coverage must not depend on UAVs that can be pulled away. *But note:* the same
  change made 40×40 much faster (224 s vs 396 s). That tension is unresolved and
  is a real design question, not a bug.
- **Retarget-on-no-CONFIRM as a reliability fix**: neutral at best. The failures
  are delivery-at-range, not wrong aim. *(REJECT-driven retargeting is a
  different thing and does work — it fires on evidence, not on a timeout.)*

**Method rule earned twice in one day:** before declaring a mechanism not worth
its cost, check it is doing what its name promises. "DATA patrol does not pay"
was measured twice on a patrol that flew in formation with the sweep it was
supposed to complement; one line of trajectory arithmetic would have caught it.

---

## 4. Open problems, ranked

0. **Nothing is currently measured on the shipping build.** The airframe speed
   split and the false-positive work moved every scheme. The whole head-to-head
   (5 schemes x N=120, both grids, with and without clutter) has to be re-run
   before anything goes in a draft. This is the only thing blocking the paper.
1. **Closed-loop still beats `proposed` on cost** *(pre-airframe-change result)*. Either find where cooperation
   genuinely pays (the p90 tail is the live lead) and build the paper on that, or
   reduce the cooperative plane's packet cost. 0/120 paired wins on packets is
   the number to attack.
2. ~~**CONFIRM closure is wrong in principle.**~~ **CLOSED.** Holding the dataset
   no longer confirms: the node must hold it AND still match it on the complete
   reference, otherwise it sends REJECT. Victim-served at M = 0 moved 92.5 % ->
   95.8 % (N = 120), the direction the fix predicts -- though bundled with
   en-route cueing, so not individually attributed.
3. **W7 is half done — never call it random deployment.** `--victimOnNode=0`
   displaces the victim inside the Voronoi cell, so the nearest node never
   changes and the victim is always ≤ 14.1 m from a sensor. A PPP deployment with
   coverage holes would attack the reliability numbers much harder.
4. **W2 — no ML/NLS estimator, no CRLB.** Two crude heuristics (argmax vs
   centroid) tie, which is the signature of both sitting far from the bound.
5. ~~**The build-provenance guard is weaker than advertised.**~~ **CLOSED.**
   `config.txt` now also carries `binary=<mtime>,<size>` of `/proc/self/exe`,
   which moves on every relink, and `assert_one_build` prefers it. The
   `dataPatrol` default flip was the live case it catches: behaviour changed
   without `sar-metrics.cc` recompiling, so the old stamp stayed identical.
6. ~~**The clue field cannot produce more than one candidate request point.**~~
   **CLOSED** by `--clutterCount`, and the conclusion drawn from it was WRONG and
   is retracted: see `RESULTS-ambiguity-vi.md`. Ambiguity is not fixed, it is a
   function of how much reference data a node holds, so the 1/(M+1) ceiling binds
   only the FIRST AIM, not the mission. With `--clutterResolve=1`, M = 2 at
   similarity 0.9 gives **0/120 wrong-object closures** and costs 5.8 pp of
   reliability against no clutter at all. Original text kept below for the record:
   **The clue field cannot produce more than one candidate request point.**
   Measured with `tools/candidate_stats.cc`: at the operating point (σ = 0.10)
   K = 1 in 94.2 % of runs at 16×16 and 98.3 % at 40×40, with **zero** distant
   decoys ever. It is structural — `maxNoiseQuality = 0.18` sits far below
   `kAlertThreshold = 0.75`, so a background false positive can never become a
   request point — and `--electSuppress` then collapses whatever remains to one
   summon. This matters beyond realism: **K = 1 is exactly the regime in which
   cooperation cannot pay off on cost**, which is open problem 1. See
   `PROBLEM-MULTI-CANDIDATE-vi.md`.
7. **A7** seed couples victim position to channel realisation; **A8** the
   2 FAST + 2 DATA split gives `proposed` half the delivering airframes of
   `tsp-mc × 4` (conservative, but must be stated in the paper).

---

## 5. Method rules learned the hard way

These cost real time. Do not relearn them.

- **N = 20 is not enough for anything.** It missed a real 3.3 % failure mode at
  8×8 and understated the 16×16 delivery error by **42 %**. Rates and error
  distributions need **N ≥ 120**.
- **A single seed will lie to you.** It happened twice: the DATA-patrol change
  looked excellent on seed 1 and was a reliability disaster at N = 120; the
  4-way partition likewise.
- **Never rebuild while a campaign is running.** It silently mixes binaries
  inside one result set.
- **Assert on every scripted source edit.** A `str.replace` that matched nothing
  meant a feature never ran while its results were attributed to it and
  reported. Verify behaviour in the event log, not in the diff.
- **State mechanisms only after measuring them.** Three explanations in this
  project were asserted from a plausible story and all three were wrong
  ("accuracy is sensing-limited", "the centroid wins the tail", "the aiming
  scope causes the error floor").
- **Every published number assumes uniqueness.** Nothing else in the search area
  matches the reference dataset. `--clutterCount` now lets that be violated
  (default 0 = the old regime, byte-identical); when it is, `reportErr_m` is a
  mixture of "right object, ~14 m" and "wrong object, ~250 m". Measured at
  M = 2, N = 120: the pooled median *flips* between similarity 0.70 and 0.85
  (25 m → 162 m) while the conditional error never moves (14.5 → 13.9 m). Quote
  `fixOnVictim` and the conditional error, never the pooled quantiles.
  `assert_one_clutter` refuses to aggregate across regimes.
- **Cost metrics are intention-to-treat.** Gating them on victim-served is
  survivorship bias worth 0.4–2.8 %, always in our favour.

---

## 6. How to reproduce anything

```bash
cd /home/user/ns3-dev
BIN=build/src/uav-sar/examples/ns3.46-scenario-sar-optimized
REAL="--senseSigma=0.10 --gpsSigma=5 --victimOnNode=0"    # realistic operating point

# one run
$BIN --seed=1 --scheme={proposed|closed-loop|tsp-mc|nocoop|pure-uav} \
     --gridSize=16 $REAL --simTime=1200 --outputDir=OUT

# campaigns (PYTHONPATH must point at uav-sar/tools)
campaign_stats.py       OUT 120 --grid=16 $REAL   # head-to-head + paired tests
campaign_reliability.py OUT 120 16       $REAL    # rates with Wilson CIs + ITT check
campaign_noise.py       OUT  20 16                # sensing-realism sweep
campaign_error_budget.py OUT 60 16                # what actually sets the error
campaign_ablation_elect.py / _aim.py              # B2 and W1 ablations
campaign_stats.py --selftest                      # validates the statistics code

# replay viewer (any number of runs, one build only)
make_viewer.py out.html "label=RUNDIR" ...
```

Key flags: `--adaptiveWindow --dataPatrol --deliverDwell --aimArgmax
--electSuppress --allHome --codedMulticast --mcRedundancy --mcRadius`.
Each has an ablation setting; every default was chosen from a measurement
recorded in `sar-params.h` or `sar-config.h` comments.

---

## 7. Document map

| file | what it is |
|---|---|
| `STATUS.md` | this file — current truth, start here |
| `SIM-SPEC-vi.md` | Vietnamese: **the agreed simulation spec** — world, two-tier sensing, fleet, the two cooperation planes, the 3x3 arm matrix, operating points, statistics, and the staged implementation order with a verification gate per stage. Decisions only; open questions listed in one place. **This file wins over the discussion log.** |
| `EXPERIMENT-DESIGN-vi.md` | Vietnamese: the discussion log behind the spec — includes rejected ideas and the reasoning. Read for *why*, not for *what to build* |
| `RESULTS-honest.md` | measured results; see §2 for what is stale |
| `AUDIT-SYNTHESIS.md` | audit round 1 (four reviewers), all Tier-0 closed |
| `AUDIT-2026-08-round2.md` | audit round 2, eleven findings A1–A11 |
| `AUDIT-2026-08.md` | earliest correctness audit |
| `PROBLEM-FORMULATION-vi.md` | Vietnamese: the eight optimization problems stated separately (P1–P8), each with who solves it and whether it is open |
| `RESULTS-ambiguity-vi.md` | Vietnamese: N=120 results once ambiguity is resolvable — 0/120 wrong-object closures, ambiguity nearly free, resolution also SAVES packets, and the +1 DATA UAV trade |
| `FIXED-WING-FAST-vi.md` | Vietnamese: what changes if the FAST team becomes fixed-wing — Dubins re-routing is fine, but the 30 s relay hold breaks at 20 m/s, the energy curve is the wrong one, and the HANDOFF retry window is shorter than an orbit period |
| `RELATED-WORK-ambiguity.md` | Vietnamese: who has already studied identity ambiguity — classical search-among-false-contacts theory, visually-identical-target association, clothes-changing re-ID — and what still has to be checked before claiming a gap |
| `FALSE-POSITIVE-RIGOR-vi.md` | Vietnamese: the uniqueness assumption every result rests on, why identity ambiguity is not sensor noise, the identifiability ceiling, and the fact that `reportErr_m` becomes a two-mode mixture once it is violated |
| `PROBLEM-MULTI-CANDIDATE-vi.md` | Vietnamese: what happens once detector false positives create K > 1 request points — routing/scheduling/partitioning problems P9–P14, the measurement showing the current field never reaches that regime, and the testable hypothesis that this is where cooperation would finally pay |
| `PROBLEM-FORMULATION.md` | the optimization problem this system solves, the tractable restriction each scheme solves, and the rendezvous constraint (R) that the experiments found to be binding |
| `DESIGN.md` | round-1 design note — **predates everything above**, does not describe the baselines or any current mechanism |
| `RESULTS.md` | **VOID**, kept only as a record |
| `visualize/replay-40x40.html` | replay, 4 schemes, generated by `tools/make_viewer.py` |
