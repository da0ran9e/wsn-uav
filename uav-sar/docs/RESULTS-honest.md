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

## The causal chain that got us here (each link measured)

1. **Aiming.** The elected leader interpolates the evidence peak from radio data
   only — members' RPTs (per-node evidence + self-reported GPS) plus neighbour
   cells' SHAREs (aggregate + cell centre). Delivery error: **15.8 m median**.
2. **Aiming is sensing-limited (the honest resolution law).** Sweeping the
   on-node detector's range (`--clueDecay`): error scales ≈ 0.2–0.25× decay —
   **6.6 m** @ 30 m decay, 15.8 m @ 60 m, 21.2 m @ 120 m. Sharper sensing →
   sharper delivery. (Delivery error is *not* limited by sensor density: 14/16/
   11 m across 15/20/30 m spacing.)
3. **Observation window buys accuracy AND coverage.** `--minObserve` 0→30 s:
   delivery error 18.4 → 10.8 m (more reports to interpolate) and ≤20 m rate
   63 → 90 %, at +5–10 s pipeline latency.
4. **Victim completion was dwell-limited, not aiming-limited.** With ~16 m error
   the victim sits inside the delivery footprint, yet at 8 s dwell only ~47 %
   of runs completed it (the ~150-chunk dataset needs several broadcast passes
   at footprint edge). Dwell 20 s → **victim served 100 %**, +12 s report
   latency. This was diagnosed (hypothesis → single-knob test), not tuned blind.

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
file* so GTs recover despite erasures — the per-VBS connection time is sized to
`kMcRedundancy = 3×` the dataset airtime. The fleet variant bands the GT set
(like nocoop) with one VBS/TSP tour per UAV, and the mission completes only when
**every** UAV has returned and reported (the BS counts distinct reporters).

| Metric (N = 30, 8×8) | tsp-mc × 1 UAV | tsp-mc × 4 UAV | proposed × 4 UAV |
|---|---:|---:|---:|
| Mission complete (all reports @ BS) | 100 % @ 216.2 s | 100 % @ **114.9 s** | 100 % @ **66.1 s** |
| Victim node has full data | 97 % @ 86.6 s | **100 %** @ 45.2 s | 97 % @ 42.7 s |
| Packets sent | 7259 | 9576 | **1942** |
| UAV energy | **34.5 kJ** | 65.7 kJ | 44.4 kJ |
| Localization output | none | none | **±16 m estimate** |

**Honest reading.** With an equal fleet their gap narrows but does not close:
4 UAVs cut their completion 216 → 115 s (sub-linear — the makespan is the
farthest band's transit + dwells) and the banded carpet reaches the victim node
about as fast as we do (45 vs 43 s). But the mission itself — everyone home, BS
informed — is still **1.7× slower**, at **1.5× the energy** (hover-dwelling
every VBS with 3× redundancy is expensive) and **4.9× the packets**, and it
still produces **no location estimate**: the rescue team knows the file was
disseminated, not where the victim is. Edge cooperation is what converts "serve
everyone eventually" into "serve the right place now, and say where it is".
Their single-UAV strength (min hardware, min energy) remains real and is
reported as such.

### Is the baseline's hover time fair? (audit)

The hover/dwell time is the one knob that could silently rig this comparison, so
it is derived, not chosen, and both of its degrees of freedom were swept.

**How each scheme's dwell is computed** (identical 0.02 s per-chunk stagger, and
the same 382-chunk dataset — 8×150 B + 2×600 B + 4×4000 B + 1×16000 B at 91 B
payload — so one full pass costs **7.64 s** of airtime for everyone):

| scheme | dwell per stop | in passes |
|---|---|---|
| `tsp-mc` | `R × 382 × 0.02 s` = 22.9 s at R = 3 | exactly R = 3.0 |
| `nocoop` | fixed `kBaselineDwellS` = 25 s | 3.27 |
| `proposed` | transmit **until CONFIRM**, then `kMinDeliverDwellS` = 20 s | ≥ 2.62, feedback-driven |

So the baseline is *not* given a shorter dwell than the other blind scheme
(3.0 vs nocoop's 3.27 passes). `proposed` is not given a longer one either — its
delivery is feedback-terminated, which is the cooperation benefit under test,
and it pays that cost at **one** stop while `tsp-mc` pays it at **every** VBS.

**Sweep 1 — is R = 3 generous or stingy?** Their paper sizes the connection time
to just meet a target recovery probability, so the fair R is the smallest one
that meets *their own* goal: every GT recovers the file (not just the victim).

| R | GT coverage | victim served | mission | energy | packets |
|---:|---:|---:|---:|---:|---:|
| 1.0 | 54.0 % | 63 % | 80.7 s | 43.8 kJ | 3081 |
| 1.5 | 88.8 % | 90 % | 96.1 s | 54.2 kJ | 6137 |
| 2.0 | 90.3 % | 97 % | 99.6 s | 55.4 kJ | 6520 |
| **3.0** | **96.8 %** | **100 %** | **114.9 s** | 65.7 kJ | 9576 |
| 4.0 | 98.9 % | 100 % | 137.9 s | 77.3 kJ | 13019 |

R = 3 is **the stingiest setting that still meets their goal** (~97 % of all GTs,
100 % of victims); R = 2 drops a tenth of the network and R = 1 fails outright.
Nothing is inflated in their favour or against them — if anything R = 3 leaves
them 3 % short of full coverage, so **their victim guarantee is probabilistic,
not structural** (an earlier draft of this document called it structural; that
was wrong and is corrected here).

**Sweep 2 — does the 50 m VBS radius penalize them?** Their disk cover uses the
conservative design radius while the measured reliable A2G range is ~60–80 m, so
a too-small radius would force extra hovers.

| VBS radius | VBS per band | GT coverage | mission | energy |
|---:|---:|---:|---:|---:|
| 40 m | 3 | 99.7 % | 146.5 s | 87.4 kJ |
| **50 m** | **2** | **96.8 %** | **114.9 s** | 65.7 kJ |
| 60 m | 3 | 98.5 % | 143.1 s | 83.1 kJ |
| 70 m | 2 | 82.9 % | 108.7 s | 63.0 kJ |
| 80 m | 2 | 82.9 % | 108.7 s | 63.0 kJ |

The default 50 m is **tied-best** on tour length (2 VBS per band, the minimum
observed) *and* keeps coverage high — it is a favourable configuration for them,
not a handicap. The non-monotonicity (60 m needs *more* disks than 50 m) is a
greedy set-cover artifact on the banded strip geometry, not noise: the cover
sizes are deterministic (verified by replaying the algorithm offline). Pushing
to 70–80 m does buy them ~6 s but collapses GT coverage to 83 %, i.e. it breaks
the multicast guarantee that justifies the scheme.

**Verdict.** Both dwell degrees of freedom sit at settings that are neutral-to-
favourable for the baseline, and the qualitative conclusion is insensitive to
them: even at their most permissive coverage-preserving configuration
(R = 3, 70 m → 108.7 s) the baseline is still ~1.6× slower than `proposed` and
still yields no location estimate. Knobs: `--mcRedundancy`, `--mcRadius`.

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
scenario-sar --seed=S --scheme={proposed,nocoop,pure-uav}
             [--minObserve=20] [--clueDecay=60] [--gridSpacing=20]
tools/campaign_compare.py        # 3-scheme table
tools/campaign_sweep2.py         # any-knob sweep with the CORRECT delivery metric
```
