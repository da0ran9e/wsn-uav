# SAR Experiment (Câu chuyện 1) — Round 1

Multi-UAV Search-and-Rescue over an infrastructure-less WSN, built on the
existing wsn-uav LR-WPAN stack. Goal of round 1: get **complete search data to
the victim's node as fast as possible**, and show cooperation (ground detection
→ emergency beacon → role-based targeted delivery) against non-cooperative
baselines.

## What it models
- 1 BS at the map edge (no ground→BS link except via UAV).
- N×N ground sensors (PECEE clustering assumed already done). One sensor, chosen
  deterministically from the seed, is the **target** (nearest the victim).
- M UAVs, single cruise altitude, A2A relay. Roles:
  - **FAST**: carry small RECOGNITION fragments, fly fast, broadcast them while
    sweeping (GMC coverage), and relay emergency beacons (A2A).
  - **DATA**: carry large DATA fragments, hold them, and on a summon divert
    straight to the victim's cell and deliver the FULL dataset.
- Detection/CV is **not** simulated — only the networking. Fragment payloads are
  opaque byte counts (100 B … `maxFragBytes`, default 4000; model supports 20 KB).

## SAR loop (proposed scheme)
1. UAVs take off, climb, sweep (GMC). FAST UAVs broadcast recognition fragments.
2. Target receives a recognition fragment → **detect** (clue) → asks
   `confirmNeighbors` neighbours to corroborate (CONFIRM_REQ/ACK).
3. On confirm (or `confirmTimeout`, send-anyway) → **emergency beacon**
   (broadcast, low-rate, capped by `beaconQuota`) summoning a DATA UAV.
4. Beacon reaches a DATA UAV (directly or via FAST A2A relay). A fleet-shared
   claim token ensures exactly one DATA UAV **diverts** to the victim cell.
5. DATA UAV delivers the FULL dataset point-blank → target **completes** →
   primary metric `timeToCompleteData_s` is stamped.

## Schemes (`--scheme`)
- `proposed` — multi-UAV, role split, detection + beacon + A2A targeted delivery.
- `nocoop`   — multi-UAV, no ground intelligence: every UAV dwell-and-dumps the
  full dataset at each cell it visits (it doesn't know which cell is the victim).
- `single`   — one UAV, same dwell-and-dump sweep (worst sweep-order case).

Baselines deliver complete data everywhere because they can't pinpoint the
victim; proposed pinpoints it. So the comparison is **time** (proposed is
consistent and wins when the victim is far in sweep order) **and airtime/energy**
(proposed transmits far less — see `pktRecv`/`pktSent` in metrics).

## Open Section-4 questions — round-1 decisions (all parameterized)
| question | flag | default |
|---|---|---|
| neighbours to confirm before beacon | `--confirmNeighbors` | 1 |
| confirm deadline then send anyway   | `--confirmTimeout`   | 0.5 s |
| emergency beacon quota per event    | `--beaconQuota`      | 60 (1/s persistent) |
| A2G channel                         | (network)            | LogDistance n=3 |

## Build
```bash
# ns-3.46 tree with this module symlinked/copied to src/wsn-uav
cd <ns3-root>
python3.10 ./ns3 configure --enable-examples --enable-modules=wsn-uav
python3.10 ./ns3 build
```
(The CC2420 `scenario-0-radio-test` example is auto-skipped when the custom
`wsn` module is absent; everything else uses standard ns-3 lr-wpan.)

## Run one scenario
```bash
./build/src/wsn-uav/examples/ns3.46-scenario-sar-default \
    --gridSize=6 --numUav=4 --numFrag=8 --maxFragBytes=4000 \
    --seed=1 --scheme=proposed --simTime=600
# -> data/results/scenario-sar/<scheme>/run-<seed>/{metrics,events,trajectories,config}.csv
```

## Batch (>=100 seeds, 3 schemes, aggregated)
```bash
bash src/wsn-uav/tools/run_batch.sh 100 6 4 8 4000 600
# -> data/results/scenario-sar/summary.csv  + per-scheme aggregate table
```

## Metrics (`metrics.csv`)
`timeToCompleteData_s` (PRIMARY), `timeToFirstBeacon_s`, `timeToConfirm_s`,
`fragDeliveredPct`, `pdr`, `beaconCount`, `custodyHandoffs`, `pktSent`,
`pktRecv` (airtime proxy), `routeDeviation_m`. `-1` means "not achieved".

## Replay visualizer
Open `docs/visualize/sar-viz.html` in a browser (works offline; has an embedded
sample). Load a real run's `trajectories.csv` / `events.csv` / `metrics.csv`
(e.g. from `docs/visualize/sample-run/`) to replay UAV flight, beacons, divert
and the completion moment on a top-down map with a timeline scrubber.

## Round-1 results (100 / 25 seeds, 4 UAVs, 8 frags, maxFrag 4 KB)

Primary metric = `timeToCompleteData_s` (lower better); airtime = mean `pktRecv`.

Grid 6×6 (100 seeds, simTime 600):
| scheme   | compl% | mean t | median t | airtime |
|----------|--------|--------|----------|---------|
| proposed | 99%    | 30.5 s | 30.1 s   | 2 367   |
| nocoop   | 68%    | 25.1 s | 27.2 s   | 14 854  |
| single   | 97%    | 24.3 s | 22.5 s   | 3 822   |

Grid 10×10 (25 seeds, simTime 1000):
| scheme   | compl% | mean t | median t | airtime |
|----------|--------|--------|----------|---------|
| proposed | 100%   | 40.8 s | 39.5 s   | 4 739   |
| nocoop   | 84%    | 49.5 s | 44.6 s   | 44 793  |
| single   | 100%   | 45.1 s | 44.5 s   | 10 517  |

Reading: in a small area, brute-force baselines reach near the victim quickly so
they edge out on raw latency, but they flood the channel (collisions → nocoop
only 68% complete) and burn 6× the airtime. As the area grows (10×10), the
proposed cooperative + targeted-delivery scheme **wins on all three**: fastest
mean/median time, 100% completion (most reliable), and ~10× less airtime than
nocoop / ~2× less than single. The approach pays off at scale — the regime SAR
actually targets.

## Round-1 scope / not yet modelled
- Single altitude; no UAV battery/no-fly constraints; AoI/TTL not yet penalised.
- Detection is a trigger only (no CV); custody/provenance is metadata-level.
- Energy column is a placeholder (airtime via pkt counts is the proxy used now).
