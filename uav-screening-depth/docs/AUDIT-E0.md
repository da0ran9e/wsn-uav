# AUDIT-E0 — self-audit before review

Per AGENT-BRIEF §11.2. The reviewer has not seen the implementation reasoning;
this document is the only channel for it. Everything I am unsure about is stated
plainly rather than smoothed over.

Artifacts under audit: `src/screening/model.py`, `tools/run_e0.py`,
`tools/make_report.py`, `results/E0/*`, `report/E0.html`, `report/index.html`.
Tests: 108 passing (`python3.10 -m pytest tests/ -q`).

---

## 1. Assumptions I made that are NOT in the brief

### A1 — m is proportional to k, and α = m/k is set by the screening threshold
**This is the most consequential thing in E0 and it needs review first.**

The brief sweeps `m` but does not say how `m` should move as `k` grows. E0 shows
the answer decides whether the paper has a question at all (95% interior vs 0%),
so I derived it from Appendix A.2 rather than picking one.

A.2 fixes `evidence_i = 1 − (1−0.90)^(pixelCount_i/totalPixels)` with pixel-stride
interleaving. If the `k` files partition one payload, each carries pixel fraction
`1/k`, so noisy-OR over `m` received fragments gives

```
C = 1 − (1−0.90)^(m/k)
```

a function of the ratio `m/k` alone, hence `α = m/k = ln(1−thr)/ln(0.10)`.

- Implemented: `model.py:fragment_evidence`, `noisy_or_confidence`,
  `m_over_k_from_suspicion_threshold`.
- Tested: `test_model.py::test_fragment_evidence_matches_appendix_A2`,
  `test_noisy_or_depends_only_on_m_over_k`, `test_alpha_from_threshold_table`.
- **Where it could be wrong:** it assumes the `k` files *partition* a fixed
  payload, so per-fragment evidence shrinks as `k` grows. If instead each file is
  a full-strength independent signature (evidence per file independent of `k`),
  then `m` is fixed and **the premise collapses — 0% interior, `k*`=40 always.**
  Which of those two the physical system implements is a question for the group,
  not for me. I flagged it as open problem #1 on the dashboard.
- Note also a tension I did not resolve: the parent project's `CLAUDE.md`
  describes per-layer utilities `0.30/0.12/0.05/0.40` (unequal contributions),
  while A.2 specifies the equal-contribution pixel-stride form and says to match
  it exactly. I followed A.2 as instructed. If the layered model is the real one,
  A1 needs redoing.

### A2 — closed-form stand-ins for T₁ and T₂
The brief gives the objective but not `T₁(k)`/`T₂(k)`. I used:

- `T₁ = max(1, θ/(λ·t_pass)) · L_sweep/v`, `t_pass = 2R_b/v`, with
  `L_sweep = A/spacing + n_tracks·π·ρ` over a square region.
- `T₂ = [β√(N·A) + N·c_dubins·ρ]/v + N·dwell`, `β = 0.7124` (BHH).

Every coefficient is in `config/default.yaml` with units. `c_dubins = 1.0` is a
**stated modelling choice, not a bound** — §3.4 forbids presenting it as one.
The `max(1, ·)` floor encodes that the area must be covered once regardless of θ.
These are replaced by real tours in E5; E0's conclusions depend on them only
through the *shape* in `k`, which comes from θ(k), r(k), f(k).

### A3 — T_miss is swept, not fixed
The brief says "a large constant". A constant would have silently decided the
gate: at `T_miss` = 1 sweep low `k` always wins. I made it a grid axis —
`T_miss = mult · L_sweep/v`, `mult ∈ {1,3,10,30}` — so the reported fractions are
over that range, not at one point.

### A4 — fixed deployment area, so C follows from R
`A` is fixed and `C = A/(2.598R²)`, so sweeping `R` moves `C`. Physically
coherent, but it means E0's main grid **confounds R with C**. That is why `k*` vs
`ln C` is computed separately at fixed `R` with `A` varied, and labelled PREVIEW.

### A5 — provenance for a pure-Python experiment
§6.5 wants `binary_mtime`/`binary_size`. There is no binary, so I stamp
`src/screening/model.py` plus a `source_sha256` over all `src/` and `tools/`
`.py` files, condensed to a 16-char `prov_id` carried on every data row.
`assert_one_build.py` enforces a single stamp per aggregation. Same guarantee
(behaviour cannot change without the stamp changing), different mechanism.

### A6 — the continuous-m relaxation is mine
Used only as a diagnostic to separate the objective's shape from `m`'s
integrality, via `P(Bin(k,q) ≥ m) = I_q(m, k−m+1)` (exact at integer `m`).
Physical `m` is an integer and the relaxation is never reported as a cost.

---

## 2. Divergences from §2–§3, with justification

| # | brief | what I did | why |
|---|---|---|---|
| D1 | §3.2 "default to m-of-k" | `regime` is a **required** argument with no default; `theta()` raises if `m` is missing | §13 forbids defaulting to A silently; refusing to default at all is stronger than defaulting to B |
| D2 | §3.2 table for `m=4, k=4` | computed via `theta_all_k` (that cell *is* Regime A) | `m=k` reduces exactly to A; asserted for k ∈ {2..40} |
| D3 | E0 "three families each for r and f" | 3 families × 3 parameter sets each = 9 + 9 | the brief asks for "a stated parameter range"; 9 per side keeps the grid at 4,860 points |
| D4 | §6.2 `metrics.csv` | E0 writes `sweep.csv`/`kstar.csv`, not `metrics.csv` | §6.2 is one row *per simulation run*; E0 has no runs. The §6.2 schema is unmodified and untouched, awaiting E1. |

