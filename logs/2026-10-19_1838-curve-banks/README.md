# 2026-10-19 · Curved Axes: local-normal Banks and MEANDER (CLAUDE.md §8 item 103)

**Purpose:**
1. Banks perpendicular to a curved flight path, compared with the old parallel Banks.
2. A curved-lane cluster restructuring that follows the terrain (MEANDER).

**Runs:**
- `run.cmd` / `run.log`: `uav-l2/tools/curve_banks.py`, geometry.
  - 18 clusters of the k4/k6/k8 maps rebuilt by regeom; one cluster fails at every angle.
  - Bends 180/135/100/70°. Deploys go to scratchpad `CURV/` (not committed). About 45 s.
- `ns3.cmd` / `ns3.log`: `uav-l2/tools/curve_ns3.py`.
  - ns-3 pass, then River (prepared, 7 colours) with both Bank kinds.
  - 18 clusters × 2 bends (100, 70) = 36 pairs. About 40 min with 3 jobs.
- `meander.cmd` / `meander.log`: `uav-l2/tools/meander.py --campaign`.
  - 60 curved maps, 3 skipped (k-medoids fails on land in pieces). About 3 min, geometry only.

**Outputs:**
- data: `uav-l2/docs/data/curve/{banks,ns3}.csv`, `uav-l2/docs/data/meander/maps.csv`
- figures: `uav-l2/docs/figures/curve-banks-example.png`, `meander-*-{steps,compare}.png`
- report: `uav-l2/docs/CURVE-vi.md`

**Main results:**
- **Local Banks** keep their distance at about 0.9 ω on bends, against 0.63–0.78 ω for parallel Banks.
- **In ns-3 there is no time gain** (mean 9.0 vs 9.1 s, 18/36 better) and 7.7 % more hops.
- **MEANDER** beats LANE on River coverage mainly in narrow bent domains (+8 points, 10/10); elsewhere 0–3 points.
- **MEANDER's cost:** 20–40 % more in-cluster flight and about 3× the turning; all curves meet ρ = 255 m.

**Open:**
- ns-3 mission run on MEANDER curves.
- Smooth spine.
- Cross-lane clusters.
