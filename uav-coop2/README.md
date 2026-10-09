# uav-coop2

A second cooperation scheme for UAV-assisted dissemination in wide clusters. It starts from
exactly the same situation as [`../uav-coop`](../uav-coop) (packaged at commit `857314a`):
same deployment, same open Dubins flight path over the CH, same UAV broadcast, same channels.
Only what the ground does after the pass changes.

Reused from `uav-coop`, not copied:
- deployment, roles, routes — `uav-coop-deploy` (seed 1, R = 100 m, 109 cells, spacing 35 m,
  2 312 nodes, CH #136 at 556 m from the edge), CSVs in `../uav-coop/docs/data/deploy-*-s35.csv`;
- the pass — `uav-coop-pass --bits` (altitude 100 m, 50 m/s, 127 B every 10 ms, +10 dBm,
  α = 3.0, Rician K = 2; packet s carries chunk s mod K), 120 independent missions.

**Status: step 0 — the situation right after the pass** — [`docs/STATE-vi.md`](docs/STATE-vi.md).
Files count only as runs of consecutive packets, and the path can be bent with
`uav-coop-deploy --angle` — [`docs/RUNS-vi.md`](docs/RUNS-vi.md).
Layer 3 (the paper's contribution): the River scheme — problem statement and short
pseudocode (the BS's Axe table, River set-up at each Axe cell) — [`docs/L3-vi.md`](docs/L3-vi.md);
sketches by `tools/concept_cells.py`.

## Layout
```
uav-coop2/
├── tools/state_report.py   # who holds what after the pass: per node, per cell (zones A/B/C)
├── tools/runs_report.py    # whole files from consecutive packets only, across flight paths
├── tools/concept_cells.py  # cell-level sketches of the River scheme (no text)
└── docs/                   # STATE-vi.md, RUNS-vi.md, L3-vi.md, figures/, data/
```
The ns-3 module (linking `uav-coop`) is added with the first C++ of the new scheme.
