# Audit synthesis — four independent reviewers (2026-08)

Four reviewers audited this project independently: **correctness/oracles**,
**experimental fairness**, **statistical rigour**, and **publication readiness**.
They did not see each other's reports (the last three were told only the first
one's findings, to avoid duplicated work).

Detail per reviewer is in `AUDIT-2026-08.md` (correctness) and in this file.
**Bottom line: every reviewer independently reached "not publishable as
written", and three of them independently converged on the same remedy.**

---

## 1. The convergent finding — the paper's thesis is a scaling law, and 8×8 is the worst place to claim it

Three reviewers arrived at this from different directions:

| Reviewer | Route | Result at 8×8 | Result at scale |
|---|---|---|---|
| Publication | ran a scale sweep the study never contained | victim-service tie (ratio 1.02–1.11×) | 16×16: **1.85×**, packets 2 634 vs 10 657, p = 2.4e-4 |
| Statistics | re-ran head-to-head at larger grids | ratio 1.74× (but see §2) | gap **holds and widens** at 12×12 |
| Fairness | re-levelled every asymmetry, then swept scale | **1.01×** — the advantage vanishes | 16×16 vs *maximally charitable* baseline: **1.46×** |

**Blind coverage cost scales with area; evidence-directed delivery cost scales
with (time-to-localize + transit).** That is a real, defensible, measurable
thesis. The study was conducted at the one configuration where the effect cannot
appear, which is why an honest author was forced to write "matches the
carpet-dump baseline".

Symmetric ratios measured by the fairness reviewer:
`8×8 @ 20 m = 1.01×` · `8×8 @ 30 m = 1.20×` · `16×16 @ 20 m = 2.13×`.

**But the scaling story has a cost that must be published with it:** the
statistics reviewer measured `proposed`'s *reliability* degrading with scale
(victim service 95 % → 80 % at 12×12; mission completion 100 % → 95 %), while
`tsp-mc` degrades less. Faster at scale, less reliable at scale. Reporting only
the first half would repeat exactly the over-claiming this project has been
trying to eliminate.

---

## 2. The headline speedup is manufactured by two asymmetries (fairness reviewer, BLOCKING)

### F1 — The proposed scheme's critical path flies 1.67× faster
`kFastSpeedMps = 25.0` vs `kDataSpeedMps = 15.0` (`sar-params.h:59-60`, both
`[Design]`, both absent from `PARAMETERS.md`). `sar-config.cc:168` gives 25 m/s
to proposed's FAST UAVs; `:149` gives 15 m/s to **every** baseline UAV.

The narrative justification (`DESIGN.md §3`: "FAST carries small fragments, flies
fast") **is not implemented**: `EnergyPowerW()` has no mass term and payload is
bytes in a `std::vector`. The indefensible case: the REPORT is the *identical
5-byte packet* in both schemes; proposed's courier flies it home at 25 m/s,
tsp-mc's at 15 m/s over a median 395 m empty return — **11.2 s of critical path
awarded purely by scheme membership**. Zeng'18's whole contribution is
completion-time minimization with speed as a decision variable; capping the
baseline at 0.6·V_max is the first thing its authors would object to.

### F2 — Asymmetric completion rule: 1-of-4 home vs 4-of-4
`sar-config.cc:93`: `SetExpectedReports(tspMc ? numUav : 1)`. At the instant
proposed's mission is declared complete (seed 1, 68.3 s), **three of its four
UAVs are still airborne in the field** and never return at all. tsp-mc must land
all four (114.9 s). The fly-home requirement is itself author-added: Zeng'18's
objective completes at a median **81.6 s**, not 114.9 s.

### F3 — Correcting both erases the result
```
ratio tsp-mc / proposed:   as published 1.74×   →   symmetric rule + equal speed 1.01×
```
The `p < 1e-16` is real; **it is measuring the two asymmetries, not the schemes.**

### F4 — The baseline was given uncoded repetition instead of coded multicast
Zeng'18 assumes rateless/network-coded multicast (any ≈1.05× file-worth of
symbols suffices). The implementation replays identical chunk indices, so a GT
must see **all 382 distinct indices** — demanding per-packet success `q ≥ 0.878`
where the coded scheme needs `q ≥ 0.35`. Verified as repetition rather than
collisions: a single-UAV run (no contention) needs the same R.

