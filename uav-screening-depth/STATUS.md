# STATUS — single source of current truth

A newcomer reading only this file must be able to continue the work.
Last updated: 2026-09-12. Maintained per AGENT-BRIEF §11.

Two pieces of work exist in this repo:

| work item | state |
|---|---|
| **E0** — does an interior `k*` exist? (screening-depth gate) | complete, GO conditional, reviewed-pending |
| **Cluster-radius probe** — does an interior `R*` exist, in 94–400 m? | **measurement in flight**, see §2 |

---

## 1. E0 — screening depth (gate: GO, conditional)

Unchanged from the previous session. Summary:

| m-policy | interior `k*` | median `k*` | reading |
|---|---|---|---|
| `m ∝ k` | **95.2%** | 12 | the question is well posed |
| `m` fixed | **0.0%** | 40, every point | **no optimum exists** — θ is flat in k |
| `all-k` (m=k) | 50.6% | 3 | exists but cosmetic (median depth 0.2%) |

Both E0 acceptance findings stand: the `ln k` factor exists only in Regime A (and
is mild even there — per-file cost grows 1.53× over a 10× range in k), and Regime A
needs 5.92 passes per CH at k=10. Full detail in `report/E0.html`,
`docs/AUDIT-E0.md`.

**Correction to the record:** the commit message at `98822fd` states "Tests: 158
passed"; the true figure at that commit was 267 (parametrized tests expand). I did
not amend that commit, deliberately — it is the pre-registration commit for the
cluster-radius probe and it must be visibly untouched after the sweeps were read.

---

## 2. Cluster-radius probe — IN FLIGHT

**The one question:** `T_total(R) = T1(R) + h_max(R)·T_hop(R, n_c)` — does an
interior minimum exist, and does it land inside 94–400 m? Everything turns on
`T_hop`, which nobody had measured.

### What is already settled

- **ns-3.46 built and LR-WPAN verified** (commit `ea50b72a`, `lr-wpan-data`
  example runs and receives). LKH 3.0.13 built from source. Both recorded in
  `results/*/env.txt`.
- **The radio was calibrated, not assumed.** TX power −8 dBm gives measured
  PER(50 m) = 0.005, PER(55) = 0.09, PER(60) = 0.55, PER(65) = 0.98 — a *reliable*
  50 m hop, 50 % point at 59 m.
- **Contention is real and instrumented.** Six LR-WPAN MAC/PHY trace sources
  connected on every run; MAC TX drop rate ≈ 2.9 % overall, rising with node
  density and with Trickle disabled. Zero `Send()` failures, zero censored runs.
- **Heading resolution chosen on tuning seeds only** (0–19, never reported):
  8 headings, within 0.9 % of 12 at 2.2× less cost.
- **Pre-registration committed before any sweep output was read** —
  `docs/PREREGISTRATION-cluster-radius.md` at `98822fd`. Seven numbered
  predictions, each with the measurement that would refute it. The report's
  scorecard is computed mechanically from those ranges.

### Early results (partial data, ~45 % of the B4 sweep)

These will be restated from the full sweep; they are here because they are already
decision-relevant.

- **`T_hop` is single-digit seconds, not tens.** 1.3–2.8 s at k = 8 over
  R = 94–300 m, against the **6.9 s** needed to bring `R*` inside 400 m.
- **`T_hop` falls with R**, exponent **−0.63**, inside the pre-registered
  [−0.9, −0.3]. The closed form assumes `T_hop` constant in R, so it is an
  approximation.
- **A prediction of mine failed.** I registered `T_hop ∝ k/λ` with exponent ≈ 1.
  Measured: **0.19–0.28**. At k = 16 and R ≥ 150 m, `T_hop` is *below* the 3.2 s a
  single node needs to emit 16 fragments — so rings are served by several nodes in
  parallel and per-node pacing never becomes the per-ring cost. **Prediction 3.2
  is REFUTED** and the report says so.
- **B5 (pooling is a precondition) looks supported**: in the pilot, 0 of 147 nodes
  completed all k with relaying disabled despite 45 % being seeded. The full arm
  has not run yet.

### What remains

1. B4 sweep: ~45 % done. Remaining cost is dominated by the `trickle_off` arm at
   R = 250–300 m.
2. A6 realised-Dubins tours: restarted with a vectorised cost matrix (27 s → 1.9 s
   per 960×960 instance) and incremental writes.
3. Analysis → `report/cluster-radius.html`. The page currently builds with a
   **STALE** banner and explicitly names which arms are missing; it will not
   silently present a gap.

---

## 3. Stale or void numbers

None void. The cluster-radius page is **STALE** by its own banner until the B4
`trickle_off`/`spacing`/`seedonly` arms and the A6 Dubins arm land. Everything in
`report/E0.html` is CURRENT.

