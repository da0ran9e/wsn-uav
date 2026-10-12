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
and full pseudocode (Axe table at the BS, River set-up at each Axe cell, critical cells,
Circle, and after the pass: Axe → Bank fill, Circle fill, critical pull) — [`docs/L3-vi.md`](docs/L3-vi.md);
sketches by `tools/concept_cells.py`. Readiness review and trial plan — [`docs/TRIAL-vi.md`](docs/TRIAL-vi.md).
**Trial run (logic level, 120 missions, straight path):** River vs a direct pull — process,
logic, stage figures and results — [`docs/RIVER-RUN-vi.md`](docs/RIVER-RUN-vi.md)
(`tools/river_plan.py`, `tools/river_sim.py`, `tools/river_figures.py`).
**ns-3 trial (in progress):** `uav-coop2-river` runs Algorithms 5-7 (`--scheme=river
--prep=full|ondemand`) and the direct pull (`--scheme=direct`) over the full IEEE 802.15.4 MAC
(CSMA/CA, ACK, retries), with the PECEE cell grid as the schedule: cell channel by 7-colour,
one channel per gateway pair, one transmitter at a time per cell and per gateway pair; in-cell
routes by least ETX on each run's links. Input plan from `tools/river_export.py`
(`docs/data/river-plan.txt`); mission 1 of each scheme in `docs/data/river-ns3-r1-*.csv`.
Step-by-step figures of mission 1 (`--trace`, `tools/river_ns3_figures.py`) —
[`docs/RIVER-NS3-vi.md`](docs/RIVER-NS3-vi.md).
Variants on mission 1: 3-colour cell grid (`--colours=3`) and a narrower River
(`docs/data/river-plan-w2.5.txt`), `tools/river_variants_figure.py`, same page.

## Layout
```
uav-coop2/
├── tools/state_report.py   # who holds what after the pass: per node, per cell (zones A/B/C)
├── tools/runs_report.py    # whole files from consecutive packets only, across flight paths
├── tools/concept_cells.py  # cell-level sketches of the River scheme (no text)
├── tools/river_plan.py     # the plan: Algorithms 1-4
├── tools/river_sim.py      # slot-level trial: Algorithms 5-7 and the direct-pull baseline
├── tools/river_figures.py  # stage figures and tables of the trial
├── tools/river_export.py   # the plan as text for the ns-3 trial
├── tools/river_ns3_figures.py  # step figures of one ns-3 mission (--trace)
├── tools/river_variants_figure.py  # channel plan x River width, one mission
├── models/river-plan.*     # reads that plan (ns-3 module uav-coop2, links uav-coop)
├── examples/coop2-river.cc # the ns-3 trial: River (full / on-demand Circle) and direct pull
└── docs/                   # STATE-vi.md, RUNS-vi.md, L3-vi.md, TRIAL-vi.md, RIVER-RUN-vi.md, RIVER-NS3-vi.md, figures/, data/
```
Build: link `uav-coop2` into `ns3-dev/src` and enable modules `uav-sar;uav-coop;uav-coop2`.
