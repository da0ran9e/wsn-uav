# uav-sar — Round-2 results (round 1 of the new build)

Setup: grid 8×8 (64 sensors), 4 UAVs, 100 seeds, realistic channel
(A2G 2.2 / G2G 3.5 + Nakagami + shadowing). Params in `sar-params.h`
(literature values pending PDFs — see PARAMETERS.md).

## 100-seed aggregate

| scheme   | compl% | complete mean (s) | median | report@BS mean (s) | airtime (pktRecv) | region cells |
|----------|--------|-------------------|--------|--------------------|-------------------|--------------|
| proposed | 100%   | 26.75             | 27.96  | **51.57**          | 68 117            | 1.51         |
| nocoop   | 100%   | 26.09             | 25.70  | — (no loop)        | 21 744            | 0            |
| pure-uav | 100%   | 33.50             | 36.66  | — (no loop)        | 21 543            | 0            |

`complete` = time the victim's node holds the full dataset (comparable across
schemes). `report@BS` = full loop closed (only the cooperative scheme does this).

## Reading (honest)

1. **Only `proposed` closes the loop.** Baselines get complete data onto the
   victim's node, but the system never *knows* or *reports* it — in real SAR that
   means no rescuer is dispatched. Proposed detects → localizes → delivers →
   confirms → **reports to BS** (mean 51.6 s). This is the qualitative win and
   matches the agreed endpoint.
2. **Cross-cell cooperation is real:** mean region size 1.51 cells → in a good
   fraction of runs the victim's evidence spans >1 cell and is merged via CGW /
   inter-cell routing into one summon (no call storm).
3. **On raw complete-time, proposed ≈ nocoop, both beat pure-uav.** At this small
   scale (8×8) with the current wide A2G range, blanket-dumping (nocoop, 4 UAVs)
   reaches the victim about as fast. Round-1 showed the cooperative scheme pulls
   ahead on time at larger scale — to confirm here, rerun at 10–15 grid.
4. **Airtime caveat (important):** `pktRecv` counts *packets*, so proposed looks
   costlier (68k) because FAST cues (tiny, 150 B) are broadcast to the whole grid
   for a long time and counted once per receiver. In **bytes**, baselines dump
   the full 16 KB dataset at *every* cell while proposed delivers it *once* at the
   victim — so byte-airtime should strongly favour proposed. Adding a
   byte-weighted airtime metric is the next fairness fix.

## Known tuning items (pending literature params)
- A2G LoS range ~300 m (0 dBm / −95 dBm) makes cue spread + localization near-
  instant; shortening effective range (TX power / reference loss from Al-Hourani
  / Khawaja / 3GPP) will make the FAST sweep matter and sharpen the time story.
- Byte-weighted airtime + energy (Zeng-Zhang) to replace packet-count proxy.
- Scale study (grid 10–15, more UAVs) to reproduce round-1's at-scale advantage.

## Reproduce
```bash
# in the ns-3 tree with uav-sar as src/uav-sar
python3.10 ./ns3 build
bash src/uav-sar/tools/run_batch.sh 100 8 4 500
# -> data/results/uav-sar/summary.csv + printed table
```