A faithful coded baseline reaches the same coverage at **R ≈ 1.5**, halving every
hover. This invalidates the "R = 3 is the stingiest setting that meets their
goal" defence — the sweep measured what *this implementation* needs, not what
*their scheme* needs.

**Maximally charitable baseline** (rateless R = 1.5 + same 25 m/s + all-4-home):
```
tsp-mc ×4  72.4 s      proposed ×4 (all home)  91.5 s
→ the baseline WINS by 1.26× at the configuration used for the headline.
```

### F5 — The energy claim reverses sign
Re-integrated with the authors' own `EnergyPowerW` to the one milestone every arm
reaches (victim holds full dataset), airborne UAVs still billed:

| scheme | E @ common milestone | E @ own stop (published) |
|---|---:|---:|
| proposed | **28.4 kJ** | 44.7 kJ |
| tsp-mc | **25.7 kJ** | 65.7 kJ |
| nocoop | 25.8 kJ | 27.2 kJ |

The published 1.5× advantage becomes a **1.10× disadvantage**. Must be
**withdrawn, not caveated**.

### Other fairness findings
- **M1** The headline metric is 0 %-by-construction for two of four arms
  (`nocoop`/`pure-uav` never get `SetReportAtEnd`). The one metric where the
  proposed scheme is unbeatable was promoted to headline; the metric all four
  reach shows no significant difference.
- **M2** "≈5× fewer packets" normalizes away: proposed serves 14/64 GTs, tsp-mc
  62/64 → **139 vs 154 packets per GT served, a 10 % difference**.
- **M3** `nocoop`'s published totals are **39 %-of-mission snapshots** (oracle
  stop fires when it has served 25/64 GTs).
- **M4** BS sits 283 m outside a 140×140 m field ⇒ tsp-mc flies **92.6 % commute,
  7.4 % actual VBS tour**. The trajectory design under test is 7 % of the flight.
- **M5** Asymmetric realism budget: the input only `proposed` consumes (clue
  field) is noise-free with exact GPS; the input both consume (radio) carries
  four impairments.
- **M7** VBS centres were restricted to GT positions; free placement needs 8
  disks where the implementation needs 12 at r = 40/60 m — so the radius sweep's
  "50 m is tied-best for them" conclusion is unsupported.
- **M9** Parameters were tuned on the reported seed set (no held-out split
  anywhere). **Partly exonerated**: held-out seeds 500–529 reproduce within
  noise, and `minObserve = 20` is *not* latency-optimal — the authors gave up
  1.4 s for accuracy, which is evidence against deliberate headline-tuning.

---

## 3. Statistical findings (statistics reviewer)

**Critical**
- **S1** The headline table's entire `proposed` column is **stale — 6/6 cells
  wrong**, contradicted by the same file 55 lines later and by its own documented
  reproduce command. Baseline columns are exact.
- **S2** `pure-uav`'s "97 %" is `--simTime=200` **truncation**, not failure (seed
  15 is served at 205.1 s). Scripts use horizons from 200 s to 900 s under one
  metric name.
- **S3** "Density doesn't limit accuracy" is **selection on the outcome
  variable**: the 3 seeds that fail at 30 m are the 73rd/77th/90th percentiles of
  difficulty. At 40 m the survivor median is 1.5 m — sparser would read as 10×
  *more* accurate.

**Major**
- **S4** The "resolution law" quotes 3 of 5 swept points — the 3 that look
  proportional. All five give an **affine** fit `err ≈ 6.2 + 0.115·decay`
  (r² = 0.82) with a floor the "law" denies, and 90 m is *lower* than 60 m.
- **S5** `minObserve` 0 and 10 are **byte-identical in 30/30 seeds**; the knob is
  a step function with one active step, and `t_localize` equals the knob exactly
  in 17/30 runs. "Localize 100 % @ 20 s" reports the setting.
- **S6** N = 30 gives **58 % power** and a ±3.9 m median CI — wider than every
  delivery-error difference the document draws a conclusion from. Also **33 % of
  delivery-error variance is victim position**, not channel: seeds are not
  replicates of a fixed scenario.
- **S7** Baseline latencies are **verifiably multimodal** (bimodality coefficient
  0.74–0.78); `pure-uav`'s 68.5 s median sits in a low-density valley with 37 %
  of runs > 90 s. Conversely `proposed` is unimodal and 4–12× tighter — a real
  advantage (predictability) that medians also hide.
