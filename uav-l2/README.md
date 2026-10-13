# uav-l2

Layer 2 of phase 1: the flight path of a fixed-wing UAV over a non-convex domain
(CLAUDE.md §8 items 56-57). The domain is made exactly like a [`../uav-coop`](../uav-coop)
cluster (`models/common/region.cc`, `deploy.h`: Eden growth, concavity filling to a target
convexity, uniform nodes), only larger: 300 grown cells, about five clusters' worth.

**Step 1 — the domain** — [`docs/MAP-vi.md`](docs/MAP-vi.md): `tools/map_gen.py`.

## Layout
```
uav-l2/
├── tools/map_gen.py   # the domain: cells, nodes (no roles yet), step figure
└── docs/              # MAP-vi.md, figures/, data/
```
