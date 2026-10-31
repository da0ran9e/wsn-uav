# 2026-10-31 · Trajectory error (wind): River plans on the planned CHORD path, the UAV flies a perturbed one

Map k8-s1 (8 clusters, 45 critical cells), r100, ns-3 seeds 1-3. `wind_path.py`: cross-track and along-track offsets,
white noise smoothed by a 10 s Gaussian kernel, stationary sd σ (cross) and σ/2 (along); the time column is kept,
so packet s still leaves at s·10 ms and matches the plan. Pass rebuilt with `--offPlan` (same bits on the planned
path, checked). River = `rf` as in campaign 4. `wind.sh R σ`, `sweep.sh`, `sweep2.sh`.

Flyability (seed 1): max normal acceleration σ 50 m 2.6, σ 100 m 5.2, σ 200 m 10.0 m/s² (1 g = 9.81: σ 200 is past
the 45° bank limit 0.5 % of the time in one cluster); time over the cluster vs plan 0.96-1.03 / 0.84-1.02 / 0.77-1.02.
σ 200 m is reported as an indication only.

| σ | seeds | critical cells ready | last cell ready (s after leaving) | T* (s) | ΔT* paired vs no wind |
|---|---|---|---|---|---|
| 0 | 1-3 | 135/135 | 118 | 904 | - |
| 50 m | 1-3 | 135/135 | 114 | 905 | +0 ± 7 s (+0.1 %) |
| 100 m | 1-3 | 106/135 | 277 | 1198 | +294 ± 77 s (+33 %) |
| 200 m | 1 | 3/45 | 900 (limit) | 3576 | +2684 ± 294 s |

Reading: the data the cluster hears barely changes (D -0.4 % at σ 100 m), but beyond about one reception radius
(R50 = 99 m at r100) the BS's Seg assignment no longer matches where packets were heard; the Axe repair only asks
adjacent cells, so some Circle chains stall. Open: Deluge (plan-free) at σ 100 m; replanning on the flown path.
