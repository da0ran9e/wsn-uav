# UAV-SAR — Honest results (bypass-free build)

**Scope.** Measured on the fully audited build: the whole cooperation control
plane runs over the real radio (RPT/SHARE/SUMMON/CLAIM/A2A/FULL/CONFIRM/REPORT),
region formation + leader election are distributed (evidence backoff + SUMMON
suppression), and every earlier shortcut (central coordinator, pointer
actuation, shared-memory tokens, ground-truth position injection) is removed.
Channel: Forest-A2G (Al-Hourani LoS + ITU-R P.833 foliage) + Nakagami +
per-pair shadowing. **The old "round-2 100-seed" numbers are invalid** (they ran
on a build where cues reached the field ~300 m before any UAV arrived).

**Declared assumptions (not per-run cheats).** The PECEE substrate — hex cells,
cell leaders, intra-cell routing trees, gateways — is computed at setup and
loaded into the nodes, i.e. the network is assumed *already initialized* (a
surveyed deployment); topology formation itself is out of scope. UAVs know
sensor positions for sweep planning. The victim node self-identifies only for
the `timeToCompleteData` metric and the baselines' stop criterion.

---

## ⚠ Correction: the localization metric was wrong (kept for the record)

Earlier revisions of this document concluded that localization error was "flat
at ~30–40 m across every knob" and blamed a granularity floor in the election.
That conclusion was an **artifact of a mismeasured metric**: the analysis read
the `summon_start` event coordinates, which log the *region leader's own
position* — a grid-quantized point that is structurally ~1 cell away from the
victim and insensitive to targeting improvements. The quantity that matters is
the **delivery error**: distance from where the DATA UAV actually drops the
dataset (`deliver_start`) to the victim. With the correct metric every
conclusion below was re-measured. The wrong-metric sweeps are superseded by the
tables in this file; the moral stands on its own: *validate the metric before
trusting the sweep*.

---

## Final head-to-head (N = 30 seeds, median, default config¹)

| Metric | proposed | nocoop (4 UAV) | pure-uav (1 UAV) |
|---|---:|---:|---:|
| Localize fired / time | **100 % @ 20 s** | — | — |
| Report reaches BS / time | **100 % @ 67 s** | — | — |
| **Delivery error (median / p90)** | **15.8 / 28.1 m** | — | — |
| Victim node has full data | **100 % @ 43.4 s** | 100 % @ 45.2 s | 97 % @ 68.5 s |
| Packets sent | **1876** | 3312 | 1878 |
| UAV energy | 47 kJ | 27 kJ | **10.8 kJ** |

¹ default = `--minObserve=20`, delivery dwell 20 s, 8×8 grid @ 20 m, 4 UAV.

**Honest reading.** With the aiming + dwell fixes, `proposed` now matches the
carpet-dump baseline on victim outcome (100 %, slightly faster) while *also*
producing what baselines cannot: a location estimate (±16 m) and a report at the
BS — at 43 % fewer packets than nocoop. The cost is energy (47 vs 27 kJ: two
extra UAVs loiter/divert instead of sweeping) and pipeline latency (67 s to
close the loop). `pure-uav` remains the energy-minimal but slowest option.

## The causal chain that got us here (each link measured)

1. **Aiming.** The elected leader interpolates the evidence peak from radio data
   only — members' RPTs (per-node evidence + self-reported GPS) plus neighbour
   cells' SHAREs (aggregate + cell centre). Delivery error: **15.8 m median**.
2. **Aiming is sensing-limited (the honest resolution law).** Sweeping the
   on-node detector's range (`--clueDecay`): error scales ≈ 0.2–0.25× decay —
   **6.6 m** @ 30 m decay, 15.8 m @ 60 m, 21.2 m @ 120 m. Sharper sensing →
   sharper delivery. (Delivery error is *not* limited by sensor density: 14/16/
   11 m across 15/20/30 m spacing.)
3. **Observation window buys accuracy AND coverage.** `--minObserve` 0→30 s:
   delivery error 18.4 → 10.8 m (more reports to interpolate) and ≤20 m rate
   63 → 90 %, at +5–10 s pipeline latency.
4. **Victim completion was dwell-limited, not aiming-limited.** With ~16 m error
   the victim sits inside the delivery footprint, yet at 8 s dwell only ~47 %
   of runs completed it (the ~150-chunk dataset needs several broadcast passes
   at footprint edge). Dwell 20 s → **victim served 100 %**, +12 s report
   latency. This was diagnosed (hypothesis → single-knob test), not tuned blind.

## Sensor-spacing sweep — connectivity threshold (N = 30)

| spacing | localize fires | delivery err (med) | intra shares | inter shares |
|---:|---:|---:|---:|---:|
| 15 m | 100 % | 13.9 m | 77 | 3.8 |
| 20 m | 100 % | 15.8 m | 56 | 8.5 |
| 30 m | 93 %  | 11.5 m | 21 | 11.7 |
| 40 m | **10 %** | — | **0** | 4.7 |

**Cooperation collapses when spacing exceeds the G2G radio range (~37 m).** At
40 m the intra-cell tree disconnects: members cannot reach their Cell Leader,
intra shares fall to 0, and localization fires in 10 % of runs. Deployments must
keep spacing below `DeriveG2gRangeM()` (~37 m at 0 dBm / −95 dBm / n = 3.5).
Below that threshold, density buys connectivity margin — not accuracy.

## Honesty ledger

- **Real over radio, channel-subject:** cue dissemination, intra-cell reports
  (RPT, multi-hop up the cell tree), inter-cell shares (SHARE flood), summon +
  suppression election, A2A relay, role claims (CLAIM), full-data delivery,
  confirm, report, courier handoff.
- **Distributed:** no global-view object; all decisions are taken by node apps
  from bytes that physically arrived. Delivery coordinates are radio-reported
  node GPS, interpolated on the leader.
- **Assumed (declared):** pre-initialized PECEE substrate (cells/trees/leaders
  loaded at setup); UAVs know sensor positions for sweep planning; victim
  self-identifies for metrics/baseline-stop only.
- **Known metric caveats:** `timeToLocalize` marks the first summon; with larger
  observation windows several cells summon simultaneously (targeted
  multi-candidate delivery), which raises packet cost — reflected in pktSent.

## Reproduce

```
scenario-sar --seed=S --scheme={proposed,nocoop,pure-uav}
             [--minObserve=20] [--clueDecay=60] [--gridSpacing=20]
tools/campaign_compare.py        # 3-scheme table
tools/campaign_sweep2.py         # any-knob sweep with the CORRECT delivery metric
```
