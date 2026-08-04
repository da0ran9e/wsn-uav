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

## A4 — The aiming scope is one cell (DESIGN LIMIT, unfixed)

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

## What must happen before submission

1. Re-report every cost metric intention-to-treat (A2). *(mechanical)*
2. Re-run the head-to-head at N ≥ 60 and restate the ratios (A1). *(running)*
3. Fix the docs' W7 language (A3). *(mechanical)*
4. Decide on A4 — either implement argmax-over-neighbours and re-measure, or
   state the one-cell bound as a known limit of the design.
5. Remove or fence the dormant oracle (A6).
6. Only then add further baselines. Adding a baseline to an under-powered
   comparison multiplies the work of re-powering it later.
