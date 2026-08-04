# Audit round 2 — before adding baselines, before submitting

Scope: everything that changed since `AUDIT-SYNTHESIS.md` closed Tier 0 — the
B3 fix delivery, the B2 election, the yield-return fix, the sensing-noise /
GPS / continuous-victim model, and the switch to argmax. Method: re-derive the
claims from the data rather than re-reading the prose. Every finding below was
*measured*, and the measurement is named.

**Headline of this round: the study's numbers were under-powered, and N = 20 was
wrong in both directions.** Nothing here overturns the central result, but two
published figures move by more than 40 %.

---

## A1 — Under-powered rates and medians (SERIOUS, corrected)

`tools/campaign_reliability.py OUT 120 {8,16}`

Every rate and every delivery-error median in the previous revision came from
N = 20. At N = 120:

| quantity | N = 20 | **N = 120** | Wilson 95 % (N=120) |
|---|---:|---:|---|
| 8×8 mission complete | 100 % | **96.7 %** | [91.7, 98.7] |
| 8×8 victim served | 90 % | **86.7 %** | [79.4, 91.6] |
| 8×8 BS fix error | 18.0 m | **21.5 m** | p90 36.8 m |
| 16×16 victim served | 75 % | **82.5 %** | [74.7, 88.3] |
| 16×16 BS fix error | 15.6 m | **22.2 m** | p90 40.2 m |

Three things this changes:

1. **N = 20 reported 100 % mission completion at 8×8 and there is a real 3.3 %
   failure mode.** Twenty seeds simply never hit it. Any claim of "always
   completes" was an artifact of the sample size.
2. **The 16×16 delivery error was understated by 42 %** (15.6 → 22.2 m). This is
   the localization claim, i.e. the thing the scheme exists to do, and it was
   the worst-estimated number in the study.
3. Once properly powered, the fix error is **~21–22 m at both scales**. The
   apparent "accuracy improves with density" reading from N = 20 was noise.

**Rule adopted:** rates and error distributions require N ≥ 120. Medians of
low-variance cost metrics may stay lower, but must say so.

## A2 — Survivorship bias in the inclusion rule (MODERATE, real but small)

Distributions were gated on *victim served*. But `t_report`, `energy` and
`packets` are defined whenever the **mission** completes — a different and much
more frequent event — so gating them on victim-served drops runs for a reason
unrelated to the metric, and the dropped runs are systematically the awkward
ones.

Measured (N = 120, gated vs intention-to-treat):

| | 8×8 | 16×16 |
|---|---:|---:|
| t_report | −0.8 % | −0.4 % |
| energy | −1.1 % | −1.6 % |
| packets | −0.5 % | **−2.8 %** |

Every delta favours the proposed scheme, which is exactly the signature of
selection on the outcome. The magnitude (≤ 2.8 %) does not threaten a 2× result,
but the fix is free: **report cost metrics intention-to-treat** and keep the
victim-served gate only for `t_victim` and the delivery error, where the metric
genuinely does not exist otherwise.

## A3 — W7 is only half-done; do not claim random deployment (SCOPE)

`--victimOnNode=0` displaces the victim uniformly in [−s/2, +s/2]². That square
**is** the Voronoi cell of the lattice point, so:

- the nearest node is *always* the original node — verified, `targetNodeId`
  differs in 0/20 seeds between the two operating points;
- the victim is therefore **always within s/√2 = 14.1 m of a sensor** by
  construction (measured: median 9.2 m, max 11.9 m over 20 runs).

So the estimator's free lunch is gone (the clue field is genuinely off-lattice),
but the *deployment* is still a perfect lattice with no density variation and no
coverage holes. **A PPP deployment where the victim can fall in a gap is still
open**, and would attack the victim-served rate far harder than this does. The
docs must say "victim off-lattice", not "random deployment".

## A9 — The ~20 m error floor was misexplained TWICE (SERIOUS, now resolved)

`tools/campaign_error_budget.py` — decomposing the fix error at 16×16, N = 60:

| detector σ | GPS σ | victim | median | p90 |
|---:|---:|---|---:|---:|
| 0.00 | 0 m | on node (fully ideal) | 20.0 m | 28.3 m |
| 0.00 | 0 m | continuous | 18.1 m | 30.3 m |
| 0.00 | 5 m | continuous | 19.3 m | 32.4 m |
| 0.10 | 0 m | continuous | 18.9 m | 36.1 m |
| 0.10 | 5 m | continuous (realistic) | 20.7 m | 38.7 m |

**The median is ~18–21 m in every configuration, including the perfect one.**
Noise moves the p90 (28 → 39 m) and almost nothing else. Two explanations
previously given in this project are therefore wrong:

