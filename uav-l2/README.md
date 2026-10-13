# uav-l2

Layer 2 of phase 1: the flight path of a fixed-wing UAV over a non-convex domain
(CLAUDE.md §8 items 56-57). The domain is made exactly like a [`../uav-coop`](../uav-coop)
cluster (`models/common/region.cc`, `deploy.h`: Eden growth, concavity filling to a target
convexity, uniform nodes), only larger: 300 grown cells, about five clusters' worth.

**Step 1 — the domain** — [`docs/MAP-vi.md`](docs/MAP-vi.md): `tools/map_gen.py`; long, curved
domains (spine-weighted growth), lakes and rivers (carved after filling): `tools/domain_gallery.py`;
clusters with a size cap on the lakes domain (phase 0): `tools/partition.py`.

## Layout
```
uav-l2/
├── tools/map_gen.py         # the domain: growth (optionally along a spine), lakes, river, nodes
├── tools/domain_gallery.py  # six example domains: long, C, S, lakes, river, mixed
├── tools/shape_stats.py     # elongation, bend, holes of plain Eden regions over seeds
├── tools/partition.py       # phase 0: capacitated, connected k-medoids clusters on a domain
└── docs/              # MAP-vi.md, figures/, data/
```