- **S8** The documented reproduce command emits the **retracted** `summon_start`
  metric under the label "localize error" (40.0 m vs the table's 15.8 m).
- **S9** `campaign_stats.py` hard-codes `spacing = 20.0` → **11× wrong** delivery
  error at any other spacing.
- **S12** `gt_done` is emitted only when `!m_cooperative`, so **GT coverage is
  structurally unmeasurable for `proposed`** — the fairness sweep built on it can
  only score one arm.
- **S13** The radius sweep's 70 m and 80 m rows are the **same experiment**
  (byte-identical, 30/30); and the doc calls 70 m both "breaks the multicast
  guarantee" and "coverage-preserving".

**Tooling verdict — the statistics tool itself is sound.** Wilson matches scipy
to ≤0.0005 pp, bootstrap coverage is 95.0 %, Mann-Whitney U matches exactly
including ties. Two real bugs: p-value **underflows to 0** above |z| ≈ 8.29 (the
reported "p < 1e-16" is a print floor; true value **3.1e-34** — fix with
`math.erfc`), and S9's spacing. Also the design is **paired** (same seed ⇒ same
channel) but an unpaired test was used: Wilcoxon signed-rank gives
**p = 3.9e-18 with 100/100 pairs favouring proposed**, plus effect sizes the
study never reports (Cliff's δ = −0.33 vs nocoop, i.e. small-to-medium).

**What replicated:** the two tsp-mc fairness sweeps reproduce **45 of 45 cells to
the last digit** — "better reproducibility than most published network-simulation
work".

---

## 4. Publication findings (publication reviewer)

- **W1 (rejection-grade)** The localization contribution **loses to a one-line
  rule**. Aiming at the single highest-evidence reporting node — a strict subset
  of the same bytes — gives **median 0.0 m, 11/15 exact hits**, versus the
  weighted centroid's 13.6 m. Cause is structural: the clue field is a noise-free
  isotropic function of true distance and the victim is **always co-located with
  a sensor node**, so argmax *is* the victim by construction. The "±16 m" is
  smoothing bias injected into a problem whose exact answer was already in the
  leader's memory.
- **W2 (rejection-grade)** The evidence²-weighted centroid **is** Weighted
  Centroid Localization (Blumenthal et al., WISP 2007) with evidence substituted
  for RSSI, presented as new. The underlying problem has known ML estimators and
  a closed-form CRLB (Sheng & Hu, IEEE TSP 2005). The paper needs an ML/NLS
  baseline and a CRLB, then a claim of the form "attains X % of the centralized
  bound using N packets".
- **W3** No detector operating characteristic. The cue-independence assumption
  (`C = 1 − Π(1−p_i)`) is unjustified for cues from one image. Background false
  positives are capped at 0.18 < the 0.30 cooperation threshold, so **false
  positives are structurally incapable of affecting any decision** — the scheme
  has never been tested against a mistaken sensor.
- **W4** All baselines are **open-loop**; the comparison demonstrates that
  feedback beats no feedback, a known result, and does not isolate this design's
  choices. Needs a **closed-loop non-cooperative** baseline (individual beaconing,
  no cell plane) and a **genie upper bound**.
- **W5** The SAR literature is absent, most damagingly **SARDO** (IEEE TMC 2021),
  a field-evaluated drone victim-localization system. Needs explicit
  differentiation (they need no infrastructure but need a powered phone; this
  needs a surveyed WSN but works for an unconscious victim and delivers data).
- **W7** Lattice + victim-on-node is a **hidden prior favouring a centroid
  estimator**. Random deployment with a continuous victim position is mandatory.
  Also `libenergy` is linked and never used — no WSN lifetime analysis despite
  citing PECEE for lifetime maximization.

**Recommendation: REJECT as-is.** Path: Tier-0 fixes (4–6 weeks) → Ad Hoc
Networks / Computer Networks; + Tier-1 (3–4 months) → IEEE IoT-J, with TWC
arguable if localization is rebuilt around an estimator with a bound and the
scaling law gets analytical treatment.

---

## 5. Consolidated verdict

**What is real and survived all four audits**
- The simulation substrate: no residual oracle in the sensing→localization chain,
  every cooperative message a real radio packet, correct seeding, packets within
  the PSDU, no flood loops or deadlocks.
- The connectivity threshold (cooperation collapses when spacing exceeds the
  derived G2G range) — independently reproduced twice.
- The scaling behaviour — independently reproduced by three reviewers, and it
  **survives even a maximally charitable baseline at 16×16 (1.46×)**.
- Reproducibility of the baseline-fairness sweeps (45/45 cells exact).
- The statistics tooling (two one-line bugs aside).

**What must be withdrawn or rebuilt**
1. The energy claim — **reverses sign** at a common milestone (F5).
2. The headline speedup at 8×8 — **1.74× → 1.01×** under symmetric rules (F3),
   and the baseline *wins* if given the coding its source paper specifies (F4).
3. The localization contribution — **loses to argmax** (W1) and is WCL under
   another name (W2).
4. "Localize @ 20 s" — reports the knob (S5/M4).
5. The headline table — **stale in every proposed-side cell** (S1).
6. "≈5× fewer packets" — **10 %** per GT served (M2).

**The honest paper that remains:** an evidence-directed delivery architecture
whose mission cost is invariant to search-area size, evaluated against
blind-coverage schemes whose cost is not, with the crossover characterised — at
16×16 and above, under symmetric completion rules, equal cruise speed, a coded
baseline, and with the reliability cost of scale reported alongside the speed
benefit.

## 6. Fix order (consolidated across all four audits)

**Tier 0 — nothing is publishable until these are done** — *all closed; see
`RESULTS-honest.md` for the regenerated numbers.*
1. ✅ Equalize cruise speed across schemes; expose `--fastSpeed/--dataSpeed` (F1).
   → `kCruiseSpeedMps = 20` for every arm; the two-tier fleet is now a declared
   variable, not a hidden advantage.
2. ✅ One termination rule applied identically to every arm (F2, B1, S2).
   → `--allHome` (default on): every UAV flies home and reports. The baselines'
   ground-truth stop condition is gone.
3. ✅ Give the baseline rateless/coded multicast semantics (F4).
   → `--codedMulticast` (default on). Required R drops 3.0 → 1.1; we run 1.2,
   which the dwell quantization actually realizes as 2.0 passes.
4. ✅ Energy claim withdrawn and re-measured under symmetric rules (F5).
   → It now holds against the 4-UAV baselines and **loses** to `tsp-mc × 1`,
   which is reported as a loss.
5. ✅ Head-to-head regenerated from the current binary (S1).
6. ✅ `fireAt = max(now, minObserve) + backoff` (M4/S5).
7. ✅ Coordinates carried to the BS over the radio; `victimX/Y`, `reportedX/Y`,
   `gridSpacing`, `reportErr_m`, `timeToFixAtBS_s` in `metrics.csv` (B3, S9, W8).
8. ✅ Argmax ablation run and reported (W1) — **and it came back negative**: the
   centroid is statistically indistinguishable from argmax (δ = +0.17 at 8×8,
   −0.03 at 16×16). No estimator claim is made; the contribution is scoped to
   the pipeline that produces a fix at all.
9. ✅ Tool fixes: `math.erfc`, `gridSpacing` plumbed, `summon_start` path deleted
   (S10, S9, S8).
10. ✅ The distributed election now actually suppresses (B2) — moved up from
    Tier 1 because it was a described-but-not-executed mechanism, not a
    presentation issue. RCLAIM floods the stand-down on the SHARE plane;
    summons per run went from several to exactly one.

**Tier 1 — required for a top-tier venue**
10. Move the headline configuration to 16×16; report the scale sweep as the
    primary result, **with the reliability degradation** (§1).
11. Add sensing noise, GPS error, and a detector ROC (M9/W3).
12. Random (PPP) deployment, victim at a continuous position (W7).
13. Closed-loop non-cooperative baseline + genie bound (W4).
14. ML/NLS estimator + CRLB vs sensing noise (W2).
15. Operating-point curve for `alertThreshold × coopThreshold` (W8).
16. N ≥ 100 for all delivery-error claims; decouple victim-position from channel
    variance; report median + IQR + p90 + CDFs (S6, S7).
17. Related work across six areas, SARDO mandatory (W5).
18. ~~Resolve what the distributed election is *for* (B2)~~ — **done**, promoted
    to Tier 0 item 10. What remains here is the *ablation*: quantify what the
    election buys versus letting every alerting cell summon.
