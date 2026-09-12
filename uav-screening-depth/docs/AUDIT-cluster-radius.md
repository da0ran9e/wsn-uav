# AUDIT — cluster-radius probe (B4, B5, A6, composition)

Per AGENT-BRIEF §11.2. The reviewer has not seen the implementation reasoning;
this is the only channel for it. Everything I am unsure about is stated plainly.

Artifacts: `ns3/cell-spread.cc`, `src/screening/{dubins,scenario,tour}.py`,
`tools/{run_b4,run_a6,analyse_cluster_radius,campaign_stats,report_cluster_radius}.py`,
`config/cluster-radius.yaml`, `results/{B4,A6,cluster-radius}/`,
`report/cluster-radius.html`.

Pre-registration: `docs/PREREGISTRATION-cluster-radius.md`, committed at `98822fd`
**before** any sweep output was read. The scorecard in the report is computed
mechanically from the ranges recorded there (`analyse_cluster_radius.py`, `REG`),
not written by hand after the fact.

---

## 1. The missing notation document

The prompt says notation is fixed by `KY-HIEU-vi.md`. **That file is not in this
repository** and I could not read it. I used the symbols exactly as the prompt
writes them — `R`, `n_c`, `η`, `h_max`, `r_tx`, `r_bc`, `T_hop`, `T_spread`,
`T₁`, `R*`, `ρ`, `β`, `κ`, `A`, `C`, `v`, `φ` — and did not invent any. One known
collision with the earlier brief: heterogeneity is `h` there and `η` here, and
`h_max` is a different quantity from either. I used `η` for heterogeneity and
`h_max` for the hop count, and renamed nothing in already-committed E0 code.
**If `KY-HIEU-vi.md` disagrees, the symbols in this probe need a pass.**

## 2. Four bugs I found in my own work, and how

Recorded because the measurement would have been wrong and plausible in every
case, and because they are the reason to trust or distrust the rest.

**2.1 — LRL Dubins word never optimal.** A transcription error in the `q` term.
Caught because every candidate word is verified by forward-integrating the control
sequence to the goal, so the bad word was *rejected* rather than returned: the
symptom was LRL winning 0 of 4 000 random instances while its mirror RLR won 1 410.
Fixed by deriving LRL from RLR through the exact x-axis mirror symmetry, so only
one three-arc formula can be wrong and that one is covered by the integration
check. Mirror-pair win counts are now balanced (RLR 833 / LRL 781) and asserted.

**2.2 — Noon-Bean penalty M = 0.** I reasoned that forbidding non-successor
intra-cluster arcs forced one visit per cluster, so `M` was unnecessary. Wrong:
*re-entering* a cluster at a fresh node uses an ordinary inter-cluster arc and
costs nothing extra. At C = 120 the tour split a cluster into two blocks — 121
blocks for 120 clusters. Caught by an assertion on the recovered representative
count, which I had written for exactly this reason. `M = C·max_arc + 1` now, and
the number of inter-cluster arcs is asserted to equal C. `tests/test_tour.py`
brute-forces 3- and 4-cluster instances against exhaustive enumeration.

**2.3 — the advertisement stream starved the fragment pushes.** The first
protocol put advertisements and pushes in one FIFO per-node send queue under the
200 ms pacing. Advertisements monopolised the budget, so a *shorter* advertisement
interval produced a *slower* spread (8.0 s at 0.25 s vs 1.9 s at 2.0 s) and a
*denser* cell finished *faster* than a sparser one. Both inversions are physically
backwards. This is precisely the task's §7 trigger — "T_hop shows no dependence on
R or n_c → suspect a bug before believing it" — and I stopped and diagnosed rather
than reporting it. Fixed by making the radio an explicit serial resource with
fragment pushes at strict priority over advertisements, plus duplicate-push
suppression when a fragment is heard on air. All monotonicities are now the right
way round.

**2.4 — the run continued for the full 900 s cap after completing.** Cost most of
the wall time and changed no result. The sim now stops once every node holds all
`k`; censored runs still use the full cap.

Two smaller ones: `hex_centres` padded cells beyond the region and overcounted
cells by up to 1.6× (now clipped, and the residual 1.1–1.4× boundary overhead is
reported rather than hidden); LKH's ATSP path asserts `Gain % Precision == 0`,
which needs `PRECISION = 1`.

## 3. Assumptions not in the prompt

**A1 — TX power was calibrated, not assumed.** The prompt fixes `r_tx = 50 m` but
not a radio configuration. I swept TX power and measured PER against distance,
then chose −8 dBm because it makes 50 m a *reliable* hop: measured PER(50 m) =
0.005, PER(55) = 0.09, PER(60) = 0.55, PER(65) = 0.98. So the reliable range is
≈ 52 m and the 50 % point ≈ 59 m. **Had I instead put the 50 % point at 50 m, hops
at the nominal range would be half-lossy and `h_max` would be meaningless.** The
full curve is in the report; if the group wants `r_tx` defined as the 50 % point
instead, the numbers shift and the calibration must be redone.

**A2 — the dissemination protocol is mine.** The prompt specifies "epidemic
rebroadcast, advertisement of held fragments, Trickle-style suppression as a
sweepable flag". Everything else — advertisement interval, the priority rule, the
1 s duplicate-push suppression window, pushing one fragment per advertisement —
I chose. `T_hop` is therefore protocol-dependent and is reported as a function of
the advertisement interval for that reason. **What is protocol-independent is the
`k/λ` floor**, and the measurement says that floor, not contention, is what sets
the answer. That is the load-bearing claim and it does not depend on A2.