- *"Accuracy is sensing-limited"* (earlier `RESULTS-honest.md`) — it is not. A
  noise-free detector with exact GPS lands in the same place.
- *"The aiming scope is capped at one cell"* (A4, this round) — fixing it moved
  the median by 0.8 m.

The actual cause is **decision time**. A leader aims at the strongest reporter
*it has heard from*, and a node reports only once the FAST sweep has delivered
it enough cues to cross the cooperation threshold. Firing early means aiming
from a sparse, biased sample of the evidence field. Sweeping the window at the
realistic operating point (16×16, N = 60) confirms it and nothing else does:

| `--minObserve` | fix median | p90 | ≤ 20 m | t_report | victim served | energy |
|---:|---:|---:|---:|---:|---:|---:|
| 0–20 (default) | 20.2 m | 38.7 m | 50 % | 92.3 s | 87 % | 57.2 kJ |
| 30 | 17.2 m | 35.5 m | 57 % | 99.7 s | 88 % | 60.5 kJ |
| **45** | **14.6 m** | **25.9 m** | **72 %** | 103.7 s | 100 % | 67.8 kJ |
| 60 | 14.5 m | 27.3 m | 73 % | 114.8 s | 95 % | 77.2 kJ |

Re-measured at **N = 120** (because N = 60 was optimistic, exactly as A1 warns):
`minObserve = 45` gives **15.9 m** median / 29.9 m p90 / **95.8 %** victim served
/ 103.6 s / 67.8 kJ — against the default's 21.4 m / 36.8 m / 90.0 % / 92.8 s /
57.2 kJ.

**This is the single most consequential finding of the audit.** The default
(`minObserve = 20`) sits at a bad operating point. Moving to 45 s buys −26 %
error, −19 % p90 and +5.8 pp reliability for +12 % mission time and +19 %
energy. Against `tsp-mc × 4` (184.9 s / 120.6 kJ) that is still **1.79× faster
and 1.78× less energy**, *with* a 15.9 m position the baseline cannot produce at
any setting.

The paper should present this as an **operating-point curve** (audit W8's
request) rather than pick one number: the proposed scheme dominates the baseline
along the whole curve, and the curve states what the extra time buys.

## A10 — The observation window is NOT a free knob (SERIOUS, unfixed)

At 8×8 the same sweep **fails completely** at `minObserve` ≥ 45: zero fixes in
60/60 seeds. Diagnosed on seed 1 — the summon fires at 45.1 s, but the FAST UAVs
finished their sweep and were already flying home; their reports reach the BS at
46.5 s and 52.5 s. There is no `divert` and no `deliver_start` at all, because
the A2A relay that carries the SUMMON to the DATA team no longer has anyone
airborne to carry it.

So the usable window is **bounded above by the FAST sweep duration**, which
scales with area: 45 s works at 16×16 (sweep ~90 s) and destroys 8×8 (sweep
~40 s). A wall-clock constant is therefore the wrong parameterization — it is
a hidden function of grid size, and a reviewer who runs the released code at a
third grid size will get a silent zero. **The window must be expressed relative
to sweep completion** (or, better, made adaptive: fire when the leader's own
evidence stops growing, or after k reports). Not fixed in this round; it is a
design change, not a defect fix.

## A11 — RCLAIM suppression is racy at a hard window edge (MODERATE, unfixed)

The same seed shows **two** `summon_start` events, 0.1 s apart (45.1 and 45.2) —
despite B2's flood. The stand-down cannot outrun a 0.1 s gap over a multi-hop
flood. The evidence-ordered backoff normally desynchronizes leaders, but
clamping every cell to the same window edge re-synchronizes them, which is the
M4/S5 failure mode returning at large `minObserve`. B2's measured "0/20 duplicate
regions" was obtained at `minObserve = 20` and **does not generalize to larger
windows**; the claim must be scoped to the window it was measured at.

## A4 — The aiming scope is one cell (DESIGN LIMIT, FIXED — but not for the reason expected)

*Update after measuring:* implemented (SHARE now carries each cell's peak
reporter and its evidence). It did **not** move the error floor (see A9), but it
substantially improved **reliability**: victim served at 16×16 went 82.5 % →
**90.0 %** (N = 120), for +4.6 % packets. Kept on those grounds. Original
finding below.

`Elect()` under argmax searches `m_cellEvidence`, which holds **only the winning
leader's own cell members**. Neighbouring cells reach the leader through SHARE,
but `FloodShare()` sends `m_cellCx/m_cellCy` — the *cell centre*, not the
neighbour's strongest node. So a leader can know "cell 7 is hot" but never
"node 112 at (x, y) is the hottest thing in cell 7".

