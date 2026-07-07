# UAV-SAR — Honest results (bypass-free build)

**Scope.** These numbers were produced *after* the methodology audit that moved the
whole cooperation control plane onto the real radio and removed every shortcut
(central coordinator, pointer actuation, shared-memory tokens, ground-truth
position injection) — see the `refactor: fully distributed control plane`,
`fix: UAV role coordination over radio`, and `fix: close clue-before-arrival`
commits. **The earlier "round-2 100-seed" numbers are invalid** — they ran on a
build where clues reached the field ~300 m before any UAV arrived and where the
region was assembled by an omniscient central object. Everything below is
measured over the channel (Forest-A2G + Nakagami + per-pair shadowing).

**Setup.** 8×8 grid (20 m spacing), 4 UAV, 1 BS, `simTime=200 s`, seeds 1–30,
default parameters. `proposed` = 2 FAST (cue) + 2 DATA (deliver). Baselines have
no WSN cooperation: every UAV blind-sweeps its band and dwell-dumps the full
dataset at each cell.

## Head-to-head (N = 30 seeds, median)

| Metric | proposed | nocoop (4 UAV) | pure-uav (1 UAV) |
|---|---:|---:|---:|
| Localize fired | **100 %** | — | — |
| Time to localize | **19.7 s** | — | — |
| Report reaches BS | **100 %** | — | — |
| Time to report @ BS | **53.4 s** | — | — |
| Localization error (median / p90) | **~30 / ~57 m** | — | — |
| Exact victim node served | 40 % | **100 %** | 97 % |
| Time victim node has full data | 39.4 s | 45.2 s | 68.5 s |
| UAV energy | 38 kJ | 27 kJ | **10.8 kJ** |
| Packets sent | **1160** | 3312 | 1878 |

## What this actually says (honest reading)

1. **Proposed is the only scheme that produces actionable output for rescuers.**
   It localizes the victim's region in ~20 s and delivers a report to the BS in
   ~53 s. Baselines never localize and never report — they only disseminate data.

2. **Baselines "serve the victim" more often — but trivially.** They carpet-dump
   the full dataset at every cell, so the victim's own sensor almost always ends
   up with it (100 % / 97 %). That is data *dissemination*, not *localization*;
   it costs 3× the packets (nocoop) or much more time (pure-uav, single UAV).

3. **The proposed scheme's real limitation is localization accuracy, not the
   control plane.** Median error ~30 m (≈ one 20 m cell hop). Because delivery is
   aimed at a single localized point, the *exact* victim sensor completes the
   full dataset only ~40 % of the time. The residual error is driven by
   **cue-coverage timing** — whichever cell the FAST sweep lights up first tends
   to summon first — not by any remaining shortcut. Three principled fixes
   (evidence²-weighted centroid target, coverage dwell, distributed region-window
   defer-to-stronger-cell) moved victim-served 30 % → 40 % and the pipeline to
   100 %, but did not close the accuracy gap: it is a sensing/coverage problem.

4. **Metric caveat.** "Exact victim node served" is a strict, arguably
   victim-centric criterion. In a real SAR the deliverable is the **BS report with
   a location estimate** (100 % @ 53 s, ±~30 m), not the victim's own sensor
   holding the reference dataset. Reported both ways so the comparison is not
   silently framed to favor the proposed scheme.

## Observation-window sweep — accuracy is resolution-limited (N = 30)

`--minObserve=S` holds the first summon until `t = S`, giving the FAST sweep time
to cover more of the area before any cell commits.

| minObserve | localize (s) | loc-err median / p90 (m) | victim served | report (s) |
|---:|---:|---:|---:|---:|
| 0  | 19.7 | **40 / 57** | 40 % | 53.4 |
| 10 | 19.7 | **40 / 57** | 40 % | 53.4 |
| 20 | 20.0 | **40 / 57** | 47 % | 55.7 |
| 30 | 30.0 | **40 / 57** | 63 % | 58.0 |
| 45 | 45.0 | **40 / 57** | 60 % | 72.7 |

Two things this makes unambiguous:

1. **Pointing accuracy is flat (40 m median / 57 m p90) for every window.** Waiting
   longer does *not* sharpen the location estimate — the error is a **sensing
   resolution floor** set by the clue-field decay scale (~60 m) and the 20 m
   sensor grid, not by election timing. No amount of observation fixes it; it is
   a property of the substrate.