---

## 4. Open problems, ranked

1. **`KY-HIEU-vi.md` is missing.** The probe prompt says notation is fixed by that
   file; it is not in this repository. I used the prompt's own symbols verbatim and
   invented none, but there is a known collision: heterogeneity is `h` in
   `AGENT-BRIEF` and `η` in the probe prompt, while `h_max` is a third quantity.
   **If that document disagrees, the probe's symbols need a pass.**
2. **Is `m` proportional to `k`, or fixed?** (From E0, unchanged and still the
   top blocker for the screening-depth paper.) 95 % vs 0 % interior. My derivation
   from Appendix A.2 says proportional; it assumes the k files partition one
   payload. Someone who knows the physical system must settle it.
3. **Quasiconvexity fails for integer `m`** (E0). Restate as trend-level with the
   sawtooth reported, or optimise over `(k, m)` jointly.
4. **Does each node match its own data, or does the CH match for the cluster?**
   (Probe prompt §9.1 — *explicitly flagged as unanswered by the group, and built
   wrong twice already.*) Not assumed either way here. It does not affect this
   probe's measurement, but it decides where the matching cost lands.
5. **Is the declared dose identical across nodes, or per-node?** (Probe prompt
   §9.2.) If it differs, the coverage problem becomes **set-cover with non-uniform
   demands** — a different problem from the one currently specified. Nothing in
   this probe assumes uniformity, because the probe does not solve coverage at all.
6. **`T_hop` is protocol-dependent.** Reported as a function of R, `n_c`, k *and*
   the advertisement interval for that reason. What is protocol-independent is the
   `k/λ` floor — and the measurement shows that floor does not bind.
7. **PECEE is absent**, so Phase 0 is a hex-tiling stand-in (CH = node nearest each
   occupied cell centre). Moves individual stops, not the `1/R` scaling.
8. **Repository location.** AGENT-BRIEF §5 wants a standalone `uav-screening-depth`
   repo. Push access is scoped to `da0ran9e/wsn-uav` branch
   `claude/jolly-ptolemy-nytjc1`, so this is a self-contained subtree that extracts
   with `git subtree split -P uav-screening-depth`. **Needs the user to create the
   repo.**

---

## 5. What to do next

1. Let the B4 and A6 sweeps finish, then `analyse_cluster_radius.py` and
   `make_report.py cluster-radius`. The analysis **refuses** input where any
   configuration is short of 120 seeds, so a partial re-run cannot be mistaken for
   a complete one.
2. Review the probe per §11.3, starting with `docs/AUDIT-cluster-radius.md` §3
   (assumptions) and §5 (things I am unsure about).
3. Settle open problems 1, 4 and 5 — all three are questions for the group, not
   measurements.

---

## 6. How to reproduce

```bash
python3.10 -m pytest tests/ -q                 # 292 tests
python3.10 tools/campaign_stats.py --selftest
python3.10 tools/run_e0.py && python3.10 tools/make_report.py E0

# probe (needs ns-3.46 at ~/ns3-dev and LKH on PATH)
cp ns3/cell-spread.cc ~/ns3-dev/scratch/ && (cd ~/ns3-dev && ./ns3 build cell-spread)
python3.10 tools/run_b4.py --workers 3         # ~5 CPU-hours, 5400 runs
python3.10 tools/run_a6.py --arms bhh,dubins --workers 4
python3.10 tools/analyse_cluster_radius.py
python3.10 tools/make_report.py all
```

Raw run directories and the 73 MB E0 `sweep.csv` are gitignored; every summary
table a report plots is committed.

---

## 7. Deviations from the briefs, in one place

| source | says | actual | why |
|---|---|---|---|
| AGENT-BRIEF §5 | standalone repo | subtree inside `wsn-uav` | push scope; extracts cleanly |
| AGENT-BRIEF §4 | ns-3 and PECEE available | ns-3 built from scratch here; PECEE still absent | environment |
| probe §3 | 7×3×3×2 = 126 configurations | **45** | ≈20 CPU-hours otherwise. **N = 120 seeds per configuration was never cut — only the factorial.** |
| probe §5 | Dubins tours at ≥4 R values | 5 (60, 94, 150, 250, 400 m) | 60 answers the kinematic-bound question, 400 reaches the top of the range |
| probe §2 | full `git clone` | shallow clone at tag `ns-3.46` | same tree and SHA, far less disk |
| probe preamble | notation fixed by `KY-HIEU-vi.md` | file absent; prompt's symbols used verbatim | see open problem 1 |

Fuller lists with justification: `docs/AUDIT-E0.md` §2,
`docs/AUDIT-cluster-radius.md` §4.
