# uav-sar campaign tools

Dependency-free Python 3 (stdlib only — no numpy/scipy) so any reviewer can
rerun every number on a bare machine.

Run them **from the ns-3 root** (the directory containing `build/`), because
every script hard-codes the relative binary path:

```bash
cd /home/user/ns3-dev
export LD_LIBRARY_PATH=$PWD/build/lib
python3 src/uav-sar/tools/campaign_stats.py /tmp/out 30
```

`campaign_common.py` is imported by the others; Python puts the script's own
directory on `sys.path`, so this works from any cwd.

---

## 1. Metric definitions

These are the only definitions. Anything reported under a different name is a
different quantity.

| name | definition | source |
|---|---|---|
| **`t_report` / mission completion** | `timeToReportAtBS_s` — sim time at which the REPORT reaches the BS. `-1` = never. | `metrics.csv` |
| **`t_victim`** | `timeToCompleteData_s` — sim time at which the victim's full dataset is delivered. `-1` = never. This is the milestone **every** arm can reach. | `metrics.csv` |
| **`t_localize`** | `timeToLocalize_s` — sim time at which the localization estimate fires. `-1` = never. | `metrics.csv` |
| **`delivery error`** | `‖ position of the first `deliver_start` event − victim position ‖`, in metres. **This is the localization metric.** It measures where the data actually got put. | `events.csv` + victim position |
| **`leader_cell_error`** | `‖ position of the first `summon_start` event − victim position ‖`. **RETRACTED — see §2.** | `events.csv` + victim position |
| **`energy`** | `uavEnergyJ`, integrated to the scheme's *own* stop condition. See §4. | `metrics.csv` |
| **`packets`** | `pktSent`, total across all nodes. See §4. | `metrics.csv` |
| **victim position** | `victimX`/`victimY` columns if present; else reconstructed from `targetNodeId`, `gridSize`, `numUav` and the `gridSpacing` column; else reconstructed at 20 m with a stderr warning. See §3. | `metrics.csv` |

Percentiles (`p90`, IQR bounds) are **nearest-rank**: the smallest observation at
or above the requested fraction, i.e. index `ceil(q·n)−1` on the sorted sample.

---

## 2. The retracted metric (audit S8)

`leader_cell_error` = `‖summon_start − victim‖`.

`summon_start` is emitted at the **region leader's own position**, which is a
sensor node on the lattice and therefore grid-quantized. It is *not* an estimate
of where the victim is and *not* where data is delivered. It reads ~2.5× higher
than the delivery error (measured on the same 12 runs: median **40.0 m** vs
**16.5 m**), and it is the number that leaked into the documented reproduce
command under the label "localize error" (40.0 m against a table that says
15.8 m).

**It must never be labelled "localize error" or "localization error".** It is
retained under the name `leader_cell_error`, and only so that historical numbers
remain reproducible. Every script that prints it also prints a `[S8]` banner
saying so.

`campaign_stats.py` does not compute it at all.

---

## 3. Grid spacing (audit S9)

The victim position used to be reconstructed as
`((tid−1−numUav) % grid · 20.0, … · 20.0)` with a **hard-coded** 20 m spacing that
no script ever overrode. Every delivery/leader error measured at another
`--gridSpacing` was therefore wrong — measured on real runs at
`--gridSpacing=40`, the old code reports a **60.2 m** median delivery error where
the true value is **1.3 m**.

`campaign_common.victim_pos()` now resolves it in this order:

1. the `victimX` / `victimY` columns of `metrics.csv` (authoritative);
2. reconstruction from `targetNodeId` + the `gridSpacing` column;
3. reconstruction from a spacing the calling sweep supplied itself
   (`fallback_spacing=`, used by `campaign_sweep2.py` and
   `campaign_sweep_spacing.py`, which know the value they passed on the CLI);
4. reconstruction at 20.0 m — **prints a warning to stderr**, once per process.

Paths 2–4 assume the lattice layout (BS = id 0, UAVs = 1..numUav, ground nodes
row-major after that). That assumption dies the moment deployment becomes random
(audit W7); `victimX`/`victimY` is the only path that survives it.

---

## 4. Inclusion rule and censoring (audits S2, reporting)

`campaign_stats.py` previously computed latency statistics over successful runs
only, while computing energy and packet statistics over **all** runs including
failed ones — so the columns of one table were not comparable with each other.

There is now **one rule**, printed in the output header:

> A run enters a distribution iff the victim was served
> (`timeToCompleteData_s >= 0`). Success/failure **rates** are over all runs.

Within the included set, a metric that is still `-1` means that stage does not
exist for that scheme (e.g. `nocoop` and `pure-uav` never report at the BS — the
metric is 0 %-by-construction for them, audit M1). Such cells print `n/a` and the
per-cell `n` shows how many runs actually contributed.

`campaign_stats.py` also prints a **censoring-horizon table**: the `--simTime`
budget used for each scheme, how many runs were censored by it, and the maximum
observed value. A run truncated by `--simTime` is indistinguishable from a failed
run in `metrics.csv` — this is how a "97 % success" figure once turned out to be
a pure `--simTime=200` artifact (a seed that was in fact served at 205.1 s).
If the maximum sits near the horizon, treat the rate as an artifact.

Note that the horizons differ per scheme (300 s to 900 s). Comparing "success
rate" across schemes is only meaningful because each horizon is generous enough
for its scheme; the table exists so a reader can check that.

---

## 5. Statistics (audits S10, S11)

