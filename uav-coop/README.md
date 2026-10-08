# uav-coop

UAV-assisted dissemination with edge cooperation inside wide clusters — a new
project that starts from the parameter set measured in `uav-sar`'s urban
experiments (`uav-sar/docs/A2G-RUN-vi.md`, `A2G-SWEEP-vi.md`, `G2G-CHAIN-vi.md`).
Those values live in `models/common/coop-params.h`.

**Packaged (closed) at this state — a different cooperation scheme continues in
[`../uav-coop2`](../uav-coop2), on the same network, flight path and broadcast.** Where it
stopped: the base manifest phase (border cells first, logic level) fills every lacking cell
on 5 of 6 flight paths at K = 2000, typically 1–6 s after the UAV leaves, never reaching the
CH; it falls short at K = 6000 (46 of 70 lacking cells stay lacking). Open, not started: the
secondary phase, the blank-border-cell experiment, gathering to the important nodes, a
radio-level (ns-3) manifest. Details and numbers: [`docs/MANIFEST-vi.md`](docs/MANIFEST-vi.md) §5–§6.

**Status: steps 1–4, step 5 in trial.** Hex lattice (corner radius R = 100 m) from the origin → a truly
random contiguous region whose concavities are filled up to a target convexity (default:
fully convex) → random sensor nodes with three random capabilities → one CH (kept at least
300 m from the edge), one CL per cell → an open Dubins flight path across the cluster: in
at a random boundary point, over the CH, out at another (min turn radius a parameter). See
[`docs/DEPLOY-vi.md`](docs/DEPLOY-vi.md). Step 3: the UAV flies that path broadcasting a
numbered stream; packets received per node — [`docs/PASS-vi.md`](docs/PASS-vi.md). Pre-built
routes planned at the BS (PECEE elastic clustering: next hop to the CL, to each adjacent
cell through its single gateway link, main route to the CH; no node left out) — [`docs/ROUTING-vi.md`](docs/ROUTING-vi.md).
Step 4, inside one cell: every node's share of the file summarised up the tree to the CL,
which learns exactly what the cell holds and lacks — [`docs/SUMMARY-vi.md`](docs/SUMMARY-vi.md).
Step 5 (trial, logic level): the base manifest phase between cells, border cells first —
[`docs/MANIFEST-vi.md`](docs/MANIFEST-vi.md), which keeps the author's description verbatim.

## Layout
```
uav-coop/
├── CMakeLists.txt            # build_lib (core); the pass example links lr-wpan etc.
├── models/common/            # pure logic, no ns-3 simulation objects
│   ├── coop-params.h         # the carried-over parameter set
│   ├── coop-rng.h            # portable seeded RNG (mt19937_64, independent streams)
│   ├── hex-grid.{h,cc}       # pointy-top lattice, axial coordinates
│   ├── region.{h,cc}         # random growth + concavity filling to a convexity; holes
│   ├── deploy.{h,cc}         # uniform random nodes; capabilities; CH and CL roles
│   ├── dubins.{h,cc}         # shortest Dubins path between two poses (six words)
│   ├── path.{h,cc}           # shortest open Dubins path through points, headings constrained
│   ├── routing.{h,cc}        # gateways, bridges, route tables: to the CL, to each adjacent cell, main to the CH
│   └── manifest.{h,cc}       # compact chunk-set frames: Rice-coded lists or bitmap, <= 100 B, self-contained
├── examples/coop-deploy.cc   # steps 1-2 with checks, writes CSV
├── examples/coop-pass.cc     # step 3: UAV broadcast pass over the deployment (ns-3 LR-WPAN)
├── examples/coop-a2g.h       # the urban A2G channel (free space to H, then alpha; Rician)
├── examples/coop-summary.cc  # step 4: per cell, a short summary of what the cell holds, up to the CL
├── examples/coop-g2g.h       # the urban G2G channel (n 3.5, static shadowing, Rayleigh blocks)
├── examples/coop-manifest.cc # step 5 trial: manifests between cells (logic level, frame-hop costs)
├── tools/deploy_figures.py   # the step-by-step figures
├── tools/pass_report.py      # merges pass missions, per-node summary, figures
├── tools/route_figures.py    # route figures
├── tools/summary_report.py   # step 4 tables and figures
└── docs/                     # DEPLOY-vi.md, PASS-vi.md, ROUTING-vi.md, SUMMARY-vi.md, MANIFEST-vi.md, figures/, data/
```

## Build and run (ns-3.46 tree with this dir linked as src/uav-coop)
```bash
ln -s /home/user/wsn-uav/uav-coop /home/user/ns3-dev/src/uav-coop
cd /home/user/ns3-dev
python3.10 ./ns3 configure -d optimized --enable-examples --enable-modules="uav-sar;uav-coop"
cmake --build cmake-cache -j 4
./build/src/uav-coop/examples/ns3.46-uav-coop-deploy-optimized --radius=100 --cells=60 --convexity=1 --spacings=20,35,50 --rho=255 --seed=1 --out=deploy
python3 /home/user/wsn-uav/uav-coop/tools/deploy_figures.py . figures
```
