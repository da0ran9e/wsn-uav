# uav-l2

Layer 2 of phase 1: the flight path of a fixed-wing UAV over a non-convex domain
(CLAUDE.md §8 items 56-57). The domain is made exactly like a [`../uav-coop`](../uav-coop)
cluster (`models/common/region.cc`, `deploy.h`: Eden growth, concavity filling to a target
convexity, uniform nodes), only larger: 300 grown cells, about five clusters' worth.

**Step 1 — the domain** — [`docs/MAP-vi.md`](docs/MAP-vi.md): `tools/map_gen.py`; long, curved
domains (spine-weighted growth), lakes and rivers (carved after filling): `tools/domain_gallery.py`;
clusters with a size cap on the lakes domain (phase 0): `tools/partition.py`.
**River on those clusters** (cap 80, mission 1) — [`docs/CLUSTER-RIVER-vi.md`](docs/CLUSTER-RIVER-vi.md):
uav-coop-deploy `--regionIn/--nodesIn`, uav-coop-pass, uav-coop2 River plan and ns-3 trial;
map `tools/cluster_river_figure.py`. Figures carry no text (CLAUDE.md §8 item 63).
**Restructuring the clusters as lanes** (phase 0 for the mission, CLAUDE.md §8 item 84) —
[`docs/RESTRUCTURE-vi.md`](docs/RESTRUCTURE-vi.md): `tools/restructure.py`, `mission.py --partition=lane`.
**C3 step by step** (path along its longest line, Algorithms 1-7 on ns-3) —
[`docs/CLUSTER-C3-vi.md`](docs/CLUSTER-C3-vi.md), `tools/cluster_steps.py`.

## Layout
```
uav-l2/
├── tools/map_gen.py         # the domain: growth (optionally along a spine), lakes, river, nodes
├── tools/domain_gallery.py  # six example domains: long, C, S, lakes, river, mixed
├── tools/shape_stats.py     # elongation, bend, holes of plain Eden regions over seeds
├── tools/partition.py       # phase 0: capacitated, connected k-medoids clusters on a domain
├── tools/cluster_river_figure.py  # River plans of the clusters on one map
├── tools/cluster_steps.py         # one cluster through every step of River, text-free figures
└── docs/              # MAP-vi.md, figures/, data/
```
