/Users/mophan/Github/ns3-uav-build/runs/T3v0/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v1/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v2/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v3/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v4/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v5/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/CP/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LM/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LMD/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/DR/open/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v0/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v1/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v2/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v3/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v4/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v5/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/CP/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LM/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LMD/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/DR/r500/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v0/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v1/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v2/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v3/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v4/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v5/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/CP/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LM/r200/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LMD/r200/k8-s1: 45 critical cells
<!-- DR r200: skipped (AssertionError(('/Users/mophan/Github/ns3-uav-build/runs/DR/r200/k8-s1', 4, 'AXE'))) -->
/Users/mophan/Github/ns3-uav-build/runs/T3v0/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v1/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v2/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v3/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v4/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/T3v5/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/CP/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LM/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/LMD/r100/k8-s1: 45 critical cells
/Users/mophan/Github/ns3-uav-build/runs/DR/r100/k8-s1: 45 critical cells
# Tier 3 check, k8-s1

1457 cell results, 32 (channel, cluster) groups, 253 passes (5-10 a group); training 632 cells of k12, k16.

| setting | model | MAE doneS (s) | mean Spearman of S | regret (s, mean ± 95 %) | best pass picked |
|---|---|---|---|---|---|
| A | formula | 19.5 | 0.52 | 26.2 ± 30.0 | 34 % |
| B | formula | 19.4 | 0.39 | 59.4 ± 50.4 | 31 % |
| A | linear | 20.2 | 0.50 | 26.9 ± 30.0 | 34 % |
| B | linear | 20.0 | 0.39 | 42.0 ± 39.7 | 28 % |
| A | trees | 19.7 | 0.42 | 45.9 ± 55.8 | 34 % |
| B | trees | 18.6 | 0.38 | 51.8 ± 55.9 | 34 % |
| A | hgb | 21.5 | 0.47 | 43.9 ± 46.1 | 28 % |
| B | hgb | 20.3 | 0.43 | 46.9 ± 46.1 | 34 % |
| - | random pass | - | 0 | 58.6 | - |

- A: regret hgb − formula +17.7 ± 24.7 s a cluster (hgb better in 9, worse in 12 of 32 groups)
- B: regret hgb − formula -12.5 ± 37.4 s a cluster (hgb better in 10, worse in 9 of 32 groups)
