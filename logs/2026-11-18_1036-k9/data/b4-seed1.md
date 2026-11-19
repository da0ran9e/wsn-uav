# K9 B4: River in ns-3 against the surrogate, on the chosen critical-cell sets (k8, seed 1)

Error = predicted minus measured, seconds, over the cells complete by the limit. T_k: last critical cell of the cluster (from leaving it). T1: last critical cell of the mission, from take-off. A cell not complete by the limit counts as 900 s, so its T_k and T1 are lower bounds (>=).

| channel | set | critical cells | not complete | cell MAE | cell bias | T_k MAE | T_k bias | T1 ns-3 | T1 model |
|---|---|---|---|---|---|---|---|---|---|
| r100 | alg3 | 45 | 0 | 30.5 | +8.9 | 39.4 | -15.6 | 770 | 753 |
| r100 | rho20 | 24 | 0 | 14.0 | -8.4 | 18.3 | -18.3 | 687 | 661 |
| r100 | rho100 | 69 | 0 | 44.1 | +7.3 | 37.5 | -20.8 | 733 | 728 |
| r100 | rho200 | 161 | 2 | 142.7 | +45.8 | 210.7 | -96.0 | >=1231 | 906 |
| r200 | alg3 | 45 | 0 | 26.9 | +14.7 | 23.8 | -7.0 | 743 | 740 |
| r200 | rho20 | 24 | 0 | 15.2 | -7.1 | 16.5 | -14.6 | 658 | 654 |
| r200 | rho100 | 70 | 0 | 58.6 | -10.4 | 76.0 | -44.2 | 755 | 714 |
| r200 | rho200 | 161 | 2 | 131.5 | +32.8 | 197.3 | -143.4 | >=1231 | 876 |

T_k per cluster, model / ns-3 (seconds; >= not complete by the limit)

| channel | set | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|---|
| r100 | alg3 | 106 / 90 | 172 / 188 | 141 / 111 | 83 / 86 | 76 / 90 | 120 / 71 | 92 / 121 | 91 / 248 |
| r100 | rho20 | 44 / 61 | 79 / 105 | 60 / 67 | 55 / 68 | 67 / 68 | 40 / 64 | 54 / 69 | 52 / 93 |
| r100 | rho100 | 152 / 114 | 146 / 151 | 126 / 123 | 145 / 142 | 154 / 131 | 150 / 153 | 146 / 195 | 156 / 333 |
| r100 | rho200 | 325 / 190 | 325 / 352 | 281 / 326 | 361 / 271 | 354 / 213 | 306 / 214 | 348 / >=900 | 297 / >=900 |
| r200 | alg3 | 100 / 93 | 158 / 161 | 129 / 112 | 81 / 78 | 68 / 90 | 110 / 70 | 81 / 139 | 82 / 123 |
| r200 | rho20 | 41 / 58 | 72 / 76 | 55 / 58 | 45 / 53 | 55 / 48 | 31 / 49 | 43 / 89 | 44 / 74 |
| r200 | rho100 | 124 / 83 | 133 / 173 | 116 / 137 | 127 / 120 | 133 / 99 | 130 / 84 | 125 / 425 | 135 / 254 |
| r200 | rho200 | 286 / 206 | 295 / 352 | 241 / 314 | 311 / 303 | 316 / 239 | 268 / 217 | 300 / >=900 | 268 / >=900 |
