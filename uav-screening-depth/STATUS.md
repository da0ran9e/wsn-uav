# STATUS — single source of current truth

A newcomer reading only this file must be able to continue the work.
Last updated: 2026-09-11. Maintained per AGENT-BRIEF §11.

---

## 1. What is true right now

**E0 is complete. The gate is GO, but conditionally, and the condition is the
most important result so far.**

The brief's literal stop condition (`k*` on a boundary for >50% of the grid in
*both* regimes) is not met: 49.4% boundary in `all-k`, 52.4% in the `m-of-k`
aggregate. So E1 is unblocked. But those per-regime averages are nearly
meaningless, because they average over structurally opposite cases:

| m-policy | interior `k*` | median `k*` | what it means |
|---|---|---|---|
| `m-of-k`, m ∝ k | **95.2%** | 12 | the paper's question is well posed |
| `m-of-k`, m fixed | **0.0%** | 40 (always) | **no optimum exists at all** — θ is flat in k, so extra files are free |
| `all-k` (m=k) | 50.6% | 3 | optimum exists but is cosmetic (median depth 0.2%, below the 1% bar) and 49.4% sit on the k=2 floor |

Measured over 4,860 config points × 39 values of `k`, plus a 9-threshold sweep at
1,620 points each. All of it is deterministic — no seeds, no CIs, because there is
nothing sampled. `N ≥ 120` applies from E1 onward.

### The three acceptance criteria
1. **Interior fraction per regime** — reported above and in `report/E0.html`.
2. **Regime A feasibility** — reproduces the brief's table exactly: 5.92 / 1.34 /
   0.79 passes per CH for all-10 / 5-of-10 / 3-of-10. **Regime A needs the UAV
   over every cluster ~6 times at k=10.** It is only feasible at the small `k` it
   actually selects (median 3), which is the same as saying Regime A is feasible
   only where the screening question is uninteresting.
3. **Does `ln k` survive Regime B?** — **No.** θ_A grows 15.3× from k=4 to 40;
   with m fixed at 3 it *falls* (26.1 → 18.1). The `ln k` factor exists only in
   Regime A, exactly as the brief predicts. **And it is mild even there:** at
   C_conf = 0.95, θ_A ≈ k·[ln k + 2.97]/|ln(1−p)| and ln k only spans 0.69–3.69
   over k = 2…40, so per-file cost grows just 1.53× while the linear factor
   contributes 10×. "θ_A grows like k ln k" must not be written as "θ_A is driven
   by ln k".

### Two findings the brief did not anticipate

**(a) `m` is not a free knob — Appendix A.2 fixes it, and it is proportional to k.**
With pixel-stride interleaving over `k` files partitioning one payload, noisy-OR
gives `C = 1 − 0.1^(m/k)`, a function of the *ratio* alone, so
`α = m/k = ln(1−thr)/ln(0.10)`. An interior `k*` exists for 85.8–99.6% of the grid
across thresholds 0.30–0.80 (α = 0.16–0.70), and median `k*` falls monotonically
32 → 3 as the threshold rises — the signature of a genuine tunable optimum.
At thr = 0.90, α = 1 and the regime degenerates into Regime A, reproducing its
numbers from an independently coded path.
**This derivation is mine, not the brief's** (`docs/AUDIT-E0.md`, A1). If it is
wrong and `m` is really fixed, the premise collapses. It is open problem #1.

**(b) The quasiconvexity claim does not hold as stated.**
The paper's central structural claim is that `T_total(k)` is quasiconvex so a
unique interior optimum exists. Measured: **0%** of curves are quasiconvex under
integer `m = ⌈αk⌉`, versus **94.4–97.1%** under real-valued `m = αk`.
Mechanism, measured not assumed: the *realised* ratio `m/k` oscillates with the
parity of `k` (at α=0.5, k=3 gives 0.67 but k=4 gives 0.50), so θ zigzags by
+7.7/−1.4 opportunities and `T_total` alternates by 1–15%.
So **the objective is quasiconvex; the realisable curve is not.** `m` is
physically an integer, so this cannot be waved away. The paper must either state
quasiconvexity *in trend* and report the sawtooth, or promote `m` to a second
decision variable and optimise over `(k, m)`.