**No divergences on the four §3 corrections.** All four are implemented in
corrected form: `κ = −ln(1−p)` (with `--kernel=linear` available as the ablation
only), both dose regimes with `m-of-k` as the non-default-able explicit choice,
no `1−1/e` anywhere (a test greps the reports for it), and no approximation
guarantee of any kind is stated.

---

## 3. Every number in the HTML report, and the line that computes it

| reported number | value | computed by |
|---|---|---|
| gate decision | GO | `run_e0.py:write_verdict` → `gate` |
| frac interior, all-k | 50.56% | `write_verdict` `per_regime`, from `kstar.csv:interior` |
| frac interior, m-of-k aggregate | 47.62% | same |
| frac interior, proportional-50 | 95.25% | `per_policy["m-of-k/proportional-50"]` |
| frac interior, fixed-3 | 0.00% | `per_policy["m-of-k/fixed-3"]` |
| median k*, proportional-50 | 12 | `per_policy` `median_k_star` |
| median k*, all-k | 3 | same |
| frac at k=2 floor, all-k | 49.44% | `per_policy` `frac_at_lower` |
| median depth, Regime A | 0.2% | `alpha_sweep.csv` row thr=0.90 `median_rel_depth` |
| θ_A(10) | 147.90 | `model.py:theta_all_k`; test vs brief 147.9 |
| θ(7,5,3,2 of 10) | 53.18 / 33.43 / 19.82 / 14.05 | `model.py:theta_m_of_k`; tests vs 53.2/33.4/19.8/14.1 |
| passes/CH, all-10 / 5-of-10 / 3-of-10 | 5.92 / 1.34 / 0.79 | `model.py:passes_per_ch`; tests vs brief 5.9/1.3/0.8 |
| θ_A k=4→40 growth | 15.26× | `write_verdict` `ln_k_survival` |
| θ_A per-file growth k=4→40 | 1.526× | same; test asserts 1.53 ± 0.03 |
| θ(m=3) k=4→40 | 26.1 → 18.1 (0.694×) | same |
| kernel understatement at p=0.2/0.3/0.5 | +11.6 / +18.9 / +38.6% | `model.py:dose_kernel`; tests vs §3.1 table |
| quasiconvex, integer m | 0% | `alpha_sweep.csv:frac_quasiconvex` |
| quasiconvex, continuous m | 94.4–97.1% | `alpha_sweep.csv:frac_quasiconvex_continuous_m` |
| median violation magnitude | 1.4–14.8% | `curve_shape` `max_violation_rel` |
| interior range over thr 0.30–0.80 | 85.8–99.6% | `alpha_sweep.csv:frac_interior` |
| median k* vs thr | 32→3 | `alpha_sweep.csv:median_k_star` |
| hex vs circle packing error | 20.9% undercount | `model.py:clusters_from_area`; test asserts 1.209 |

`tests/test_report.py::test_headline_numbers_match_verdict_json` checks the
report's headline figures against `verdict.json` rather than trusting the
template.

---

## 4. Things I am unsure about

1. **A1 is load-bearing and I derived it.** If the reviewer rejects it, the E0
   verdict flips from "GO, conditional" to "NO-GO". It deserves more scrutiny
   than anything else here.
2. **Two bugs I found in my own work, both caught by assertions, both disclosed:**
   a test asserted the hex/circle packing ratio inverted, and another asserted a
   cleaner `k ln k` asymptotic separation than actually exists at C_conf = 0.95.
   Both were my tests being wrong, not the model. The second turned into a real
   finding (the `ln k` factor is mild — see the report). I have not re-derived
   every other test from scratch, so there may be more of this.
3. **The `interior` definition is grid-dependent.** `k*` at k=40 is "at the upper
   boundary" only because the grid stops at 40 (Appendix A.2 sets that range). For
   fixed-m, `T_total` is still falling at k=40, so the honest statement is "no
   interior optimum within the specified range", which is what I wrote.
4. **`rel_depth` uses the better of the two boundaries.** A curve that is
   shallow-but-genuinely-U-shaped and one that is flat both get small depth; I
   report depth rather than thresholding on it, except for the stated 1% bar.
5. **`frac_interior` under continuous m is *lower* than under integer m at small
   α** (80.4% vs 94.4% at α=0.155). The sawtooth can manufacture spurious interior
   minima. I report both and did not pick the flattering one.
6. **The even-k quasiconvexity control is α-specific** and only valid at α=0.5
   (⌈αk⌉ has period 2 only there). It is still emitted in `kstar.csv` because the
   main grid uses α=0.5, but the continuous-m arm is the general diagnostic. The
   column name does not say this; the docstring does.
7. **No E0 number is a measurement of the physical system.** Every `k*` is a
   property of an assumed r/f pair. The report says so in "What E0 does not
   establish"; I would rather the reviewer check I said it loudly enough.

---

## 5. Environment deviation (not my choice, but it shapes what follows)

§4 states ns-3 and PECEE are available. They are not present in this container,
nor is LKH. `env.txt` records this. E0 needs none of them; **E2, E3, E5 and E7 are
blocked** until the environment provides them. I did not stub them out, because a
stub that silently stands in for a measurement is exactly the failure mode §8
warns about.
