# uav-sar

Multi-UAV Search-and-Rescue over a PECEE cell substrate — **round-2, fresh
start, pure ns-3 (no CC2420)**.

- **Idea / agreed design:** see [`docs/DESIGN.md`](docs/DESIGN.md) — read this first.
- **Status:** skeleton only. Module builds and runs; simulation logic not yet
  implemented (by design — idea is being locked down first).

## Layout
```
uav-sar/
├── CMakeLists.txt              # build_lib, standard ns-3 libs only
├── docs/DESIGN.md              # the agreed research idea (reference)
├── models/
│   ├── common/                 # sar-info (stub) → enums/types/fragments later
│   ├── network/                # (PECEE cell substrate + topology later)
│   └── application/            # (FAST/DATA UAV + ground/CL apps later)
├── helper/                     # (orchestrator later)
└── examples/
    ├── CMakeLists.txt
    └── uav-sar-hello.cc        # smoke test
```

## Build (inside an ns-3.46 tree with this dir as src/uav-sar)
```bash
python3.10 ./ns3 configure --enable-examples --enable-modules=uav-sar
python3.10 ./ns3 build
./build/src/uav-sar/examples/ns3.46-uav-sar-hello-default
```

## Dependencies
Standard ns-3 only: core, network, mobility, spectrum, propagation, lr-wpan,
energy. **No `wsn`/CC2420.**
