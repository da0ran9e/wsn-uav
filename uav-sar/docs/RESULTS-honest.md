# UAV-SAR — Results (post-audit, re-levelled)

> **Provenance.** Every head-to-head number below comes from **N = 120 seeds on
> a single build**, after two rounds of audit (`AUDIT-SYNTHESIS.md`,
> `AUDIT-2026-08-round2.md`). Numbers in earlier revisions of this file are
> void — in particular anything measured at N = 20, which audit A1 showed to be
> wrong in both directions (it missed a real 3.3 % failure mode at 8×8 and
> understated the 16×16 delivery error by 42 %).
>
> `config.txt` in every run directory records the binary's build stamp, and
> `campaign_common.assert_one_build()` refuses to aggregate a run set that spans
> builds.
>
> **Read "What cooperation actually buys" first.** The closed-loop
> non-cooperative baseline (audit W4) shows the cost advantage comes from
> closing the loop, not from cooperation, and it narrows what this study may
> claim.

## The comparison is now symmetric

Four audits showed the previous headline measured two asymmetries rather than
the schemes. All are removed, and each change makes the comparison **harder for
the proposed scheme or more generous to the baseline**:

| Was | Now |
|---|---|
| proposed's FAST UAVs 25 m/s, every baseline UAV 15 m/s | **one cruise speed, 20 m/s, all schemes** (`--fastSpeed/--dataSpeed` keep the two-tier fleet as a declared variable) |
| proposed's mission ended when 1-of-4 UAVs reported, with 3 still airborne; tsp-mc needed 4-of-4 | **every UAV returns to the BS and reports, all schemes** (`--allHome`) |
| baselines' simulation ended when the ground-truth victim node finished — an oracle that set their energy and packet totals | **no scheme stops on the oracle**; all arms end at the same milestone |
| baseline replayed identical chunk indices (uncoded), needing R=3 | **rateless recovery** per Zeng'18; the baseline meets its own goal (98.8 % of GTs, 100 % of victims) at **R=1.2**, halving every hover |
| `nocoop`/`pure-uav` could never complete the mission (0 % by construction) | they fly home and report too — every arm has a real completion rate (baselines 100 %, proposed 95.0 / 97.5 % at N = 120) |
| `timeToLocalize` reported the `--minObserve` knob | window applied first, evidence-ordered backoff on top |
| the election's stand-down was a one-hop SUMMON that could not reach another leader; 30–40 % of runs formed two competing regions | **RCLAIM floods the stand-down** — 0/20 duplicate regions **at `minObserve = 20`**, at +4–8 % packets (B2; audit A11 shows this does *not* hold at a hard 45 s window edge, where two summons fired 0.1 s apart — faster than a multi-hop flood can suppress) |
| the victim fix existed only in simulator state | **carried to the BS in the REPORT packet** and reported as `reportErr_m` (B3) |

## Operating points

Every head-to-head below is at the **realistic** point — detector σ = 0.10,
GPS σ = 5 m, victim at a continuous position, adaptive observation window. The
idealized configuration (noise-free detector, exact GPS, victim on a sensor)
that earlier revisions reported *as if it were reality* is retained only as an
ablation, in "When to summon" and the noise sweep.

The realism knobs are passed to *every* arm, not just the proposed one. The
blind-coverage baselines ignore the clue field entirely, so their numbers are
byte-identical at both points — verified across all seeds, not assumed. That is
not a shortcut, it is the finding: **sensing realism does not touch the cost
comparison at all. It costs reliability, and it costs accuracy in the tail.**

## Head-to-head — 8×8, 64 sensors, 140×140 m

**N = 120 seeds**, one build, adaptive window, realistic sensing, cost metrics
intention-to-treat. Medians with bootstrap 95 % CI.
`tools/campaign_stats.py OUT 120 --grid=8 --senseSigma=0.10 --gpsSigma=5 --victimOnNode=0`

| scheme | mission | victim | t_report | energy | packets | **fix at BS** |
|---|---:|---:|---:|---:|---:|---:|
| **proposed** × 4 | 95.0 % | 87.5 % | **76.0 s** [74.8, 77.3] | **48.4 kJ** | **2 107** | **13.6 m @ 50.8 s** |
| tsp-mc × 4 (coded, R=1.2) | 100 % | 99.2 % | 81.2 s | 53.1 kJ | 6 134 | — none — |
| tsp-mc × 1 | 100 % | 93.3 % | 146.2 s | **25.1 kJ** | 4 585 | — none — |
| nocoop × 4 | 100 % | 99.2 % | 111.8 s | 73.5 kJ | 12 246 | — none — |
| pure-uav | 100 % | 98.3 % | 309.3 s | 52.7 kJ | 12 225 | — none — |

