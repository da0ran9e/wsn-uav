# K9 B6: node density and device tiers (model level, k8 r100)

## Density

Loads and indexes scale with rho x fcam x density, so density d at rho equals the 816 nodes/km^2 map at rho x d / 816. Largest rho with an AI node in every cell (617 AI cells), fcam 0.3:

| budget | 816 | 400 | 280 |
|---|---|---|---|
| 0.1 | 640 | 1306 | 1865 |
| 0.2 | 1275 | 2601 | 3716 |

The B3 sets (chosen at 816 for rho 20 / 100 / 200, budget 0.1) serve, at 400 and 280 nodes/km^2:

| set | 816 | 400 | 280 |
|---|---|---|---|
| rho20 | 20 | 41 | 58 |
| rho100 | 100 | 204 | 291 |
| rho200 | 200 | 408 | 583 |

Check by binomial thinning (seed 1): busiest medium on the thinned map / (p x full map); 1 is exact scaling.

| density | set | AI cells | ratio |
|---|---|---|---|
| 400 | rho20 | 24 | 0.996 |
| 400 | rho100 | 69 | 1.017 |
| 400 | rho200 | 161 | 1.078 |
| 280 | rho20 | 24 | 1.012 |
| 280 | rho100 | 69 | 1.104 |
| 280 | rho200 | 161 | 1.231 |

## Device tiers (option D3)

Camera: busy share embedding one crop per passer-by at rho = 200 and 3 700 people/h. AI node: reference embedding plus search of the largest B5 index (Algorithm 3 at rho 200, fcam 0.3, 2 h), first pass L = 3 and V1 L = 20; the V1 visit itself is 78 s. Index bytes against the device memory.

Largest index 152280 vectors (80 MB); smallest feasible 1368 (0.7 MB).

| tier | camera busy, rho 200 | camera busy, rho 3 700 | AI query L=3 (s) | V1 L=20 (s) | largest index fits | smallest fits | source |
|---|---|---|---|---|---|---|---|
| T0 MCU (ESP32-S3) | 1.50% | 27.7% | 0.83 | 5.42 | no | yes | face embedding 255-287 ms on ESP32-S3 [repo]; PSRAM 8 MB |
| T0 MCU (STM32N6) | 0.06% | 1.0% | 0.05 | 0.22 | no | yes | OSNet x0.25 extrapolated 3-10 ms [estimate]; 4.2 MB RAM |
| T1 camera SoC | 0.06% | 1.0% | 0.05 | 0.22 | yes | yes | about 100 crops/s [repo] |
| T2 Pi 5 CPU | 0.44% | 8.2% | 0.26 | 1.61 | yes | yes | ResNet-50 INT8 12.6/s (l1_mission.py); OSNet x0.25 faster |
| T2 Pi 5 + Hailo-8L | 0.02% | 0.4% | 0.03 | 0.10 | yes | yes | 257.6/s (l1_mission.py) |
