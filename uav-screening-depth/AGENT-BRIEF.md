# Agent Brief — Experimental Campaign for the "Screening Depth" Paper

**Audience:** a cloud-based coding agent with no prior knowledge of this project.
**Status of this document:** it is the contract. If anything you build disagrees with this file, this file wins. If this file is wrong, say so in writing before you code around it.

---

## 0. How to use this document

Read §1–§6 completely before writing a single line of code. They contain the model, the corrections, and the data contracts. §7 is the work queue. §8–§13 are the process rules — they are not optional and they are not boilerplate; each one was paid for with lost time on a previous campaign in this group.

Your first action is **E0**. E0 is a GO/NO-GO gate. If E0 fails, you stop and report. You do not proceed to E1 "to make progress while we discuss it".

---

## 1. Mission

We are writing a 6-page IEEE paper. The paper asks one question:

> A UAV flies over a large pre-deployed sensor network and broadcasts a *signature set* of `k` files. Ground clusters use those files to screen their own raw data and flag themselves as suspicious. The UAV then flies again to verify only the flagged clusters. **How large should `k` be?**

Small `k` → screening is cheap but coarse → too many clusters flagged → verification explodes.
Large `k` → screening is precise but the dissemination flight itself is slow.

The paper's central claim is that total time-to-confirmation is **quasiconvex in `k`**, so a unique interior optimum `k*` exists, and that `k*` grows like `log C` in the number of clusters `C`.

**Your job is to produce the measurements that either support or refute that claim.** You are not here to make the claim true. A campaign that cleanly refutes it is a successful campaign; a campaign that supports it with weak statistics is a failed one.

---

## 2. The model, stated from scratch

### 2.1 Three phases

| Phase | What happens | Cost symbol |
|---|---|---|
| **Phase 0** — Grid construction | The network partitions itself into clusters of bounded size and elects a cluster head (CH) per cluster. Produces a set of CH positions with transmission radii. | not timed in the objective; sets up the geometry |
| **Phase 1** — Dissemination / screening | The UAV flies a trajectory and broadcasts `k` signature files round-robin. Each CH accumulates fragments, then matches them against its own raw data and emits a suspicion score over a low-rate long-range feedback channel. | `T₁(k)` |
| **Phase 2** — Verification | The UAV visits flagged clusters in order of decreasing suspicion score to confirm. | `T₂(k)` |

### 2.2 Objective

```
T_total(k)  =  T₁(k)  +  r(k)·T₂(k)  +  (1 − r(k))·T_miss
```

