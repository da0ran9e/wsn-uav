# uav-l2

Layer 2 of phase 1: the flight path of a fixed-wing UAV over a non-convex domain made of
several clusters (CLAUDE.md §8 item 56). Each cluster is made exactly as in
[`../uav-coop`](../uav-coop) (`models/common/region.cc`, `deploy.h`): Eden growth, concavity
filling to a target convexity, uniform nodes, CH away from the edge, one CL per cell.

**Step 1 — the map** — [`docs/MAP-vi.md`](docs/MAP-vi.md): `tools/map_gen.py` places 4-5
clusters on one wide hex map with a minimum gap between them.

## Layout
```
uav-l2/
├── tools/map_gen.py   # the multi-cluster map: cells, nodes, roles, step figure
└── docs/              # MAP-vi.md, figures/, data/
```