**At 64 sensors the cost advantage is marginal and must be reported as such.**
Against `tsp-mc × 4`: 1.07× on time and 1.10× on energy, and the paired tests
say the same — 84/114 wins, Cliff's δ = −0.474 (*medium*, not large) on time;
100/120 and δ = −0.667 on energy. Only the packet count is decisive (2.91×,
120/120, δ = −1.00). An earlier revision reported 1.29× with 19/19 wins and
δ = −1.00 at N = 20; **that was sample size, not effect.**

The **fix at BS** column is what the scheme is for, and is measured rather than
asserted: the error of the coordinates the base station decoded out of a REPORT
packet that physically arrived. It lands at **50.8 s — 25 s before** the mission
formally completes, because the fix rides home with the first returning UAV
while the rest of the fleet is still inbound. No baseline produces this column
at any parameter setting.

**Two losses, stated plainly.** `tsp-mc × 1` wins on energy, 25.1 kJ vs 48.4, in
120/120 paired seeds (δ = +1.00) — one UAV on one tour is the minimum-energy way
to blanket a field. And every baseline beats us on victim-served (99.2 % vs
87.5 %).

## Head-to-head — 16×16, 256 sensors, 300×300 m

Same protocol: N = 120, one build, adaptive window, realistic sensing, ITT.

| scheme | mission | victim | t_report | t_victim | energy | packets | **fix at BS** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **proposed** × 4 | 97.5 % | 90.0 % | **113.3 s** [105.5, 116.6] | **68.6 s** (IQR 16.9) | **72.6 kJ** | **3 583** | **14.6 m @ 90.4 s** |
| tsp-mc × 4 (coded, R=1.2) | 100 % | 97.5 % | 184.9 s | 80.9 s (IQR 51.8) | 120.6 kJ | 21 421 | — none — |

## What cooperation actually buys — and what it does not (audit W4)

**This is the most important result in the document, and it contradicts the
thesis the study started with.**

Every other baseline is *open-loop*: it blankets the field and never reacts to
anything. So the large cost advantage over them could equally be explained by
**closing the loop** rather than by *cooperation*. `--scheme=closed-loop` settles
it: identical fleet, identical cue sweep, identical delivery, identical
completion rule, and the only difference is that the ground has **no cooperative
substrate** — a node that crosses the threshold answers whatever UAV is overhead
with a direct single-hop ECHO. No cell tree, no cross-cell SHARE, no election.

16×16, **N = 120 paired seeds**, one build, realistic sensing:

| metric | proposed | closed-loop | proposed wins | Cliff δ | p |
|---|---:|---:|---:|---:|---:|
| mission time | 103.9 s | **99.2 s** | 17/117 | +0.479 | 6.6e-15 |
| UAV energy | 68.3 kJ | **61.1 kJ** | 15/120 | +0.569 | 7.5e-18 |
| application packets | 3 471 | **1 616** | **0/120** | +0.997 | 2.0e-21 |
| fix error (median) | **14.6 m** | 19.0 m | 51/117 | −0.159 | 0.0047 |
| fix error (p90) | **29.9 m** | 42.0 m | — | — | — |
| victim served | **92.5 %** | 87.5 % | — | — | — |

**Read it plainly: the cooperative scheme is beaten on every cost axis by a
non-cooperative one that merely closes the loop.** On packets it does not win a
single one of 120 paired seeds. The cost advantage this study has been reporting
against blind coverage is therefore attributable to **feedback**, not to
cooperation — and any claim that "edge cooperation makes SAR faster and cheaper"
is not supported by this data.

What cooperation does buy, at a cost of +5 % time, +12 % energy and +115 %
packets:

- **Tail accuracy — the strongest of the three.** p90 fix error 29.9 m vs 42.0 m
  (−29 %). Aggregating a region beats trusting the loudest thing one UAV
  happened to overhear, precisely when that single overheard reading is bad.
- **Median accuracy — real but small.** 14.6 m vs 19.0 m, δ = −0.159 (*small*),
  p = 0.005. Note proposed is closer in only 51/117 pairs: it wins by margin,
  not by frequency.
- **Reliability — directional, not established at this N.** 92.5 % vs 87.5 %.

The mechanism is what the design predicts: a single-hop ECHO is simply never
heard when no UAV is overhead, so the closed-loop arm aims from whatever it
caught in passing. The cooperative substrate exists to carry evidence that no
UAV was in position to hear. That is a **quality-of-estimate** argument, and it
is the only one this study can defend.

**Consequence for the paper.** The claim must be narrowed to: *closing the loop
is what delivers the cost advantage over blind coverage; edge cooperation buys a
markedly better tail on the delivered position, at a measurable cost in time,
energy and airtime.* The scaling-law tables below remain valid against the
open-loop baselines — but the closed-loop arm, not `tsp-mc`, is now the honest
comparator for any claim about cooperation.

