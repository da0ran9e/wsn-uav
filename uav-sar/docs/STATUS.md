# UAV-SAR — project status and handover

**Read this first in any new session.** It is the single place that says what is
true right now, what is stale, and what to do next. Everything else in
`docs/` is either a historical audit record or a results file that this document
tells you how far to trust.

- Branch: `claude/document-review-xslwgg`
- Last commit at time of writing: `f17c081`
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

| source | status |
|---|---|
| `RESULTS-honest.md` §W4 (closed-loop) | **current** |
| `RESULTS-honest.md` 16×16 head-to-head | **current** — re-verified after the re-announce change; 104.1 s vs 103.9 s, unchanged |
| `RESULTS-honest.md` 8×8 head-to-head | **STALE** — not re-run since `b4ac588`. Re-run before quoting. |
| all baseline arms (`tsp-mc`, `nocoop`, `pure-uav`) | **current** — they never touch the cooperative plane, so recent edits cannot move them (verified byte-identical across the realism knobs) |
| anything measured at N = 20 | **VOID** — see §5 |
| `RESULTS.md` | **VOID**, banner at top |
| `docs/visualize/replay-40x40.html` | current, one build, seed 1 |

---

## 3. Where the scheme stands mechanically

Recent design changes, all measured:

- **Cue-triggered SUMMON re-announce** (`b4ac588`) — *this is the one that
  mattered.* An elected leader re-announces whenever it hears a CUE chunk,
  because that chunk proves a UAV is within one hop right now. Fixed 40×40
  outright: victim served 0/5 → 5/5.
- **Adaptive observation window + bounded relay hold** (A10) — summon when the
  leader's own evidence stops growing; a FAST UAV holds station 30 s after its
  sweep so a relay stays airborne.
- **`--deliverDwell`** — reliability/cost knob. 40 s takes 16×16 victim-served
  90.0 → 96.7 % for +10 % time; at 8×8 the same setting *inverts* the comparison
  (0.86× time). Density-dependent, default 20 s.
- **`--dataPatrol`** — DATA UAVs patrol and cue while waiting. **Default off:**
  measured net-negative at 16×16 (+14 % packets, −2.5 pp reliability) and
  marginal at 40×40. The parked-UAV problem it was meant to solve was actually
  solved by the re-announce.

Known-bad, do not retry without a new idea:

- **Splitting cue coverage across all 4 airframes**: victim served 90.0 → 42.5 %
  at N = 120, localization firing in only 70 % of runs. A DATA UAV diverts,
  yields or goes home mid-patrol, so any band it owns is left half-cued.
  Coverage must not depend on UAVs that can be pulled away. *But note:* the same
  change made 40×40 much faster (224 s vs 396 s). That tension is unresolved and
  is a real design question, not a bug.
- **Retarget-on-no-CONFIRM as a reliability fix**: neutral at best. The failures
  are delivery-at-range, not wrong aim.

---

## 4. Open problems, ranked

1. **Closed-loop still beats `proposed` on cost.** Either find where cooperation
   genuinely pays (the p90 tail is the live lead) and build the paper on that, or
   reduce the cooperative plane's packet cost. 0/120 paired wins on packets is
   the number to attack.
2. **CONFIRM closure is wrong in principle.** *Any* node holding the dataset may
   confirm, so the loop can close on a bystander under the drop point while the
   victim, further out, never finishes. `--deliverDwell` masks the symptom.
   Proper fix: CONFIRM carries the confirming node's evidence; closure requires
   the aim target or its equal.
3. **W7 is half done — never call it random deployment.** `--victimOnNode=0`
   displaces the victim inside the Voronoi cell, so the nearest node never
   changes and the victim is always ≤ 14.1 m from a sensor. A PPP deployment with
   coverage holes would attack the reliability numbers much harder.
4. **W2 — no ML/NLS estimator, no CRLB.** Two crude heuristics (argmax vs
   centroid) tie, which is the signature of both sitting far from the bound.
5. **The build-provenance guard is weaker than advertised.** `config.txt`'s
   `build=` uses `__DATE__/__TIME__` compiled into `sar-metrics.cc`, which only
   updates when *that file* recompiles — so it will **not** catch a mixed-binary
   campaign where only another translation unit changed. Fix: stamp
   `/proc/self/exe` mtime+size at runtime.
6. **The clue field cannot produce more than one candidate request point.**
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
| `RESULTS-honest.md` | measured results; see §2 for what is stale |
| `AUDIT-SYNTHESIS.md` | audit round 1 (four reviewers), all Tier-0 closed |
| `AUDIT-2026-08-round2.md` | audit round 2, eleven findings A1–A11 |
| `AUDIT-2026-08.md` | earliest correctness audit |
| `PROBLEM-FORMULATION-vi.md` | Vietnamese: the eight optimization problems stated separately (P1–P8), each with who solves it and whether it is open |
| `FALSE-POSITIVE-RIGOR-vi.md` | Vietnamese: the uniqueness assumption every result rests on, why identity ambiguity is not sensor noise, the identifiability ceiling, and the fact that `reportErr_m` becomes a two-mode mixture once it is violated |
| `PROBLEM-MULTI-CANDIDATE-vi.md` | Vietnamese: what happens once detector false positives create K > 1 request points — routing/scheduling/partitioning problems P9–P14, the measurement showing the current field never reaches that regime, and the testable hypothesis that this is where cooperation would finally pay |
| `PROBLEM-FORMULATION.md` | the optimization problem this system solves, the tractable restriction each scheme solves, and the rendezvous constraint (R) that the experiments found to be binding |
| `DESIGN.md` | round-1 design note — **predates everything above**, does not describe the baselines or any current mechanism |
| `RESULTS.md` | **VOID**, kept only as a record |
| `visualize/replay-40x40.html` | replay, 4 schemes, generated by `tools/make_viewer.py` |
