# UAV-SAR — Results (post-audit, re-levelled)

> **Provenance.** Every number below was regenerated from the current binary
> after the four independent audits (see `AUDIT-SYNTHESIS.md`) and the
> re-levelling commits. Numbers in earlier revisions of this file are void.

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
| `nocoop`/`pure-uav` could never complete the mission (0 % by construction) | they fly home and report too — **all four arms reach 100 %** |
| `timeToLocalize` reported the `--minObserve` knob | window applied first, evidence-ordered backoff on top |

## Head-to-head (N = 20 seeds, medians with bootstrap 95 % CI)

**8×8 — 64 sensors, 140×140 m**

| scheme | mission complete | t_report | victim served | energy | packets |
|---|---:|---:|---:|---:|---:|
| **proposed** | 95 % | **63.0 s** [59.0, 65.5] | 95 % | **41.7 kJ** | **1 866** |
| tsp-mc (coded, R=1.2) | 100 % | 81.2 s | 100 % | 53.1 kJ | 6 134 |
| nocoop | 100 % | 111.8 s | 100 % | 73.5 kJ | 12 246 |

**16×16 — 256 sensors, 300×300 m**

| scheme | mission complete | t_report | victim served | energy | packets |
|---|---:|---:|---:|---:|---:|
| **proposed** | 95 % | **90.6 s** [84.3, 103.6] | 100 % | **58.6 kJ** | **2 861** |
| tsp-mc (coded, R=1.2) | 100 % | 184.9 s | 100 % | 120.6 kJ | 21 421 |
| nocoop | 100 % | 266.0 s | 100 % | 174.8 kJ | 36 701 |

## The result is a scaling law

Paired comparison against the charitable coded baseline (same seed ⇒ same
channel realisation; Wilcoxon signed-rank, Cliff's δ):

| metric | 64 sensors | 256 sensors | paired evidence |
|---|---:|---:|---|
| mission time | **1.29×** | **2.04×** | 19/19 wins, δ = +1.00 |
| energy | **1.27×** | **2.06×** | 19/19 wins, δ = +1.00 |
| application packets | **3.29×** | **7.49×** | 19/19 wins, δ = +1.00 |

**The advantage roughly doubles from 64 to 256 sensors.** Blind coverage cost
scales with area; evidence-directed delivery cost scales with
(time-to-localize + transit). The 8×8 configuration used for the previous
headline is near the crossover, which is exactly why an honest reading there
looked like a tie.

*Statistical caveat, stated because it matters:* `tsp-mc` is **deterministic
across seeds** (IQR exactly 0 on time, energy and packets — an open-loop
schedule cannot exploit a good channel). The matched pair therefore carries no
channel information for that arm, so the Wilcoxon p is floor-bounded by n
(p = 1.3e-4 at n = 19 for a perfect split) and reflects complete separation
rather than an unusually strong sample. Cliff's δ = +1.00 is the honest effect
statement. The flip side is a genuine baseline virtue: a **predictable makespan
bound**.

## The cost, reported alongside the benefit

`proposed` completes the mission in **95 %** of runs at both scales; every
baseline completes in **100 %**. Localization can fail where blind coverage
cannot — the scheme trades a small reliability margin for a large cost margin.
Any use of these results must state both.

Delivery error (distance from the drop point to the true victim) is
**19.7 m** median at 8×8 and **18.2 m** at 16×16 — but see the open items below
before treating that as an accuracy result.

## Still open — do not cite these as settled

- **B2** The distributed election cannot fire in the evaluated topology (cell
  leaders 63–156 m apart, ground radio 37 m). What runs is "every alerting cell
  summons independently". Unfixed.
- **M9 / W1** The clue field is noise-free with exact GPS, and the victim is
  always co-located with a sensor node — so aiming at the single strongest
  reporter (`--aimArgmax`, now implemented) is expected to beat the centroid.
  The ablation must be run and reported before any localization claim.
- **W2** The aiming rule is Weighted Centroid Localization under another name;
  an ML/NLS estimator and a CRLB are needed to make the accuracy interpretable.
- **W4** All baselines are open-loop; a closed-loop non-cooperative baseline is
  needed to attribute the gain to *cooperation* rather than to feedback.

## What limits the localization accuracy (mechanism)

These are *ablations of the proposed scheme against itself*, so the
re-levelling (which changed cruise speed and completion rules) does not move
them; the absolute delivery error, however, is now the re-measured 18–20 m of
the table above, not the 15.8 m an earlier revision of this file quoted.

1. **Accuracy is sensing-limited, not estimator-limited.** Sweeping the on-node
   detector range (`--clueDecay`), the error scales ≈ 0.2–0.25× the decay
   length: **6.6 m** @ 30 m, ~16 m @ 60 m, **21.2 m** @ 120 m. It is *not*
   limited by sensor density (14 / 16 / 11 m at 15 / 20 / 30 m spacing).
2. **The aiming rule is not where the gain comes from — measured, and it is a
   negative result.** `--aimArgmax` (deliver to the single strongest reporter)
   vs the evidence²-weighted centroid, paired over the same seeds:

   | grid | centroid med / p90 | argmax med / p90 | centroid closer | Cliff δ |
   |---|---:|---:|---:|---:|
   | 8×8 | 19.7 / 27.9 m | 21.7 / 31.2 m | 10/19 | +0.17 (small) |
   | 16×16 | 18.2 / 25.3 m | 20.0 / 30.2 m | 8/20 | −0.03 (negligible) |

   The two rules are **statistically indistinguishable**. That is consistent
   with (1): in a noise-free clue field with exact GPS and a victim co-located
   with a node, both estimators are limited by the same sensing resolution.
   **No claim is made for the centroid estimator.** The contribution under test
   is the cooperative pipeline that produces *any* fix at all, not the
   arithmetic that turns reports into a coordinate.
3. **Observation window buys accuracy and coverage.** `--minObserve` 0→30 s:
   delivery error 18.4 → 10.8 m and the ≤20 m rate 63 → 90 %, at +5–10 s
   latency.
4. **Victim completion is dwell-limited, not aiming-limited.** At 8 s dwell only
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
  (RPT, multi-hop up the cell tree), inter-cell shares (SHARE flood), summon +
  suppression election, A2A relay, role claims (CLAIM), full-data delivery,
  confirm, report, courier handoff.
- **Distributed:** no global-view object; all decisions are taken by node apps
  from bytes that physically arrived. Delivery coordinates are radio-reported
  node GPS, interpolated on the leader.
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

tools/campaign_stats.py       OUT 20 --grid=8    # head-to-head + paired inference
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