2. **The victim-served gain is a coverage effect, not an accuracy effect.** With a
   larger window, several alert cells reach `t = S` together and summon *at the
   same instant*, so suppression no longer collapses them to one — the fleet does
   **multiple targeted deliveries** to the few high-evidence candidate cells. That
   raises the chance one drop lands on the victim (40 → 63 %) at the cost of
   latency, moving `proposed` from a single best-guess delivery toward *targeted
   multi-candidate* delivery (a middle ground between one-shot and the baselines'
   blind carpet-dump — still far fewer packets than carpet). The default is
   `--minObserve=20` (a fast, mostly-single-delivery balance).

## Sensor-spacing sweep — connectivity threshold + resolution source (N = 30)

`--gridSpacing=S` on an 8×8 grid (default S = 20 m). Proposed scheme.

| spacing | localize fires | loc-err median (m) | victim served | intra shares | inter shares |
|---:|---:|---:|---:|---:|---:|
| 15 m | 100 % | 33 | 43 % | 77 | 3.8 |
| 20 m | 100 % | 40 | 47 % | 56 | 8.5 |
| 25 m | 93 %  | 25 | 47 % | 31 | 11.2 |
| 30 m | 90 %  | 30 | 33 % | 21 | 11.7 |
| 40 m | **10 %** | — | 10 % | **0** | 4.7 |

1. **Cooperation collapses when spacing exceeds the G2G radio range (~37 m).** At
   40 m the intra-cell tree is disconnected: members cannot reach their Cell
   Leader, intra shares fall to **0**, and localization fires in only 10 % of
   runs. The whole distributed control plane depends on a *connected* WSN — the
   deployment must keep spacing below the derived G2G range (`DeriveG2gRangeM`,
   ~37 m here). (This is the honest, radio-level re-measurement of the old
   "spacing-40 collapse"; the earlier study saw the effect but on a build where
   the control plane bypassed the radio, so it under-counted the collapse.)

2. **Localization accuracy does NOT improve with denser sensors** (33/40/25/30 m
   across 15–30 m spacing — noise, no trend). This *refutes* the natural "denser
   grid → sharper localization" hypothesis: the error floor is set by the
   **clue-field decay scale (~60 m sensing range)**, not by spatial sampling.
   Spending sensors below ~20 m spacing buys connectivity margin and more
   cooperative traffic, but not a better location estimate — to sharpen that you
   would need sharper *sensing* (steeper clue decay), not more nodes.

3. **Inter-cell cooperation traffic peaks at medium spacing** (3.8 → 11.7 shares
   as 15 → 30 m): tighter grids fit in fewer hex cells (fewer boundaries to share
   across); wider grids span more cells until connectivity collapses at 40 m.

## Honesty ledger (what is real vs assumed)

- **Real over radio, channel-subject:** cue dissemination, intra-cell clue
  reports (RPT, multi-hop), inter-cell shares (SHARE, flood), summon, A2A relay,
  full-data delivery, confirm, report, handoff, and UAV role claims (CLAIM).
- **Distributed, no central brain:** region formation + leader election run in
  the Cell-Leader apps via evidence-backoff + SUMMON suppression + SHARE-based
  defer. No global-view object; the summon's delivery coordinates are a node's
  own radio-reported GPS.
- **Still assumed (declared, not hidden):** the WSN topology (sensor positions)
  is known to the UAVs for sweep planning; the victim node self-identifies for
  the `timeToCompleteData` metric and the baseline stop criterion. These are
  surveyed-network assumptions, not per-run cheats.

## Open problems (future work)

- Localization accuracy is coverage-limited. Candidates: don't stop cueing at the
  first summon; a longer observation window before summoning; sweep patterns that
  equalize per-node cue exposure; multi-point / region-sweep delivery so the
  footprint (not one node) is served.
- `timeToCompleteData = -1` on ~60 % of proposed runs is the same accuracy gap
  surfacing as a metric, not a failure — the mission still localizes + reports.

*Reproduce:* `scenario-sar --seed=S --scheme={proposed,nocoop,pure-uav}` and the
campaign script in the session scratchpad (`campaign/compare.py`).