- `r(k)` — true accept rate (the target's cluster is actually flagged). Increasing, concave, saturating. Same quantity as **TAR** in set-based face-recognition benchmarks.
- `f(k)` — false alarm rate. Decreasing, convex. Same quantity as **FAR**.
- `N(k)` — number of clusters flagged `= r(k) + f(k)·(C − 1)` where `C` is the number of clusters.
- `T_miss` — cost of a full re-sweep when the target is missed. A large constant.

### 2.3 Phase-1 constraint and the dose reduction

The physical requirement is a **chance constraint**: each CH must end the flight holding enough of the signature set, with confidence `C_conf`.

Because the UAV broadcasts round-robin over a fixed schedule, the reception events for different files use disjoint transmission slots and are therefore independent. This collapses the whole trajectory into one scalar per CH:

```
D_n  =  λ · ∫₀ᵀ  κ( p_n( ‖x(t) − x_n‖ ) )  dt        ≥   θ(k, C_conf)
```

- `λ` — transmission opportunity rate, in opportunities per second. **This factor is mandatory.** `∫ p dt` alone has units of seconds; `θ` is a count. A constraint that omits `λ` is dimensionally wrong.
- `κ(·)` — the **integral kernel**. See §3.1. It is **not** the identity.
- `p_n(d)` — per-opportunity success probability at distance `d` (the PER model).
- `θ(k, C_conf)` — required dose, in opportunities. Closed form in §3.2.

This turns Phase 1 into a **sweep-coverage problem with a per-node dose demand**, which is what the algorithm in §7-E4/E5 attacks.

### 2.4 Vehicle

Fixed-wing, therefore a **Dubins vehicle**: constant speed `v`, no reverse, minimum turning radius `ρ`. State is `(x, y, ψ)` — position *and heading*. Shortest path between two states is one of six types (RSR, RSL, LSR, LSL, RLR, LRL).

```
ρ = v² / (g · tan φ)          φ = bank angle
```

| `v` | `φ = 20°` | `φ = 30°` | `φ = 45°` |
|---|---|---|---|
| 15 m/s | 63.0 m | 39.7 m | 22.9 m |
| **20 m/s** | 112.0 m | **70.6 m** | 40.8 m |
| 25 m/s | 175.0 m | 110.3 m | 63.7 m |

Default operating point: `v = 20 m/s`, `φ = 30°`, **`ρ = 70.6 m`**.

---

## 3. Known model corrections — read before coding

These four items are **already-identified defects in the group's own design document**. They are not open questions for you to rediscover; they are instructions. Implement the corrected form and note the correction in your code comments.

### 3.1 The integral kernel is `|ln(1 − p)|`, not `p`

The design document writes the dose constraint as `∫ p_n(t) dt ≥ θ`. That is the small-`p` linearisation, not the exact quantity.

Along the path, the probability of missing a given file entirely is `exp( −(λ/k) ∫ |ln(1 − p_n(t))| dt )`. The additive quantity is therefore `|ln(1 − p)|`:

```
κ(p) = −ln(1 − p)
```

Error from using `p` instead:

| `p` | `p` | `\|ln(1−p)\|` | error |
|---|---|---|---|
| 0.05 | 0.050 | 0.051 | +2.6 % |
| 0.10 | 0.100 | 0.105 | +5.4 % |
| 0.20 | 0.200 | 0.223 | **+11.6 %** |
| 0.30 | 0.300 | 0.357 | **+18.9 %** |
| 0.50 | 0.500 | 0.693 | **+38.6 %** |

`p` is largest close to the UAV, which is exactly where the error is worst — so the linearised model systematically **understates** the contribution of the segments that matter most. Use `κ(p) = −ln(1 − p)`. It is exactly additive, so this is a strict improvement with no algorithmic cost.

Implement `κ` as a single function `dose_kernel(p)` used everywhere. Expose `--kernel={log,linear}` so the linearised variant can be measured as an ablation — the size of that gap is itself a reportable result.

### 3.2 Two dose regimes — implement both, default to `m-of-k`

**Regime A, "collect all k".** Every CH must hold all `k` files.

```
θ_A(k, C_conf) = k · ln(1 − C_conf^(1/k)) / ln(1 − p)
               ≈ k · [ ln k − ln|ln C_conf| ] / |ln(1 − p)|        (the k·ln k form)
```

**Regime B, "collect m of k".** The confidence model used by the group's prior ICCE work is a noisy-OR over fragments with equal contributions, so a node crosses threshold from a **subset** of `m < k` fragments. The correct constraint is

```
P( Bin(k, q_n) ≥ m ) ≥ C_conf ,        q_n = 1 − (1 − p)^(D_n / k)
```

**This distinction is not cosmetic. It decides whether the paper's headline `k ln k` proposition exists at all.** Measured, `p = 0.3`, `C_conf = 0.95`:

| requirement, `k = 10` | `θ` (opportunities) | vs all-k |
|---|---|---|
| all 10 | **147.9** | — |
| 7 of 10 | 53.2 | 2.8× cheaper |
| 5 of 10 | 33.4 | 4.4× cheaper |
| 3 of 10 | 19.8 | **7.5× cheaper** |
| 2 of 10 | 14.1 | **10.5× cheaper** |

And with `m` held fixed while `k` grows, `θ` is **essentially flat**:

| `m` | `k=4` | `k=6` | `k=10` | `k=16` | `k=25` | `k=40` |
|---|---|---|---|---|---|---|
| 2 | 15.6 | 14.7 | 14.1 | 13.7 | 13.6 | 13.5 |
| 3 | 26.1 | 21.9 | 19.8 | 18.9 | 18.4 | 18.1 |
| 4 | 48.9 | 31.6 | 26.2 | 24.2 | 23.2 | 22.6 |

⇒ **the `ln k` factor exists only in Regime A.** E0 and E7 must measure and report this explicitly.

**Feasibility check that makes this concrete.** At `λ = 5 opportunities/s` (the LR-WPAN ceiling, §A.3), `p = 0.3`, a 50 m broadcast radius and `v = 20 m/s`, one straight pass over a CH gives ≈ 5 s in range:

| regime | `θ` | in-range time needed | passes over each CH |
|---|---|---|---|
| all 10 | 147.9 | 29.6 s | **5.9** |
| 5 of 10 | 33.4 | 6.7 s | 1.3 |
| 3 of 10 | 19.8 | 4.0 s | **0.8** |

Regime A requires flying over every cluster roughly six times. Report this in E0. If it holds, Regime A is not merely more expensive — it may be operationally infeasible, and the paper must say so rather than quietly assuming it.

### 3.3 The greedy guarantee is Wolsey's `1 + ln(·)`, not `1 − 1/e`

The design document claims a `(1 − 1/e)` guarantee for the dose-coverage step. That bound is for **submodular maximisation under a cardinality constraint**. Our step is stated as **covering**: choose locations so that *every* CH reaches `θ`. The correct reference is **Wolsey 1982, submodular set cover**:

```
|S_greedy|  ≤  |S*| · ( 1 + ln( max_j f({j}) ) )
```

— a logarithmic factor, not a constant.

Verified numerically: on 3 851 random dose-cover instances (6 nodes × 9 locations) with brute-forced optima, greedy/OPT averaged 1.031 with a **maximum of 1.667**, which exceeds `1/(1−1/e) = 1.582`. The `1 − 1/e` claim is falsifiable at instance sizes small enough to brute-force, and you must include that check as a unit test (§7-E4).

The submodularity itself is fine: `f(S) = Σ_n min(D_n(S), θ)` is a truncated sum of a modular function, hence monotone submodular — verified, 0 violations in 3 000 random diminishing-returns checks. Keep that as a property test.

**Note also:** dwell time is continuous. A submodular *set* function needs a discrete ground set. Discretise dwell into unit slots so the ground set is `(location × slot)`, and state the slot granularity in the config.

### 3.4 There is no end-to-end approximation guarantee — do not report one

Even with Wolsey's bound corrected, it bounds `|S|`, while the paper's objective is **flight time**. Dubins tour length is not monotone in `|S|`. And the constant-factor DTSPN result (Isaacs & Hespanha) requires **disjoint** neighborhoods, whereas our transmission-location footprints overlap heavily by construction.

Report the step-local bound as a step-local bound. Any sentence of the form "our algorithm has a theoretical guarantee on mission time" is false and must not appear in any output you generate.

---

## 4. Environment

You have **ns-3** and **PECEE** available.

```bash
# ns-3 build (the established incantation for this group)
cd /home/user/ns3-dev
/usr/bin/cmake --build cmake-cache -j 3
```

- **Python 3.10 is required.** Python 3.14+ breaks ns-3's argparse. Check the interpreter version before any build and fail loudly if it is wrong.
- Python-side work uses `python3.10`. Do not assume `python3` points at it.
- `shapely` for geometry, `numpy`/`scipy` for numerics, **LKH** for the ATSP solver. If LKH is not present, install it and record the version in `env.txt`.
- ns-3 module work is confined to the module you create. **Do not modify `src/wsn/`, other ns-3 modules, or root files.**

Record the full environment (`python --version`, `cmake --version`, ns-3 commit, LKH version, CPU count) into `results/env.txt` at the start of every campaign, and copy it into each run directory.

---

## 5. Repository

Create a **new, standalone repository**: `uav-screening-depth`. Do not put this work inside the existing `wsn-uav` repo.

```
uav-screening-depth/
├── README.md                  # 20 lines: what this is, how to reproduce Fig 1
├── AGENT-BRIEF.md             # a copy of this file
├── STATUS.md                  # YOU MAINTAIN THIS. See §11.
├── env.txt
├── pyproject.toml
├── config/
│   ├── default.yaml           # every parameter, with units, no magic numbers in code
│   ├── channel-synthetic.yaml
│   └── channel-ns3.yaml       # produced by E3
├── src/screening/
│   ├── model.py               # theta(), dose_kernel(), T_total(), r(k), f(k)
│   ├── scenario.py            # E1: non-convex region + node generation
│   ├── phase0.py              # E2: clustering + CH election adapter (PECEE)
│   ├── channel.py             # PER model; loads from config, never hardcoded
│   ├── cover.py               # E4: discretisation + submodular greedy
│   ├── tour.py                # E5: heading sampling -> GTSP -> ATSP -> Dubins
│   ├── refine.py              # E5: iterative refinement loop
│   ├── baselines.py           # E6
│   └── metrics.py             # every number the paper quotes, computed in one place
├── ns3/                       # the ns-3 module for E3, E7
├── tools/
│   ├── run_campaign.py
│   ├── campaign_stats.py      # paired tests, CIs, --selftest
│   ├── make_report.py         # E-anything -> self-contained HTML
│   └── assert_one_build.py
├── tests/
├── results/                   # gitignored except manifests and figure CSVs
└── report/                    # generated HTML, committed
```

---

## 6. Data contracts

These schemas are how results reach the paper. **Freeze them before E1.** If a schema must change, bump `schema_version`, write a migration note in `STATUS.md`, and re-run everything that depends on it — do not silently mix versions.

### 6.1 Run directory

Every single simulation run writes exactly this:

```
results/<experiment>/run-<NNNNN>/
├── config.txt        # every resolved parameter + build provenance (see 6.5)
├── metrics.csv       # ONE row — the run's summary
├── nodes.csv         # node/CH geometry as actually realised
├── trajectory.csv    # the flown path
├── dose.csv          # per-CH delivered dose
└── events.jsonl      # append-only event log (optional for pure-Python runs)
```

### 6.2 `metrics.csv` — one row per run

| column | type | units | meaning |
|---|---|---|---|
| `schema_version` | int | — | start at 1 |
| `run_id` | str | — | `<experiment>/run-NNNNN` |
| `seed` | int | — | |
| `scheme` | str | — | `proposed \| boustrophedon \| alternating \| greedy-nodubins \| zeng-sca` |
| `k` | int | — | signature set size |
| `m` | int | — | fragments needed; `m == k` ⇒ Regime A |
| `regime` | str | — | `all-k \| m-of-k` |
| `kernel` | str | — | `log \| linear` |
| `C_clusters` | int | — | number of clusters |
| `R_cluster_m` | float | m | cluster radius parameter |
| `rho_m` | float | m | Dubins turning radius |
| `v_mps` | float | m/s | |
| `lambda_ops` | float | 1/s | transmission opportunity rate |
| `theta_required` | float | ops | `θ(k, C_conf)` |
| `T1_s` | float | s | Phase-1 flight time |
| `T2_s` | float | s | Phase-2 verification time |
| `T_total_s` | float | s | objective |
| `tour_len_m` | float | m | Phase-1 Dubins tour length |
| `n_locations` | int | — | `\|S\|` selected by the cover step |
| `n_refine_iters` | int | — | Step-4 iterations to convergence |
| `dose_min_ratio` | float | — | `min_n D_n / θ` — **must be ≥ 1.0 or the run is infeasible** |
| `dose_transit_frac` | float | — | fraction of total delivered dose accrued off the selected locations |
| `r_k` | float | — | realised true-accept rate |
| `f_k` | float | — | realised false-alarm rate |
| `N_flagged` | int | — | clusters flagged |
| `feasible` | int | 0/1 | 1 iff every CH reached `θ` |
| `wall_s` | float | s | solver wall time |

**Rule:** if `feasible == 0`, the run still gets written. It is not discarded. Infeasible runs are a result.

### 6.3 `nodes.csv`

`node_id, x_m, y_m, is_ch, cluster_id, r_tx_m, theta_required, dose_delivered, dose_ratio`

### 6.4 `trajectory.csv`

`t_s, x_m, y_m, psi_rad, v_mps, segment_type, transmitting`
where `segment_type ∈ {L, S, R}` (the Dubins primitive) and `transmitting ∈ {0,1}`.

### 6.5 `config.txt` — build provenance is mandatory

Key=value lines, one per parameter, plus:

```
git_commit=<sha>
git_dirty=<0|1>
binary_mtime=<...>
binary_size=<...>
schema_version=1
```

`binary_mtime,binary_size` come from the actual executable (`/proc/self/exe` for ns-3 runs). This catches the case where behaviour changes without the metrics source recompiling. `tools/assert_one_build.py` refuses to aggregate a result set whose runs carry different provenance stamps. **Wire this into every aggregation path.**

### 6.6 Figure data — one CSV per paper figure

`results/figures/H1.csv` … `H5.csv`. Long format, one row per plotted point, with a `series` column. The figure CSV is the paper's citable artifact; the plot is a rendering of it. Never plot from an in-memory object that was not written to disk first.

---

## 7. Work queue

Each item states **Goal / Input / Output / Acceptance**. Do not start an item until its predecessors' acceptance criteria are met and committed.

---

### E0 — Numerical feasibility of `k*`  ·  **GO / NO-GO GATE**

**Goal.** Before writing any simulator, determine by direct numerical evaluation whether `T_total(k)` even has an interior minimum, under parameterised `r(k)` and `f(k)`.

**Input.** `config/default.yaml`. Three families each for `r(k)` and `f(k)` (e.g. `r` saturating-exponential / logistic / power-law; `f` exponential-decay / power-law / logistic), each with a stated parameter range.

**Output.**
- `results/E0/sweep.csv` — grid over `(k, family_r, family_f, regime, R_cluster)` with `T₁, T₂, T_total, k_star, interior`.
- `report/E0.html` — see §9.
- A one-paragraph verdict in `STATUS.md`.

**Acceptance.**
1. Report the **fraction of the parameter grid for which `k*` is interior**, per regime, not just the default point.
2. Report the feasibility table of §3.2 (passes-per-CH) for both regimes at the default operating point.
3. Report whether the `ln k` factor survives under Regime B, using the table in §3.2 as the expected result.
4. **STOP CONDITION.** If `k*` is at a boundary for more than half the parameter grid in *both* regimes, halt. Write the finding, open an issue, and do not start E1. That outcome means the paper's premise needs redesign, and discovering it in week 1 instead of week 8 is the single most valuable thing you can do.

---

### E1 — Scenario generator

**Goal.** Reproducible non-convex deployment scenarios.

**Input.** Seed, region spec (outer polygon + holes), node count, a **heterogeneity parameter** `h ∈ [0,1]` controlling how non-uniform node density is (`h = 0` uniform, `h = 1` strongly clustered).

**Output.** `nodes.csv` + region polygon as GeoJSON; deterministic given the seed.

**Acceptance.** Same seed ⇒ byte-identical output. A seed sweep shows node density Gini coefficient increasing monotonically in `h`. `h` is a first-class experimental axis — see E10.

---

### E2 — Phase 0 via PECEE

**Goal.** Produce the CH set and transmission radii the routing stage consumes.

**Input.** E1 output; cluster radius `R`; PECEE parameters.

**Output.** Per-scenario CH set with `r_tx`, plus a measured `T_local(R)` curve (intra-cluster dissemination time vs `R`).

**Acceptance.** Cluster size bound is respected. `T_local(R)` is measured, not assumed. Report the number of clusters `C` as a function of `R` and compare against `A / ((3√3/2)·R²)` for a hexagonal packing — **note that `A / (π R²)` is wrong by 21 % and appears in earlier drafts.**

---

### E3 — Channel measurement in ns-3

**Goal.** An empirical `p(d)` for the air-to-ground link, and effective radius vs speed `R_eff(v)`.

**Input.** ns-3 LR-WPAN A2G setup at the default geometry (§A).

**Output.** `config/channel-ns3.yaml` conforming to the same schema as `channel-synthetic.yaml`, so downstream code switches with one config line and zero code changes.

**Acceptance.** `p(d)` measured over the full distance range at `N ≥ 120` seeds per distance bin, with CIs. The effective `λ` is measured, not assumed from the 200 ms figure. Any deviation from `λ = 5 /s` is reported.

---

### E4 — Discretisation + submodular greedy dose cover

**Goal.** Given CHs, doses and `θ`, select transmission locations and dwell slots.

**Input.** E2 CH set, E3 channel, `θ` from `model.py`.

**Output.** Selected `(location, slot)` set; `dose.csv`; solver wall time.

**Acceptance — four tests, all in `tests/`:**
1. **Submodularity property test.** Random instances; assert `f(A∪{j}) − f(A) ≥ f(B∪{j}) − f(B)` for `A ⊆ B`. Expect zero violations.
2. **Wolsey-vs-`1−1/e` test.** Brute-force optima on small instances (≤ 10 locations); assert that the observed max ratio is reported, and assert **explicitly** that instances exceeding 1.582 exist. This test exists to prevent the `1 − 1/e` claim from re-entering the paper.
3. Non-convex regions with holes produce no selected location inside a hole.
4. Every CH ends with `dose_ratio ≥ 1` or the instance is reported infeasible with a reason.

---

### E5 — Dubins tour + iterative refinement

**Goal.** Order the selected locations into a kinematically feasible tour; then feed transit dose back.

**Input.** E4 locations, `ρ`, `v`.

**Output.** `trajectory.csv`, `T₁(k)`, `n_refine_iters`, `dose_transit_frac`.

**Acceptance.**
1. Heading sampling → GTSP → Noon–Bean → ATSP → LKH. Record the heading discretisation level and show a sensitivity curve of `T₁` vs heading resolution.
2. Curvature check: assert `|κ(t)| ≤ 1/ρ` everywhere along the realised path, to numerical tolerance. A tour that violates this is not a result.
3. **`dose_transit_frac` is a headline number.** It quantifies how much dose the two-stage plan ignores. Report it prominently.
4. Refinement must be shown to **converge**: assert total dwell is non-increasing across iterations and bounded below. Report the iteration count distribution. Do not write "converges quickly" anywhere — report the distribution.

---

### E6 — Baselines

Four arms, not three:

| arm | description | why it matters |
|---|---|---|
| `boustrophedon` | lawnmower sweep, **with spacing and speed tuned** so `∫κ dt = θ` | **The dangerous baseline.** For uniform CH density and uniform `θ` this is probably near-optimal. Do not ship a fixed-speed straw man. |
| `alternating` | Savla's Alternating Algorithm over the selected locations | has a bound relative to the Euclidean tour |
| `greedy-nodubins` | E4 selection, Euclidean ordering, Dubins path appended | isolates the value of the DTSPN step |
| `zeng-sca` | Zeng, Xu & Zhang 2018 — SCA trajectory ignoring curvature, then post-processed to Dubins | **Mandatory.** The paper claims four differences from Zeng 2018. Claiming them without running Zeng is not defensible. |

**Acceptance.** All four run on identical scenarios and seeds. Paired comparison, `N ≥ 120`.

> **Expect the lawnmower to win at `h = 0`.** That is the correct outcome and it is not a failure — it locates the method's actual value proposition in heterogeneity. See E10.

---

### E7 — Validate `θ` against packet-level simulation

**Goal.** Does the analytical `θ` predict the dose actually delivered in ns-3?

**Input.** E3 channel, E5 trajectory, ns-3 packet-level run.

**Output.** Measured `θ` curve vs both analytical regimes; the predicted-vs-measured scatter.

**Acceptance.**
1. Sweep `k` in Regime A and confirm or refute the `k ln k` scaling.
2. Sweep `k` **with `m` fixed** in Regime B and confirm or refute that `θ` is flat in `k`. The expected values are in §3.2 — a mismatch means either the model or the implementation is wrong, and you must find out which before proceeding.
3. Run both `--kernel=log` and `--kernel=linear`; report the gap. This measures §3.1.

---

### E8 — `T_total(k)` sweep → **Figure H1**

Sweep `k`; produce four curves against `k`: `T₁` rising, verification cost falling, miss cost falling, and `T_total` U-shaped with its minimum at `k*`. `N ≥ 120` seeds per `k`. CIs on every point.

---

### E9 — `k*` vs `ln C` → **Figure H2**

Sweep the number of clusters `C` over at least a decade. Plot `k*` against `ln C`. Fit a line; report slope, intercept, `R²`, and the CI on the slope. **If it is not a straight line, report that it is not a straight line.**

---

### E10 — Sensitivity → **Figures H4, H5**

- **H4:** `k*` vs `R_cluster`, and `k*` across the three `r`/`f` function families from E0. Establishes robustness.
- **H5 — new, and it decides whether the method has a reason to exist:** win margin of `proposed` over the tuned lawnmower **as a function of heterogeneity `h`**. If that curve is flat, the sophisticated pipeline buys nothing and the paper must say so.

---

## 8. Statistics rules

These are not negotiable. Each was learned at cost on a previous campaign in this group.

- **`N = 20` is not enough for anything.** On the prior campaign it missed a real 3.3 % failure mode and understated a delivery error by 42 %. Rates and error distributions need **`N ≥ 120`**.
- **A single seed will lie to you.** It happened twice on the prior campaign: a change looked excellent on seed 1 and was a disaster at `N = 120`. Never draw a conclusion from a single run, not even a "quick check".
- **Never rebuild while a campaign is running.** It silently mixes binaries inside one result set. `assert_one_build.py` exists to catch this; do not bypass it.
- **Assert on every scripted source edit.** A `str.replace` that matched nothing once meant a feature never ran while its results were attributed to it. Verify behaviour in the event log, not in the diff.
- **State mechanisms only after measuring them.** On the prior campaign three plausible explanations were asserted without measurement and all three were wrong.
- **Paired comparisons, on identical seeds.** Report paired win counts, Cliff's δ, and a p-value — not just means. A mean difference without a win count hides bimodality.
- **Cost metrics are intention-to-treat.** Do not condition cost on success; that is survivorship bias and it always flatters us.
- **Report CIs on everything.** Wilson intervals for rates, bootstrap for medians and quantiles.
- `campaign_stats.py --selftest` must exist and must pass, validating the statistics code against instances with known answers.

---

## 9. HTML reporting

Every experiment produces a **self-contained HTML report**, generated by `tools/make_report.py`, committed under `report/`.

**Requirements.**
- One file per experiment: `report/E0.html` … `report/E10.html`, plus `report/index.html` as the dashboard.
- **Self-contained**: inline all CSS and JS, images as `data:` URIs. It must open correctly from `file://` with no network. Do not rely on a CDN.
- Every report carries a header block: git SHA, generation timestamp, `N` seeds, config hash, and a **trust banner** — `CURRENT` / `STALE` / `VOID`. When a change invalidates a result, you mark the banner; you do not silently delete the page.
- Every chart is accompanied by the **CSV it was plotted from**, linked and committed.
- `report/index.html` shows: the work queue with per-item status, the latest headline numbers, current open problems, and a link to each experiment page.

**Progress reporting cadence.** Regenerate `report/index.html` at the end of every work session and at every commit that changes a result. The HTML dashboard is the primary progress artifact — not chat messages, not a text log.

**Replay viewer.** For E5, also produce an interactive trajectory viewer: the region, CH positions coloured by `dose_ratio`, the flown path coloured by curvature (red where `κ·ρ > 1` — there should be none), and a slider over refinement iterations.

---

## 10. Git discipline

- **Never commit unless the state is one you would defend.** Working tree must be clean, tests green, and the relevant HTML report regenerated.
- One logical change per commit. Commit message states *why*, not *what*.
- Commit message format:
  ```
  <area>: <why this change exists>

  - what changed, one line per file that matters
  - measurement that justifies it, or "no measurement yet"
  Tests: <pass/fail summary>
  Report: <which HTML pages regenerated>
  ```
- **Results are committed as manifests and figure CSVs, not raw run directories.** Raw runs are gitignored; `results/figures/*.csv` and `results/*/manifest.csv` are committed.
- Tag the commit that produced each paper figure: `fig-H1`, `fig-H2`, … The paper cites the tag.
- Branch per experiment: `exp/E4-dose-cover`. Merge only after the review loop in §11 closes.

---

## 11. The implement / review loop

**Implementation is done by the coding agent (Opus 5). Review is done by a separate reviewer (Codex).** The reviewer has not seen the implementation reasoning and must not be given it — that is the point.

**Per work item:**

1. **Implement** on `exp/EN-*`. Write tests first where the acceptance criteria are testable.
2. **Self-audit before requesting review.** Produce `docs/AUDIT-EN.md` containing:
   - every assumption you made that is not in this brief;
   - every place where the implementation diverges from §2–§3, with justification;
   - every number in the HTML report and the line of code that computes it;
   - anything you are unsure about, stated plainly.
3. **Request review.** The reviewer checks: correctness against §2–§3, the four corrections in §3 specifically, statistics against §8, the data contracts in §6, and whether any output claims more than the data supports.
4. **Findings are tiered.** *Tier 0* — wrong number, wrong math, or an unsupported claim in an output. *Tier 1* — correct but fragile. *Tier 2* — style. **All Tier 0 must be closed before merge.** Tier 1 goes into `STATUS.md` open problems.
5. **Merge, tag, regenerate `report/index.html`, update `STATUS.md`.**

**`STATUS.md` is yours to maintain and it is the single source of current truth.** It must always contain: what is true right now, which numbers are stale or void and why, the ranked open problems, and what to do next. A newcomer reading only `STATUS.md` must be able to continue the work. Update it at the end of every session — not at the end of the project.

**Re-audit trigger.** Any time a result changes by more than 10 %, or any time a default flips, re-audit the affected experiment even if nobody asked.

---

## 12. Stop and escalate

Halt and write up rather than working around, if any of these occur:

| trigger | why it matters |
|---|---|
| **E0 fails** (`k*` on the boundary across most of the grid) | the paper's premise does not hold |
| Regime A turns out infeasible at the operating point (§3.2) | changes what the paper can assume |
| `θ` measured in E7 disagrees with theory by more than the CI | model or implementation is wrong; both are serious |
| the tuned lawnmower beats `proposed` even at high `h` | the method has no value proposition |
| `zeng-sca` matches or beats `proposed` | the four claimed differences do not translate into performance |
| the refinement loop does not converge | Step 4 is unsound as specified |
| you find yourself needing to exclude runs to make a result | stop; that is the beginning of a retraction |

In every case: write the finding into `STATUS.md`, generate the HTML page showing it, commit, and report. A clean negative result delivered early is worth more than a positive result delivered late.

---

## 13. Anti-patterns — do not do these

- Do not write a claim about a mechanism you have not measured.
- Do not report `1 − 1/e`, or any end-to-end approximation guarantee on mission time. See §3.3, §3.4.
- Do not use `∫ p dt` as the dose. See §3.1.
- Do not omit `λ`. The constraint must be dimensionally consistent.
- Do not default to Regime A silently. The regime is an explicit, logged parameter.
- Do not tune a parameter on the same seeds you report results from. Hold out a tuning seed set.
- Do not hardcode a parameter in code. Everything lives in `config/`, with units.
- Do not delete or overwrite a result because it became stale. Mark it `STALE`/`VOID` and keep it.
- Do not present a mean without a paired win count and a CI.
- Do not reformat or refactor code you were not asked to touch.
- Do not commit a red test.
- Do not skip E0.

---

## Appendix A — Default parameters

### A.1 Geometry and vehicle

| parameter | default | note |
|---|---|---|
| node lattice spacing | 20.0 m | from the group's prior work |
| UAV altitude | 20.0 m | |
| UAV speed `v` | 20.0 m/s | fixed-wing |
| bank angle `φ` | 30° | |
| **turning radius `ρ`** | **70.6 m** | derived: `v²/(g tan φ)` |
| broadcast radius | 50.0 m | |
| cluster radius `R` | swept | 50–150 m; `R` is a parameter, `k` is the decision variable |

### A.2 Signature model

| parameter | default |
|---|---|
| `k` | swept, 2 … 40 |
| `m` | swept; `m = k` selects Regime A |
| `C_conf` | 0.95 |
| per-opportunity success `p` at reference distance | 0.3 |
| fragment evidence | `evidence_i = 1 − (1 − 0.90)^(pixelCount_i / totalPixels)`, pixel-stride interleaving over 416×416×3 — **match this exactly**, the group's ICCE baseline depends on it |

### A.3 Radio — hard constraints, do not exceed

- IEEE 802.15.4 PSDU is 127 B including MAC header and FCS. **Safe application payload ceiling is 100 B, not 127.** Measured: 125 B payload ⇒ `Send()` returns FAIL; 100 B ⇒ OK.
- **Back-to-back `Send()` calls need ≥ 200 ms spacing.** 50 ms is not enough — verified. This gives **`λ = 5 opportunities/s ≈ 4 kbps` effective**, and `λ` is therefore a hard physical ceiling, not a free parameter.
- Always check the `Send()` return value. A silent FAIL looks like nothing at all.
- Use **one** `LrWpanHelper` instance for all nodes, and **keep it alive for the whole simulation.** Its destructor calls `m_channel->Dispose()`, which empties the channel's PHY list — after that, TX still fires but no packet ever reaches any RX. Store it as a member, not a local. Fast check: `dev->GetChannel()->GetNDevices()` should be non-zero after setup.
- Set RX callbacks before `Simulator::Run()`, once per device.
- Control packets must use compact binary encoding. No JSON, no verbose strings.

### A.4 Statistics

| parameter | default |
|---|---|
| seeds per configuration | **120** |
| tuning seed set | disjoint, 20 seeds, never reported |
| CI method, rates | Wilson |
| CI method, medians/quantiles | bootstrap, 10 000 resamples |
| paired effect size | Cliff's δ |

---

## Appendix B — Notation

| symbol | meaning | units |
|---|---|---|
| `k` | signature set size — **the decision variable** | files |
| `m` | fragments needed to cross threshold; `m = k` ⇒ Regime A | files |
| `C` | number of clusters | — |
| `C_conf` | required per-CH confidence | — |
| `R` | cluster radius | m |
| `ρ` | Dubins minimum turning radius | m |
| `v` | UAV speed | m/s |
| `λ` | transmission opportunity rate | 1/s |
| `p_n(d)` | per-opportunity success probability at distance `d` | — |
| `κ(p)` | dose kernel, `−ln(1 − p)` | — |
| `D_n` | delivered dose at CH `n` | opportunities |
| `θ(k, C_conf)` | required dose | opportunities |
| `r(k)` | true accept rate ≡ TAR | — |
| `f(k)` | false alarm rate ≡ FAR | — |
| `T₁, T₂` | Phase-1, Phase-2 time | s |
| `T_miss` | re-sweep cost on a miss | s |
| `h` | deployment heterogeneity, 0 = uniform | — |

⚠ **Notation collision to avoid:** earlier drafts use `C` for both the cluster count and the confidence level, in two central formulas. This brief uses `C` for cluster count and `C_conf` for confidence. Keep them distinct in code and in every output.

---

## Appendix C — First session checklist

1. Read §1–§6 in full.
2. Create the repo and the layout in §5. Commit the skeleton.
3. Write `env.txt`. Verify Python 3.10 and the ns-3 build.
4. Implement `model.py`: `dose_kernel`, `theta_all_k`, `theta_m_of_k`, `T_total`. Unit-test against the tables in §3.1 and §3.2 — those are the expected values and they must reproduce.
5. Run **E0**. Generate `report/E0.html`. Write the verdict in `STATUS.md`.
6. Request review. Do not start E1 until E0's gate is passed and reviewed.
