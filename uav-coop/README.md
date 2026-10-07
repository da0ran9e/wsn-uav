# uav-coop

UAV-assisted dissemination with edge cooperation inside wide clusters — a new
project that starts from the parameter set measured in `uav-sar`'s urban
experiments (`uav-sar/docs/A2G-RUN-vi.md`, `A2G-SWEEP-vi.md`, `G2G-CHAIN-vi.md`).
Those values live in `models/common/coop-params.h`.

**Status: steps 1–3 + routes.** Hex lattice (corner radius R = 100 m) from the origin → a truly
random contiguous region whose concavities are filled up to a target convexity (default:
fully convex) → random sensor nodes with three random capabilities → one CH (kept at least
300 m from the edge), one CL per cell → an open Dubins flight path across the cluster: in
at a random boundary point, over the CH, out at another (min turn radius a parameter). See
[`docs/DEPLOY-vi.md`](docs/DEPLOY-vi.md). Step 3: the UAV flies that path broadcasting a
numbered stream; packets received per node — [`docs/PASS-vi.md`](docs/PASS-vi.md). Pre-built
routes (PECEE elastic clustering: next hop to the CL, to each adjacent cell, main route
to the CH) — [`docs/ROUTING-vi.md`](docs/ROUTING-vi.md).

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
│   └── routing.{h,cc}        # route tables: to the CL, to each adjacent cell, main to the CH
├── examples/coop-deploy.cc   # steps 1-2 with checks, writes CSV
├── examples/coop-pass.cc     # step 3: UAV broadcast pass over the deployment (ns-3 LR-WPAN)
├── examples/coop-a2g.h       # the urban A2G channel (free space to H, then alpha; Rician)
├── tools/deploy_figures.py   # the step-by-step figures
├── tools/pass_report.py      # merges pass missions, per-node summary, figures
├── tools/route_figures.py    # route figures
└── docs/                     # DEPLOY-vi.md, PASS-vi.md, ROUTING-vi.md, figures/, data/
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
