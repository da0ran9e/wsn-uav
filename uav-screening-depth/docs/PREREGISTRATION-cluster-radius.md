# Pre-registration — composed prediction for T_total(R)

**Written and committed BEFORE the joint check was run.** Task §6 requires this,
and the reason is blunt: without it there is nothing stopping either side being
tuned until the story works. Git history is the evidence of ordering.

Status at the time of writing: B4/B5 and A6 sweeps are **running but not read**.
Nothing below is fitted to them. The only numbers used are (a) the calibration
measurements already recorded in `config/cluster-radius.yaml`, (b) the single-seed
pilot values quoted explicitly as pilots, and (c) closed forms.

---

## 1. The composition

```
T_total(R)  =  T1(R)  +  h_max(R) · T_hop(R, n_c)
h_max(R)    =  max(0, (R − r_bc) / r_tx)
```

Note `h_max(R) · T_hop(R, n_c) = T_spread(R, n_c)` by construction, since
`T_hop := T_spread / h_max`. So the composition is really
`T_total(R) = T1(R) + T_spread(R)`, and `T_hop` is a *derived, reported* quantity
rather than an independent input. This matters: it means the composition cannot be
wrong about the ground term — only the closed form for `R*` can be.

## 2. Closed form for R*, and its self-check

With `T1(R) = β√(C·A)/v` and `C = A/(c_h R²)`, `c_h = 3√3/2`:

```
T1(R) = β·A / ( sqrt(c_h) · R · v )          ~ 1/R
```

Setting `dT_total/dR = 0` with `T_hop` treated as constant in `R`:

```
R* = sqrt( r_tx · β · A / ( sqrt(c_h) · v · T_hop ) )
```

which is exactly the form in task §6. Self-check against the task's own figure:
with `T_hop = 2 s`, `r_tx = 50 m`, `β = 0.7`, `A = 10⁶ m²`, `v = 20 m/s`,
`sqrt(c_h) = 1.612` this gives **R\* = 736.8 m**, and the task states 736 m. The
implementation of the model therefore agrees with the group's analytic check
before any measurement is consulted.

Inverting for the operating range: `R*` falls at or below 400 m only if

```
T_hop  ≥  r_tx·β·A / ( sqrt(c_h)·v·400² )  =  6.9 s
```

and at or above 94 m only if `T_hop ≤ 125 s`.

## 3. The prediction being registered

**3.1 — `T_hop` will come out at a few seconds, not tens.** Predicted range
**1.3 – 4 s** over R = 94–300 m at k = 8.

Mechanism, stated in advance: `T_hop` is floored by the radio, not by contention.
Moving `k` fragments across one ring costs at least `k/λ = k × 0.2 s` because of
the ≥ 200 ms `Send()` spacing (Appendix A.3). At k = 8 that floor is **1.6 s**.
Single-seed pilots gave T_spread = 3.85 s at R = 150 where h_max = 2, i.e.
T_hop ≈ 1.9 s — about 1.2× the floor. Contention is therefore predicted to add of
order 20 %, not an order of magnitude.

**3.2 — `T_hop` will scale with k, roughly as k/λ.** Predicted T_hop ≈ 0.8 s at
k = 4 and ≈ 3.2 s at k = 16, i.e. an exponent in k near 1. This is the sharpest
falsifiable claim here: if `T_hop` does not track `k/λ`, the stated mechanism is
wrong.

**3.3 — `T_hop` will *decrease* with R, not increase.** Predicted exponent in R
of about **−0.6** (95 % interval −0.9 to −0.3). Equivalently `T_spread ~ R^0.9`,
sub-linear, while `h_max ~ R^1`. Pilots: T_spread 2.64 → 7.32 s for R 94 → 300
gives exponent 0.88, hence T_hop exponent ≈ −0.62.
**This makes the task's closed form an approximation, not a law** — it assumes
`T_hop` constant in `R`. The measured exponent is the reportable quantity.

**3.4 — Spatial reuse will beat the R² traffic growth.** Predicted: at fixed R,
denser deployments (smaller lattice spacing, larger `n_c`) complete no slower, and
possibly faster, despite carrying more total traffic. Pilot at R = 150:
T_spread 4.06 / 3.85 / 3.18 s for spacing 30 / 20 / 15 m while MAC drops rose
1 → 27 → 83. Registered prediction: `T_spread` exponent in `n_c` in
**[−0.4, +0.2]**, i.e. flat to mildly negative.

**3.5 — `R*` will fall OUTSIDE the operating range, above 400 m.** Predicted
`R*` ≈ **500 – 800 m** at k = 8. Consequence if confirmed: the contribution as
framed does not stand, and the design rule becomes *make clusters as large as the
kinematics allow*. Predicted exception worth checking: at k = 16 with a slow
advertisement regime, `T_hop` could reach the 6.9 s needed to pull `R*` inside
400 m — this is the one corner where the interior optimum might survive.

**3.6 — The kinematic lower bound R ≥ 4ρ/3 = 94.1 m will bind, and the penalty
below it is large.** Pilot: the realised Dubins tour is ≈ 1.7× the BHH estimate
for R ≥ 94 but **2.22× at R = 60**. Registered prediction: the Dubins/BHH ratio
is flat near 1.7 for R ≥ 94 and rises sharply below it, so the true `T1` at
R = 60 is ~30 % worse than the estimate implies. Since `T_total` is predicted to
be decreasing in `R` throughout the range anyway, this bound is not expected to
be the *active* constraint on the optimum — it penalises the small-R end that is
already losing.

**3.7 — B5: no node completes without pooling.** Predicted fraction of nodes
holding all k from seeding alone: **0.000** at every R. Pilot at R = 150: 0 of
147 complete with 66 seeded.

## 4. What would refute each claim

| claim | refuted by |
|---|---|
| 3.1 | measured `T_hop` median > 10 s at k = 8 anywhere in R = 94–300 |
| 3.2 | `T_hop` exponent in k outside [0.6, 1.4] |
| 3.3 | measured R-exponent of `T_hop` positive, or outside [−0.9, −0.3] |
| 3.4 | `T_spread` exponent in `n_c` above +0.2 |
| 3.5 | `R*` interior to [94, 400] at k = 8 with CIs excluding the boundary |
| 3.6 | Dubins/BHH ratio at R = 60 within 5 % of the ratio at R ≥ 94 |
| 3.7 | any node completing all k in `seedonly` mode |

## 5. Analysis decided in advance

- `T_hop = T_spread / h_max(R)`. At R = 60, `h_max = 0.2`, so `T_hop` is
  `5 × T_spread` — a division by a small number that inflates both the value and
  its CI. **R = 60 will be plotted but excluded from every exponent fit**, and the
  reason stated. Fits use R ∈ {94, 120, 150, 200, 250, 300}.
- Exponents by OLS on log–log, with a bootstrap CI on the slope
  (`tools/campaign_stats.py:bootstrap_slope_ci`, 2 000 resamples).
- Medians with 10 000-resample percentile bootstrap CIs; rates with Wilson.
- Censored runs (not all nodes complete within the cap) are **reported, never
  dropped**. If any arm censors, the censoring rate is quoted beside its median.
- `R*` is located on the composed curve by grid search over R with the measured
  `T_spread(R)`, and separately from the closed form, and **both** are reported
  even if they disagree.