## The scaling law against open-loop baselines (still valid, but no longer the headline)

Paired against the charitable coded baseline (same seed ⇒ same channel
realisation; Wilcoxon signed-rank, Cliff's δ), N = 120 at both scales:

| metric | 64 sensors | 256 sensors | paired evidence at 256 |
|---|---:|---:|---|
| mission time | 1.07× | **1.63×** | 117/117, δ = −1.00, p = 6.2e-21 |
| UAV energy | 1.10× | **1.66×** | 117/120, δ = −0.95, p = 1.0e-17 |
| application packets | 2.91× | **5.98×** | 120/120, δ = −1.00, p = 2.0e-21 |

**The effect emerges with scale — it does not merely grow.** At 64 sensors the
time and energy advantages are marginal and the paired statistics say so
(δ = −0.474, *medium*, 84/114 wins on time). At 256 they are decisive
(δ = −1.00, 117/117). Blind coverage cost grows with area; evidence-directed
delivery cost grows with (time-to-localize + transit), which is nearly flat in
area. So 8×8 sits at or below the crossover and 16×16 sits clearly above it.

This is a **cleaner** thesis than the earlier "the advantage roughly doubles",
which was measured at N = 20 and reported 1.29× → 2.09× with δ = −1.00
everywhere. Properly powered, the honest statement is *a tie at 64 sensors, a
clear win at 256* — a scaling claim needs a regime where the effect is absent,
and now the study has one.

Two secondary findings at 256 sensors, both in the proposed scheme's favour and
neither previously noticed:

- **We reach the victim faster than blind coverage does**, 68.6 s vs 80.9 s —
  despite spending the first ~40 s not delivering anything at all.
- **And far more predictably**: t_victim IQR 16.9 s vs the baseline's 51.8 s.
  The baseline's *makespan* is deterministic, but *when it happens to reach the
  particular node that matters* is a lottery over tour order. That distinction
  is worth making explicitly, because "predictable makespan" is otherwise the
  baseline's strongest selling point.

*Statistical caveat, stated because it matters:* `tsp-mc` is **deterministic
across seeds** (IQR exactly 0 on time, energy and packets — an open-loop
schedule cannot exploit a good channel). The matched pair therefore carries no
channel information for that arm, so the Wilcoxon p is floor-bounded by n
(2.0e-4 at n = 18, 6.6e-4 at n = 15, for a perfect split) and reflects complete
separation rather than an unusually strong sample. **Cliff's δ = −1.00 is the
honest effect statement.** The flip side is a genuine baseline virtue: a
**predictable makespan bound**, which the proposed scheme does not offer
(t_report IQR 24.1 s at 16×16).

## Closing the reliability gap — `--deliverDwell`, and what it costs

The victim-served gap (88–90 % against the baselines' ~99 %) was the scheme's
worst weakness. It is **not** an aiming problem. Of 12 failures at 16×16, nine
had a delivery that landed 19.7–43.6 m from the victim and three never got a
SUMMON to the DATA team at all — so the aim was right and the *delivery was too
short at range*. The mechanism: CONFIRM is broadcast by **any** node that
reconstructs the dataset, so a bystander sitting under the drop point closes the
loop while the victim, further out on a worse link, never finishes.

Re-aiming at the next candidate does not fix it — measured, no change (and at an
eager 26 s trigger it actively *hurt*, degrading the fix from 14.6 m to 22.8 m).
Delivering for longer does:

| | 8×8 dwell 20 | **8×8 dwell 40** | 16×16 dwell 20 | **16×16 dwell 40** |
|---|---:|---:|---:|---:|
| victim served | 87.5 % | **93.3 %** | 90.0 % | **96.7 %** |
| mission time | 76.0 s | 94.1 s | 113.3 s | 125.2 s |
| energy | 48.4 kJ | 57.7 kJ | 72.6 kJ | 78.5 kJ |
| packets | 2 107 | 3 180 | 3 583 | 4 667 |
| fix error | 13.6 m | 13.6 m | 14.6 m | 14.6 m |
| **vs tsp-mc × 4, time** | 1.07× | **0.86×** | 1.63× | **1.48×** |
| **vs tsp-mc × 4, energy** | 1.10× | **0.92×** | 1.66× | **1.54×** |

**The right setting depends on density, and at 64 sensors it inverts the
comparison.** At 256 sensors, dwell 40 buys near-parity reliability (96.7 % vs
the baseline's 97.5 %) while staying 1.48× faster and 1.54× cheaper — that is
the configuration to lead with. At 64 sensors the same setting makes the scheme
**slower and more expensive than blind coverage** (0.86×, 0.92×), so at that
density the honest recommendation is the short dwell and the localization
output, not a cost claim.

The default stays at 20 s so published numbers do not shift silently; 40 s is
`--deliverDwell=40`.

## The cost, reported alongside the benefit

Three costs, all real:

1. **Reliability, and it is the real one.** Victim served, N = 120:

   | | 8×8 | 16×16 |
   |---|---:|---:|
   | **proposed** | **87.5 %** [80.4, 92.3] | **90.0 %** [83.3, 94.2] |
   | tsp-mc × 4 | 99.2 % | 97.5 % |
   | nocoop × 4 | 99.2 % | — |

   Directed delivery misses where a carpet cannot. **`--deliverDwell=40` closes
   most of this** — 93.3 % / 96.7 %, against the baselines' 99.2 % / 97.5 % — at
   the cost documented above, which is affordable at 256 sensors and is not at
   64. Mission completion is also below 100 % (95.0 % / 97.5 %), which the
   N = 20 campaigns missed entirely.
2. **Energy against minimum hardware.** `tsp-mc × 1` uses 25.1 kJ to our 48.4,
   in 120/120 paired seeds (δ = +1.00).
3. **Makespan predictability.** The baselines' *completion time* has exactly
   zero variance; ours has a 22.9 s IQR at 16×16. A planner that must promise a
   deadline is better served by the open-loop schedule. (But see above: the
   baseline's *time to the victim specifically* is far less predictable than
   ours, IQR 51.8 s vs 16.9 s. The two "predictability" claims point opposite
   ways and both belong in the paper.)
4. **At 64 sensors, the cost advantage is marginal** — 1.07× time, 1.10× energy,
   with a medium rather than large effect size. Anyone deploying at that density
   should choose on the localization output, not on cost.

None of these is hidden in an appendix. A deployment that values guaranteed
coverage, minimum airframes, or a hard deadline over speed and a position
should not use this scheme as it currently stands.

## Still open — do not cite these as settled

- **The CONFIRM closure criterion is still wrong in principle**, even though
  `--deliverDwell` papers over its effect. Any node that reconstructs the
  dataset may CONFIRM, so the loop can close on a bystander rather than on the
  node the summon actually aimed at. Making CONFIRM carry the confirming node's
  evidence — and requiring closure to come from the aim target or its equal —
  is the principled fix and is not implemented.
- **Three of twelve failures never got a SUMMON to the DATA team at all**
  (no divert, no delivery). That is a coordination failure distinct from the
  range failure the dwell addresses, and it is unfixed.
- **The noise model is a first cut.** Additive Gaussian on the clue quality with
  a per-node frozen GPS offset is defensible but not derived from a real
  detector; a measured ROC from an actual person-detector on forest imagery
  would replace a modelling assumption with data.
- **W2** The aiming rule is Weighted Centroid Localization under another name.
  The noise sweep now gives this teeth: centroid and argmax swap places
  depending on whether you care about the median or the tail, which means
  neither is near optimal. An ML/NLS estimator and a CRLB would say how much is
  being left on the table.
- ~~**W4** All baselines are open-loop~~ — **done, and it went against us.**
  See "What cooperation actually buys". The closed-loop non-cooperative arm is
  cheaper than the cooperative one on time, energy and packets; cooperation's
  defensible gain is a −29 % p90 fix error. The thesis is narrowed accordingly.
- **W7 is only HALF addressed — this is not random deployment.** `--victimOnNode=0`
  displaces the victim uniformly in [−s/2, +s/2]², which *is* the Voronoi cell of
  the lattice point. Consequences, both verified (audit A3): the nearest node is
  therefore **always** the original node (`targetNodeId` differs in 0/20 seeds),
  and the victim is **always within s/√2 = 14.1 m of a sensor** by construction
  (measured median 9.2 m, max 11.9 m). The estimator's free lunch is gone, but
  the deployment is still a perfect lattice with no density variation and no
  coverage holes. Say "victim off-lattice"; **never** say "random deployment".
  A PPP deployment where the victim can fall in a gap would attack the
  victim-served rate far harder than this does.
- **Repro gap** The HTML replay viewers in `docs/visualize/` were generated ad
  hoc and have no committed generator; they are illustrations, not evidence.
  Every number in this file comes from a committed script in `tools/`.

## When to summon — the mechanism that actually sets the accuracy

Decomposing the fix error across the realism knobs (16×16, N = 60,
`tools/campaign_error_budget.py`) produced the most useful negative result in
this study:

| detector σ | GPS σ | victim | median | p90 |
|---:|---:|---|---:|---:|
| 0.00 | 0 m | on node (fully ideal) | 20.0 m | 28.3 m |
| 0.00 | 0 m | continuous | 18.1 m | 30.3 m |
| 0.00 | 5 m | continuous | 19.3 m | 32.4 m |
| 0.10 | 0 m | continuous | 18.9 m | 36.1 m |
| 0.10 | 5 m | continuous (realistic) | 20.7 m | 38.7 m |

**The median is ~18–21 m everywhere, including the perfect configuration.**
Measurement quality moves the p90 and essentially nothing else. So the floor is
not a sensing problem, and it is not an estimator problem (centroid vs argmax is
a wash — see below) and it is not the one-cell aiming scope either (fixing that
moved the median 0.8 m, though it did buy +7.5 pp reliability).

It is **decision time**. A leader aims at the strongest reporter *it has heard
from*, and a node reports only once the FAST sweep has delivered it enough cues
to cross the cooperation threshold. Summon early and you aim from a sparse,
biased sample of the evidence field.

**But the observation window is not a free knob** (audit A10). It must be long
enough for the field to be sampled and *shorter than the sweep*, because once
the FAST UAVs finish and fly home there is nobody airborne to relay the SUMMON
to the DATA team. That upper bound scales with area — a fixed 45 s was optimal
at 16×16 and produced **zero localizations in 60/60 seeds at 8×8**. A wall-clock
constant is therefore a hidden function of grid size.

Two changes remove that trap, both local and both bounded:

- **Adaptive window** (`--adaptiveWindow`, default): summon once this cell's own
  evidence has stopped growing for `kEvidenceStableS`, with `--minObserve` as a
  floor and `kElectDeadlineS` as a ceiling. Big grids keep feeding the leader
  longer and so defer the decision longer, with no knowledge of the grid at all.
- **Bounded relay hold** (`kRelayGraceS = 30 s`): a FAST UAV that has finished
  sweeping holds station as a relay until it relays a SUMMON or the grace
  expires. Adaptive timing *alone* made 8×8 worse (63 % mission completion),
  which is what showed the window was the symptom and the departing relay the
  cause.

Result at the realistic operating point (N = 60), versus the fixed window:

| | 8×8 fixed | **8×8 adaptive** | 16×16 fixed | **16×16 adaptive** |
|---|---:|---:|---:|---:|
| fix error (median) | 19.2 m | **15.6 m** | 20.2 m | **14.7 m** |
| fix error (p90) | 36.2 m | **30.6 m** | 38.7 m | **27.3 m** |
| victim served | 88 % | **90 %** | 85 % | **92 %** |
| mission time | 64 s | 75 s | 94 s | 114 s |
| energy | 41 kJ | 48 kJ | 59 kJ | 73 kJ |

**This is a real trade, not a free win.** Roughly 25–30 % better localization and
better reliability, for roughly 20 % more time and energy — which drops the cost
ratio against `tsp-mc × 4` from 1.28× to ~1.08× at 8×8 and from 2.05× to ~1.63×
at 16×16. Both operating points still dominate the baseline on every axis while
producing a position it cannot produce at all, so **the paper should publish the
curve and let the deployment pick its point**, rather than quote whichever end
flatters the scheme.

## What limits the localization accuracy (mechanism)

These are *ablations of the proposed scheme against itself*, so the
re-levelling (which changed cruise speed and completion rules) does not move
them; the absolute delivery error, however, is now the re-measured 18–20 m of
the table above, not the 15.8 m an earlier revision of this file quoted.

> **Retracted.** Item 1 below said the accuracy is *sensing-limited*. It is not.
> Decomposing the error budget (audit A9, `tools/campaign_error_budget.py`,
> 16×16, N = 60) gives a ~18–21 m median in **every** configuration including a
> noise-free detector with exact GPS and the victim on a node. The `clueDecay`
> sweep below is real, but it varies the *field's* spatial scale, not the
> measurement quality, so it does not support the sensing-limited reading. The
> actual limit is **decision time** — see "When to summon" below.

1. **Accuracy is sensing-limited, not estimator-limited.** *(retracted, above.)*
   Sweeping the on-node
   detector range (`--clueDecay`), the error scales ≈ 0.2–0.25× the decay
   length: **6.6 m** @ 30 m, ~16 m @ 60 m, **21.2 m** @ 120 m. It is *not*
   limited by sensor density (14 / 16 / 11 m at 15 / 20 / 30 m spacing).
2. **How the pipeline degrades as the sensing side stops being idealized.**
   The published configuration has a noise-free detector, exact GPS, and the
   victim sitting exactly on a sensor — so the strongest reporter *is* the
   answer. `tools/campaign_noise.py` walks away from that, scoring the fix the
   BS decoded, with both estimators paired at every point (8×8, N = 20):

   **8×8, N = 20:**

   | detector σ | GPS σ | victim | centroid med / p90 | argmax med / p90 | Cliff δ | victim served |
   |---:|---:|---|---:|---:|---:|---:|
   | 0.00 | 0 m | on node | **16.4** / 25.5 m | 20.0 / 28.3 m | −0.28 | 95 % |
   | 0.00 | 0 m | continuous | 19.9 / 31.6 m | 17.8 / 34.1 m | +0.01 | 85 % |
   | 0.05 | 2 m | continuous | 19.0 / 30.3 m | **16.5** / 34.0 m | +0.14 | 95 % |
   | 0.10 | 5 m | continuous | 21.8 / 33.3 m | **18.0** / 37.8 m | −0.01 | 95 % |
   | 0.20 | 10 m | continuous | 39.8 / 59.1 m | **25.3** / 84.9 m | +0.16 | 70 % |

   **16×16, N = 20:**

   | detector σ | GPS σ | victim | centroid med / p90 | argmax med / p90 | Cliff δ | victim served |
   |---:|---:|---|---:|---:|---:|---:|
   | 0.00 | 0 m | on node | **17.3** / 24.7 m | 20.0 / 28.3 m | +0.04 | 100 % |
   | 0.00 | 0 m | continuous | **14.9** / 24.6 m | 18.2 / 28.3 m | −0.09 | 90 % |
   | 0.05 | 2 m | continuous | 19.6 / 30.2 m | **16.9** / 27.3 m | +0.14 | 95 % |
   | 0.10 | 5 m | continuous | 19.0 / 34.4 m | **18.2** / 35.4 m | −0.06 | 100 % |
   | 0.20 | 10 m | continuous | 64.6 / 104.4 m | **24.1** / 64.5 m | **+0.51** | 30 % |

   Three readings, two of them unflattering:

   - **Removing the victim-on-a-node coincidence alone costs 16.4 → 19.9 m at
     8×8**, with no noise added. That much of the published accuracy was a
     property of the deployment, not of the scheme. (At 16×16 it happens to
     help, 17.3 → 14.9 m: denser reporting absorbs the offset.)
   - **The estimator hypothesis is refuted.** Averaging several noisy reports was
     supposed to beat trusting the loudest one, with the gap *growing* in noise.
     The opposite happens: **argmax is better or tied at every noisy operating
     point on both grids**, and at σ = 0.20 the centroid collapses (64.6 m
     median, 104 m p90, Cliff δ = +0.51 — a large effect against it). The
     evidence²-weighted centroid is not robust: a distant false positive enters
     with *squared* weight and drags the estimate off the victim, and false
     positives are exactly what detector noise manufactures.
   - An earlier revision of this file claimed the centroid at least won the tail
     "at every operating point". That was read off the 8×8 sweep alone and **is
     wrong** — the 16×16 sweep contradicts it in two rows and reverses it
     catastrophically in the last.

   **Consequence, applied rather than noted:** the default aiming rule is now
   argmax (`--aimArgmax=0` selects the centroid as the ablation). This is audit
   item W1's own stated remedy — *if the centroid does not beat argmax under
   realistic noise, replace it* — and the data says replace it.

   It also makes W2 (an ML/NLS estimator with a CRLB) the right next step rather
   than a formality: a rule as crude as "believe the loudest sensor" beating a
   weighted estimator is the signature of both sitting far from the bound.
3. **The distributed election is a tail-risk fix, not a median improvement —
   and it costs packets.** `--electSuppress=0` restores the pre-fix behaviour
   (the stand-down was a one-hop SUMMON that could not reach a leader 63–156 m
   away over a ~37 m radio). Paired over 20 seeds:

   | | 8×8 ON | 8×8 OFF | 16×16 ON | 16×16 OFF |
   |---|---:|---:|---:|---:|
   | runs forming **two** competing regions | **0/20** | 8/20 | **0/20** | 6/20 |
   | mission complete | **100 %** | 95 % | 100 % | 100 % |
   | fix error (median) | 16.4 m | 17.4 m | 17.3 m | 17.3 m |
   | packets (median) | 2 010 | 1 864 | 2 939 | 2 806 |
   | t_report / energy | — no measurable difference — | | | |

   Read honestly: the *median* run already elected one region without the flood,
   because the SHARE-plane deferral (yield to a stronger neighbouring cell) was
   doing that work. What the flood removes is the **tail** — the 30–40 % of runs
   that split the fleet across two simultaneous deliveries, which is where the
   5 % mission failure at 8×8 lived. It buys that for **+4 % to +8 % packets**
   and no latency or energy change. It is a robustness mechanism, and this study
   claims nothing more for it.
4. **Observation window buys accuracy and coverage.** `--minObserve` 0→30 s:
   delivery error 18.4 → 10.8 m and the ≤20 m rate 63 → 90 %, at +5–10 s
   latency.
5. **Victim completion is dwell-limited, not aiming-limited.** At 8 s dwell only
   ~47 % of runs completed the victim's dataset even though it sat inside the
   delivery footprint; 20 s dwell → 100 %, +12 s latency. Diagnosed by
   single-knob test, not tuned blind.

## Literature baseline: UAV-enabled multicasting (Zeng–Xu–Zhang, TWC 2018)

`--scheme=tsp-mc` implements the core contribution of *"Trajectory Design for
Completion Time Minimization in UAV-Enabled Multicasting"* (Zeng, Xu, Zhang,
IEEE TWC 17(4), 2018), adapted to our scenario: a **single UAV** covers ALL
ground terminals with a minimum-disk **virtual-base-station placement**, flies a
**TSP tour** over the VBSs (nearest-neighbour + 2-opt, from the BS), and
fly-hovers at each VBS for a connection-time dwell so every GT in the disk
recovers the multicast file (their network-coded accumulation maps to our
order-insensitive chunk model). Per our mission definition the UAV must then
**return to the BS and report** to complete. Same radio, channel, chunking and
dwell constants as the other baselines — only the trajectory logic is theirs.
Faithfulness note: this is their *fly-hover* design; their LP speed-optimized
variant would shave some travel time but cannot change the structural gap below.

Redundancy is modeled explicitly: their coded multicast sends *more than the
file* so GTs recover despite erasures. The fleet variant bands the GT set (like
nocoop) with one VBS/TSP tour per UAV, and the mission completes only when
**every** UAV has returned and reported (the BS counts distinct reporters).

### Is the baseline's hover time fair? (audit F4)

The per-VBS dwell is the one knob that could silently rig this comparison, so it
is derived, not chosen, and every degree of freedom in it was swept.

**Recovery semantics come first, and getting them wrong is what inflated the
dwell.** Zeng'18 multicasts *rateless / network-coded* symbols: a terminal
recovers after roughly a file-worth of **any** symbols. An earlier revision of
this study replayed identical chunk indices instead (uncoded repetition), which
forces every GT to see all 382 *distinct* indices — a per-packet success
requirement of q ≥ 0.878 where the coded scheme needs q ≥ 0.35. That is a
modelling error against the baseline, not a property of their design, and it is
what pushed the "required" redundancy to R = 3. Both are now measurable via
`--codedMulticast`:

| nominal R | coded (their semantics) |  | uncoded replay (wrong) |  |
|---:|---:|---:|---:|---:|
|  | GT coverage | victim | GT coverage | victim |
| 1.0 | 89.5 % | 95 % | 60.4 % | 65 % |
| **1.1** | **98.8 %** | **100 %** | 85.5 % | 90 % |
| 1.2 | 98.8 % | 100 % | 85.5 % | 90 % |
| 1.5 | 98.8 % | 100 % | 85.5 % | 90 % |
| 2.0 | 98.9 % | 100 % | 88.1 % | 95 % |
| 3.0 | 100.0 % | 100 % | 95.8 % | 100 % |

(N = 20, 8×8, 4 UAVs. Their own goal is "every GT recovers the file", so the
fair operating point is the smallest R that meets it — **R = 1.1** under coded
recovery, not 3.0.)

**The realized dwell quantizes to whole dataset passes, in the baseline's
favour.** The dwell budget is `R × 382 × 0.02 s`, but the DELIVER state only
re-checks it at the *end* of a full pass, so the airtime actually spent is
⌈budget / 7.64 s⌉ passes. Measured chunk counts confirm it:

| nominal R | realized passes per stop |
|---:|---:|
| 1.0 | 1.05 |
| 1.1 – 2.0 | **2.03** |
| 3.0 | 3.01 |

So the configuration this study reports (`--mcRedundancy=1.2`) actually grants
the baseline **2× the file airtime per stop**, i.e. an effective R of 2.0, well
above the R = 1.1 that meets its goal.

**The head-to-head is therefore insensitive to this knob.** Every nominal R in
**[1.1, 2.0]** produces the *identical* baseline result (81.2 s, 53.1 kJ, 6 134
packets at 8×8) because they all buy the same 2 passes. There is no value in
that band at which the comparison flips, and the two endpoints outside it move
it the wrong way for us to have picked it: R = 1.0 makes the baseline faster but
fails its own coverage goal, R = 3.0 makes it slower still.

**Sweep 2 — does the 50 m VBS radius penalize them?** Their disk cover uses the
conservative design radius while the measured reliable A2G range is ~60–80 m.

| VBS radius | VBS per band | GT coverage | mission | energy |
|---:|---:|---:|---:|---:|
| 40 m | 3 | 99.7 % | 146.5 s | 87.4 kJ |
| **50 m** | **2** | **96.8 %** | **114.9 s** | 65.7 kJ |
| 60 m | 3 | 98.5 % | 143.1 s | 83.1 kJ |
| 70 m | 2 | 82.9 % | 108.7 s | 63.0 kJ |
| 80 m | 2 | 82.9 % | 108.7 s | 63.0 kJ |

*(measured at R = 3; the ranking across radii is a property of the disk cover,
not of the dwell.)* The default 50 m is **tied-best** on tour length (2 VBS per
band, the minimum observed) *and* keeps coverage high — a favourable
configuration for them, not a handicap. The non-monotonicity (60 m needs *more*
disks than 50 m) is a greedy set-cover artifact on the banded strip geometry,
verified deterministic by replaying the algorithm offline. Pushing to 70–80 m
buys ~6 s but collapses GT coverage to 83 %, breaking the multicast guarantee
that justifies the scheme.

**Verdict.** Both degrees of freedom sit at settings that are
neutral-to-favourable for the baseline, and the conclusion is insensitive to
both. Knobs: `--mcRedundancy`, `--mcRadius`, `--codedMulticast`.

### What the baseline structurally cannot do

`tsp-mc` and `nocoop` complete the mission and serve the victim — reliably, and
with a predictable makespan bound the proposed scheme does not offer. What they
never produce is a **position**. This is now measured rather than asserted: the
BS decodes `reportedX/reportedY` out of the REPORT packet it physically
received, and for every blind-coverage run that field is empty, because no UAV
ever had a coordinate to carry. The rescue team learns that the file was
disseminated, not where to go. Edge cooperation is what converts "serve everyone
eventually" into "serve the right place now, and say where it is".

## Sensor-spacing sweep — connectivity threshold (N = 30)

| spacing | localize fires | delivery err (med) | intra shares | inter shares |
|---:|---:|---:|---:|---:|
| 15 m | 100 % | 13.9 m | 77 | 3.8 |
| 20 m | 100 % | 15.8 m | 56 | 8.5 |
| 30 m | 93 %  | 11.5 m | 21 | 11.7 |
| 40 m | **10 %** | — | **0** | 4.7 |

**Cooperation collapses when spacing exceeds the G2G radio range (~37 m).** At
40 m the intra-cell tree disconnects: members cannot reach their Cell Leader,
intra shares fall to 0, and localization fires in 10 % of runs. Deployments must
keep spacing below `DeriveG2gRangeM()` (~37 m at 0 dBm / −95 dBm / n = 3.5).
Below that threshold, density buys connectivity margin — not accuracy.

## Honesty ledger

- **Real over radio, channel-subject:** cue dissemination, intra-cell reports
  (RPT, multi-hop up the cell tree), inter-cell shares (SHARE flood), summon,
  election stand-down (RCLAIM flood), A2A relay, role claims (CLAIM), full-data
  delivery, confirm, report + victim fix, courier handoff.
- **Distributed:** no global-view object; all decisions are taken by node apps
  from bytes that physically arrived. Delivery coordinates are radio-reported
  node GPS, interpolated on the leader, and the coordinates the BS ends up
  holding are the ones it decoded out of a REPORT packet — not simulator state.
- **Assumed (declared):** pre-initialized PECEE substrate (cells/trees/leaders
  loaded at setup); UAVs know sensor positions for sweep planning; victim
  self-identifies for metrics/baseline-stop only.
- **Known metric caveats:** `timeToLocalize` marks the first summon; with larger
  observation windows several cells summon simultaneously (targeted
  multi-candidate delivery), which raises packet cost — reflected in pktSent.

## Reproduce

```
scenario-sar --seed=S --scheme={proposed,nocoop,pure-uav,tsp-mc}
             [--gridSize=8] [--gridSpacing=20] [--minObserve=20] [--clueDecay=60]
             [--allHome=1] [--codedMulticast=1] [--mcRedundancy=1.2] [--mcRadius=50]
             [--fastSpeed=0] [--dataSpeed=0] [--aimArgmax=0]

tools/campaign_stats.py OUT 20 --grid=8 \
    --senseSigma=0.10 --gpsSigma=5 --victimOnNode=0   # head-to-head (realistic)
tools/campaign_stats.py       OUT 20 --grid=16   # the scaling arm
tools/campaign_stats.py       --selftest         # validates the statistics code
tools/campaign_mc_redundancy.py OUT 20 4 coded 8 # baseline fairness sweep (F4)
tools/campaign_ablation_aim.py  OUT 20 8,16      # centroid vs argmax (W1)
tools/campaign_sweep2.py      OUT 20 <knob> <v,v># any-knob sweep, delivery metric
```

Every table above names the script that produced it and the N it used. Nothing
in this file is quoted from a run whose configuration is not reconstructible
from `metrics.csv` alone — that is why `gridSpacing`, `victimX/Y` and
`reportedX/Y` are columns rather than assumptions in the analysis scripts.