---

## 2. Stale or void numbers

None. This is the first campaign result set. Everything carries `prov_id`
`1d478b3dd653a6b1` and `report/E0.html` is banner `CURRENT`.

---

## 3. Open problems, ranked

1. **Is `m` proportional to `k`, or fixed?** (Tier 0 — blocks the paper's premise,
   not just E0.) The two answers give 95% vs 0% interior. My derivation from
   Appendix A.2 says proportional, but it assumes the `k` files *partition* one
   payload. If each file is instead a full-strength independent signature, `m` is
   fixed and there is no optimum to find. **Someone who knows the physical system
   must settle this before E1 is worth starting.** Note also a tension I could not
   resolve: the parent `wsn-uav` `CLAUDE.md` describes *unequal* per-layer
   utilities (0.30/0.12/0.05/0.40) while A.2 specifies equal-contribution pixel
   stride and says to match it exactly. I followed A.2.
2. **Quasiconvexity fails for integer `m`** (Tier 0 for any output that claims
   it). Restate as trend-level with the sawtooth reported, or optimise `(k, m)`.
3. **Regime A is operationally marginal** (5.92 passes/CH at k=10). If the paper
   needs all-k it must argue feasibility rather than assume it.
4. **`r(k)` and `f(k)` are entirely unmeasured.** They are plausible parametric
   families. They decide *where* `k*` lands, so nothing downstream of E0 is
   quantitative until they come from data. E0 only establishes that an optimum
   *can* exist.
5. **Environment: ns-3, PECEE and LKH are all absent**, though §4 says they are
   available. **E2, E3, E5, E7 are blocked.** I did not stub them — a stub
   standing in for a measurement is the failure mode §8 warns about.
6. **Repository location.** §5 requires a standalone `uav-screening-depth` repo
   and says explicitly not to put this inside `wsn-uav`. Push access for this
   session is scoped to `da0ran9e/wsn-uav` on branch
   `claude/jolly-ptolemy-nytjc1` only, so the tree lives as a self-contained
   subtree: it imports nothing from the parent and extracts with
   `git subtree split -P uav-screening-depth`. **Needs the user to create the
   repo.**
7. **E0's main grid confounds `R` with `C`** (fixed area ⇒ `C = A/2.598R²`). The
   `k*` vs `ln C` data is computed separately at fixed `R` and is labelled
   PREVIEW; no slope, intercept or R² is quoted. That is E9's job.

---

## 4. What to do next

1. **Answer open problem #1.** Everything else is contingent on it.
2. **Review E0** per §11.3 — especially `docs/AUDIT-E0.md` assumption A1. Do not
   start E1 until the gate is reviewed (§Appendix C.6).
3. Once reviewed, **E1** is implementable here (needs `shapely`, which pip can
   install). **E4** is also pure Python and unblocked if given synthetic geometry.
4. Decide how to handle the blocked items: either provision ns-3/PECEE/LKH, or
   rescope the paper to what can be measured without them and say so.

---

## 5. How to reproduce everything in this file

```bash
python3.10 -m pytest tests/ -q          # 108 tests
python3.10 tools/run_e0.py              # ~19 s -> results/E0/
python3.10 tools/make_report.py all     # -> report/E0.html, report/index.html
python3.10 tools/assert_one_build.py results/E0/kstar.csv results/E0/alpha_sweep.csv
```

`results/E0/sweep.csv` (73 MB) is gitignored and regenerated by `run_e0.py`;
every summary table it feeds is committed.

---

## 6. Deviations from the brief, in one place

| § | brief says | actual | why |
|---|---|---|---|
| 5 | standalone repo, not inside `wsn-uav` | self-contained subtree inside `wsn-uav` | push scope; extracts cleanly, see open problem #6 |
| 4 | ns-3 and PECEE available | absent, LKH too | environment; recorded in `env.txt` |
| 6.2 | `metrics.csv` per run | E0 emits `sweep.csv`/`kstar.csv` | E0 has no simulation runs; §6.2 schema untouched, awaiting E1 |
| A.4 | N ≥ 120 seeds | E0 is deterministic | nothing is sampled; applies from E1 |

Fuller list with justifications: `docs/AUDIT-E0.md` §2.