Consequence: the fix is structurally bounded by *the best node inside a single
80 m-radius cell*, which is a plausible explanation for the ~21 m floor that no
amount of estimator work will move. The cheap fix — carry the cell's argmax node
position in SHARE instead of the cell centre — is a design change, not a bug
fix, and is deliberately **not** made in an audit round.

## A5 — The centroid ablation is run under mixed geometry (MINOR)

Under `--aimArgmax=0`, member positions carry the GPS bias (from RPT) but
neighbour terms use true cell centres (from SHARE). The ablation arm therefore
mixes noised and un-noised geometry. It does not affect the default (argmax
never reads the neighbour terms), but it makes the centroid look slightly
*better* than it should in the noise sweep — which only strengthens the
conclusion that argmax wins, so the reported decision stands.

## A6 — A dormant oracle remains reachable (MINOR)

`if (m_stopOnComplete && m_isTarget) Simulator::Stop(...)` is the old
ground-truth stop. It is dead under the default (`--allHome=1` forces
`SetStopOnComplete(false)`), but `--allHome=0` revives it. Every other use of
`m_isTarget` is metrics-only. Either delete it or document it as an
ablation-only path; leaving an oracle one flag away from live is how the
original bypass got published.

## A7 — Seed confounds victim position with channel (NOTED, by design)

One seed fixes the victim position *and* the channel realisation. The paired
design stays valid (both arms see the same victim and the same channel), but
variance cannot be attributed between the two. Decoupling them needs a second
RNG stream and would let the study say which source dominates the 20 m spread.

## A8 — Fleet asymmetry runs *against* the proposed scheme (NOTED, state it)

`proposed` splits 4 airframes into 2 FAST + 2 DATA, so only **two** can deliver
the full dataset; `tsp-mc × 4` has four delivering UAVs. All four fly and all
four count toward energy and the all-home completion rule. This is conservative
— but a reviewer who spots it unaided will wonder what else is unstated, so it
belongs in the paper.

---

## Verified clean

- **Failures are genuine, not censoring.** Max `t_victim` is 70.9 s against a
  1200 s horizon at 16×16, 48.4 s against 300 s at 8×8. No truncation artifact.
- **Baselines are exactly invariant to the realism knobs.** `tsp-mc-x4`,
  `tsp-mc-x1` and `nocoop` produce byte-identical time/energy/packets and
  identical `targetNodeId` and `t_victim` at both operating points, across all
  20 seeds. This was asserted last round; it is now checked.
- **No live oracle in the default path.** `m_isTarget` drives only metrics; the
  fix reaching the BS is decoded from a REPORT packet; delivery coordinates are
  radio-reported GPS-biased node positions.
- **The statistics code self-tests.** `campaign_stats.py --selftest` passes
  against hand-computed Wilcoxon, Cliff's δ, erfc-based p, and nearest-rank p90.

## Status and what must happen before submission

**Done in this round:** A4 (cross-cell aiming implemented, +7.5 pp reliability),
A5 (SHARE geometry now consistently GPS-biased), A6 (dormant oracle deleted),
A9 (error budget decomposed; two prior explanations retracted).

**Blocking, before any new baseline:**

1. **A10 — reparameterize the observation window** relative to sweep completion,
   or make it adaptive. Right now the released code silently produces zero
   localizations at 8×8 with `minObserve ≥ 45`. This is the one finding that
   would embarrass the work if a reviewer ran it.
2. **A1 — re-run the head-to-head at N ≥ 120** and restate every ratio. Two
   published figures moved by >40 % between N = 20 and N = 120; the cost ratios
   have not yet been re-derived at the corrected sample size.
3. **A2 — report cost metrics intention-to-treat.** Mechanical, ≤ 2.8 % effect.
4. **A11 — scope B2's "0/20 duplicate regions" to `minObserve = 20`**, or fix
   the race, before claiming the election is sound in general.
5. **A3 — fix the W7 language.** Say "victim off-lattice", never "random
   deployment".

**Then, and only then, add baselines.** Every new arm must be run at N ≥ 120 at
the chosen operating point; adding one to an under-powered comparison multiplies
the cost of re-powering it later.

## Meta-finding: two process failures worth recording

- **A rebuild during two in-flight campaigns** silently mixed binaries within
  one campaign. Caught, and the outputs were deleted rather than reported — but
  only because the timing happened to be noticed. Campaign scripts should record
  the binary's hash in `config.txt` and refuse to aggregate across hashes.
- **Three separate claims in this project were stated before being measured**
  ("accuracy is sensing-limited", "the centroid wins the tail at every operating
  point", "the aiming scope causes the error floor"). All three were wrong, and
  all three were caught only by running the measurement afterwards. The pattern
  is stating a mechanism from a plausible story rather than from data.