**A3 — seeding draws each fragment with probability 0.5 per corridor node**, then
repairs so the corridor collectively holds all `k`. The prompt says "a random
subset ... drawn so the corridor collectively holds all k" without fixing the
distribution. A denser or sparser draw changes how much work the spread has to do.
The seeded fraction is reported per configuration so the reader can see it (it is
a large fraction at small R, because a ±50 m corridor through a small cell covers
most of it — which is a property of the specified geometry, not a choice).

**A4 — Phase 0 is a hex-tiling stand-in, not PECEE.** Cluster heads are the node
nearest each occupied cell centre. PECEE is not available in this environment.
This moves individual stops but not the `1/R` scaling of `T₁`.

**A5 — composition CI treats the two terms as independent** because they come
from disjoint seed sets (A6 scenarios and B4 runs are separate draws). If flight
geometry and ground density were correlated in a deployment, the interval is wrong.

**A6 — 8 headings, chosen on tuning seeds 0–19 and never on reporting seeds.**
Within 0.9 % of 12 headings at 2.2× less cost; 4 headings is 2.4–9.3 % off. Per
§8, no parameter was tuned on reported seeds.

## 4. Divergences from the prompt

| # | prompt | actual | why |
|---|---|---|---|
| D1 | §3 sweep: R(7) × k(3) × spacing(3) × Trickle(2) = 126 configs | **45 configs** | the full factorial is ≈ 20 CPU-hours. **N = 120 seeds per configuration was held fixed — the factorial was cut, never N.** Kept: the whole R × k grid, spacing at three R, Trickle on/off at every R, plus an advertisement-interval axis the prompt did not ask for. |
| D2 | §5 "Dubins tour at a minimum of four R values" | five: 60, 94, 150, 250, 400 m | 60 and 400 are needed to answer the kinematic-bound question and to reach the top of the operating range |
| D3 | §2 `cd ~ && git clone … ns3-dev` | shallow clone at tag `ns-3.46` | identical tree, records the same commit SHA (`ea50b72a`), far less disk |
| D4 | §5 `η` swept for the Dubins arm | η ∈ {0, 0.5, 1} at three R; η = 0 at all five | cost; η enters the flight side only through the occupied-cell count, which the BHH arm covers at every R |
| D5 | §6 composition | reported for **both** BHH and realised-Dubins `T₁` | the realised tour is ~1.7× the estimate; reporting only BHH would flatter the conclusion, so both are shown and the BHH figure is flagged as the conservative one |

No divergence on the things the prompt marks as hard constraints: one
`LrWpanHelper` kept alive for the whole simulation (heap-allocated, never freed,
with the `GetNDevices() != 0` check asserted at setup), 64 B payload against the
100 B ceiling, ≥ 200 ms `Send()` spacing enforced by the transmit tick, every
`Send()` return value checked (`send_fail` is reported and is 0 throughout), RX
callbacks set once per device before `Simulator::Run()`, compact binary control
packets, and `A/((3√3/2)R²)` never `A/(πR²)`.

## 5. Things I am unsure about

1. **`T_hop` at R = 60 m is an artifact and I excluded it from fits.** `h_max(60)
   = 0.2`, so `T_hop = 5 × T_spread` there and its CI is inflated by the same
   factor. The exclusion was pre-registered, not chosen after seeing it, but it is
   still a judgement call: it is the one point that could be argued either way.
2. **`h_max(R) = (R − r_bc)/r_tx` is a continuous hop count.** It is fractional
   below R = 100 m, which is geometrically odd. I used the prompt's definition
   unchanged rather than rounding, because rounding would create steps that are
   harder to read than the fraction.
3. **`T_spread` is full-cell completion.** Crossing times for 50/90/95/99 % are
   recorded per run so a partial criterion can be applied later, but every headline
   number uses 100 %. A 95 % criterion would give a smaller and less variable
   `T_hop`, and would push `R*` further out still.
4. **Contention is present but not dominant, and I should say how I know.** MAC
   TX drops rise monotonically with node count and with Trickle disabled, and six
   MAC/PHY trace sources are connected and counted (`traces_connected = 6` in every
   row). PHY RX drops are large but mostly out-of-range receptions, so that counter
   is *not* a contention measure and is not used as one.
5. **LKH is heuristic.** It matches exhaustive enumeration on 3- and 4-cluster
   instances to 0.2 %, but at C = 120 I have no optimality certificate, only
   `RUNS = 1`. Tour lengths at small R may be slightly pessimistic.
6. **The two open questions in §9 of the prompt are untouched** and are recorded in
   `STATUS.md`: whether each node matches its own data or the CH matches for the
   cluster, and whether the declared dose is uniform across nodes. Neither affects
   this probe's measurement, but the second would change the coverage problem into
   set-cover with non-uniform demands.
7. **My previous commit message undercounted the test suite** as 158 when the
   actual figure was 267 (parametrized tests expand). I did not amend the
   pre-registration commit to fix it, deliberately, so that nobody has to wonder
   whether that commit was touched after the sweeps were read. The correction is
   recorded here and in `STATUS.md`.