- **p-values** come from `math.erfc(|z|/√2)`. The previous form,
  `2·(1 − ½(1+erf(|z|/√2)))`, cancels catastrophically and returns exactly `0.0`
  for `|z| > 8.29`; that is the origin of the "p < 1e-16" print floor. At
  z = 12.20 the true value is **3.1e-34**. The real value is printed.
- **The design is matched-pairs**: seed *k* produces the same channel
  realisation in every scheme, so the schemes are compared on the same
  realisations. The **Wilcoxon signed-rank test** (paired, mid-ranks for ties,
  zero differences dropped, tie-corrected normal approximation, no continuity
  correction — matching scipy's default) is therefore reported as **primary**.
- **Mann–Whitney U** (unpaired) is retained alongside, because the published
  table quotes it. Where the comparator is deterministic across seeds it can
  show a *smaller* p than the paired test — that is the comparator's degeneracy,
  not extra evidence.
- **Cliff's delta** is reported as the effect size, with the conventional
  thresholds `|d| < 0.147` negligible, `< 0.33` small, `< 0.474` medium, else
  large. Sign convention: negative means `proposed`'s values are smaller.
- Also reported: the **median paired difference** and the **count of pairs
  favouring each arm**.
- Every median carries a percentile-bootstrap 95 % CI (5000 resamples, fixed
  seed 12345), an IQR, and a p90.

Self-test, validating all of the above against hand-computed examples:

```bash
python3 src/uav-sar/tools/campaign_stats.py --selftest
```

---

## 6. The scripts

| script | what it does | usage |
|---|---|---|
| `campaign_common.py` | shared victim-position resolution and nearest-rank percentiles. Not runnable. | — |
| `campaign_stats.py` | **the reporting tool.** Runs 5 schemes × N seeds; prints censoring horizons, Wilson-CI success rates, median/IQR/p90/bootstrap-CI for every distribution, paired Wilcoxon + Cliff's delta (primary) and Mann–Whitney (secondary). Uses the delivery error; never touches the retracted metric. | `campaign_stats.py <outdir> <N> [--quick] [--selftest]` (`--quick` = `proposed` + `tsp-mc-x4` only) |
| `campaign_analyze2.py` | side-by-side of `leader_cell_error` and delivery error on the same runs — this is the script that documents the ~2.5× gap. Reuses an existing output dir unless given a 3rd argument. | `campaign_analyze2.py <dir> <N> [rerun]` |
| `campaign_sweep2.py` | generic single-knob sweep reporting **delivery error**. Supersedes the three named sweeps below. | `campaign_sweep2.py <dir> <N> <knob> <v1,v2,…>` |
| `campaign_compare.py` | quick 3-scheme comparison (`proposed`/`nocoop`/`pure-uav`) at `--simTime=200`; dumps `results.json`. Beware the 200 s horizon (§4). | `campaign_compare.py <dir> <N>` |
| `campaign_analyze.py` | single-scheme detail: rates, region cells, intra/inter shares. | `campaign_analyze.py <dir> <scheme> <N>` |
| `campaign_tspmc.py` | one-line head-to-head of `tsp-mc ×4`, `tsp-mc ×1`, `proposed ×4`. | `campaign_tspmc.py <dir> <N>` |
| `campaign_mc_redundancy.py` | fairness probe: smallest `--mcRedundancy` at which `tsp-mc` reaches ~100 % GT coverage. | `campaign_mc_redundancy.py <dir> <N> [numUav]` |
| `campaign_mc_radius.py` | `--mcRadius` sweep for `tsp-mc`. | `campaign_mc_radius.py <dir> <N> <R>` |
| `campaign_sweep_decay.py` | `--clueDecay` sweep. **Reports only the retracted metric** — prefer `campaign_sweep2.py <dir> <N> clueDecay 30,45,60,90,120`. | `campaign_sweep_decay.py <dir> <N>` |
| `campaign_sweep_minobserve.py` | `--minObserve` sweep. **Reports only the retracted metric** — prefer `campaign_sweep2.py <dir> <N> minObserve 0,10,20,30,45`. | `campaign_sweep_minobserve.py <dir> <N>` |
| `campaign_sweep_spacing.py` | `--gridSpacing` sweep. **Reports only the retracted metric** — prefer `campaign_sweep2.py <dir> <N> gridSpacing 15,20,25,30,40`. | `campaign_sweep_spacing.py <dir> <N>` |
| `run_batch.sh` | legacy bash batch runner. Targets `ns3.46-scenario-sar-default`, **not** the `-optimized` binary the Python tools use, and applies none of the fixes above. Kept for history; do not report from it. | `bash run_batch.sh [N] [GRID] [NUMUAV] [SIMTIME]` |

`campaign_mc_redundancy.py` and `campaign_mc_radius.py` score GT coverage from
`gt_done` events, which are only emitted when the scheme is non-cooperative —
so they can score `tsp-mc` but **cannot** score `proposed` (audit S12). Their
coverage column is single-arm by construction.

---

## 7. Known gaps not fixed here

- `reportedX`/`reportedY` are now emitted by the binary but no script uses them;
  the delivery error is still derived from the `deliver_start` event position.
  Cross-checking the two would catch a whole class of bookkeeping error.
- The three named sweeps still report only `leader_cell_error`. They are
  correctly labelled, but they should be re-pointed at delivery error (or
  deleted in favour of `campaign_sweep2.py`).
- `campaign_compare.py` uses a 200 s horizon with no censoring report.
- Nothing here reports CDFs or the multimodality the audit found in the baseline
  latency distributions (S7); medians and p90 alone hide it.
